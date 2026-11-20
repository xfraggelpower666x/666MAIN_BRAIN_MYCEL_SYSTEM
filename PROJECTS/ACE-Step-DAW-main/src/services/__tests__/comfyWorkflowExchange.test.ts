import { describe, expect, it, vi } from 'vitest';
import { captureComfyWorkflow } from '../comfyWorkflowExchange';

describe('ComfyUI workflow capture', () => {
  it('accepts only the requested response from the embedded gateway', async () => {
    const frame = document.createElement('iframe');
    document.body.appendChild(frame);
    const target = frame.contentWindow!;
    const post = vi.spyOn(target, 'postMessage').mockImplementation(() => {});
    const pending = captureComfyWorkflow(frame);
    const request = post.mock.calls[0][0] as { id: string };
    const data = { channel: 'ace-daw-comfy-v1', id: request.id, action: 'capture', ok: true, workflow: { nodes: [] } };
    window.dispatchEvent(new MessageEvent('message', { origin: 'https://evil.example', source: target, data }));
    window.dispatchEvent(new MessageEvent('message', { origin: 'http://127.0.0.1:8189', source: window, data }));
    window.dispatchEvent(new MessageEvent('message', { origin: 'http://127.0.0.1:8189', source: target, data: { ...data, id: 'other' } }));
    window.dispatchEvent(new MessageEvent('message', { origin: 'http://127.0.0.1:8189', source: target, data }));
    await expect(pending).resolves.toBe('{"nodes":[]}');
    expect(post).toHaveBeenCalledWith(expect.objectContaining({ action: 'capture' }), 'http://127.0.0.1:8189');
    frame.remove();
  });
});
