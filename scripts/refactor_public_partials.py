#!/usr/bin/env python3
"""Refactor public Sofiati header, menu and footer partials across concepts."""

from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
CSS_START = "/* SOFIATI PUBLIC PARTIAL REFACTOR START */"
CSS_END = "/* SOFIATI PUBLIC PARTIAL REFACTOR END */"
JS_START = "/* SOFIATI PUBLIC MENU ACCESSIBILITY START */"
JS_END = "/* SOFIATI PUBLIC MENU ACCESSIBILITY END */"

PRIMARY = [
    ("index.html", "Home"),
    ("about.html", "About"),
    ("care.html", "Care"),
    ("laser.html", "Laser"),
    ("skin.html", "Skin"),
    ("results.html", "Results"),
    ("consultation.html", "Consultation"),
    ("contact.html", "Contact"),
]
FOOTER_TRUST = [
    ("mission.html", "Mission"),
    ("values.html", "Values"),
    ("testimonials.html", "Testimonials"),
    ("faq.html", "FAQ"),
    ("journal.html", "Journal"),
    ("blog.html", "Blog"),
]
FOOTER_LEGAL = [
    ("legal.html", "Legal"),
    ("privacy.html", "Privacy"),
    ("cookies.html", "Cookies"),
    ("accessibility.html", "Accessibility"),
    ("../../sitemap.xml", "Sitemap"),
]
SECONDARY = [
    ("care.html", "Care"),
    ("laser.html", "Laser"),
    ("skin.html", "Skin"),
    ("results.html", "Results"),
]
CARE_ANCHORS = [
    ("#main", "Evaluation"),
    ("care.html", "Care"),
    ("laser.html", "Laser"),
    ("skin.html", "Skin"),
    ("consultation.html", "Consultation"),
]

PAGE_DESCRIPTIONS = {
    "404": "A quiet recovery route back to Sofiati consultation, care and contact pages.",
    "about": "Professional background, care philosophy and credentials for Franciele Sofiati.",
    "accessibility": "Accessibility guidance for the Sofiati website experience.",
    "blog": "Educational writing about laser care, skin quality and responsible aesthetic decisions.",
    "care": "Advanced aesthetic biomedicine shaped by evaluation, planning and aftercare.",
    "consultation": "A calm route to request professional evaluation with Franciele Sofiati.",
    "contact": "Public contact routes for Franciele Sofiati in Londrina, PR.",
    "cookies": "Simple cookie information for the Sofiati website.",
    "faq": "Short answers to common questions before consultation.",
    "index": "Advanced aesthetic biomedicine, laser and skin care guided by professional evaluation.",
    "journal": "Short educational notes for laser, skin and aftercare questions.",
    "laser": "Laser care explained through safety, suitability, preparation and aftercare.",
    "legal": "Responsible legal information for the Sofiati website.",
    "mission": "A responsible Sofiati mission for natural-looking care and clinical clarity.",
    "privacy": "Privacy guidance for consultation requests, communication and patient media.",
    "results": "Responsible expectations for aesthetic results, individual variation and aftercare.",
    "skin": "Skin quality care focused on clarity, texture, sensitivity and barrier respect.",
    "testimonials": "Approval-first trust content without invented claims or private details.",
    "values": "Sofiati values for safety, precision, naturalness and professional restraint.",
}

HEADER_LAYOUTS = [
    "split", "capsule", "clinical", "transparent", "stacked", "minimal", "luminous", "balanced",
    "editorial", "menu-only", "botanical", "dynamic", "poised", "aura", "grid", "curved",
    "sculptural", "glass", "verdant", "halo", "calm", "precision", "ritual", "signal",
    "align", "vivant", "form", "pure", "solace", "method", "evolve", "serene",
    "elan", "flora", "atelier", "lumina", "vellum", "origin", "kindred", "noble",
    "vista", "softline", "meridian", "safeguard", "silhouette", "curate", "proof",
    "signature", "wisdom", "sovereign",
]
MENU_LAYOUTS = [
    "editorial-full", "bottom-sheet", "clinical-drawer", "botanical-fade", "ivory-editorial",
    "minimal-drawer", "luminous-overlay", "two-column", "soft-gradient", "typographic-full",
    "botanical-panel", "energetic-drawer", "quiet-editorial", "soft-overlay", "clinical-grid",
    "curved-panel", "geometric-layer", "frosted-glass", "deep-botanical", "radial",
    "calm-cream", "precise-drawer", "ritual-full", "signal-drawer", "card-stack",
    "animated-full", "shape-panels", "pure-ivory", "warm-full", "process-step",
    "animated-reveal", "serene-ivory", "bold-editorial", "floral-full", "atelier-type",
    "luminous-panel", "paper-menu", "grounded-sage", "warm-card", "dark-elegant",
    "wide-panel", "curved-line", "meridian-drawer", "secure-clean", "silhouette-overlay",
    "boutique-selection", "structured-proof", "signature-full", "wisdom-editorial", "premium-brand",
]
FOOTER_LAYOUTS = [
    "business-card", "split-cta", "technical-ledger", "flowing-botanical", "luxury-skin",
    "minimal-legal", "radiant-ivory", "symmetrical", "airy-editorial", "distilled",
    "immersive-botanical", "staggered-motion", "poised-editorial", "aura-gradient", "clarity-grid",
    "signature-curve", "sculptural", "luminous", "verdant", "halo",
    "calm", "precision", "ritual", "signal", "aligned",
    "vivant", "form", "pure", "solace", "method",
    "evolve", "serene", "elan", "flora", "atelier",
    "lumina", "vellum", "origin", "kindred", "noble",
    "vista", "softline", "meridian", "safeguard", "silhouette",
    "curate", "proof", "signature", "wisdom", "sovereign",
]


def concept_dirs() -> list[Path]:
    return sorted(path for path in CONCEPTS_DIR.iterdir() if path.is_dir() and re.match(r"\d{2}-", path.name))


def concept_meta(concept: Path) -> tuple[int, str, str, str]:
    number = int(concept.name.split("-", 1)[0])
    code = f"{number:02d}"
    slug = concept.name.split("-", 1)[1]
    label = slug.replace("-", " ").title()
    return number, code, slug, label


