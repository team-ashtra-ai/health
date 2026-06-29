#!/usr/bin/env python3
from __future__ import annotations
"""
Sofiati Architecture Conflict Repair

Fixes the problems visible after the architecture rebuild:

- duplicated desktop menus/navs
- mobile menu visible by default
- mobile menu overlay sitting behind hero content
- hero text becoming white/pale on pale backgrounds
- oversized header/menu conflicts
- duplicate stylesheet/script references
- false architecture labels where the declared component does not exist
- no-image sections still containing images
- floating CTA / WhatsApp overlap risks
- partials wrongly ignored as production UI

Run from repo root:

  python3 qa/fix_sofiati_architecture_conflicts.py --audit
  python3 qa/fix_sofiati_architecture_conflicts.py --fix
  python3 qa/fix_sofiati_architecture_conflicts.py --fix --branch

Outputs:
  docs/script-runs/architecture-conflict-repair-report.md
  docs/script-runs/architecture-conflict-repair-report.json

Backups:
  Each changed HTML file gets one .bak-conflictfix backup.
"""


import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Any


BRANCH_NAME = "sofiati-architecture-conflict-repair"

CSS_FILE = "sofiati-architecture-conflict-repair.css"
JS_FILE = "sofiati-architecture-conflict-repair.js"

BAD_ASSET_TEXT_RE = re.compile(
    r"pattern decoration|home background|section background|decorative asset|"
    r"texture decoration|CONCEPT-SPECIFIC|concept-specific|section asset|background asset",
    re.I,
)

SECTION_RE = re.compile(r"<section\b[\s\S]*?</section>", re.I)
OPEN_SECTION_RE = re.compile(r"^<section\b[^>]*>", re.I | re.S)
ATTR_RE = re.compile(r'([\w:-]+)\s*=\s*"([^"]*)"')
LINK_RE = re.compile(r'<link\b[^>]*rel=["\']stylesheet["\'][^>]*>', re.I)
SCRIPT_RE = re.compile(r'<script\b[^>]*\bsrc=["\']([^"\']+)["\'][^>]*>\s*</script>', re.I)
HREF_RE = re.compile(r'href=["\']([^"\']+)["\']', re.I)
MOUNT_RE = re.compile(r'data-partial-mount=["\']([^"\']+)["\']', re.I)


def now() -> str:
    return dt.datetime.now().isoformat(timespec="seconds")


def run(cmd: List[str], cwd: Path) -> str:
    try:
        out = subprocess.run(
            cmd,
            cwd=str(cwd),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            check=False,
        )
        return out.stdout.strip()
    except Exception as exc:
        return f"ERROR: {exc}"


def root_from(start: Path) -> Path:
    start = start.resolve()
    for p in [start, *start.parents]:
        if (p / "concepts").is_dir():
            return p
    raise SystemExit("Run this from the repo root or inside the Sofiati repo.")


def rel(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root)).replace(os.sep, "/")
    except ValueError:
        return str(path).replace(os.sep, "/")


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def backup_once(path: Path) -> None:
    backup = path.with_suffix(path.suffix + ".bak-conflictfix")
    if not backup.exists():
        shutil.copy2(path, backup)


def real_pages(root: Path) -> List[Path]:
    return sorted(
        p for p in (root / "concepts").glob("**/*.html")
        if "partials" not in p.parts
    )


def partials(root: Path) -> List[Path]:
    return sorted((root / "concepts").glob("**/partials/*.html"))


def concept_id(path: Path, root: Path) -> str:
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    if "concepts" in parts:
        i = parts.index("concepts")
        if i + 1 < len(parts):
            return parts[i + 1]
    return "unknown"


def rel_href(from_file: Path, target: Path) -> str:
    return os.path.relpath(target, from_file.parent).replace(os.sep, "/")


def parse_attrs(tag: str) -> Dict[str, str]:
    return dict(ATTR_RE.findall(tag))


def set_attr(open_tag: str, name: str, value: str) -> str:
    safe = value.replace('"', "&quot;")
    pat = re.compile(rf'({re.escape(name)}\s*=\s*")[^"]*(")', re.I)
    if pat.search(open_tag):
        return pat.sub(rf"\1{safe}\2", open_tag, count=1)
    return open_tag[:-1] + f' {name}="{safe}">'


def update_open_tag(section: str, updates: Dict[str, str]) -> str:
    m = OPEN_SECTION_RE.match(section)
    if not m:
        return section
    tag = m.group(0)
    new_tag = tag
    for k, v in updates.items():
        new_tag = set_attr(new_tag, k, v)
    return new_tag + section[len(tag):]


def has_any(text: str, needles: List[str]) -> bool:
    low = text.lower()
    return any(n.lower() in low for n in needles)


def has_form(section: str) -> bool:
    return bool(re.search(r"<form\b|<input\b|<textarea\b|<select\b", section, re.I))


def has_tabs(section: str) -> bool:
    return has_any(section, ['role="tab"', "role='tab'", "tablist", "tabpanel", "data-tab", "tab-panel"])


def has_accordion(section: str) -> bool:
    return has_any(section, ["<details", "accordion", "aria-expanded", "data-accordion"])


def has_stepper(section: str) -> bool:
    return has_any(section, ["data-step", "stepper", "process-step", "process-rail", "timeline", "aria-current"])


def has_carousel(section: str) -> bool:
    return has_any(section, ["carousel", "slider", "swiper", "data-carousel", "aria-roledescription"])


