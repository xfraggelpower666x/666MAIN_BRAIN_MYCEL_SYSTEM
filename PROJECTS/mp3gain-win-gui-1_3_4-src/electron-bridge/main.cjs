'use strict'

const { app, BrowserWindow, ipcMain } = require('electron')
const fs = require('node:fs')
const path = require('node:path')
const { pathToFileURL } = require('node:url')
const { parseArguments } = require('./cli.cjs')

let bridgeWindow
let exiting = false

app.disableHardwareAcceleration()

function getArguments() {
  const args = process.argv.slice(1)
  const appPath = path.resolve(app.getAppPath())

  if (args.length > 0) {
    const firstArg = args[0]
    if (firstArg === '.' || path.resolve(firstArg) === appPath) {
      args.shift()
    }
  }

  if (args[0] === '--') {
    args.shift()
  }

  return args
}

function writeOutput(stream, message) {
  const output = String(message)
  fs.writeSync(stream.fd, output.endsWith('\n') ? output : `${output}\r\n`)
}

function translateOutput(message, files) {
  let output = String(message)
  for (const file of files) {
    output = output.split(`/mp3/${file.name}`).join(file.path)
    output = output.split(file.name).join(file.path)
  }
  return output
}

function fail(error) {
  writeOutput(process.stderr, error && error.message ? error.message : error)
  finish(1)
}

function finish(exitCode) {
  if (exiting) return
  exiting = true
  process.exitCode = exitCode
  if (exitCode !== 0) {
    if (bridgeWindow && !bridgeWindow.isDestroyed()) {
      bridgeWindow.once('closed', () => app.exit(exitCode))
      bridgeWindow.close()
    } else {
      app.exit(exitCode)
    }
    return
  }
  app.quit()
}

async function run() {
  const { engineArgs, filePaths } = parseArguments(getArguments())
  const workerPath = path.join(process.resourcesPath, 'engine', 'mp3gain-worker.js')
  if (engineArgs.length === 1 && engineArgs[0] === '-v' && filePaths.length === 0) {
    if (!fs.existsSync(workerPath)) {
      throw new Error(`MP3Gain JavaScript worker not found: ${workerPath}`)
    }
    writeOutput(process.stdout, 'mp3gain.js engine version 1.1.0')
    finish(0)
    return
  }

  const files = filePaths.map((filePath, index) => {
    const absolutePath = path.resolve(filePath)
    const stat = fs.statSync(absolutePath)
    if (!stat.isFile()) {
      throw new Error(`Not a file: ${filePath}`)
    }

    const basename = path.basename(absolutePath)
    const name = `${String(index).padStart(6, '0')}-${basename}`
    return {
      name,
      path: absolutePath,
      data: fs.readFileSync(absolutePath),
      accessedAt: stat.atime,
      modifiedAt: stat.mtime
    }
  })

  const fileByName = new Map(files.map((file) => [file.name, file]))
  const workerUrl = pathToFileURL(workerPath).href

  ipcMain.on('engine:output', (event, output) => {
    if (event.sender !== bridgeWindow.webContents) return
    writeOutput(
      output.stream === 'stderr' ? process.stderr : process.stdout,
      translateOutput(output.text, files)
    )
  })

  ipcMain.on('engine:error', (event, message) => {
    if (event.sender !== bridgeWindow.webContents) return
    fail(new Error(message))
  })

  ipcMain.on('engine:result', async (event, results) => {
    if (event.sender !== bridgeWindow.webContents) return
    try {
      if (!Array.isArray(results) || results.length !== files.length) {
        throw new Error('The MP3Gain engine returned an incomplete file list.')
      }

      for (const result of results) {
        const file = fileByName.get(result.name)
        if (!file || result.data === undefined) {
          throw new Error(`Unexpected result from MP3Gain engine: ${result.name}`)
        }
        const outputData = Buffer.from(result.data)
        if (Buffer.compare(file.data, outputData) !== 0) {
          fs.writeFileSync(file.path, outputData)
        }
        if (engineArgs.includes('-p')) {
          fs.utimesSync(file.path, file.accessedAt, file.modifiedAt)
        }
      }
      finish(0)
    } catch (error) {
      fail(error)
    }
  })

  bridgeWindow = new BrowserWindow({
    show: false,
    webPreferences: {
      preload: path.join(__dirname, 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true
    }
  })

  bridgeWindow.webContents.once('did-finish-load', () => {
    bridgeWindow.webContents.send('engine:run', {
      args: engineArgs,
      files: files.map(({ name, data }) => ({ name, data })),
      workerUrl
    })
  })

  await bridgeWindow.loadFile(path.join(__dirname, 'bridge.html'))
}

app.whenReady().then(run).catch(fail)