def strip_marked_block(text: str, start: str, end: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    return pattern.sub("", text).rstrip() + "\n"


def strip_legacy_footer_decoration(text: str) -> str:
    legacy_patterns = [
        r"\n?\.footer-botanical-mark\{[^{}]*\}",
        r"\n?\.site-footer\{position:relative;overflow:hidden\}",
        r"\n?\.site-footer::after\{[^{}]*footer-botanical-stamp[^{}]*\}",
    ]
    for pattern in legacy_patterns:
        text = re.sub(pattern, "", text)
    return text


def links(items: list[tuple[str, str]], class_name: str = "") -> str:
    attrs = f' class="{class_name}"' if class_name else ""
    return "\n".join(f'    <a href="{href}"{attrs}>{label}</a>' for href, label in items)


def language_switcher(modifier: str) -> str:
    return (
        f'<div class="language-switcher public-language public-language-{modifier}" aria-label="Site language">'
        '<button type="button" data-lang-switch="en" aria-pressed="true">EN</button>'
        '<button type="button" data-lang-switch="pt" aria-pressed="false">PT</button>'
        "</div>"
    )


def logo(mark: str = "sage") -> str:
    src = "assets/brand/sofiati-logo-primary-white.png" if mark == "white" else "assets/brand/sofiati-logo-primary-sage.png"
    return (
        '<a class="brand-mark public-brand-mark" href="index.html" aria-label="Sofiati home">'
        f'<img src="{src}" alt="Sofiati logo">'
        "</a>"
    )


def dark_header(number: int, layout: str) -> bool:
    return number % 10 in {4, 9} or layout in {"verdant", "origin", "noble", "signal", "silhouette", "wisdom", "sovereign"}


def status_banner_partial(number: int, code: str) -> str:
    rhythm = ["line", "dot", "leaf", "rule", "monogram"][number % 5]
    return f'''<div class="status-banner public-utility public-utility-{code} public-utility-{rhythm}" data-public-layer="utility">
  <span class="public-utility-rule" aria-hidden="true"></span>
  <span class="public-utility-mark" aria-hidden="true">Sofiati</span>
  {language_switcher("utility")}
</div>
'''


def accessibility_partial(number: int, code: str) -> str:
    return f'''<div class="accessibility-tools public-accessibility public-accessibility-{code}" data-accessibility-tools aria-label="Accessibility controls">
  <button type="button" data-text-size aria-label="Increase text size"><span aria-hidden="true">A+</span></button>
  <button type="button" data-motion-toggle aria-label="Reduce motion"><span aria-hidden="true">~</span></button>
</div>
'''


def header_partial(number: int, code: str) -> str:
    layout = HEADER_LAYOUTS[number - 1]
    logo_mark = "white" if dark_header(number, layout) else "sage"
    secondary = "none" if layout in {"minimal", "menu-only", "pure", "calm"} else ("care" if number % 3 else "path")
    cta = '<a class="header-consultation" href="consultation.html">Consultation</a>' if layout != "menu-only" else ""
    menu_button = (
        '<button class="menu-button public-menu-button" type="button" data-menu-toggle '
        'aria-controls="mobile-menu" aria-expanded="false" aria-label="Open menu">Menu</button>'
    )
    tools = f'<div class="public-header-tools">{cta}{menu_button}</div>'
    nav = '<div class="public-nav-zone" data-navigation-slot="primary"></div>'
    secondary_slot = f'<div class="public-secondary-bar public-secondary-{secondary}" data-public-secondary="{secondary}"><div data-navigation-slot="secondary-{secondary}"></div></div>'

    if layout in {"split", "balanced"}:
        inner = (
            '<div class="public-nav-zone public-nav-left" data-navigation-slot="split-left"></div>'
            f"{logo(logo_mark)}"
            '<div class="public-nav-zone public-nav-right" data-navigation-slot="split-right"></div>'
            f"{tools}"
        )
    elif layout in {"stacked", "ritual", "noble", "signature", "sovereign", "atelier"}:
        inner = (
            f'<div class="public-header-brand-row">{logo(logo_mark)}</div>'
            f'<div class="public-header-nav-row">{nav}{tools}</div>'
        )
    elif layout == "menu-only":
        inner = f"{logo(logo_mark)}<div class=\"public-menu-only-line\" aria-hidden=\"true\"></div>{tools}"
    elif layout in {"halo"}:
        inner = f'<div class="public-halo-shell">{logo(logo_mark)}{nav}</div>{tools}'
    else:
        inner = f"{logo(logo_mark)}{nav}{tools}"

    return f'''<header class="site-header public-header public-header-{code} public-header-layout-{layout}" data-public-header="{layout}">
  <div class="public-header-shell">{inner}</div>
  {secondary_slot}
</header>
'''


def mobile_menu_partial(number: int, code: str) -> str:
    layout = MENU_LAYOUTS[number - 1]
    logo_mark = "sage" if layout in {"bottom-sheet", "ivory-editorial", "calm-cream", "pure-ivory", "serene-ivory", "paper-menu"} else "white"
    cta = '<a class="mobile-consult public-mobile-cta" href="consultation.html">Consultation</a>' if number % 4 else ""
    return f'''<aside class="mobile-menu public-mobile-menu public-menu-{code} public-menu-layout-{layout}" id="mobile-menu" data-public-menu="{layout}" aria-hidden="true" aria-modal="true" role="dialog" aria-label="Site menu" tabindex="-1">
  <img class="mobile-menu-asset-bg public-menu-bg" src="assets/backgrounds/mobile-menu-background.svg" alt="" aria-hidden="true">
  <div class="mobile-menu-top public-mobile-menu-top">
    {logo(logo_mark)}
    {language_switcher("menu")}
    <button class="public-menu-close" type="button" data-menu-close aria-label="Close menu">Close</button>
  </div>
  <nav class="mobile-menu-primary public-mobile-primary" aria-label="Mobile primary navigation">
{links(PRIMARY, "mobile-menu-link")}
  </nav>
  {cta}
</aside>
'''


def footer_group(title: str, items: list[tuple[str, str]], class_name: str) -> str:
    return (
        f'<nav class="footer-link-group {class_name}" aria-label="{title}">\n'
        f"  <h3>{title}</h3>\n"
        f"{links(items)}\n"
        "</nav>"
    )


def footer_is_dark(number: int) -> bool:
    return footer_tone(number)["dark"]


def footer_partial(number: int, code: str) -> str:
    layout = FOOTER_LAYOUTS[number - 1]
    cta_label = ["Book consultation", "Request evaluation", "Contact"][(number - 1) % 3]
    cta_href = "contact.html" if cta_label == "Contact" else "consultation.html"
    cta_attrs = ""
    dark_footer = footer_is_dark(number)
    logo_mark = "white" if dark_footer else "sage"
    monogram = "assets/brand/sofiati-monogram-white.png" if dark_footer else "assets/brand/sofiati-monogram-sage.png"
    return f'''<footer class="site-footer public-footer public-footer-{code} public-footer-layout-{layout}" data-public-footer="{layout}">
  <div class="public-footer-shell">
    <section class="footer-brand-panel" aria-label="Brand">
      {logo(logo_mark)}
      <h3>Brand</h3>
      <img class="footer-monogram" src="{monogram}" alt="" aria-hidden="true">
      <h2>Franciele Sofiati</h2>
      <p class="footer-role">Advanced Aesthetic Biomedicine</p>
      <p class="footer-credential">CRBM 6277</p>
      <p>Laser and skin care guided by professional evaluation in Londrina, PR.</p>
      <a class="footer-cta" href="{cta_href}"{cta_attrs}>{cta_label}</a>
    </section>
    {footer_group("Main Pages", PRIMARY, "footer-main-links")}
    {footer_group("Brand and Trust", FOOTER_TRUST, "footer-trust-links")}
    {footer_group("Legal", FOOTER_LEGAL, "footer-legal-links")}
    <address class="footer-contact" aria-label="Contact">
      <h3>Contact</h3>
      <a href="https://wa.me/5543991043536" rel="noopener" target="_blank">WhatsApp: (43) 9 9104-3536</a>
      <a href="mailto:sofiatimendonca@gmail.com">sofiatimendonca@gmail.com</a>
      <a href="https://www.instagram.com/fransofiati_biomedica/" rel="noopener" target="_blank">@fransofiati_biomedica</a>
      <span>Londrina, PR</span>
    </address>
    <div class="footer-bottom-row">
      <p>Information on this website is educational and does not replace an individual professional evaluation.</p>
      <p>© 2026 Franciele Sofiati. All rights reserved.</p>
    </div>
  </div>
</footer>
'''


def navigation_partial() -> str:
    split_left = PRIMARY[:4]
    split_right = PRIMARY[4:]
    return f'''<template data-navigation-template="primary"><nav class="desktop-nav desktop-nav-primary" aria-label="Primary navigation">
{links(PRIMARY)}
</nav></template>
<template data-navigation-template="compact"><nav class="desktop-nav desktop-nav-compact" aria-label="Primary navigation">
{links(PRIMARY)}
</nav></template>
<template data-navigation-template="split-left"><nav class="desktop-nav desktop-nav-split-left" aria-label="Primary navigation">
{links(split_left)}
</nav></template>
<template data-navigation-template="split-right"><nav class="desktop-nav desktop-nav-split-right" aria-label="Primary navigation">
{links(split_right)}
</nav></template>
<template data-navigation-template="secondary-care"><nav class="desktop-nav desktop-nav-secondary" aria-label="Care quick links">
{links(SECONDARY)}
</nav></template>
<template data-navigation-template="secondary-path"><nav class="desktop-nav desktop-nav-secondary" aria-label="Page context navigation">
{links(CARE_ANCHORS)}
</nav></template>
<template data-navigation-template="secondary-none"><span></span></template>
'''


def color_plan(number: int) -> dict[str, str]:
    plans = [
        {"bg": "linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--deep-sage) 72%,var(--ink)))", "fg": "#fff", "panel": "rgba(255,255,255,.075)", "grid": "1.18fr .78fr .86fr .74fr 1fr"},
        {"bg": "var(--soft-white)", "fg": "var(--ink)", "panel": "color-mix(in srgb,var(--sage) 14%,white)", "grid": "1.25fr .8fr .88fr .72fr 1.05fr"},
        {"bg": "linear-gradient(180deg,var(--cream),var(--soft-white))", "fg": "var(--ink)", "panel": "white", "grid": ".98fr .82fr .98fr .72fr 1.16fr"},
        {"bg": "color-mix(in srgb,var(--deep-sage) 82%,var(--ink))", "fg": "#fff", "panel": "rgba(255,255,255,.09)", "grid": "1.32fr .74fr .84fr .7fr 1fr"},
        {"bg": "linear-gradient(135deg,var(--ink),#384139 48%,var(--bronze))", "fg": "#fff", "panel": "rgba(255,255,255,.08)", "grid": "1.05fr .82fr .88fr .76fr 1.18fr"},
    ]
    return plans[(number - 1) % len(plans)]


FOOTER_TONES = [
    {"bg": "linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--deep-sage) 76%,var(--ink)))", "fg": "#fff", "panel": "rgba(255,255,255,.085)", "line": "rgba(218,178,111,.28)", "accent": "var(--bronze)", "dark": True},
    {"bg": "linear-gradient(90deg,var(--soft-white),color-mix(in srgb,var(--sage) 10%,white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.78)", "line": "color-mix(in srgb,var(--sage) 28%,var(--line))", "accent": "var(--sage)", "dark": False},
    {"bg": "linear-gradient(180deg,var(--cream),var(--soft-white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.82)", "line": "color-mix(in srgb,var(--bronze) 34%,var(--line))", "accent": "var(--bronze)", "dark": False},
    {"bg": "linear-gradient(135deg,#242422,color-mix(in srgb,var(--deep-sage) 44%,#242422))", "fg": "#fff", "panel": "rgba(255,255,255,.07)", "line": "rgba(255,255,255,.16)", "accent": "color-mix(in srgb,var(--bronze) 84%,white)", "dark": True},
    {"bg": "linear-gradient(90deg,color-mix(in srgb,var(--deep-sage) 88%,var(--ink)) 0 38%,var(--soft-white) 38% 100%)", "fg": "var(--ink)", "panel": "rgba(255,255,255,.76)", "line": "color-mix(in srgb,var(--sage) 28%,var(--line))", "accent": "var(--bronze)", "dark": False},
    {"bg": "linear-gradient(180deg,#ffffff,color-mix(in srgb,var(--sage) 7%,white))", "fg": "var(--ink)", "panel": "#fff", "line": "color-mix(in srgb,var(--ink) 12%,var(--line))", "accent": "var(--sage)", "dark": False},
    {"bg": "color-mix(in srgb,var(--sage) 18%,var(--soft-white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.64)", "line": "color-mix(in srgb,var(--sage) 30%,var(--line))", "accent": "color-mix(in srgb,var(--sage) 72%,var(--bronze))", "dark": False},
    {"bg": "linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--bronze) 24%,var(--deep-sage)))", "fg": "#fff", "panel": "rgba(255,255,255,.08)", "line": "rgba(218,178,111,.34)", "accent": "var(--bronze)", "dark": True},
    {"bg": "linear-gradient(135deg,var(--cream),color-mix(in srgb,var(--champagne) 32%,white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.7)", "line": "color-mix(in srgb,var(--bronze) 28%,var(--line))", "accent": "var(--bronze)", "dark": False},
    {"bg": "color-mix(in srgb,var(--deep-sage) 86%,var(--ink))", "fg": "#fff", "panel": "rgba(255,255,255,.09)", "line": "rgba(255,255,255,.18)", "accent": "color-mix(in srgb,var(--bronze) 82%,white)", "dark": True},
    {"bg": "#fbfbf8", "fg": "var(--ink)", "panel": "color-mix(in srgb,var(--sage) 9%,white)", "line": "color-mix(in srgb,var(--ink) 10%,var(--line))", "accent": "var(--sage)", "dark": False},
    {"bg": "linear-gradient(120deg,color-mix(in srgb,var(--champagne) 22%,white),var(--soft-white) 62%,color-mix(in srgb,var(--sage) 12%,white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.74)", "line": "color-mix(in srgb,var(--bronze) 28%,var(--line))", "accent": "var(--bronze)", "dark": False},
    {"bg": "linear-gradient(180deg,var(--ink),#1f2320)", "fg": "#fff", "panel": "rgba(255,255,255,.065)", "line": "rgba(255,255,255,.14)", "accent": "var(--bronze)", "dark": True},
    {"bg": "linear-gradient(90deg,var(--soft-white) 0 64%,color-mix(in srgb,var(--sage) 20%,white) 64% 100%)", "fg": "var(--ink)", "panel": "rgba(255,255,255,.8)", "line": "color-mix(in srgb,var(--sage) 30%,var(--line))", "accent": "var(--sage)", "dark": False},
    {"bg": "linear-gradient(135deg,color-mix(in srgb,var(--deep-sage) 72%,#fff),color-mix(in srgb,var(--ink) 78%,var(--deep-sage)))", "fg": "#fff", "panel": "rgba(255,255,255,.1)", "line": "rgba(255,255,255,.2)", "accent": "color-mix(in srgb,var(--bronze) 76%,white)", "dark": True},
]


FOOTER_SILHOUETTES = [
    {"grid": "minmax(250px,1.34fr) .74fr .86fr .68fr minmax(230px,1.08fr)", "areas": '"brand main trust legal contact" "bottom bottom bottom bottom bottom"', "width": "var(--page)"},
    {"grid": "1.15fr .78fr .92fr minmax(250px,1.16fr)", "areas": '"brand main trust contact" "brand legal legal contact" "bottom bottom bottom bottom"', "width": "min(1180px,calc(100% - 32px))"},
    {"grid": "1.05fr .82fr .95fr .72fr 1.1fr", "areas": '"brand main trust legal contact" "brand bottom bottom bottom contact"', "width": "min(1240px,calc(100% - 36px))"},
    {"grid": "1.12fr .82fr .82fr .7fr", "areas": '"brand brand contact contact" "main trust legal legal" "bottom bottom bottom bottom"', "width": "var(--page)"},
    {"grid": "minmax(230px,1.08fr) .78fr .84fr .68fr minmax(240px,1.18fr)", "areas": '"brand main trust legal contact" "brand main trust legal contact" "bottom bottom bottom bottom bottom"', "width": "min(1280px,calc(100% - 34px))"},
    {"grid": "1.18fr 1fr minmax(260px,1.12fr)", "areas": '"brand main contact" "brand trust contact" "legal legal bottom"', "width": "min(1120px,calc(100% - 34px))"},
    {"grid": "1.2fr .72fr .82fr .72fr", "areas": '"brand brand brand brand" "main trust legal contact" "bottom bottom bottom bottom"', "width": "var(--page)"},
    {"grid": ".9fr .9fr .76fr minmax(260px,1.2fr)", "areas": '"main trust legal contact" "brand brand brand contact" "bottom bottom bottom bottom"', "width": "min(1200px,calc(100% - 40px))"},
    {"grid": "minmax(260px,1.18fr) .84fr .94fr minmax(230px,1fr)", "areas": '"brand main trust contact" "legal legal bottom bottom"', "width": "min(1160px,calc(100% - 30px))"},
    {"grid": "1fr .76fr .88fr .7fr 1.12fr", "areas": '"brand main trust legal contact" "bottom bottom bottom bottom contact"', "width": "var(--page)"},
    {"grid": "1.26fr .7fr .82fr .7fr .98fr", "areas": '"brand main trust legal contact" "brand bottom bottom bottom bottom"', "width": "min(1260px,calc(100% - 42px))"},
    {"grid": "1.06fr .88fr minmax(250px,1.14fr)", "areas": '"brand main contact" "trust legal contact" "bottom bottom bottom"', "width": "min(1040px,calc(100% - 32px))"},
]


FOOTER_BRAND_TREATMENTS = [
    "padding:clamp(16px,2vw,24px);border:1px solid var(--footer-line);background:var(--footer-panel);",
    "padding-left:clamp(14px,2vw,24px);border-left:3px solid var(--footer-accent);",
    "text-align:center;justify-items:center;padding:clamp(10px,1.8vw,18px) clamp(12px,2vw,22px);",
    "padding:clamp(16px,2.2vw,26px);background:linear-gradient(180deg,var(--footer-panel),transparent);border-top:1px solid var(--footer-line);",
    "padding:clamp(14px,2vw,22px);border:1px solid var(--footer-line);box-shadow:inset 0 0 0 6px color-mix(in srgb,var(--footer-panel) 62%,transparent);",
    "padding:0 0 0 clamp(18px,2vw,30px);border-left:1px solid var(--footer-line);",
    "justify-items:center;text-align:center;padding-bottom:clamp(12px,2vw,22px);border-bottom:1px solid var(--footer-line);",
    "padding:clamp(18px,2.4vw,30px);background:var(--footer-panel);border-radius:var(--footer-radius);",
    "padding-top:clamp(10px,1.8vw,20px);border-top:3px double var(--footer-line);",
    "padding:clamp(16px,2.2vw,26px);background:color-mix(in srgb,var(--footer-panel) 72%,transparent);border:1px solid var(--footer-line);border-radius:0 var(--footer-radius) 0 var(--footer-radius);",
]


FOOTER_CONTACT_TREATMENTS = [
    "background:var(--footer-panel);border:1px solid var(--footer-line);padding:clamp(16px,2vw,24px);",
    "background:color-mix(in srgb,var(--footer-accent) 12%,var(--footer-panel));border-left:3px solid var(--footer-accent);padding:clamp(14px,2vw,22px);",
    "background:transparent;border:1px solid var(--footer-line);padding:clamp(14px,2vw,22px);",
    "background:var(--footer-fg);color:var(--footer-bg-solid,var(--ink));padding:clamp(16px,2vw,24px);box-shadow:0 18px 44px rgba(37,35,33,.12);",
    "background:linear-gradient(135deg,var(--footer-panel),transparent);border-top:1px solid var(--footer-line);border-bottom:1px solid var(--footer-line);padding:clamp(14px,2vw,22px);",
    "background:var(--footer-panel);border-radius:999px;padding:clamp(14px,2vw,22px) clamp(18px,2.4vw,28px);",
    "background:rgba(255,255,255,.08);border:1px solid var(--footer-line);padding:clamp(16px,2.2vw,26px);border-radius:var(--footer-radius) 0 var(--footer-radius) 0;",
    "background:color-mix(in srgb,var(--footer-panel) 86%,transparent);border:1px solid var(--footer-line);padding:clamp(16px,2vw,24px);transform:translateY(-8px);",
]


FOOTER_GROUP_TREATMENTS = [
    "border-top:1px solid var(--footer-line);padding-top:12px;",
    "padding-left:14px;border-left:1px solid var(--footer-line);",
    "background:color-mix(in srgb,var(--footer-panel) 48%,transparent);padding:14px;border:1px solid color-mix(in srgb,var(--footer-line) 70%,transparent);",
    "border-bottom:1px solid var(--footer-line);padding-bottom:12px;",
    "padding-top:8px;",
    "box-shadow:inset 0 1px 0 var(--footer-line);padding-top:14px;",
]


FOOTER_ACCENTS = [
    (
        "inset:0 0 auto 0;height:3px;background:linear-gradient(90deg,transparent,var(--footer-accent),transparent);",
        "display:none;",
    ),
    (
        "left:clamp(18px,4vw,70px);top:24px;width:1px;height:calc(100% - 48px);background:linear-gradient(180deg,transparent,var(--footer-line),transparent);",
        "display:none;",
    ),
    (
        "right:clamp(18px,5vw,84px);top:22px;width:86px;height:22px;background:url(\"../assets/botanical/gold-leaf-divider.svg\") center/contain no-repeat;opacity:.42;",
        "display:none;",
    ),
    (
        "right:clamp(20px,7vw,120px);bottom:clamp(18px,4vw,54px);width:min(150px,24vw);aspect-ratio:1;background:url(\"../assets/brand/sofiati-monogram-bronze.png\") center/contain no-repeat;opacity:.11;",
        "display:none;",
    ),
    (
        "inset:0;background:linear-gradient(90deg,var(--footer-line) 1px,transparent 1px) 0 0/96px 96px;opacity:.16;",
        "display:none;",
    ),
    (
        "left:50%;top:18px;width:min(460px,42vw);height:1px;background:linear-gradient(90deg,transparent,var(--footer-accent),transparent);transform:translateX(-50%);",
        "right:50%;bottom:18px;width:80px;height:1px;background:var(--footer-accent);transform:translateX(50%);opacity:.75;",
    ),
    (
        "left:0;top:0;width:min(28vw,320px);height:100%;background:linear-gradient(90deg,color-mix(in srgb,var(--footer-accent) 13%,transparent),transparent);",
        "display:none;",
    ),
    (
        "right:0;top:0;width:min(34vw,420px);height:100%;background:radial-gradient(circle at 55% 40%,color-mix(in srgb,var(--footer-accent) 18%,transparent),transparent 62%);",
        "display:none;",
    ),
    (
        "left:clamp(18px,5vw,90px);right:clamp(18px,5vw,90px);top:18px;height:1px;background:linear-gradient(90deg,var(--footer-accent),transparent,var(--footer-accent));opacity:.58;",
        "display:none;",
    ),
    (
        "right:clamp(24px,6vw,100px);top:28px;width:54px;height:54px;border:1px solid var(--footer-line);border-radius:999px;",
        "right:calc(clamp(24px,6vw,100px) + 15px);top:43px;width:24px;height:24px;background:var(--footer-accent);border-radius:999px;opacity:.26;",
    ),
]


def footer_tone(number: int) -> dict[str, object]:
    return FOOTER_TONES[(number - 1) % len(FOOTER_TONES)]


def footer_shell(number: int) -> dict[str, str]:
    return FOOTER_SILHOUETTES[(number - 1) % len(FOOTER_SILHOUETTES)]


def footer_css(number: int, code: str) -> str:
    tone = footer_tone(number)
    shell = footer_shell(number)
    brand = FOOTER_BRAND_TREATMENTS[(number - 1) % len(FOOTER_BRAND_TREATMENTS)]
    contact = FOOTER_CONTACT_TREATMENTS[(number + 2) % len(FOOTER_CONTACT_TREATMENTS)]
    group = FOOTER_GROUP_TREATMENTS[(number + 1) % len(FOOTER_GROUP_TREATMENTS)]
    accent_before, accent_after = FOOTER_ACCENTS[(number - 1) % len(FOOTER_ACCENTS)]
    radius = [0, 4, 8, 14, 22, 30, 6, 18, 2, 26][(number - 1) % 10]
    top_pad = 32 + (number % 5) * 4
    bottom_pad = 34 + (number % 4) * 5
    gap = 16 + (number % 6) * 3
    logo_width = 176 + (number % 8) * 12
    mono_size = 48 + (number % 5) * 10
    shell_bg = [
        "transparent",
        "color-mix(in srgb,var(--footer-panel) 70%,transparent)",
        "linear-gradient(135deg,var(--footer-panel),transparent)",
        "rgba(255,255,255,.03)",
        "color-mix(in srgb,var(--footer-panel) 82%,transparent)",
    ][(number - 1) % 5]
    shell_border = [
        "0",
        "1px solid var(--footer-line)",
        "1px solid color-mix(in srgb,var(--footer-line) 72%,transparent)",
        "0",
        "1px solid var(--footer-line)",
    ][(number + 1) % 5]
    shell_shadow = [
        "none",
        "0 24px 70px rgba(37,35,33,.09)",
        "inset 0 1px 0 color-mix(in srgb,var(--footer-fg) 8%,transparent)",
        "0 18px 50px rgba(37,35,33,.08)",
    ][(number - 1) % 4]
    footer_top = [
        "1px solid var(--footer-line)",
        "3px solid color-mix(in srgb,var(--footer-accent) 62%,transparent)",
        "0",
        "1px double var(--footer-line)",
    ][(number - 1) % 4]
    bottom_style = [
        "justify-content:space-between;text-align:left;",
        "justify-content:center;text-align:center;",
        "display:grid;grid-template-columns:minmax(0,1fr) auto;",
        "justify-content:flex-start;",
    ][(number - 1) % 4]
    tablet_areas = [
        '"brand contact" "main trust" "legal legal" "bottom bottom"',
        '"brand brand" "contact contact" "main trust" "legal legal" "bottom bottom"',
        '"contact brand" "main trust" "legal legal" "bottom bottom"',
        '"brand main" "contact trust" "legal legal" "bottom bottom"',
    ][(number - 1) % 4]
    mobile_areas = [
        '"brand" "contact" "main" "trust" "legal" "bottom"',
        '"contact" "brand" "main" "trust" "legal" "bottom"',
        '"brand" "main" "trust" "contact" "legal" "bottom"',
        '"brand" "main" "contact" "trust" "legal" "bottom"',
        '"contact" "main" "trust" "legal" "brand" "bottom"',
    ][(number - 1) % 5]
    mobile_align = "center" if number % 7 in {0, 3} else "start"

    return f'''
.public-footer.site-footer{{
  --footer-bg:linear-gradient(135deg,var(--ink),var(--deep-sage));
  --footer-fg:#fff;
  --footer-panel:rgba(255,255,255,.08);
  --footer-line:rgba(255,255,255,.18);
  --footer-accent:var(--bronze);
  --footer-radius:8px;
  --footer-bg-solid:var(--ink);
  position:relative;
  isolation:isolate;
  overflow:hidden;
  display:block;
  margin-top:clamp(34px,5vw,72px);
  padding:0!important;
  background:var(--footer-bg);
  color:var(--footer-fg);
  border-top:1px solid var(--footer-line);
}}
.public-footer::before,
.public-footer::after{{
  content:"";
  position:absolute;
  z-index:-1;
  pointer-events:none;
}}
.public-footer-shell{{
  position:relative;
  z-index:1;
  margin:auto;
  display:grid;
  align-items:start;
}}
.footer-brand-panel{{grid-area:brand}}
.footer-main-links{{grid-area:main}}
.footer-trust-links{{grid-area:trust}}
.footer-legal-links{{grid-area:legal}}
.footer-contact{{grid-area:contact}}
.footer-bottom-row{{grid-area:bottom}}
.footer-brand-panel,
.footer-link-group,
.footer-contact{{
  display:grid;
  align-content:start;
  gap:8px;
}}
.public-footer img{{
  margin:0;
  filter:none;
}}
.public-footer .footer-link-group{{
  grid-template-columns:1fr;
}}
.public-footer .public-brand-mark{{
  display:inline-flex;
  justify-self:start;
  text-decoration:none;
}}
.public-footer .public-brand-mark img{{
  width:min(220px,72vw);
  max-height:78px;
  object-fit:contain;
}}
.public-footer .footer-monogram{{
  width:clamp(44px,5vw,78px);
  max-width:92px;
  max-height:92px;
  opacity:.66;
  margin:2px 0;
}}
.public-footer h3{{
  margin:0 0 8px;
  color:inherit;
  font-family:Inter,ui-sans-serif,system-ui,sans-serif;
  font-size:clamp(.78rem,.76vw,.9rem);
  line-height:1.2;
  font-weight:900;
  letter-spacing:.1em;
  text-transform:uppercase;
}}
.footer-brand-panel h2{{
  margin:0;
  color:inherit;
  font-size:clamp(1.45rem,2.3vw,2.8rem);
  line-height:1.04;
  letter-spacing:0;
}}
.footer-role,
.footer-credential{{
  font-weight:850;
  color:color-mix(in srgb,var(--footer-fg) 82%,var(--footer-accent));
}}
.public-footer p{{
  max-width:30ch;
  margin:0;
  color:color-mix(in srgb,var(--footer-fg) 74%,transparent);
  font-size:clamp(.92rem,.86vw,1rem);
  line-height:1.55;
}}
.footer-link-group a,
.footer-contact a,
.footer-contact span{{
  min-height:32px;
  display:flex;
  align-items:center;
  color:color-mix(in srgb,var(--footer-fg) 80%,transparent);
  font-size:clamp(.92rem,.86vw,1.01rem);
  line-height:1.34;
  text-decoration:none;
}}
.footer-legal-links a{{
  font-size:clamp(.88rem,.8vw,.96rem);
}}
.footer-contact{{
  font-style:normal;
  color:var(--footer-fg);
}}
.footer-contact a,
.footer-contact span{{
  color:color-mix(in srgb,currentColor 86%,transparent);
}}
.footer-link-group a:hover,
.footer-contact a:hover{{
  color:var(--footer-fg);
}}
.footer-contact a:hover{{
  color:inherit;
}}
.public-footer a:focus-visible{{
  outline:2px solid var(--footer-accent);
  outline-offset:4px;
  border-radius:4px;
}}
.footer-cta{{
  justify-self:start;
  min-height:40px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  margin-top:6px;
  padding:9px 14px;
  border:1px solid color-mix(in srgb,var(--footer-accent) 48%,var(--footer-line));
  border-radius:999px;
  background:color-mix(in srgb,var(--footer-accent) 16%,transparent);
  color:var(--footer-fg)!important;
  text-decoration:none;
  font-size:.94rem;
  font-weight:850;
}}
.footer-bottom-row{{
  display:flex;
  gap:14px 24px;
  flex-wrap:wrap;
  padding-top:18px;
  border-top:1px solid var(--footer-line);
}}
.footer-bottom-row p{{
  max-width:78ch;
  font-size:clamp(.84rem,.78vw,.92rem);
  line-height:1.45;
}}
.public-footer-{code}{{
  --footer-bg:{tone["bg"]};
  --footer-fg:{tone["fg"]};
  --footer-panel:{tone["panel"]};
  --footer-line:{tone["line"]};
  --footer-accent:{tone["accent"]};
  --footer-radius:{radius}px;
  --footer-bg-solid:{"var(--ink)" if tone["dark"] else "var(--soft-white)"};
  background:{tone["bg"]};
  color:{tone["fg"]};
  border-top:{footer_top};
}}
.public-footer-{code}::before{{{accent_before}}}
.public-footer-{code}::after{{{accent_after}}}
.public-footer-{code} .public-footer-shell{{
  width:{shell["width"]};
  grid-template-columns:{shell["grid"]};
  grid-template-areas:{shell["areas"]};
  gap:clamp({gap}px,3vw,{gap + 18}px);
  padding:clamp({top_pad}px,5vw,{top_pad + 22}px) 0 clamp({bottom_pad}px,5vw,{bottom_pad + 24}px);
  background:{shell_bg};
  border:{shell_border};
  border-radius:{radius}px;
  box-shadow:{shell_shadow};
}}
.public-footer-{code} .footer-brand-panel{{{brand}}}
.public-footer-{code} .footer-contact{{{contact}}}
.public-footer-{code} .footer-link-group{{{group}}}
.public-footer-{code} .public-brand-mark img{{width:min({logo_width}px,72vw)}}
.public-footer-{code} .footer-monogram{{width:clamp(44px,5vw,{mono_size}px)}}
.public-footer-{code} .footer-bottom-row{{{bottom_style}}}
@media(max-width:980px){{
  .public-footer-{code} .public-footer-shell{{
    width:min(760px,calc(100% - 28px));
    grid-template-columns:1fr 1fr;
    grid-template-areas:{tablet_areas};
    gap:20px;
    padding:32px 0 42px;
  }}
  .public-footer-{code} .footer-contact{{transform:none;border-radius:var(--footer-radius)}}
}}
@media(max-width:620px){{
  .public-footer-{code}{{
    margin-top:34px;
  }}
  .public-footer-{code} .public-footer-shell{{
    width:min(520px,calc(100% - 28px));
    grid-template-columns:1fr;
    grid-template-areas:{mobile_areas};
    gap:16px;
    padding:28px 0 34px;
  }}
  .public-footer-{code} .footer-brand-panel,
  .public-footer-{code} .footer-link-group,
  .public-footer-{code} .footer-contact{{
    justify-items:{mobile_align};
    text-align:{mobile_align};
  }}
  .public-footer-{code} .public-brand-mark,
  .public-footer-{code} .footer-cta{{
    justify-self:{mobile_align};
  }}
  .public-footer-{code} .footer-link-group a,
  .public-footer-{code} .footer-contact a,
  .public-footer-{code} .footer-contact span{{
    min-height:38px;
  }}
  .public-footer-{code} .footer-bottom-row{{
    display:grid;
    text-align:{mobile_align};
  }}
  .public-footer-{code}::before,
  .public-footer-{code}::after{{
    display:none;
  }}
  .public-footer-{code} .footer-brand-panel,
  .public-footer-{code} .footer-contact{{
    padding:14px!important;
    gap:6px;
    min-height:0;
  }}
  .public-footer-{code} .footer-link-group{{
    grid-template-columns:repeat(2,minmax(0,1fr));
    gap:4px 14px;
    padding:12px!important;
    min-height:0;
  }}
  .public-footer-{code} .footer-link-group h3{{
    grid-column:1/-1;
    margin-bottom:2px;
  }}
  .public-footer-{code} .public-brand-mark img{{
    width:min(168px,62vw);
    max-height:56px;
  }}
  .public-footer-{code} .footer-monogram{{
    display:none;
  }}
  .public-footer-{code} .footer-brand-panel h2{{
    font-size:clamp(1.28rem,7vw,1.85rem);
  }}
  .public-footer-{code} p{{
    font-size:.88rem;
    line-height:1.4;
  }}
  .public-footer-{code} .footer-cta{{
    min-height:36px;
    padding:7px 12px;
    font-size:.88rem;
  }}
  .public-footer-{code} .footer-link-group a{{
    min-height:30px;
    font-size:.88rem;
  }}
  .public-footer-{code} .footer-contact a,
  .public-footer-{code} .footer-contact span{{
    min-height:32px;
    font-size:.9rem;
  }}
  .public-footer-{code} .footer-bottom-row{{
    padding-top:12px;
  }}
}}
'''


# Footer v2: intentionally concept-specific visual systems.
FOOTER_V2_PALETTES = [
    {"bg": "linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--deep-sage) 72%,var(--ink)))", "fg": "#fff", "panel": "rgba(255,255,255,.085)", "card": "rgba(255,255,255,.12)", "line": "rgba(253,227,176,.28)", "accent": "var(--bronze)", "cta_bg": "color-mix(in srgb,var(--bronze) 32%,transparent)", "cta_fg": "#fff", "dark": True},
    {"bg": "linear-gradient(90deg,var(--soft-white),color-mix(in srgb,var(--sage) 14%,white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.76)", "card": "#fff", "line": "color-mix(in srgb,var(--sage) 30%,var(--line))", "accent": "var(--sage)", "cta_bg": "var(--ink)", "cta_fg": "#fff", "dark": False},
    {"bg": "linear-gradient(180deg,var(--cream),var(--soft-white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.82)", "card": "color-mix(in srgb,var(--champagne) 18%,white)", "line": "color-mix(in srgb,var(--bronze) 34%,var(--line))", "accent": "var(--bronze)", "cta_bg": "color-mix(in srgb,var(--bronze) 24%,white)", "cta_fg": "var(--ink)", "dark": False},
    {"bg": "linear-gradient(135deg,#242624,color-mix(in srgb,var(--deep-sage) 44%,#242624))", "fg": "#fff", "panel": "rgba(255,255,255,.07)", "card": "rgba(255,255,255,.11)", "line": "rgba(255,255,255,.17)", "accent": "color-mix(in srgb,var(--bronze) 84%,white)", "cta_bg": "#fff", "cta_fg": "var(--ink)", "dark": True},
    {"bg": "linear-gradient(90deg,color-mix(in srgb,var(--deep-sage) 88%,var(--ink)) 0 36%,var(--soft-white) 36% 100%)", "fg": "var(--ink)", "panel": "rgba(255,255,255,.82)", "card": "#fff", "line": "color-mix(in srgb,var(--sage) 30%,var(--line))", "accent": "var(--bronze)", "cta_bg": "var(--deep-sage)", "cta_fg": "#fff", "dark": False},
    {"bg": "linear-gradient(180deg,#fff,color-mix(in srgb,var(--sage) 7%,white))", "fg": "var(--ink)", "panel": "#fff", "card": "color-mix(in srgb,var(--sage) 10%,white)", "line": "color-mix(in srgb,var(--ink) 12%,var(--line))", "accent": "var(--sage)", "cta_bg": "var(--ink)", "cta_fg": "#fff", "dark": False},
    {"bg": "color-mix(in srgb,var(--sage) 21%,var(--soft-white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.68)", "card": "rgba(255,255,255,.82)", "line": "color-mix(in srgb,var(--sage) 34%,var(--line))", "accent": "color-mix(in srgb,var(--sage) 72%,var(--bronze))", "cta_bg": "color-mix(in srgb,var(--sage) 62%,var(--ink))", "cta_fg": "#fff", "dark": False},
    {"bg": "linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--bronze) 22%,var(--deep-sage)))", "fg": "#fff", "panel": "rgba(255,255,255,.08)", "card": "rgba(255,255,255,.13)", "line": "rgba(218,178,111,.34)", "accent": "var(--bronze)", "cta_bg": "color-mix(in srgb,var(--bronze) 42%,transparent)", "cta_fg": "#fff", "dark": True},
    {"bg": "linear-gradient(135deg,var(--cream),color-mix(in srgb,var(--champagne) 34%,white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.74)", "card": "#fff", "line": "color-mix(in srgb,var(--bronze) 28%,var(--line))", "accent": "var(--bronze)", "cta_bg": "var(--ink)", "cta_fg": "#fff", "dark": False},
    {"bg": "color-mix(in srgb,var(--deep-sage) 86%,var(--ink))", "fg": "#fff", "panel": "rgba(255,255,255,.09)", "card": "rgba(255,255,255,.12)", "line": "rgba(255,255,255,.18)", "accent": "color-mix(in srgb,var(--bronze) 82%,white)", "cta_bg": "#fff", "cta_fg": "var(--ink)", "dark": True},
    {"bg": "#fbfbf8", "fg": "var(--ink)", "panel": "color-mix(in srgb,var(--sage) 9%,white)", "card": "#fff", "line": "color-mix(in srgb,var(--ink) 10%,var(--line))", "accent": "var(--sage)", "cta_bg": "var(--deep-sage)", "cta_fg": "#fff", "dark": False},
    {"bg": "linear-gradient(120deg,color-mix(in srgb,var(--champagne) 20%,white),var(--soft-white) 58%,color-mix(in srgb,var(--sage) 14%,white))", "fg": "var(--ink)", "panel": "rgba(255,255,255,.78)", "card": "#fff", "line": "color-mix(in srgb,var(--bronze) 28%,var(--line))", "accent": "var(--bronze)", "cta_bg": "color-mix(in srgb,var(--bronze) 22%,var(--ink))", "cta_fg": "#fff", "dark": False},
    {"bg": "linear-gradient(180deg,var(--ink),#1f2320)", "fg": "#fff", "panel": "rgba(255,255,255,.065)", "card": "rgba(255,255,255,.105)", "line": "rgba(255,255,255,.14)", "accent": "var(--bronze)", "cta_bg": "rgba(255,255,255,.12)", "cta_fg": "#fff", "dark": True},
    {"bg": "linear-gradient(90deg,var(--soft-white) 0 62%,color-mix(in srgb,var(--sage) 22%,white) 62% 100%)", "fg": "var(--ink)", "panel": "rgba(255,255,255,.84)", "card": "#fff", "line": "color-mix(in srgb,var(--sage) 30%,var(--line))", "accent": "var(--sage)", "cta_bg": "var(--ink)", "cta_fg": "#fff", "dark": False},
    {"bg": "linear-gradient(135deg,color-mix(in srgb,var(--deep-sage) 70%,#fff),color-mix(in srgb,var(--ink) 80%,var(--deep-sage)))", "fg": "#fff", "panel": "rgba(255,255,255,.1)", "card": "rgba(255,255,255,.14)", "line": "rgba(255,255,255,.2)", "accent": "color-mix(in srgb,var(--bronze) 76%,white)", "cta_bg": "#fff", "cta_fg": "var(--ink)", "dark": True},
]


def area_template(*rows: str) -> str:
    return " ".join(f'"{row}"' for row in rows)


def footer_area_plan(number: int) -> dict[str, str]:
    mode = (number - 1) % 10
    fixed_areas = area_template("brand main trust legal contact", "bottom bottom bottom bottom bottom")
    widths = [
        "minmax(250px,1.3fr) minmax(130px,.74fr) minmax(160px,.88fr) minmax(136px,.72fr) minmax(230px,1.06fr)",
        "minmax(265px,1.2fr) minmax(140px,.8fr) minmax(166px,.9fr) minmax(132px,.68fr) minmax(250px,1.14fr)",
        "minmax(280px,1.38fr) minmax(130px,.7fr) minmax(170px,.86fr) minmax(132px,.66fr) minmax(230px,1fr)",
        "minmax(245px,1.08fr) minmax(150px,.82fr) minmax(178px,.92fr) minmax(138px,.7fr) minmax(255px,1.18fr)",
        "minmax(270px,1.28fr) minmax(136px,.72fr) minmax(168px,.84fr) minmax(136px,.68fr) minmax(240px,1.08fr)",
        "minmax(255px,1.16fr) minmax(144px,.78fr) minmax(176px,.94fr) minmax(136px,.72fr) minmax(236px,1.04fr)",
        "minmax(240px,1.08fr) minmax(150px,.86fr) minmax(184px,1fr) minmax(136px,.7fr) minmax(230px,1fr)",
        "minmax(275px,1.42fr) minmax(128px,.66fr) minmax(166px,.82fr) minmax(134px,.64fr) minmax(248px,1.12fr)",
        "minmax(250px,1.18fr) minmax(148px,.82fr) minmax(180px,.98fr) minmax(138px,.72fr) minmax(245px,1.12fr)",
        "minmax(260px,1.26fr) minmax(136px,.74fr) minmax(172px,.9fr) minmax(140px,.76fr) minmax(232px,1.02fr)",
    ]
    widths_by_mode = widths[mode]
    if mode == 0:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "var(--page)"}
    if mode == 1:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "min(1180px,calc(100% - 34px))"}
    if mode == 2:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "min(1140px,calc(100% - 32px))"}
    if mode == 3:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "var(--page)"}
    if mode == 4:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "min(1220px,calc(100% - 34px))"}
    if mode == 5:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "min(1160px,calc(100% - 36px))"}
    if mode == 6:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "min(1220px,calc(100% - 34px))"}
    if mode == 7:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "min(1240px,calc(100% - 32px))"}
    if mode == 8:
        return {"columns": widths_by_mode, "areas": fixed_areas, "width": "min(1280px,calc(100% - 36px))"}
    return {"columns": widths_by_mode, "areas": fixed_areas, "width": "var(--page)"}


