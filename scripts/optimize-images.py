#!/usr/bin/env python3
"""Report large image assets and suggest optimization targets."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico"}


def main() -> int:
    images = sorted(path for path in (ROOT / "assets").rglob("*") if path.suffix.lower() in IMAGE_EXTS)
    large = [path for path in images if path.stat().st_size > 500_000]

    print(f"Found {len(images)} image assets.")
    if large:
      print("Large files to review:")
      for path in large:
          size = path.stat().st_size / 1024
          print(f"- {path.relative_to(ROOT)} ({size:.0f} KB)")
    else:
      print("No image assets over 500 KB.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
