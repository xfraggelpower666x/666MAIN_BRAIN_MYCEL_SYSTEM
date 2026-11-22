"""Build 3DX Profile Studio from src/.

    python build.py                 standalone page -> dist/3DX-Profile-Studio.html and docs/index.html (GitHub Pages)
    python build.py --release       ...plus versioned release assets and SHA256SUMS.txt in dist/
    python build.py --artifact OUT  the Claude-hosted variant (AI runs on the viewer's Claude account)

Every build also writes build/pure.js, the page's DOM-free functions, for tests/test.js.
"""

import argparse
import hashlib
import json
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src" / "profile-studio.html"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
# Address of the free AI server (worker/). Public, not a secret: the Anthropic key stays on the server.
AI_PROXY_FILE = ROOT / "AI_PROXY_URL"
AI_PROXY = AI_PROXY_FILE.read_text(encoding="utf-8").strip().rstrip("/") if AI_PROXY_FILE.exists() else ""

# The same minimal skeleton the Claude artifact host wraps around a page, so both variants render alike
HEAD = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        '<style>[hidden]{display:none!important}img{max-width:100%}</style>\n</head>\n<body>\n')
TAIL = "\n</body>\n</html>\n"


def render(build):
    src = SRC.read_text(encoding="utf-8")
    symbols = json.loads((ROOT / "src" / "symbols.json").read_text(encoding="utf-8"))
    templates = json.loads((ROOT / "src" / "templates.json").read_text(encoding="utf-8"))
    for token in ("/*SYMBOLS*/", "/*TEMPLATES*/", '"__BUILD__"', '"__VERSION__"', '"__AI_PROXY__"'):
        assert src.count(token) == 1, f"{token} must appear exactly once in {SRC.name}"
    return (src.replace("/*SYMBOLS*/", json.dumps(symbols, ensure_ascii=False))
               .replace("/*TEMPLATES*/", json.dumps(templates, ensure_ascii=False))
               .replace('"__BUILD__"', json.dumps(build))
               .replace('"__VERSION__"', json.dumps(VERSION))
               .replace('"__AI_PROXY__"', json.dumps(AI_PROXY if build == "release" else "")))


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path} ({len(text.encode('utf-8')):,} bytes)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--release", action="store_true")
    ap.add_argument("--artifact", type=Path)
    args = ap.parse_args()

    page = render("release")
    standalone = HEAD + page + TAIL
    write(ROOT / "dist" / "3DX-Profile-Studio.html", standalone)
    write(ROOT / "docs" / "index.html", standalone)

    pure = page.split("// ===== PURE-START")[1].split("// ===== PURE-END")[0]
    names = re.findall(r"^(?:function|const) ([A-Za-z_]\w*)", pure, re.M)
    write(ROOT / "build" / "pure.js", "//" + pure + "\nmodule.exports = { " + ", ".join(names) + " };\n")
    write(ROOT / "build" / "page.js", "\n".join(re.findall(r"<script>(.*?)</script>", page, re.S)))

    if args.artifact:
        write(args.artifact, render("artifact"))

    if args.release:
        dist = ROOT / "dist"
        html_name = f"3DX-Profile-Studio-{VERSION}.html"
        write(dist / html_name, standalone)
        zip_path = dist / f"3DX-Profile-Studio-{VERSION}.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
            z.writestr("3DX Profile Studio/3DX Profile Studio.html", standalone)
            z.write(ROOT / "LICENSE", "3DX Profile Studio/LICENSE.txt")
            ai_line = ("The AI writer works right away with the free built-in AI, or with your own key\r\n"
                       "from any provider listed under AI settings." if AI_PROXY else
                       "AI features take an API key from any provider listed under AI settings.")
            z.writestr("3DX Profile Studio/README.txt",
                       f"3DX Profile Studio {VERSION}\r\n\r\nDouble-click '3DX Profile Studio.html' to open it in your browser.\r\n"
                       f"No install needed. {ai_line}\r\n\r\n"
                       "https://github.com/Deaeath/3dx-profile-studio\r\n")
        print(f"wrote dist/{zip_path.name}")
        sums = [f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}" for p in (dist / html_name, zip_path)]
        (dist / "SHA256SUMS.txt").write_text("\n".join(sums) + "\n", encoding="utf-8", newline="\n")
        print("wrote dist/SHA256SUMS.txt")


if __name__ == "__main__":
    main()
