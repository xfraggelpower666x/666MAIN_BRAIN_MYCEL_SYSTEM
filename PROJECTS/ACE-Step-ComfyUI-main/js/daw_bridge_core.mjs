const CHANNEL = 'ace-daw-comfy-v1';
const GATEWAY_ORIGIN = 'http://127.0.0.1:8189';
const PARENT_ORIGINS = new Set(['http://127.0.0.1:5174', 'http://tauri.localhost']);
const MAX_WORKFLOW_BYTES = 5 * 1024 * 1024;

function validWorkflow(value) {
    return value !== null && typeof value === 'object' && !Array.isArray(value) && Array.isArray(value.nodes);
}

export async function handleDawMessage(app, host, event) {
    if (host.location.origin !== GATEWAY_ORIGIN || host.parent === host ||
        event.source !== host.parent || !PARENT_ORIGINS.has(event.origin)) return;
    const data = event.data;
    if (!data || data.channel !== CHANNEL || typeof data.id !== 'string' ||
        data.action !== 'capture') return;
    const response = { channel: CHANNEL, id: data.id, action: data.action };
    try {
        const workflow = app.graph.serialize();
        if (!validWorkflow(workflow) || JSON.stringify(workflow).length > MAX_WORKFLOW_BYTES) {
            throw new Error('Invalid or oversized workflow.');
        }
        response.workflow = workflow;
        response.ok = true;
    } catch (error) {
        response.ok = false;
        response.error = error instanceof Error ? error.message : String(error);
    }
    host.parent.postMessage(response, event.origin);
}
