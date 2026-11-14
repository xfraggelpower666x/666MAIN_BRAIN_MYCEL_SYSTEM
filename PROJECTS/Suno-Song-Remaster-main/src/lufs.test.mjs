import assert from 'node:assert/strict';
import test from 'node:test';
import { calculateRelativeThreshold } from './lufsGate.mjs';

function energyAtLufs(lufs) {
  return Math.pow(10, (lufs + 0.691) / 10);
}

test('relative gate uses mean block energy instead of mean LUFS', () => {
  const energies = [
    energyAtLufs(-10),
    energyAtLufs(-30)
  ];
  const expected = -0.691 + 10 * Math.log10(
    energies.reduce((sum, energy) => sum + energy, 0) / energies.length
  ) - 10;

  assert.ok(Math.abs(calculateRelativeThreshold(energies) - expected) < 1e-10);
  assert.ok(calculateRelativeThreshold(energies) > -30);
});

test('relative gate ignores blocks below the absolute threshold', () => {
  assert.ok(Math.abs(
    calculateRelativeThreshold([energyAtLufs(-20), energyAtLufs(-80)]) - (-30)
  ) < 1e-10);
  assert.equal(calculateRelativeThreshold([energyAtLufs(-80)]), -Infinity);
});
