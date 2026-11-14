'use strict';

const { execSync, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const { path7za } = require('7zip-bin');
const writeReleaseArtifactHashes = require('./write-release-hashes.cjs');

async function buildPortablePackage() {
  const projectDir = path.join(__dirname, '..');
  const distDir = path.join(projectDir, 'dist');
  const packagedDir = path.join(distDir, 'win-unpacked');
  const zipPath = path.join(distDir, 'SoundwaveStudio-portable-win-x64.zip');

  console.log('📦 Building the unpacked Windows runtime for the portable ZIP...');
  execSync('npx electron-builder --win --x64 --dir --publish never --config.win.signAndEditExecutable=false', {
    stdio: 'inherit',
    cwd: projectDir
  });

  console.log('🛡️ Preserving Electron locales and third-party license notices...');
  const localesDir = path.join(packagedDir, 'locales');
  if (!fs.existsSync(localesDir)) throw new Error(`Electron locales directory missing: ${localesDir}`);
  const localeCount = fs.readdirSync(localesDir).filter(file => file.endsWith('.pak')).length;
  if (localeCount < 2) throw new Error(`Locale integrity gate failed: ${localeCount} locale pack(s).`);
  console.log(`PASS Electron locale packs preserved: ${localeCount}`);

  const licenseHtml = path.join(packagedDir, 'LICENSES.chromium.html');
  if (!fs.existsSync(licenseHtml)) throw new Error(`Chromium third-party license notice missing: ${licenseHtml}`);
  console.log('PASS Chromium license notice preserved.');

  console.log('🤐 Compressing packaged application to portable ZIP...');
  fs.rmSync(zipPath, { force: true });
  execFileSync(path7za, ['a', '-tzip', '-mx=5', zipPath, path.basename(packagedDir)], {
    stdio: 'inherit',
    cwd: distDir
  });
  if (!fs.existsSync(zipPath)) throw new Error(`Portable ZIP was not created: ${zipPath}`);
  execFileSync(path7za, ['t', '-bb0', zipPath], { stdio: 'inherit' });

  const manifestPath = writeReleaseArtifactHashes(distDir);

  const sizeMb = (fs.statSync(zipPath).size / (1024 * 1024)).toFixed(2);
  console.log(`PASS portable ZIP: ${zipPath} (${sizeMb} MB)`);
  console.log(`PASS release SHA-256 manifest: ${manifestPath}`);
}

buildPortablePackage().catch(error => {
  console.error('❌ Portable build failed:', error.stack || error.message || error);
  process.exitCode = 1;
});