def has_comparison(section: str) -> bool:
    return has_any(section, ["comparison", "compare", "<table", "versus"])


def has_route_selector(section: str) -> bool:
    return has_any(section, ["route-selector", "data-route", "route-panel", "tablist", "aria-controls"])


def has_sticky_cta(section: str) -> bool:
    return has_any(section, ["sticky-cta", "cta-dock", "data-sticky", "position: sticky"])


def has_figure(section: str) -> bool:
    return bool(re.search(r"<figure\b[\s\S]*?</figure>", section, re.I))


def has_cards(section: str) -> bool:
    return has_any(section, ["atlas-card-row", "<article", "route-card", "service-card", "card-row"])


def has_bullets(section: str) -> bool:
    return bool(re.search(r"<ul\b|<ol\b", section, re.I))


def has_actions(section: str) -> bool:
    return "atlas-actions" in section or bool(re.search(r"<a\b[^>]*button", section, re.I))


def has_sofiati_photo(section: str) -> bool:
    return 'data-sofiati-photo="true"' in section or "sofiati-photo" in section


def infer_real_component(section: str) -> Tuple[str, str, str]:
    if has_form(section):
        return "real-form-panel", "form-layout", "form-led"
    if has_tabs(section):
        return "real-tabbed-panel", "tabs-layout", "route-led"
    if has_accordion(section):
        return "real-accordion", "accordion-layout", "question-led"
    if has_comparison(section):
        return "real-comparison-panel", "comparison-layout", "comparison-led"
    if has_carousel(section):
        return "real-carousel", "carousel-layout", "journal-led"
    if has_cards(section) and has_figure(section):
        return "card-row-with-media", "copy-cards-media-grid", "cards-led"
    if has_cards(section):
        return "card-row", "card-grid-or-row", "cards-led"
    if has_bullets(section) and has_figure(section):
        return "bullet-list-with-media", "copy-list-media-grid", "step-led"
    if has_bullets(section):
        return "bullet-list", "list-layout", "step-led"
    if has_figure(section) and has_actions(section):
        return "copy-media-actions", "copy-media-grid", "paragraph-led"
    if has_figure(section):
        return "copy-media", "copy-media-grid", "paragraph-led"
    if has_actions(section):
        return "copy-actions", "statement-cta-layout", "paragraph-led"
    return "editorial-statement", "statement-band", "statement-led"


def architecture_mismatches(section: str, attrs: Dict[str, str]) -> List[str]:
    declared = " ".join(
        [
            attrs.get("data-component-type", ""),
            attrs.get("data-html-anatomy", ""),
            attrs.get("data-css-layout", ""),
            attrs.get("data-interaction", ""),
            attrs.get("data-cta-pattern", ""),
            attrs.get("data-content-presentation", ""),
        ]
    ).lower()

    problems = []

    if "tab" in declared and not has_tabs(section):
        problems.append("declares tabs/tabbed panel but no real tab controls/panels exist")
    if "accordion" in declared and not has_accordion(section):
        problems.append("declares accordion but no accordion/details/aria-expanded structure exists")
    if "form" in declared and not has_form(section):
        problems.append("declares form-led/form-first architecture but no real form exists")
    if "stepper" in declared and not has_stepper(section):
        problems.append("declares stepper/process interaction but no real stepper exists")
    if "comparison" in declared and not has_comparison(section):
        problems.append("declares comparison panel but no comparison/table structure exists")
    if "carousel" in declared and not has_carousel(section):
        problems.append("declares carousel but no carousel structure exists")
    if "route-selector" in declared and not has_route_selector(section):
        problems.append("declares route-selector but no selector controls exist")
    if "sticky-cta" in declared and not has_sticky_cta(section):
        problems.append("declares sticky CTA but no sticky CTA structure exists")

    img_treatment = attrs.get("data-image-treatment", "").lower()
    if "no-image" in img_treatment and has_figure(section):
        problems.append("declares no-image treatment but still contains image/figure")

    return problems


def remove_first_figure(section: str) -> str:
    return re.sub(r"\s*<figure\b[\s\S]*?</figure>\s*", "\n", section, count=1, flags=re.I)


def repair_section(section: str, fix: bool) -> Tuple[str, Dict[str, Any]]:
    m = OPEN_SECTION_RE.match(section)
    if not m:
        return section, {"problems": ["could not parse opening section tag"]}

    attrs = parse_attrs(m.group(0))
    sec_no = attrs.get("data-section", "?")
    real_component, real_layout, real_presentation = infer_real_component(section)
    problems = architecture_mismatches(section, attrs)

    info = {
        "section": sec_no,
        "declaredComponent": attrs.get("data-component-type", ""),
        "declaredLayout": attrs.get("data-css-layout", ""),
        "declaredInteraction": attrs.get("data-interaction", ""),
        "actualComponent": real_component,
        "actualLayout": real_layout,
        "actualPresentation": real_presentation,
        "hasFigure": has_figure(section),
        "hasSofiatiPhoto": has_sofiati_photo(section),
        "problems": problems,
        "fixes": [],
    }

    if not fix:
        return section, info

    new_section = section

    if any("declares no-image" in p for p in problems):
        new_section = remove_first_figure(new_section)
        info["fixes"].append("removed figure from section because section declared no-image treatment")
        real_component, real_layout, real_presentation = infer_real_component(new_section)

    if problems:
        updates = {
            "data-component-type": real_component,
            "data-css-layout": real_layout,
            "data-content-presentation": real_presentation,
            "data-architecture-repair": "truth-normalized",
        }

        declared_interaction = attrs.get("data-interaction", "").strip().lower()
        if declared_interaction and declared_interaction != "none":
            if not (
                has_tabs(new_section)
                or has_accordion(new_section)
                or has_stepper(new_section)
                or has_carousel(new_section)
                or has_route_selector(new_section)
                or has_sticky_cta(new_section)
            ):
                updates["data-interaction"] = "none"
                info["fixes"].append(f"removed false interaction declaration: {declared_interaction}")

        new_section = update_open_tag(new_section, updates)
        info["fixes"].append(f"normalized component declaration to actual DOM: {real_component}")

    return new_section, info


