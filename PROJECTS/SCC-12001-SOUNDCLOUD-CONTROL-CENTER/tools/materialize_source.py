#!/usr/bin/env python3
from __future__ import annotations
import base64, gzip, hashlib, json, re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = PROJECT_ROOT / "source" / "CURRENT_SOURCE.json"

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def _parse_unified_patch(text: str):
    lines=text.splitlines(keepends=True); hunks=[]; i=0
    header=re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")
    while i < len(lines):
        m=header.match(lines[i])
        if not m: i+=1; continue
        old_start=int(m.group(1)); old_count=int(m.group(2) or "1")
        new_start=int(m.group(3)); new_count=int(m.group(4) or "1")
        i+=1; body=[]
        while i < len(lines) and not lines[i].startswith("@@ "):
            if lines[i].startswith(("--- ","+++ ")): break
            if lines[i].startswith((" ","+","-","\\")): body.append(lines[i])
            i+=1
        hunks.append((old_start,old_count,new_start,new_count,body))
    if not hunks: raise RuntimeError("Unified diff contains no hunks")
    return hunks

def apply_unified_patch(original: str, patch_text: str) -> str:
    src=original.splitlines(keepends=True); out=[]; src_index=0
    for old_start,old_count,_new_start,_new_count,body in _parse_unified_patch(patch_text):
        target=old_start-1
        if target < src_index: raise RuntimeError("Overlapping patch hunk")
        out.extend(src[src_index:target]); src_index=target; consumed=0
        for line in body:
            if line.startswith("\\"): continue
            prefix,payload=line[0],line[1:]
            if prefix==" ":
                if src_index>=len(src) or src[src_index]!=payload: raise RuntimeError(f"Patch context mismatch at source line {src_index+1}")
                out.append(src[src_index]); src_index+=1; consumed+=1
            elif prefix=="-":
                if src_index>=len(src) or src[src_index]!=payload: raise RuntimeError(f"Patch deletion mismatch at source line {src_index+1}")
                src_index+=1; consumed+=1
            elif prefix=="+": out.append(payload)
        if consumed!=old_count: raise RuntimeError(f"Patch old-count mismatch: expected {old_count}, got {consumed}")
    out.extend(src[src_index:])
    return "".join(out)

def materialize(output: Path | None=None) -> Path:
    manifest=json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    carrier_root=PROJECT_ROOT/manifest["carrier_root"]
    encoded="".join((carrier_root/rel).read_text(encoding="utf-8") for rel in manifest["base_parts"])
    encoded_bytes=encoded.encode("ascii")
    if sha256_bytes(encoded_bytes)!=manifest["base_encoded_sha256"]: raise RuntimeError("Base encoded SHA-256 mismatch")
    gz=base64.b64decode(encoded_bytes)
    if sha256_bytes(gz)!=manifest["base_gzip_sha256"]: raise RuntimeError("Base gzip SHA-256 mismatch")
    base=gzip.decompress(gz)
    if sha256_bytes(base)!=manifest["base_source_sha256"]: raise RuntimeError("Base source SHA-256 mismatch")
    patch=(PROJECT_ROOT/manifest["patch_path"]).read_text(encoding="utf-8")
    patched=apply_unified_patch(base.decode("utf-8"),patch).encode("utf-8")
    if sha256_bytes(patched)!=manifest["current_source_sha256"]: raise RuntimeError("Current source SHA-256 mismatch after patch")
    if len(patched)!=manifest["current_source_size_bytes"]: raise RuntimeError("Current source size mismatch after patch")
    if output is None: output=PROJECT_ROOT/".runtime"/manifest["current_source_filename"]
    output.parent.mkdir(parents=True,exist_ok=True); output.write_bytes(patched); return output

if __name__=="__main__":
    print(materialize())
