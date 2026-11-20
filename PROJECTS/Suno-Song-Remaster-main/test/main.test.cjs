const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs/promises');
const os = require('node:os');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const Module = require('node:module');

test('filesystem IPC requires dialog authorization and avoids batch collisions', async () => {
  const directory = await fs.mkdtemp(path.join(os.tmpdir(), 'suno-ipc-test-'));
  const input = path.join(directory, 'input.wav');
  const save = path.join(directory, 'single.wav');
  const handlers = new Map();
  const dialogs = [];
  let window;

  const electron = {
    app: {
      isPackaged: true,
      whenReady: () => Promise.resolve(),
      on: () => {},
      getAppPath: () => directory
    },
    BrowserWindow: class {
      constructor() {
        this.webContents = {
          mainFrame: { url: pathToFileURL(path.join(__dirname, '../dist/index.html')).href },
          on: () => {},
          setWindowOpenHandler: () => {},
          openDevTools: () => {}
        };
        window = this;
      }
      loadFile() {}
      loadURL() {}
    },
    ipcMain: { handle: (name, handler) => handlers.set(name, handler) },
    dialog: {
      showOpenDialog: async () => dialogs.shift(),
      showSaveDialog: async () => dialogs.shift()
    }
  };
  const originalLoad = Module._load;
  try {
    await fs.writeFile(input, Buffer.from([1, 2, 3]));
    Module._load = function (request, ...args) {
      return request === 'electron' ? electron : originalLoad.call(this, request, ...args);
    };
    require('../electron/main.js');
    await new Promise(resolve => setImmediate(resolve));
    const event = { sender: window.webContents, senderFrame: window.webContents.mainFrame };
    const invoke = (name, ...args) => handlers.get(name)(event, ...args);

    await assert.rejects(invoke('read-audio-file', input), /not selected/);
    dialogs.push({ filePaths: [input] });
    await invoke('select-file');
    assert.deepEqual(await invoke('read-audio-file', input), new Uint8Array([1, 2, 3]));
    await assert.rejects(handlers.get('read-audio-file')(
      { sender: {}, senderFrame: window.webContents.mainFrame }, input
    ), /Untrusted/);

    await assert.rejects(invoke('write-file', save, new Uint8Array([4])), /not selected/);
    dialogs.push({ filePath: save });
    await invoke('save-file');
    await invoke('write-file', save, new Uint8Array([4]));
    assert.deepEqual(await fs.readFile(save), Buffer.from([4]));

    await assert.rejects(invoke('write-batch-file', directory, 'track', new Uint8Array([5])), /not selected/);
    dialogs.push({ filePaths: [directory] });
    await invoke('select-directory');
    const first = await invoke('write-batch-file', directory, 'track', new Uint8Array([5]));
    const second = await invoke('write-batch-file', directory, 'track', new Uint8Array([6]));
    assert.notEqual(first.path, second.path);
    assert.deepEqual(await fs.readFile(first.path), Buffer.from([5]));
    assert.deepEqual(await fs.readFile(second.path), Buffer.from([6]));
  } finally {
    Module._load = originalLoad;
    await fs.rm(directory, { recursive: true, force: true });
  }
});
