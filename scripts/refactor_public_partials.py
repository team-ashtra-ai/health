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


def footer_partial(number: int, code: str) -> str:
    layout = FOOTER_LAYOUTS[number - 1]
    cta_label = ["Book consultation", "Request evaluation", "Contact Franciele", "Start with WhatsApp"][(number - 1) % 4]
    cta_href = "https://wa.me/5543991043536" if cta_label == "Start with WhatsApp" else "consultation.html"
    cta_attrs = ' rel="noopener" target="_blank"' if cta_label == "Start with WhatsApp" else ""
    dark_footer = number % 5 in {0, 1, 4} or layout in {"business-card", "immersive-botanical", "noble", "wisdom", "sovereign", "silhouette", "origin"}
    logo_mark = "white" if dark_footer else "sage"
    monogram = "assets/brand/sofiati-monogram-white.png" if dark_footer else "assets/brand/sofiati-monogram-sage.png"
    return f'''<footer class="site-footer public-footer public-footer-{code} public-footer-layout-{layout}" data-public-footer="{layout}">
  <div class="public-footer-shell">
    <section class="footer-brand-panel" aria-label="Brand">
      {logo(logo_mark)}
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
      <p>&copy; 2026 Franciele Sofiati. All rights reserved.</p>
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
.public-footer.site-footer{{
  --public-footer-bg:{colors["bg"]};
  --public-footer-fg:{colors["fg"]};
  --public-footer-panel:{colors["panel"]};
  --public-footer-grid:{colors["grid"]};
  position:relative;
  overflow:hidden;
  display:block;
  margin-top:clamp(46px,7vw,96px);
  padding:0;
  background:var(--public-footer-bg);
  color:var(--public-footer-fg);
}}
.public-footer-shell{{width:var(--page);margin:auto;padding:clamp(48px,8vw,104px) 0 clamp(78px,9vw,132px);display:grid;grid-template-columns:var(--public-footer-grid);gap:clamp(18px,3.6vw,48px);align-items:start}}
.footer-brand-panel,
.footer-link-group,
.footer-contact{{display:grid;align-content:start;gap:9px}}
.public-footer .public-brand-mark{{display:inline-flex;text-decoration:none;justify-self:start}}
.public-footer .public-brand-mark img{{width:min(236px,70vw);max-height:84px;object-fit:contain}}
.footer-monogram{{width:clamp(48px,6vw,88px);opacity:.7;margin:4px 0}}
.footer-brand-panel h2{{margin:0;color:inherit;font-size:clamp(1.5rem,2.8vw,3.2rem)}}
.footer-role,
.footer-credential{{font-weight:800;color:color-mix(in srgb,currentColor 84%,var(--bronze))}}
.public-footer p,
.footer-contact,
.public-footer a{{color:color-mix(in srgb,currentColor 78%,transparent)}}
.public-footer h3{{margin:0 0 8px;color:inherit;font-family:Inter,ui-sans-serif,system-ui,sans-serif;font-size:.72rem;font-weight:900;letter-spacing:.12em;text-transform:uppercase}}
.footer-link-group a,
.footer-contact a{{text-decoration:none}}
.footer-link-group a:hover,
.footer-contact a:hover{{color:inherit}}
.footer-cta{{justify-self:start;min-height:42px;display:inline-flex;align-items:center;justify-content:center;margin-top:8px;padding:9px 14px;border:1px solid color-mix(in srgb,currentColor 28%,transparent);border-radius:999px;background:color-mix(in srgb,var(--bronze) 18%,transparent);color:inherit;text-decoration:none;font-weight:800}}
.footer-contact{{font-style:normal;padding:clamp(14px,2vw,22px);border:1px solid color-mix(in srgb,currentColor 16%,transparent);border-radius:max(4px,{radius}px);background:var(--public-footer-panel)}}
.footer-bottom-row{{grid-column:1/-1;display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap;padding-top:20px;border-top:1px solid color-mix(in srgb,currentColor 16%,transparent);font-size:.86rem}}
.public-footer::after{{content:"";position:absolute;left:{footer_stamp_x}%;bottom:{footer_stamp_y}px;width:min(300px,44vw);aspect-ratio:1;background:url("../assets/botanical/footer-botanical-stamp.svg") center/contain no-repeat;opacity:.08;pointer-events:none}}
.public-footer-layout-split-cta .footer-brand-panel,
.public-footer-layout-kindred .footer-contact,
.public-footer-layout-solace .footer-contact,
.public-footer-layout-luminous .footer-contact{{box-shadow:0 22px 58px rgba(37,35,33,.10)}}
.public-footer-layout-minimal-legal .public-footer-shell,
.public-footer-layout-pure .public-footer-shell,
.public-footer-layout-proof .public-footer-shell,
.public-footer-layout-safeguard .public-footer-shell{{border-top:1px solid color-mix(in srgb,currentColor 18%,transparent);gap:24px}}
.public-footer-layout-centered .public-footer-shell,
.public-footer-layout-symmetrical .public-footer-shell,
.public-footer-layout-halo .public-footer-shell{{text-align:center}}
.public-footer-layout-centered .public-brand-mark,
.public-footer-layout-symmetrical .public-brand-mark,
.public-footer-layout-halo .public-brand-mark,
.public-footer-layout-centered .footer-cta,
.public-footer-layout-symmetrical .footer-cta,
.public-footer-layout-halo .footer-cta{{justify-self:center}}
.public-footer-layout-staggered-motion .footer-link-group:nth-of-type(2),
.public-footer-layout-evolve .footer-link-group:nth-of-type(2),
.public-footer-layout-vivant .footer-link-group:nth-of-type(2){{margin-top:clamp(18px,4vw,46px)}}
.public-footer-layout-sculptural .footer-brand-panel,
.public-footer-layout-form .footer-brand-panel,
.public-footer-layout-curate .footer-link-group{{padding:clamp(14px,2vw,22px);border:1px solid color-mix(in srgb,currentColor 14%,transparent);background:var(--public-footer-panel)}}
.public-footer-layout-business-card .public-footer-shell,
.public-footer-layout-noble .public-footer-shell,
.public-footer-layout-sovereign .public-footer-shell{{grid-template-columns:1.32fr .76fr .86fr .68fr 1fr}}
.public-footer-layout-atelier .public-footer-shell,
.public-footer-layout-vista .public-footer-shell{{width:min(1320px,calc(100% - 32px));grid-template-columns:1.1fr .9fr .9fr .8fr 1.12fr}}
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
  .public-footer-shell{{grid-template-columns:1fr 1fr;gap:28px;padding-bottom:112px}}
  .footer-brand-panel,
  .footer-bottom-row{{grid-column:1/-1}}
}}
@media(max-width:620px){{
  .public-mobile-menu.mobile-menu{{padding:18px}}
  .public-mobile-menu-top{{grid-template-columns:1fr auto;align-items:start}}
  .public-mobile-menu .public-language{{grid-column:1/-1;justify-self:start}}
  .public-mobile-primary{{grid-template-columns:1fr}}
  .public-mobile-primary a{{min-height:50px;font-size:clamp(1.55rem,8vw,2.45rem)}}
  .public-footer-shell{{grid-template-columns:1fr}}
  .public-footer .public-brand-mark img{{width:min(220px,76vw)}}
  .footer-bottom-row{{display:grid}}
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
  if (window.SofiatiPartialsReady) {{
    window.SofiatiPartialsReady.then(enhancePublicMenu);
  }} else if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", enhancePublicMenu, {{ once: true }});
  }} else {{
    enhancePublicMenu();
  }}
}})();
{JS_END}
'''


def update_css(path: Path, number: int, code: str) -> None:
    css = path.read_text(encoding="utf-8")
    css = strip_marked_block(css, CSS_START, CSS_END)
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
        (partials / "navigation.html").write_text(navigation_partial(), encoding="utf-8")
        (partials / "status-banner.html").write_text(status_banner_partial(number, code), encoding="utf-8")
        (partials / "accessibility.html").write_text(accessibility_partial(number, code), encoding="utf-8")
        (partials / "concept-switcher.html").write_text("", encoding="utf-8")
        clean_form_partial(partials / "consultation-form.html")
        update_js(concept / "js" / "main.js")
        update_css(concept / "css" / "style.css", number, code)
        for page in sorted(concept.glob("*.html")):
            clean_page_html(page, code, label)
    print(f"Refactored {len(concepts)} Sofiati public partial systems.")


if __name__ == "__main__":
    main()