def dedupe_stylesheet_links(text: str) -> Tuple[str, List[str]]:
    seen = set()
    fixes = []

    def cb(m: re.Match) -> str:
        tag = m.group(0)
        hm = HREF_RE.search(tag)
        if not hm:
            return tag
        href = hm.group(1)
        if href in seen:
            fixes.append(f"removed duplicate stylesheet link: {href}")
            return ""
        seen.add(href)
        return tag

    return LINK_RE.sub(cb, text), fixes


def dedupe_scripts(text: str) -> Tuple[str, List[str]]:
    seen = set()
    fixes = []

    def cb(m: re.Match) -> str:
        src = m.group(1)
        if src in seen:
            fixes.append(f"removed duplicate script: {src}")
            return ""
        seen.add(src)
        return m.group(0)

    return SCRIPT_RE.sub(cb, text), fixes


def ensure_link(text: str, href: str) -> Tuple[str, bool]:
    if href in text:
        return text, False
    tag = f'    <link rel="stylesheet" href="{href}" data-sofiati-conflict-repair="true" />\n'
    if "</head>" in text:
        return text.replace("</head>", tag + "  </head>", 1), True
    return text, False


def ensure_script(text: str, src: str) -> Tuple[str, bool]:
    if src in text:
        return text, False
    tag = f'    <script src="{src}" defer data-sofiati-conflict-repair="true"></script>\n'
    if "</body>" in text:
        return text.replace("</body>", tag + "  </body>", 1), True
    return text, False


def ensure_body_flag(text: str) -> Tuple[str, bool]:
    m = re.search(r"<body\b[^>]*>", text, re.I | re.S)
    if not m:
        return text, False
    tag = m.group(0)
    if 'data-sofiati-conflict-repair="true"' in tag:
        return text, False
    new_tag = tag[:-1] + ' data-sofiati-conflict-repair="true">'
    return text[:m.start()] + new_tag + text[m.end():], True


