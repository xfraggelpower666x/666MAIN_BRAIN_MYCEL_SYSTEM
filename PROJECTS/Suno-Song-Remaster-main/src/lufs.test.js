import test from 'node:test';
import assert from 'node:assert/strict';
import { calculateIntegratedLoudness } from './lufs.js';

test('relative gating uses mean block energy rather than mean LUFS', () => {
  const integrated = calculateIntegratedLoudness([1, 0.01, 0.01, 0.01]);
  assert.ok(Math.abs(integrated - -0.691) < 1e-9);
});

test('absolute gating excludes blocks below -70 LUFS', () => {
  assert.equal(calculateIntegratedLoudness([1e-10]), -Infinity);
});
