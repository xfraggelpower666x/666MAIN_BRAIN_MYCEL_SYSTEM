import { useEffect, useRef, useState, type RefObject } from 'react';
import { useProjectStore } from '../../store/projectStore';
import { downloadBlob } from '../../services/browserDownload';
import { importComfyAudio, listComfyAudio, type ComfyAudioOutput } from '../../services/comfyAudioExchange';
import { captureComfyWorkflow } from '../../services/comfyWorkflowExchange';
import { Button } from '../ui/Button';

export function ComfyExchange({ frameRef, unavailable }: {
  frameRef: RefObject<HTMLIFrameElement | null>;
  unavailable: boolean;
}) {
  const project = useProjectStore((state) => state.project);
  const [outputs, setOutputs] = useState<ComfyAudioOutput[]>([]);
  const [selected, setSelected] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const active = useRef<AbortController | null>(null);

  useEffect(() => () => { active.current?.abort(); }, []);

  async function run(action: (signal: AbortSignal) => Promise<void>) {
    const controller = new AbortController();
    active.current = controller;
    setBusy(true);
    setError('');
    setMessage('');
    try {
      await action(controller.signal);
    } catch (reason) {
      if (!controller.signal.aborted) setError(reason instanceof Error ? reason.message : String(reason));
    } finally {
      if (active.current === controller) {
        active.current = null;
        if (!controller.signal.aborted) setBusy(false);
      }
    }
  }

  async function saveWorkflow(signal: AbortSignal) {
    if (!project || !frameRef.current) throw new Error('Open a project and connect ComfyUI first.');
    const projectId = project.id;
    const workflow = await captureComfyWorkflow(frameRef.current);
    signal.throwIfAborted();
    if (!useProjectStore.getState().saveComfyWorkflow(projectId, workflow)) {
      throw new Error('The active project changed or is read-only.');
    }
    setMessage('Workflow saved in the project. Undo restores the previous snapshot.');
  }

  async function findAudio(signal: AbortSignal) {
    const found = await listComfyAudio(signal);
    setOutputs(found);
    setSelected(found[0]?.id ?? '');
    setMessage(found.length ? `${found.length} audio output(s) found.` : 'No saved or preview audio found in ComfyUI history.');
  }

  async function importAudio(signal: AbortSignal) {
    const output = outputs.find((item) => item.id === selected);
    if (!project || !output) throw new Error('Open a project and select an audio output.');
    await importComfyAudio(output, project.id, signal);
    setMessage('Audio copied to a new DAW track.');
  }

  return (
    <div className="border-b border-daw-border-strong bg-daw-surface-2 px-4 py-2 text-sm text-zinc-300">
      <div className="flex flex-wrap items-center gap-2">
        <Button size="sm" disabled={busy || unavailable || !project} onClick={() => void run(saveWorkflow)}>
          Save workflow to project
        </Button>
        <Button size="sm" disabled={!project?.comfyWorkflow} onClick={() => {
          if (project?.comfyWorkflow) downloadBlob(new Blob([project.comfyWorkflow], { type: 'application/json' }), 'comfy-workflow.json');
        }}>
          Download saved workflow
        </Button>
        <Button size="sm" disabled={busy || unavailable} onClick={() => void run(findAudio)}>Find output audio</Button>
        {outputs.length > 0 && (
          <>
            <label htmlFor="comfy-audio-output">Audio</label>
            <select id="comfy-audio-output" className="max-w-64 bg-daw-bg text-zinc-100" value={selected} onChange={(event) => setSelected(event.target.value)}>
              {outputs.map((output) => <option key={output.id} value={output.id}>{output.filename} ({output.type})</option>)}
            </select>
            <Button size="sm" disabled={busy || unavailable || !project || !selected} onClick={() => void run(importAudio)}>Import to DAW</Button>
          </>
        )}
      </div>
      {message && <p className="mt-2" role="status">{message}</p>}
      {error && <p className="mt-2 text-red-300" role="alert">{error}</p>}
    </div>
  );
}
