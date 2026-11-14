'use strict';

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

function writeReleaseArtifactHashes(distDir = path.join(__dirname, '..', 'dist')) {
  const packagedDir = path.join(distDir, 'win-unpacked');
  const candidates = [
    'SoundwaveStudio-portable-win-x64.zip',
    'RADIO-WAVE-v6.66-Setup.exe',
    'RADIO-WAVE-v6.66-Portable.exe'
  ].map(name => path.join(distDir, name));
  if (fs.existsSync(packagedDir)) {
    const appExe = fs.readdirSync(packagedDir).find(file => /\.exe$/i.test(file));
    if (appExe) candidates.push(path.join(packagedDir, appExe));
  }
  const artifacts = candidates.filter(file => fs.existsSync(file));
  if (!artifacts.some(file => path.basename(file) === 'RADIO-WAVE-v6.66-Setup.exe')) {
    throw new Error('NSIS installer missing; release hash manifest was not written.');
  }

  const lines = artifacts.map(file => {
    const digest = crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
    return `${digest}  ${path.relative(distDir, file)}`;
  });
  const manifestPath = path.join(distDir, 'RELEASE_ARTIFACT_SHA256SUMS.txt');
  fs.writeFileSync(manifestPath, `${lines.join('\n')}\n`, 'utf8');
  return manifestPath;
}

if (require.main === module) {
  try {
    console.log(`PASS release SHA-256 manifest: ${writeReleaseArtifactHashes()}`);
  } catch (error) {
    console.error('Release hash generation failed:', error.message);
    process.exitCode = 1;
  }
}

module.exports = writeReleaseArtifactHashes;
