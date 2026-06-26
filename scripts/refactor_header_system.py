#!/usr/bin/env python3
"""Polish the public header system across all Sofiati concepts.

The script keeps the existing per-concept header/menu layout signatures, but
normalizes the technical skeleton: visible utility name, bounded EN/PT switcher,
non-wrapping desktop nav, visible Consultation CTA, and one shared mobile-menu
runtime. It does not edit page body copy or medical/legal claims.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
CANONICAL_NAME = "Franciele Sofiati"

STATUS_DIV_RE = re.compile(r'<div class="([^"]*status-banner[^"]*)" data-public-layer="utility">')
OLD_HEADER_BLOCK_RE = re.compile(
    r"\n*/\* SOFIATI HEADER REFINEMENT START \*/[\s\S]*?/\* SOFIATI HEADER REFINEMENT END \*/\n*",
    re.M,
)
OLD_HEADER_RUNTIME_RE = re.compile(
    r"\n*/\* SOFIATI HEADER RUNTIME START \*/[\s\S]*?/\* SOFIATI HEADER RUNTIME END \*/\n*",
    re.M,
)
OLD_RENEW_MENU_RUNTIME_RE = re.compile(
    r"\n*/\* SOFIATI 04 RENEW MENU RUNTIME START \*/[\s\S]*?/\* SOFIATI 04 RENEW MENU RUNTIME END \*/\n*",
    re.M,
)


PALETTES = [
    {
        "utility_bg": "linear-gradient(90deg,color-mix(in srgb,var(--soft-white) 94%,white),color-mix(in srgb,var(--sage) 12%,white))",
        "utility_color": "color-mix(in srgb,var(--ink) 76%,var(--bronze))",
        "rule": "linear-gradient(90deg,transparent,color-mix(in srgb,var(--bronze) 54%,transparent),transparent)",
        "switch_bg": "rgba(255,255,255,.72)",
        "switch_active_bg": "var(--ink)",
        "switch_active_color": "white",
        "cta_bg": "var(--ink)",
        "cta_color": "white",
        "cta_shadow": "0 14px 34px rgba(37,35,33,.16)",
    },
    {
        "utility_bg": "linear-gradient(90deg,color-mix(in srgb,var(--sage) 18%,white),color-mix(in srgb,var(--soft-white) 96%,white))",
        "utility_color": "color-mix(in srgb,var(--deep-sage) 82%,var(--ink))",
        "rule": "linear-gradient(90deg,transparent,color-mix(in srgb,var(--sage) 60%,transparent),transparent)",
        "switch_bg": "color-mix(in srgb,var(--soft-white) 86%,white)",
        "switch_active_bg": "var(--deep-sage)",
        "switch_active_color": "white",
        "cta_bg": "var(--deep-sage)",
        "cta_color": "white",
        "cta_shadow": "0 14px 30px color-mix(in srgb,var(--deep-sage) 22%,transparent)",
    },
    {
        "utility_bg": "linear-gradient(90deg,color-mix(in srgb,var(--ink) 94%,black),color-mix(in srgb,var(--deep-sage) 82%,black))",
        "utility_color": "color-mix(in srgb,var(--soft-white) 92%,white)",
        "rule": "linear-gradient(90deg,transparent,color-mix(in srgb,var(--bronze) 68%,transparent),transparent)",
        "switch_bg": "rgba(255,255,255,.1)",
        "switch_active_bg": "color-mix(in srgb,var(--bronze) 78%,white)",
        "switch_active_color": "var(--ink)",
        "cta_bg": "linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--bronze) 46%,var(--ink)))",
        "cta_color": "white",
        "cta_shadow": "0 16px 36px rgba(37,35,33,.22)",
    },
    {
        "utility_bg": "linear-gradient(90deg,color-mix(in srgb,var(--bronze) 13%,white),color-mix(in srgb,var(--soft-white) 96%,white))",
        "utility_color": "color-mix(in srgb,var(--bronze) 72%,var(--ink))",
        "rule": "linear-gradient(90deg,transparent,color-mix(in srgb,var(--bronze) 64%,transparent),transparent)",
        "switch_bg": "rgba(255,255,255,.78)",
        "switch_active_bg": "color-mix(in srgb,var(--bronze) 78%,var(--ink))",
        "switch_active_color": "white",
        "cta_bg": "color-mix(in srgb,var(--bronze) 72%,var(--ink))",
        "cta_color": "white",
        "cta_shadow": "0 13px 30px color-mix(in srgb,var(--bronze) 24%,transparent)",
    },
    {
        "utility_bg": "linear-gradient(90deg,color-mix(in srgb,var(--soft-white) 90%,white),rgba(255,255,255,.72))",
        "utility_color": "var(--ink)",
        "rule": "linear-gradient(90deg,transparent,color-mix(in srgb,var(--line) 70%,var(--bronze)),transparent)",
        "switch_bg": "transparent",
        "switch_active_bg": "white",
        "switch_active_color": "var(--ink)",
        "cta_bg": "white",
        "cta_color": "var(--ink)",
        "cta_shadow": "inset 0 0 0 1px color-mix(in srgb,var(--bronze) 44%,var(--line)),0 12px 26px rgba(37,35,33,.08)",
    },
    {
        "utility_bg": "linear-gradient(90deg,color-mix(in srgb,var(--deep-sage) 14%,var(--soft-white)),color-mix(in srgb,var(--bronze) 12%,white))",
        "utility_color": "color-mix(in srgb,var(--ink) 86%,var(--deep-sage))",
        "rule": "linear-gradient(90deg,transparent,color-mix(in srgb,var(--deep-sage) 52%,transparent),transparent)",
        "switch_bg": "rgba(255,255,255,.62)",
        "switch_active_bg": "color-mix(in srgb,var(--deep-sage) 78%,var(--bronze))",
        "switch_active_color": "white",
        "cta_bg": "linear-gradient(135deg,var(--deep-sage),color-mix(in srgb,var(--bronze) 38%,var(--deep-sage)))",
        "cta_color": "white",
        "cta_shadow": "0 15px 34px color-mix(in srgb,var(--deep-sage) 24%,transparent)",
    },
]

RADII = [
    "999px",
    "18px 42px 18px 18px",
    "8px 26px 8px 26px",
    "26px 8px 26px 8px",
    "14px",
    "0",
    "34px 34px 10px 10px",
]

CTA_RADII = ["999px", "18px", "8px 22px 8px 22px", "22px 8px 22px 8px", "10px", "3px"]


HEADER_RUNTIME = r'''
/* SOFIATI HEADER RUNTIME START */
(() => {
  "use strict";

  const MENU_SELECTOR = "#mobile-menu";
  let lastTrigger = null;

  const menu = () => document.querySelector(MENU_SELECTOR);
  const triggers = () => document.querySelectorAll("[data-menu-toggle]");

  const setExpanded = (expanded) => {
    triggers().forEach((button) => {
      button.setAttribute("aria-expanded", expanded ? "true" : "false");
      button.setAttribute("aria-label", expanded ? "Close menu" : "Open menu");
    });
  };

  const syncMenu = () => {
    const panel = menu();
    if (!panel) return;
    const open = panel.classList.contains("is-open");
    panel.setAttribute("aria-hidden", open ? "false" : "true");
    document.body.classList.toggle("public-menu-locked", open);
    setExpanded(open);
  };

  const openMenu = (trigger) => {
    const panel = menu();
    if (!panel) return;
    lastTrigger = trigger || document.activeElement;
    panel.classList.add("is-open");
    syncMenu();
    window.requestAnimationFrame(() => panel.focus({ preventScroll: true }));
  };

  const closeMenu = ({ restoreFocus = true } = {}) => {
    const panel = menu();
    if (!panel) return;
    panel.classList.remove("is-open");
    syncMenu();
    if (restoreFocus && lastTrigger && typeof lastTrigger.focus === "function") {
      lastTrigger.focus({ preventScroll: true });
    }
  };

  const toggleMenu = (trigger) => {
    if (menu()?.classList.contains("is-open")) closeMenu();
    else openMenu(trigger);
  };

  document.addEventListener("click", (event) => {
    const toggle = event.target.closest("[data-menu-toggle]");
    if (toggle) {
      event.preventDefault();
      toggleMenu(toggle);
      return;
    }

    if (event.target.closest("[data-menu-close]")) {
      event.preventDefault();
      closeMenu();
      return;
    }

    if (event.target.closest("#mobile-menu a")) {
      closeMenu({ restoreFocus: false });
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu()?.classList.contains("is-open")) {
      closeMenu();
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", syncMenu, { once: true });
  } else {
    syncMenu();
  }

  document.addEventListener("sofiati:partials-ready", syncMenu);
})();
/* SOFIATI HEADER RUNTIME END */
'''.strip()


def concept_dirs() -> list[Path]:
    return sorted(path for path in CONCEPTS_DIR.glob("[0-9][0-9]-*") if path.is_dir())


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, text: str) -> bool:
    original = read(path)
    if original == text:
        return False
    path.write_text(text, encoding="utf-8")
    return True


def concept_number(concept: Path) -> int:
    return int(concept.name.split("-", 1)[0])


def utility_classes(original: str, number: int) -> str:
    classes = [token for token in original.split() if not token.startswith("public-utility-tone-")]
    tone = f"public-utility-tone-{number % len(PALETTES)}"
    if tone not in classes:
        classes.append(tone)
    return " ".join(classes)


def update_status_banner(concept: Path) -> bool:
    path = concept / "partials" / "status-banner.html"
    text = read(path)
    number = concept_number(concept)
    match = STATUS_DIV_RE.search(text)
    if not match:
        raise SystemExit(f"Missing utility wrapper: {path.relative_to(ROOT)}")
    classes = utility_classes(match.group(1), number)
    updated = f'''<div class="{classes}" data-public-layer="utility">
  <span class="public-utility-rule" aria-hidden="true"></span>
  <span class="public-utility-mark public-utility-name">{CANONICAL_NAME}</span>
  <span class="public-utility-accent" aria-hidden="true"></span>
  <div class="language-switcher public-language public-language-utility" aria-label="Site language"><button type="button" data-lang-switch="en" aria-pressed="true">EN</button><button type="button" data-lang-switch="pt" aria-pressed="false">PT</button></div>
</div>
'''
    return write_if_changed(path, updated)


def update_essence_header(concept: Path) -> bool:
    if concept.name != "10-essence":
        return False
    path = concept / "partials" / "header.html"
    updated = '''<header class="site-header public-header public-header-10 public-header-layout-essence" data-public-header="essence">
  <div class="public-header-shell"><a class="brand-mark public-brand-mark" href="index.html" aria-label="Sofiati home"><img src="assets/brand/sofiati-logo-primary-white.png" alt="Sofiati logo"></a><div class="public-nav-zone" data-navigation-slot="primary"></div><div class="public-header-tools"><a class="header-consultation" href="consultation.html">Consultation</a><button class="menu-button public-menu-button" type="button" data-menu-toggle aria-controls="mobile-menu" aria-expanded="false" aria-label="Open menu">Menu</button></div></div>
  <div class="public-secondary-bar public-secondary-none" data-public-secondary="none"><div data-navigation-slot="secondary-none"></div></div>
</header>
'''
    return write_if_changed(path, updated)


def ensure_mobile_cta(concept: Path) -> bool:
    path = concept / "partials" / "mobile-menu.html"
    text = read(path)
    if "public-mobile-cta" in text:
        return False
    cta = '  <a class="mobile-consult public-mobile-cta" href="consultation.html">Consultation</a>\n'
    updated = text.replace("</aside>\n", f"{cta}</aside>\n")
    if updated == text:
        raise SystemExit(f"Could not insert mobile CTA: {path.relative_to(ROOT)}")
    return write_if_changed(path, updated)


def install_header_runtime(concept: Path) -> bool:
    path = concept / "js" / "main.js"
    text = read(path)
    cleaned = OLD_HEADER_RUNTIME_RE.sub("\n", text)
    cleaned = OLD_RENEW_MENU_RUNTIME_RE.sub("\n", cleaned).rstrip()
    updated = f"{cleaned}\n\n{HEADER_RUNTIME}\n"
    return write_if_changed(path, updated)


def css_block(number: int) -> str:
    palette = PALETTES[number % len(PALETTES)]
    shell_radius = RADII[number % len(RADII)]
    cta_radius = CTA_RADII[number % len(CTA_RADII)]
    motion = "translateY(-1px)" if number % 2 else "translateY(-2px)"
    accent_shape = "999px 0 999px 0" if number % 3 == 0 else "999px"
    essence_logo = ""
    if number == 10:
        essence_logo = """
