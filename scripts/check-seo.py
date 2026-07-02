#!/usr/bin/env python3
"""Run basic SEO checks for the static HTML pages."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(ROOT.glob("*.html")) + sorted((ROOT / "pt").glob("*.html"))


def main() -> int:
    failures: list[str] = []
    titles: dict[str, str] = {}
    descriptions: dict[str, str] = {}

    for path in PAGES:
        html = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        rel = str(path.relative_to(ROOT))
        h1_count = len(soup.find_all("h1"))
        title = soup.title.get_text(strip=True) if soup.title else None
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag.get("content", "").strip() if description_tag else None
        canonical_tag = soup.find("link", rel="canonical")
        canonical = canonical_tag.get("href", "").strip() if canonical_tag else None
        schema_tag = soup.find("script", attrs={"type": "application/ld+json"})
        schema = schema_tag.string.strip() if schema_tag and schema_tag.string else None

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
        for hreflang in ("en", "pt-BR", "x-default"):
            if not soup.find("link", rel="alternate", hreflang=hreflang):
                failures.append(f"{rel}: missing hreflang {hreflang}")
        for required in ("og:title", "og:description", "og:image", "og:url"):
            if not soup.find("meta", property=required):
                failures.append(f"{rel}: missing {required}")
        if not soup.find("meta", attrs={"name": "twitter:card"}) or not soup.find("meta", attrs={"name": "twitter:image"}):
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
