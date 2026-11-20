const ORIGIN = 'http://127.0.0.1:8189';
const CHANNEL = 'ace-daw-comfy-v1';
const MAX_WORKFLOW_LENGTH = 5 * 1024 * 1024;

export function captureComfyWorkflow(frame: HTMLIFrameElement): Promise<string> {
  const target = frame.contentWindow;
  if (!target) return Promise.reject(new Error('The ComfyUI editor is not available.'));
  const id = crypto.randomUUID();
  return new Promise((resolve, reject) => {
    const timer = window.setTimeout(() => {
      window.removeEventListener('message', onMessage);
      reject(new Error('ComfyUI did not respond. Install the ACE-Step ComfyUI nodes and reconnect.'));
    }, 10000);
    function onMessage(event: MessageEvent) {
      if (event.origin !== ORIGIN || event.source !== target || !event.data ||
          event.data.channel !== CHANNEL || event.data.id !== id || event.data.action !== 'capture') return;
      window.clearTimeout(timer);
      window.removeEventListener('message', onMessage);
      if (event.data.ok !== true) {
        reject(new Error(typeof event.data.error === 'string' ? event.data.error : 'ComfyUI could not capture the workflow.'));
        return;
      }
      const workflow: unknown = event.data.workflow;
      if (!workflow || typeof workflow !== 'object' || Array.isArray(workflow) ||
          !('nodes' in workflow) || !Array.isArray(workflow.nodes)) {
        reject(new Error('ComfyUI returned an invalid workflow.'));
        return;
      }
      try {
        const json = JSON.stringify(workflow);
        if (json.length > MAX_WORKFLOW_LENGTH) {
          throw new Error('The workflow is too large to save in this project.');
        }
        resolve(json);
      } catch (error) {
        reject(error);
      }
    }
    window.addEventListener('message', onMessage);
    try {
      target.postMessage({ channel: CHANNEL, id, action: 'capture' }, ORIGIN);
    } catch (error) {
      window.clearTimeout(timer);
      window.removeEventListener('message', onMessage);
      reject(error);
    }
  });
}