def write_conflict_css(root: Path) -> Path:
    css_path = root / "css" / CSS_FILE
    css = r'''
/*
Sofiati Architecture Conflict Repair
Purpose: repair duplicated nav/menu conflicts, mobile overlay problems,
hero contrast, full-image sizing, floating widget overlap, and post-architecture cascade issues.
This file is intentionally loaded last.
*/

:root {
  --sofiati-sage: #A2AEA0;
  --sofiati-sage-deep: #485041;
  --sofiati-ivory: #F2EEE3;
  --sofiati-cream: #F8F7F2;
  --sofiati-bronze: #9A6B35;
  --sofiati-gold: #CDAA78;
  --sofiati-ink: #252321;
  --sofiati-conflict-header-z: 1200;
  --sofiati-conflict-menu-z: 1400;
  --sofiati-conflict-widget-z: 1100;
}

/* Runtime nav dedupe marker used by js/sofiati-architecture-conflict-repair.js */
[data-sofiati-hidden-duplicate-nav="true"],
[data-sofiati-hidden-duplicate-ui="true"] {
  display: none !important;
  visibility: hidden !important;
  pointer-events: none !important;
}

/* Keep production UI above page sections without letting drawers leak over the hero. */
[data-partial-mount="status-banner"],
.sofiati-status-banner,
.site-status,
.top-status {
  position: relative;
  z-index: calc(var(--sofiati-conflict-header-z) + 1);
}

[data-partial-mount="header"],
.site-header,
.sofiati-header,
header[role="banner"] {
  position: relative;
  z-index: var(--sofiati-conflict-header-z);
  isolation: isolate;
}

/* The separate mobile-menu partial must be closed by default. */
[data-partial-mount="mobile-menu"] {
  display: none !important;
}

[data-partial-mount="mobile-menu"][data-open="true"] {
  display: block !important;
}

/* Desktop should never show the mobile drawer partial. */
@media (min-width: 901px) {
  [data-partial-mount="mobile-menu"],
  [data-partial-mount="mobile-menu"][data-open="true"] {
    display: none !important;
  }
}

/* Mobile drawer only appears when JS sets data-open=true. */
@media (max-width: 900px) {
  body.sofiati-menu-open {
    overflow: hidden;
  }

  [data-partial-mount="mobile-menu"][data-open="true"] {
    position: fixed !important;
    inset: 0 !important;
    z-index: var(--sofiati-conflict-menu-z) !important;
    display: block !important;
    padding: clamp(5rem, 16vw, 7rem) 1.1rem 2rem !important;
    overflow-y: auto !important;
    background:
      linear-gradient(180deg, rgba(72,80,65,.96), rgba(72,80,65,.91)),
      var(--sofiati-sage-deep) !important;
    color: #fff !important;
    backdrop-filter: blur(16px);
  }

  [data-partial-mount="mobile-menu"][data-open="true"] a,
  [data-partial-mount="mobile-menu"][data-open="true"] button {
    color: #fff !important;
  }

  [data-partial-mount="mobile-menu"][data-open="true"] nav,
  [data-partial-mount="mobile-menu"][data-open="true"] ul,
  [data-partial-mount="mobile-menu"][data-open="true"] ol {
    display: grid !important;
    gap: .5rem !important;
    margin: 0 !important;
    padding: 0 !important;
    list-style: none !important;
  }

  [data-partial-mount="mobile-menu"][data-open="true"] a {
    display: block !important;
    padding: 1rem .9rem !important;
    border-bottom: 1px solid rgba(255,255,255,.16) !important;
    font-size: clamp(1.4rem, 8vw, 2.4rem) !important;
    line-height: 1 !important;
    text-decoration: none !important;
  }
}

/* Menu buttons should stay above the drawer. */
button[aria-label*="Menu" i],
button[aria-controls*="menu" i],
.menu-toggle,
.mobile-menu-toggle,
.sofiati-menu-toggle,
[data-menu-toggle],
[data-mobile-menu-toggle] {
  position: relative;
  z-index: calc(var(--sofiati-conflict-menu-z) + 1);
}

/* Reduce giant post-header dead space introduced by stacked rescue systems. */
.atlas-main,
.architecture-main {
  padding-block-start: clamp(2.5rem, 6vw, 6rem) !important;
}

/* Do not let hero cards force viewport-height layouts that hide content. */
.story-section,
.page-section,
.atlas-section,
.architecture-section {
  min-height: auto !important;
  overflow: visible;
}

/* Hero / section contrast repair. Some concepts generated white text on ivory/sage panels. */
.story-section[data-section="01"] .atlas-section__copy,
.story-section[data-role="opening-promise"] .atlas-section__copy,
.atlas-section[data-section="01"] .atlas-section__copy {
  color: var(--sofiati-ink) !important;
}

.story-section[data-section="01"] h1,
.story-section[data-section="01"] h2,
.story-section[data-section="01"] p,
.story-section[data-section="01"] .eyebrow,
.story-section[data-role="opening-promise"] h1,
.story-section[data-role="opening-promise"] h2,
.story-section[data-role="opening-promise"] p,
.story-section[data-role="opening-promise"] .eyebrow {
  color: var(--sofiati-ink) !important;
  text-shadow: none !important;
}

.story-section[data-section="01"] .eyebrow,
.story-section[data-role="opening-promise"] .eyebrow {
  color: #1f2924 !important;
}

/* Full-image rule: keep entire Franciele image visible. */
img[data-sofiati-photo="true"],
.sofiati-photo,
.sofiati-portrait,
.sofiati-hero-photo,
.sofiati-brand-photo {
  width: 100% !important;
  height: auto !important;
  max-width: 100% !important;
  object-fit: contain !important;
  object-position: center center !important;
  word-break: normal !important;
}

.sofiati-photo-frame,
.sofiati-portrait-frame,
.sofiati-hero-photo-frame,
.atlas-section__media {
  overflow: visible !important;
}

/* Prevent huge blank image frames. */
.sofiati-photo-frame:empty,
.sofiati-portrait-frame:empty,
.sofiati-hero-photo-frame:empty,
.atlas-section__media:empty {
  display: none !important;
}

/* Desktop nav cleanup after JS de-duping. */
[data-partial-mount="header"] nav {
  max-width: 100%;
}

[data-partial-mount="header"] a {
  white-space: nowrap;
}

/* Desktop hero readability and sensible image sizing. */
@media (min-width: 901px) {
  .story-section[data-section="01"],
  .story-section[data-role="opening-promise"] {
    align-items: center !important;
  }

  .story-section[data-section="01"] .atlas-section__media,
  .story-section[data-role="opening-promise"] .atlas-section__media {
    max-width: min(48vw, 620px) !important;
  }

  .story-section[data-section="01"] .atlas-section__copy,
  .story-section[data-role="opening-promise"] .atlas-section__copy {
    max-width: min(42vw, 620px) !important;
  }
}

/* Mobile repair: the drawer must not sit over the hero by default, and headings must not split mid-word. */
@media (max-width: 900px) {
  html,
  body {
    max-width: 100%;
    overflow-x: hidden;
  }

  .atlas-main,
  .architecture-main {
    padding-block-start: 1.25rem !important;
  }

  .story-section,
  .page-section,
  .atlas-section,
  .architecture-section {
    width: min(100% - 1.5rem, 680px) !important;
    margin-inline: auto !important;
    margin-block: 1rem !important;
    padding: clamp(1.1rem, 4vw, 1.6rem) !important;
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: 1rem !important;
    min-height: auto !important;
  }

  .atlas-section__copy {
    width: 100% !important;
    max-width: 100% !important;
    min-width: 0 !important;
    order: 1;
  }

  .atlas-section__media,
  .sofiati-photo-frame,
  .sofiati-portrait-frame,
  .sofiati-hero-photo-frame {
    width: 100% !important;
    max-width: min(100%, 430px) !important;
    margin-inline: auto !important;
    order: 2;
  }

  .story-section h1,
  .page-section h1,
  .atlas-section h1 {
    font-size: clamp(3rem, 13vw, 4.9rem) !important;
    line-height: .92 !important;
    letter-spacing: -0.04em !important;
    max-width: 100% !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
    hyphens: none !important;
    text-wrap: balance;
  }

  .story-section h2,
  .page-section h2,
  .atlas-section h2 {
    font-size: clamp(2rem, 9vw, 3.25rem) !important;
    line-height: 1 !important;
    word-break: normal !important;
    overflow-wrap: normal !important;
    hyphens: none !important;
    text-wrap: balance;
  }

  .atlas-actions {
    display: grid !important;
    grid-template-columns: 1fr !important;
    gap: .75rem !important;
    width: 100% !important;
  }

  .atlas-actions .button,
  .atlas-button,
  .button {
    width: 100%;
    max-width: 100%;
    justify-content: center;
    text-align: center;
  }

  img[data-sofiati-photo="true"],
  .sofiati-photo,
  .sofiati-portrait,
  .sofiati-hero-photo,
  .sofiati-brand-photo {
    max-height: 68vh !important;
  }
}

/* Floating widget conflict repair. Keep it visible but stop covering the main CTA/text. */
[data-partial-mount="floating-widgets"],
.floating-widgets,
.sofiati-floating-widgets,
.whatsapp-floating,
.whatsapp-button,
.back-to-top,
[data-floating-widget] {
  z-index: var(--sofiati-conflict-widget-z) !important;
}

@media (max-width: 900px) {
  [data-partial-mount="floating-widgets"],
  .floating-widgets,
  .sofiati-floating-widgets {
    pointer-events: none;
  }

  [data-partial-mount="floating-widgets"] a,
  [data-partial-mount="floating-widgets"] button,
  .floating-widgets a,
  .floating-widgets button,
  .sofiati-floating-widgets a,
  .sofiati-floating-widgets button {
    pointer-events: auto;
  }

  .sticky-cta,
  .cta-dock,
  [data-sticky-cta],
  [data-architecture-interaction="sticky-cta"] {
    position: static !important;
    inset: auto !important;
    width: 100% !important;
    margin-block: 1rem !important;
  }
}

/* Cookie banner should not block the whole hero permanently. */
.cookie-banner,
.cookie-preferences,
[data-partial-mount="cookie-banner"] > * {
  z-index: calc(var(--sofiati-conflict-widget-z) + 10) !important;
}

@media (max-width: 900px) {
  .cookie-banner,
  .cookie-preferences,
  [data-partial-mount="cookie-banner"] > * {
    max-width: calc(100vw - 1rem) !important;
    left: .5rem !important;
    right: .5rem !important;
    bottom: .5rem !important;
  }
}
'''.strip() + "\n"
    write(css_path, css)
    return css_path


