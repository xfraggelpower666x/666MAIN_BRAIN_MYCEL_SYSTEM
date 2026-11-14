import { beforeEach, describe, expect, it, vi } from 'vitest';
import { importComfyAudio, listComfyAudio } from '../comfyAudioExchange';
import { getAudioEngine } from '../../hooks/useAudioEngine';
import { saveAudioBlob, deleteAudioBlobByKey } from '../audioFileManager';
import { useProjectStore } from '../../store/projectStore';

vi.mock('../../hooks/useAudioEngine', () => ({ getAudioEngine: vi.fn() }));
vi.mock('../audioFileManager', () => ({ saveAudioBlob: vi.fn(), deleteAudioBlobByKey: vi.fn() }));
vi.mock('../../utils/waveformPeaks', () => ({ computeWaveformPeaks: () => [1, -1, 1, -1] }));
vi.mock('../../store/projectStore', () => ({ useProjectStore: { getState: vi.fn() } }));

describe('ComfyUI audio exchange', () => {
  const output = { id: 'a', filename: 'song.wav', subfolder: 'audio', type: 'output' as const };
  const addComfyAudio = vi.fn();
  const decodeAudioData = vi.fn();
  const resume = vi.fn();
  let projectId: string;

  beforeEach(() => {
    vi.resetAllMocks();
    projectId = 'project-a';
    vi.mocked(useProjectStore.getState).mockImplementation(() => ({
      project: { id: projectId }, addComfyAudio,
    }) as ReturnType<typeof useProjectStore.getState>);
    vi.mocked(getAudioEngine).mockReturnValue({ resume, ctx: { decodeAudioData } } as ReturnType<typeof getAudioEngine>);
    decodeAudioData.mockResolvedValue({ duration: 7, length: 3200 });
    vi.mocked(saveAudioBlob).mockResolvedValue('audio-key');
    addComfyAudio.mockReturnValue(true);
  });

  it('lists only valid audio entries from history', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: true, json: async () => ({
        job: { outputs: { node: { audio: [
          { filename: 'song.wav', subfolder: 'audio', type: 'output' },
          { filename: '../bad.wav', subfolder: '', type: 'output' },
          { filename: 'bad.wav', subfolder: '../secret', type: 'output' },
          { filename: 'bad.wav', subfolder: '', type: 'input' },
        ] } } },
      }),
    }));
    expect(await listComfyAudio()).toMatchObject([{ filename: 'song.wav', subfolder: 'audio', type: 'output' }]);
    vi.unstubAllGlobals();
  });

  it('reports actionable gateway failures when listing audio', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false, status: 502, text: async () => 'ComfyUI CORS mode is unsafe; restart without --enable-cors-header.',
    }));
    await expect(listComfyAudio()).rejects.toThrow('restart without --enable-cors-header');
    vi.unstubAllGlobals();
  });

  it('copies the original blob into the selected project', async () => {
    const blob = new Blob(['original'], { type: 'audio/wav' });
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, blob: async () => blob }));
    await importComfyAudio(output, projectId);
    expect(saveAudioBlob).toHaveBeenCalledWith('project-a', expect.any(String), 'isolated', blob);
    expect(addComfyAudio).toHaveBeenCalledWith(expect.objectContaining({
      projectId: 'project-a', audioKey: 'audio-key', name: 'song.wav', duration: 7,
    }));
    vi.unstubAllGlobals();
  });

  it('does not insert or leak the new blob if the project changes during storage', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, blob: async () => new Blob(['audio']) }));
    vi.mocked(saveAudioBlob).mockImplementation(async () => { projectId = 'project-b'; return 'audio-key'; });
    addComfyAudio.mockReturnValue(false);
    await expect(importComfyAudio(output, 'project-a')).rejects.toThrow('project changed');
    expect(deleteAudioBlobByKey).toHaveBeenCalledWith('audio-key');
    vi.unstubAllGlobals();
  });

  it('does not mutate the project when decoding fails', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, blob: async () => new Blob(['bad']) }));
    decodeAudioData.mockRejectedValue(new Error('decode failed'));
    await expect(importComfyAudio(output, projectId)).rejects.toThrow('decode failed');
    expect(saveAudioBlob).not.toHaveBeenCalled();
    expect(addComfyAudio).not.toHaveBeenCalled();
    vi.unstubAllGlobals();
  });

  it('removes stored audio and does not add a track if disconnected during storage', async () => {
    const controller = new AbortController();
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({ ok: true, blob: async () => new Blob(['audio']) }));
    vi.mocked(saveAudioBlob).mockImplementation(async () => { controller.abort(); return 'audio-key'; });
    await expect(importComfyAudio(output, projectId, controller.signal)).rejects.toThrow();
    expect(addComfyAudio).not.toHaveBeenCalled();
    expect(deleteAudioBlobByKey).toHaveBeenCalledWith('audio-key');
    vi.unstubAllGlobals();
  });
});
