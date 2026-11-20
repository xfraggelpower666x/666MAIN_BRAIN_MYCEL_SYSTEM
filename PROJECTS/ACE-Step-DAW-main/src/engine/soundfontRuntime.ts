import type { WorkletSynthesizer } from 'spessasynth_lib';

let processorUrlPromise: Promise<string> | undefined;
const loadedContexts = new WeakMap<BaseAudioContext, Promise<void>>();

function getProcessorUrl(): Promise<string> {
  processorUrlPromise ??= import('spessasynth_lib/dist/spessasynth_processor.min.js?url')
    .then((module) => module.default)
    .catch((error: unknown) => {
      processorUrlPromise = undefined;
      throw error;
    });
  return processorUrlPromise;
}

export async function loadSoundfontWorklet(context: BaseAudioContext): Promise<void> {
  const existing = loadedContexts.get(context);
  if (existing) return existing;

  const loading = getProcessorUrl()
    .then((url) => context.audioWorklet.addModule(url))
    .catch((error: unknown) => {
      loadedContexts.delete(context);
      throw error;
    });
  loadedContexts.set(context, loading);
  return loading;
}

export async function createSoundfontSynth(context: BaseAudioContext): Promise<WorkletSynthesizer> {
  await loadSoundfontWorklet(context);
  const { WorkletSynthesizer: WorkletSynthesizerClass } = await import('spessasynth_lib');
  const synth = new WorkletSynthesizerClass(context, { eventsEnabled: false });
  await synth.isReady;
  return synth;
}
