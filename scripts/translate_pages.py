#!/usr/bin/env python3
"""Create an English-source translation inventory without rewriting pages.

The corrective build requirement keeps every page English-first. This script is
therefore intentionally non-destructive: it extracts visible strings and
metadata from the standalone concepts, writes a translation inventory/report,
and leaves the concept HTML, CSS and JS untouched.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
FINAL_DIR = ROOT / "final"
DATA_DIR = ROOT / "data"
SKIP_PARENTS = {"script", "style", "noscript", "template"}
TRANSLATABLE_ATTRS = {"alt", "aria-label", "content", "placeholder", "title"}
CONTACT_RE = re.compile(r"(@|https?://|mailto:|\bwa\.me\b|\w+@\w+)", re.I)
ALPHA_RE = re.compile(r"[A-Za-z]")


def concept_dirs() -> list[Path]:
    return sorted(path for path in CONCEPTS_DIR.iterdir() if path.is_dir())


def should_keep(value: str) -> bool:
    value = " ".join(value.split())
    if not value or len(value) < 2:
        return False
    if not ALPHA_RE.search(value):
        return False
    if CONTACT_RE.search(value):
        return False
    if value in {"Franciele Sofiati", "CRBM 6277", "Londrina, PR"}:
        return False
    return True


def visible_strings(path: Path) -> list[str]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    strings: list[str] = []
    for node in soup.find_all(string=True):
        if isinstance(node, NavigableString) and node.parent and node.parent.name not in SKIP_PARENTS:
            value = " ".join(str(node).split())
            if should_keep(value):
                strings.append(value)
    for tag in soup.find_all(True):
        for attr in TRANSLATABLE_ATTRS:
            value = tag.get(attr)
            if isinstance(value, str):
                value = " ".join(value.split())
                if should_keep(value):
                    strings.append(value)
    return strings


def build_inventory() -> dict[str, object]:
    concepts = concept_dirs()
    counter: Counter[str] = Counter()
    by_page: dict[str, list[str]] = {}
    for concept in concepts:
        for page in sorted(concept.glob("*.html")):
            strings = visible_strings(page)
            rel = page.relative_to(ROOT).as_posix()
            by_page[rel] = sorted(set(strings))
            counter.update(set(strings))
    strings = [
        {"source": text, "occurrences": count, "pt_BR": ""}
        for text, count in sorted(counter.items(), key=lambda item: (-item[1], item[0].lower()))
    ]
    return {
        "mode": "english-preserving",
        "note": "Standalone concept HTML was not rewritten because the corrective acceptance criteria require English-first pages.",
        "conceptCount": len(concepts),
        "htmlFileCount": sum(1 for concept in concepts for _ in concept.glob("*.html")),
        "uniqueStringCount": len(strings),
        "strings": strings,
        "byPage": by_page,
    }


def write_reports(inventory: dict[str, object]) -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "translation-strings.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    (FINAL_DIR / "translation-report.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Translation Inventory",
        "",
        "- Mode: english-preserving",
        f"- Concept count: {inventory['conceptCount']}",
        f"- HTML file count: {inventory['htmlFileCount']}",
        f"- Unique source strings: {inventory['uniqueStringCount']}",
        "- HTML rewrite: no",
        "",
        "The standalone sites remain English-first. This inventory can seed a later Portuguese translation pass without changing the reviewed concepts.",
    ]
    (FINAL_DIR / "translation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    inventory = build_inventory()
    write_reports(inventory)
    print(
        json.dumps(
            {
                "mode": inventory["mode"],
                "conceptCount": inventory["conceptCount"],
                "htmlFileCount": inventory["htmlFileCount"],
                "uniqueStringCount": inventory["uniqueStringCount"],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
