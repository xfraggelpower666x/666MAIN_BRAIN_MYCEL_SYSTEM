const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { pathToFileURL } = require('url');

let mainWindow;
const authorizedReadPaths = new Set();
const authorizedSavePaths = new Set();
const authorizedOutputDirectories = new Set();

function normalizePath(filePath) {
  const resolved = path.resolve(filePath);
  return process.platform === 'win32' ? resolved.toLowerCase() : resolved;
}

function assertTrustedSender(event) {
  const frameUrl = event.senderFrame?.url;
  const trustedUrl = frameUrl === pathToFileURL(path.join(__dirname, '../dist/index.html')).href ||
    (!app.isPackaged && frameUrl && new URL(frameUrl).origin === 'http://localhost:5173');
  if (!mainWindow || event.sender !== mainWindow.webContents ||
      event.senderFrame !== mainWindow.webContents.mainFrame || !trustedUrl) {
    throw new Error('Untrusted IPC sender');
  }
}

function registerHandler(channel, handler) {
  ipcMain.handle(channel, async (event, ...args) => {
    assertTrustedSender(event);
    return handler(...args);
  });
}

function toBuffer(data) {
  if (data instanceof ArrayBuffer) return Buffer.from(data);
  if (ArrayBuffer.isView(data)) {
    return Buffer.from(data.buffer, data.byteOffset, data.byteLength);
  }
  throw new Error('Invalid file data');
}

const previewDir = path.join(os.tmpdir(), 'spotify-worthy-preview');
if (!fs.existsSync(previewDir)) {
  fs.mkdirSync(previewDir, { recursive: true });
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1100,
    height: 800,
    minWidth: 1050,
    minHeight: 750,
    frame: false,
    titleBarStyle: 'hidden',
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    backgroundColor: '#0a0a0a',
    icon: path.join(__dirname, '../image.png')
  });

  // Always try to load from dist first, fall back to dev server
  const distPath = path.join(__dirname, '../dist/index.html');
  if (fs.existsSync(distPath)) {
    mainWindow.loadFile(distPath);
  } else if (!app.isPackaged) {
    mainWindow.loadURL('http://localhost:5173');
  } else {
    mainWindow.loadFile(distPath);
  }
  
  if (!app.isPackaged) {
    mainWindow.webContents.openDevTools();
  }
}

// Window control handlers
registerHandler('window-minimize', () => mainWindow.minimize());
registerHandler('window-maximize', () => {
  mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
});
registerHandler('window-close', () => mainWindow.close());

// File selection
registerHandler('select-file', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'aac', 'm4a'] }]
  });
  const filePath = result.filePaths[0] || null;
  if (filePath) authorizedReadPaths.add(normalizePath(filePath));
  return filePath;
});

// Batch file selection (multiple files)
registerHandler('select-files', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [{ name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'aac', 'm4a'] }]
  });
  result.filePaths.forEach(filePath => authorizedReadPaths.add(normalizePath(filePath)));
  return result.filePaths || [];
});

// Select output directory for batch export
registerHandler('select-directory', async () => {
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  const directory = result.filePaths[0] || null;
  if (directory) authorizedOutputDirectories.add(normalizePath(directory));
  return directory;
});

// Save file dialog
registerHandler('save-file', async () => {
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [{ name: 'WAV File', extensions: ['wav'] }]
  });
  const filePath = result.filePath || null;
  if (filePath) authorizedSavePaths.add(normalizePath(filePath));
  return filePath;
});

// Read audio file
registerHandler('read-audio-file', async (filePath) => {
  if (typeof filePath !== 'string' || !authorizedReadPaths.has(normalizePath(filePath))) {
    throw new Error('File was not selected through the file dialog');
  }

  try {
    const buffer = await fs.promises.readFile(filePath);
    return new Uint8Array(buffer);
  } catch (error) {
    throw new Error(`Failed to read file: ${error.message}`);
  }
});

// Write a single export to the path explicitly approved in the save dialog.
registerHandler('write-file', async (filePath, data) => {
  if (typeof filePath !== 'string' || !authorizedSavePaths.has(normalizePath(filePath))) {
    throw new Error('Export path was not selected through the save dialog');
  }

  try {
    await fs.promises.writeFile(filePath, toBuffer(data));
    return { success: true };
  } catch (error) {
    throw new Error(`Failed to write file: ${error.message}`);
  }
});

// Batch exports are created exclusively in a dialog-authorized directory.
registerHandler('write-batch-file', async (directory, baseName, data) => {
  if (typeof directory !== 'string' ||
      !authorizedOutputDirectories.has(normalizePath(directory))) {
    throw new Error('Output directory was not selected through the directory dialog');
  }
  if (typeof baseName !== 'string') throw new Error('Invalid output filename');

  const safeBaseName = baseName
    .replace(/[<>:"/\\|?*\x00-\x1f]/g, '_')
    .replace(/[. ]+$/g, '')
    .trim() || 'audio';
  const buffer = toBuffer(data);

  for (let suffix = 1; ; suffix++) {
    const numberedSuffix = suffix === 1 ? '' : ` (${suffix})`;
    const outputPath = path.join(directory, `${safeBaseName}_mastered${numberedSuffix}.wav`);
    let handle;
    try {
      handle = await fs.promises.open(outputPath, 'wx');
    } catch (error) {
      if (error.code === 'EEXIST') continue;
      throw new Error(`Failed to create batch export: ${error.message}`);
    }

    try {
      await handle.writeFile(buffer);
      return { success: true, path: outputPath };
    } catch (error) {
      await handle.close();
      handle = null;
      await fs.promises.unlink(outputPath);
      throw new Error(`Failed to write batch export: ${error.message}`);
    } finally {
      if (handle) await handle.close();
    }
  }
});

// Get system info
registerHandler('get-system-info', () => ({
  platform: process.platform,
  arch: process.arch,
  isPackaged: app.isPackaged,
  appPath: app.getAppPath(),
  electronVersion: process.versions.electron,
  nodeVersion: process.versions.node
}));

app.whenReady().then(() => {
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

app.on('before-quit', () => {
  try {
    if (fs.existsSync(previewDir)) {
      fs.rmSync(previewDir, { recursive: true, force: true });
    }
  } catch (e) {
    console.error('Cleanup error:', e);
  }
});
