#!/usr/bin/env python3
"""
Sofiati Minimal Footer Cookie Bars

What this script does:
- Removes old floating cookie notices, popups, banners and old cookie scripts.
- Adds one tiny cookie-loader script to index.html by default.
- Creates assets/js/sofiati-footer-cookie.js for each concept.
- JS inserts the cookie bar AFTER the final <footer>.
- The cookie bar is not fixed, not floating, not modal, not a popup.
- All 50 bars are still minimal footer bars, but each one has a clearer unique treatment.
- If the visitor does nothing, it saves essential-only and disappears.

Run:
  /usr/bin/python3 scripts/refactor_sofiati_cookie_notices.py --apply --force

Optional, add to every page:
  /usr/bin/python3 scripts/refactor_sofiati_cookie_notices.py --apply --force --all-pages
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path


NEW_HTML_START = "<!-- SOFIATI FOOTER COOKIE BAR START -->"
NEW_HTML_END = "<!-- SOFIATI FOOTER COOKIE BAR END -->"
JS_FILENAME = "sofiati-footer-cookie.js"

CONCEPT_SLUGS = [
    "inspire", "empower", "enhance", "renew", "elevate",
    "refine", "glow", "balance", "radiance", "essence",
    "bloom", "vital", "poise", "aura", "clarity",
    "grace", "sculpt", "lumin", "verda", "halo",
    "calm", "precision", "ritual", "signal", "align",
    "vivant", "form", "pure", "solace", "method",
    "evolve", "serene", "elan", "flora", "atelier",
    "lumina", "vellum", "origin", "kindred", "noble",
    "vista", "softline", "meridian", "safeguard", "silhouette",
    "curate", "proof", "signature", "wisdom", "sovereign",
]

OLD_MARKER_BLOCKS = [
    ("<!-- SOFIATI COOKIE NOTICE V1 START -->", "<!-- SOFIATI COOKIE NOTICE V1 END -->"),
    ("<!-- SOFIATI COOKIE NOTICE V2 START -->", "<!-- SOFIATI COOKIE NOTICE V2 END -->"),
    ("<!-- SOFIATI MINIMAL HOME COOKIE START -->", "<!-- SOFIATI MINIMAL HOME COOKIE END -->"),
    ("<!-- SOFIATI FOOTER COOKIE BAR START -->", "<!-- SOFIATI FOOTER COOKIE BAR END -->"),
    ("/* SOFIATI COOKIE NOTICE V1 START */", "/* SOFIATI COOKIE NOTICE V1 END */"),
    ("/* SOFIATI COOKIE NOTICE V2 START */", "/* SOFIATI COOKIE NOTICE V2 END */"),
    ("/* SOFIATI MINIMAL HOME COOKIE START */", "/* SOFIATI MINIMAL HOME COOKIE END */"),
    ("/* SOFIATI FOOTER COOKIE BAR START */", "/* SOFIATI FOOTER COOKIE BAR END */"),
]


VARIANTS = [
    {"layout":"split", "tone":"dark", "sep":"gold-top", "mark":"dot", "buttons":"solid-first", "width":"wide", "align":"left"},
    {"layout":"center", "tone":"sage", "sep":"thin-top", "mark":"leaf", "buttons":"soft", "width":"medium", "align":"center"},
    {"layout":"ledger", "tone":"white", "sep":"left-rule", "mark":"line", "buttons":"square", "width":"compact", "align":"left"},
    {"layout":"quiet", "tone":"eucalyptus", "sep":"none", "mark":"sprig", "buttons":"text", "width":"narrow", "align":"left"},
    {"layout":"editorial", "tone":"cream", "sep":"champagne", "mark":"diamond", "buttons":"solid-first", "width":"wide", "align":"center"},
    {"layout":"micro", "tone":"plain", "sep":"none", "mark":"none", "buttons":"text", "width":"narrow", "align":"center"},
    {"layout":"balanced", "tone":"white-warm", "sep":"center-line", "mark":"sun", "buttons":"pill-outline", "width":"medium", "align":"center"},
    {"layout":"two-part", "tone":"ivory", "sep":"soft-top", "mark":"bracket", "buttons":"soft", "width":"wide", "align":"left"},
    {"layout":"fine-print", "tone":"radiance", "sep":"bottom-line", "mark":"ray", "buttons":"text", "width":"medium", "align":"left"},
    {"layout":"single-line", "tone":"transparent", "sep":"top-only", "mark":"none", "buttons":"text", "width":"compact", "align":"center"},

    {"layout":"botanical", "tone":"bloom", "sep":"soft-top", "mark":"leaf", "buttons":"pill-outline", "width":"medium", "align":"left"},
    {"layout":"split", "tone":"warm-sage", "sep":"motion", "mark":"arrow", "buttons":"soft", "width":"wide", "align":"left"},
    {"layout":"editorial", "tone":"charcoal", "sep":"gold-top", "mark":"diamond", "buttons":"text", "width":"medium", "align":"left"},
    {"layout":"center", "tone":"aura", "sep":"halo", "mark":"circle", "buttons":"solid-first", "width":"medium", "align":"center"},
    {"layout":"ledger", "tone":"white", "sep":"thin-top", "mark":"check", "buttons":"square", "width":"compact", "align":"left"},
    {"layout":"soft", "tone":"grace", "sep":"soft-top", "mark":"curve", "buttons":"pill-outline", "width":"medium", "align":"center"},
    {"layout":"angular", "tone":"dark-bronze", "sep":"diagonal", "mark":"angle", "buttons":"square", "width":"medium", "align":"left"},
    {"layout":"balanced", "tone":"lumin", "sep":"glow", "mark":"ray", "buttons":"solid-first", "width":"medium", "align":"center"},
    {"layout":"botanical", "tone":"deep-green", "sep":"gold-top", "mark":"sprig", "buttons":"soft", "width":"wide", "align":"left"},
    {"layout":"center", "tone":"dark", "sep":"halo", "mark":"circle", "buttons":"pill-outline", "width":"medium", "align":"center"},

    {"layout":"micro", "tone":"calm", "sep":"none", "mark":"dash", "buttons":"text", "width":"narrow", "align":"left"},
    {"layout":"ledger", "tone":"precision", "sep":"left-rule", "mark":"line", "buttons":"square", "width":"compact", "align":"left"},
    {"layout":"ritual", "tone":"cream", "sep":"step", "mark":"step", "buttons":"pill-outline", "width":"medium", "align":"left"},
    {"layout":"signal", "tone":"signal-dark", "sep":"scan", "mark":"signal", "buttons":"square", "width":"medium", "align":"left"},
    {"layout":"two-part", "tone":"plain", "sep":"center-line", "mark":"line", "buttons":"soft", "width":"wide", "align":"left"},
    {"layout":"soft", "tone":"vivant", "sep":"motion", "mark":"arrow", "buttons":"solid-first", "width":"medium", "align":"left"},
    {"layout":"angular", "tone":"form-dark", "sep":"diagonal", "mark":"angle", "buttons":"square", "width":"medium", "align":"left"},
    {"layout":"single-line", "tone":"transparent", "sep":"none", "mark":"none", "buttons":"text", "width":"narrow", "align":"center"},
    {"layout":"quiet", "tone":"solace", "sep":"soft-top", "mark":"circle", "buttons":"pill-outline", "width":"medium", "align":"left"},
    {"layout":"ledger", "tone":"method", "sep":"step", "mark":"step", "buttons":"square", "width":"compact", "align":"left"},

    {"layout":"balanced", "tone":"evolve", "sep":"motion", "mark":"arrow", "buttons":"soft", "width":"wide", "align":"center"},
    {"layout":"micro", "tone":"serene", "sep":"none", "mark":"dash", "buttons":"text", "width":"narrow", "align":"center"},
    {"layout":"editorial", "tone":"elan-dark", "sep":"gold-top", "mark":"diamond", "buttons":"text", "width":"wide", "align":"left"},
    {"layout":"botanical", "tone":"flora", "sep":"soft-top", "mark":"sprig", "buttons":"pill-outline", "width":"medium", "align":"left"},
    {"layout":"two-part", "tone":"atelier", "sep":"left-rule", "mark":"bracket", "buttons":"square", "width":"wide", "align":"left"},
    {"layout":"balanced", "tone":"lumina", "sep":"glow", "mark":"ray", "buttons":"solid-first", "width":"medium", "align":"center"},
    {"layout":"fine-print", "tone":"vellum", "sep":"dashed", "mark":"line", "buttons":"text", "width":"compact", "align":"left"},
    {"layout":"botanical", "tone":"origin-dark", "sep":"left-rule", "mark":"leaf", "buttons":"pill-outline", "width":"medium", "align":"left"},
    {"layout":"quiet", "tone":"kindred", "sep":"soft-top", "mark":"circle", "buttons":"soft", "width":"medium", "align":"left"},
    {"layout":"editorial", "tone":"noble-dark", "sep":"champagne", "mark":"diamond", "buttons":"text", "width":"wide", "align":"center"},

    {"layout":"wide", "tone":"vista", "sep":"thin-top", "mark":"line", "buttons":"square", "width":"extra-wide", "align":"center"},
    {"layout":"soft", "tone":"softline", "sep":"soft-top", "mark":"curve", "buttons":"pill-outline", "width":"medium", "align":"center"},
    {"layout":"two-part", "tone":"meridian", "sep":"left-rule", "mark":"bracket", "buttons":"square", "width":"medium", "align":"left"},
    {"layout":"ledger", "tone":"safeguard", "sep":"thin-top", "mark":"check", "buttons":"square", "width":"compact", "align":"left"},
    {"layout":"minimal", "tone":"silhouette-dark", "sep":"none", "mark":"none", "buttons":"text", "width":"compact", "align":"left"},
    {"layout":"split", "tone":"curate", "sep":"soft-top", "mark":"bracket", "buttons":"pill-outline", "width":"wide", "align":"left"},
    {"layout":"ledger", "tone":"proof", "sep":"left-rule", "mark":"check", "buttons":"square", "width":"compact", "align":"left"},
    {"layout":"center", "tone":"signature", "sep":"champagne", "mark":"signature", "buttons":"solid-first", "width":"wide", "align":"center"},
    {"layout":"fine-print", "tone":"wisdom-dark", "sep":"gold-top", "mark":"book", "buttons":"pill-outline", "width":"medium", "align":"left"},
    {"layout":"wide", "tone":"sovereign-dark", "sep":"champagne", "mark":"crest", "buttons":"solid-first", "width":"extra-wide", "align":"center"},
]


TONES = {
    "dark": ("#252321", "#F8F7F2", "rgba(248,247,242,.70)", "#C9A56A", "1px solid rgba(201,165,106,.24)"),
    "sage": ("#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#879588", "1px solid rgba(127,141,130,.20)"),
    "white": ("#FFFFFF", "#252321", "rgba(37,35,33,.64)", "#7F8D82", "1px solid rgba(37,35,33,.12)"),
    "eucalyptus": ("#EEF1EA", "#252321", "rgba(37,35,33,.64)", "#879588", "1px solid rgba(127,141,130,.22)"),
    "cream": ("#F4EFE5", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px solid rgba(154,107,53,.20)"),
    "plain": ("transparent", "#252321", "rgba(37,35,33,.55)", "#7F8D82", "0"),
    "white-warm": ("#FFFDF8", "#252321", "rgba(37,35,33,.62)", "#C9A56A", "1px solid rgba(201,165,106,.18)"),
    "ivory": ("#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#879588", "1px solid rgba(127,141,130,.18)"),
    "radiance": ("#FFFDF8", "#252321", "rgba(37,35,33,.62)", "#C9A56A", "1px solid rgba(201,165,106,.20)"),
    "transparent": ("transparent", "#252321", "rgba(37,35,33,.55)", "#A2AEA0", "0"),
    "bloom": ("#EAF0E8", "#252321", "rgba(37,35,33,.64)", "#879588", "1px solid rgba(127,141,130,.22)"),
    "warm-sage": ("#EEF1EA", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px solid rgba(154,107,53,.18)"),
    "charcoal": ("#252321", "#F8F7F2", "rgba(248,247,242,.70)", "#C9A56A", "1px solid rgba(201,165,106,.22)"),
    "aura": ("#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#C9A56A", "1px solid rgba(201,165,106,.18)"),
    "grace": ("#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#A2AEA0", "1px solid rgba(162,174,160,.18)"),
    "dark-bronze": ("#2B2B27", "#F8F7F2", "rgba(248,247,242,.70)", "#C9A56A", "1px solid rgba(201,165,106,.22)"),
    "lumin": ("#FFFFFF", "#252321", "rgba(37,35,33,.62)", "#C9A56A", "1px solid rgba(201,165,106,.16)"),
    "deep-green": ("#2E3A32", "#F8F7F2", "rgba(248,247,242,.70)", "#DAB26F", "1px solid rgba(218,178,111,.22)"),
    "calm": ("#F8F7F2", "#252321", "rgba(37,35,33,.58)", "#A2AEA0", "1px solid rgba(162,174,160,.16)"),
    "precision": ("#FFFFFF", "#252321", "rgba(37,35,33,.66)", "#7F8D82", "1px solid rgba(37,35,33,.12)"),
    "signal-dark": ("#202524", "#F8F7F2", "rgba(248,247,242,.70)", "#A2AEA0", "1px solid rgba(162,174,160,.22)"),
    "vivant": ("#EEF1EA", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px solid rgba(154,107,53,.18)"),
    "form-dark": ("#2B2B27", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "1px solid rgba(201,165,106,.22)"),
    "solace": ("#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#879588", "1px solid rgba(127,141,130,.18)"),
    "method": ("#FBFAF6", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px solid rgba(154,107,53,.18)"),
    "evolve": ("#EEF1EA", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px solid rgba(154,107,53,.18)"),
    "serene": ("#F8F7F2", "#252321", "rgba(37,35,33,.58)", "#A2AEA0", "1px solid rgba(162,174,160,.16)"),
    "elan-dark": ("#252321", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "1px solid rgba(201,165,106,.24)"),
    "flora": ("#E9F0E6", "#252321", "rgba(37,35,33,.64)", "#879588", "1px solid rgba(127,141,130,.20)"),
    "atelier": ("#FBFAF6", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px solid rgba(154,107,53,.20)"),
    "lumina": ("#FFFFFF", "#252321", "rgba(37,35,33,.62)", "#C9A56A", "1px solid rgba(201,165,106,.16)"),
    "vellum": ("#FBFAF6", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px dashed rgba(154,107,53,.22)"),
    "origin-dark": ("#2B312D", "#F8F7F2", "rgba(248,247,242,.70)", "#C9A56A", "1px solid rgba(201,165,106,.20)"),
    "kindred": ("#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#A2AEA0", "1px solid rgba(162,174,160,.18)"),
    "noble-dark": ("#201F1E", "#F8F7F2", "rgba(248,247,242,.72)", "#DAB26F", "1px solid rgba(218,178,111,.24)"),
    "vista": ("#F8F7F2", "#252321", "rgba(37,35,33,.64)", "#879588", "1px solid rgba(127,141,130,.18)"),
    "softline": ("#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#A2AEA0", "1px solid rgba(162,174,160,.18)"),
    "meridian": ("#FFFFFF", "#252321", "rgba(37,35,33,.64)", "#879588", "1px solid rgba(127,141,130,.18)"),
    "safeguard": ("#FFFFFF", "#252321", "rgba(37,35,33,.66)", "#7F8D82", "1px solid rgba(37,35,33,.12)"),
    "silhouette-dark": ("#252321", "#F8F7F2", "rgba(248,247,242,.68)", "#C9A56A", "1px solid rgba(201,165,106,.18)"),
    "curate": ("#F4EFE5", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px solid rgba(154,107,53,.20)"),
    "proof": ("#FBFBF8", "#252321", "rgba(37,35,33,.66)", "#7F8D82", "1px solid rgba(37,35,33,.12)"),
    "signature": ("#F8F7F2", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "1px solid rgba(154,107,53,.20)"),
    "wisdom-dark": ("#252321", "#F8F7F2", "rgba(248,247,242,.70)", "#C9A56A", "1px solid rgba(201,165,106,.20)"),
    "sovereign-dark": ("#1F1E1D", "#F8F7F2", "rgba(248,247,242,.74)", "#DAB26F", "1px solid rgba(218,178,111,.24)"),
}


WIDTHS = {
    "narrow": "min(780px,calc(100% - 28px))",
    "compact": "min(940px,calc(100% - 30px))",
    "medium": "min(1080px,calc(100% - 34px))",
    "wide": "min(1180px,calc(100% - 38px))",
    "extra-wide": "min(1280px,calc(100% - 44px))",
}


def concept_dirs(concepts_dir: Path) -> list[Path]:
    if not concepts_dir.exists():
        raise FileNotFoundError(f"Missing concepts directory: {concepts_dir}")
    return sorted(p for p in concepts_dir.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name))


def concept_number(concept: Path) -> int:
    return int(concept.name.split("-", 1)[0])


def all_html_files(concept: Path) -> list[Path]:
    return sorted(p for p in concept.glob("*.html") if p.is_file())


def target_html_files(concept: Path, all_pages: bool) -> list[Path]:
    if all_pages:
        return all_html_files(concept)
    index = concept / "index.html"
    return [index] if index.exists() else []


def git_is_dirty(root: Path) -> bool:
    try:
        result = subprocess.run(["git", "status", "--porcelain"], cwd=root, text=True, capture_output=True, check=False)
        return bool(result.stdout.strip())
    except Exception:
        return False


def backup_file(path: Path) -> None:
    if path.exists():
        shutil.copy2(path, path.with_suffix(path.suffix + ".cookie-clean.bak"))


def write_if_changed(path: Path, content: str, apply: bool) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == content:
        return False
    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        backup_file(path)
        path.write_text(content, encoding="utf-8")
    return True


def remove_marker_blocks(text: str) -> str:
    for start, end in OLD_MARKER_BLOCKS:
        text = re.sub(re.escape(start) + r".*?" + re.escape(end), "", text, flags=re.S)
    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def remove_old_cookie_html(text: str) -> str:
    text = remove_marker_blocks(text)

    old_patterns = [
        r"\s*<section\b[^>]*(?:data-cookie-notice|data-cookie-bar|cookie)[^>]*>.*?</section>\s*",
        r"\s*<div\b[^>]*(?:cookie-consent|cookie-banner|cookie-notice|cookie-popup|cookie-toast|cookie-preferences|cookie-widget|cookie-box)[^>]*>.*?</div>\s*",
        r"\s*<aside\b[^>]*(?:cookie-consent|cookie-banner|cookie-notice|cookie-popup|cookie-toast|cookie-preferences|cookie-widget|cookie-box)[^>]*>.*?</aside>\s*",
        r"\s*<dialog\b[^>]*(?:cookie-consent|cookie-banner|cookie-notice|cookie-popup|cookie-toast|cookie-preferences|cookie-widget|cookie-box)[^>]*>.*?</dialog>\s*",
    ]

    for pattern in old_patterns:
        text = re.sub(pattern, "\n", text, flags=re.S | re.I)

    # Remove old cookie loader script tags, but not normal links to cookies.html.
    text = re.sub(
        r'\s*<script\b[^>]*src=["\'][^"\']*(?:cookie|consent)[^"\']*["\'][^>]*>\s*</script>\s*',
        "\n",
        text,
        flags=re.S | re.I,
    )

    text = re.sub(
        r'\s*<script\b[^>]*data-sofiati-cookie-loader[^>]*>\s*</script>\s*',
        "\n",
        text,
        flags=re.S | re.I,
    )

    # Remove inline scripts that contain the exact old floating notice wording.
    text = re.sub(
        r"\s*<script\b[^>]*>[^<]*(?:Cookie preferences|Only essential preferences are active in this static concept)[\s\S]*?</script>\s*",
        "\n",
        text,
        flags=re.I,
    )

    return re.sub(r"\n{3,}", "\n\n", text).rstrip() + "\n"


def inject_loader(html: str) -> str:
    html = remove_old_cookie_html(html)

    loader = f"""
{NEW_HTML_START}
<script src="assets/js/{JS_FILENAME}" defer data-sofiati-cookie-loader></script>
{NEW_HTML_END}
""".strip()

    if re.search(r"</body\s*>", html, flags=re.I):
        return re.sub(r"</body\s*>", loader + "\n</body>", html, count=1, flags=re.I)

    return html.rstrip() + "\n" + loader + "\n"


def clean_asset_files(concept: Path, apply: bool) -> tuple[int, int]:
    css_changed = 0
    js_changed = 0
    files: list[Path] = []

    for folder in [concept / "assets", concept / "css", concept / "js"]:
        if folder.exists():
            files.extend(folder.glob("**/*.css"))
            files.extend(folder.glob("**/*.js"))

    files.extend(concept.glob("*.css"))
    files.extend(concept.glob("*.js"))

    for path in sorted(set(files)):
        if path.name == JS_FILENAME:
            continue

        old = path.read_text(encoding="utf-8")
        new = remove_marker_blocks(old)

        # Remove old generated floating notice JS if present.
        new = re.sub(
            r"[\s\S]*?(?:Cookie preferences|Only essential preferences are active in this static concept)[\s\S]*",
            "",
            new,
            flags=re.I,
        ) if path.suffix.lower() == ".js" and (
            "Cookie preferences" in new or "Only essential preferences are active in this static concept" in new
        ) else new

        # Remove old cookie CSS blocks/classes likely responsible for the floating box.
        if path.suffix.lower() == ".css":
            new = re.sub(
                r"\.[^{]*(?:cookie-consent|cookie-banner|cookie-notice|cookie-popup|cookie-toast|cookie-preferences|cookie-widget|cookie-box)[^{]*\{[^}]*\}\s*",
                "",
                new,
                flags=re.I,
            )

        if write_if_changed(path, new, apply):
            if path.suffix.lower() == ".css":
                css_changed += 1
            elif path.suffix.lower() == ".js":
                js_changed += 1

    return css_changed, js_changed


def recipe_for(number: int, slug: str) -> dict[str, object]:
    variant = VARIANTS[number - 1]
    bg, fg, muted, accent, border = TONES[variant["tone"]]

    recipe = {
        "code": f"{number:02d}",
        "slug": slug,
        "bg": bg,
        "fg": fg,
        "muted": muted,
        "accent": accent,
        "border": border,
        "width": WIDTHS[variant["width"]],
        "padding": "8px 0" if variant["layout"] in {"micro", "minimal", "single-line"} else "10px 0",
        "fontSize": ".77rem" if variant["layout"] in {"micro", "minimal", "fine-print"} else ".81rem",
        "align": variant["align"],
        "layout": variant["layout"],
        "separator": variant["sep"],
        "marker": variant["mark"],
        "buttonStyle": variant["buttons"],
        "radius": "999px" if variant["buttons"] in {"pill-outline", "soft", "solid-first"} else "4px",
        "autoDelayMs": 9000 + number * 120,
    }

    return recipe


def render_cookie_js(recipe: dict[str, object]) -> str:
    config_json = json.dumps(recipe, ensure_ascii=False)

    js = r'''/* SOFIATI FOOTER COOKIE BAR START */
(() => {
  "use strict";

  const CONFIG = __CONFIG_JSON__;
  const STORAGE_KEY = "sofiatiFooterCookie:" + CONFIG.code;

  if (localStorage.getItem(STORAGE_KEY)) return;

  function saveConsent(mode) {
    const payload = {
      essential: true,
      analytics: mode === "all",
      experience: mode === "all",
      mode,
      updatedAt: new Date().toISOString()
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
    window.dispatchEvent(new CustomEvent("sofiati:cookie-consent", { detail: payload }));
  }

  function injectStyle() {
    const style = document.createElement("style");
    style.setAttribute("data-sofiati-footer-cookie-style", CONFIG.code);

    style.textContent = `
      .sf-footer-cookie-bar {
        --bar-bg: ${CONFIG.bg};
        --bar-fg: ${CONFIG.fg};
        --bar-muted: ${CONFIG.muted};
        --bar-accent: ${CONFIG.accent};
        --bar-border: ${CONFIG.border};
        --bar-width: ${CONFIG.width};
        --bar-padding: ${CONFIG.padding};
        --bar-font-size: ${CONFIG.fontSize};
        --bar-radius: ${CONFIG.radius};

        position: static;
        display: block;
        width: 100%;
        background: var(--bar-bg);
        color: var(--bar-fg);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      .sf-footer-cookie-bar[data-separator="gold-top"],
      .sf-footer-cookie-bar[data-separator="thin-top"],
      .sf-footer-cookie-bar[data-separator="soft-top"],
      .sf-footer-cookie-bar[data-separator="top-only"] {
        border-top: var(--bar-border);
      }

      .sf-footer-cookie-bar[data-separator="bottom-line"] {
        border-bottom: var(--bar-border);
      }

      .sf-footer-cookie-bar[data-separator="champagne"] {
        border-top: 1px solid color-mix(in srgb, var(--bar-accent) 38%, transparent);
      }

      .sf-footer-cookie-bar[data-separator="dashed"] {
        border-top: 1px dashed color-mix(in srgb, var(--bar-accent) 42%, transparent);
      }

      .sf-footer-cookie-bar[data-separator="motion"] {
        border-top: 1px solid color-mix(in srgb, var(--bar-accent) 18%, transparent);
        background-image: linear-gradient(90deg, color-mix(in srgb, var(--bar-accent) 7%, transparent), transparent 44%);
      }

      .sf-footer-cookie-bar[data-separator="scan"] {
        background-image: repeating-linear-gradient(180deg, color-mix(in srgb, var(--bar-accent) 8%, transparent) 0 1px, transparent 1px 8px);
      }

      .sf-footer-cookie-inner {
        width: var(--bar-width);
        margin-inline: auto;
        min-height: 36px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px 14px;
        padding: var(--bar-padding);
        text-align: ${CONFIG.align};
        font-size: var(--bar-font-size);
        line-height: 1.35;
      }

      .sf-footer-cookie-bar[data-layout="micro"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="minimal"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="single-line"] .sf-footer-cookie-inner {
        min-height: 28px;
        justify-content: center;
      }

      .sf-footer-cookie-bar[data-layout="center"],
      .sf-footer-cookie-bar[data-layout="centered"],
      .sf-footer-cookie-bar[data-layout="balanced"] {
        text-align: center;
      }

      .sf-footer-cookie-bar[data-layout="center"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="centered"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="balanced"] .sf-footer-cookie-inner {
        justify-content: center;
      }

      .sf-footer-cookie-bar[data-layout="ledger"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="fine-print"] .sf-footer-cookie-inner {
        min-height: 32px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        letter-spacing: -.02em;
      }

      .sf-footer-cookie-bar[data-layout="editorial"] strong {
        letter-spacing: .08em;
        text-transform: uppercase;
      }

      .sf-footer-cookie-bar[data-separator="left-rule"] .sf-footer-cookie-inner {
        border-left: 3px solid var(--bar-accent);
        padding-left: 12px;
      }

      .sf-footer-cookie-bar[data-separator="center-line"] .sf-footer-cookie-inner::before,
      .sf-footer-cookie-bar[data-separator="halo"] .sf-footer-cookie-inner::before,
      .sf-footer-cookie-bar[data-separator="glow"] .sf-footer-cookie-inner::before {
        content: "";
        width: 34px;
        height: 1px;
        background: var(--bar-accent);
        opacity: .72;
        flex: 0 0 auto;
      }

      .sf-footer-cookie-bar[data-separator="diagonal"] .sf-footer-cookie-inner {
        background-image: linear-gradient(112deg, transparent 0 48%, color-mix(in srgb, var(--bar-accent) 18%, transparent) 48% 49%, transparent 49%);
      }

      .sf-footer-cookie-bar[data-separator="step"] .sf-footer-cookie-inner {
        border-top: 1px solid color-mix(in srgb, var(--bar-accent) 26%, transparent);
      }

      .sf-footer-cookie-mark {
        width: 7px;
        height: 7px;
        flex: 0 0 auto;
        background: var(--bar-accent);
        opacity: .85;
        border-radius: 999px;
      }

      .sf-footer-cookie-bar[data-marker="none"] .sf-footer-cookie-mark {
        display: none;
      }

      .sf-footer-cookie-bar[data-marker="line"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="dash"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="signal"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="book"] .sf-footer-cookie-mark {
        width: 16px;
        height: 1px;
        border-radius: 0;
      }

      .sf-footer-cookie-bar[data-marker="diamond"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="check"] .sf-footer-cookie-mark {
        width: 7px;
        height: 7px;
        border-radius: 0;
        transform: rotate(45deg);
      }

      .sf-footer-cookie-bar[data-marker="leaf"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="sprig"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="curve"] .sf-footer-cookie-mark {
        width: 12px;
        height: 7px;
        border-radius: 100% 0 100% 0;
        transform: rotate(-24deg);
      }

      .sf-footer-cookie-bar[data-marker="bracket"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="signature"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="crest"] .sf-footer-cookie-mark {
        width: 8px;
        height: 12px;
        background: transparent;
        border-left: 1px solid var(--bar-accent);
        border-top: 1px solid var(--bar-accent);
        border-bottom: 1px solid var(--bar-accent);
        border-radius: 0;
      }

      .sf-footer-cookie-text {
        margin: 0;
        color: var(--bar-muted);
        flex: 1 1 auto;
      }

      .sf-footer-cookie-text strong {
        color: var(--bar-fg);
        font-weight: 850;
      }

      .sf-footer-cookie-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 6px;
        flex: 0 0 auto;
      }

      .sf-footer-cookie-actions button,
      .sf-footer-cookie-actions a {
        min-height: 26px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 3px 8px;
        border: 1px solid color-mix(in srgb, var(--bar-accent) 32%, transparent);
        border-radius: var(--bar-radius);
        background: transparent;
        color: var(--bar-fg);
        font: inherit;
        font-size: .75rem;
        font-weight: 800;
        text-decoration: none;
        cursor: pointer;
        white-space: nowrap;
      }

      .sf-footer-cookie-bar[data-button-style="solid-first"] .sf-footer-cookie-actions button:first-child,
      .sf-footer-cookie-bar[data-button-style="soft"] .sf-footer-cookie-actions button:first-child,
      .sf-footer-cookie-bar[data-button-style="pill-outline"] .sf-footer-cookie-actions button:first-child {
        background: var(--bar-accent);
        border-color: var(--bar-accent);
        color: #fff;
      }

      .sf-footer-cookie-bar[data-button-style="text"] .sf-footer-cookie-actions button,
      .sf-footer-cookie-bar[data-button-style="text"] .sf-footer-cookie-actions a {
        border: 0;
        padding-inline: 4px;
        text-decoration: underline;
        text-underline-offset: .25em;
        background: transparent;
        color: var(--bar-muted);
      }

      .sf-footer-cookie-bar[data-button-style="text"] .sf-footer-cookie-actions button:first-child {
        color: var(--bar-fg);
      }

      .sf-footer-cookie-actions button:focus-visible,
      .sf-footer-cookie-actions a:focus-visible {
        outline: 2px solid var(--bar-accent);
        outline-offset: 3px;
      }

      @media (max-width: 720px) {
        .sf-footer-cookie-inner {
          width: min(520px, calc(100% - 26px));
          display: grid;
          justify-items: start;
          justify-content: start;
          text-align: left;
          gap: 8px;
          padding-block: 9px;
        }

        .sf-footer-cookie-actions {
          justify-content: start;
          flex-wrap: wrap;
        }

        .sf-footer-cookie-actions button,
        .sf-footer-cookie-actions a {
          min-height: 28px;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function createBar() {
    injectStyle();

    const bar = document.createElement("section");
    bar.className = "sf-footer-cookie-bar";
    bar.setAttribute("data-cookie-bar", CONFIG.code);
    bar.setAttribute("data-layout", CONFIG.layout);
    bar.setAttribute("data-separator", CONFIG.separator);
    bar.setAttribute("data-marker", CONFIG.marker);
    bar.setAttribute("data-button-style", CONFIG.buttonStyle);
    bar.setAttribute("aria-label", "Cookie notice");

    bar.innerHTML = `
      <div class="sf-footer-cookie-inner">
        <span class="sf-footer-cookie-mark" aria-hidden="true"></span>
        <p class="sf-footer-cookie-text">
          <strong>Cookies:</strong> essential cookies keep this site working. Optional cookies help improve the experience.
        </p>
        <div class="sf-footer-cookie-actions">
          <button type="button" data-cookie-choice="all">Accept</button>
          <button type="button" data-cookie-choice="essential">Essential only</button>
          <a href="cookies.html">Cookies</a>
        </div>
      </div>
    `;

    bar.addEventListener("click", (event) => {
      const choice = event.target.closest("[data-cookie-choice]");
      if (!choice) return;

      const mode = choice.getAttribute("data-cookie-choice") === "all" ? "all" : "essential";
      saveConsent(mode);
      bar.remove();
    });

    const footers = Array.from(document.querySelectorAll("footer"));
    const footer = footers.length ? footers[footers.length - 1] : null;

    if (footer && footer.parentNode) {
      footer.insertAdjacentElement("afterend", bar);
    } else {
      document.body.appendChild(bar);
    }

    window.setTimeout(() => {
      if (!localStorage.getItem(STORAGE_KEY) && document.body.contains(bar)) {
        saveConsent("essential");
        bar.remove();
      }
    }, CONFIG.autoDelayMs);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createBar, { once: true });
  } else {
    createBar();
  }
})();
/* SOFIATI FOOTER COOKIE BAR END */
'''

    return js.replace("__CONFIG_JSON__", config_json)


def update_concept(concept: Path, apply: bool, all_pages: bool) -> tuple[int, int, int]:
    number = concept_number(concept)
    slug = CONCEPT_SLUGS[number - 1]
    recipe = recipe_for(number, slug)

    html_changed = 0
    target_pages = set(target_html_files(concept, all_pages))

    for page in all_html_files(concept):
        old = page.read_text(encoding="utf-8")
        cleaned = remove_old_cookie_html(old)
        new = inject_loader(cleaned) if page in target_pages else cleaned

        if write_if_changed(page, new, apply):
            html_changed += 1

    css_changed, old_js_cleaned = clean_asset_files(concept, apply)

    js_path = concept / "assets" / "js" / JS_FILENAME
    js_content = render_cookie_js(recipe)
    new_js_written = 1 if write_if_changed(js_path, js_content, apply) else 0

    return html_changed, css_changed, old_js_cleaned + new_js_written


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Write files. Without this, dry run only.")
    parser.add_argument("--force", action="store_true", help="Allow running on a dirty Git tree.")
    parser.add_argument("--all-pages", action="store_true", help="Inject loader on every HTML page, not only index.html.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    concepts_dir = root / "concepts"

    if git_is_dirty(root) and not args.force:
        print("Git tree has changes. Commit/stash first, or rerun with --force.")
        return

    total_html = 0
    total_css = 0
    total_js = 0

    audit = [
        "# Sofiati Footer Cookie Bar Audit",
        "",
        "- Old floating cookie boxes removed.",
        "- Bars are inserted after the final footer element.",
        "- Bars are not fixed, floating, modal or invasive.",
        "- Default injection: index.html only.",
        "- If --all-pages is used, loader is added to every HTML page.",
        "- If the visitor does nothing, essential-only is saved automatically.",
        "",
    ]

    for concept in concept_dirs(concepts_dir):
        html_count, css_count, js_count = update_concept(concept, args.apply, args.all_pages)

        total_html += html_count
        total_css += css_count
        total_js += js_count

        number = concept_number(concept)
        slug = CONCEPT_SLUGS[number - 1]
        recipe = recipe_for(number, slug)

        audit.extend([
            f"## {concept.name}",
            "",
            f"- Recipe: `{slug}`",
            f"- Layout: `{recipe['layout']}`",
            f"- Separator: `{recipe['separator']}`",
            f"- Marker: `{recipe['marker']}`",
            f"- Button style: `{recipe['buttonStyle']}`",
            f"- Background: `{recipe['bg']}`",
            f"- Accent: `{recipe['accent']}`",
            f"- Width: `{recipe['width']}`",
            f"- Auto fallback: `essential-only after {recipe['autoDelayMs']}ms`",
            f"- Placement: `after final footer element`",
            f"- Loader target: `{'all pages' if args.all_pages else 'index.html only'}`",
            f"- HTML changed: `{html_count}`",
            f"- CSS cleaned: `{css_count}`",
            f"- JS cleaned/written: `{js_count}`",
            "",
        ])

        print(f"{'Would update' if not args.apply else 'Updated'} {concept.name}: html={html_count}, css={css_count}, js={js_count}")

    audit_path = root / "audit" / "footer-cookie-bar-audit.md"

    if args.apply:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text("\n".join(audit).rstrip() + "\n", encoding="utf-8")

    if args.apply:
        print(f"Done. HTML changed: {total_html}, CSS cleaned: {total_css}, JS cleaned/written: {total_js}")
        print("Audit written to audit/footer-cookie-bar-audit.md")
    else:
        print(f"Dry run complete. HTML would change: {total_html}, CSS would clean: {total_css}, JS would clean/write: {total_js}")
        print("Rerun with --apply --force to write files.")


if __name__ == "__main__":
    main()