def write_conflict_js(root: Path) -> Path:
    js_path = root / "js" / JS_FILE
    js = r'''
/*
Sofiati Architecture Conflict Repair JS
- Deduplicates repeated navs in header.
- Keeps mobile menu closed by default.
- Provides one accessible mobile menu toggle.
- Prevents architecture JS/partials from leaving the drawer open over the hero.
- Reduces duplicated floating consultation UI when it overlaps.
*/

(function () {
  "use strict";

  const MOBILE_QUERY = "(max-width: 900px)";

  function textOf(el) {
    return (el.textContent || "").replace(/\s+/g, " ").trim().toLowerCase();
  }

  function linkSignature(nav) {
    const links = Array.from(nav.querySelectorAll("a[href]"));
    return links
      .map((a) => {
        const href = (a.getAttribute("href") || "").split("#")[0].trim().toLowerCase();
        const text = textOf(a);
        return href + "::" + text;
      })
      .filter(Boolean);
  }

  function overlapRatio(a, b) {
    if (!a.length || !b.length) return 0;
    const setA = new Set(a);
    const setB = new Set(b);
    let common = 0;
    for (const item of setA) {
      if (setB.has(item)) common += 1;
    }
    return common / Math.min(setA.size || 1, setB.size || 1);
  }

  function dedupeHeaderNavs() {
    const scopes = Array.from(
      document.querySelectorAll('[data-partial-mount="header"], header, .site-header, .sofiati-header')
    );

    for (const scope of scopes) {
      const navs = Array.from(scope.querySelectorAll("nav")).filter((nav) => {
        if (nav.closest('[data-partial-mount="mobile-menu"]')) return false;
        if (nav.dataset.sofiatiHiddenDuplicateNav === "true") return false;
        return linkSignature(nav).length >= 3;
      });

      if (navs.length < 2) continue;

      const keep = [];
      for (const nav of navs) {
        const sig = linkSignature(nav);
        const duplicateOfKept = keep.some((kept) => overlapRatio(sig, linkSignature(kept)) >= 0.72);

        if (duplicateOfKept) {
          nav.dataset.sofiatiHiddenDuplicateNav = "true";
          nav.setAttribute("aria-hidden", "true");
        } else {
          keep.push(nav);
        }
      }
    }
  }

  function ensureMobileMountHasLinks(mobileMount) {
    if (!mobileMount) return;
    if (mobileMount.querySelectorAll("a[href]").length >= 3) return;

    const header = document.querySelector('[data-partial-mount="header"], header, .site-header, .sofiati-header');
    if (!header) return;

    const nav = Array.from(header.querySelectorAll("nav"))
      .filter((n) => n.dataset.sofiatiHiddenDuplicateNav !== "true")
      .sort((a, b) => linkSignature(b).length - linkSignature(a).length)[0];

    if (!nav) return;

    const cloned = nav.cloneNode(true);
    cloned.removeAttribute("id");
    cloned.querySelectorAll("[id]").forEach((el) => el.removeAttribute("id"));
    mobileMount.appendChild(cloned);
  }

  function findMenuButtons() {
    const candidates = Array.from(document.querySelectorAll("button, a, [role='button']"));

    return candidates.filter((el) => {
      const label = [
        el.getAttribute("aria-label") || "",
        el.getAttribute("data-menu-toggle") || "",
        el.getAttribute("data-mobile-menu-toggle") || "",
        el.textContent || "",
      ].join(" ").toLowerCase();

      if (el.closest('[data-partial-mount="mobile-menu"]')) return false;

      return (
        /\bmenu\b/.test(label) ||
        label.includes("open menu") ||
        label.includes("mobile menu") ||
        el.className.toString().toLowerCase().includes("menu-toggle") ||
        el.className.toString().toLowerCase().includes("mobile-menu")
      );
    });
  }

  function closeMenu(mobileMount, buttons) {
    if (!mobileMount) return;
    mobileMount.removeAttribute("data-open");
    mobileMount.setAttribute("aria-hidden", "true");
    document.body.classList.remove("sofiati-menu-open");
    for (const button of buttons) {
      button.setAttribute("aria-expanded", "false");
    }
  }

  function openMenu(mobileMount, buttons) {
    if (!mobileMount) return;
    ensureMobileMountHasLinks(mobileMount);
    mobileMount.setAttribute("data-open", "true");
    mobileMount.setAttribute("aria-hidden", "false");
    document.body.classList.add("sofiati-menu-open");
    for (const button of buttons) {
      button.setAttribute("aria-expanded", "true");
    }

    const firstLink = mobileMount.querySelector("a[href], button");
    if (firstLink) {
      setTimeout(() => firstLink.focus({ preventScroll: true }), 50);
    }
  }

  function setupMobileMenu() {
    const mobileMount = document.querySelector('[data-partial-mount="mobile-menu"]');
    const buttons = findMenuButtons();

    if (!mobileMount) {
      for (const button of buttons) {
        button.setAttribute("aria-expanded", "false");
      }
      return;
    }

    mobileMount.setAttribute("aria-hidden", "true");
    mobileMount.removeAttribute("data-open");

    if (!mobileMount.id) {
      mobileMount.id = "sofiati-mobile-menu";
    }

    for (const button of buttons) {
      button.setAttribute("aria-controls", mobileMount.id);
      button.setAttribute("aria-expanded", "false");

      if (button.dataset.sofiatiMenuBound === "true") continue;
      button.dataset.sofiatiMenuBound = "true";

      button.addEventListener("click", function (event) {
        if (!window.matchMedia(MOBILE_QUERY).matches) return;

        event.preventDefault();
        event.stopPropagation();

        if (mobileMount.getAttribute("data-open") === "true") {
          closeMenu(mobileMount, buttons);
        } else {
          openMenu(mobileMount, buttons);
        }
      });
    }

    mobileMount.addEventListener("click", function (event) {
      const target = event.target;
      if (target && target.closest && target.closest("a[href]")) {
        closeMenu(mobileMount, buttons);
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeMenu(mobileMount, buttons);
      }
    });

    window.addEventListener("resize", function () {
      if (!window.matchMedia(MOBILE_QUERY).matches) {
        closeMenu(mobileMount, buttons);
      }
    });
  }

  function repairHeroContrast() {
    const heroSections = Array.from(
      document.querySelectorAll(
        'section[data-section="01"], section[data-role="opening-promise"]'
      )
    );

    for (const section of heroSections) {
      section.setAttribute("data-hero-contrast-repaired", "true");

      const copy = section.querySelector(".atlas-section__copy");
      if (copy) {
        copy.style.color = "var(--sofiati-ink, #252321)";
      }

      section.querySelectorAll("h1,h2,p,.eyebrow").forEach((el) => {
        el.style.textShadow = "none";
      });
    }
  }

  function dedupeFloatingConsultation() {
    const isMobile = window.matchMedia(MOBILE_QUERY).matches;
    if (!isMobile) return;

    const items = Array.from(document.querySelectorAll("a, button"))
      .filter((el) => textOf(el) === "consultation")
      .filter((el) => {
        const style = window.getComputedStyle(el);
        return style.position === "fixed" || style.position === "sticky";
      });

    if (items.length <= 1) return;

    items.slice(1).forEach((el) => {
      el.dataset.sofiatiHiddenDuplicateUi = "true";
      el.setAttribute("aria-hidden", "true");
    });
  }

  function removeOpenDrawerLeak() {
    const mobileMount = document.querySelector('[data-partial-mount="mobile-menu"]');
    if (!mobileMount) return;

    if (!document.body.classList.contains("sofiati-menu-open")) {
      mobileMount.removeAttribute("data-open");
      mobileMount.setAttribute("aria-hidden", "true");
    }
  }

  function runRepairs() {
    dedupeHeaderNavs();
    setupMobileMenu();
    repairHeroContrast();
    dedupeFloatingConsultation();
    removeOpenDrawerLeak();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", runRepairs);
  } else {
    runRepairs();
  }

  /* Partial loaders often inject after DOMContentLoaded. Re-run a few times safely. */
  [250, 750, 1500, 3000].forEach((delay) => {
    window.setTimeout(runRepairs, delay);
  });
})();
'''.strip() + "\n"
    write(js_path, js)
    return js_path


