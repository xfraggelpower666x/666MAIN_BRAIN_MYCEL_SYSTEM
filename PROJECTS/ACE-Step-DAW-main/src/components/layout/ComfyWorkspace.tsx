import { useEffect, useRef, useState } from 'react';
import { Button } from '../ui/Button';

const COMFY_URL = 'http://127.0.0.1:8188';
const CHECK_TIMEOUT_MS = 5000;

type ConnectionState = 'disconnected' | 'checking' | 'connected' | 'error';

export function ComfyWorkspace() {
  const [status, setStatus] = useState<ConnectionState>('disconnected');
  const [error, setError] = useState('');
  const activeCheck = useRef<AbortController | null>(null);

  useEffect(() => () => {
    const controller = activeCheck.current;
    activeCheck.current = null;
    controller?.abort();
  }, []);

  async function connect() {
    activeCheck.current?.abort();
    const controller = new AbortController();
    activeCheck.current = controller;
    setStatus('checking');
    setError('');
    const timeout = window.setTimeout(() => controller.abort(), CHECK_TIMEOUT_MS);
    try {
      const response = await fetch(`${COMFY_URL}/system_stats`, {
        signal: controller.signal,
        redirect: 'error',
        credentials: 'omit',
        cache: 'no-store',
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data: unknown = await response.json();
      if (!data || typeof data !== 'object' || !('system' in data) || !('devices' in data)) {
        throw new Error('The local service did not return ComfyUI system information.');
      }
      if (activeCheck.current === controller) setStatus('connected');
    } catch (reason) {
      if (activeCheck.current === controller) {
        const detail = reason instanceof Error ? reason.message : String(reason);
        setError(`Cannot connect to ComfyUI: ${detail}. Check that it is running on 127.0.0.1:8188 and allows this app's origin.`);
        setStatus('error');
      }
    } finally {
      window.clearTimeout(timeout);
      if (activeCheck.current === controller) activeCheck.current = null;
    }
  }

  function disconnect() {
    const controller = activeCheck.current;
    activeCheck.current = null;
    controller?.abort();
    setStatus('disconnected');
    setError('');
  }

  return (
    <section className="flex min-h-0 flex-1 flex-col bg-daw-bg" aria-label="ComfyUI workspace">
      <div className="flex flex-wrap items-center gap-3 border-b border-daw-border-strong bg-daw-surface-2 px-4 py-2">
        <h2 className="text-sm font-medium text-zinc-100">ComfyUI</h2>
        <span className="text-xs text-zinc-300" role="status">
          {status === 'connected' ? 'Local service responded' : status === 'checking' ? 'Checking local service...' : 'Not connected'}
        </span>
        {status === 'connected' || status === 'checking' ? (
          <Button size="sm" onClick={disconnect}>Disconnect</Button>
        ) : (
          <Button size="sm" onClick={() => void connect()}>{status === 'error' ? 'Retry connection' : 'Connect'}</Button>
        )}
      </div>
      {status === 'connected' ? (
        <iframe
          title="ComfyUI workflow editor"
          src={COMFY_URL}
          sandbox="allow-scripts allow-same-origin allow-forms allow-downloads"
          className="min-h-0 w-full flex-1 border-0"
        />
      ) : (
        <div className="max-w-2xl px-6 py-6 text-sm text-zinc-300">
          <p>Start your trusted local ComfyUI service separately, then connect to open its workflow editor here.</p>
          <p className="mt-2">Connecting does not start or stop the service. Only the local address 127.0.0.1:8188 is supported.</p>
          {error && <p className="mt-4 text-red-300" role="alert">{error}</p>}
        </div>
      )}
    </section>
  );
}