.public-header-10.public-header-layout-essence .public-brand-mark {
  min-width: 116px;
  padding: 6px 10px;
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 999px;
  background: rgba(255,255,255,.08);
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.04);
}

.public-header-10.public-header-layout-essence .public-brand-mark img {
  width: 116px;
  height: 44px;
  max-width: 116px;
  max-height: none;
  object-fit: cover;
  object-position: center;
  filter: brightness(1.12) drop-shadow(0 8px 16px rgba(0,0,0,.16));
}

@media (max-width: 980px) {
  .public-header-10.public-header-layout-essence .public-brand-mark {
    min-width: 92px;
    padding: 5px 8px;
  }

  .public-header-10.public-header-layout-essence .public-brand-mark img {
    width: 88px;
    height: 36px;
    max-width: 88px;
    max-height: none;
  }
}
"""
    return f'''
/* SOFIATI HEADER REFINEMENT START */
body.concept {{
  --sf-utility-bg: {palette["utility_bg"]};
  --sf-utility-color: {palette["utility_color"]};
  --sf-utility-rule: {palette["rule"]};
  --sf-language-bg: {palette["switch_bg"]};
  --sf-language-active-bg: {palette["switch_active_bg"]};
  --sf-language-active-color: {palette["switch_active_color"]};
  --sf-header-shell-radius: {shell_radius};
  --sf-header-cta-bg: {palette["cta_bg"]};
  --sf-header-cta-color: {palette["cta_color"]};
  --sf-header-cta-radius: {cta_radius};
  --sf-header-cta-shadow: {palette["cta_shadow"]};
  --sf-header-hover-shift: {motion};
}}

.public-utility.status-banner {{
  display: grid;
  grid-template-columns: minmax(28px, 1fr) auto auto auto;
  align-items: center;
  column-gap: clamp(9px, 1.5vw, 18px);
  min-height: 34px;
  width: 100%;
  padding: 5px max(14px, env(safe-area-inset-right)) 5px max(14px, env(safe-area-inset-left));
  border-bottom: 1px solid color-mix(in srgb, var(--line) 72%, transparent);
  background: var(--sf-utility-bg);
  color: var(--sf-utility-color);
  overflow: clip;
  position: relative;
  z-index: 84;
}}

.public-utility-rule {{
  width: 100%;
  min-width: 28px;
  height: 1px;
  background: var(--sf-utility-rule);
}}

.public-utility-mark.public-utility-name {{
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: max-content;
  font-family: Georgia, "Times New Roman", serif;
  font-style: italic;
  font-weight: 500;
  font-size: clamp(.86rem, 1.1vw, 1.04rem);
  line-height: 1;
  letter-spacing: .035em;
  text-transform: none;
  white-space: nowrap;
  color: currentColor;
}}

.public-utility-dot .public-utility-name::before,
.public-utility-leaf .public-utility-name::before {{
  content: "";
  display: inline-block;
  width: 7px;
  height: 7px;
  border-radius: 999px;
  background: color-mix(in srgb, var(--bronze) 78%, currentColor);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--bronze) 12%, transparent);
}}

.public-utility-leaf .public-utility-name::before {{
  width: 15px;
  height: 7px;
  border-radius: 999px 0 999px 0;
  background: color-mix(in srgb, var(--sage) 68%, var(--bronze));
}}

.public-utility-accent {{
  width: clamp(14px, 2vw, 28px);
  height: 7px;
  border-radius: {accent_shape};
  background: color-mix(in srgb, currentColor 28%, transparent);
  opacity: .78;
}}

.public-language {{
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  gap: 3px;
  max-width: 100%;
  padding: 3px;
  border: 1px solid color-mix(in srgb, currentColor 22%, transparent);
  border-radius: 999px;
  background: var(--sf-language-bg);
  box-shadow: inset 0 0 0 1px color-mix(in srgb, white 26%, transparent);
}}

.public-language button {{
  min-width: 32px;
  min-height: 24px;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: currentColor;
  cursor: pointer;
  font-size: .68rem;
  font-weight: 800;
  line-height: 1;
  letter-spacing: .08em;
  transition: background .18s ease, color .18s ease, transform .18s ease, box-shadow .18s ease;
}}

.public-language button[aria-pressed="true"] {{
  background: var(--sf-language-active-bg);
  color: var(--sf-language-active-color);
  box-shadow: 0 5px 14px color-mix(in srgb, currentColor 12%, transparent);
}}

.public-language button:hover,
.public-language button:focus-visible {{
  outline: 2px solid color-mix(in srgb, var(--bronze) 64%, transparent);
  outline-offset: 2px;
  transform: translateY(-1px);
}}

.public-header.site-header {{
  overflow: visible;
  position: sticky;
  top: 0;
  z-index: 78;
}}

.public-header-shell {{
  width: min(1240px, calc(100% - 28px));
  max-width: calc(100% - 20px);
  min-height: clamp(58px, 5.8vw, 74px);
  align-items: center;
  gap: clamp(8px, 1.1vw, 18px);
  border-radius: var(--sf-header-shell-radius);
  overflow: visible;
}}

.public-header .public-brand-mark {{
  min-width: 0;
  flex: 0 0 auto;
}}

.public-header .public-brand-mark img {{
  display: block;
  width: auto;
  max-width: min(156px, 15vw);
  max-height: 44px;
  object-fit: contain;
}}

.public-header .public-nav-zone {{
  min-width: 0;
}}

.public-header .desktop-nav {{
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: nowrap !important;
  white-space: nowrap;
  min-width: 0;
  gap: clamp(2px, .48vw, 8px) !important;
}}

.public-header .desktop-nav a {{
  flex: 0 0 auto;
  min-height: 34px;
  padding: 7px clamp(4px, .46vw, 8px);
  border-radius: max(4px, calc(var(--radius) / 2));
  font-size: clamp(.58rem, .58vw, .72rem);
  letter-spacing: .012em;
  line-height: 1;
}}

.public-header .desktop-nav a:hover,
.public-header .desktop-nav a:focus-visible {{
  transform: var(--sf-header-hover-shift);
}}

.public-header-tools {{
  display: inline-flex;
  align-items: center;
  justify-content: flex-end;
  gap: clamp(6px, .8vw, 11px);
  min-width: max-content;
}}

.header-consultation {{
  min-height: 38px;
  display: inline-flex !important;
  align-items: center;
  justify-content: center;
  border: 1px solid color-mix(in srgb, var(--bronze) 46%, transparent) !important;
  border-radius: var(--sf-header-cta-radius) !important;
  background: var(--sf-header-cta-bg) !important;
  color: var(--sf-header-cta-color) !important;
  padding: 8px clamp(11px, 1vw, 16px);
  box-shadow: var(--sf-header-cta-shadow);
  font-size: clamp(.66rem, .62vw, .76rem);
  font-weight: 850;
  letter-spacing: .02em;
  line-height: 1;
  text-decoration: none;
  white-space: nowrap;
  transition: transform .2s ease, box-shadow .2s ease, background .2s ease, color .2s ease;
}}

.header-consultation:hover,
.header-consultation:focus-visible {{
  outline: 2px solid color-mix(in srgb, var(--bronze) 58%, transparent);
  outline-offset: 3px;
  transform: translateY(-2px);
}}

.public-header .public-menu-button {{
  min-width: 42px;
  min-height: 38px;
  border-radius: 999px;
  white-space: nowrap;
}}

.public-menu-locked {{
  overflow: hidden;
}}

{essence_logo}

@media (min-width: 981px) {{
  .public-header .public-menu-button {{
    display: none !important;
  }}

  .public-header-layout-essence .public-header-shell {{
    grid-template-columns: auto minmax(0, 1fr) auto;
    width: min(1180px, calc(100% - 30px));
  }}

  .public-header-layout-essence .public-nav-zone,
  .public-header-layout-essence .desktop-nav {{
    display: flex !important;
  }}
}}

@media (max-width: 1180px) and (min-width: 981px) {{
  .public-header-shell {{
    width: min(100%, calc(100% - 18px));
    padding-left: clamp(10px, 1.2vw, 18px);
    padding-right: clamp(10px, 1.2vw, 18px);
  }}

  .public-header .public-brand-mark img {{
    max-width: min(132px, 13vw);
  }}

  .public-header .desktop-nav a {{
    font-size: .58rem;
    padding-left: 4px;
    padding-right: 4px;
  }}

  .header-consultation {{
    padding-left: 10px;
    padding-right: 10px;
  }}
}}

@media (max-width: 980px) {{
  .public-utility.status-banner {{
    display: grid !important;
    grid-template-columns: minmax(0, 1fr) auto;
    min-height: 32px;
    padding: 4px max(12px, env(safe-area-inset-right)) 4px max(12px, env(safe-area-inset-left));
    column-gap: 10px;
    position: sticky;
    top: 0;
    z-index: 90;
  }}

  .public-utility-rule,
  .public-utility-accent {{
    display: none;
  }}

  .public-utility-mark.public-utility-name {{
    min-width: 0;
    overflow: hidden;
    text-overflow: ellipsis;
    font-size: clamp(.78rem, 3.1vw, .92rem);
  }}

  .public-language {{
    padding: 2px;
  }}

  .public-language button {{
    min-width: 30px;
    min-height: 23px;
    font-size: .64rem;
  }}

  .public-header.site-header {{
    top: 32px;
    z-index: 82;
  }}

  .public-header-shell,
  .public-header-layout-split .public-header-shell,
  .public-header-layout-balanced .public-header-shell,
  .public-header-layout-stacked .public-header-shell,
  .public-header-layout-ritual .public-header-shell,
  .public-header-layout-noble .public-header-shell,
  .public-header-layout-sovereign .public-header-shell,
  .public-header-layout-atelier .public-header-shell,
  .public-header-layout-essence .public-header-shell {{
    width: 100%;
    max-width: 100%;
    min-height: 58px;
    margin: 0;
    grid-template-columns: auto minmax(0, 1fr) auto;
    border-radius: 0;
    padding: 8px max(12px, env(safe-area-inset-right)) 8px max(12px, env(safe-area-inset-left));
    transform: none !important;
  }}

  .public-header .public-brand-mark img {{
    max-width: min(126px, 34vw);
    max-height: 38px;
  }}

  .public-header .public-nav-zone,
  .public-header .desktop-nav,
  .public-secondary-bar {{
    display: none !important;
  }}

  .public-header-tools {{
    grid-column: 3;
    gap: 7px;
  }}

  .header-consultation {{
    min-height: 36px;
    padding: 8px 10px;
    font-size: .66rem;
  }}

  .public-menu-button {{
    display: inline-flex !important;
    min-width: 42px;
    min-height: 36px;
    padding: 7px 11px;
  }}
}}

@media (max-width: 430px) {{
  .public-header .public-brand-mark img {{
    max-width: min(112px, 29vw);
  }}

  .public-header-tools {{
    gap: 5px;
  }}

  .header-consultation {{
    min-width: 38px;
    max-width: 104px;
    overflow: hidden;
    text-overflow: ellipsis;
  }}

  .public-menu-button {{
    min-width: 38px;
    padding-left: 9px;
    padding-right: 9px;
  }}
}}
/* SOFIATI HEADER REFINEMENT END */
'''.strip()


def update_css(concept: Path) -> bool:
    path = concept / "css" / "style.css"
    text = read(path)
    cleaned = OLD_HEADER_BLOCK_RE.sub("\n", text).rstrip()
    updated = f"{cleaned}\n\n{css_block(concept_number(concept))}\n"
    return write_if_changed(path, updated)


def main() -> None:
    changed: dict[str, list[str]] = {}
    for concept in concept_dirs():
        touched: list[str] = []
        if update_status_banner(concept):
            touched.append("status-banner")
        if update_essence_header(concept):
            touched.append("header")
        if ensure_mobile_cta(concept):
            touched.append("mobile-menu")
        if install_header_runtime(concept):
            touched.append("main-js")
        if update_css(concept):
            touched.append("css")
        if touched:
            changed[concept.name] = touched

    for concept, touched in changed.items():
        print(f"{concept}: {', '.join(touched)}")
    print(f"Updated {len(changed)} concepts.")


if __name__ == "__main__":
    main()
