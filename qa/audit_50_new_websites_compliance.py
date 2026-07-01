#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
SCRIPT_RUNS = ROOT / "docs" / "script-runs"
BIBLE_JSON = ROOT / "docs" / "design-destination-bible" / "10-50-new-website-destinations.json"

REQUIRED_PAGES = [
    "index.html",
    "about.html",
    "care.html",
    "laser.html",
    "skin.html",
    "results.html",
    "journal.html",
    "blog.html",
    "consultation.html",
    "contact.html",
    "values.html",
    "mission.html",
    "testimonials.html",
    "faq.html",
    "legal.html",
    "privacy.html",
    "cookies.html",
    "accessibility.html",
    "sitemap.html",
    "thank-you.html",
    "404.html",
]

REQUIRED_PARTIALS = [
    "header.html",
    "mobile-menu.html",
    "footer.html",
    "cookie-banner.html",
    "floating-widgets.html",
]

FORBIDDEN_ACTIVE_TOKENS = [
    "css/atlas-story.css",
    "sofiati-premium-visual-dna.css",
    "sofiati-50-architecture-system.css",
    "sofiati-architecture-conflict-repair.css",
    "sofiati-50-architecture-system.js",
    "sofiati-architecture-conflict-repair.js",
    "atlas-site",
    "atlas-layout-family",
    "premium-visual-dna",
    "visual-dna-site",
    "architecture-site",
    "architecture-main",
    "architecture-section",
    "visual-dna-section",
    "story-section",
    "atlas-section",
    "atlas-main",
    "atlas-section__copy",
    "atlas-section__media",
    "atlas-actions",
    "atlas-button",
    "data-architecture-repair",
    "data-sofiati-conflict-repair",
    "data-component-type",
    "data-interaction",
    "data-css-layout",
]


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def active_links(html: str, kind: str) -> list[str]:
    if kind == "css":
        return re.findall(r'<link[^>]+rel="stylesheet"[^>]+href="([^"]+)"', html)
    return re.findall(r'<script[^>]+src="([^"]+)"', html)


def count_main_sections(html: str) -> int:
    main = re.search(r"<main\b[^>]*>(.*?)</main>", html, re.S | re.I)
    if not main:
        return 0
    return len(re.findall(r'<section\b[^>]*data-content-section="', main.group(1), re.I))


def figure_without_image(html: str) -> list[str]:
    failures = []
    for match in re.finditer(r"<figure\b([^>]*)>(.*?)</figure>", html, re.S | re.I):
        if "<img" not in match.group(2).lower():
            failures.append(match.group(1)[:120])
    return failures


def homepage_photo_count(html: str) -> int:
    main = re.search(r"<main\b[^>]*>(.*?)</main>", html, re.S | re.I)
    if not main:
        return 0
    return len(re.findall(r"<img\b", main.group(1), re.I))


def local_page_links(html: str, concept_dir: Path) -> list[str]:
    broken = []
    for href in re.findall(r'<a\b[^>]+href="([^"]+)"', html, re.I):
        if href.startswith(("#", "mailto:", "tel:")):
            continue
        parsed = urlparse(href)
        if parsed.scheme in {"http", "https"}:
            continue
        target = href.split("#", 1)[0]
        if not target:
            continue
        if target.endswith(".html") and not (concept_dir / target).exists():
            broken.append(href)
    return broken


def cta_styles(html: str) -> set[str]:
    styles = set()
    for classes in re.findall(r'class="([^"]*\baction--[^"]*)"', html):
        for item in classes.split():
            if "action--" in item and not item.endswith("--quiet"):
                styles.add(item)
    return styles


def concept_specific(partial: str, number: str, name: str) -> bool:
    prefix = f"c{number}-"
    public_theme = f"sf-theme-{number}"
    return (prefix in partial and name in partial) or public_theme in partial


