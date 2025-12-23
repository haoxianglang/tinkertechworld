#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS_DIR = ROOT / "products"
MANIFEST_PATH = PRODUCTS_DIR / "manifest.json"
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"}

def main() -> None:
    if not PRODUCTS_DIR.exists():
        raise SystemExit("products/ directory not found.")

    files = [
        p.name
        for p in PRODUCTS_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in EXTENSIONS
        and p.name != MANIFEST_PATH.name
    ]
    files.sort(key=str.lower)

    with MANIFEST_PATH.open("w", encoding="utf-8") as handle:
        json.dump(files, handle, indent=2)
        handle.write("\n")

    print(f"Wrote {MANIFEST_PATH} with {len(files)} entries.")

if __name__ == "__main__":
    main()
