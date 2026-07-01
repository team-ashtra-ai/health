#!/usr/bin/env python3
"""Run basic SEO checks for the static HTML pages."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(ROOT.glob("*.html"))


def one(pattern: str, html: str) -> str | None:
    match = re.search(pattern, html, re.S)
    return match.group(1).strip() if match else None


def main() -> int:
    failures: list[str] = []
    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}

    for path in PAGES:
        html = path.read_text(encoding="utf-8")
        rel = path.name
        h1_count = len(re.findall(r"<h1\b", html))
        title = one(r"<title>(.*?)</title>", html)
        description = one(r'<meta name="description" content="([^"]+)"', html)
        canonical = one(r'<link rel="canonical" href="([^"]+)"', html)
        schema = one(r'<script type="application/ld\+json">(.*?)</script>', html)

        if h1_count != 1:
            failures.append(f"{rel}: expected exactly one h1, found {h1_count}")
        if not title:
            failures.append(f"{rel}: missing title")
        elif title in titles:
            failures.append(f"{rel}: duplicate title also used by {titles[title]}")
        else:
            titles[title] = rel
        if not description:
            failures.append(f"{rel}: missing meta description")
        elif description in descriptions:
            failures.append(f"{rel}: duplicate meta description also used by {descriptions[description]}")
        else:
            descriptions[description] = rel
        if not canonical:
            failures.append(f"{rel}: missing canonical URL")
        for required in ("og:title", "og:description", "og:image", "og:url"):
            if f'property="{required}"' not in html:
                failures.append(f"{rel}: missing {required}")
        if 'name="twitter:card"' not in html or 'name="twitter:image"' not in html:
            failures.append(f"{rel}: missing Twitter card metadata")
        if not schema:
            failures.append(f"{rel}: missing JSON-LD schema")
        else:
            try:
                data = json.loads(schema)
                if not data.get("image"):
                    failures.append(f"{rel}: schema missing image")
            except json.JSONDecodeError:
                failures.append(f"{rel}: invalid JSON-LD schema")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"SEO checks passed for {len(PAGES)} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