def audit() -> tuple[dict, bool]:
    data = json.loads(read(BIBLE_JSON))
    concepts = data["concepts"]
    results = {
        "generatedAt": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
        "totalConcepts": len(concepts),
        "passed": True,
        "concepts": {},
        "failures": [],
    }
    seen_colour_sequences: dict[str, str] = {}

    for concept in concepts:
        concept_id = concept["conceptId"]
        number = concept_id[:2]
        name = concept["name"]
        folder = CONCEPTS_DIR / concept_id
        concept_result = {
            "passed": True,
            "pagesChecked": 0,
            "partialsChecked": 0,
            "sectionCounts": {},
            "homepagePhotoCount": None,
            "issues": [],
        }

        def fail(message: str) -> None:
            concept_result["passed"] = False
            results["passed"] = False
            concept_result["issues"].append(message)
            results["failures"].append({"concept": concept_id, "issue": message})

        if not folder.exists():
            fail("concept folder missing")
            results["concepts"][concept_id] = concept_result
            continue

        destination_md = ROOT / "docs" / "design-destination-bible" / "concepts" / f"{concept_id}.md"
        if not destination_md.exists():
            fail("concept destination file missing")

        if not (folder / "css" / "concept.css").exists():
            fail("local concept CSS missing")
        if not (folder / "js" / "concept.js").exists():
            fail("local concept JS missing")

        css_text = read(folder / "css" / "concept.css") if (folder / "css" / "concept.css").exists() else ""
        if "object-fit: cover" in css_text:
            fail("cropped photo rule found in active concept CSS")

        for partial_name in REQUIRED_PARTIALS:
            partial_path = folder / "partials" / partial_name
            if not partial_path.exists():
                fail(f"required partial missing: {partial_name}")
                continue
            concept_result["partialsChecked"] += 1
            partial_text = read(partial_path)
            if not concept_specific(partial_text, number, name):
                fail(f"partial is not concept-specific: {partial_name}")
            if partial_name == "mobile-menu.html" and 'aria-hidden="true"' not in partial_text:
                fail("mobile menu is not closed by default")
            if partial_name == "cookie-banner.html" and "position" in partial_text.lower():
                fail("cookie banner partial contains layout CSS instead of concept CSS ownership")

        rhythm = concept.get("colourRhythm", {})
        sequence = tuple(rhythm.get("homepageSectionColourSequence", []))
        if len(sequence) != 10:
            fail("colour rhythm contract does not define 10 homepage colours")
        sequence_key = json.dumps(sequence)
        if sequence_key in seen_colour_sequences:
            fail(f"homepage colour sequence duplicates {seen_colour_sequences[sequence_key]}")
        seen_colour_sequences[sequence_key] = concept_id

        for page in REQUIRED_PAGES:
            page_path = folder / page
            if not page_path.exists():
                fail(f"page missing: {page}")
                continue
            concept_result["pagesChecked"] += 1
            html = read(page_path)
            section_count = count_main_sections(html)
            concept_result["sectionCounts"][page] = section_count
            if section_count != 10:
                fail(f"{page} has {section_count} real sections, expected 10")

            css_links = active_links(html, "css")
            js_links = active_links(html, "js")
            if css_links != ["../../css/sofiati-brand-foundation.css", "css/concept.css"]:
                fail(f"{page} active CSS links are not clean: {css_links}")
            if js_links != ["../../js/sofiati-brand-foundation.js", "js/concept.js"]:
                fail(f"{page} active JS links are not clean: {js_links}")

            for token in FORBIDDEN_ACTIVE_TOKENS:
                if token in html:
                    fail(f"{page} contains forbidden active token `{token}`")
                    break

            body_match = re.search(r"<body\b([^>]*)>", html, re.I)
            if not body_match or f"c{number}-site" not in body_match.group(1):
                fail(f"{page} body classes are not concept-specific")

            main_match = re.search(r"<main\b([^>]*)>", html, re.I)
            if not main_match or f"c{number}-main" not in main_match.group(1):
                fail(f"{page} main class is not concept-specific")

            blanks = figure_without_image(html)
            if blanks:
                fail(f"{page} contains blank image frame(s)")

            broken = local_page_links(html, folder)
            if broken:
                fail(f"{page} contains broken local links: {broken}")

            if page == "index.html":
                photos = homepage_photo_count(html)
                concept_result["homepagePhotoCount"] = photos
                if photos < 2 or photos > 5:
                    fail(f"homepage photo count {photos} outside 2-5 range")
                if len(cta_styles(html)) < 3:
                    fail("homepage CTA rhythm is too repetitive")

        results["concepts"][concept_id] = concept_result

    return results, results["passed"]


def write_reports(results: dict) -> None:
    json_path = SCRIPT_RUNS / "50-new-websites-compliance-audit.json"
    md_path = SCRIPT_RUNS / "50-new-websites-compliance-audit.md"
    write(json_path, json.dumps(results, indent=2))
    lines = [
        "# 50 New Websites Compliance Audit",
        "",
        f"- Concepts checked: {results['totalConcepts']}",
        f"- Passed: {results['passed']}",
        f"- Failures: {len(results['failures'])}",
        "",
    ]
    if results["failures"]:
        lines.extend(["## Failures", ""])
        lines.extend(f"- `{item['concept']}`: {item['issue']}" for item in results["failures"])
    else:
        lines.extend(["All compliance checks passed."])
    write(md_path, "\n".join(lines))


def main() -> int:
    results, passed = audit()
    write_reports(results)
    print(f"Compliance audit passed: {passed}")
    print(f"Failures: {len(results['failures'])}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
