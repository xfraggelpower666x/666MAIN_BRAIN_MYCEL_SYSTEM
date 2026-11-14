<<<<<<< HEAD
const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const { runPowerShell } = require('../src/shared/powershell.cjs');
=======
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');
>>>>>>> 41fd3f0895bc0ea78d28d958775e3b82973854b2

console.log('🚀 Starting Soundwave Studio optimized build pipeline...');

const distDir = path.join(__dirname, '../dist');
<<<<<<< HEAD
const packagedDir = path.join(distDir, 'win-unpacked');
const zipPath = path.join(distDir, 'SoundwaveStudio-portable-win-x64.zip');

// 1. Build the same Electron application used by the installer.
console.log('📦 Running electron-builder...');
try {
  execFileSync(process.execPath, [path.join(__dirname, 'build-cyber-studio.cjs')], { stdio: 'inherit', cwd: path.join(__dirname, '..') });
  execFileSync(process.execPath, [path.join(__dirname, '..', 'node_modules', 'electron-builder', 'cli.js'), '--win', '--x64', '--dir', '--publish', 'never'], {
=======
const packagedDir = path.join(distDir, 'SoundwaveStudio-win32-x64');
const zipPath = path.join(distDir, 'SoundwaveStudio-portable-win-x64.zip');

// 1. Execute electron-packager
console.log('📦 Running electron-packager...');
try {
  execSync('npx electron-packager . SoundwaveStudio --platform=win32 --arch=x64 --out=dist --overwrite --asar', {
>>>>>>> 41fd3f0895bc0ea78d28d958775e3b82973854b2
    stdio: 'inherit',
    cwd: path.join(__dirname, '..')
  });
} catch (error) {
<<<<<<< HEAD
  console.error('❌ electron-builder failed:', error.message);
=======
  console.error('❌ electron-packager failed:', error.message);
>>>>>>> 41fd3f0895bc0ea78d28d958775e3b82973854b2
  process.exit(1);
}

// 2. Preserve Electron runtime resources. Do not strip locales or legal notices.
console.log('🛡️ Preserving Electron locales and third-party license notices...');
const localesDir = path.join(packagedDir, 'locales');
if (!fs.existsSync(localesDir)) { console.error('❌ Electron locales directory missing.'); process.exit(1); }
const localeCount = fs.readdirSync(localesDir).filter(f => f.endsWith('.pak')).length;
if (localeCount < 2) { console.error(`❌ Locale integrity gate failed: ${localeCount} locale pack(s).`); process.exit(1); }
console.log(`PASS Electron locale packs preserved: ${localeCount}`);
const licenseHtml = path.join(packagedDir, 'LICENSES.chromium.html');
if (!fs.existsSync(licenseHtml)) { console.error('❌ Chromium third-party license notice missing.'); process.exit(1); }
console.log('PASS Chromium license notice preserved.');

// 3. Compress folder into portable ZIP
console.log('🤐 Compressing packaged application to portable ZIP...');
<<<<<<< HEAD
const tempZip = path.join(distDir, `.radio-wave-${crypto.randomUUID()}.zip`);

try {
  const quote = value => "'" + value.replace(/'/g, "''") + "'";
  const psCommand = `$ErrorActionPreference='Stop'; Add-Type -AssemblyName System.IO.Compression; Add-Type -AssemblyName System.IO.Compression.FileSystem; $root=${quote(packagedDir)}; $zip=[IO.Compression.ZipFile]::Open(${quote(tempZip)},[IO.Compression.ZipArchiveMode]::Create); try { Get-ChildItem -LiteralPath $root -File -Recurse -Force | ForEach-Object { $relative=$_.FullName.Substring($root.Length+1).Replace('\\','/'); [void][IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip,$_.FullName,('win-unpacked/'+$relative),[IO.Compression.CompressionLevel]::Optimal) } } finally { $zip.Dispose() }`;
  const result = runPowerShell(['-NoProfile', '-NonInteractive', '-Command', psCommand], { stdio: 'inherit' });
  if (result.error || result.status !== 0) throw result.error || new Error(`PowerShell exited with status ${result.status}`);
  fs.renameSync(tempZip, zipPath);
=======
if (fs.existsSync(zipPath)) {
  fs.unlinkSync(zipPath);
}

try {
  // Use PowerShell's Compress-Archive
  const psCommand = `powershell -Command "Compress-Archive -Path '${packagedDir}' -DestinationPath '${zipPath}' -Force"`;
  execSync(psCommand, { stdio: 'inherit' });
>>>>>>> 41fd3f0895bc0ea78d28d958775e3b82973854b2
  console.log(`🎉 Optimization complete! Portable ZIP successfully generated.`);
  const stats = fs.statSync(zipPath);
  const sizeMb = (stats.size / (1024 * 1024)).toFixed(2);
  console.log(`📁 Final ZIP Size: ${sizeMb} MB`);
<<<<<<< HEAD
=======
  const crypto = require('crypto');
>>>>>>> 41fd3f0895bc0ea78d28d958775e3b82973854b2
  const sha256 = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
  const manifestPath = path.join(distDir, 'RELEASE_ARTIFACT_SHA256SUMS.txt');
  const lines = [`${sha256(zipPath)}  ${path.basename(zipPath)}`];
  const exe = fs.readdirSync(packagedDir).find(n=>/\.exe$/i.test(n));
  if (exe) lines.push(`${sha256(path.join(packagedDir,exe))}  ${path.join(path.basename(packagedDir),exe)}`);
  fs.writeFileSync(manifestPath, lines.join('\n')+'\n', 'utf8');
  console.log(`PASS release SHA-256 manifest: ${manifestPath}`);
} catch (error) {
<<<<<<< HEAD
  try { fs.unlinkSync(tempZip); } catch (cleanupError) {
    if (cleanupError.code !== 'ENOENT') console.error('Temporary ZIP cleanup failed:', cleanupError.message);
  }
=======
>>>>>>> 41fd3f0895bc0ea78d28d958775e3b82973854b2
  console.error('❌ Compression failed:', error.message);
  process.exit(1);
}
