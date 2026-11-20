'use strict'

const test = require('node:test')
const assert = require('node:assert/strict')
const { parseArguments } = require('../cli.cjs')

test('translates legacy VB6 switches and separates file paths', () => {
  const parsed = parseArguments([
    '/o', '/g', '5', '/t', '/p', '/s', 's',
    'C:\\Music\\one.mp3', 'C:\\Music\\two.mp3'
  ])

  assert.deepEqual(parsed, {
    engineArgs: ['-o', '-g', '5', '-t', '-p', '-s', 's'],
    filePaths: ['C:\\Music\\one.mp3', 'C:\\Music\\two.mp3']
  })
})

test('converts VB6 single-channel gain switches to the JavaScript engine form', () => {
  assert.deepEqual(parseArguments(['/l0', '-4', 'C:\\Music\\left.mp3']), {
    engineArgs: ['-l', '0', '-4'],
    filePaths: ['C:\\Music\\left.mp3']
  })
})

test('rejects switches with missing values instead of running a partial command', () => {
  assert.throws(() => parseArguments(['/g']), /Missing value after \/g/)
  assert.throws(() => parseArguments(['/l1']), /Missing gain value after \/l1/)
})
