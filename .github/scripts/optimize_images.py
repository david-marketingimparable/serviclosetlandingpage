#!/usr/bin/env python3
"""Create WebP copies of site raster images and update local references."""
from pathlib import Path
import re
import subprocess
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
IMAGE_EXTS = {".jpg", ".jpeg", ".png"}
TEXT_EXTS = {".html", ".css", ".js"}
QUALITY = 82

def main():
    converted = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        try:
            with Image.open(path) as source:
                image = source.convert("RGB") if source.mode not in ("RGB", "RGBA") else source.copy()
                target = path.with_suffix(".webp")
                image.save(target, "WEBP", quality=QUALITY, method=6)
            if target.stat().st_size >= path.stat().st_size * 0.96:
                target.unlink(missing_ok=True)
                continue
            converted += 1
            print(f"{path.relative_to(ROOT)} -> {target.relative_to(ROOT)} ({path.stat().st_size} -> {target.stat().st_size} bytes)")
        except Exception as exc:
            print(f"Skipping {path}: {exc}")
    for file in ROOT.rglob("*"):
        if not file.is_file() or file.suffix.lower() not in TEXT_EXTS:
            continue
        content = file.read_text(encoding="utf-8")
        updated = content
        for ext in IMAGE_EXTS:
            updated = re.sub(re.escape(ext) + r'(?=([?#"\' )]|$))', ".webp", updated, flags=re.IGNORECASE)
        if updated != content:
            file.write_text(updated, encoding="utf-8")
    print(f"Converted {converted} raster images to WebP where smaller.")

if __name__ == "__main__":
    main()
