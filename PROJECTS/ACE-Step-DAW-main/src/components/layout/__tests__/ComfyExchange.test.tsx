import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { ComfyExchange } from '../ComfyExchange';
import { captureComfyWorkflow } from '../../../services/comfyWorkflowExchange';
import { importComfyAudio, listComfyAudio } from '../../../services/comfyAudioExchange';

vi.mock('../../../services/comfyWorkflowExchange', () => ({ captureComfyWorkflow: vi.fn() }));
vi.mock('../../../services/comfyAudioExchange', () => ({ importComfyAudio: vi.fn(), listComfyAudio: vi.fn() }));
vi.mock('../../../store/projectStore', () => {
  const state = { project: { id: 'project-a' }, saveComfyWorkflow: vi.fn(() => true) };
  return { useProjectStore: Object.assign((selector: (value: typeof state) => unknown) => selector(state), { getState: () => state }) };
});

describe('ComfyExchange progress', () => {
  beforeEach(() => vi.clearAllMocks());

  it('announces workflow capture while it is pending', async () => {
    let finish!: (workflow: string) => void;
    vi.mocked(captureComfyWorkflow).mockReturnValue(new Promise((resolve) => { finish = resolve; }));
    render(<ComfyExchange frameRef={{ current: document.createElement('iframe') }} unavailable={false} />);
    fireEvent.click(screen.getByRole('button', { name: 'Save workflow to project' }));
    expect(screen.getByRole('status')).toHaveTextContent('Saving workflow...');
    finish('{}');
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Workflow saved'));
  });

  it('announces output discovery and audio import while pending', async () => {
    const output = { id: 'a', filename: 'song.wav', subfolder: '', type: 'output' as const };
    let finishList!: (value: typeof output[]) => void;
    let finishImport!: () => void;
    vi.mocked(listComfyAudio).mockReturnValue(new Promise((resolve) => { finishList = resolve; }));
    vi.mocked(importComfyAudio).mockReturnValue(new Promise((resolve) => { finishImport = resolve; }));
    render(<ComfyExchange frameRef={{ current: null }} unavailable={false} />);
    fireEvent.click(screen.getByRole('button', { name: 'Find output audio' }));
    expect(screen.getByRole('status')).toHaveTextContent('Finding output audio...');
    finishList([output]);
    fireEvent.click(await screen.findByRole('button', { name: 'Import to DAW' }));
    expect(screen.getByRole('status')).toHaveTextContent('Importing audio...');
    finishImport();
    await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent('Audio copied'));
  });
});
