import { act, fireEvent, render, screen, waitFor } from '@testing-library/react';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { ComfyWorkspace } from '../ComfyWorkspace';

describe('ComfyWorkspace', () => {
  afterEach(() => { vi.useRealTimers(); vi.unstubAllGlobals(); });

  it('connects only on request and disconnects without stopping the service', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ system: {}, devices: [] }),
    });
    vi.stubGlobal('fetch', fetchMock);
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
