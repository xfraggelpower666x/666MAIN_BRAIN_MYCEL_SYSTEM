"""Optional: fehlende Original-Binärassets aus dem Upstream beschaffen.

Nur die neun SHA-verifizierten Assets des vom Nutzer gelieferten ZIPs.
Ausführen im Projektverzeichnis: python tools/restore_original_assets.py
"""
from pathlib import Path
from urllib.request import urlopen
from urllib.parse import quote
import hashlib

ROOT = Path(__file__).resolve().parent.parent
UPSTREAM = "https://raw.githubusercontent.com/Deaeath/3dx-radio-streamer/main/"
EXPECTED = {
    "assets/icon.ico": "18c1bba698bf40eea6d07fe8c95a2607cb8d555f",
    "assets/icon.png": "e87f0f46b5748827fe250f6b727cd68f331171e6",
    "docs/images/add-links.png": "f60e045c358862a088ffd9cf42b2d0a2bc3fe5d1",
    "docs/images/main-live.png": "5e723237db33f7ffcf50457ce693fb15a020a012",
    "docs/images/server-tab.png": "6ca78ea81a771c1b64b94a1f5d34cbd81bd97a15",
    "docs/images/wizard-1-welcome.png": "0314ba8d020686712452cb0c136c994f62ae31f6",
    "docs/images/wizard-2-server.png": "aae1d19e8fd17064422638ad5c18b1421a9d9faa",
    "docs/images/wizard-3-source.png": "a8c58a09d4e2782be6a28b87f7762b587fd12d38",
    "docs/images/wizard-4-done.png": "a19b4e995f193646bd823fa89f5a8c1b8bcd15f2"
}

def git_sha(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()

def main() -> None:
    for name, expected in EXPECTED.items():
        target = ROOT / name
        if target.exists():
            if git_sha(target.read_bytes()) != expected:
                raise RuntimeError(f"SHA mismatch at existing file: {name}")
            print(f"OK: {name}")
            continue
        url = UPSTREAM + quote(name, safe="/")
        with urlopen(url, timeout=30) as response:
            data = response.read()
        if git_sha(data) != expected:
            raise RuntimeError(f"Downloaded asset does not match original: {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        print(f"Restored: {name}")

if __name__ == "__main__":
    main()