def process_page(path: Path, root: Path, fix: bool, css_path: Path, js_path: Path) -> Tuple[Dict[str, Any], bool]:
    original = read(path)
    text = original

    report: Dict[str, Any] = {
        "path": rel(path, root),
        "concept": concept_id(path, root),
        "changed": False,
        "sectionCount": len(SECTION_RE.findall(text)),
        "warnings": [],
        "fixes": [],
        "sectionIssues": [],
        "partialMounts": MOUNT_RE.findall(text),
    }

    if report["sectionCount"] != 10:
        report["warnings"].append(f"real page has {report['sectionCount']} sections, expected 10")

    if BAD_ASSET_TEXT_RE.search(text):
        report["warnings"].append("bad generated asset text still present")

    css_href = rel_href(path, css_path)
    js_src = rel_href(path, js_path)

    if fix:
        text, body_changed = ensure_body_flag(text)
        if body_changed:
            report["fixes"].append("added body conflict-repair data flag")

        text, css_fixes = dedupe_stylesheet_links(text)
        report["fixes"].extend(css_fixes)

        text, script_fixes = dedupe_scripts(text)
        report["fixes"].extend(script_fixes)

        text, added_css = ensure_link(text, css_href)
        if added_css:
            report["fixes"].append(f"added conflict repair CSS: {css_href}")

        text, added_js = ensure_script(text, js_src)
        if added_js:
            report["fixes"].append(f"added conflict repair JS: {js_src}")

    if "header" in report["partialMounts"] and "mobile-menu" in report["partialMounts"]:
        report["warnings"].append(
            "header and mobile-menu mounts both exist; CSS/JS will keep mobile menu closed by default and dedupe navs"
        )

    if "footer" not in report["partialMounts"]:
        report["warnings"].append("footer partial mount not detected")
    if "header" not in report["partialMounts"]:
        report["warnings"].append("header partial mount not detected")

    section_infos: List[Dict[str, Any]] = []

    def section_cb(m: re.Match) -> str:
        section = m.group(0)
        new_section, info = repair_section(section, fix)
        if info.get("problems"):
            report["sectionIssues"].append(info)
        section_infos.append(info)
        return new_section

    new_text = SECTION_RE.sub(section_cb, text)
    if fix:
        text = new_text

    photo_sections = [s["section"] for s in section_infos if s.get("hasSofiatiPhoto")]
    report["photoSectionCount"] = len(photo_sections)
    report["photoSections"] = photo_sections

    if len(photo_sections) > 5:
        report["warnings"].append(
            f"photo overuse risk: {len(photo_sections)} sections contain Franciele photos"
        )

    if fix and text != original:
        backup_once(path)
        write(path, text)
        report["changed"] = True

    return report, report["changed"]


