import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ComfyWorkspace } from '../ComfyWorkspace';

const nativeWindow = vi.hoisted(() => ({ onCloseRequested: vi.fn(), close: vi.fn() }));
vi.mock('@tauri-apps/api/window', () => ({ getCurrentWindow: () => nativeWindow }));

describe('ComfyWorkspace', () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    nativeWindow.onCloseRequested.mockReset();
    nativeWindow.close.mockReset();
  });

  it('connects only on request and disconnects without stopping the service', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ system: {}, devices: [] }),
    });
    vi.stubGlobal('fetch', fetchMock);
    vi.stubGlobal('confirm', vi.fn().mockReturnValue(true));
    render(<ComfyWorkspace />);
    expect(fetchMock).not.toHaveBeenCalled();

    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    await screen.findByTitle('ComfyUI workflow editor');
    expect(fetchMock).toHaveBeenCalledWith(
      'http://127.0.0.1:8189/system_stats',
      expect.objectContaining({ credentials: 'omit', redirect: 'error' }),
    );
    expect(screen.getByTitle('ComfyUI workflow editor')).toHaveAttribute('src', 'http://127.0.0.1:8189');
    fireEvent.click(screen.getByRole('button', { name: 'Disconnect' }));
    expect(screen.queryByTitle('ComfyUI workflow editor')).not.toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledTimes(1);
  });

  it('keeps the editor mounted when disconnect is cancelled', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true, json: async () => ({ system: {}, devices: [] }),
    }));
    const confirm = vi.fn().mockReturnValue(false);
    vi.stubGlobal('confirm', confirm);
    render(<ComfyWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    const editor = await screen.findByTitle('ComfyUI workflow editor');
    fireEvent.click(screen.getByRole('button', { name: 'Disconnect' }));
    expect(confirm).toHaveBeenCalledWith(expect.stringContaining('Unsaved workflow changes may be lost'));
    expect(screen.getByTitle('ComfyUI workflow editor')).toBe(editor);
  });

  it('warns before closing the window while the editor is connected', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true, json: async () => ({ system: {}, devices: [] }),
    }));
    render(<ComfyWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    await screen.findByTitle('ComfyUI workflow editor');
    const event = new Event('beforeunload', { cancelable: true });
    window.dispatchEvent(event);
    expect(event.defaultPrevented).toBe(true);
  });

  it('intercepts native close and closes only after explicit confirmation', async () => {
    vi.stubGlobal('__TAURI_INTERNALS__', {});
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true, json: async () => ({ system: {}, devices: [] }),
    }));
    const confirm = vi.fn().mockReturnValue(false);
    vi.stubGlobal('confirm', confirm);
    let closeHandler!: (event: { preventDefault: () => void }) => Promise<void> | void;
    nativeWindow.onCloseRequested.mockImplementation(async (handler) => {
      closeHandler = handler;
      return vi.fn();
    });
    nativeWindow.close.mockImplementation(async () => closeHandler({ preventDefault: vi.fn() }));
    render(<ComfyWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    await screen.findByTitle('ComfyUI workflow editor');
    await waitFor(() => expect(nativeWindow.onCloseRequested).toHaveBeenCalledOnce());

    const preventDefault = vi.fn();
    await closeHandler({ preventDefault });
    expect(preventDefault).toHaveBeenCalledOnce();
    expect(nativeWindow.close).not.toHaveBeenCalled();

    confirm.mockReturnValue(true);
    await closeHandler({ preventDefault: vi.fn() });
    expect(nativeWindow.close).toHaveBeenCalledOnce();
  });

  it('shows actionable gateway errors when connecting', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false, status: 502, text: async () => 'ComfyUI CORS mode is unsafe; restart without --enable-cors-header.',
    }));
    render(<ComfyWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('restart without --enable-cors-header');
  });

  it('reports an unexpected service instead of opening the editor', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, json: async () => ({}) }));
    render(<ComfyWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('did not return ComfyUI system information');
    expect(screen.queryByTitle('ComfyUI workflow editor')).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Retry connection' })).toBeInTheDocument();
  });

  it('allows retry after a network error', async () => {
    const fetchMock = vi.fn()
      .mockRejectedValueOnce(new TypeError('Network error'))
      .mockResolvedValueOnce({ ok: true, json: async () => ({ system: {}, devices: [] }) });
    vi.stubGlobal('fetch', fetchMock);
    render(<ComfyWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Network error');
    fireEvent.click(screen.getByRole('button', { name: 'Retry connection' }));
    expect(await screen.findByTitle('ComfyUI workflow editor')).toBeInTheDocument();
  });

  it('ignores a late response after disconnecting', async () => {
    let resolve!: (value: unknown) => void;
    const fetchMock = vi.fn(() => new Promise((done) => { resolve = done; }));
    vi.stubGlobal('fetch', fetchMock);
    render(<ComfyWorkspace />);
    fireEvent.click(screen.getByRole('button', { name: 'Connect' }));
    fireEvent.click(screen.getByRole('button', { name: 'Disconnect' }));
    resolve({ ok: true, json: async () => ({ system: {}, devices: [] }) });
    await waitFor(() => expect(screen.getByText('Not connected')).toBeInTheDocument());
    expect(screen.queryByTitle('ComfyUI workflow editor')).not.toBeInTheDocument();
  });

  it('reports a lost service and preserves the editor until the service recovers', async () => {
    vi.useFakeTimers();
    const ok = { ok: true, json: async () => ({ system: {}, devices: [] }) };
    vi.stubGlobal('fetch', vi.fn().mockResolvedValueOnce(ok)
      .mockRejectedValueOnce(new Error('offline')).mockResolvedValueOnce(ok));
    render(<ComfyWorkspace />);
    await act(async () => { fireEvent.click(screen.getByRole('button', { name: 'Connect' })); });
    const editor = screen.getByTitle('ComfyUI workflow editor');
    await act(async () => { await vi.advanceTimersByTimeAsync(10000); });
    expect(screen.getByRole('alert')).toHaveTextContent('stopped responding');
    expect(screen.getByTitle('ComfyUI workflow editor')).toBe(editor);
    await act(async () => { await vi.advanceTimersByTimeAsync(10000); });
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(screen.getByTitle('ComfyUI workflow editor')).toBe(editor);
  });
});
