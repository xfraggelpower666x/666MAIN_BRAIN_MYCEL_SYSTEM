'use strict'

const OPTION_MAP = new Map([
  ['/a', '-a'],
  ['/c', '-c'],
  ['/f', '-f'],
  ['/h', '-h'],
  ['/?', '-?'],
  ['/k', '-k'],
  ['/o', '-o'],
  ['/p', '-p'],
  ['/q', '-q'],
  ['/r', '-r'],
  ['/t', '-t'],
  ['/T', '-T'],
  ['/u', '-u'],
  ['/v', '-v'],
  ['/w', '-w'],
  ['/x', '-x']
])

function parseArguments(argv) {
  const engineArgs = []
  const filePaths = []
  let literalPaths = false

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index]

    if (literalPaths) {
      filePaths.push(arg)
      continue
    }

    if (arg === '--') {
      literalPaths = true
      continue
    }

    if (arg === '/l0' || arg === '/l1') {
      const gain = argv[index + 1]
      if (gain === undefined) {
        throw new Error(`Missing gain value after ${arg}`)
      }
      engineArgs.push('-l', arg.slice(-1), gain)
      index += 1
      continue
    }

    const mappedOption = OPTION_MAP.get(arg)
    if (mappedOption) {
      engineArgs.push(mappedOption)
      continue
    }

    if (arg === '/g' || arg === '/d' || arg === '/m' || arg === '/s') {
      const value = argv[index + 1]
      if (value === undefined) {
        throw new Error(`Missing value after ${arg}`)
      }
      engineArgs.push(`-${arg.slice(1)}`, value)
      index += 1
      continue
    }

    if (arg === '-l') {
      const channel = argv[index + 1]
      const gain = argv[index + 2]
      if (channel === undefined || gain === undefined) {
        throw new Error('Expected channel and gain values after -l')
      }
      engineArgs.push(arg, channel, gain)
      index += 2
      continue
    }

    if (arg.startsWith('-')) {
      engineArgs.push(arg)
      continue
    }

    filePaths.push(arg)
  }

  return { engineArgs, filePaths }
}

module.exports = { parseArguments }
