export function calculateRelativeThreshold(blockEnergies, absoluteThreshold = -70) {
  const absoluteThresholdEnergy = Math.pow(10, (absoluteThreshold + 0.691) / 10);
  const absoluteGatedEnergies = blockEnergies.filter(energy =>
    Number.isFinite(energy) && energy > absoluteThresholdEnergy
  );
  if (absoluteGatedEnergies.length === 0) return -Infinity;

  const averageEnergy = absoluteGatedEnergies.reduce((sum, energy) => sum + energy, 0) /
    absoluteGatedEnergies.length;
  return -0.691 + 10 * Math.log10(averageEnergy) - 10;
}
