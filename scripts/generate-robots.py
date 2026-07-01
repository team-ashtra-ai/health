#!/usr/bin/env python3
"""Generate robots.txt for the static site."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    (ROOT / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://www.sofiati.com/sitemap.xml\n",
        encoding="utf-8",
    )
    print("Generated robots.txt.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
