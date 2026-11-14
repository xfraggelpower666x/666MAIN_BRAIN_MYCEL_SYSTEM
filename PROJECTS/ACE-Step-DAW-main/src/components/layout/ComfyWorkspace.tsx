import { useEffect, useRef, useState } from 'react';
import { Button } from '../ui/Button';
import { ComfyExchange } from './ComfyExchange';
import { requireComfyResponse } from '../../services/comfyGateway';
import { isTauri } from '../../utils/tauri';

const COMFY_URL = 'http://127.0.0.1:8189';
const CHECK_TIMEOUT_MS = 5000;
const HEALTH_INTERVAL_MS = 10000;

type ConnectionState = 'disconnected' | 'checking' | 'connected' | 'error';

async function checkService(signal: AbortSignal) {
  const response = await fetch(`${COMFY_URL}/system_stats`, {
    signal,
    redirect: 'error',
    credentials: 'omit',
    cache: 'no-store',
  });
  await requireComfyResponse(response);
  const data: unknown = await response.json();
  if (!data || typeof data !== 'object' || !('system' in data) || !('devices' in data)) {
    throw new Error('The local service did not return ComfyUI system information.');
  }
}

export function ComfyWorkspace() {
  const [status, setStatus] = useState<ConnectionState>('disconnected');
  const [error, setError] = useState('');
  const [serviceUnavailable, setServiceUnavailable] = useState(false);
  const activeCheck = useRef<AbortController | null>(null);
  const frameRef = useRef<HTMLIFrameElement>(null);
  const allowNativeClose = useRef(false);

  useEffect(() => () => {
    const controller = activeCheck.current;
    activeCheck.current = null;
    controller?.abort();
  }, []);

  useEffect(() => {
    if (status !== 'connected') return;
    const warnBeforeClose = (event: BeforeUnloadEvent) => {
      if (allowNativeClose.current) return;
      event.preventDefault();
      event.returnValue = '';
    };
    window.addEventListener('beforeunload', warnBeforeClose);
    let active = true;
    let unlisten: (() => void) | undefined;
    if (isTauri()) {
      void import('@tauri-apps/api/window').then(async ({ getCurrentWindow }) => {
        const currentWindow = getCurrentWindow();
        const removeListener = await currentWindow.onCloseRequested(async (event) => {
          if (allowNativeClose.current) return;
          event.preventDefault();
          if (!window.confirm('The ComfyUI editor may contain unsaved changes. Close the application anyway?')) return;
          allowNativeClose.current = true;
          try {
            await currentWindow.close();
          } catch (reason) {
            allowNativeClose.current = false;
            console.error('Failed to close the application after ComfyUI confirmation.', reason);
          }
        });
        if (active) unlisten = removeListener;
        else removeListener();
      }).catch((reason: unknown) => {
        console.error('Failed to protect the ComfyUI editor from native window close.', reason);
      });
    }
    return () => {
      active = false;
      unlisten?.();
      window.removeEventListener('beforeunload', warnBeforeClose);
    };
  }, [status]);

  useEffect(() => {
    if (status !== 'connected') return;
    let active = true;
    let controller: AbortController | null = null;
    let timeout: number | undefined;
    const interval = window.setInterval(async () => {
      if (controller) return;
      controller = new AbortController();
      const current = controller;
      timeout = window.setTimeout(() => current.abort(), CHECK_TIMEOUT_MS);
      try {
        await checkService(current.signal);
        if (active) setServiceUnavailable(false);
      } catch {
        if (active) setServiceUnavailable(true);
      } finally {
        window.clearTimeout(timeout);
        controller = null;
      }
    }, HEALTH_INTERVAL_MS);
    return () => {
      active = false;
      window.clearInterval(interval);
      window.clearTimeout(timeout);
      controller?.abort();
    };
  }, [status]);

  async function connect() {
    activeCheck.current?.abort();
    const controller = new AbortController();
    activeCheck.current = controller;
    setStatus('checking');
    setError('');
    setServiceUnavailable(false);
    const timeout = window.setTimeout(() => controller.abort(), CHECK_TIMEOUT_MS);
    try {
      await checkService(controller.signal);
      if (activeCheck.current === controller) setStatus('connected');
    } catch (reason) {
      if (activeCheck.current === controller) {
        const detail = reason instanceof Error ? reason.message : String(reason);
        setError(`Cannot connect to ComfyUI: ${detail}. Check that ComfyUI and its local gateway are running.`);
        setStatus('error');
      }
    } finally {
      window.clearTimeout(timeout);
      if (activeCheck.current === controller) activeCheck.current = null;
    }
  }

  function disconnect() {
    if (status === 'connected' && !window.confirm(
      'Disconnecting closes the ComfyUI editor. Unsaved workflow changes may be lost. Disconnect anyway?',
    )) return;
    const controller = activeCheck.current;
    activeCheck.current = null;
    controller?.abort();
    setStatus('disconnected');
    setError('');
    setServiceUnavailable(false);
  }

  return (
    <section id="comfy-workspace" className="flex min-h-0 flex-1 flex-col bg-daw-bg" aria-label="ComfyUI workspace" tabIndex={-1}>
      <div className="flex flex-wrap items-center gap-3 border-b border-daw-border-strong bg-daw-surface-2 px-4 py-2">
        <h2 className="text-sm font-medium text-zinc-100">ComfyUI</h2>
        <span className="text-xs text-zinc-300" role="status">
          {status === 'connected' ? (serviceUnavailable ? 'Local service unavailable' : 'Local service responded') : status === 'checking' ? 'Checking local service...' : 'Not connected'}
        </span>
        {status === 'connected' || status === 'checking' ? (
          <Button size="sm" onClick={disconnect}>Disconnect</Button>
        ) : (
          <Button size="sm" onClick={() => void connect()}>{status === 'error' ? 'Retry connection' : 'Connect'}</Button>
        )}
      </div>
      {status === 'connected' && serviceUnavailable && (
        <p className="bg-daw-surface-2 px-4 py-2 text-sm text-red-300" role="alert">
          The local service stopped responding. The editor remains open; restart the service and gateway to reconnect.
        </p>
      )}
      {status === 'connected' && <ComfyExchange frameRef={frameRef} unavailable={serviceUnavailable} />}
      {status === 'connected' ? (
        <iframe
          ref={frameRef}
          title="ComfyUI workflow editor"
          src={COMFY_URL}
          sandbox="allow-scripts allow-same-origin allow-forms allow-downloads"
          className="min-h-0 w-full flex-1 border-0"
        />
      ) : (
        <div className="max-w-2xl px-6 py-6 text-sm text-zinc-300">
          <p>Start your trusted local ComfyUI service and its gateway separately, then connect to open its workflow editor here.</p>
          <p className="mt-2">Connecting does not start or stop either service. The gateway listens on 127.0.0.1:8189.</p>
          {error && <p className="mt-4 text-red-300" role="alert">{error}</p>}
        </div>
      )}
    </section>
  );
}
