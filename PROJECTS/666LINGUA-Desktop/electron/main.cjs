'use strict';

const { app, BrowserWindow, clipboard, ipcMain, Menu, protocol, session } = require('electron');
const { createConnection } = require('node:net');
const { createInterface } = require('node:readline');

const origin = 'lingua://desktop';
const pending = new Map();
let nextId = 0;
let closing = false;

protocol.registerSchemesAsPrivileged([
  { scheme: 'lingua', privileges: { standard: true, secure: true, supportFetchAPI: true } }
]);

app.setName('666LINGUA');
app.commandLine.appendSwitch('disable-background-networking');
app.setPath('userData', process.argv[process.argv.indexOf('--lingua-profile') + 1]);
const bridgePath = process.env.LINGUA_BRIDGE_PIPE;
if (!bridgePath) throw new Error('Der lokale 666LINGUA-Datenkanal fehlt.');
const bridge = createConnection(bridgePath);
bridge.on('error', (error) => {
  if (closing) return;
  console.error('Electron-Datenkanal:', error);
  app.exit(1);
});
const responses = createInterface({ input: bridge, terminal: false });
responses.on('line', (line) => {
  try {
    const { id, status, headers, body } = JSON.parse(line);
    const resolve = pending.get(id);
    if (!resolve) throw new Error('Unerwartete Antwort-ID');
    const data = status === 204 || status === 304 ? null : Buffer.from(body || '', 'base64');
    const response = new Response(data, { status, headers });
    pending.delete(id);
    resolve(response);
  } catch (error) {
    console.error(error);
    app.exit(1);
  }
});
responses.on('close', () => {
  if (!closing) {
    console.error('Der lokale 666LINGUA-Datenkanal wurde geschlossen.');
    app.exit(1);
  }
});
app.on('before-quit', () => { closing = true; });
app.on('window-all-closed', () => app.quit());

function isLocal(url) {
  const parsed = new URL(url);
  return parsed.protocol === 'lingua:' && parsed.host === 'desktop' &&
    !parsed.username && !parsed.password;
}

async function serve(request) {
  const { url, method } = request;
  if (!isLocal(url) || !['GET', 'POST'].includes(method)) return new Response(null, { status: 403 });
  const { pathname, search } = new URL(url);
  const body = method === 'POST' ? await request.text() : '';
  const isAPI = pathname.startsWith('/api/');
  if (isAPI && request.headers.get('X-Lingua-Session') !== 'desktop') {
    return new Response(null, { status: 403 });
  }
  if (method === 'POST' && (!isAPI || request.headers.get('Content-Type') !== 'application/json')) {
    return new Response(null, { status: 400 });
  }
  if (Buffer.byteLength(body, 'utf8') > 200000) return new Response(null, { status: 413 });

  return new Promise((resolve) => {
    const id = ++nextId;
    pending.set(id, resolve);
    bridge.write(JSON.stringify({ id, method, path: pathname + search, body }) + '\n');
  });
}

app.whenReady().then(async () => {
  Menu.setApplicationMenu(null);
  session.defaultSession.setPermissionRequestHandler((_contents, _permission, callback) => callback(false));
  session.defaultSession.setPermissionCheckHandler(() => false);
  protocol.handle('lingua', serve);

  const win = new BrowserWindow({
    title: '666LINGUA',
    width: 1280,
    height: 800,
    minWidth: 480,
    minHeight: 480,
    fullscreen: !process.argv.includes('--lingua-windowed'),
    show: false,
    backgroundColor: '#050b1b',
    webPreferences: {
      preload: require('node:path').join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      sandbox: true,
      nodeIntegration: false,
      webSecurity: true
    }
  });
  win.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));
  win.webContents.on('will-navigate', (event) => event.preventDefault());
  win.webContents.on('will-redirect', (event, url) => {
    if (!isLocal(url)) event.preventDefault();
  });
  win.webContents.on('render-process-gone', (_event, details) => {
    if (!closing && details.reason !== 'clean-exit') {
      console.error('Electron-Anzeige beendet:', details.reason);
      app.exit(1);
    }
  });
  function verifySender(event) {
    const frame = event.senderFrame;
    if (event.sender !== win.webContents || !frame || frame.parent || !isLocal(frame.url)) {
      throw new Error('Ungültiger Fensterkontext');
    }
  }
  ipcMain.handle('lingua:copy', (event, text) => {
    verifySender(event);
    if (typeof text !== 'string' || text.length > 200000) throw new Error('Ungültiger Text');
    clipboard.writeText(text);
    return true;
  });
  ipcMain.handle('lingua:fullscreen', (event) => {
    verifySender(event);
    win.setFullScreen(!win.isFullScreen());
  });
  ipcMain.handle('lingua:quit', (event) => {
    verifySender(event);
    setImmediate(() => app.quit());
  });
  win.once('ready-to-show', () => win.show());
  await win.loadURL(origin + '/');
}).catch((error) => {
  console.error(error);
  app.exit(1);
});
