#!/usr/bin/env python3
"""Check generated Brazilian Portuguese pages for bilingual static-site rules."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
PT_DIR = ROOT / "pt"
DOMAIN = "https://www.sofiati.com"
PUBLIC_PAGES = [
    "index.html",
    "about.html",
    "accessibility.html",
    "blog.html",
    "care.html",
    "consultation.html",
    "contact.html",
    "cookies.html",
    "faq.html",
    "journal.html",
    "laser.html",
    "legal.html",
    "mission.html",
    "privacy.html",
    "results.html",
    "skin.html",
    "testimonials.html",
    "thank-you.html",
    "values.html",
    "404.html",
]

LOCAL_ATTRS = {"href", "src"}
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "sms", "whatsapp"}
ENGLISH_UI_PATTERN = re.compile(
    r"\b(the|and|with|before|after|through|should|could|would|what|when|where|your|you|care|skin|consultation|results|questions|contact|guidance|page)\b",
    re.I,
)


def en_url(page: str) -> str:
    return f"{DOMAIN}/" if page == "index.html" else f"{DOMAIN}/{page}"


def pt_url(page: str) -> str:
    return f"{DOMAIN}/pt/" if page == "index.html" else f"{DOMAIN}/pt/{page}"


def is_local(value: str) -> bool:
    parsed = urlparse(value)
    return not parsed.scheme or parsed.scheme not in SKIP_SCHEMES


def resolve(base: Path, value: str) -> Path | None:
    value = value.split("#", 1)[0].split("?", 1)[0]
    if not value or value.startswith("data:"):
        return None
    if value.startswith("/"):
        return ROOT / value.lstrip("/")
    return (base.parent / value).resolve()


def visible_text(soup: BeautifulSoup) -> str:
    clone = BeautifulSoup(str(soup), "html.parser")
    for node in clone(["script", "style"]):
        node.decompose()
    return " ".join(clone.get_text(" ").split())


def collect_classes_and_ids(path: Path) -> tuple[set[str], set[str]]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    classes: set[str] = set()
    ids: set[str] = set()
    for tag in soup.find_all(True):
        ids.add(tag.get("id", ""))
        for cls in tag.get("class", []):
            classes.add(cls)
    ids.discard("")
    return classes, ids


def main() -> int:
    failures: list[str] = []
    warnings: list[str] = []

    if not PT_DIR.exists():
        failures.append("Missing pt/ directory.")

    for page in PUBLIC_PAGES:
        source = ROOT / page
        target = PT_DIR / page
        if not source.exists():
            failures.append(f"Missing English source: {page}")
            continue
        if not target.exists():
            failures.append(f"Missing Portuguese page: pt/{page}")
            continue

        html = target.read_text(encoding="utf-8")
        soup = BeautifulSoup(html, "html.parser")
        rel = f"pt/{page}"

        html_tag = soup.find("html")
        if not html_tag or html_tag.get("lang") != "pt-BR":
            failures.append(f"{rel}: html lang is not pt-BR")

        if len(soup.find_all("h1")) != 1:
            failures.append(f"{rel}: expected exactly one h1")
        if len(soup.find_all("section")) != 10:
            failures.append(f"{rel}: expected 10 sections")

        canonical = soup.find("link", rel="canonical")
        if not canonical or canonical.get("href") != pt_url(page):
            failures.append(f"{rel}: missing or wrong Portuguese canonical")

        alternates = {link.get("hreflang"): link.get("href") for link in soup.find_all("link", rel="alternate")}
        if alternates.get("en") != en_url(page):
            failures.append(f"{rel}: missing or wrong en hreflang")
        if alternates.get("pt-BR") != pt_url(page):
            failures.append(f"{rel}: missing or wrong pt-BR hreflang")

        if 'data-sofiati-partial="header"' not in html or 'data-sofiati-partial="footer"' not in html:
            failures.append(f"{rel}: partial placeholders missing")
        for translated_value in ["cabeçalho", "rodapé", "menu móvel"]:
            if f'data-sofiati-partial="{translated_value}"' in html:
                failures.append(f"{rel}: data-sofiati-partial value appears translated")

        schema = soup.find("script", {"type": "application/ld+json"})
        if not schema or not schema.string:
            failures.append(f"{rel}: missing JSON-LD schema")
        else:
            try:
                data = json.loads(schema.string)
                if data.get("url") != pt_url(page):
                    failures.append(f"{rel}: schema url is not Portuguese canonical")
            except json.JSONDecodeError:
                failures.append(f"{rel}: invalid JSON-LD")

        for tag in soup.find_all(True):
            for attr in LOCAL_ATTRS:
                value = tag.get(attr)
                if not value or not is_local(value):
                    continue
                # English switcher link intentionally points one level up.
                target_path = resolve(target, value)
                if target_path and not target_path.exists():
                    failures.append(f"{rel}: missing {attr} -> {value}")

        source_classes, source_ids = collect_classes_and_ids(source)
        target_classes, target_ids = collect_classes_and_ids(target)
        missing_classes = source_classes - target_classes
        missing_ids = source_ids - target_ids
        if missing_classes:
            failures.append(f"{rel}: missing classes from source: {', '.join(sorted(list(missing_classes))[:8])}")
        if missing_ids:
            failures.append(f"{rel}: missing ids from source: {', '.join(sorted(list(missing_ids))[:8])}")

        text = visible_text(soup)
        matches = sorted({match.group(0).lower() for match in ENGLISH_UI_PATTERN.finditer(text)})
        intentional = {"laser", "faq", "whatsapp", "instagram", "email", "en", "pt"}
        suspicious = [match for match in matches if match not in intentional]
        if suspicious:
            warnings.append(f"{rel}: possible English leftovers: {', '.join(suspicious)}")

        for form in soup.find_all("form"):
            if not form.get("action") or not form.get("method"):
                failures.append(f"{rel}: form missing action or method")

    if failures:
        print("Portuguese site check failed:", file=sys.stderr)
        print("\n".join(failures), file=sys.stderr)
        return 1

    print(f"Portuguese site checks passed for {len(PUBLIC_PAGES)} pages.")
    if warnings:
        print("Review warnings:")
        print("\n".join(warnings))
    else:
        print("No obvious English UI leftovers detected.")
    print("Human review by a Brazilian Portuguese speaker is still recommended for final nuance.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
