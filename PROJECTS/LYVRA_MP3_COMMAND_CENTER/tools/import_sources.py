"""Verifiziert Originalarchive und importiert sie lokal, ohne Originale zu verändern."""
import hashlib, pathlib, zipfile, argparse, tempfile, shutil, stat, json
ROOT=pathlib.Path(__file__).resolve().parents[1]
SOURCES={
'mp3':('LYVRA_MP3_MANAGER_v2_40_1_ELECTRON_C02_ID3_PARITY_SOURCE.zip','e0c415e253e37362673efc338546f45d401b94c2ee0cf9110a418ff7c1a33b43'),
'dj':('666_AUTO_DJ_STUDIO_R07_NEON_UI_CONTINUITY(1).zip','61eedae4460d5aba6630c81ce80d4b35dbc497bdf74241521b135113bd9b7b4f'),
'restore':('Restoration-Lab-main-Windows-Workflow-Fix.zip','b8d3d51c4c03fb8472826dd123aad12d01ea8de059aba12bf7a7d2dd857e60c1'),
'boot':('666_UNIVERSAL_PYTHON_ELECTRON_BUILDKIT_R01_11_1_ELECTRON_SOURCE_PUBLISH.zip','ae646788d0f55ad63100628ccc67d6bd12e20a242eb11fe95163bc26bb008b1c')}
def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def main():
    p=argparse.ArgumentParser();p.add_argument('archive_directory',type=pathlib.Path);a=p.parse_args()
    target=ROOT/'imports'
    if target.exists(): raise SystemExit('imports existiert bereits; keine automatische Ersetzung')
    for name,sha in SOURCES.values():
        if digest(a.archive_directory/name)!=sha: raise ValueError('SHA256-Konflikt: '+name)
    with tempfile.TemporaryDirectory(dir=ROOT) as temp:
        stage=pathlib.Path(temp)/'imports';stage.mkdir()
        for key,(name,sha) in SOURCES.items():
            dest=stage/key;dest.mkdir()
            with zipfile.ZipFile(a.archive_directory/name) as z:
                if z.testzip(): raise ValueError('CRC-Konflikt')
                seen=set()
                for item in z.infolist():
                    parts=pathlib.PurePosixPath(item.filename).parts
                    if not parts or item.filename.startswith('/') or any(x in ('..','.') or ':' in x or chr(92) in x for x in parts) or stat.S_ISLNK(item.external_attr>>16): raise ValueError('Unsicherer Archivpfad')
                    if any(x.lower() in ('.venv-gui','.venv','node_modules','__pycache__','.git') for x in parts): continue
                    out=dest.joinpath(*parts)
                    if item.is_dir(): out.mkdir(parents=True,exist_ok=True);continue
                    k=str(out).casefold()
                    if k in seen: raise ValueError('Doppelter Archivpfad')
                    seen.add(k);out.parent.mkdir(parents=True,exist_ok=True)
                    with z.open(item) as src,out.open('xb') as dst: shutil.copyfileobj(src,dst)
        (stage/'manifest.json').write_text(json.dumps(SOURCES,indent=2),encoding='utf8')
        stage.rename(target)
    print('Vier SHA256-geprüfte Quellen lokal importiert.')
if __name__=='__main__': main()