def footer_tone(number: int) -> dict[str, object]:
    return FOOTER_V2_PALETTES[(number - 1) % len(FOOTER_V2_PALETTES)]


def footer_css(number: int, code: str) -> str:
    palette = footer_tone(number)
    plan = footer_area_plan(number)
    mode = (number - 1) % 10
    surface = (number * 7 + number // 4) % 10
    brand_index = (number * 3 + number // 8) % 10
    contact_index = (number * 5 + number // 7 + 3) % 10
    group_index = (number * 7 + number // 6) % 10
    accent_index = (number * 11 + number // 5) % 10
    overlay_x = 12 + ((number * 17) % 76)
    overlay_y = 16 + ((number * 23) % 68)
    overlay_strength = 7 + ((number * 5) % 12)
    overlay_stop = 34 + ((number * 3) % 20)
    footer_bg = (
        f"radial-gradient(circle at {overlay_x}% {overlay_y}%,"
        f"color-mix(in srgb,var(--footer-accent) {overlay_strength}%,transparent),"
        f"transparent {overlay_stop}%),{palette['bg']}"
    )
    radius = [0, 4, 8, 14, 22, 30, 6, 18, 2, 26][surface]
    outer_pad = [24, 26, 24, 28, 24, 22, 26, 24, 26, 24][surface]
    inner_pad = [14, 16, 16, 14, 16, 14, 14, 16, 14, 14][surface]
    gap = [12, 14, 12, 16, 14, 12, 12, 14, 16, 12][surface]
    logo_width = 186 + ((number * 17) % 82)
    monogram_size = 46 + ((number * 11) % 48)
    shell_bg = [
        "transparent",
        "linear-gradient(135deg,var(--footer-card),transparent)",
        "var(--footer-panel)",
        "color-mix(in srgb,var(--footer-card) 82%,transparent)",
        "linear-gradient(90deg,var(--footer-panel),transparent 72%)",
        "transparent",
        "var(--footer-card)",
        "linear-gradient(180deg,var(--footer-panel),transparent)",
        "color-mix(in srgb,var(--footer-panel) 72%,transparent)",
        "transparent",
    ][surface]
    shell_border = [
        "1px solid var(--footer-line)",
        "0",
        "1px solid var(--footer-line)",
        "1px solid color-mix(in srgb,var(--footer-line) 72%,transparent)",
        "0",
        "1px solid var(--footer-line)",
        "0",
        "1px solid var(--footer-line)",
        "1px solid color-mix(in srgb,var(--footer-accent) 38%,var(--footer-line))",
        "0",
    ][surface]
    shell_shadow = [
        "none",
        "0 18px 54px rgba(37,35,33,.08)",
        "inset 0 1px 0 color-mix(in srgb,var(--footer-fg) 9%,transparent)",
        "0 24px 70px rgba(37,35,33,.1)",
        "none",
        "0 14px 44px rgba(37,35,33,.07)",
        "0 22px 60px rgba(37,35,33,.1)",
        "none",
        "0 18px 54px rgba(37,35,33,.085)",
        "inset 0 -1px 0 var(--footer-line)",
    ][surface]
    brand_styles = [
        "padding:18px;border:1px solid var(--footer-line);background:var(--footer-card);",
        "padding-left:18px;border-left:3px solid var(--footer-accent);",
        "justify-items:center;text-align:center;padding:12px 18px;border-bottom:1px solid var(--footer-line);",
        "padding:18px 20px;background:var(--footer-card);border-radius:var(--footer-radius);",
        "padding:16px;border:1px solid var(--footer-line);box-shadow:inset 0 0 0 6px color-mix(in srgb,var(--footer-panel) 68%,transparent);",
        "padding:0 0 0 20px;border-left:1px solid var(--footer-line);",
        "justify-items:center;text-align:center;padding:16px;border:1px solid var(--footer-line);border-radius:999px;",
        "padding:18px;background:linear-gradient(180deg,var(--footer-card),transparent);border-top:3px double var(--footer-line);",
        "padding:18px;border-radius:0 var(--footer-radius) 0 var(--footer-radius);background:var(--footer-panel);",
        "padding:16px 18px;border-top:1px solid var(--footer-line);border-bottom:1px solid var(--footer-line);",
    ][brand_index]
    contact_styles = [
        "padding:18px;background:var(--footer-card);border:1px solid var(--footer-line);",
        "padding:18px;background:var(--footer-fg);--footer-contact-fg:var(--footer-invert);color:var(--footer-contact-fg);box-shadow:0 18px 44px rgba(37,35,33,.12);",
        "padding:18px;border-left:3px solid var(--footer-accent);background:color-mix(in srgb,var(--footer-accent) 11%,var(--footer-card));",
        "padding:18px;border:1px solid var(--footer-line);border-radius:999px;",
        "padding:18px;background:linear-gradient(135deg,var(--footer-card),transparent);border-top:1px solid var(--footer-line);",
        "padding:16px;border:1px solid var(--footer-line);background:transparent;",
        "padding:18px;background:var(--footer-card);border-radius:var(--footer-radius) 0 var(--footer-radius) 0;",
        "padding:18px;background:color-mix(in srgb,var(--footer-accent) 14%,var(--footer-card));border-bottom:3px solid var(--footer-accent);",
        "padding:18px;background:var(--footer-fg);--footer-contact-fg:var(--footer-invert);color:var(--footer-contact-fg);border-radius:var(--footer-radius);",
        "padding:16px 18px;border:1px solid var(--footer-line);background:var(--footer-panel);",
    ][contact_index]
    group_styles = [
        "padding-top:10px;border-top:1px solid var(--footer-line);",
        "padding-left:14px;border-left:1px solid var(--footer-line);",
        "padding:14px;background:var(--footer-panel);border:1px solid color-mix(in srgb,var(--footer-line) 70%,transparent);",
        "padding-bottom:10px;border-bottom:1px solid var(--footer-line);",
        "padding:12px;background:color-mix(in srgb,var(--footer-card) 64%,transparent);",
        "padding-top:12px;box-shadow:inset 0 1px 0 var(--footer-line);",
        "padding:12px 0;border-top:1px solid var(--footer-line);border-bottom:1px solid var(--footer-line);",
        "padding:12px;border-radius:var(--footer-radius);background:var(--footer-panel);",
        "padding-left:16px;border-left:3px double var(--footer-line);",
        "padding:10px 12px;border:1px solid var(--footer-line);",
    ][group_index]
    accents = [
        ("inset:0 0 auto 0;height:3px;background:linear-gradient(90deg,transparent,var(--footer-accent),transparent);", "display:none;"),
        ("left:clamp(18px,4vw,70px);top:20px;width:1px;height:calc(100% - 40px);background:linear-gradient(180deg,transparent,var(--footer-line),transparent);", "display:none;"),
        ("right:clamp(20px,5vw,84px);top:18px;width:76px;height:18px;background:url(\"../assets/botanical/gold-leaf-divider.svg\") center/contain no-repeat;opacity:.42;", "display:none;"),
        ("right:clamp(24px,7vw,120px);bottom:clamp(18px,4vw,46px);width:min(118px,20vw);aspect-ratio:1;background:url(\"../assets/brand/sofiati-monogram-bronze.png\") center/contain no-repeat;opacity:.09;", "display:none;"),
        ("inset:0;background:linear-gradient(90deg,var(--footer-line) 1px,transparent 1px) 0 0/90px 90px;opacity:.13;", "display:none;"),
        ("left:50%;top:18px;width:min(420px,42vw);height:1px;background:linear-gradient(90deg,transparent,var(--footer-accent),transparent);transform:translateX(-50%);", "right:50%;bottom:18px;width:74px;height:1px;background:var(--footer-accent);transform:translateX(50%);opacity:.68;"),
        ("left:0;top:0;width:min(24vw,280px);height:100%;background:linear-gradient(90deg,color-mix(in srgb,var(--footer-accent) 13%,transparent),transparent);", "display:none;"),
        ("right:0;top:0;width:min(32vw,390px);height:100%;background:radial-gradient(circle at 55% 40%,color-mix(in srgb,var(--footer-accent) 16%,transparent),transparent 62%);", "display:none;"),
        ("left:clamp(18px,5vw,90px);right:clamp(18px,5vw,90px);top:16px;height:1px;background:linear-gradient(90deg,var(--footer-accent),transparent,var(--footer-accent));opacity:.54;", "display:none;"),
        ("right:clamp(24px,6vw,96px);top:24px;width:48px;height:48px;border:1px solid var(--footer-line);border-radius:999px;", "right:calc(clamp(24px,6vw,96px) + 14px);top:38px;width:20px;height:20px;background:var(--footer-accent);border-radius:999px;opacity:.24;"),
    ]
    accent_before, accent_after = accents[accent_index]
    tablet_areas = area_template("brand brand", "main trust", "legal contact", "bottom bottom")
    mobile_areas = area_template("brand", "main", "trust", "legal", "contact", "bottom")
    mobile_align = "start"
    nav_cols = 3
    legal_cols = 3

    return f'''
.site-footer.public-footer-{code}{{
  --footer-bg:{footer_bg};
  --footer-fg:{palette["fg"]};
  --footer-panel:{palette["panel"]};
  --footer-card:{palette["card"]};
  --footer-line:{palette["line"]};
  --footer-accent:{palette["accent"]};
  --footer-cta-bg:{palette["cta_bg"]};
  --footer-cta-fg:{palette["cta_fg"]};
  --footer-invert:{"var(--ink)" if palette["dark"] else "#fff"};
  --footer-contact-fg:{palette["fg"]};
  --footer-radius:{radius}px;
  position:relative;
  isolation:isolate;
  overflow:hidden;
  display:block!important;
  grid-template-columns:none!important;
  gap:0!important;
  width:100%!important;
  margin-top:clamp(26px,4vw,58px);
  padding:0!important;
  background:var(--footer-bg);
  color:{palette["fg"]};
  border-top:{["1px solid var(--footer-line)","3px solid color-mix(in srgb,var(--footer-accent) 58%,transparent)","0","1px double var(--footer-line)"][surface % 4]};
}}
.public-footer-{code}::before,
.public-footer-{code}::after{{
  content:"";
  position:absolute;
  z-index:-1;
  pointer-events:none;
}}
.public-footer-{code}::before{{{accent_before}}}
.public-footer-{code}::after{{{accent_after}}}
.public-footer-{code} .public-footer-shell{{
  position:relative;
  z-index:1;
  width:{plan["width"]};
  margin:auto;
  display:grid!important;
  grid-template-columns:{plan["columns"]};
  grid-template-areas:{plan["areas"]};
  gap:clamp({gap}px,2vw,{gap + 12}px);
  align-items:start;
  align-content:start;
  padding:clamp({outer_pad}px,4vw,{outer_pad + 18}px) {inner_pad}px clamp({outer_pad - 2}px,4vw,{outer_pad + 16}px);
  background:{shell_bg};
  border:{shell_border};
  border-radius:{radius}px;
  box-shadow:{shell_shadow};
}}
.public-footer-{code} img{{margin:0!important;filter:none!important}}
.public-footer-{code} .footer-brand-panel{{grid-area:brand;{brand_styles}}}
.public-footer-{code} .footer-main-links{{grid-area:main;{group_styles}}}
.public-footer-{code} .footer-trust-links{{grid-area:trust;{group_styles}}}
.public-footer-{code} .footer-legal-links{{grid-area:legal;{group_styles}}}
.public-footer-{code} .footer-contact{{grid-area:contact;{contact_styles}}}
.public-footer-{code} .footer-bottom-row{{grid-area:bottom}}
.public-footer-{code} .footer-brand-panel,
.public-footer-{code} .footer-link-group,
.public-footer-{code} .footer-contact{{
  display:grid!important;
  align-content:start;
  gap:7px;
  min-width:0;
}}
.public-footer-{code} .public-brand-mark{{
  display:inline-flex;
  justify-self:start;
  text-decoration:none;
}}
.public-footer-{code} .public-brand-mark img{{
  width:min({logo_width}px,72vw)!important;
  max-height:70px;
  object-fit:contain;
}}
.public-footer-{code} .footer-monogram{{
  width:clamp(38px,4vw,{monogram_size}px)!important;
  max-width:84px;
  max-height:84px;
  opacity:.74;
}}
.public-footer-{code} h3{{
  margin:0 0 6px;
  color:inherit;
  font-family:Inter,ui-sans-serif,system-ui,sans-serif;
  font-size:clamp(.82rem,.78vw,.96rem);
  line-height:1.2;
  font-weight:900;
  letter-spacing:.1em;
  text-transform:uppercase;
}}
.public-footer-{code} .footer-brand-panel h2{{
  margin:0;
  color:inherit;
  font-size:clamp(1.38rem,2.2vw,2.55rem);
  line-height:1.04;
  letter-spacing:0;
}}
.public-footer-{code} .footer-role,
.public-footer-{code} .footer-credential{{
  font-weight:850;
  color:color-mix(in srgb,currentColor 80%,var(--footer-accent));
}}
.public-footer-{code} p{{
  max-width:30ch;
  margin:0;
  color:color-mix(in srgb,currentColor 76%,transparent);
  font-size:clamp(.94rem,.86vw,1.02rem);
  line-height:1.48;
}}
.public-footer-{code} .footer-link-group{{
  grid-template-columns:1fr!important;
}}
.public-footer-{code} .footer-main-links,
.public-footer-{code} .footer-trust-links{{
  grid-template-columns:1fr!important;
  column-gap:0;
}}
.public-footer-{code} .footer-legal-links{{
  grid-template-columns:1fr!important;
  column-gap:0;
}}
.public-footer-{code} .footer-link-group h3{{
  grid-column:1/-1;
}}
.public-footer-{code} .footer-link-group a,
.public-footer-{code} .footer-contact a,
.public-footer-{code} .footer-contact span{{
  min-height:31px;
  display:flex;
  align-items:center;
  color:color-mix(in srgb,currentColor 84%,transparent);
  font-size:clamp(.94rem,.86vw,1.03rem);
  line-height:1.3;
  text-decoration:none;
}}
.public-footer-{code} .footer-link-group a,
.public-footer-{code} .footer-contact a{{
  position:relative;
  width:fit-content;
  max-width:100%;
  transition:color .18s ease,transform .18s ease,opacity .18s ease;
}}
.public-footer-{code} .footer-link-group a::after,
.public-footer-{code} .footer-contact a::after{{
  content:"";
  position:absolute;
  left:0;
  right:0;
  bottom:2px;
  height:1px;
  background:var(--footer-accent);
  transform:scaleX(0);
  transform-origin:left;
  transition:transform .2s ease;
}}
.public-footer-{code} .footer-legal-links a{{
  font-size:clamp(.9rem,.8vw,.97rem);
}}
.public-footer-{code} .footer-contact{{
  font-style:normal;
  color:var(--footer-contact-fg);
}}
.public-footer-{code} .footer-contact h3{{
  color:var(--footer-contact-fg);
  opacity:1;
}}
.public-footer-{code} .footer-contact a,
.public-footer-{code} .footer-contact span{{
  color:var(--footer-contact-fg);
  font-weight:720;
  opacity:1;
}}
.public-footer-{code} .footer-contact a[href*="wa.me"]{{
  font-weight:900;
  color:var(--footer-contact-fg)!important;
}}
.public-footer-{code} a:hover{{
  color:inherit;
  transform:translateX(2px);
}}
.public-footer-{code} .footer-link-group a:hover::after,
.public-footer-{code} .footer-contact a:hover::after{{
  transform:scaleX(1);
}}
.public-footer-{code} a:focus-visible{{
  outline:2px solid var(--footer-accent);
  outline-offset:4px;
  border-radius:4px;
}}
.public-footer-{code} .footer-cta{{
  justify-self:start;
  min-height:38px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  margin-top:5px;
  padding:8px 13px;
  border:1px solid color-mix(in srgb,var(--footer-accent) 44%,var(--footer-line));
  border-radius:999px;
  background:var(--footer-cta-bg);
  color:var(--footer-cta-fg)!important;
  text-decoration:none;
  font-size:.92rem;
  font-weight:850;
  transition:transform .18s ease,box-shadow .18s ease,background-color .18s ease;
}}
.public-footer-{code} .footer-cta:hover{{
  transform:translateY(-2px);
  box-shadow:0 8px 20px color-mix(in srgb,var(--footer-accent) 16%,transparent);
}}
.public-footer-{code} .footer-bottom-row{{
  display:grid;
  justify-items:center;
  gap:6px;
  padding-top:16px;
  border-top:1px solid var(--footer-line);
  text-align:center;
}}
.public-footer-{code} .footer-bottom-row p{{
  max-width:80ch;
  font-size:clamp(.84rem,.78vw,.92rem);
  line-height:1.42;
}}
@media(max-width:980px){{
  .public-footer-{code} .public-footer-shell{{
    width:min(760px,calc(100% - 28px));
    grid-template-columns:1fr 1fr;
    grid-template-areas:{tablet_areas};
    gap:16px;
    padding:28px 14px 34px;
  }}
  .public-footer-{code} .footer-contact{{
    transform:none!important;
    border-radius:var(--footer-radius);
  }}
}}
@media(max-width:620px){{
  .site-footer.public-footer-{code}{{
    margin-top:28px;
  }}
  .public-footer-{code}::before,
  .public-footer-{code}::after{{
    display:none;
  }}
  .public-footer-{code} .public-footer-shell{{
    width:min(520px,calc(100% - 24px));
    grid-template-columns:1fr;
    grid-template-areas:{mobile_areas};
    gap:12px;
    padding:24px 12px 28px;
    border-radius:var(--footer-radius);
  }}
  .public-footer-{code} .footer-brand-panel,
  .public-footer-{code} .footer-link-group,
  .public-footer-{code} .footer-contact{{
    justify-items:{mobile_align};
    text-align:{mobile_align};
    padding:12px!important;
    gap:5px;
    min-height:0;
  }}
  .public-footer-{code} .footer-link-group{{
    background:transparent!important;
    border-left:0!important;
    border-right:0!important;
    border-bottom:0!important;
    border-top:1px solid var(--footer-line)!important;
    box-shadow:none!important;
    border-radius:0!important;
  }}
  .public-footer-{code} .public-brand-mark,
  .public-footer-{code} .footer-cta{{
    justify-self:{mobile_align};
  }}
  .public-footer-{code} .public-brand-mark img{{
    width:min(166px,62vw)!important;
    max-height:54px;
  }}
  .public-footer-{code} .footer-monogram{{
    display:none;
  }}
  .public-footer-{code} .footer-brand-panel h2{{
    font-size:clamp(1.26rem,7vw,1.78rem);
  }}
  .public-footer-{code} p{{
    font-size:.88rem;
    line-height:1.38;
  }}
  .public-footer-{code} .footer-main-links,
  .public-footer-{code} .footer-trust-links{{
    grid-template-columns:repeat({nav_cols},minmax(0,1fr))!important;
    gap:3px 12px;
  }}
  .public-footer-{code} .footer-legal-links{{
    grid-template-columns:repeat({legal_cols},minmax(0,1fr))!important;
    gap:3px 12px;
  }}
  .public-footer-{code} .footer-link-group h3{{
    grid-column:1/-1;
    margin-bottom:2px;
  }}
  .public-footer-{code} .footer-link-group a{{
    min-height:30px;
    font-size:.9rem;
  }}
  .public-footer-{code} .footer-contact a,
  .public-footer-{code} .footer-contact span{{
    min-height:32px;
    font-size:.92rem;
  }}
  .public-footer-{code} .footer-cta{{
    min-height:36px;
    padding:7px 12px;
    font-size:.88rem;
  }}
  .public-footer-{code} .footer-bottom-row{{
    padding-top:12px;
  }}
}}
'''


def public_css(number: int, code: str) -> str:
    header_layout = HEADER_LAYOUTS[number - 1]
    menu_layout = MENU_LAYOUTS[number - 1]
    footer_layout = FOOTER_LAYOUTS[number - 1]
    colors = color_plan(number)
    radius = [0, 3, 6, 10, 18, 28, 999][number % 7]
    logo_width = 144 + (number % 8) * 10
    utility_mix = 5 + (number % 8) * 3
    header_offset = (number % 5) * 2
    footer_stamp_x = 8 + (number % 7) * 11
    footer_stamp_y = 10 + (number % 5) * 12
    is_dark_header = dark_header(number, header_layout)
    header_widths = [
        "var(--page)",
        "min(1180px,calc(100% - 30px))",
        "min(1040px,calc(100% - 44px))",
        "100%",
        "min(1280px,calc(100% - 24px))",
        "min(980px,calc(100% - 48px))",
        "min(1160px,calc(100% - 58px))",
        "calc(100% - 56px)",
        "min(1220px,calc(100% - 36px))",
        "min(900px,calc(100% - 38px))",
    ]
    header_bgs = [
        "color-mix(in srgb,var(--soft-white) 92%,white)",
        "linear-gradient(90deg,rgba(255,255,255,.96),color-mix(in srgb,var(--sage) 16%,var(--soft-white)))",
        "color-mix(in srgb,var(--cream) 86%,white)",
        "linear-gradient(135deg,color-mix(in srgb,var(--deep-sage) 82%,var(--ink)),var(--ink))",
        "rgba(248,247,242,.74)",
        "linear-gradient(90deg,color-mix(in srgb,var(--champagne) 20%,white),var(--soft-white))",
        "linear-gradient(135deg,color-mix(in srgb,var(--sage) 22%,white),rgba(255,255,255,.86))",
        "color-mix(in srgb,var(--soft-white) 72%,var(--sage))",
        "linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--deep-sage) 70%,var(--ink)))",
        "rgba(255,255,255,.82)",
    ]
    header_bg = header_bgs[(number - 1) % len(header_bgs)]
    header_width = header_widths[(number - 1) % len(header_widths)]
    header_fg = "white" if is_dark_header else "var(--ink)"
    header_link = "rgba(255,255,255,.84)" if is_dark_header else "color-mix(in srgb,var(--ink) 88%,var(--muted))"
    header_active_bg = "rgba(255,255,255,.12)" if is_dark_header else "rgba(255,255,255,.78)"
    header_cta_bg = "white" if is_dark_header else "var(--ink)"
    header_cta_fg = "var(--ink)" if is_dark_header else "white"
    header_button_bg = "rgba(255,255,255,.08)" if is_dark_header else "white"
    header_button_fg = "white" if is_dark_header else "var(--ink)"
    utility_fg = "white" if is_dark_header else "var(--ink)"
    utility_bg = (
        "linear-gradient(90deg,var(--ink),color-mix(in srgb,var(--deep-sage) 76%,var(--ink)))"
        if is_dark_header
        else f"color-mix(in srgb,var(--soft-white) calc(100% - {utility_mix}%),var(--sage))"
    )
    shell_padding_y = 8 + (number % 4) * 2
    shell_padding_x = 14 + (number % 6) * 4
    deco_positions = [
        ("auto", "14px", "14px", "auto", "86px", "1px", "linear-gradient(90deg,var(--bronze),transparent)"),
        ("50%", "auto", "auto", "18px", "1px", "42px", "color-mix(in srgb,var(--sage) 42%,transparent)"),
        ("12px", "auto", "auto", "14px", "58px", "58px", "url(\"../assets/botanical/gold-leaf-divider.svg\") center/contain no-repeat"),
        ("auto", "8%", "-22px", "auto", "160px", "80px", "radial-gradient(circle,rgba(253,227,176,.28),transparent 64%)"),
        ("8px", "8px", "auto", "auto", "74px", "74px", "url(\"../assets/brand/sofiati-monogram-bronze.png\") center/contain no-repeat"),
    ]
    deco_top, deco_right, deco_bottom, deco_left, deco_width, deco_height, deco_bg = deco_positions[number % len(deco_positions)]
    return f'''
{CSS_START}
.public-utility.status-banner{{
  min-height:30px;
  display:grid;
  grid-template-columns:minmax(0,1fr) auto auto;
  align-items:center;
  gap:clamp(10px,2vw,24px);
  padding:4px max(16px,calc((100vw - 1160px)/2));
  border:0;
  border-bottom:1px solid color-mix(in srgb,var(--bronze) 18%,var(--line));
  background:{utility_bg};
  color:{utility_fg};
  font-size:.68rem;
  letter-spacing:.08em;
  text-transform:uppercase;
  z-index:45;
}}
.public-utility-rule{{height:1px;background:linear-gradient(90deg,transparent,color-mix(in srgb,var(--bronze) 60%,var(--sage)),transparent)}}
.public-utility-mark{{font-family:Georgia,"Times New Roman",serif;letter-spacing:.16em;color:color-mix(in srgb,var(--ink) 70%,var(--bronze))}}
.public-utility-dot .public-utility-mark::before,
.public-utility-leaf .public-utility-mark::before{{content:"";display:inline-block;width:6px;height:6px;margin-right:9px;border-radius:999px;background:var(--bronze);vertical-align:middle}}
.public-utility-leaf .public-utility-mark::before{{width:14px;height:7px;border-radius:999px 0 999px 0;background:color-mix(in srgb,var(--sage) 72%,var(--bronze))}}
.public-language{{display:inline-flex;align-items:center;gap:2px;border:1px solid color-mix(in srgb,var(--bronze) 26%,var(--line));border-radius:999px;padding:2px;background:rgba(255,255,255,.52);color:inherit}}
.public-language button{{min-height:26px;border:0;border-radius:999px;background:transparent;color:inherit;padding:3px 8px;font-size:.62rem;font-weight:800;letter-spacing:.08em;cursor:pointer}}
.public-language button[aria-pressed="true"]{{background:var(--ink);color:white}}
.public-header.site-header{{
  position:sticky;
  top:0;
  z-index:44;
  display:block;
  width:100%;
  margin:0;
  padding:0;
  border:0;
  background:transparent;
  color:var(--ink);
  backdrop-filter:none;
}}
.public-header-shell{{
  position:relative;
  overflow:hidden;
  width:var(--page);
  min-height:70px;
  margin:clamp(8px,1.4vw,18px) auto 0;
  display:grid;
  grid-template-columns:auto minmax(0,1fr) auto;
  align-items:center;
  gap:clamp(12px,2.2vw,34px);
  padding:10px clamp(14px,2vw,26px);
  border:1px solid color-mix(in srgb,var(--bronze) 18%,var(--line));
  border-radius:{radius}px;
  background:color-mix(in srgb,var(--soft-white) 90%,white);
  box-shadow:0 18px 54px rgba(37,35,33,.08);
  backdrop-filter:blur(18px);
}}
.public-header-shell>*{{position:relative;z-index:1}}
.public-header .public-brand-mark{{display:flex;align-items:center;justify-content:center;justify-self:start;text-decoration:none;min-width:max-content}}
.public-header .public-brand-mark img{{width:clamp(132px,{logo_width / 10:.1f}vw,{logo_width}px);max-height:62px;object-fit:contain}}
.public-header .desktop-nav{{display:flex;align-items:center;justify-content:center;gap:clamp(6px,1vw,15px);flex-wrap:wrap}}
.public-header .desktop-nav a{{min-height:36px;display:inline-flex;align-items:center;padding:7px 9px;border-radius:max(2px,calc({radius}px / 2));color:color-mix(in srgb,var(--ink) 88%,var(--muted));font-size:.74rem;line-height:1;text-decoration:none;letter-spacing:.02em;transition:background .2s ease,color .2s ease,box-shadow .2s ease,transform .2s ease}}
.public-header .desktop-nav a:hover,
.public-header .desktop-nav a:focus-visible,
.public-header .desktop-nav a[aria-current="page"]{{background:rgba(255,255,255,.74);color:var(--ink);box-shadow:inset 0 -1px 0 color-mix(in srgb,var(--bronze) 58%,transparent);outline:none}}
.public-header-tools{{display:flex;align-items:center;justify-content:flex-end;gap:8px;min-width:max-content}}
.header-consultation{{min-height:38px;display:inline-flex;align-items:center;justify-content:center;border:1px solid color-mix(in srgb,var(--bronze) 32%,var(--line));border-radius:max(3px,calc({radius}px / 2 + 3px));background:var(--ink);color:white;padding:8px 13px;text-decoration:none;font-size:.76rem;font-weight:800}}
.public-menu-button{{display:none;min-height:40px;align-items:center;justify-content:center;border:1px solid color-mix(in srgb,var(--bronze) 30%,var(--line));border-radius:999px;background:white;color:var(--ink);padding:8px 14px;font-weight:800;cursor:pointer}}
.public-secondary-bar{{display:none;width:var(--page);margin:0 auto clamp(4px,1vw,10px);padding:7px clamp(12px,2vw,24px);border:1px solid color-mix(in srgb,var(--bronze) 14%,var(--line));border-top:0;border-radius:0 0 max(4px,{radius}px) max(4px,{radius}px);background:rgba(248,247,242,.72);backdrop-filter:blur(16px)}}
body.page-care .public-secondary-bar:not(.public-secondary-none),
body.page-laser .public-secondary-bar:not(.public-secondary-none),
body.page-skin .public-secondary-bar:not(.public-secondary-none),
body.page-results .public-secondary-bar:not(.public-secondary-none),
body.page-consultation .public-secondary-bar:not(.public-secondary-none){{display:block}}
.public-secondary-bar .desktop-nav{{justify-content:center}}
.public-secondary-bar .desktop-nav a{{font-size:.68rem;letter-spacing:.08em;text-transform:uppercase;min-height:28px;padding:5px 8px}}
.public-header-layout-split .public-header-shell,
.public-header-layout-balanced .public-header-shell{{grid-template-columns:minmax(0,1fr) auto minmax(0,1fr) auto;border-radius:0 0 30px 30px;border-top:0}}
.public-header-layout-split .public-brand-mark,
.public-header-layout-balanced .public-brand-mark{{justify-self:center}}
.public-header-layout-capsule .public-header-shell,
.public-header-layout-luminous .public-header-shell,
.public-header-layout-calm .public-header-shell{{width:min(1180px,calc(100% - 30px));border-radius:999px;padding-left:clamp(18px,3vw,40px);padding-right:clamp(18px,3vw,40px)}}
.public-header-layout-clinical .public-header-shell,
.public-header-layout-grid .public-header-shell,
.public-header-layout-precision .public-header-shell,
.public-header-layout-meridian .public-header-shell{{background:linear-gradient(90deg,rgba(255,255,255,.96),color-mix(in srgb,var(--sage) 12%,var(--soft-white)));border-style:solid;box-shadow:inset 0 -1px 0 color-mix(in srgb,var(--sage) 20%,transparent),0 16px 42px rgba(37,35,33,.06)}}
.public-header-layout-transparent .public-header-shell,
.public-header-layout-aura .public-header-shell,
.public-header-layout-glass .public-header-shell{{background:rgba(248,247,242,.68);backdrop-filter:blur(24px);box-shadow:0 18px 60px rgba(37,35,33,.075)}}
.public-header-layout-stacked .public-header-shell,
.public-header-layout-ritual .public-header-shell,
.public-header-layout-noble .public-header-shell,
.public-header-layout-signature .public-header-shell,
.public-header-layout-sovereign .public-header-shell,
.public-header-layout-atelier .public-header-shell{{grid-template-columns:1fr;justify-items:center;gap:9px}}
.public-header-brand-row{{display:flex;justify-content:center}}
.public-header-nav-row{{width:100%;display:grid;grid-template-columns:1fr auto;align-items:center;gap:16px}}
.public-header-nav-row .public-nav-zone{{justify-self:center}}
.public-header-layout-minimal .public-header-shell,
.public-header-layout-pure .public-header-shell,
.public-header-layout-proof .public-header-shell,
.public-header-layout-safeguard .public-header-shell{{box-shadow:none;border-left:0;border-right:0;border-radius:0;width:100%;margin:0;padding-left:max(18px,calc((100vw - 1240px)/2));padding-right:max(18px,calc((100vw - 1240px)/2))}}
.public-header-layout-menu-only .public-header-shell{{grid-template-columns:auto minmax(0,1fr) auto;width:min(980px,calc(100% - 36px));border-radius:28px;background:color-mix(in srgb,var(--soft-white) 94%,white)}}
.public-header-layout-menu-only .public-menu-button{{display:inline-flex}}
.public-header-layout-menu-only .public-menu-only-line{{height:1px;background:linear-gradient(90deg,var(--bronze),transparent)}}
.public-header-layout-botanical .public-header-shell,
.public-header-layout-flora .public-header-shell,
.public-header-layout-verdant .public-header-shell,
.public-header-layout-origin .public-header-shell{{box-shadow:inset 0 0 0 6px color-mix(in srgb,var(--sage) 10%,transparent),0 18px 48px rgba(37,35,33,.08)}}
.public-header-layout-halo .public-header-shell{{grid-template-columns:1fr auto;border-radius:42px 4px 42px 4px}}
.public-halo-shell{{display:grid;justify-items:center;gap:8px}}
.public-header-layout-wide .public-header-shell,
.public-header-layout-vista .public-header-shell{{width:100%;margin:0;border-left:0;border-right:0;border-radius:0;box-shadow:none;padding-left:max(18px,calc((100vw - 1320px)/2));padding-right:max(18px,calc((100vw - 1320px)/2))}}
.public-header-{code} .public-header-shell{{
  width:{header_width};
  min-height:{66 + (number % 5) * 4}px;
  padding:{shell_padding_y}px clamp({shell_padding_x}px,{1.5 + (number % 4) * .3:.1f}vw,{shell_padding_x + 18}px);
  color:{header_fg};
  background:{header_bg};
  border-color:color-mix(in srgb,var(--bronze) {18 + (number % 5) * 5}%,var(--line));
  border-radius:{[0, 4, 12, 22, 36, 999, 18, 2, 28, 44][(number - 1) % 10]}px;
  box-shadow:0 {10 + (number % 6) * 4}px {34 + (number % 7) * 7}px rgba(37,35,33,{0.055 + (number % 5) * 0.012:.3f});
}}
.public-header-{code} .public-header-shell::after{{
  content:"";
  position:absolute;
  top:{deco_top};
  right:{deco_right};
  bottom:{deco_bottom};
  left:{deco_left};
  width:{deco_width};
  height:{deco_height};
  background:{deco_bg};
  opacity:{0.10 + (number % 4) * 0.045:.3f};
  pointer-events:none;
}}
.public-header-{code} .desktop-nav a{{color:{header_link}}}
.public-header-{code} .desktop-nav a:hover,
.public-header-{code} .desktop-nav a:focus-visible,
.public-header-{code} .desktop-nav a[aria-current="page"]{{background:{header_active_bg};color:{header_fg}}}
.public-header-{code} .header-consultation{{background:{header_cta_bg};color:{header_cta_fg};border-color:color-mix(in srgb,currentColor 26%,transparent)}}
.public-header-{code} .public-menu-button{{background:{header_button_bg};color:{header_button_fg};border-color:color-mix(in srgb,currentColor 30%,transparent)}}
.public-header-{code}.public-header-layout-dynamic .public-header-shell,
.public-header-{code}.public-header-layout-evolve .public-header-shell{{border-bottom-width:4px}}
.public-header-{code}.public-header-layout-sculptural .public-brand-mark,
.public-header-{code}.public-header-layout-form .public-brand-mark{{padding:8px 12px;border:1px solid color-mix(in srgb,currentColor 18%,transparent);background:rgba(255,255,255,.14);box-shadow:0 10px 28px rgba(37,35,33,.06)}}
.public-header-{code}.public-header-layout-softline .public-header-shell{{border-radius:36px 6px 36px 6px}}
.public-header-{code}.public-header-layout-silhouette .public-header-shell,
.public-header-{code}.public-header-layout-origin .public-header-shell,
.public-header-{code}.public-header-layout-wisdom .public-header-shell{{border-radius:2px 34px 2px 34px}}
@media(min-width:981px){{
  .public-header-{code} .public-header-shell{{transform:translateY({header_offset}px)}}
  .public-header-{code}.public-header-layout-{header_layout} .public-brand-mark img{{filter:drop-shadow(0 8px 18px rgba(37,35,33,{0.04 + (number % 4) * 0.015:.3f}))}}
}}
.public-mobile-menu.mobile-menu{{
  position:fixed;
  inset:0;
  z-index:80;
  min-height:100vh;
  display:grid;
  grid-template-rows:auto 1fr auto;
  gap:clamp(22px,5vw,48px);
  padding:clamp(18px,5vw,44px);
  overflow:auto;
  color:white;
  background:linear-gradient(135deg,rgba(37,35,33,.74),rgba(52,64,57,.64)),url("../assets/backgrounds/mobile-menu-background.svg") right bottom/360px 360px no-repeat,var(--deep-sage);
  transform:translate3d(0,-104%,0);
  opacity:0;
  pointer-events:none;
  transition:transform .42s cubic-bezier(.22,.61,.36,1),opacity .32s ease,clip-path .42s ease;
}}
.public-mobile-menu.is-open{{transform:none;opacity:1;pointer-events:auto}}
.public-mobile-menu-top{{position:relative;z-index:2;display:grid;grid-template-columns:auto auto auto;align-items:center;justify-content:space-between;gap:12px}}
.public-mobile-menu .public-brand-mark img{{width:min(190px,52vw);max-height:66px;object-fit:contain}}
.public-mobile-menu .public-language{{justify-self:center;border-color:rgba(255,255,255,.28);background:rgba(255,255,255,.12);color:white}}
.public-mobile-menu .public-language button[aria-pressed="true"]{{background:white;color:var(--ink)}}
.public-menu-close{{min-height:40px;border:1px solid rgba(255,255,255,.36);border-radius:999px;padding:8px 14px;background:transparent;color:inherit;font-weight:800;cursor:pointer}}
.public-mobile-primary{{position:relative;z-index:2;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:clamp(8px,2vw,16px);align-content:center;max-width:980px;margin:auto 0}}
.public-mobile-primary a{{min-height:56px;display:flex;align-items:center;border-bottom:1px solid rgba(255,255,255,.17);color:inherit;font-family:Georgia,"Times New Roman",serif;font-size:clamp(1.6rem,5.8vw,3.4rem);line-height:1;text-decoration:none}}
.public-mobile-cta{{position:relative;z-index:2;justify-self:start;align-self:end;min-height:46px;display:inline-flex;align-items:center;justify-content:center;border:1px solid currentColor;border-radius:999px;padding:11px 18px;color:inherit;text-decoration:none;font-weight:800}}
.public-menu-layout-bottom-sheet,
.public-menu-layout-calm-cream,
.public-menu-layout-pure-ivory,
.public-menu-layout-serene-ivory,
.public-menu-layout-paper-menu{{inset:auto 0 0 0;min-height:min(82vh,760px);transform:translate3d(0,104%,0);border-radius:28px 28px 0 0;background:linear-gradient(180deg,var(--soft-white),color-mix(in srgb,var(--sage) 18%,white));color:var(--ink)}}
.public-menu-layout-bottom-sheet .public-language,
.public-menu-layout-calm-cream .public-language,
.public-menu-layout-pure-ivory .public-language,
.public-menu-layout-serene-ivory .public-language,
.public-menu-layout-paper-menu .public-language{{color:var(--ink);background:white;border-color:var(--line)}}
.public-menu-layout-bottom-sheet .public-menu-close,
.public-menu-layout-calm-cream .public-menu-close,
.public-menu-layout-pure-ivory .public-menu-close,
.public-menu-layout-serene-ivory .public-menu-close,
.public-menu-layout-paper-menu .public-menu-close{{border-color:var(--line)}}
.public-menu-layout-clinical-drawer,
.public-menu-layout-precise-drawer,
.public-menu-layout-signal-drawer,
.public-menu-layout-meridian-drawer,
.public-menu-layout-secure-clean{{inset:0 auto 0 0;width:min(540px,100%);transform:translate3d(-104%,0,0);background:linear-gradient(90deg,rgba(37,35,33,.86),rgba(52,64,57,.72)),url("../assets/textures/clinical-paper-texture.svg") center/260px 260px,var(--ink)}}
.public-menu-layout-botanical-fade,
.public-menu-layout-botanical-panel,
.public-menu-layout-floral-full,
.public-menu-layout-deep-botanical{{background:radial-gradient(circle at 82% 28%,rgba(253,227,176,.18),transparent 24%),linear-gradient(135deg,var(--deep-sage),color-mix(in srgb,var(--sage) 32%,var(--ink)))}}
.public-menu-layout-two-column .public-mobile-primary,
.public-menu-layout-clinical-grid .public-mobile-primary{{grid-template-columns:repeat(2,minmax(0,1fr));border-top:1px solid rgba(255,255,255,.16);border-left:1px solid rgba(255,255,255,.16);gap:0}}
.public-menu-layout-two-column .public-mobile-primary a,
.public-menu-layout-clinical-grid .public-mobile-primary a{{border-right:1px solid rgba(255,255,255,.16);padding:14px}}
.public-menu-layout-radial,
.public-menu-layout-geometric-layer,
.public-menu-layout-shape-panels{{clip-path:circle(0 at 90% 10%)}}
.public-menu-layout-radial.is-open,
.public-menu-layout-geometric-layer.is-open,
.public-menu-layout-shape-panels.is-open{{clip-path:circle(150% at 90% 10%)}}
.public-menu-layout-dark-elegant,
.public-menu-layout-premium-brand,
.public-menu-layout-signature-full{{background:linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--bronze) 22%,var(--deep-sage)))}}
body.public-menu-locked{{overflow:hidden}}
.public-accessibility{{opacity:.22}}
.public-accessibility:hover,
.public-accessibility:focus-within{{opacity:1}}
.public-accessibility button{{width:38px;height:38px;display:inline-flex;align-items:center;justify-content:center;border-radius:999px}}
{footer_css(number, code).strip()}
@media(max-width:980px){{
  .public-utility.status-banner{{display:none}}
  .public-header.site-header{{background:rgba(248,247,242,.94);border-bottom:1px solid var(--line)}}
  .public-header-shell,
  .public-header-layout-split .public-header-shell,
  .public-header-layout-balanced .public-header-shell,
  .public-header-layout-stacked .public-header-shell,
  .public-header-layout-ritual .public-header-shell,
  .public-header-layout-noble .public-header-shell,
  .public-header-layout-sovereign .public-header-shell,
  .public-header-layout-atelier .public-header-shell{{width:100%;min-height:66px;margin:0;grid-template-columns:auto 1fr auto;grid-template-areas:none;border:0;border-radius:0;box-shadow:none;background:transparent;padding:9px 14px;transform:none!important}}
  .public-header-brand-row,
  .public-header-nav-row{{display:contents}}
  .public-header .public-brand-mark{{grid-column:1;justify-self:start}}
  .public-header .public-brand-mark img{{width:clamp(128px,38vw,174px);max-height:54px}}
  .public-header .public-nav-zone,
  .public-secondary-bar,
  .header-consultation,
  .public-menu-only-line{{display:none!important}}
  .public-header-tools{{grid-column:3;justify-self:end}}
  .public-menu-button{{display:inline-flex}}
}}
@media(max-width:620px){{
  .public-mobile-menu.mobile-menu{{padding:18px}}
  .public-mobile-menu-top{{grid-template-columns:1fr auto;align-items:start}}
  .public-mobile-menu .public-language{{grid-column:1/-1;justify-self:start}}
  .public-mobile-primary{{grid-template-columns:1fr}}
  .public-mobile-primary a{{min-height:50px;font-size:clamp(1.55rem,8vw,2.45rem)}}
}}
@media(prefers-reduced-motion:reduce){{
  .public-header .desktop-nav a,
  .public-mobile-menu.mobile-menu,
  .public-mobile-primary a{{transition:none!important}}
}}
{CSS_END}
'''


def public_js() -> str:
    return f'''
{JS_START}
(() => {{
  const enhancePublicMenu = () => {{
    const menu = document.querySelector("#mobile-menu");
    const openButton = document.querySelector("[data-menu-toggle]");
    const closeButton = document.querySelector("[data-menu-close]");
    if (!menu || !openButton || menu.dataset.enhancedPublicMenu === "true") return;
    menu.dataset.enhancedPublicMenu = "true";
    const focusableSelector = 'a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),textarea:not([disabled]),[tabindex]:not([tabindex="-1"])';
    let lastTrigger = null;
    const focusables = () => Array.from(menu.querySelectorAll(focusableSelector)).filter((item) => item.offsetParent !== null || item === closeButton);
    const setOpen = (active) => {{
      menu.classList.toggle("is-open", active);
      menu.setAttribute("aria-hidden", String(!active));
      openButton.setAttribute("aria-expanded", String(active));
      document.body.classList.toggle("public-menu-locked", active);
      if (active) {{
        lastTrigger = document.activeElement === openButton ? openButton : lastTrigger || openButton;
        window.setTimeout(() => (closeButton || focusables()[0] || menu).focus(), 40);
      }} else if (lastTrigger && typeof lastTrigger.focus === "function") {{
        window.setTimeout(() => lastTrigger.focus(), 20);
      }}
    }};
    openButton.addEventListener("click", () => setOpen(true));
    closeButton?.addEventListener("click", () => setOpen(false));
    menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => setOpen(false)));
    document.addEventListener("keydown", (event) => {{
      if (!menu.classList.contains("is-open")) return;
      if (event.key === "Escape") {{
        event.preventDefault();
        setOpen(false);
        return;
      }}
      if (event.key !== "Tab") return;
      const items = focusables();
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {{
        event.preventDefault();
        last.focus();
      }} else if (!event.shiftKey && document.activeElement === last) {{
        event.preventDefault();
        first.focus();
      }}
    }});
  }};
  const enhanceFloatingWidgets = () => {{
    const dock = document.querySelector("[data-floating-tools]");
    const topButton = document.querySelector("[data-back-to-top]");
    if (!dock || dock.dataset.enhancedFloatingWidgets === "true") return;
    dock.dataset.enhancedFloatingWidgets = "true";
    const footer = document.querySelector(".public-footer");
    const baseOffset = () => {{
      const mobile = window.matchMedia("(max-width: 620px)").matches;
      return mobile ? 12 : 20;
    }};
    const update = () => {{
      const scrolled = window.scrollY > 24;
      document.body.classList.toggle("public-page-scrolled", scrolled);
      if (topButton) {{
        topButton.classList.toggle("is-visible", scrolled);
        topButton.setAttribute("aria-hidden", String(!scrolled));
        topButton.setAttribute("tabindex", scrolled ? "0" : "-1");
      }}
      let bottom = baseOffset();
      if (footer) {{
        const rect = footer.getBoundingClientRect();
        if (rect.top < window.innerHeight - bottom) {{
          const dockHeight = dock.getBoundingClientRect().height || 128;
          const lifted = window.innerHeight - rect.top + bottom + 12;
          const maxLift = Math.max(bottom, window.innerHeight - dockHeight - 14);
          bottom = Math.min(lifted, maxLift);
        }}
      }}
      dock.style.setProperty("--floating-bottom", `${{Math.max(bottom, baseOffset())}}px`);
    }};
    topButton?.addEventListener("click", () => window.scrollTo({{ top: 0, behavior: "smooth" }}));
    requestAnimationFrame(() => {{
      dock.classList.add("is-loaded");
      update();
    }});
    window.addEventListener("scroll", update, {{ passive: true }});
    window.addEventListener("resize", update);
  }};
  const bootPublicLayer = () => {{
    enhancePublicMenu();
    enhanceFloatingWidgets();
  }};
  if (window.SofiatiPartialsReady) {{
    window.SofiatiPartialsReady.then(bootPublicLayer);
  }} else if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", bootPublicLayer, {{ once: true }});
  }} else {{
    bootPublicLayer();
  }}
}})();
{JS_END}
'''


# Footer/widget refresh overrides. These names intentionally shadow the older
# generators above so the refactor stays repeatable without touching the older
# audit history in this file.
FOOTER_REFRESH_PALETTES = [
    {"bg": "linear-gradient(135deg,#252321 0%,#3f4a43 64%,#2b2825 100%)", "fg": "#fffaf2", "muted": "rgba(255,250,242,.72)", "line": "rgba(253,227,176,.22)", "accent": "#d7b17d", "soft": "#e7b9c8", "button": "#fffaf2", "button_fg": "#252321", "arrow_bg": "#31473d", "arrow_fg": "#fff8eb", "wm": (215, 177, 125), "dark": True},
    {"bg": "linear-gradient(120deg,#fbfaf5 0%,#edf1e9 58%,#f8f4ea 100%)", "fg": "#252321", "muted": "rgba(37,35,33,.68)", "line": "rgba(121,138,128,.24)", "accent": "#798a80", "soft": "#e8b8c6", "button": "#252321", "button_fg": "#fffaf2", "arrow_bg": "#f8f4ea", "arrow_fg": "#56695f", "wm": (121, 138, 128), "dark": False},
    {"bg": "linear-gradient(180deg,#f8f4ea 0%,#fffdf7 56%,#f1eadb 100%)", "fg": "#28231e", "muted": "rgba(40,35,30,.68)", "line": "rgba(154,107,53,.24)", "accent": "#9a6b35", "soft": "#e4b9c5", "button": "#5c4631", "button_fg": "#fffaf2", "arrow_bg": "#fff8ee", "arrow_fg": "#8a653e", "wm": (154, 107, 53), "dark": False},
    {"bg": "linear-gradient(135deg,#202522 0%,#5f7466 100%)", "fg": "#f9f4e9", "muted": "rgba(249,244,233,.7)", "line": "rgba(255,255,255,.18)", "accent": "#c9d0bc", "soft": "#e9bacb", "button": "#f9f4e9", "button_fg": "#202522", "arrow_bg": "#23352f", "arrow_fg": "#f9f4e9", "wm": (201, 208, 188), "dark": True},
    {"bg": "linear-gradient(90deg,#344039 0 34%,#f8f7f2 34% 100%)", "fg": "#252321", "muted": "rgba(37,35,33,.7)", "line": "rgba(121,138,128,.28)", "accent": "#9a6b35", "soft": "#e5b6c7", "button": "#344039", "button_fg": "#fffaf2", "arrow_bg": "#edf1e9", "arrow_fg": "#344039", "wm": (154, 107, 53), "dark": False},
    {"bg": "linear-gradient(180deg,#ffffff 0%,#eef3ef 100%)", "fg": "#23211f", "muted": "rgba(35,33,31,.66)", "line": "rgba(37,35,33,.13)", "accent": "#a2ae9f", "soft": "#eac0cb", "button": "#23211f", "button_fg": "#ffffff", "arrow_bg": "#ffffff", "arrow_fg": "#6c7c73", "wm": (162, 174, 159), "dark": False},
    {"bg": "linear-gradient(135deg,#e8eee4 0%,#fbf7ef 54%,#dfe7dc 100%)", "fg": "#252321", "muted": "rgba(37,35,33,.68)", "line": "rgba(121,138,128,.25)", "accent": "#6f8277", "soft": "#e6b4c3", "button": "#6f8277", "button_fg": "#ffffff", "arrow_bg": "#f8f4ea", "arrow_fg": "#53645c", "wm": (111, 130, 119), "dark": False},
    {"bg": "linear-gradient(135deg,#24211f 0%,#74614a 48%,#3c4941 100%)", "fg": "#fff8ec", "muted": "rgba(255,248,236,.72)", "line": "rgba(215,177,125,.28)", "accent": "#dab26f", "soft": "#edbdcb", "button": "#dab26f", "button_fg": "#24211f", "arrow_bg": "#3c2f28", "arrow_fg": "#fff8ec", "wm": (218, 178, 111), "dark": True},
    {"bg": "linear-gradient(135deg,#f8f1e2 0%,#fffdf7 42%,#efe1bd 100%)", "fg": "#27231f", "muted": "rgba(39,35,31,.66)", "line": "rgba(154,107,53,.2)", "accent": "#b2864f", "soft": "#e9b7c7", "button": "#27231f", "button_fg": "#fffdf7", "arrow_bg": "#fff8ed", "arrow_fg": "#9a6b35", "wm": (178, 134, 79), "dark": False},
    {"bg": "linear-gradient(180deg,#2c3933 0%,#151817 100%)", "fg": "#fbf7ed", "muted": "rgba(251,247,237,.7)", "line": "rgba(255,255,255,.17)", "accent": "#bfcbb8", "soft": "#eab8c8", "button": "#fbf7ed", "button_fg": "#151817", "arrow_bg": "#1f2b27", "arrow_fg": "#fbf7ed", "wm": (191, 203, 184), "dark": True},
]


def refresh_palette(number: int) -> dict[str, object]:
    return FOOTER_REFRESH_PALETTES[(number - 1) % len(FOOTER_REFRESH_PALETTES)]


def accessibility_partial(number: int, code: str) -> str:
    return f'''<nav class="accessibility-tools public-accessibility public-accessibility-{code}" data-accessibility-tools aria-label="Accessibility shortcuts">
  <a class="skip-link" href="#main">Skip to content</a>
  <a class="accessibility-page-link" href="accessibility.html">Accessibility</a>
</nav>
'''


def footer_group(title: str, items: list[tuple[str, str]], class_name: str) -> str:
    return (
        f'<nav class="footer-link-group {class_name}" aria-label="{title}">\n'
        f"      <h3>{title}</h3>\n"
        f"{links(items)}\n"
        "    </nav>"
    )


def footer_partial(number: int, code: str) -> str:
    layout = FOOTER_LAYOUTS[number - 1]
    return f'''<footer class="site-footer public-footer public-footer-{code} public-footer-layout-{layout}" data-public-footer="{layout}">
  <div class="public-footer-shell">
    <section class="footer-brand-panel" aria-label="Brand identity">
      <h3>Brand</h3>
      <a class="brand-mark public-brand-mark footer-signature-mark" href="index.html" aria-label="Sofiati home">
        <img src="assets/brand/assinatura-1.jpg" alt="Franciele Sofiati signature logo" width="500" height="500">
      </a>
      <h2>Franciele Sofiati</h2>
      <p class="footer-role">Advanced Aesthetic Biomedicine</p>
      <p class="footer-credential">CRBM 6277</p>
      <p class="footer-slogan"><em>Take care of yourself with sophistication.</em></p>
      <div class="footer-actions" aria-label="Footer actions">
        <a class="footer-button footer-button-primary" href="consultation.html">Consultation</a>
        <a class="footer-button footer-button-secondary" href="care.html">Care</a>
        <a class="footer-button footer-button-tertiary" href="contact.html">Contact</a>
      </div>
    </section>
    {footer_group("Pages", PRIMARY, "footer-main-links")}
    {footer_group("Trust", FOOTER_TRUST, "footer-trust-links")}
    {footer_group("Legal", FOOTER_LEGAL, "footer-legal-links")}
    <address class="footer-contact" aria-label="Contact">
      <h3>Contact</h3>
      <a href="https://wa.me/5543991043536" rel="noopener" target="_blank">WhatsApp: (43) 9 9104-3536</a>
      <a href="mailto:sofiatimendonca@gmail.com">sofiatimendonca@gmail.com</a>
      <a href="https://www.instagram.com/fransofiati_biomedica/" rel="noopener" target="_blank">@fransofiati_biomedica</a>
      <span>Londrina, PR</span>
    </address>
    <div class="footer-bottom-row">
      <p>Information on this website is educational and does not replace an individual professional evaluation.</p>
      <p>© 2026 Franciele Sofiati. All rights reserved.</p>
    </div>
  </div>
</footer>
'''


def floating_whatsapp_partial(number: int, code: str) -> str:
    return f'''<a class="floating-whatsapp floating-whatsapp-{code}" href="https://wa.me/5543991043536" rel="noopener" target="_blank" aria-label="Contact on WhatsApp">
  <img src="assets/icons/whatsapp.svg" alt="" aria-hidden="true">
  <b>Contact on WhatsApp</b>
</a>
'''


def back_to_top_partial(number: int, code: str) -> str:
    return f'''<button class="back-to-top back-to-top-{code}" type="button" data-back-to-top aria-label="Back to top" aria-hidden="true" tabindex="-1">
  <img src="assets/icons/back-to-top.svg" alt="" aria-hidden="true">
</button>
'''


def widget_css(number: int, code: str) -> str:
    palette = refresh_palette(number)
    radius = [999, 18, 8, 26, 14, 30, 999, 4, 22, 12][(number - 1) % 10]
    size = 58 if number % 4 else 56
    gap = 10 + (number % 3)
    lift = 2 + (number % 4)
    return f'''
.floating-tools.floating-tools-{code}{{
  --widget-size:{size}px;
  --widget-gap:{gap}px;
  --widget-radius:{radius}px;
  --widget-frame:color-mix(in srgb,{palette["accent"]} 38%,rgba(255,255,255,.38));
  --widget-shadow:0 18px 42px rgba(37,35,33,.18);
  --widget-pink:{palette["soft"]};
  position:fixed!important;
  right:max(14px,calc(env(safe-area-inset-right) + 14px))!important;
  bottom:var(--floating-bottom,max(16px,calc(env(safe-area-inset-bottom) + 16px)))!important;
  z-index:76!important;
  display:grid!important;
  gap:var(--widget-gap)!important;
  justify-items:end!important;
  width:var(--widget-size)!important;
  pointer-events:none;
  transform:translate3d(0,10px,0);
  opacity:0;
  transition:opacity .45s ease,transform .45s cubic-bezier(.22,.61,.36,1),bottom .22s ease;
}}
.floating-tools-{code}.is-loaded{{
  opacity:1;
  transform:none;
}}
.floating-tools-{code} a,
.floating-tools-{code} button{{
  pointer-events:auto;
}}
.floating-tools-{code} .floating-whatsapp,
.floating-tools-{code} .back-to-top{{
  position:relative!important;
  width:var(--widget-size)!important;
  height:var(--widget-size)!important;
  min-width:var(--widget-size)!important;
  min-height:var(--widget-size)!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  padding:0!important;
  border:1px solid var(--widget-frame)!important;
  border-radius:var(--widget-radius)!important;
  text-decoration:none!important;
  box-shadow:var(--widget-shadow),0 0 0 7px color-mix(in srgb,var(--widget-pink) 14%,transparent),0 0 34px color-mix(in srgb,var(--widget-pink) 34%,transparent)!important;
  transform:translateZ(0);
  transition:transform .22s ease,box-shadow .22s ease,opacity .22s ease,filter .22s ease!important;
  overflow:visible!important;
}}
.floating-tools-{code} .floating-whatsapp{{
  background:radial-gradient(circle at 36% 30%,rgba(255,255,255,.3),transparent 34%),linear-gradient(145deg,#128c4a,#25d366 58%,#0f7d42)!important;
  animation:whatsapp-premium-glow-{code} {5.2 + (number % 5) * .18:.2f}s ease-in-out infinite;
}}
.floating-tools-{code} .floating-whatsapp::before,
.floating-tools-{code} .back-to-top::before{{
  content:"";
  position:absolute;
  inset:-5px;
  border-radius:inherit;
  border:1px solid color-mix(in srgb,var(--widget-pink) 42%,transparent);
  opacity:.58;
  pointer-events:none;
}}
.floating-tools-{code} .floating-whatsapp img,
.floating-tools-{code} .back-to-top img{{
  width:calc(var(--widget-size) * .56)!important;
  height:calc(var(--widget-size) * .56)!important;
  object-fit:contain!important;
  filter:none!important;
}}
.floating-tools-{code} .floating-whatsapp b{{
  position:absolute;
  right:calc(100% + 11px);
  bottom:6px;
  width:max-content;
  max-width:180px;
  padding:8px 10px;
  border:1px solid color-mix(in srgb,{palette["accent"]} 24%,rgba(37,35,33,.1));
  border-radius:999px;
  background:rgba(248,247,242,.96);
  color:#252321;
  box-shadow:0 14px 32px rgba(37,35,33,.14);
  font-size:.72rem;
  line-height:1.1;
  font-weight:850;
  white-space:nowrap;
  opacity:0;
  transform:translateX(7px);
  transition:opacity .2s ease,transform .2s ease;
  pointer-events:none;
}}
.floating-tools-{code} .floating-whatsapp:hover b,
.floating-tools-{code} .floating-whatsapp:focus-visible b{{
  opacity:1;
  transform:none;
}}
.floating-tools-{code} .back-to-top{{
  background:radial-gradient(circle at 38% 28%,rgba(255,255,255,.34),transparent 36%),{palette["arrow_bg"]}!important;
  color:{palette["arrow_fg"]}!important;
  opacity:0;
  visibility:hidden;
  transform:translate3d(0,12px,0) scale(.92);
}}
.floating-tools-{code} .back-to-top.is-visible{{
  opacity:1;
  visibility:visible;
  transform:none;
}}
.floating-tools-{code} .floating-whatsapp:hover,
.floating-tools-{code} .floating-whatsapp:focus-visible,
.floating-tools-{code} .back-to-top:hover,
.floating-tools-{code} .back-to-top:focus-visible{{
  transform:translateY(-{lift}px);
  box-shadow:0 22px 48px rgba(37,35,33,.2),0 0 0 8px color-mix(in srgb,var(--widget-pink) 20%,transparent),0 0 38px color-mix(in srgb,var(--widget-pink) 42%,transparent)!important;
  outline:0;
}}
.floating-tools-{code} .floating-whatsapp:focus-visible,
.floating-tools-{code} .back-to-top:focus-visible{{
  outline:2px solid color-mix(in srgb,{palette["accent"]} 72%,white);
  outline-offset:4px;
}}
@keyframes whatsapp-premium-glow-{code}{{
  0%,100%{{filter:saturate(1);box-shadow:var(--widget-shadow),0 0 0 6px color-mix(in srgb,var(--widget-pink) 13%,transparent),0 0 28px color-mix(in srgb,var(--widget-pink) 27%,transparent)!important;}}
  50%{{filter:saturate(1.04);box-shadow:var(--widget-shadow),0 0 0 8px color-mix(in srgb,var(--widget-pink) 18%,transparent),0 0 38px color-mix(in srgb,var(--widget-pink) 36%,transparent)!important;}}
}}
@media(max-width:620px){{
  .floating-tools.floating-tools-{code}{{
    --widget-size:54px;
    right:max(12px,calc(env(safe-area-inset-right) + 12px))!important;
    bottom:var(--floating-bottom,max(12px,calc(env(safe-area-inset-bottom) + 12px)))!important;
    gap:8px!important;
  }}
  .floating-tools-{code} .floating-whatsapp b{{display:none}}
  .cookie-banner{{
    left:12px!important;
    right:calc(84px + env(safe-area-inset-right))!important;
    bottom:max(12px,calc(env(safe-area-inset-bottom) + 12px))!important;
    max-width:none!important;
  }}
}}
@media(prefers-reduced-motion:reduce){{
  .floating-tools-{code},
  .floating-tools-{code} .floating-whatsapp,
  .floating-tools-{code} .back-to-top{{
    animation:none!important;
    transition:none!important;
  }}
}}
'''


def footer_css(number: int, code: str) -> str:
    palette = refresh_palette(number)
    shell_widths = [
        "min(1240px,calc(100% - 36px))",
        "min(1180px,calc(100% - 32px))",
        "var(--page)",
        "min(1280px,calc(100% - 40px))",
        "min(1160px,calc(100% - 34px))",
    ]
    gap = 22 + (number % 6) * 3
    top_pad = 44 + (number % 5) * 5
    bottom_pad = 40 + (number % 4) * 6
    signature_size = 104 + (number % 7) * 10
    watermark_width = 290 + (number % 8) * 22
    divider_alpha = 13 + (number % 5) * 3
    return f'''
.public-accessibility.accessibility-tools{{
  position:absolute!important;
  inset:0 auto auto 0!important;
  z-index:90!important;
  display:block!important;
  width:0!important;
  height:0!important;
  opacity:1!important;
  pointer-events:none!important;
}}
.public-accessibility button{{
  display:none!important;
}}
.public-accessibility a{{
  pointer-events:auto;
}}
.public-accessibility .skip-link,
.public-accessibility .accessibility-page-link{{
  position:fixed;
  left:14px;
  z-index:91;
  display:inline-flex;
  align-items:center;
  min-height:38px;
  padding:9px 12px;
  border-radius:999px;
  background:var(--ink);
  color:white;
  box-shadow:0 14px 34px rgba(37,35,33,.18);
  text-decoration:none;
  font-size:.86rem;
  font-weight:850;
  transform:translateY(-260%);
  transition:transform .2s ease;
}}
.public-accessibility .skip-link{{top:12px}}
.public-accessibility .accessibility-page-link{{top:58px}}
.public-accessibility .skip-link:focus,
.public-accessibility .accessibility-page-link:focus{{
  transform:none;
  outline:2px solid var(--bronze);
  outline-offset:3px;
}}
.site-footer.public-footer-{code}{{
  --footer-bg:{palette["bg"]};
  --footer-fg:{palette["fg"]};
  --footer-muted:{palette["muted"]};
  --footer-line:{palette["line"]};
  --footer-accent:{palette["accent"]};
  --footer-soft:{palette["soft"]};
  --footer-button:{palette["button"]};
  --footer-button-fg:{palette["button_fg"]};
  position:relative;
  isolation:isolate;
  overflow:hidden;
  display:block!important;
  width:100%!important;
  margin-top:clamp(34px,5vw,76px)!important;
  padding:0!important;
  background:var(--footer-bg)!important;
  color:var(--footer-fg)!important;
  border-top:1px solid var(--footer-line)!important;
}}
.public-footer-{code}::before,
.public-footer-{code}::after{{
  content:"";
  position:absolute;
  pointer-events:none;
  z-index:0;
}}
.public-footer-{code}::before{{
  inset:0;
  background:
    linear-gradient(90deg,transparent 0 10%,color-mix(in srgb,var(--footer-accent) {divider_alpha}%,transparent) 10% calc(10% + 1px),transparent calc(10% + 1px)),
    radial-gradient(circle at {18 + (number * 7) % 68}% {20 + (number * 11) % 60}%,color-mix(in srgb,var(--footer-soft) 18%,transparent),transparent 34%);
  opacity:.78;
}}
.public-footer-{code}::after{{
  right:clamp(18px,5vw,78px);
  bottom:clamp(12px,3vw,34px);
  width:min({watermark_width}px,42vw);
  aspect-ratio:1;
  background:url("../assets/brand/footer-signature-watermark.png") center/contain no-repeat;
  opacity:{0.075 + (number % 5) * 0.012:.3f};
  transform:rotate({-7 + (number % 8) * 2}deg);
  animation:footer-signature-breathe-{code} {9 + (number % 5)}s ease-in-out infinite;
}}
.public-footer-{code} .public-footer-shell{{
  position:relative;
  z-index:1;
  width:{shell_widths[(number - 1) % len(shell_widths)]};
  margin:auto;
  display:grid!important;
  grid-template-columns:minmax(230px,1.34fr) minmax(118px,.7fr) minmax(154px,.86fr) minmax(118px,.66fr) minmax(220px,1.05fr);
  grid-template-areas:"brand main trust legal contact" "bottom bottom bottom bottom bottom";
  gap:clamp({gap}px,3vw,{gap + 18}px);
  align-items:start;
  padding:clamp({top_pad}px,6vw,{top_pad + 30}px) 0 clamp({bottom_pad}px,5vw,{bottom_pad + 26}px);
  background:transparent!important;
  border:0!important;
  border-radius:0!important;
  box-shadow:none!important;
}}
.public-footer-{code} .footer-brand-panel{{grid-area:brand}}
.public-footer-{code} .footer-main-links{{grid-area:main}}
.public-footer-{code} .footer-trust-links{{grid-area:trust}}
.public-footer-{code} .footer-legal-links{{grid-area:legal}}
.public-footer-{code} .footer-contact{{grid-area:contact}}
.public-footer-{code} .footer-bottom-row{{grid-area:bottom}}
.public-footer-{code} .footer-brand-panel,
.public-footer-{code} .footer-link-group,
.public-footer-{code} .footer-contact{{
  display:grid!important;
  align-content:start;
  gap:8px;
  min-width:0;
  padding:0!important;
  background:transparent!important;
  border:0!important;
  border-radius:0!important;
  box-shadow:none!important;
  transform:none!important;
}}
.public-footer-{code} .footer-link-group,
.public-footer-{code} .footer-contact{{
  padding-left:clamp(14px,1.8vw,24px)!important;
  border-left:1px solid var(--footer-line)!important;
}}
.public-footer-{code} img{{
  margin:0!important;
  filter:none!important;
}}
.public-footer-{code} .footer-signature-mark{{
  justify-self:start;
  width:{signature_size}px;
  max-width:min({signature_size}px,42vw);
  aspect-ratio:1;
  display:block;
  overflow:hidden;
  border-radius:{[0, 6, 14, 999, 22][number % 5]}px;
  background:color-mix(in srgb,var(--footer-fg) 8%,transparent);
  mix-blend-mode:normal;
}}
.public-footer-{code} .footer-signature-mark img{{
  width:100%!important;
  height:100%!important;
  object-fit:cover!important;
}}
.public-footer-{code} h3{{
  margin:0 0 6px;
  color:color-mix(in srgb,var(--footer-fg) 82%,var(--footer-accent));
  font-family:Inter,ui-sans-serif,system-ui,sans-serif;
  font-size:clamp(.76rem,.72vw,.88rem);
  line-height:1.2;
  font-weight:900;
  letter-spacing:.14em;
  text-transform:uppercase;
}}
.public-footer-{code} .footer-brand-panel h2{{
  margin:0;
  color:var(--footer-fg);
  font-size:clamp(1.48rem,2.4vw,2.9rem);
  line-height:1.02;
  letter-spacing:0;
}}
.public-footer-{code} .footer-role,
.public-footer-{code} .footer-credential{{
  color:color-mix(in srgb,var(--footer-fg) 82%,var(--footer-accent));
  font-weight:820;
}}
.public-footer-{code} .footer-slogan{{
  max-width:24ch;
  color:var(--footer-muted);
  font-family:Georgia,"Times New Roman",serif;
  font-size:clamp(1rem,1.1vw,1.22rem);
  line-height:1.42;
}}
.public-footer-{code} .footer-actions{{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  margin-top:8px;
}}
.public-footer-{code} .footer-button{{
  min-height:38px;
  display:inline-flex;
  align-items:center;
  justify-content:center;
  padding:8px 13px;
  border-radius:{[999, 4, 12, 22, 2][(number - 1) % 5]}px;
  font-size:.88rem;
  font-weight:850;
  line-height:1;
  text-decoration:none;
  transition:transform .18s ease,box-shadow .18s ease,background-color .18s ease,color .18s ease;
}}
.public-footer-{code} .footer-button-primary{{
  background:var(--footer-button);
  color:var(--footer-button-fg)!important;
  border:1px solid var(--footer-button);
}}
.public-footer-{code} .footer-button-secondary{{
  background:color-mix(in srgb,var(--footer-accent) {10 + number % 15}%,transparent);
  color:var(--footer-fg)!important;
  border:1px solid color-mix(in srgb,var(--footer-accent) 46%,var(--footer-line));
}}
.public-footer-{code} .footer-button-tertiary{{
  background:transparent;
  color:var(--footer-fg)!important;
  border:1px solid transparent;
  box-shadow:inset 0 -1px 0 var(--footer-accent);
}}
.public-footer-{code} p{{
  margin:0;
  color:var(--footer-muted);
  font-size:clamp(.92rem,.86vw,1rem);
  line-height:1.5;
}}
.public-footer-{code} .footer-link-group{{
  grid-template-columns:1fr!important;
}}
.public-footer-{code} .footer-link-group a,
.public-footer-{code} .footer-contact a,
.public-footer-{code} .footer-contact span{{
  min-height:31px;
  display:flex;
  align-items:center;
  width:fit-content;
  max-width:100%;
  color:var(--footer-muted);
  font-size:clamp(.92rem,.84vw,1rem);
  line-height:1.25;
  text-decoration:none;
  font-style:normal;
  transition:color .18s ease,transform .18s ease;
}}
.public-footer-{code} .footer-contact{{
  font-style:normal;
}}
.public-footer-{code} .footer-contact a[href*="wa.me"]{{
  color:color-mix(in srgb,var(--footer-fg) 88%,var(--footer-accent));
  font-weight:860;
}}
.public-footer-{code} a:hover,
.public-footer-{code} a:focus-visible{{
  color:var(--footer-fg)!important;
}}
.public-footer-{code} .footer-link-group a:hover,
.public-footer-{code} .footer-contact a:hover{{
  transform:translateX(3px);
}}
.public-footer-{code} .footer-button:hover{{
  transform:translateY(-2px);
  box-shadow:0 12px 28px color-mix(in srgb,var(--footer-accent) 18%,transparent);
}}
.public-footer-{code} a:focus-visible{{
  outline:2px solid var(--footer-accent);
  outline-offset:4px;
  border-radius:4px;
}}
.public-footer-{code} .footer-bottom-row{{
  display:flex;
  flex-wrap:wrap;
  justify-content:space-between;
  gap:10px 22px;
  padding-top:clamp(18px,2.2vw,28px);
  border-top:1px solid var(--footer-line);
}}
.public-footer-{code} .footer-bottom-row p{{
  max-width:72ch;
  font-size:clamp(.82rem,.76vw,.9rem);
  line-height:1.42;
}}
@keyframes footer-signature-breathe-{code}{{
  0%,100%{{opacity:{0.07 + (number % 5) * 0.012:.3f};transform:translate3d(0,0,0) rotate({-7 + (number % 8) * 2}deg);}}
  50%{{opacity:{0.10 + (number % 5) * 0.014:.3f};transform:translate3d(0,-5px,0) rotate({-6 + (number % 8) * 2}deg);}}
}}
@media(max-width:980px){{
  .public-footer-{code} .public-footer-shell{{
    width:min(760px,calc(100% - 30px));
    grid-template-columns:1fr 1fr;
    grid-template-areas:"brand contact" "main trust" "legal legal" "bottom bottom";
    gap:24px 18px;
  }}
  .public-footer-{code} .footer-contact{{
    padding-left:0!important;
    border-left:0!important;
  }}
}}
@media(max-width:620px){{
  .site-footer.public-footer-{code}{{
    margin-top:34px!important;
  }}
  .public-footer-{code}::after{{
    width:min(260px,74vw);
    right:-18px;
    bottom:18px;
    opacity:.055;
  }}
  .public-footer-{code} .public-footer-shell{{
    width:min(520px,calc(100% - 28px));
    grid-template-columns:1fr;
    grid-template-areas:"brand" "main" "trust" "legal" "contact" "bottom";
    gap:18px;
    padding:34px 0 126px;
  }}
  .public-footer-{code} .footer-link-group,
  .public-footer-{code} .footer-contact{{
    padding-left:0!important;
    padding-top:14px!important;
    border-left:0!important;
    border-top:1px solid var(--footer-line)!important;
  }}
  .public-footer-{code} .footer-main-links,
  .public-footer-{code} .footer-trust-links,
  .public-footer-{code} .footer-legal-links{{
    grid-template-columns:repeat(2,minmax(0,1fr))!important;
    gap:3px 14px;
  }}
  .public-footer-{code} .footer-link-group h3{{
    grid-column:1/-1;
  }}
  .public-footer-{code} .footer-signature-mark{{
    width:min(118px,38vw);
  }}
  .public-footer-{code} .footer-bottom-row{{
    display:grid;
  }}
}}
@media(prefers-reduced-motion:reduce){{
  .public-footer-{code}::after{{
    animation:none!important;
  }}
}}
{widget_css(number, code).strip()}
'''


def footer_brand_source() -> Path:
    return ROOT / "brand identity" / "ASSINATURA 1.jpg"


def footer_watermark_source() -> Path:
    matches = sorted((ROOT / "brand identity").glob("VARIA*LOGOTIPO PRINCIPAL VERDE PNG.png"))
    if not matches:
        raise FileNotFoundError("Could not find footer watermark source in brand identity")
    return matches[0]


def write_footer_assets(concept: Path, number: int) -> None:
    from PIL import Image

    resampling = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
    brand_dir = concept / "assets" / "brand"
    brand_dir.mkdir(parents=True, exist_ok=True)

    signature_output = brand_dir / "assinatura-1.jpg"
    with Image.open(footer_brand_source()) as source:
        image = source.convert("RGB")
        image.thumbnail((430, 430), resampling)
        canvas = Image.new("RGB", (500, 500), (248, 247, 242))
        canvas.paste(image, ((500 - image.width) // 2, (500 - image.height) // 2))
        canvas.save(signature_output, quality=94, optimize=True)

    palette = refresh_palette(number)
    color = palette["wm"]
    watermark_output = brand_dir / "footer-signature-watermark.png"
    with Image.open(footer_watermark_source()) as source:
        image = source.convert("RGBA")
        alpha = image.getchannel("A")
        bbox = alpha.getbbox()
        if bbox:
            image = image.crop(bbox)
            alpha = alpha.crop(bbox)
        image.thumbnail((900, 900), resampling)
        alpha = image.getchannel("A").point(lambda value: int(value * 0.52))
        tinted = Image.new("RGBA", image.size, (*color, 0))
        tinted.putalpha(alpha)
        tinted.save(watermark_output)


def whatsapp_svg() -> str:
    return '''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240" viewBox="0 0 240 240" fill="none" role="img" aria-label="WhatsApp">
  <circle cx="120" cy="120" r="104" fill="#25D366"/>
  <circle cx="120" cy="120" r="88" fill="#18B85E"/>
  <path d="M72 174l9.8-35.7A60.8 60.8 0 1 1 103 159.8L72 174Z" fill="none" stroke="#FFFFFF" stroke-width="13" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M98.7 84.6c-4.2 2.5-8.2 8.6-7.5 14.2 2.7 22.6 24.2 44.8 47.7 50.5 5.6 1.4 12.1-2.4 14.9-6.4l4.4-6.3c1.7-2.4.8-5.8-1.9-7.1l-17.2-8.4c-2.2-1.1-4.9-.5-6.5 1.4l-5.4 6.5c-10.9-5.2-19.7-14.1-25.6-25.8l6.2-5.1c2-1.6 2.6-4.5 1.4-6.7l-8.3-15.4c-1.4-2.6-4.7-3.5-7.2-2l-5 3Z" fill="#FFFFFF"/>
</svg>
'''


def back_to_top_svg(number: int, code: str) -> str:
    palette = refresh_palette(number)
    bg = palette["arrow_bg"]
    fg = palette["arrow_fg"]
    accent = palette["accent"]
    radius = [118, 38, 22, 66, 12, 96, 44, 28, 82, 16][(number - 1) % 10]
    stroke = 8 + (number % 4)
    cap = "round" if number % 3 else "square"
    motifs = [
        f'<path d="M120 178V70M84 108l36-38 36 38" stroke="{fg}" stroke-width="{stroke}" stroke-linecap="{cap}" stroke-linejoin="round"/>',
        f'<path d="M76 132l44-48 44 48M120 88v86" stroke="{fg}" stroke-width="{stroke}" stroke-linecap="{cap}" stroke-linejoin="round"/>',
        f'<path d="M88 118l32-34 32 34M96 154l24-26 24 26" stroke="{fg}" stroke-width="{stroke}" stroke-linecap="{cap}" stroke-linejoin="round"/>',
        f'<path d="M120 178V76" stroke="{fg}" stroke-width="{stroke}" stroke-linecap="{cap}"/><path d="M82 116C102 96 112 86 120 76c8 10 18 20 38 40" stroke="{fg}" stroke-width="{stroke}" stroke-linecap="{cap}" stroke-linejoin="round"/>',
        f'<path d="M78 126l42-50 42 50" stroke="{fg}" stroke-width="{stroke}" stroke-linecap="{cap}" stroke-linejoin="round"/><path d="M120 80v90" stroke="{fg}" stroke-width="{max(5, stroke - 2)}" stroke-linecap="{cap}"/>',
    ]
    motif = motifs[(number - 1) % len(motifs)]
    ornament = [
        f'<circle cx="178" cy="62" r="{7 + number % 7}" fill="{accent}" opacity=".32"/>',
        f'<path d="M64 178h112" stroke="{accent}" stroke-width="3" stroke-linecap="round" opacity=".45"/>',
        f'<path d="M70 70c18-14 34-18 50-18s32 4 50 18" stroke="{accent}" stroke-width="3" stroke-linecap="round" opacity=".38"/>',
        f'<circle cx="120" cy="120" r="{54 + number % 12}" stroke="{accent}" stroke-width="3" opacity=".18"/>',
        f'<path d="M54 150c24 16 46 24 66 24s42-8 66-24" stroke="{accent}" stroke-width="3" stroke-linecap="round" opacity=".32"/>',
    ][(number + 2) % 5]
    unique_accent = (
        f'<circle cx="{54 + (number * 29) % 132}" cy="{54 + (number * 31) % 132}" '
        f'r="{3 + number % 5}" fill="{accent}" opacity="{0.16 + (number % 6) * 0.025:.3f}"/>'
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="240" height="240" viewBox="0 0 240 240" fill="none" role="img" aria-label="Back to top">
  <rect x="34" y="34" width="172" height="172" rx="{radius}" fill="{bg}" stroke="{accent}" stroke-width="4"/>
  <path d="M52 188C86 164 103 154 120 154s34 10 68 34" stroke="{accent}" stroke-width="3" stroke-linecap="round" opacity=".18"/>
  {unique_accent}
  {ornament}
  {motif}
</svg>
'''


def write_widget_icons(concept: Path, number: int, code: str) -> None:
    icons_dir = concept / "assets" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)
    (icons_dir / "whatsapp.svg").write_text(whatsapp_svg(), encoding="utf-8")
    (icons_dir / "back-to-top.svg").write_text(back_to_top_svg(number, code), encoding="utf-8")


def update_css(path: Path, number: int, code: str) -> None:
    css = path.read_text(encoding="utf-8")
    css = strip_marked_block(css, CSS_START, CSS_END)
    css = strip_legacy_footer_decoration(css)
    path.write_text(css + "\n" + public_css(number, code).strip() + "\n", encoding="utf-8")


def update_js(path: Path) -> None:
    js = path.read_text(encoding="utf-8")
    js = strip_marked_block(js, JS_START, JS_END)
    path.write_text(js + "\n" + public_js().strip() + "\n", encoding="utf-8")


def page_title(label: str) -> str:
    return f"{label} | Franciele Sofiati"


def clean_page_html(path: Path, code: str, concept_label: str) -> None:
    text = path.read_text(encoding="utf-8")
    label_match = re.search(r'data-page-label="([^"]+)"', text)
    page_match = re.search(r'data-page="([^"]+)"', text)
    layout_match = re.search(r'data-layout="([^"]+)"', text)
    label = html.unescape(label_match.group(1)) if label_match else path.stem.title()
    page = page_match.group(1) if page_match else path.stem
    title = page_title(label)
    description = PAGE_DESCRIPTIONS.get(page, f"{label} for Franciele Sofiati, laser and skin care in Londrina, PR.")
    text = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", text, count=1, flags=re.S)
    text = re.sub(r'data-page-title="[^"]*"', f'data-page-title="{html.escape(title)}"', text, count=1)
    text = re.sub(r'data-page-description="[^"]*"', f'data-page-description="{html.escape(description)}"', text, count=1)
    for attr in ("data-concept-name", "data-concept-number", "data-layout", "data-header", "data-footer", "data-menu"):
        text = re.sub(rf'\s{attr}="[^"]*"', "", text, count=1)
    if layout_match:
        layout = html.escape(layout_match.group(1))
        text = text.replace(f'<p class="eyebrow">{layout}</p>', '<p class="eyebrow">Care pathways</p>')
    text = re.sub(rf"\s*\|\s*{code}\s+{re.escape(concept_label)}\s*\|", " |", text)
    text = re.sub(rf"\b{code}\s+{re.escape(concept_label)}\b", "Sofiati", text)
    text = text.replace(f" for {concept_label}", "")
    text = text.replace(f" page for {concept_label}, a standalone Sofiati concept", " page for Franciele Sofiati")
    text = text.replace(f"Sofiati Home visual for {concept_label}", "Sofiati Home visual")
    path.write_text(text, encoding="utf-8")


def clean_form_partial(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    text = re.sub(r'<input type="hidden" name="concept" value="[^"]*">', '<input type="hidden" name="source" value="Sofiati website">', text)
    path.write_text(text, encoding="utf-8")


def main() -> None:
    concepts = concept_dirs()
    for concept in concepts:
        number, code, _slug, label = concept_meta(concept)
        partials = concept / "partials"
        (partials / "header.html").write_text(header_partial(number, code), encoding="utf-8")
        (partials / "mobile-menu.html").write_text(mobile_menu_partial(number, code), encoding="utf-8")
        (partials / "footer.html").write_text(footer_partial(number, code), encoding="utf-8")
        (partials / "floating-whatsapp.html").write_text(floating_whatsapp_partial(number, code), encoding="utf-8")
        (partials / "back-to-top.html").write_text(back_to_top_partial(number, code), encoding="utf-8")
        (partials / "navigation.html").write_text(navigation_partial(), encoding="utf-8")
        (partials / "status-banner.html").write_text(status_banner_partial(number, code), encoding="utf-8")
        (partials / "accessibility.html").write_text(accessibility_partial(number, code), encoding="utf-8")
        (partials / "concept-switcher.html").write_text("", encoding="utf-8")
        write_footer_assets(concept, number)
        write_widget_icons(concept, number, code)
        clean_form_partial(partials / "consultation-form.html")
        update_js(concept / "js" / "main.js")
        update_css(concept / "css" / "style.css", number, code)
        for page in sorted(concept.glob("*.html")):
            clean_page_html(page, code, label)
    print(f"Refactored {len(concepts)} Sofiati public partial systems.")


if __name__ == "__main__":
    main()
