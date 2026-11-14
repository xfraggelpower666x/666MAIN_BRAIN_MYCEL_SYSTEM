'use strict';

const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { downloadArtifact } = require('@electron/get');
const { path7za } = require('7zip-bin');

function runtimeReportsVersion(executablePath, version) {
  try {
    return execFileSync(executablePath, ['--version'], {
      encoding: 'utf8',
      timeout: 30000,
      windowsHide: true
    }).trim() === `v${version}`;
  } catch {
    return false;
  }
}

async function ensureElectronRuntime() {
  if (process.platform !== 'win32' || process.arch !== 'x64') {
    console.log(`Skipping Windows Electron repair on ${process.platform}/${process.arch}.`);
    return;
  }

  const packagePath = require.resolve('electron/package.json');
  const electronDir = path.dirname(packagePath);
  const { version } = require(packagePath);
  const distDir = path.join(electronDir, 'dist');
  const executablePath = path.join(distDir, 'electron.exe');
  const markerPath = path.join(electronDir, 'path.txt');
  const versionPath = path.join(distDir, 'version');
  const repairRequested = process.argv.includes('--repair');

  if (
    !repairRequested &&
    fs.existsSync(executablePath) &&
    fs.existsSync(markerPath) &&
    fs.readFileSync(markerPath, 'utf8') === 'electron.exe' &&
    fs.existsSync(versionPath) &&
    fs.readFileSync(versionPath, 'utf8').replace(/^v/, '').trim() === version &&
    runtimeReportsVersion(executablePath, version)
  ) {
    console.log(`PASS Electron ${version} runtime is installed.`);
    return;
  }

  console.log(`Restoring verified Electron ${version} archive...`);
  const archivePath = await downloadArtifact({
    version,
    artifactName: 'electron',
    platform: 'win32',
    arch: 'x64',
    checksums: require(path.join(electronDir, 'checksums.json'))
  });

  fs.mkdirSync(distDir, { recursive: true });
  execFileSync(path7za, ['x', '-y', `-o${distDir}`, archivePath], { stdio: 'inherit' });

  if (
    !fs.existsSync(executablePath) ||
    !fs.existsSync(versionPath) ||
    fs.readFileSync(versionPath, 'utf8').replace(/^v/, '').trim() !== version
  ) {
    throw new Error(`Electron ${version} archive extraction did not produce a valid runtime.`);
  }

  fs.writeFileSync(markerPath, 'electron.exe', 'utf8');
  if (!runtimeReportsVersion(executablePath, version)) {
    throw new Error(`Electron runtime failed to report the expected version v${version}.`);
  }
  console.log(`PASS restored Electron runtime v${version}.`);
}

ensureElectronRuntime().catch(error => {
  console.error('Electron runtime verification failed:', error.stack || error.message || error);
  process.exitCode = 1;
});