def partial_report(path: Path, root: Path) -> Dict[str, Any]:
    text = read(path)
    low = text.lower()
    return {
        "path": rel(path, root),
        "concept": concept_id(path, root),
        "hasHeader": "<header" in low or "site-header" in low or "sofiati-header" in low,
        "hasNav": "<nav" in low,
        "hasMobileSignals": any(x in low for x in ["mobile", "drawer", "menu-toggle", "hamburger", "aria-expanded"]),
        "hasFooter": "<footer" in low or "site-footer" in low,
        "hasCookie": "cookie" in low,
        "hasWhatsApp": "wa.me" in low or "whatsapp" in low,
        "hasAccessibility": "accessibility" in low or "aria-" in low or "skip" in low,
        "badAssetText": bool(BAD_ASSET_TEXT_RE.search(text)),
    }


def write_reports(root: Path, report: Dict[str, Any]) -> None:
    out_dir = root / "docs" / "script-runs"
    out_dir.mkdir(parents=True, exist_ok=True)

    json_path = out_dir / "architecture-conflict-repair-report.json"
    md_path = out_dir / "architecture-conflict-repair-report.md"

    write(json_path, json.dumps(report, indent=2, ensure_ascii=False))

    lines: List[str] = []
    lines.append("# Sofiati Architecture Conflict Repair Report\n")
    lines.append(f"- Generated: `{report['generatedAt']}`")
    lines.append(f"- Branch: `{report['branch']}`")
    lines.append(f"- Mode: `{'fix' if report['fix'] else 'audit'}`")
    lines.append(f"- Real pages checked: `{len(report['pages'])}`")
    lines.append(f"- Partials checked: `{len(report['partials'])}`")
    lines.append(f"- Pages changed: `{len(report['changedPages'])}`")
    lines.append("")

    lines.append("## Screenshot-driven issues addressed\n")
    lines.append("- Desktop duplicated nav/header risk")
    lines.append("- Mobile menu visible by default over hero")
    lines.append("- Mobile drawer z-index and closed/open state")
    lines.append("- Hero text contrast on pale panels")
    lines.append("- Mobile H1 splitting mid-word")
    lines.append("- Floating CTA / WhatsApp overlap risk")
    lines.append("- Duplicate stylesheet/script references")
    lines.append("- False architecture component declarations")
    lines.append("- Partials validated separately from real pages")
    lines.append("")

    if report["changedPages"]:
        lines.append("## Changed pages\n")
        for p in report["changedPages"]:
            lines.append(f"- `{p}`")
        lines.append("")

    lines.append("## Page warnings\n")
    warned = False
    for p in report["pages"]:
        for w in p["warnings"]:
            warned = True
            lines.append(f"- `{p['path']}`: {w}")
    if not warned:
        lines.append("- None")
    lines.append("")

    lines.append("## Section architecture mismatches repaired or reported\n")
    any_issue = False
    for p in report["pages"]:
        if not p["sectionIssues"]:
            continue
        any_issue = True
        lines.append(f"### `{p['path']}`\n")
        for s in p["sectionIssues"]:
            lines.append(
                f"- Section `{s['section']}` declared `{s.get('declaredComponent')}` / "
                f"`{s.get('declaredLayout')}` / `{s.get('declaredInteraction')}` "
                f"but actual DOM is `{s.get('actualComponent')}` / `{s.get('actualLayout')}`."
            )
            for problem in s.get("problems", []):
                lines.append(f"  - {problem}")
            for fix in s.get("fixes", []):
                lines.append(f"  - fix: {fix}")
        lines.append("")
    if not any_issue:
        lines.append("- None")
    lines.append("")

    lines.append("## Photo overuse risks\n")
    any_photo = False
    for p in report["pages"]:
        if p.get("photoSectionCount", 0) > 5:
            any_photo = True
            lines.append(
                f"- `{p['path']}`: `{p['photoSectionCount']}` photo sections "
                f"({', '.join(p.get('photoSections', []))})"
            )
    if not any_photo:
        lines.append("- None above limit")
    lines.append("")

    lines.append("## Partials production UI summary\n")
    for item in report["partials"]:
        flags = []
        for k in ["hasHeader", "hasNav", "hasMobileSignals", "hasFooter", "hasCookie", "hasWhatsApp", "hasAccessibility", "badAssetText"]:
            if item.get(k):
                flags.append(k)
        lines.append(f"- `{item['path']}`: {', '.join(flags) if flags else 'no major UI signals'}")
    lines.append("")

    lines.append("## Files created/updated\n")
    lines.append(f"- `css/{CSS_FILE}`")
    lines.append(f"- `js/{JS_FILE}`")
    lines.append("- `docs/script-runs/architecture-conflict-repair-report.md`")
    lines.append("- `docs/script-runs/architecture-conflict-repair-report.json`")
    lines.append("")

    lines.append("## Next manual visual check\n")
    lines.append("- Desktop should show one nav system, not duplicated left/right full menus.")
    lines.append("- Mobile should not show the drawer links until the Menu button is clicked.")
    lines.append("- Hero title should not split inside the word `Personalized`.")
    lines.append("- Hero text should be readable on every concept.")
    lines.append("- Floating Consultation/WhatsApp should not cover primary hero buttons.")
    lines.append("")

    write(md_path, "\n".join(lines))


