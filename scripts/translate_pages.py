#!/usr/bin/env python3
"""Verify the Portuguese-default runtime and write a translation report.

The concept HTML stays English-authored as the source of truth. Each standalone
site owns a local `js/main.js` runtime that renders Portuguese by default and
offers a minimal EN/PT switcher.
"""

from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path

from bs4 import BeautifulSoup, NavigableString

from generate_concepts import CONCEPTS, PAGE_SPECS, ROOT, translation_dictionary


CONCEPTS_DIR = ROOT / "concepts"
FINAL_DIR = ROOT / "final"
DATA_DIR = ROOT / "data"
SKIP_PARENTS = {"script", "style", "noscript", "template"}
TRANSLATABLE_ATTRS = {"alt", "aria-label", "content", "placeholder", "title"}
CONTACT_RE = re.compile(r"(@|https?://|mailto:|\bwa\.me\b|\w+@\w+)", re.I)
ALPHA_RE = re.compile(r"[A-Za-z]")


def required_concepts() -> list[str]:
    return [f"{number}-{slug}" for number, slug, *_ in CONCEPTS]


def should_keep(value: str) -> bool:
    value = " ".join(value.split())
    if not value or len(value) < 2:
        return False
    if not ALPHA_RE.search(value):
        return False
    if CONTACT_RE.search(value):
        return False
    if value in {"Franciele Sofiati", "CRBM 6277", "Londrina, PR", "PT", "EN"}:
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


def phrase_translation(value: str, translations: dict[str, str]) -> str:
    if value in translations:
        return translations[value]
    output = value
    for source, target in sorted(translations.items(), key=lambda item: len(item[0]), reverse=True):
        if source and source in output:
            output = output.replace(source, target)
    return output


def runtime_errors() -> list[str]:
    errors: list[str] = []
    page_files = [page[2] for page in PAGE_SPECS]
    for folder in required_concepts():
        concept = CONCEPTS_DIR / folder
        js = concept / "js" / "main.js"
        partials_js = concept / "js" / "partials.js"
        if not js.exists():
            errors.append(f"Missing runtime: concepts/{folder}/js/main.js")
        else:
            js_text = js.read_text(encoding="utf-8")
            for needle in ("sofiati-language", "data-lang-switch", "pt-BR", "applyLanguage", "translations"):
                if needle not in js_text:
                    errors.append(f"Translation runtime missing {needle}: concepts/{folder}/js/main.js")
        if not partials_js.exists():
            errors.append(f"Missing partial loader runtime: concepts/{folder}/js/partials.js")
        else:
            partials_text = partials_js.read_text(encoding="utf-8")
            for needle in ("data-partial-mount", "partials/", "head", "schema"):
                if needle not in partials_text:
                    errors.append(f"Partial loader missing {needle}: concepts/{folder}/js/partials.js")
        status_partial = concept / "partials" / "status-banner.html"
        if not status_partial.exists():
            errors.append(f"Missing status banner partial: concepts/{folder}/partials/status-banner.html")
        else:
            status_raw = status_partial.read_text(encoding="utf-8")
            for needle in ("data-status-banner", "data-lang-switch"):
                if needle not in status_raw:
                    errors.append(f"Status/language marker missing {needle}: concepts/{folder}/partials/status-banner.html")
        for filename in page_files:
            path = concept / filename
            if not path.exists():
                errors.append(f"Missing page for translation check: concepts/{folder}/{filename}")
                continue
            raw = path.read_text(encoding="utf-8")
            for needle in ('lang="pt-BR"', 'data-source-lang="en"', 'data-default-lang="pt"', 'data-partial-mount="status-banner"', 'js/partials.js'):
                if needle not in raw:
                    errors.append(f"PT-default marker missing {needle}: concepts/{folder}/{filename}")
    return errors


def build_inventory() -> dict[str, object]:
    translations = translation_dictionary()
    counter: Counter[str] = Counter()
    by_page: dict[str, list[str]] = {}
    for folder in required_concepts():
        concept = CONCEPTS_DIR / folder
        inventory_paths = list(sorted(concept.glob("*.html"))) + list(sorted((concept / "partials").glob("*.html")))
        for page in inventory_paths:
            strings = visible_strings(page)
            rel = page.relative_to(ROOT).as_posix()
            by_page[rel] = sorted(set(strings))
            counter.update(set(strings))
    rows = []
    covered = 0
    for text, count in sorted(counter.items(), key=lambda item: (-item[1], item[0].lower())):
        pt = phrase_translation(text, translations)
        if pt != text:
            covered += 1
        rows.append({"source": text, "occurrences": count, "pt_BR": pt})
    errors = runtime_errors()
    return {
        "mode": "pt-default-runtime",
        "note": "HTML is English-authored; local concept JavaScript renders Portuguese by default with EN/PT switching.",
        "conceptCount": len(required_concepts()),
        "htmlFileCount": sum(1 for folder in required_concepts() for _ in (CONCEPTS_DIR / folder).glob("*.html")),
        "uniqueStringCount": len(rows),
        "translatedOrPhraseCovered": covered,
        "runtimeErrors": errors,
        "strings": rows,
        "byPage": by_page,
    }


def write_reports(inventory: dict[str, object]) -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "translation-strings.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    (FINAL_DIR / "translation-report.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False), encoding="utf-8")
    lines = [
        "# Translation Runtime Report",
        "",
        "- Mode: pt-default-runtime",
        f"- Concept count: {inventory['conceptCount']}",
        f"- HTML file count: {inventory['htmlFileCount']}",
        f"- Unique source strings: {inventory['uniqueStringCount']}",
        f"- Covered by exact or phrase translations: {inventory['translatedOrPhraseCovered']}",
        f"- Runtime errors: {len(inventory['runtimeErrors'])}",
        "- HTML rewrite: no",
        "",
        "The standalone sites keep English source copy in the files and render Portuguese by default through each concept's own `js/main.js`.",
    ]
    if inventory["runtimeErrors"]:
        lines.append("")
        lines.extend(f"- {error}" for error in inventory["runtimeErrors"])
    (FINAL_DIR / "translation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    inventory = build_inventory()
    write_reports(inventory)
    summary = {
        "mode": inventory["mode"],
        "conceptCount": inventory["conceptCount"],
        "htmlFileCount": inventory["htmlFileCount"],
        "uniqueStringCount": inventory["uniqueStringCount"],
        "translatedOrPhraseCovered": inventory["translatedOrPhraseCovered"],
        "runtimeErrorCount": len(inventory["runtimeErrors"]),
    }
    print(json.dumps(summary, indent=2))
    if inventory["runtimeErrors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
