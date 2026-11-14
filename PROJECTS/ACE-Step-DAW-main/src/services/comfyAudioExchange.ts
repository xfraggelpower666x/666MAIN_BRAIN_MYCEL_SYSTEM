import { getAudioEngine } from '../hooks/useAudioEngine';
import { useProjectStore } from '../store/projectStore';
import { computeWaveformPeaks } from '../utils/waveformPeaks';
import { deleteAudioBlobByKey, saveAudioBlob } from './audioFileManager';

const GATEWAY = 'http://127.0.0.1:8189';

export interface ComfyAudioOutput {
  id: string;
  filename: string;
  subfolder: string;
  type: 'output' | 'temp';
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === 'object' && !Array.isArray(value);
}

async function request<T>(path: string, consume: (response: Response) => Promise<T>, signal?: AbortSignal): Promise<T> {
  const controller = new AbortController();
  const abort = () => controller.abort();
  if (signal?.aborted) controller.abort();
  else signal?.addEventListener('abort', abort, { once: true });
  const timeout = window.setTimeout(() => controller.abort(), 60000);
  try {
    const response = await fetch(`${GATEWAY}${path}`, {
      credentials: 'omit', redirect: 'error', cache: 'no-store', signal: controller.signal,
    });
    if (!response.ok) throw new Error(`ComfyUI gateway returned HTTP ${response.status}`);
    return await consume(response);
  } finally {
    window.clearTimeout(timeout);
    signal?.removeEventListener('abort', abort);
  }
}

export async function listComfyAudio(signal?: AbortSignal): Promise<ComfyAudioOutput[]> {
  const history: unknown = await request('/history', (response) => response.json(), signal);
  signal?.throwIfAborted();
  if (!isRecord(history)) throw new Error('Invalid ComfyUI history response.');
  const results: ComfyAudioOutput[] = [];
  for (const [jobId, job] of Object.entries(history).reverse()) {
    if (!isRecord(job) || !isRecord(job.outputs)) continue;
    for (const [nodeId, output] of Object.entries(job.outputs)) {
      if (!isRecord(output) || !Array.isArray(output.audio)) continue;
      output.audio.forEach((value: unknown, index: number) => {
        if (!isRecord(value) || typeof value.filename !== 'string' ||
            typeof value.subfolder !== 'string' || (value.type !== 'output' && value.type !== 'temp')) return;
        if (!value.filename || /[\\/\0]/.test(value.filename) || value.filename === '..' ||
            value.subfolder.split(/[\\/]/).some((part: string) => part === '..')) return;
        results.push({
          id: JSON.stringify([jobId, nodeId, index]),
          filename: value.filename,
          subfolder: value.subfolder,
          type: value.type,
        });
      });
    }
  }
  return results;
}

export async function importComfyAudio(output: ComfyAudioOutput, projectId: string, signal?: AbortSignal): Promise<void> {
  signal?.throwIfAborted();
  if (useProjectStore.getState().project?.id !== projectId) throw new Error('The active project changed.');
  const engine = getAudioEngine();
  await engine.resume();
  const query = new URLSearchParams({
    filename: output.filename, subfolder: output.subfolder, type: output.type,
  });
  const blob = await request(`/view?${query}`, (response) => response.blob(), signal);
  if (!blob.size) throw new Error('ComfyUI returned an empty audio file.');
  const buffer = await engine.ctx.decodeAudioData(await blob.arrayBuffer());
  signal?.throwIfAborted();
  if (!Number.isFinite(buffer.duration) || buffer.duration <= 0) throw new Error('Invalid audio duration.');
  const peaks = computeWaveformPeaks(buffer, Math.min(2000, Math.max(1, Math.floor(buffer.length / 32))));
  if (useProjectStore.getState().project?.id !== projectId) throw new Error('The active project changed.');
  const clipId = crypto.randomUUID();
  const key = await saveAudioBlob(projectId, clipId, 'isolated', blob);
  try {
    signal?.throwIfAborted();
    const added = useProjectStore.getState().addComfyAudio({
      projectId, clipId, audioKey: key, name: output.filename, duration: buffer.duration, peaks,
    });
    if (!added) throw new Error('The project changed, is read-only, or has reached the track limit.');
  } catch (error) {
    try {
      await deleteAudioBlobByKey(key);
    } catch (cleanupError) {
      console.error('Failed to remove temporary ComfyUI audio:', cleanupError);
      throw new Error(`Audio import failed (${String(error)}) and temporary audio cleanup failed (${String(cleanupError)}).`);
    }
    throw error;
  }
}
