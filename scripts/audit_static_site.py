#!/usr/bin/env python3
"""Audit the standalone Sofiati concept builds."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
REPORT_DIR = ROOT / "final"

CONCEPTS = [
    "01-inspire", "02-empower", "03-enhance", "04-renew", "05-elevate",
    "06-refine", "07-glow", "08-balance", "09-radiance", "10-essence",
    "11-bloom", "12-vital", "13-poise", "14-aura", "15-clarity",
    "16-grace", "17-sculpt", "18-lumin", "19-verda", "20-halo",
    "21-calm", "22-precision", "23-ritual", "24-signal", "25-align",
    "26-vivant", "27-form", "28-pure", "29-solace", "30-method",
    "31-evolve", "32-serene", "33-elan", "34-flora", "35-atelier",
    "36-lumina", "37-vellum", "38-origin", "39-kindred", "40-noble",
    "41-vista", "42-softline", "43-meridian", "44-safeguard", "45-silhouette",
    "46-curate", "47-proof", "48-signature", "49-wisdom", "50-sovereign",
]

PAGE_FILES = [
    "index.html", "about.html", "mission.html", "values.html", "care.html",
    "laser.html", "skin.html", "results.html", "testimonials.html", "journal.html",
    "blog.html", "faq.html", "contact.html", "consultation.html", "legal.html",
    "privacy.html", "cookies.html", "accessibility.html", "404.html",
]

PARTIALS = ["status-banner.html", "header.html", "footer.html", "mobile-menu.html", "concept-switcher.html"]

SERVICE_TERMS = [
    "Advanced aesthetic biomedicine",
    "Professional evaluation",
    "Personalised care",
    "Laser care",
    "Laser hair removal",
    "Laser rejuvenation",
    "Skin care",
    "Skin cleansing",
    "Skin quality",
    "Spots and melasma education",
    "Rosacea education",
    "Flaccidity and wrinkles education",
    "Technology-based treatments",
    "Aftercare",
    "Consultation",
    "Results with responsibility",
]

CONTACT_TERMS = [
    "Franciele Sofiati",
    "Advanced Aesthetic Biomedicine",
    "CRBM 6277",
    "(43) 9 9104-3536",
    "sofiatimendonca@gmail.com",
    "@fransofiati_biomedica",
    "Londrina, PR",
    "www.sofiati.com",
]

DESIGN_NOTE_FIELDS = [
    "Concept name:",
    "Assigned inspiration URL:",
    "What was studied:",
    "How the header differs from the other concepts:",
    "How the hero differs from the other concepts:",
    "How the page layout differs from the other concepts:",
    "How the mobile menu differs from the other concepts:",
    "How the footer differs from the other concepts:",
    "How the motion differs from the other concepts:",
    "How Sofiati’s brand identity was applied:",
    "Why this concept is not a clone of the others:",
]

FORBIDDEN_PATTERNS = {
    "full address": re.compile(r"\b(rua|avenida|av\.|r\.)\s+[A-ZÀ-Ý0-9]", re.I),
    "map reference": re.compile(r"google maps|map embed|map pin|mapa|iframe[^>]+maps", re.I),
    "public address found": re.compile(r"public address found|endereco publico encontrado|endereço público encontrado", re.I),
    "unsafe claim": re.compile(
        r"guaranteed results|miracle treatment|risk-free|definitive|perfect skin guaranteed|"
        r"instant transformation|sensational before and after|dream body|aggressive discount",
        re.I,
    ),
    "template residue": re.compile(r"lorem ipsum|old portfolio|placeholder brand|generic template", re.I),
}

ROOT_RUNTIME_RE = re.compile(r"""(?:href|src)=["'](?:/css/|/js/|/partials/|/assets/|../../|../../../)""", re.I)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def text_for(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    return soup.get_text(" ", strip=True)


def html_paths() -> list[Path]:
    return sorted(
        path
        for concept in CONCEPTS
        for path in (CONCEPTS_DIR / concept).glob("*.html")
    )


def is_external(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "mailto", "tel", "sms", "whatsapp"}


def local_target_exists(page: Path, value: str, concept_dir: Path) -> bool:
    if not value or value == "#" or value.startswith("#") or value.startswith("data:"):
        return True
    if is_external(value):
        return True
    clean = value.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return True
    target = (page.parent / clean).resolve()
    try:
        target.relative_to(concept_dir.resolve())
    except ValueError:
        return False
    if clean.endswith("/"):
        return (target / "index.html").exists()
    return target.exists()


def tracked_videos() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files"],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return [line for line in result.stdout.splitlines() if re.search(r"\.(mp4|mov|webm|avi|mkv)$", line, re.I)]


def marker(raw: str, name: str) -> str | None:
    found = re.findall(rf'data-{name}="([^"]+)"', raw)
    return found[-1] if found else None


def check_structure(errors: list[str]) -> list[Path]:
    concept_dirs = sorted(path for path in CONCEPTS_DIR.iterdir() if path.is_dir()) if CONCEPTS_DIR.exists() else []
    names = [path.name for path in concept_dirs]
    if names != CONCEPTS:
        errors.append("Concept directory set/order does not match required names")
        missing = sorted(set(CONCEPTS) - set(names))
        unexpected = sorted(set(names) - set(CONCEPTS))
        if missing:
            errors.append("Missing concept folders: " + ", ".join(missing))
        if unexpected:
            errors.append("Unexpected concept folders: " + ", ".join(unexpected))

    for name in CONCEPTS:
        concept = CONCEPTS_DIR / name
        if not concept.exists():
            continue
        for filename in PAGE_FILES:
            if not (concept / filename).exists():
                errors.append(f"Missing page: concepts/{name}/{filename}")
        for filename in PARTIALS:
            if not (concept / "partials" / filename).exists():
                errors.append(f"Missing partial: concepts/{name}/partials/{filename}")
        if not (concept / "css" / "style.css").exists():
            errors.append(f"Missing CSS: concepts/{name}/css/style.css")
        if not (concept / "js" / "main.js").exists():
            errors.append(f"Missing JS: concepts/{name}/js/main.js")
        if not (concept / "assets").is_dir():
            errors.append(f"Missing assets folder: concepts/{name}/assets")
        notes = concept / "design-notes.md"
        if not notes.exists():
            errors.append(f"Missing design notes: concepts/{name}/design-notes.md")
        else:
            notes_text = notes.read_text(encoding="utf-8")
            for field in DESIGN_NOTE_FIELDS:
                if field not in notes_text:
                    errors.append(f"Missing design note field '{field}' in concepts/{name}/design-notes.md")
    return concept_dirs


def check_files(errors: list[str]) -> dict[str, object]:
    css_hashes: dict[str, list[str]] = {}
    js_hashes: dict[str, list[str]] = {}
    header_markers: dict[str, str] = {}
    footer_markers: dict[str, str] = {}
    menu_markers: dict[str, str] = {}
    section_orders: dict[str, str] = {}

    for name in CONCEPTS:
        concept = CONCEPTS_DIR / name
        if not concept.exists():
            continue
        css = concept / "css" / "style.css"
        js = concept / "js" / "main.js"
        if css.exists():
            css_hashes.setdefault(digest(css), []).append(name)
            css_text = css.read_text(encoding="utf-8")
            for needle in ("site-header", "mobile-menu", "hero", "site-footer", "@media"):
                if needle not in css_text:
                    errors.append(f"CSS missing {needle}: concepts/{name}/css/style.css")
        if js.exists():
            js_hashes.setdefault(digest(js), []).append(name)
            js_text = js.read_text(encoding="utf-8")
            for needle in ("data-menu-toggle", "IntersectionObserver", "data-consultation-form", "sofiati-language", "applyLanguage", "pt-BR"):
                if needle not in js_text:
                    errors.append(f"JS missing {needle}: concepts/{name}/js/main.js")

        combined_text_parts: list[str] = []
        for filename in PAGE_FILES:
            page = concept / filename
            if not page.exists():
                continue
            raw = page.read_text(encoding="utf-8")
            text = text_for(page)
            combined_text_parts.append(text)
            if ROOT_RUNTIME_RE.search(raw):
                errors.append(f"Root/shared runtime dependency in concepts/{name}/{filename}")
            if '<html lang="pt-BR" data-source-lang="en" data-default-lang="pt">' not in raw:
                errors.append(f"Page is not PT-default with English source marker: concepts/{name}/{filename}")
            for needle in ("data-status-banner", "data-lang-switch", "data-default-lang=\"pt\""):
                if needle not in raw:
                    errors.append(f"Missing PT/banner marker {needle}: concepts/{name}/{filename}")
            for label, pattern in FORBIDDEN_PATTERNS.items():
                if pattern.search(raw) or pattern.search(text):
                    errors.append(f"Forbidden {label}: concepts/{name}/{filename}")
            soup = BeautifulSoup(raw, "html.parser")
            for tag in soup.find_all(["a", "link", "script", "img"]):
                attr = "href" if tag.name in {"a", "link"} else "src"
                value = tag.get(attr)
                if value and not local_target_exists(page, value, concept):
                    errors.append(f"Broken local {attr}: concepts/{name}/{filename} -> {value}")
            if filename == "index.html":
                for key, store in (
                    ("header", header_markers),
                    ("footer", footer_markers),
                    ("menu", menu_markers),
                    ("section-order", section_orders),
                ):
                    found = marker(raw, key)
                    if found:
                        store[name] = found
                    else:
                        errors.append(f"Missing data-{key} marker in concepts/{name}/index.html")

        combined_text = " ".join(combined_text_parts)
        lowered = combined_text.lower()
        for term in SERVICE_TERMS:
            if term.lower() not in lowered:
                errors.append(f"Missing required service/topic '{term}' in concept {name}")
        for term in CONTACT_TERMS:
            if term not in combined_text:
                errors.append(f"Missing Sofiati detail '{term}' in concept {name}")
        for filename in ("laser.html", "skin.html", "results.html", "consultation.html"):
            page = concept / filename
            if page.exists():
                page_text = text_for(page)
                if "Results may vary according to individual characteristics" not in page_text:
                    errors.append(f"Missing results disclaimer on concepts/{name}/{filename}")
                if "Information on this website is educational" not in page_text:
                    errors.append(f"Missing educational disclaimer on concepts/{name}/{filename}")

    for label, hashes in (("CSS", css_hashes), ("JS", js_hashes)):
        duplicates = [names for names in hashes.values() if len(names) > 1]
        if duplicates:
            errors.append(f"{label} files are duplicated across concepts: {duplicates}")

    for label, values in (
        ("header", header_markers),
        ("footer", footer_markers),
        ("mobile menu", menu_markers),
        ("section order", section_orders),
    ):
        if len(set(values.values())) != 50:
            errors.append(f"Non-unique {label} markers across concepts")

    return {
        "cssUniqueCount": len(css_hashes),
        "jsUniqueCount": len(js_hashes),
        "uniqueHeaderMarkers": len(set(header_markers.values())),
        "uniqueFooterMarkers": len(set(footer_markers.values())),
        "uniqueMenuMarkers": len(set(menu_markers.values())),
        "uniqueSectionOrders": len(set(section_orders.values())),
    }


def check_screenshots(errors: list[str]) -> int:
    manifest = ROOT / "final" / "homepage-screenshots" / "manifest.json"
    if not manifest.exists():
        errors.append("Missing homepage screenshot manifest")
        return 0
    data = json.loads(manifest.read_text(encoding="utf-8"))
    count = int(data.get("count", 0))
    if count < 100:
        errors.append(f"Expected at least 100 concept homepage screenshots, found {count}")
    for entry in data.get("screenshots", []):
        file_path = ROOT / entry.get("file", "")
        if not file_path.exists():
            errors.append(f"Screenshot listed but missing: {entry.get('file')}")
    return count


def audit() -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    concept_dirs = check_structure(errors)
    uniqueness = check_files(errors)
    videos = tracked_videos()
    if videos:
        errors.append("Tracked video files: " + ", ".join(videos))
    screenshot_count = check_screenshots(errors)
    html_count = len(html_paths())
    summary = {
        "conceptCount": len(concept_dirs),
        "expectedConceptCount": len(CONCEPTS),
        "htmlFileCount": html_count,
        "expectedHtmlFileCount": len(CONCEPTS) * len(PAGE_FILES),
        "trackedVideos": videos,
        "screenshotCount": screenshot_count,
        **uniqueness,
        "errorCount": len(errors),
    }
    if html_count != len(CONCEPTS) * len(PAGE_FILES):
        errors.append(f"Expected {len(CONCEPTS) * len(PAGE_FILES)} concept HTML files, found {html_count}")
        summary["errorCount"] = len(errors)
    return errors, summary


def write_report(errors: list[str], summary: dict[str, object]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / "audit-report.json").write_text(
        json.dumps({"summary": summary, "errors": errors}, indent=2),
        encoding="utf-8",
    )
    lines = ["# Sofiati Standalone Concept Audit", "", "## Summary", ""]
    lines.extend(f"- {key}: {value}" for key, value in summary.items())
    lines.extend(["", "## Errors", ""])
    lines.extend(f"- {error}" for error in errors) if errors else lines.append("- None")
    (REPORT_DIR / "audit-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    errors, summary = audit()
    write_report(errors, summary)
    print(json.dumps(summary, indent=2))
    if errors:
        print(f"Audit failed with {len(errors)} errors. See final/audit-report.md")
        raise SystemExit(1)
    print("Audit passed")


if __name__ == "__main__":
    main()
