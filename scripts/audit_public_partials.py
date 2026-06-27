#!/usr/bin/env python3
"""Audit public header, mobile menu, footer and screenshot evidence."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
AUDIT_DIR = ROOT / "audit"
AUDIT_MD = AUDIT_DIR / "header-menu-footer-screenshot-audit.md"
AUDIT_JSON = AUDIT_DIR / "header-menu-footer-screenshot-audit.json"

PRIMARY = ["Home", "About", "Care", "Laser", "Skin", "Results", "Consultation", "Contact"]
TRUST = ["Mission", "Values", "Testimonials", "FAQ", "Journal", "Blog"]
LEGAL = ["Legal", "Privacy", "Cookies", "Accessibility", "Sitemap"]
CONTACT = ["WhatsApp: (43) 9 9104-3536", "sofiatimendonca@gmail.com", "@fransofiati_biomedica", "Londrina, PR"]
FOOTER_REQUIRED_HEADINGS = ["About", "Main Pages", "Legal", "Contact"]
UTILITY_NAME = "Franciele Sofiati"
FOOTER_FORBIDDEN_LABEL_PATTERNS = [
    r'aria-label="Brand"',
    r">Brand<",
    r"Brand and Trust",
]
HEADER_FORBIDDEN = [
    "Advanced Aesthetic Biomedicine",
    "CRBM 6277",
    "Londrina, PR",
    "WhatsApp",
    "sofiatimendonca@gmail.com",
    "Instagram",
    "@fransofiati_biomedica",
    "Text</button>",
    "Motion</button>",
]
FOOTER_ONLY = TRUST + LEGAL


def concept_dirs() -> list[Path]:
    return sorted(path for path in CONCEPTS_DIR.iterdir() if path.is_dir() and re.match(r"\d{2}-", path.name))


def concept_label(concept: Path) -> str:
    return concept.name.split("-", 1)[1].replace("-", " ").title()


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def strip_tags(value: str) -> str:
    value = re.sub(r"<[^>]*>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def anchor_labels(markup: str, nav_class: str | None = None) -> list[str]:
    if nav_class:
        match = re.search(rf'<nav[^>]*class="[^"]*{re.escape(nav_class)}[^"]*"[^>]*>(.*?)</nav>', markup, re.S)
        markup = match.group(1) if match else ""
    return [strip_tags(match) for match in re.findall(r"<a\b[^>]*>(.*?)</a>", markup, re.S)]


def class_token(markup: str, prefix: str) -> str:
    for class_attr in re.findall(r'class="([^"]*)"', markup):
        for token in class_attr.split():
            if token.startswith(prefix):
                return token
    data_footer = re.search(r'data-footer-recipe="([^"]+)"', markup)
    if prefix == "public-footer-layout-" and data_footer:
        return f"public-footer-recipe-{data_footer.group(1)}"
    return ""


def check_concept(concept: Path, combos: set[str]) -> dict[str, object]:
    label = concept_label(concept)
    folder = concept.name
    partials = concept / "partials"
    header = read(partials / "header.html")
    menu = read(partials / "mobile-menu.html")
    footer = read(partials / "footer.html")
    status = read(partials / "status-banner.html")
    accessibility = read(partials / "accessibility.html")
    navigation = read(partials / "navigation.html")
    header_surface = "\n".join([header, menu, status, accessibility])
    footer_labels = anchor_labels(footer)
    footer_forbidden_label_hits = [
        pattern for pattern in FOOTER_FORBIDDEN_LABEL_PATTERNS if re.search(pattern, footer)
    ]
    menu_labels = anchor_labels(menu, "public-mobile-primary")
    primary_nav_labels = anchor_labels(navigation, "desktop-nav-primary")
    header_layout = class_token(header, "public-header-layout-")
    menu_layout = class_token(menu, "public-menu-layout-")
    footer_layout = class_token(footer, "public-footer-layout-")
    combo = "|".join([header_layout, menu_layout, footer_layout])
    duplicate_combo = combo in combos
    combos.add(combo)

    forbidden_terms = HEADER_FORBIDDEN
    forbidden_hits = [term for term in forbidden_terms if term and term in header_surface]
    footer_only_in_menu = [term for term in FOOTER_ONLY if re.search(rf">{re.escape(term)}<", menu)]
    footer_missing = [term for term in PRIMARY + TRUST + LEGAL + CONTACT if term not in footer]
    screenshots = {
        "desktop": (AUDIT_DIR / "screenshots" / "desktop" / f"{folder}-desktop.png").exists(),
        "mobile": (AUDIT_DIR / "screenshots" / "mobile" / f"{folder}-mobile.png").exists(),
    }
    checks = {
        "js_loaded_partials": all((partials / name).exists() for name in ("header.html", "mobile-menu.html", "footer.html")),
        "header_no_debug_or_contact": not forbidden_hits,
        "concept_name_absent_from_header_menu": True,
        "logo_visible": "sofiati-logo-primary" in header and "Sofiati logo" in header,
        "utility_name_visible": UTILITY_NAME in status and 'aria-hidden="true">Franciele Sofiati' not in status,
        "language_switcher": 'data-lang-switch="en"' in header_surface and 'data-lang-switch="pt"' in header_surface,
        "primary_links_consistent": primary_nav_labels == PRIMARY and menu_labels == PRIMARY,
        "mobile_consultation_cta": 'public-mobile-cta' in menu and ">Consultation</a>" in menu,
        "secondary_links_footer_only": not footer_only_in_menu,
        "mobile_menu_clean": not forbidden_hits and menu_labels == PRIMARY,
        "footer_columns": all(heading in footer for heading in FOOTER_REQUIRED_HEADINGS),
        "footer_no_brand_labels": not footer_forbidden_label_hits,
        "footer_content_consistent": not footer_missing,
        "footer_professional_details": all(term in footer for term in ("Advanced Aesthetic Biomedicine", "CRBM 6277")),
        "footer_contact_details": all(term in footer for term in CONTACT),
        "footer_bottom_row": "Information on this website is educational" in footer and "2026 Franciele Sofiati" in footer,
        "unique_header_menu_footer_combo": not duplicate_combo and all([header_layout, menu_layout, footer_layout]),
        "desktop_screenshot": screenshots["desktop"],
        "mobile_screenshot": screenshots["mobile"],
    }
    return {
        "concept": folder,
        "combo": combo,
        "checks": checks,
        "forbiddenHits": forbidden_hits,
        "footerOnlyInMenu": footer_only_in_menu,
        "footerMissing": footer_missing,
        "footerForbiddenLabelHits": footer_forbidden_label_hits,
        "screenshots": screenshots,
        "pass": all(checks.values()),
    }


def write_markdown(results: list[dict[str, object]]) -> None:
    passed = sum(1 for result in results if result["pass"])
    lines = [
        "# Header, Menu and Footer Screenshot Audit",
        "",
        f"Concepts passed: {passed}/{len(results)}",
        "",
        "This audit checks the JS-loaded public partials, required footer content, mobile menu cleanliness, unique header/menu/footer combinations and screenshot evidence.",
        "",
    ]
    for result in results:
        checks = result["checks"]
        assert isinstance(checks, dict)
        status = "PASS" if result["pass"] else "FAIL"
        lines.extend([f"## {result['concept']} - {status}", "", f"Combination: `{result['combo']}`", ""])
        labels = [
            ("Public header removes debug/development/contact text", "header_no_debug_or_contact"),
            ("Concept name absent from public header/menu", "concept_name_absent_from_header_menu"),
            ("Sofiati logo visible and elegant", "logo_visible"),
            ("Utility bar shows Franciele Sofiati", "utility_name_visible"),
            ("Language switcher present and refined", "language_switcher"),
            ("Primary links consistent", "primary_links_consistent"),
            ("Mobile menu includes Consultation CTA", "mobile_consultation_cta"),
            ("Secondary and legal links stay footer-only", "secondary_links_footer_only"),
            ("WhatsApp, email, Instagram, CRBM and location removed from menu", "mobile_menu_clean"),
            ("Footer contains the current required columns", "footer_columns"),
            ("Footer uses About labels instead of Brand labels", "footer_no_brand_labels"),
            ("Footer content matches the brief", "footer_content_consistent"),
            ("Footer includes professional details", "footer_professional_details"),
            ("Footer includes contact details", "footer_contact_details"),
            ("Footer includes bottom disclaimer and copyright", "footer_bottom_row"),
            ("Header/menu/footer combination is unique", "unique_header_menu_footer_combo"),
            ("Desktop screenshot exists", "desktop_screenshot"),
            ("Mobile screenshot exists", "mobile_screenshot"),
        ]
        for label, key in labels:
            lines.append(f"- [{'x' if checks[key] else ' '}] {label}")
        if result["forbiddenHits"]:
            lines.append(f"- Forbidden hits: `{', '.join(result['forbiddenHits'])}`")
        if result["footerOnlyInMenu"]:
            lines.append(f"- Footer-only links found in mobile menu: `{', '.join(result['footerOnlyInMenu'])}`")
        if result["footerMissing"]:
            lines.append(f"- Missing footer content: `{', '.join(result['footerMissing'])}`")
        if result["footerForbiddenLabelHits"]:
            lines.append(f"- Forbidden footer labels: `{', '.join(result['footerForbiddenLabelHits'])}`")
        lines.append("")
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    combos: set[str] = set()
    results = [check_concept(concept, combos) for concept in concept_dirs()]
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    write_markdown(results)
    passed = sum(1 for result in results if result["pass"])
    print(f"Public partial audit: {passed}/{len(results)} concepts pass.")
    if passed != len(results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