def maybe_branch(root: Path, create_branch: bool) -> str:
    current = run(["git", "branch", "--show-current"], root) or "unknown"
    if not create_branch:
        return current

    branches = run(["git", "branch", "--list", BRANCH_NAME], root)
    if branches.strip():
        run(["git", "checkout", BRANCH_NAME], root)
    else:
        run(["git", "checkout", "-b", BRANCH_NAME], root)

    return run(["git", "branch", "--show-current"], root) or BRANCH_NAME


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit", action="store_true", help="Audit only. No files changed.")
    parser.add_argument("--fix", action="store_true", help="Apply safe conflict fixes.")
    parser.add_argument("--branch", action="store_true", help=f"Create/switch to {BRANCH_NAME}.")
    args = parser.parse_args()

    if not args.audit and not args.fix:
        parser.error("Choose --audit or --fix")

    root = root_from(Path.cwd())
    (root / "docs" / "script-runs").mkdir(parents=True, exist_ok=True)
    (root / "css").mkdir(parents=True, exist_ok=True)
    (root / "js").mkdir(parents=True, exist_ok=True)
    (root / "qa").mkdir(parents=True, exist_ok=True)

    branch = maybe_branch(root, args.branch)

    css_path = write_conflict_css(root) if args.fix else root / "css" / CSS_FILE
    js_path = write_conflict_js(root) if args.fix else root / "js" / JS_FILE

    pages = real_pages(root)
    partial_files = partials(root)

    page_reports = []
    changed_pages = []

    for page in pages:
        pr, changed = process_page(page, root, args.fix, css_path, js_path)
        page_reports.append(pr)
        if changed:
            changed_pages.append(pr["path"])

    part_reports = [partial_report(p, root) for p in partial_files]

    report = {
        "generatedAt": now(),
        "branch": branch,
        "fix": args.fix,
        "root": str(root),
        "pages": page_reports,
        "partials": part_reports,
        "changedPages": changed_pages,
        "createdCss": f"css/{CSS_FILE}" if args.fix else None,
        "createdJs": f"js/{JS_FILE}" if args.fix else None,
    }

    write_reports(root, report)

    print("Done.")
    print("Report: docs/script-runs/architecture-conflict-repair-report.md")
    print("JSON:   docs/script-runs/architecture-conflict-repair-report.json")
    if args.fix:
        print(f"Created/updated: css/{CSS_FILE}")
        print(f"Created/updated: js/{JS_FILE}")
        print("Backups use suffix: .bak-conflictfix")
    else:
        print("Audit only. Re-run with --fix to apply safe repairs.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
PY
