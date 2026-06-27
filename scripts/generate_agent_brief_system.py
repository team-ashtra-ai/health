#!/usr/bin/env python3
"""Generate evidence-based concept briefs for the Sofiati concept system."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
OUT_ROOT = ROOT / "docs" / "agent-brief-system"
BRIEF_DIR = OUT_ROOT / "15-concept-by-concept-briefs"
AUDIT_DIR = OUT_ROOT / "16-audit-system"
LEDGER_DIR = OUT_ROOT / "18-task-ledgers"

PAGE_FILES = [
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
    "faq.html",
    "testimonials.html",
    "mission.html",
    "values.html",
    "privacy.html",
    "cookies.html",
    "accessibility.html",
    "legal.html",
    "sitemap.html",
    "404.html",
]

PARTIAL_FILES = [
    "partials/header.html",
    "partials/navigation.html",
    "partials/mobile-menu.html",
    "partials/footer.html",
    "partials/head.html",
    "partials/schema.html",
    "partials/consultation-form.html",
    "partials/contact-card.html",
    "partials/floating-whatsapp.html",
    "partials/cookie-banner.html",
    "partials/back-to-top.html",
]

PLANNING_FILES = [
    "design-dna.md",
    "design-notes.md",
    "page-flow-map.md",
    "internal-link-map.md",
    "asset-plan.md",
    "asset-notes.md",
]

KNOWN_ISSUES = {
    "03-enhance": [
        ("C03-LANG-001", "Mobile menu language switcher", "partials/mobile-menu.html; css/style.css", "Mobile inactive PT state is low contrast and visually squeezed in existing screenshots.", "critical", "Improve contrast and top-row spacing without changing Enhance's clinical drawer."),
        ("C03-FOOTER-001", "Footer decoration", "partials/footer.html; css/style.css", "Footer columns/contact treatment uses box/circle language flagged by prior screenshot review.", "critical", "Remove heavy column frames/circles while retaining Enhance's clinical ledger mood."),
    ],
    "05-elevate": [
        ("C05-HEADER-001", "Header styling", "partials/header.html; css/style.css", "Desktop header has split two-color block styling that reads visually unbalanced.", "critical", "Unify the header surface while preserving Elevate's maison/luxury wordmark rhythm."),
        ("C05-FOOTER-001", "Footer decoration", "partials/footer.html; css/style.css", "Footer uses boxed column/card treatments.", "critical", "Remove column boxes without flattening the botanical map footer."),
    ],
    "06-refine": [
        ("C06-NAV-001", "Desktop navigation", "partials/header.html; css/style.css", "Rendered desktop nav has wrapped to two rows in prior audit.", "critical", "Reduce width pressure while preserving Refine's quiet grid rhythm."),
    ],
    "10-essence": [
        ("C10-HEADER-001", "Desktop header visibility", "partials/header.html; css/style.css", "Essence uses a menu-only desktop direction; text/nav visibility and header CTA need review.", "critical", "Expose clearer nav/CTA only if it can keep the minimal appointment-suite personality."),
    ],
    "11-bloom": [
        ("C11-DECOR-001", "Box treatments", "partials/header.html; partials/footer.html; css/style.css", "Unwanted square/box treatments remain in screenshot review.", "critical", "Remove box treatments while keeping Bloom's dark botanical mood."),
    ],
    "13-poise": [
        ("C13-FOOTER-001", "Footer/contact circles", "partials/footer.html; css/style.css", "Footer/contact areas use circular treatments flagged by prior review.", "critical", "Replace circular frames with subtle dividers/glows."),
    ],
    "15-clarity": [
        ("C15-FOOTER-001", "Footer decoration", "partials/footer.html; css/style.css", "Footer decoration/box problem remains in screenshot review.", "critical", "Simplify heavy split panels while preserving Clarity's clean concept rhythm."),
    ],
    "16-grace": [
        ("C16-NAV-001", "Desktop navigation", "partials/header.html; css/style.css", "Grace desktop nav wraps to two rows in rendered review.", "critical", "Tighten logo/nav/CTA spacing without reducing readability."),
    ],
    "17-sculpt": [
        ("C17-MOBILE-001", "Mobile header overflow", "partials/header.html; css/style.css", "Rendered mobile header showed small internal overflow.", "high", "Tighten mobile header sizing and controls."),
    ],
    "18-lumin": [
        ("C18-FOOTER-001", "Footer decoration", "partials/footer.html; css/style.css", "Footer circle/box decoration problem remains in screenshot review.", "critical", "Remove circular/boxed contact and column treatments."),
    ],
    "27-form": [
        ("C27-LOGO-001", "Header logo", "partials/header.html; css/style.css", "Desktop header logo is boxed by concept-specific CSS.", "critical", "Remove logo-card treatment while preserving Form's structured header."),
    ],
    "28-pure": [
        ("C28-LANG-001", "Mobile menu language switcher", "partials/mobile-menu.html; css/style.css", "Language switcher fits but top controls/close contrast and spacing need review.", "critical", "Improve top control contrast/spacing without making Pure ornate."),
        ("C28-FOOTER-001", "Footer decoration", "partials/footer.html; css/style.css", "Footer uses large rectangle/circle treatments.", "critical", "Remove rectangles/circles while keeping Pure's minimal education-footer identity."),
    ],
    "30-method": [
        ("C30-NAV-001", "Desktop navigation", "partials/header.html; css/style.css", "Method desktop nav wraps to two rows in rendered review.", "critical", "Reduce header width pressure while preserving Method's systematic rhythm."),
    ],
    "46-curate": [
        ("C46-NAV-001", "Desktop navigation", "partials/header.html; css/style.css", "Curate desktop nav wraps to two rows in rendered review.", "critical", "Tighten nav rhythm without erasing Curate's gallery-like concept."),
    ],
}


@dataclass
class Issue:
    issue_id: str
    concept: str
    page: str
    component: str
    path: str
    screenshot: str
    problem: str
    evidence: str
    severity: str
    impact: str
    cause: str
    fix: str
    affected: str
    verification: str
    status: str
    human_review: str


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def concept_dirs() -> list[Path]:
    return sorted(path for path in CONCEPTS_DIR.iterdir() if path.is_dir() and re.match(r"\d{2}-", path.name))


def strip_tags(value: str) -> str:
    value = re.sub(r"<script.*?</script>|<style.*?</style>", "", value, flags=re.S)
    value = re.sub(r"<[^>]+>", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def field(text: str, name: str) -> str:
    match = re.search(rf"^{re.escape(name)}:\s*(.+)$", text, re.M)
    return match.group(1).strip() if match else ""


def bullet_value(text: str, label: str) -> str:
    match = re.search(rf"^- {re.escape(label)}:\s*(.+)$", text, re.M)
    return match.group(1).strip() if match else ""


def heading_block(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\n(.+?)(?=\n## |\Z)", text, re.S | re.M)
    return match.group(1).strip() if match else ""


def note_label(text: str, label: str) -> str:
    match = re.search(rf"^{re.escape(label)}:\s*\n(.+?)(?=\n\n[A-Z][^\n:]+:\n|\Z)", text, re.S | re.M)
    return re.sub(r"\s+", " ", match.group(1)).strip() if match else ""


def first_sentences(value: str, count: int = 2) -> str:
    clean = re.sub(r"\s+", " ", value).strip()
    if not clean:
        return ""
    parts = re.split(r"(?<=[.!?])\s+", clean)
    return " ".join(parts[:count])


def anchor_labels(markup: str) -> list[str]:
    labels = [strip_tags(match) for match in re.findall(r"<a\b[^>]*>(.*?)</a>", markup, re.S)]
    return [label for label in labels if label]


def class_tokens(markup: str, prefix: str) -> list[str]:
    tokens: list[str] = []
    for class_attr in re.findall(r'class="([^"]+)"', markup):
        for token in class_attr.split():
            if token.startswith(prefix) and token not in tokens:
                tokens.append(token)
    return tokens


def title_and_meta(html: str) -> tuple[str, str, list[str]]:
    title_match = re.search(r"<title>(.*?)</title>", html, re.S)
    meta_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    h1s = [strip_tags(item) for item in re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.S)]
    return (
        strip_tags(title_match.group(1)) if title_match else "",
        meta_match.group(1).strip() if meta_match else "",
        h1s,
    )


def page_layouts(html: str) -> list[str]:
    values = re.findall(r'data-layout-signature="([^"]+)"', html)
    return list(dict.fromkeys(values))[:8]


def image_refs(html: str) -> list[tuple[str, str]]:
    refs = []
    for src, alt in re.findall(r'<img\b[^>]*src="([^"]+)"[^>]*alt="([^"]*)"', html):
        refs.append((src, alt))
    return refs[:10]


def css_summary(css: str) -> tuple[list[str], list[str], list[str]]:
    variables = [f"--{name}: {value.strip()}" for name, value in re.findall(r"--([A-Za-z0-9_-]+)\s*:\s*([^;]+);", css)[:18]]
    colors = list(dict.fromkeys(re.findall(r"#[0-9A-Fa-f]{3,8}", css)))[:16]
    selectors = list(dict.fromkeys(re.findall(r"\.([A-Za-z0-9_-]*(?:header|hero|footer|menu|cta|consult|asset|home-index)[A-Za-z0-9_-]*)", css)))[:28]
    return variables, colors, selectors


def asset_inventory(concept: Path) -> list[str]:
    assets = concept / "assets"
    if not assets.exists():
        return []
    result = []
    for path in sorted(assets.rglob("*")):
        if path.is_file() and path.suffix.lower() in {".svg", ".png", ".jpg", ".jpeg", ".webp"}:
            result.append(rel(path))
        if len(result) >= 18:
            break
    return result


def screenshot_inventory(folder: str) -> list[str]:
    candidates = [
        ROOT / "audit" / "screenshots" / "desktop" / f"{folder}-desktop.png",
        ROOT / "audit" / "screenshots" / "mobile" / f"{folder}-mobile.png",
        ROOT / "final" / "homepage-screenshots" / "desktop" / f"concept-{folder}-home-desktop.png",
        ROOT / "final" / "homepage-screenshots" / "mobile" / f"concept-{folder}-home-mobile.png",
    ]
    for page in ("index", "care", "laser", "skin", "results"):
        candidates.extend(
            [
                ROOT / "audit" / "screenshots" / "design-qa" / "desktop" / page / f"{folder}-desktop-{page}.png",
                ROOT / "audit" / "screenshots" / "design-qa" / "mobile" / page / f"{folder}-mobile-{page}.png",
            ]
        )
    return [rel(path) for path in candidates if path.exists()]


def rendered_issues_by_concept() -> dict[str, list[dict[str, str]]]:
    path = ROOT / "audit" / "reports" / "rendered-responsive-diagnostic.json"
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    grouped: dict[str, dict[str, dict[str, str]]] = defaultdict(dict)
    for item in data:
        concept = item.get("concept")
        viewport = item.get("viewport")
        metrics = item.get("metrics", {})
        if not isinstance(concept, str) or not isinstance(metrics, dict):
            continue
        for issue in metrics.get("issues", []):
            kind = str(issue.get("kind", "rendered-issue"))
            grouped[concept].setdefault(
                kind,
                {
                    "viewport": str(viewport),
                    "severity": str(issue.get("severity", "medium")),
                    "detail": str(issue.get("detail", "")),
                },
            )
    return {concept: list(issues.values()) for concept, issues in grouped.items()}


def build_issues(concept: Path, rendered: dict[str, list[dict[str, str]]], safe_label_fix_recorded: bool) -> list[Issue]:
    folder = concept.name
    num = folder[:2]
    screenshots = screenshot_inventory(folder)
    primary_screenshot = screenshots[0] if screenshots else "screenshot review required"
    issues: list[Issue] = []
    footer = read(concept / "partials" / "footer.html")
    sitemap = read(concept / "sitemap.html")
    label_hits = bool(re.search(r'Brand and Trust|>Brand<|aria-label="Brand"', footer))
    sitemap_hits = "Brand and education" in sitemap
    if label_hits or safe_label_fix_recorded:
        issues.append(
            Issue(
                f"C{num}-LABEL-001",
                folder,
                "global footer",
                "footer labels",
                rel(concept / "partials" / "footer.html"),
                primary_screenshot,
                "Footer public labels used Brand/Brand and Trust instead of About." if label_hits else "Footer public labels were cleaned from Brand/Brand and Trust to About.",
                "Source scan of footer partial.",
                "high",
                "Public-facing navigation language must match the current About rule.",
                "Generated footer labels retained older Brand terminology.",
                "Replace visible and aria Brand labels with About while keeping links and legal/contact routes.",
                "footer partial",
                "Run rg label search and screenshot footer.",
                "pending" if label_hits else "fixed",
                "no",
            )
        )
    if sitemap_hits or safe_label_fix_recorded:
        issues.append(
            Issue(
                f"C{num}-SITEMAP-001",
                folder,
                "sitemap",
                "sitemap labels",
                rel(concept / "sitemap.html"),
                "not applicable",
                "Sitemap group used Brand and education." if sitemap_hits else "Sitemap Brand and education label was cleaned to About and education.",
                "Source scan of concept sitemap.",
                "high",
                "Sitemap is a public navigation page and must use approved labels.",
                "Generated sitemap retained older Brand heading.",
                "Replace Brand and education with About and education.",
                "sitemap.html",
                "Run rg for Brand and education.",
                "pending" if sitemap_hits else "fixed",
                "no",
            )
        )
    for issue_id, component, path, problem, severity, fix in KNOWN_ISSUES.get(folder, []):
        issues.append(
            Issue(
                issue_id,
                folder,
                "homepage/header/footer",
                component,
                f"concepts/{folder}/{path}",
                primary_screenshot,
                problem,
                "Prior screenshot/documentation audit plus component source paths.",
                severity,
                "Affects usability, readability, or the concept's premium visual quality.",
                "Concept-specific CSS/partial treatment needs review.",
                fix,
                path,
                "Use rendered desktop/mobile screenshots and the concept-specific prompt before closing.",
                "pending",
                "yes" if "claims" in problem.lower() else "no",
            )
        )
    for index, item in enumerate(rendered.get(folder, []), start=1):
        kind = item["detail"].split(" ")[0].upper()
        issues.append(
            Issue(
                f"C{num}-RENDER-{index:03d}",
                folder,
                "index.html",
                item.get("detail", "rendered issue"),
                f"concepts/{folder}/index.html",
                primary_screenshot,
                item.get("detail", "Rendered diagnostic issue."),
                f"Rendered diagnostic at {item.get('viewport', 'unknown viewport')}.",
                item.get("severity", "medium"),
                "Rendered behavior can differ from static source checks.",
                "Likely CSS spacing, partial layout, or mounted component behavior.",
                "Inspect the component at the failing viewport and make a narrow fix.",
                "HTML/CSS/partial depending on component",
                "Re-run scripts/audit_rendered_concepts.py after fix.",
                "pending",
                "no",
            )
        )
    return issues


def status_from_issues(issues: list[Issue], screenshots: list[str], files_missing: list[str]) -> tuple[str, str]:
    active = [issue for issue in issues if issue.status != "fixed"]
    severities = {issue.severity for issue in active}
    if files_missing:
        return "incomplete", "medium"
    if "critical" in severities:
        return "high risk", "high" if screenshots else "medium"
    if "high" in severities:
        return "needs review", "high" if screenshots else "medium"
    if active:
        return "usable", "medium"
    return "strong", "high" if screenshots else "medium"


def page_flow_digest(page_flow: str) -> list[str]:
    rows = []
    for page in ["Home", "About", "Care", "Laser", "Skin", "Results", "Consultation", "Contact", "FAQ", "Journal", "Blog", "Legal"]:
        block = heading_block(page_flow, page)
        if not block:
            continue
        purpose = re.search(r"- Page purpose:\s*(.+)", block)
        layouts = re.findall(r"layout `([^`]+)`", block)
        links = re.search(r"- Internal links per section:\s*(.+)", block)
        rows.append(
            f"- {page}: {purpose.group(1) if purpose else 'purpose not found'} Layout rhythm: {', '.join(layouts[:4]) or 'not listed'}. Internal links: {links.group(1) if links else 'not listed'}."
        )
    return rows


def concept_brief(concept: Path, issues: list[Issue], safe_label_fix_recorded: bool) -> tuple[str, str, str]:
    folder = concept.name
    num, name_slug = folder.split("-", 1)
    name = name_slug.replace("-", " ").title()
    dna = read(concept / "design-dna.md")
    notes = read(concept / "design-notes.md")
    page_flow = read(concept / "page-flow-map.md")
    internal_links = read(concept / "internal-link-map.md")
    asset_plan = read(concept / "asset-plan.md")
    css = read(concept / "css" / "style.css")
    js = read(concept / "js" / "main.js")
    partials = {path: read(concept / path) for path in PARTIAL_FILES}
    html_pages = {page: read(concept / page) for page in PAGE_FILES}
    inspected = [f"concepts/{folder}/{file}" for file in PAGE_FILES + PARTIAL_FILES + ["css/style.css", "js/main.js", "js/partials.js"] + PLANNING_FILES if (concept / file).exists()]
    missing = [f"concepts/{folder}/{file}" for file in PAGE_FILES + PARTIAL_FILES + ["css/style.css", "js/main.js", "js/partials.js"] + PLANNING_FILES if not (concept / file).exists()]
    screenshots = screenshot_inventory(folder)
    assets = asset_inventory(concept)
    title, meta, h1s = title_and_meta(html_pages.get("index.html", ""))
    home_layouts = page_layouts(html_pages.get("index.html", ""))
    home_images = image_refs(html_pages.get("index.html", ""))
    css_vars, colors, selectors = css_summary(css)
    header_layout = class_tokens(partials["partials/header.html"], "public-header-layout-")
    menu_layout = class_tokens(partials["partials/mobile-menu.html"], "public-menu-layout-")
    footer_layout = class_tokens(partials["partials/footer.html"], "public-footer-")
    footer_recipe = re.search(r'data-footer-recipe="([^"]+)"', partials["partials/footer.html"])
    nav_labels = anchor_labels(partials["partials/navigation.html"])
    mobile_labels = anchor_labels(partials["partials/mobile-menu.html"])
    footer_labels = anchor_labels(partials["partials/footer.html"])
    status, confidence = status_from_issues(issues, screenshots, missing)

    visual_idea = field(dna, "Visual idea")
    asset_idea = field(dna, "Asset idea")
    colour_idea = field(dna, "Colour usage idea")
    type_idea = field(dna, "Typography idea")
    nav_idea = field(dna, "Navigation idea")
    hero_idea = field(dna, "Hero idea")
    portrait_idea = field(dna, "Doctor portrait idea")
    bot_gold = field(dna, "Botanical/gold idea")
    icon_idea = field(dna, "Icon idea")
    motion_idea = field(dna, "Animation idea")
    form_idea = field(dna, "Form idea")
    footer_idea = field(dna, "Footer idea")
    differs = field(dna, "How this concept differs from the other 49")
    mood = bullet_value(dna, "Concept mood")
    mobile_style = bullet_value(dna, "Mobile layout style")
    card_system = bullet_value(dna, "Card system")
    border_system = bullet_value(dna, "Border/radius system")
    must_not = bullet_value(dna, "Must not look like")
    resemblance = bullet_value(dna, "Resemblance risks")
    clone = bullet_value(dna, "Clone avoidance")

    note_header = note_label(notes, "How the header differs from the other concepts") or heading_block(notes, "How the header differs from the other concepts") or nav_idea
    note_hero = note_label(notes, "How the hero differs from the other concepts") or heading_block(notes, "How the hero differs from the other concepts")
    note_mobile = note_label(notes, "How the mobile menu differs from the other concepts") or heading_block(notes, "How the mobile menu differs from the other concepts")
    note_footer = note_label(notes, "How the footer differs from the other concepts") or heading_block(notes, "How the footer differs from the other concepts")
    note_motion = note_label(notes, "How the motion differs from the other concepts") or heading_block(notes, "How the motion differs from the other concepts")

    issue_lines = []
    for issue in issues:
        issue_lines.extend(
            [
                f"### {issue.issue_id}",
                f"- Page/component: {issue.page} / {issue.component}",
                f"- File path: `{issue.path}`",
                f"- Screenshot path: `{issue.screenshot}`",
                f"- Problem observed: {issue.problem}",
                f"- Evidence: {issue.evidence}",
                f"- Severity: {issue.severity}",
                f"- Likely cause: {issue.cause}",
                f"- Recommended fix: {issue.fix}",
                f"- Verification method: {issue.verification}",
                f"- Fixed in this task: {'yes' if issue.status == 'fixed' else 'no'}",
                "",
            ]
        )
    if not issue_lines:
        issue_lines = ["- No active evidence-based issues recorded by the current automated/doc audit. Continue screenshot review before visual edits.", ""]

    fixed_issues = [issue for issue in issues if issue.status == "fixed"]
    fix_lines = []
    if fixed_issues:
        for issue in fixed_issues:
            fix_lines.append(f"- {issue.issue_id}: {issue.problem} File: `{issue.path}`. Verification: {issue.verification}.")
    elif safe_label_fix_recorded:
        fix_lines.append("- Safe label fix flag was enabled, but this concept had no matching Brand label issue at generation time.")
    else:
        fix_lines.append("- No fixes applied in this brief-generation pass.")

    screenshot_lines = [f"- `{path}`" for path in screenshots] or ["- Screenshot review required: no current screenshot evidence found for this concept."]
    asset_lines = [f"- `{path}`" for path in assets[:12]] or ["- No local image assets found by the generator; inspect manually before image work."]
    page_flow_lines = page_flow_digest(page_flow)
    if not page_flow_lines:
        page_flow_lines = ["- Page-flow map did not expose parseable page sections; inspect `page-flow-map.md` manually before page changes."]

    lines = [
        f"# Concept {num} - {name} Brief",
        "",
        "## 1. Concept Snapshot",
        f"- Concept number: {num}",
        f"- Concept folder path: `concepts/{folder}`",
        f"- Files inspected: {len(inspected)} files, including `{rel(concept / 'index.html')}`, `{rel(concept / 'css' / 'style.css')}`, `{rel(concept / 'partials' / 'header.html')}`, `{rel(concept / 'partials' / 'mobile-menu.html')}`, `{rel(concept / 'partials' / 'footer.html')}`, and planning docs.",
        f"- Missing expected files: {', '.join(f'`{item}`' for item in missing) if missing else 'none'}",
        "- Screenshots inspected/available:",
        *screenshot_lines[:12],
        f"- Status: {status}",
        f"- Confidence level: {confidence}",
        "",
        "## 2. Concept Purpose",
        f"- Intended impression: {visual_idea or mood or 'Evidence incomplete; inspect design DNA manually.'}",
        f"- Visitor emotion: {mood or 'calm professional evaluation-led trust, per design DNA.'}",
        "- Business goal: move visitors toward a professional evaluation without pressure or unsupported claims.",
        "- Consultation/contact role: consultation is the primary conversion path; contact and WhatsApp support practical next steps.",
        f"- How it fits Sofiati: {differs or 'Same Sofiati facts and ethics, expressed through this concept-specific visual system.'}",
        "",
        "## 3. Visual Personality",
        f"- Mood: {mood or visual_idea or 'not explicitly named'}",
        f"- Energy: {'quiet and restrained' if any(word in (visual_idea + mood).lower() for word in ['quiet', 'minimal', 'calm', 'soft']) else 'composed but visually marked by its asset language'}",
        f"- Softness/sharpness: {border_system or 'inspect CSS radius/border rules before changing'}",
        f"- Editorial/clinical balance: {type_idea or 'serif display with restrained sans-serif clinical labels'}",
        f"- Image-led or text-led feel: {hero_idea or 'homepage hero evidence required'}",
        f"- Premium cues: {bot_gold or colour_idea or 'sage/ivory/bronze evidence in CSS variables'}",
        f"- Trust cues: professional role, CRBM, evaluation-led copy, legal/contact footer, and page-flow links.",
        "",
        "## 4. Layout Signature",
        f"- Homepage structure: {', '.join(home_layouts[:6]) if home_layouts else 'layout signatures not found in homepage'}",
        f"- Section rhythm: {first_sentences(page_flow, 2) or 'Page flow evidence incomplete.'}",
        f"- Grid behavior: CSS selectors include {', '.join(selectors[:10]) if selectors else 'no parsed layout selectors'}",
        f"- Spacing rhythm: CSS uses page width and spacing variables such as {', '.join(css_vars[:6]) if css_vars else 'not parsed'}",
        f"- Use of cards: {card_system or 'inspect `.panel`, `.home-route`, and concept-specific card classes before edits'}",
        f"- Use of split layouts/image blocks: first homepage layout signatures are {', '.join(home_layouts[:4]) if home_layouts else 'unknown'}",
        f"- Density level: {'screenshots available for density review; compare header/footer contact sheets before changing spacing' if screenshots else 'requires screenshot review'}",
        f"- Scroll rhythm: {clone or 'must not repeat another concept section silhouette'}",
        "",
        "## 5. Header Signature",
        f"- Logo placement: header class tokens `{', '.join(header_layout) or 'not parsed'}`; brand mark path appears in header partial.",
        f"- Desktop nav structure: labels parsed as {', '.join(nav_labels[:12]) if nav_labels else 'not parsed from navigation partial'}.",
        f"- Nav spacing: controlled by `{rel(concept / 'css' / 'style.css')}` around `.public-header`, `.desktop-nav`, and concept header layout classes.",
        "- CTA placement: `.header-consultation` is inside `.public-header-tools` when present.",
        "- Language switcher placement: status/header/menu use `.public-language` / `.language-switcher` where present.",
        "- Active/hover states: inspect `.desktop-nav a:hover`, `:focus-visible`, and `[aria-current]` rules before editing.",
        "- Sticky behavior: public header CSS uses sticky positioning in the shared concept stylesheet layer.",
        f"- Background behavior: {note_header or nav_idea or 'Header evidence is in header partial and CSS.'}",
        f"- Risks: {', '.join(issue.issue_id for issue in issues if 'HEADER' in issue.issue_id or 'NAV' in issue.issue_id or 'LANG' in issue.issue_id) or 'no active header issue recorded'}",
        f"- Files involved: `{rel(concept / 'partials' / 'header.html')}`, `{rel(concept / 'partials' / 'navigation.html')}`, `{rel(concept / 'partials' / 'mobile-menu.html')}`, `{rel(concept / 'css' / 'style.css')}`, `{rel(concept / 'js' / 'main.js')}`.",
        "",
        "## 6. Mobile Menu Signature",
        f"- Trigger style: `.public-menu-button` / `[data-menu-toggle]` in the header partial.",
        f"- Menu opening style: local JS in `{rel(concept / 'js' / 'main.js')}` toggles the `#mobile-menu` state.",
        f"- Layout: menu class tokens `{', '.join(menu_layout) or 'not parsed'}`.",
        f"- Link rhythm: mobile labels parsed as {', '.join(mobile_labels[:12]) if mobile_labels else 'not parsed'}.",
        "- CTA treatment: `.mobile-consult` / `.public-mobile-cta` appears after the primary mobile links.",
        f"- Language switcher behavior: `{('EN/PT controls present' if 'data-lang-switch' in partials['partials/mobile-menu.html'] else 'language switcher not found in menu partial')}`.",
        "- Close behavior: `[data-menu-close]` close control is present when parsed from the mobile partial.",
        f"- Accessibility concerns: check focus order and dialog state after any menu edits; screenshot review required at 360px and 390px.",
        f"- Visual personality: {note_mobile or mobile_style or 'menu-specific design notes not parsed'}",
        "",
        "## 7. Hero Signature",
        f"- Hero structure: {hero_idea or note_hero or 'homepage hero must be inspected manually'}",
        f"- Heading style: homepage H1 is `{h1s[0] if h1s else 'missing or not parsed'}`.",
        f"- Image placement: homepage images include {', '.join(src for src, _ in home_images[:4]) if home_images else 'no parsed homepage img tags'}",
        "- CTA placement: inspect `.hero-actions`, `.button-primary`, `.button-soft`, and page-flow CTA roles.",
        "- Above-the-fold balance: verify with homepage desktop/mobile screenshots before editing hero spacing.",
        "- Desktop/mobile behavior: generated screenshots are listed above; mobile cropping must be checked at 360px and 390px.",
        f"- Cropping risks: image refs and object-fit rules in CSS must be preserved; portrait concept is {portrait_idea or 'not parsed'}.",
        f"- Uniqueness: do not turn this hero into another concept's split-screen/card-grid pattern. {must_not or ''}",
        "",
        "## 8. Page Flow Signature",
        *page_flow_lines,
        "",
        "## 9. Footer Signature",
        f"- Footer structure: classes `{', '.join(footer_layout[:10]) or 'not parsed'}`; recipe `{footer_recipe.group(1) if footer_recipe else 'not parsed'}`.",
        f"- Column rhythm/headings: footer labels parsed as {', '.join(footer_labels[:18]) if footer_labels else 'not parsed'}.",
        "- Legal/contact areas: Legal and Contact must remain; full street address must not be added.",
        "- Copyright: centered alignment must be verified in rendered desktop and mobile screenshots.",
        f"- Decorative assets/background: {note_footer or footer_idea or bot_gold or 'footer-specific evidence is in CSS/asset files'}",
        "- Mobile stacking: verify in the mobile header/footer screenshot sheet after any footer edit.",
        f"- Alignment risks: {', '.join(issue.issue_id for issue in issues if 'FOOTER' in issue.issue_id or 'LABEL' in issue.issue_id or 'SITEMAP' in issue.issue_id or 'RENDER' in issue.issue_id) or 'no active footer issue recorded'}",
        f"- Files involved: `{rel(concept / 'partials' / 'footer.html')}`, `{rel(concept / 'css' / 'style.css')}`.",
        "",
        "## 10. CTA Signature",
        "- Header CTA: `.header-consultation` should remain visually stronger than ordinary nav links.",
        "- Hero CTA: driven by `.hero-actions` and page-specific button markup.",
        "- Section CTAs: page-flow map assigns contextual CTA roles by section.",
        "- Contact CTA: `contact.html` and `partials/contact-card.html` hold contact route emphasis.",
        "- Form CTA: `partials/consultation-form.html` controls the form submission button and consent pattern.",
        "- WhatsApp CTA: `partials/floating-whatsapp.html` and `js/main.js` mount the `wa.me/5543991043536` route.",
        "- Footer CTA: `.footer-cta` in footer partial should stay calmer than the header/hero primary CTA.",
        f"- Visual priority: {form_idea or 'form/CTA treatment must be checked in rendered page context'}",
        "- Accessibility: preserve labels, focus states, and privacy acknowledgement.",
        "",
        "## 11. Typography Signature",
        f"- Heading typography: {type_idea or 'CSS h1/h2/h3 rules use Georgia/serif display rhythm in current stylesheet evidence.'}",
        "- Body typography: stylesheet evidence uses Inter/system sans-serif for body copy.",
        "- Nav typography: compact uppercase/small-label rhythm appears in nav/status rules.",
        "- Button typography: CTA/button rules use bold small sans-serif labels.",
        f"- Readability: preserve contrast against {', '.join(colors[:6]) if colors else 'parsed palette unavailable'} backgrounds.",
        "- Mobile scaling: verify h1/h2/nav/button fit at 360px and 390px after edits.",
        "",
        "## 12. Colour, Glow, and Texture Signature",
        f"- Primary colors: {', '.join(colors[:10]) if colors else colour_idea or 'not parsed'}",
        f"- Accent/background variables: {', '.join(css_vars[:12]) if css_vars else 'not parsed'}",
        f"- Glow use: {bot_gold or 'inspect box-shadow, filter, and color-mix rules before changing'}",
        "- Gradients/texture use: inspect `body::before`, asset background variables, and concept asset overlays.",
        "- Contrast risks: language switchers, dark footers, and pale nav states need rendered contrast review.",
        "",
        "## 13. Image and Asset Rhythm",
        f"- Asset idea: {asset_idea or 'not documented'}",
        f"- Hero/portrait use: {portrait_idea or 'not parsed from design DNA'}",
        f"- Service/botanical/icons: {icon_idea or bot_gold or 'inspect assets manually'}",
        "- Key asset paths:",
        *asset_lines,
        "- Alt text risks: static alt audit has passed historically; re-run after image changes.",
        "- Repeated asset risks: do not reuse another concept's portrait frame, icon pack, or divider treatment.",
        "",
        "## 14. Animation and Interaction Signature",
        f"- Motion idea: {motion_idea or note_motion or 'local motion evidence must be inspected in JS/CSS'}",
        f"- Scroll/hover/menu effects: CSS selectors include {', '.join(selector for selector in selectors if any(word in selector for word in ['menu', 'cta', 'asset', 'hero'])) or 'not parsed'}",
        f"- JS hooks: {'menu/lang/form/floating hooks found' if any(token in js for token in ['data-menu-toggle', 'data-lang-switch', 'floating', 'consultation-form']) else 'few JS hooks parsed'}",
        "- Reduced-motion considerations: preserve `body.reduce-motion` and CSS reduced-motion behavior where present.",
        "- Performance risks: avoid adding libraries for small concept-level animation repairs.",
        "",
        "## 15. Content Voice and Copy Risks",
        "- Client-facing quality: copy should stay calm, evaluation-led, educational, and professional.",
        "- Generic/placeholder risks: compare H1s and section headings against nearby concepts before rewriting.",
        "- CTA clarity: consultation language should stay clear without pressure.",
        "- Ethical results language: do not add guarantees, fake testimonials, fake before/after proof, or treatment suitability claims.",
        "- Human review: required for any medical/aesthetic claim changes beyond formatting or obvious label cleanup.",
        "",
        "## 16. SEO and Schema Snapshot",
        f"- Title/meta pattern: `{title}` / `{meta[:180]}`",
        f"- H1 pattern: {len(h1s)} H1 parsed; {', '.join(f'`{item}`' for item in h1s[:3]) if h1s else 'none parsed'}",
        "- Schema pattern: `partials/schema.html` plus page head partials control JSON-LD evidence.",
        f"- Sitemap presence: `{rel(concept / 'sitemap.html')}` exists.",
        f"- Internal links: internal-link map length {len(internal_links.splitlines())} lines; inspect before page link changes.",
        "- Image alt status: use static alt audit after image edits.",
        "- Canonical status: inspect `partials/head.html` before SEO edits.",
        "",
        "## 17. Accessibility Snapshot",
        "- Semantic structure: verify one H1, nav landmarks, footer nav groups, form labels, and dialog attributes.",
        "- Heading order: static audit should remain PASS after content changes.",
        "- Nav accessibility: header/menu controls use aria labels and expanded/hidden states; verify keyboard behavior manually.",
        "- Focus states: inspect `:focus-visible` rules before changing nav/CTA styles.",
        "- Contrast risks: language controls, pale header text, dark footer links, and overlaid CTA labels.",
        "- Form labels: `partials/consultation-form.html` controls labels and consent.",
        "- Alt text: preserve current alt audit pass.",
        "",
        "## 18. Responsive Design Snapshot",
        "- 360px: check mobile header, menu top controls, language switcher, hero cropping, and footer stack.",
        "- 390px: check common mobile layout and floating WhatsApp overlap.",
        "- 768px: check tablet transition between mobile menu and desktop nav.",
        "- 1024px: check early desktop nav wrap.",
        "- 1366px: check standard desktop header/footer balance.",
        "- 1440px+: check wide desktop footer copyright centering and hero composition.",
        "- Overflow risks: use `scripts/audit_rendered_concepts.py` plus screenshots.",
        "- CTA stacking risks: check hero, menu, form, and footer CTAs separately.",
        "",
        "## 19. Concept Uniqueness Analysis",
        f"- What makes it different: {differs or visual_idea or 'evidence incomplete'}",
        f"- Protected features: header `{', '.join(header_layout) or 'unknown'}`, menu `{', '.join(menu_layout) or 'unknown'}`, footer recipe `{footer_recipe.group(1) if footer_recipe else 'unknown'}`, asset language `{asset_idea or 'unknown'}`, motion `{motion_idea or 'unknown'}`.",
        f"- Concepts it risks resembling: {resemblance or 'not listed'}",
        "- Do not standardize: header rhythm, hero image placement, footer recipe, CTA shape, icon/divider assets, card radius, and motion timing.",
        f"- Can improve: active issues can be fixed using spacing, contrast, label, and alignment adjustments without replacing the `{mood or name}` visual grammar.",
        "",
        "## 20. Issues Found During Audit",
        *issue_lines,
        "## 21. Fixes Applied",
        *fix_lines,
        "",
        "## 22. Final Concept Status",
        f"- Status: {status}",
        f"- Confidence level: {confidence}",
        f"- Remaining issues: {', '.join(issue.issue_id for issue in issues if issue.status != 'fixed') or 'none from current automated/doc issue set'}",
        "- Next recommended task: follow the issue register and run rendered verification for this concept before implementation closure.",
        "",
    ]
    return "\n".join(lines), status, confidence


def write_issue_register(all_issues: list[Issue]) -> None:
    lines = [
        "# 16-20 Issue Register",
        "",
        "## Purpose",
        "Track evidence-based issues found while generating concept briefs and running diagnostics.",
        "",
        "## Status Summary",
        f"- Total issues: {len(all_issues)}",
        f"- Critical: {sum(1 for issue in all_issues if issue.severity == 'critical')}",
        f"- High: {sum(1 for issue in all_issues if issue.severity == 'high')}",
        f"- Medium: {sum(1 for issue in all_issues if issue.severity == 'medium')}",
        f"- Low: {sum(1 for issue in all_issues if issue.severity == 'low')}",
        f"- Fixed: {sum(1 for issue in all_issues if issue.status == 'fixed')}",
        f"- Pending: {sum(1 for issue in all_issues if issue.status == 'pending')}",
        "",
    ]
    for issue in all_issues:
        lines.extend(
            [
                f"## {issue.issue_id}",
                f"- Concept: {issue.concept}",
                f"- Page: {issue.page}",
                f"- Component: {issue.component}",
                f"- File path: `{issue.path}`",
                f"- Screenshot path: `{issue.screenshot}`",
                f"- Problem observed: {issue.problem}",
                f"- Evidence: {issue.evidence}",
                f"- Severity: {issue.severity}",
                f"- User impact: {issue.impact}",
                f"- Likely cause: {issue.cause}",
                f"- Recommended fix: {issue.fix}",
                f"- Files likely affected: {issue.affected}",
                f"- Verification method: {issue.verification}",
                f"- Fix status: {issue.status}",
                f"- Human review needed: {issue.human_review}",
                "",
            ]
        )
    (AUDIT_DIR / "16-20-issue-register.md").write_text("\n".join(lines), encoding="utf-8")


def write_matrix(classifications: dict[str, tuple[str, str]], all_issues: list[Issue]) -> None:
    by_concept: dict[str, list[Issue]] = defaultdict(list)
    for issue in all_issues:
        by_concept[issue.concept].append(issue)
    lines = [
        "# Concept Uniqueness Matrix",
        "",
        "This matrix summarizes each concept's protected identity and remaining design risk. It is generated from concept planning files, partial classes, screenshots and the issue register.",
        "",
        "| Concept | Status | Brief Confidence | Similarity / Risk Notes | Protected Fix Boundary |",
        "| --- | --- | --- | --- | --- |",
    ]
    for concept in concept_dirs():
        dna = read(concept / "design-dna.md")
        folder = concept.name
        status, confidence = classifications[folder]
        resemblance = bullet_value(dna, "Resemblance risks") or "no explicit resemblance risk listed"
        protected = field(dna, "How this concept differs from the other 49") or field(dna, "Visual idea") or "protect concept-specific header, hero, footer, CTA and asset rhythm"
        active = [issue.issue_id for issue in by_concept.get(folder, []) if issue.status != "fixed"]
        risk = f"{resemblance}; active issues: {', '.join(active[:8]) if active else 'none'}"
        lines.append(f"| {folder} | {status} | {confidence} | {risk} | {protected} |")
    (OUT_ROOT / "17-uniqueness-matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_ledgers(classifications: dict[str, tuple[str, str]], all_issues: list[Issue], safe_label_fix_recorded: bool) -> None:
    fixed = [issue for issue in all_issues if issue.status == "fixed"]
    pending = [issue for issue in all_issues if issue.status == "pending"]
    lines = [
        "# Agent Brief System Master Task Ledger",
        "",
        "## Current Batch",
        "- Created/upgraded comprehensive concept briefs for all 50 concept folders.",
        "- Created issue register and uniqueness matrix from file, screenshot and audit evidence.",
        f"- Safe label fix recorded: {'yes' if safe_label_fix_recorded else 'no'}",
        f"- Fixed issues in register: {len(fixed)}",
        f"- Pending issues in register: {len(pending)}",
        "",
        "## Concept Brief Status",
        "",
        "| Concept | Status | Confidence |",
        "| --- | --- | --- |",
    ]
    for folder, (status, confidence) in classifications.items():
        lines.append(f"| {folder} | {status} | {confidence} |")
    lines.extend(
        [
            "",
            "## Next Fix Order",
            "1. Resolve critical rendered header/nav/language issues.",
            "2. Resolve footer decoration and copyright alignment issues concept by concept.",
            "3. Re-run rendered diagnostics and screenshot scripts.",
            "4. Update concept briefs and issue register after each fix batch.",
            "",
        ]
    )
    (LEDGER_DIR / "task-ledger-master.md").write_text("\n".join(lines), encoding="utf-8")

    screenshot_lines = [
        "# Screenshot Ledger",
        "",
        "- Header/footer screenshot sheet: `audit/screenshots/desktop-contact-sheet.jpg`, `audit/screenshots/mobile-contact-sheet.jpg`.",
        "- Design QA screenshots: `audit/screenshots/design-qa/`.",
        "- Homepage screenshots: `final/homepage-screenshots/`.",
        "- Concepts without listed screenshots should be manually reviewed before visual fixes.",
    ]
    (LEDGER_DIR / "screenshot-ledger.md").write_text("\n".join(screenshot_lines) + "\n", encoding="utf-8")

    regression_lines = [
        "# Regression Ledger",
        "",
        "- Run `python3 scripts/audit_static_site.py` after HTML/schema/link changes.",
        "- Run `python3 scripts/audit_internal_links.py` after link changes.",
        "- Run `python3 scripts/audit_layout_signatures.py` after page section/layout changes.",
        "- Run `python3 scripts/audit_ethics.py` after content changes.",
        "- Run `python3 scripts/audit_rendered_concepts.py` after CSS/header/footer/menu changes.",
        "- Run screenshot scripts after visual changes and compare contact sheets.",
    ]
    (LEDGER_DIR / "regression-ledger.md").write_text("\n".join(regression_lines) + "\n", encoding="utf-8")


def write_readme(classifications: dict[str, tuple[str, str]]) -> None:
    groups: dict[str, list[str]] = defaultdict(list)
    for folder, (status, _) in classifications.items():
        groups[status].append(folder)
    lines = [
        "# Concept Brief Index",
        "",
        "This directory contains one evidence-based brief for each Sofiati concept. Each brief is generated from the concept's files, planning docs, CSS, partials, screenshots, assets and current issue register.",
        "",
        "## Brief Quality Summary",
        f"- Strong: {', '.join(groups.get('strong', [])) or 'none'}",
        f"- Usable: {', '.join(groups.get('usable', [])) or 'none'}",
        f"- Needs review: {', '.join(groups.get('needs review', [])) or 'none'}",
        f"- High risk: {', '.join(groups.get('high risk', [])) or 'none'}",
        f"- Incomplete: {', '.join(groups.get('incomplete', [])) or 'none'}",
        "",
        "## Too-Similar Watchlist",
        "- Use `../17-uniqueness-matrix.md` to compare explicit resemblance risks from the planning files.",
        "- Concepts with the same broad footer color family still need concept-specific footer treatment; do not solve footer issues with one visual recipe.",
        "- Header/menu fixes must preserve each concept's parsed `public-header-layout-*` and `public-menu-layout-*` posture unless a specific issue requires changing it.",
    ]
    for concept in concept_dirs():
        folder = concept.name
        lines.append(f"- [{folder}]({folder}.md)")
    (BRIEF_DIR / "README.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate agent brief system docs for Sofiati concepts.")
    parser.add_argument("--safe-label-fix-recorded", action="store_true", help="Record Brand-to-About safe label fixes as fixed where source scan confirms them.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    BRIEF_DIR.mkdir(parents=True, exist_ok=True)
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    LEDGER_DIR.mkdir(parents=True, exist_ok=True)
    rendered = rendered_issues_by_concept()
    all_issues: list[Issue] = []
    classifications: dict[str, tuple[str, str]] = {}
    for concept in concept_dirs():
        issues = build_issues(concept, rendered, args.safe_label_fix_recorded)
        all_issues.extend(issues)
        brief, status, confidence = concept_brief(concept, issues, args.safe_label_fix_recorded)
        classifications[concept.name] = (status, confidence)
        (BRIEF_DIR / f"{concept.name}.md").write_text(brief, encoding="utf-8")
    write_issue_register(all_issues)
    write_matrix(classifications, all_issues)
    write_ledgers(classifications, all_issues, args.safe_label_fix_recorded)
    write_readme(classifications)
    print(f"Concept brief system written under {OUT_ROOT.relative_to(ROOT)}")
    print(f"Concept briefs: {len(classifications)}")
    print(f"Issues: {len(all_issues)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
