const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const fs = require('fs');
const os = require('os');
const { fileURLToPath } = require('url');

let mainWindow;

const previewDir = path.join(os.tmpdir(), 'spotify-worthy-preview');
const allowedOutputDirectories = new Set();
const allowedOutputFiles = new Set();
const audioExtensions = new Set(['.mp3', '.wav', '.flac', '.aac', '.m4a']);

if (!fs.existsSync(previewDir)) {
  fs.mkdirSync(previewDir, { recursive: true });
}

function isAppUrl(value) {
  try {
    const url = new URL(value);
    if (!app.isPackaged && url.origin === 'http://localhost:5173') return true;
    return url.protocol === 'file:' &&
      path.resolve(fileURLToPath(url)) === path.resolve(__dirname, '../dist/index.html');
  } catch {
    return false;
  }
}

function assertTrustedSender(event) {
  if (!mainWindow || event.sender !== mainWindow.webContents ||
      event.senderFrame !== mainWindow.webContents.mainFrame ||
      !isAppUrl(event.senderFrame.url)) {
    throw new Error('Untrusted IPC sender');
  }
}

function getPathKey(filePath) {
  const resolvedPath = path.resolve(filePath);
  return process.platform === 'win32' ? resolvedPath.toLowerCase() : resolvedPath;
}

function validateAudioPath(filePath) {
  if (typeof filePath !== 'string' || !path.isAbsolute(filePath) ||
      !audioExtensions.has(path.extname(filePath).toLowerCase())) {
    throw new Error('Invalid audio file path');
  }
  const stats = fs.statSync(filePath);
  if (!stats.isFile()) throw new Error('Audio path is not a file');
  return filePath;
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
      sandbox: true,
      webSecurity: true,
      allowRunningInsecureContent: false,
      webviewTag: false,
      preload: path.join(__dirname, 'preload.js')
    },
    backgroundColor: '#0a0a0a',
    icon: path.join(__dirname, '../image.png')
  });

  mainWindow.webContents.on('will-navigate', (event, url) => {
    if (!isAppUrl(url)) event.preventDefault();
  });
  mainWindow.webContents.on('will-redirect', (event, url) => {
    if (!isAppUrl(url)) event.preventDefault();
  });
  mainWindow.webContents.setWindowOpenHandler(() => ({ action: 'deny' }));

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
ipcMain.handle('window-minimize', (event) => {
  assertTrustedSender(event);
  if (!mainWindow.isDestroyed()) mainWindow.minimize();
});
ipcMain.handle('window-maximize', (event) => {
  assertTrustedSender(event);
  if (mainWindow.isDestroyed()) return;
  mainWindow.isMaximized() ? mainWindow.unmaximize() : mainWindow.maximize();
});
ipcMain.handle('window-close', (event) => {
  assertTrustedSender(event);
  if (!mainWindow.isDestroyed()) mainWindow.close();
});

// File selection
ipcMain.handle('select-file', async (event) => {
  assertTrustedSender(event);
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile'],
    filters: [{ name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'aac', 'm4a'] }]
  });
  return result.filePaths[0] || null;
});

// Batch file selection (multiple files)
ipcMain.handle('select-files', async (event) => {
  assertTrustedSender(event);
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openFile', 'multiSelections'],
    filters: [{ name: 'Audio Files', extensions: ['mp3', 'wav', 'flac', 'aac', 'm4a'] }]
  });
  return result.filePaths || [];
});

// Select output directory for batch export
ipcMain.handle('select-directory', async (event) => {
  assertTrustedSender(event);
  const result = await dialog.showOpenDialog(mainWindow, {
    properties: ['openDirectory']
  });
  const directory = result.filePaths[0] || null;
  if (directory) allowedOutputDirectories.add(getPathKey(directory));
  return directory;
});

// Save file dialog
ipcMain.handle('save-file', async (event) => {
  assertTrustedSender(event);
  const result = await dialog.showSaveDialog(mainWindow, {
    filters: [{ name: 'WAV File', extensions: ['wav'] }]
  });
  const filePath = result.filePath || null;
  if (filePath) allowedOutputFiles.add(getPathKey(filePath));
  return filePath;
});

// Read audio file
ipcMain.handle('read-audio-file', async (event, filePath) => {
  assertTrustedSender(event);
  try {
    validateAudioPath(filePath);
    return fs.readFileSync(filePath);
  } catch (error) {
    throw new Error(`Failed to read file: ${error.message}`);
  }
});

// Write file (for WAV export)
ipcMain.handle('write-file', async (event, filePath, data) => {
  assertTrustedSender(event);
  try {
    if (typeof filePath !== 'string' || !path.isAbsolute(filePath) ||
        path.extname(filePath).toLowerCase() !== '.wav') {
      throw new Error('Invalid WAV output path');
    }
    const outputPath = path.resolve(filePath);
    const outputDirectory = getPathKey(path.dirname(outputPath));
    if (!allowedOutputDirectories.has(outputDirectory) &&
        !allowedOutputFiles.has(getPathKey(outputPath))) {
      throw new Error('Output path was not selected in a save dialog');
    }
    if (!(data instanceof ArrayBuffer) && !(data instanceof Uint8Array)) {
      throw new Error('WAV data must be an ArrayBuffer or typed array');
    }
    const buffer = data instanceof ArrayBuffer
      ? Buffer.from(data)
      : Buffer.from(data.buffer, data.byteOffset, data.byteLength);
    fs.writeFileSync(outputPath, buffer, { flag: 'wx' });
    return { success: true };
  } catch (error) {
    if (error.code === 'EEXIST') {
      throw new Error('Output already exists. Choose a different name or directory.');
    }
    throw new Error(`Failed to write file: ${error.message}`);
  }
});

// Get system info
ipcMain.handle('get-system-info', (event) => {
  assertTrustedSender(event);
  return {
    platform: process.platform,
    arch: process.arch,
    isPackaged: app.isPackaged,
    appPath: app.getAppPath(),
    electronVersion: process.versions.electron,
    nodeVersion: process.versions.node
  };
});

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
