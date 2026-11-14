'use strict'

window.engineBridge.onRun((task) => {
  try {
    const worker = new Worker(task.workerUrl)

    worker.onmessage = (event) => {
      const result = event.data
      if (Array.isArray(result)) {
        worker.terminate()
        window.engineBridge.result(result)
      } else if (result && typeof result.stdout === 'string') {
        window.engineBridge.output('stdout', result.stdout)
      } else if (result && typeof result.stderr === 'string') {
        window.engineBridge.output('stderr', result.stderr)
      }
    }

    worker.onerror = (event) => {
      worker.terminate()
      window.engineBridge.error(event.message || 'The MP3Gain worker failed.')
    }

    worker.postMessage({
      files: task.files.map((file) => ({
        name: file.name,
        data: new Uint8Array(file.data)
      })),
      arguments: task.args
    })
  } catch (error) {
    window.engineBridge.error(error.message || String(error))
  }
})
