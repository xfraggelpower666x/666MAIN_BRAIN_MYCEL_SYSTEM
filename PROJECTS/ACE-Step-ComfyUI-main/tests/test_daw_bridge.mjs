import assert from 'node:assert/strict';
import test from 'node:test';
import { handleDawMessage } from '../js/daw_bridge_core.mjs';

test('only the authorized parent can capture a workflow', async () => {
    const replies = [];
    const parent = { postMessage: (data, origin) => replies.push({ data, origin }) };
    const host = { location: { origin: 'http://127.0.0.1:8189' }, parent };
    const app = { graph: { serialize: () => ({ nodes: [] }) } };
    const event = {
        source: parent, origin: 'http://127.0.0.1:5174',
        data: { channel: 'ace-daw-comfy-v1', id: 'id', action: 'capture' },
    };
    await handleDawMessage(app, host, { ...event, origin: 'https://evil.example' });
    await handleDawMessage(app, host, { ...event, source: {} });
    assert.equal(replies.length, 0);
    await handleDawMessage(app, host, event);
    assert.deepEqual(replies[0].data.workflow, { nodes: [] });
    await handleDawMessage(app, host, { ...event, data: { ...event.data, action: 'restore' } });
    assert.equal(replies.length, 1);
    app.graph.serialize = () => ({ nodes: 'bad' });
    await handleDawMessage(app, host, event);
    assert.equal(replies.at(-1).data.ok, false);
});
