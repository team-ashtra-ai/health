#!/usr/bin/env python3
"""
Refactor Sofiati cookie notices across all 50 concepts.

Goal:
- Same cookie notice meaning/content across all concepts.
- 50 visibly different cookie notice designs.
- Concept-specific colours, spacing, layout, icons, radius, motion and position.
- Accessible buttons and preference panel.
- Works without React/frameworks.
- Injects the notice into each concept's HTML pages before </body>.
- Adds a marked CSS block to each concept stylesheet.
- Adds a marked JS block to each concept JS file.

Run dry:
  python3 scripts/refactor_sofiati_cookie_notices.py

Apply:
  python3 scripts/refactor_sofiati_cookie_notices.py --apply --force
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


HTML_START = "<!-- SOFIATI COOKIE NOTICE V1 START -->"
HTML_END = "<!-- SOFIATI COOKIE NOTICE V1 END -->"

CSS_START = "/* SOFIATI COOKIE NOTICE V1 START */"
CSS_END = "/* SOFIATI COOKIE NOTICE V1 END */"

JS_START = "/* SOFIATI COOKIE NOTICE V1 START */"
JS_END = "/* SOFIATI COOKIE NOTICE V1 END */"


@dataclass(frozen=True)
class CookieRecipe:
    number: int
    slug: str
    layout: str
    bg: str
    fg: str
    muted: str
    accent: str
    accent_2: str
    border: str
    shadow: str
    width: str
    radius: str
    padding: str
    gap: str
    title_size: str
    text_size: str
    button_radius: str
    icon_style: str
    align: str
    motion: str


R = CookieRecipe


COOKIE_RECIPES: dict[int, CookieRecipe] = {
    1: R(1, "inspire", "bottom-editorial", "linear-gradient(135deg,#252321,#354139)", "#F8F7F2", "rgba(248,247,242,.74)", "#C9A56A", "#A2AEA0", "1px solid rgba(201,165,106,.34)", "0 24px 70px rgba(0,0,0,.24)", "min(1040px,calc(100% - 32px))", "18px", "18px", "18px", "1.04rem", ".94rem", "999px", "dot", "left", "rise"),
    2: R(2, "empower", "bottom-sheet", "linear-gradient(180deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.66)", "#879588", "#C9A56A", "1px solid rgba(127,141,130,.26)", "0 -18px 60px rgba(37,35,33,.11)", "100%", "24px 24px 0 0", "20px", "18px", "1.05rem", ".95rem", "999px", "leaf", "left", "slide-up"),
    3: R(3, "enhance", "right-rail", "#FBFAF6", "#252321", "rgba(37,35,33,.66)", "#7F8D82", "#9A6B35", "1px solid rgba(37,35,33,.14)", "0 24px 70px rgba(37,35,33,.14)", "360px", "8px", "18px", "14px", "1rem", ".92rem", "6px", "ledger", "left", "slide-left"),
    4: R(4, "renew", "floating-left", "linear-gradient(135deg,#EEF1EA,#F8F7F2)", "#252321", "rgba(37,35,33,.66)", "#879588", "#DAB26F", "1px solid rgba(127,141,130,.28)", "0 22px 60px rgba(37,35,33,.13)", "390px", "26px", "18px", "14px", "1.04rem", ".94rem", "999px", "sprig", "left", "rise"),
    5: R(5, "elevate", "center-card", "linear-gradient(135deg,#F4EFE5,#FFFFFF)", "#252321", "rgba(37,35,33,.66)", "#9A6B35", "#C9A56A", "1px solid rgba(154,107,53,.24)", "0 28px 90px rgba(37,35,33,.18)", "440px", "30px", "22px", "18px", "1.15rem", ".95rem", "999px", "diamond", "center", "scale-in"),
    6: R(6, "refine", "mini-toast", "#FFFFFF", "#252321", "rgba(37,35,33,.62)", "#7F8D82", "#A2AEA0", "1px solid rgba(37,35,33,.12)", "0 18px 48px rgba(37,35,33,.12)", "340px", "4px", "14px", "10px", ".96rem", ".88rem", "4px", "dash", "left", "fade"),
    7: R(7, "glow", "bottom-glass", "rgba(255,255,255,.82)", "#252321", "rgba(37,35,33,.68)", "#C9A56A", "#A2AEA0", "1px solid rgba(201,165,106,.22)", "0 24px 70px rgba(37,35,33,.14)", "min(980px,calc(100% - 34px))", "28px", "18px", "18px", "1.05rem", ".94rem", "999px", "sun", "left", "rise"),
    8: R(8, "balance", "split-bottom", "linear-gradient(90deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.66)", "#879588", "#C9A56A", "1px solid rgba(127,141,130,.26)", "0 18px 54px rgba(37,35,33,.12)", "min(1080px,calc(100% - 36px))", "18px", "18px", "18px", "1.02rem", ".94rem", "999px", "bracket", "left", "rise"),
    9: R(9, "radiance", "top-ribbon", "linear-gradient(135deg,#FFFDF8,#F4EFE5)", "#252321", "rgba(37,35,33,.66)", "#C9A56A", "#879588", "1px solid rgba(201,165,106,.28)", "0 14px 40px rgba(37,35,33,.1)", "100%", "0", "14px 22px", "16px", "1rem", ".9rem", "999px", "ray", "left", "slide-down"),
    10: R(10, "essence", "minimal-line", "#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#7F8D82", "#C9A56A", "0", "none", "min(920px,calc(100% - 32px))", "0", "16px 0", "12px", ".96rem", ".88rem", "0", "none", "left", "fade"),
    11: R(11, "bloom", "botanical-card", "linear-gradient(135deg,#EAF0E8,#F8F7F2)", "#252321", "rgba(37,35,33,.66)", "#879588", "#9A6B35", "1px solid rgba(127,141,130,.28)", "0 22px 64px rgba(37,35,33,.13)", "400px", "28px", "20px", "14px", "1.06rem", ".94rem", "999px", "sprig", "left", "rise"),
    12: R(12, "vital", "progress-strip", "linear-gradient(135deg,#334339,#F8F7F2)", "#252321", "rgba(37,35,33,.7)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.22)", "0 18px 56px rgba(37,35,33,.13)", "min(1000px,calc(100% - 34px))", "16px", "16px", "16px", "1rem", ".92rem", "999px", "arrow", "left", "rise"),
    13: R(13, "poise", "editorial-card", "linear-gradient(180deg,#252321,#313833)", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "#A2AEA0", "1px solid rgba(201,165,106,.26)", "0 28px 80px rgba(0,0,0,.24)", "430px", "0", "22px", "16px", "1.1rem", ".94rem", "0", "diamond", "left", "slide-left"),
    14: R(14, "aura", "soft-modal", "radial-gradient(circle at 80% 12%,rgba(201,165,106,.18),transparent 38%),#F8F7F2", "#252321", "rgba(37,35,33,.66)", "#C9A56A", "#879588", "1px solid rgba(201,165,106,.24)", "0 30px 90px rgba(37,35,33,.18)", "430px", "32px", "22px", "18px", "1.1rem", ".95rem", "999px", "halo", "center", "scale-in"),
    15: R(15, "clarity", "clean-bottom", "#FFFFFF", "#252321", "rgba(37,35,33,.7)", "#7F8D82", "#9A6B35", "1px solid rgba(37,35,33,.14)", "0 -12px 42px rgba(37,35,33,.09)", "100%", "0", "16px 24px", "16px", "1rem", ".92rem", "6px", "check", "left", "slide-up"),
    16: R(16, "grace", "curved-card", "linear-gradient(180deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.66)", "#A2AEA0", "#C9A56A", "1px solid rgba(162,174,160,.3)", "0 22px 64px rgba(37,35,33,.12)", "390px", "34px 8px 34px 34px", "20px", "14px", "1.05rem", ".94rem", "999px", "curve", "left", "rise"),
    17: R(17, "sculpt", "geometric-card", "linear-gradient(135deg,#252321,#3D372F)", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "#879588", "1px solid rgba(201,165,106,.3)", "0 26px 76px rgba(0,0,0,.26)", "400px", "4px 28px 4px 28px", "20px", "14px", "1.05rem", ".93rem", "4px", "angle", "left", "slide-left"),
    18: R(18, "lumin", "glass-corner", "rgba(255,255,255,.76)", "#252321", "rgba(37,35,33,.68)", "#C9A56A", "#A2AEA0", "1px solid rgba(255,255,255,.48)", "0 24px 70px rgba(37,35,33,.14)", "390px", "26px", "18px", "14px", "1.04rem", ".94rem", "999px", "ray", "left", "rise"),
    19: R(19, "verda", "deep-card", "linear-gradient(135deg,#2E3A32,#506052)", "#F8F7F2", "rgba(248,247,242,.72)", "#DAB26F", "#A2AEA0", "1px solid rgba(218,178,111,.28)", "0 24px 70px rgba(0,0,0,.24)", "410px", "22px", "20px", "14px", "1.05rem", ".94rem", "999px", "sprig", "left", "rise"),
    20: R(20, "halo", "radial-card", "radial-gradient(circle at 50% 0%,rgba(201,165,106,.2),transparent 44%),#252321", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "#879588", "1px solid rgba(201,165,106,.26)", "0 26px 82px rgba(0,0,0,.24)", "420px", "999px 999px 28px 28px", "26px", "16px", "1.08rem", ".94rem", "999px", "halo", "center", "scale-in"),
    21: R(21, "calm", "quiet-card", "#F8F7F2", "#252321", "rgba(37,35,33,.62)", "#A2AEA0", "#879588", "1px solid rgba(162,174,160,.28)", "0 18px 48px rgba(37,35,33,.1)", "370px", "18px", "16px", "12px", "1rem", ".9rem", "999px", "dash", "left", "fade"),
    22: R(22, "precision", "ledger-panel", "#FFFFFF", "#252321", "rgba(37,35,33,.7)", "#7F8D82", "#9A6B35", "1px solid rgba(37,35,33,.16)", "0 18px 48px rgba(37,35,33,.1)", "380px", "2px", "16px", "12px", ".98rem", ".9rem", "2px", "ledger", "left", "slide-left"),
    23: R(23, "ritual", "step-card", "linear-gradient(180deg,#F4EFE5,#FBFAF6)", "#252321", "rgba(37,35,33,.66)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.24)", "0 22px 60px rgba(37,35,33,.12)", "400px", "24px", "20px", "14px", "1.04rem", ".94rem", "999px", "step", "left", "rise"),
    24: R(24, "signal", "interface-toast", "linear-gradient(135deg,#202524,#313A35)", "#F8F7F2", "rgba(248,247,242,.72)", "#A2AEA0", "#C9A56A", "1px solid rgba(162,174,160,.28)", "0 20px 60px rgba(0,0,0,.24)", "390px", "10px", "16px", "12px", ".98rem", ".9rem", "6px", "signal", "left", "slide-left"),
    25: R(25, "align", "aligned-strip", "#FBFBF8", "#252321", "rgba(37,35,33,.66)", "#879588", "#C9A56A", "1px solid rgba(127,141,130,.24)", "0 16px 46px rgba(37,35,33,.09)", "min(980px,calc(100% - 32px))", "10px", "16px", "16px", "1rem", ".92rem", "8px", "line", "left", "rise"),
    26: R(26, "vivant", "animated-card", "linear-gradient(135deg,#EEF1EA,#FFFFFF 55%,#F4EFE5)", "#252321", "rgba(37,35,33,.66)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.22)", "0 24px 70px rgba(37,35,33,.12)", "410px", "22px", "18px", "14px", "1.06rem", ".94rem", "999px", "arrow", "left", "rise"),
    27: R(27, "form", "shape-card", "linear-gradient(135deg,#2B2B27,#40382F)", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "#A2AEA0", "1px solid rgba(201,165,106,.28)", "0 24px 72px rgba(0,0,0,.25)", "400px", "4px 34px 4px 34px", "20px", "14px", "1.05rem", ".94rem", "4px", "angle", "left", "slide-left"),
    28: R(28, "pure", "text-line", "#FFFFFF", "#252321", "rgba(37,35,33,.6)", "#A2AEA0", "#879588", "0", "none", "min(920px,calc(100% - 30px))", "0", "14px 0", "12px", ".96rem", ".88rem", "0", "none", "left", "fade"),
    29: R(29, "solace", "comfort-card", "linear-gradient(180deg,#F8F7F2,#F1EEE7)", "#252321", "rgba(37,35,33,.66)", "#879588", "#C9A56A", "1px solid rgba(127,141,130,.24)", "0 22px 60px rgba(37,35,33,.12)", "395px", "28px", "20px", "14px", "1.04rem", ".94rem", "999px", "circle", "left", "rise"),
    30: R(30, "method", "wizard-card", "#FBFAF6", "#252321", "rgba(37,35,33,.66)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.24)", "0 20px 58px rgba(37,35,33,.12)", "410px", "14px", "18px", "14px", "1.02rem", ".92rem", "8px", "step", "left", "slide-left"),
    31: R(31, "evolve", "progress-card", "linear-gradient(135deg,#EEF1EA,#F8F7F2 60%,#E7D7BA)", "#252321", "rgba(37,35,33,.66)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.22)", "0 22px 64px rgba(37,35,33,.13)", "420px", "22px", "20px", "14px", "1.04rem", ".94rem", "999px", "arrow", "left", "rise"),
    32: R(32, "serene", "serene-sheet", "linear-gradient(180deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.62)", "#A2AEA0", "#879588", "1px solid rgba(162,174,160,.24)", "0 -14px 50px rgba(37,35,33,.1)", "100%", "28px 28px 0 0", "18px", "16px", "1.02rem", ".92rem", "999px", "dash", "center", "slide-up"),
    33: R(33, "elan", "bold-editorial", "linear-gradient(135deg,#252321,#2E3A32)", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "#A2AEA0", "1px solid rgba(201,165,106,.28)", "0 28px 80px rgba(0,0,0,.25)", "450px", "0", "22px", "16px", "1.14rem", ".94rem", "0", "diamond", "left", "slide-left"),
    34: R(34, "flora", "flora-card", "linear-gradient(135deg,#E9F0E6,#F8F7F2)", "#252321", "rgba(37,35,33,.66)", "#879588", "#9A6B35", "1px solid rgba(127,141,130,.28)", "0 22px 64px rgba(37,35,33,.12)", "410px", "30px", "20px", "14px", "1.05rem", ".94rem", "999px", "sprig", "left", "rise"),
    35: R(35, "atelier", "studio-panel", "#FBFAF6", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.24)", "0 22px 64px rgba(37,35,33,.12)", "430px", "6px", "20px", "14px", "1.08rem", ".94rem", "6px", "bracket", "left", "slide-left"),
    36: R(36, "lumina", "light-panel", "radial-gradient(circle at 70% 22%,rgba(201,165,106,.18),transparent 36%),#FFFFFF", "#252321", "rgba(37,35,33,.66)", "#C9A56A", "#879588", "1px solid rgba(201,165,106,.22)", "0 24px 70px rgba(37,35,33,.12)", "410px", "28px", "20px", "14px", "1.05rem", ".94rem", "999px", "ray", "left", "rise"),
    37: R(37, "vellum", "paper-note", "linear-gradient(180deg,#FBFAF6,#F4EFE5)", "#252321", "rgba(37,35,33,.66)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.22)", "0 18px 50px rgba(37,35,33,.1)", "390px", "2px", "18px", "12px", ".98rem", ".9rem", "2px", "ledger", "left", "fade"),
    38: R(38, "origin", "grounded-card", "linear-gradient(135deg,#2B312D,#445044)", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "#A2AEA0", "1px solid rgba(201,165,106,.26)", "0 22px 64px rgba(0,0,0,.24)", "400px", "20px", "20px", "14px", "1.04rem", ".94rem", "999px", "root", "left", "rise"),
    39: R(39, "kindred", "warm-card", "linear-gradient(180deg,#F8F7F2,#F1EEE7)", "#252321", "rgba(37,35,33,.66)", "#A2AEA0", "#9A6B35", "1px solid rgba(162,174,160,.24)", "0 22px 60px rgba(37,35,33,.12)", "405px", "26px", "20px", "14px", "1.04rem", ".94rem", "999px", "circle", "left", "rise"),
    40: R(40, "noble", "formal-modal", "linear-gradient(135deg,#201F1E,#302A23)", "#F8F7F2", "rgba(248,247,242,.72)", "#DAB26F", "#A2AEA0", "1px solid rgba(218,178,111,.3)", "0 30px 90px rgba(0,0,0,.28)", "440px", "0 34px 0 34px", "24px", "18px", "1.14rem", ".95rem", "0", "diamond", "center", "scale-in"),
    41: R(41, "vista", "wide-strip", "linear-gradient(90deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.66)", "#879588", "#C9A56A", "1px solid rgba(127,141,130,.24)", "0 18px 54px rgba(37,35,33,.1)", "min(1180px,calc(100% - 42px))", "12px", "16px", "18px", "1rem", ".92rem", "8px", "horizon", "left", "rise"),
    42: R(42, "softline", "softline-card", "linear-gradient(180deg,#F8F7F2,#EEF1EA)", "#252321", "rgba(37,35,33,.64)", "#A2AEA0", "#879588", "1px solid rgba(162,174,160,.28)", "0 22px 60px rgba(37,35,33,.12)", "400px", "36px", "20px", "14px", "1.04rem", ".94rem", "999px", "curve", "left", "rise"),
    43: R(43, "meridian", "path-selector", "#FBFBF8", "#252321", "rgba(37,35,33,.66)", "#879588", "#9A6B35", "1px solid rgba(127,141,130,.24)", "0 20px 56px rgba(37,35,33,.1)", "420px", "18px", "20px", "14px", "1.04rem", ".92rem", "999px", "compass", "left", "slide-left"),
    44: R(44, "safeguard", "secure-panel", "#FFFFFF", "#252321", "rgba(37,35,33,.7)", "#7F8D82", "#9A6B35", "1px solid rgba(37,35,33,.16)", "0 18px 52px rgba(37,35,33,.11)", "390px", "10px", "18px", "12px", "1rem", ".92rem", "6px", "shield", "left", "slide-left"),
    45: R(45, "silhouette", "dark-minimal", "linear-gradient(135deg,#252321,#354139)", "#F8F7F2", "rgba(248,247,242,.68)", "#C9A56A", "#A2AEA0", "1px solid rgba(201,165,106,.22)", "0 22px 64px rgba(0,0,0,.24)", "380px", "0 28px 0 28px", "20px", "14px", "1.04rem", ".92rem", "0", "silhouette", "left", "fade"),
    46: R(46, "curate", "choice-tabs", "linear-gradient(135deg,#F4EFE5,#FFFFFF)", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.22)", "0 22px 64px rgba(37,35,33,.12)", "430px", "24px", "20px", "14px", "1.05rem", ".94rem", "999px", "bracket", "left", "rise"),
    47: R(47, "proof", "proof-ledger", "#FBFBF8", "#252321", "rgba(37,35,33,.68)", "#7F8D82", "#9A6B35", "1px solid rgba(37,35,33,.16)", "0 18px 50px rgba(37,35,33,.1)", "400px", "4px", "18px", "12px", "1rem", ".9rem", "4px", "check", "left", "slide-left"),
    48: R(48, "signature", "signature-panel", "linear-gradient(180deg,#F8F7F2,#F4EFE5)", "#252321", "rgba(37,35,33,.64)", "#9A6B35", "#879588", "1px solid rgba(154,107,53,.24)", "0 24px 70px rgba(37,35,33,.12)", "440px", "28px 28px 6px 28px", "22px", "16px", "1.08rem", ".94rem", "999px", "signature", "center", "scale-in"),
    49: R(49, "wisdom", "education-card", "linear-gradient(135deg,#252321,#313833)", "#F8F7F2", "rgba(248,247,242,.72)", "#C9A56A", "#A2AEA0", "1px solid rgba(201,165,106,.26)", "0 24px 72px rgba(0,0,0,.24)", "420px", "16px", "20px", "14px", "1.05rem", ".94rem", "999px", "book", "left", "rise"),
    50: R(50, "sovereign", "flagship-modal", "linear-gradient(135deg,#1F1E1D,#334139 58%,#9A6B35)", "#F8F7F2", "rgba(248,247,242,.74)", "#DAB26F", "#A2AEA0", "1px solid rgba(218,178,111,.34)", "0 34px 100px rgba(0,0,0,.32)", "460px", "34px", "26px", "18px", "1.16rem", ".96rem", "999px", "crest", "center", "scale-in"),
}


def concept_dirs(concepts_dir: Path) -> list[Path]:
    if not concepts_dir.exists():
        raise FileNotFoundError(f"Missing concepts directory: {concepts_dir}")
    return sorted(
        p for p in concepts_dir.iterdir()
        if p.is_dir() and re.match(r"^\d{2}-", p.name)
    )


def concept_number(concept: Path) -> int:
    return int(concept.name.split("-", 1)[0])


def find_css_file(concept: Path) -> Path:
    candidates = [
        concept / "assets" / "css" / "style.css",
        concept / "assets" / "css" / "main.css",
        concept / "css" / "style.css",
        concept / "style.css",
    ]
    for path in candidates:
        if path.exists():
            return path
    path = concept / "assets" / "css" / "style.css"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


def find_js_file(concept: Path) -> Path:
    candidates = [
        concept / "assets" / "js" / "main.js",
        concept / "assets" / "js" / "script.js",
        concept / "js" / "main.js",
        concept / "script.js",
    ]
    for path in candidates:
        if path.exists():
            return path
    path = concept / "assets" / "js" / "main.js"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch()
    return path


def page_files(concept: Path) -> list[Path]:
    return sorted(
        p for p in concept.glob("*.html")
        if p.is_file()
    )


def replace_between_markers(text: str, start: str, end: str, block: str) -> str:
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if pattern.search(text):
        return pattern.sub(block.strip(), text).rstrip() + "\n"
    return text.rstrip() + "\n\n" + block.strip() + "\n"


def inject_html_block(text: str, block: str) -> str:
    pattern = re.compile(re.escape(HTML_START) + r".*?" + re.escape(HTML_END), re.S)
    text = pattern.sub("", text).rstrip() + "\n"

    if "</body>" in text:
        return text.replace("</body>", block.strip() + "\n</body>")
    return text.rstrip() + "\n" + block.strip() + "\n"


def render_cookie_html(recipe: CookieRecipe, code: str) -> str:
    return f"""
{HTML_START}
<section
  class="sofiati-cookie-notice sofiati-cookie-{code} sofiati-cookie-layout-{recipe.layout} sofiati-cookie-motion-{recipe.motion}"
  data-cookie-notice
  data-cookie-key="sofiatiCookieConsent:{code}"
  data-cookie-visible="false"
  role="region"
  aria-label="Cookie preferences"
>
  <div class="sofiati-cookie-shell">
    <div class="sofiati-cookie-icon" aria-hidden="true"></div>

    <div class="sofiati-cookie-copy">
      <p class="sofiati-cookie-kicker">Cookie preferences</p>
      <h2>Choose how this site may use cookies</h2>
      <p>
        We use essential cookies to keep the website working. With your permission,
        optional cookies may help improve the experience and understand general site use.
      </p>
    </div>

    <div class="sofiati-cookie-actions" aria-label="Cookie actions">
      <button type="button" class="sofiati-cookie-btn sofiati-cookie-btn-primary" data-cookie-action="accept">
        Accept all
      </button>
      <button type="button" class="sofiati-cookie-btn sofiati-cookie-btn-secondary" data-cookie-action="reject">
        Reject optional
      </button>
      <button type="button" class="sofiati-cookie-btn sofiati-cookie-btn-ghost" data-cookie-action="manage" aria-expanded="false">
        Manage choices
      </button>
    </div>

    <div class="sofiati-cookie-panel" data-cookie-panel hidden>
      <div class="sofiati-cookie-choice">
        <div>
          <strong>Essential cookies</strong>
          <span>Required for the website to work.</span>
        </div>
        <span class="sofiati-cookie-always">Always on</span>
      </div>

      <label class="sofiati-cookie-choice">
        <span>
          <strong>Analytics cookies</strong>
          <span>Help understand general site use if analytics are enabled.</span>
        </span>
        <input type="checkbox" data-cookie-toggle="analytics">
      </label>

      <label class="sofiati-cookie-choice">
        <span>
          <strong>Experience cookies</strong>
          <span>Help remember simple preferences where available.</span>
        </span>
        <input type="checkbox" data-cookie-toggle="experience">
      </label>

      <div class="sofiati-cookie-panel-actions">
        <button type="button" class="sofiati-cookie-btn sofiati-cookie-btn-primary" data-cookie-action="save">
          Save choices
        </button>
        <a href="cookies.html">Cookies policy</a>
        <a href="privacy.html">Privacy information</a>
      </div>
    </div>
  </div>
</section>
{HTML_END}
"""


def render_cookie_css(recipe: CookieRecipe, code: str) -> str:
    return f"""
{CSS_START}
.sofiati-cookie-notice {{
  --cookie-bg: #F8F7F2;
  --cookie-fg: #252321;
  --cookie-muted: rgba(37,35,33,.66);
  --cookie-accent: #879588;
  --cookie-accent-2: #C9A56A;
  --cookie-border: 1px solid rgba(37,35,33,.14);
  --cookie-shadow: 0 20px 60px rgba(37,35,33,.14);
  --cookie-width: 400px;
  --cookie-radius: 22px;
  --cookie-padding: 18px;
  --cookie-gap: 14px;
  --cookie-title-size: 1.05rem;
  --cookie-text-size: .94rem;
  --cookie-button-radius: 999px;

  position: fixed;
  z-index: 9999;
  color: var(--cookie-fg);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

.sofiati-cookie-notice[data-cookie-visible="false"] {{
  display: none;
}}

.sofiati-cookie-shell {{
  width: var(--cookie-width);
  max-width: calc(100vw - 28px);
  display: grid;
  gap: var(--cookie-gap);
  padding: var(--cookie-padding);
  background: var(--cookie-bg);
  color: var(--cookie-fg);
  border: var(--cookie-border);
  border-radius: var(--cookie-radius);
  box-shadow: var(--cookie-shadow);
  backdrop-filter: blur(18px);
}}

.sofiati-cookie-icon {{
  width: 32px;
  height: 32px;
  color: var(--cookie-accent);
  position: relative;
}}

.sofiati-cookie-icon::before,
.sofiati-cookie-icon::after {{
  content: "";
  position: absolute;
  inset: 0;
}}

.sofiati-cookie-icon::before {{
  border: 1px solid currentColor;
  border-radius: 999px;
}}

.sofiati-cookie-icon::after {{
  inset: 10px;
  background: currentColor;
  border-radius: 999px;
}}

.sofiati-cookie-kicker {{
  margin: 0 0 4px;
  color: var(--cookie-accent);
  font-size: .72rem;
  font-weight: 900;
  letter-spacing: .14em;
  text-transform: uppercase;
}}

.sofiati-cookie-copy h2 {{
  margin: 0;
  color: var(--cookie-fg);
  font-size: var(--cookie-title-size);
  line-height: 1.14;
  letter-spacing: -.01em;
}}

.sofiati-cookie-copy p {{
  margin: 8px 0 0;
  color: var(--cookie-muted);
  font-size: var(--cookie-text-size);
  line-height: 1.5;
}}

.sofiati-cookie-actions,
.sofiati-cookie-panel-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}}

.sofiati-cookie-btn {{
  min-height: 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 13px;
  border-radius: var(--cookie-button-radius);
  border: 1px solid color-mix(in srgb, var(--cookie-accent) 34%, transparent);
  background: transparent;
  color: var(--cookie-fg);
  font: inherit;
  font-size: .9rem;
  font-weight: 800;
  cursor: pointer;
}}

.sofiati-cookie-btn-primary {{
  background: var(--cookie-accent);
  color: #fff;
  border-color: var(--cookie-accent);
}}

.sofiati-cookie-btn-secondary {{
  background: color-mix(in srgb, var(--cookie-accent) 10%, transparent);
}}

.sofiati-cookie-btn-ghost {{
  border-color: transparent;
  color: var(--cookie-muted);
  text-decoration: underline;
  text-underline-offset: .25em;
}}

.sofiati-cookie-btn:focus-visible,
.sofiati-cookie-panel-actions a:focus-visible {{
  outline: 2px solid var(--cookie-accent-2);
  outline-offset: 3px;
}}

.sofiati-cookie-panel {{
  display: grid;
  gap: 10px;
  padding-top: 12px;
  border-top: 1px solid color-mix(in srgb, var(--cookie-accent) 22%, transparent);
}}

.sofiati-cookie-choice {{
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 14px;
  padding: 10px 0;
  border-bottom: 1px solid color-mix(in srgb, var(--cookie-fg) 10%, transparent);
}}

.sofiati-cookie-choice strong {{
  display: block;
  color: var(--cookie-fg);
  font-size: .9rem;
}}

.sofiati-cookie-choice span span {{
  display: block;
  margin-top: 2px;
  color: var(--cookie-muted);
  font-size: .82rem;
  line-height: 1.35;
}}

.sofiati-cookie-choice input {{
  width: 42px;
  height: 24px;
  accent-color: var(--cookie-accent);
}}

.sofiati-cookie-always {{
  color: var(--cookie-accent);
  font-size: .78rem;
  font-weight: 900;
  text-transform: uppercase;
  letter-spacing: .08em;
}}

.sofiati-cookie-panel-actions a {{
  color: var(--cookie-muted);
  font-size: .86rem;
  text-decoration: underline;
  text-underline-offset: .25em;
}}

.sofiati-cookie-layout-bottom-editorial,
.sofiati-cookie-layout-bottom-glass,
.sofiati-cookie-layout-split-bottom,
.sofiati-cookie-layout-aligned-strip,
.sofiati-cookie-layout-wide-strip {{
  left: 50%;
  bottom: 18px;
  transform: translateX(-50%);
}}

.sofiati-cookie-layout-bottom-editorial .sofiati-cookie-shell,
.sofiati-cookie-layout-bottom-glass .sofiati-cookie-shell,
.sofiati-cookie-layout-split-bottom .sofiati-cookie-shell,
.sofiati-cookie-layout-aligned-strip .sofiati-cookie-shell,
.sofiati-cookie-layout-wide-strip .sofiati-cookie-shell {{
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
}}

.sofiati-cookie-layout-bottom-sheet,
.sofiati-cookie-layout-serene-sheet,
.sofiati-cookie-layout-clean-bottom {{
  left: 0;
  right: 0;
  bottom: 0;
}}

.sofiati-cookie-layout-bottom-sheet .sofiati-cookie-shell,
.sofiati-cookie-layout-serene-sheet .sofiati-cookie-shell,
.sofiati-cookie-layout-clean-bottom .sofiati-cookie-shell {{
  width: 100%;
  max-width: none;
  border-left: 0;
  border-right: 0;
  border-bottom: 0;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
}}

.sofiati-cookie-layout-right-rail,
.sofiati-cookie-layout-editorial-card,
.sofiati-cookie-layout-geometric-card,
.sofiati-cookie-layout-interface-toast,
.sofiati-cookie-layout-wizard-card,
.sofiati-cookie-layout-studio-panel,
.sofiati-cookie-layout-secure-panel,
.sofiati-cookie-layout-proof-ledger,
.sofiati-cookie-layout-education-card {{
  right: 18px;
  bottom: 18px;
}}

.sofiati-cookie-layout-floating-left,
.sofiati-cookie-layout-botanical-card,
.sofiati-cookie-layout-deep-card,
.sofiati-cookie-layout-comfort-card,
.sofiati-cookie-layout-flora-card,
.sofiati-cookie-layout-grounded-card,
.sofiati-cookie-layout-warm-card,
.sofiati-cookie-layout-softline-card {{
  left: 18px;
  bottom: 18px;
}}

.sofiati-cookie-layout-center-card,
.sofiati-cookie-layout-soft-modal,
.sofiati-cookie-layout-radial-card,
.sofiati-cookie-layout-formal-modal,
.sofiati-cookie-layout-signature-panel,
.sofiati-cookie-layout-flagship-modal {{
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
}}

.sofiati-cookie-layout-top-ribbon {{
  left: 0;
  right: 0;
  top: 0;
}}

.sofiati-cookie-layout-top-ribbon .sofiati-cookie-shell {{
  width: 100%;
  max-width: none;
  border-radius: 0;
  border-left: 0;
  border-right: 0;
  border-top: 0;
  grid-template-columns: auto minmax(0, 1fr) auto;
  align-items: center;
}}

.sofiati-cookie-layout-mini-toast,
.sofiati-cookie-layout-minimal-line,
.sofiati-cookie-layout-text-line,
.sofiati-cookie-layout-quiet-card,
.sofiati-cookie-layout-paper-note,
.sofiati-cookie-layout-dark-minimal {{
  right: 18px;
  bottom: 18px;
}}

.sofiati-cookie-layout-minimal-line .sofiati-cookie-shell,
.sofiati-cookie-layout-text-line .sofiati-cookie-shell {{
  box-shadow: none;
  border-top: 1px solid color-mix(in srgb, var(--cookie-accent) 38%, transparent);
  border-radius: 0;
}}

.sofiati-cookie-layout-progress-strip,
.sofiati-cookie-layout-step-card,
.sofiati-cookie-layout-progress-card,
.sofiati-cookie-layout-path-selector,
.sofiati-cookie-layout-choice-tabs {{
  right: 18px;
  bottom: 18px;
}}

.sofiati-cookie-layout-glass-corner,
.sofiati-cookie-layout-light-panel {{
  right: 18px;
  bottom: 18px;
}}

.sofiati-cookie-layout-glass-corner .sofiati-cookie-shell,
.sofiati-cookie-layout-bottom-glass .sofiati-cookie-shell {{
  backdrop-filter: blur(22px);
}}

.sofiati-cookie-{code} {{
  --cookie-bg: {recipe.bg};
  --cookie-fg: {recipe.fg};
  --cookie-muted: {recipe.muted};
  --cookie-accent: {recipe.accent};
  --cookie-accent-2: {recipe.accent_2};
  --cookie-border: {recipe.border};
  --cookie-shadow: {recipe.shadow};
  --cookie-width: {recipe.width};
  --cookie-radius: {recipe.radius};
  --cookie-padding: {recipe.padding};
  --cookie-gap: {recipe.gap};
  --cookie-title-size: {recipe.title_size};
  --cookie-text-size: {recipe.text_size};
  --cookie-button-radius: {recipe.button_radius};
  text-align: {recipe.align};
}}

.sofiati-cookie-{code} .sofiati-cookie-shell {{
  animation: sofiatiCookie{recipe.motion.replace("-", "").title()} .38s ease both;
}}

.sofiati-cookie-{code}.sofiati-cookie-layout-soft-modal::before,
.sofiati-cookie-{code}.sofiati-cookie-layout-center-card::before,
.sofiati-cookie-{code}.sofiati-cookie-layout-formal-modal::before,
.sofiati-cookie-{code}.sofiati-cookie-layout-flagship-modal::before {{
  content: "";
  position: fixed;
  inset: -100vmax;
  background: rgba(37,35,33,.28);
  z-index: -1;
}}

@keyframes sofiatiCookieRise {{
  from {{ opacity: 0; transform: translateY(14px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes sofiatiCookieSlideUp {{
  from {{ opacity: 0; transform: translateY(100%); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes sofiatiCookieSlideLeft {{
  from {{ opacity: 0; transform: translateX(18px); }}
  to {{ opacity: 1; transform: translateX(0); }}
}}

@keyframes sofiatiCookieSlideDown {{
  from {{ opacity: 0; transform: translateY(-100%); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}

@keyframes sofiatiCookieFade {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}

@keyframes sofiatiCookieScaleIn {{
  from {{ opacity: 0; transform: scale(.96); }}
  to {{ opacity: 1; transform: scale(1); }}
}}

@media (max-width: 760px) {{
  .sofiati-cookie-notice {{
    left: 12px !important;
    right: 12px !important;
    bottom: 12px !important;
    top: auto !important;
    transform: none !important;
  }}

  .sofiati-cookie-shell,
  .sofiati-cookie-layout-bottom-sheet .sofiati-cookie-shell,
  .sofiati-cookie-layout-serene-sheet .sofiati-cookie-shell,
  .sofiati-cookie-layout-clean-bottom .sofiati-cookie-shell,
  .sofiati-cookie-layout-top-ribbon .sofiati-cookie-shell {{
    width: 100%;
    max-width: none;
    grid-template-columns: 1fr;
    border-radius: 18px;
    padding: 16px;
  }}

  .sofiati-cookie-icon {{
    display: none;
  }}

  .sofiati-cookie-actions,
  .sofiati-cookie-panel-actions {{
    display: grid;
    grid-template-columns: 1fr;
  }}

  .sofiati-cookie-btn {{
    width: 100%;
  }}

  .sofiati-cookie-choice {{
    align-items: flex-start;
  }}
}}

@media (prefers-reduced-motion: reduce) {{
  .sofiati-cookie-shell {{
    animation: none !important;
  }}
}}
{CSS_END}
"""


def render_cookie_js() -> str:
    return f"""
{JS_START}
(() => {{
  const notices = Array.from(document.querySelectorAll("[data-cookie-notice]"));
  if (!notices.length) return;

  const defaultConsent = {{
    essential: true,
    analytics: false,
    experience: false,
    updatedAt: null,
  }};

  function readConsent(key) {{
    try {{
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : null;
    }} catch {{
      return null;
    }}
  }}

  function writeConsent(key, consent) {{
    const payload = {{
      ...defaultConsent,
      ...consent,
      essential: true,
      updatedAt: new Date().toISOString(),
    }};
    localStorage.setItem(key, JSON.stringify(payload));
    window.dispatchEvent(new CustomEvent("sofiati:cookie-consent", {{ detail: payload }}));
    return payload;
  }}

  function closeNotice(notice) {{
    notice.setAttribute("data-cookie-visible", "false");
  }}

  function openNotice(notice) {{
    notice.setAttribute("data-cookie-visible", "true");
  }}

  function setupNotice(notice) {{
    const key = notice.getAttribute("data-cookie-key") || "sofiatiCookieConsent";
    const existing = readConsent(key);

    if (existing) {{
      closeNotice(notice);
      window.dispatchEvent(new CustomEvent("sofiati:cookie-consent", {{ detail: existing }}));
      return;
    }}

    openNotice(notice);

    const panel = notice.querySelector("[data-cookie-panel]");
    const manageButton = notice.querySelector('[data-cookie-action="manage"]');
    const analyticsToggle = notice.querySelector('[data-cookie-toggle="analytics"]');
    const experienceToggle = notice.querySelector('[data-cookie-toggle="experience"]');

    notice.addEventListener("click", (event) => {{
      const button = event.target.closest("[data-cookie-action]");
      if (!button) return;

      const action = button.getAttribute("data-cookie-action");

      if (action === "accept") {{
        writeConsent(key, {{ analytics: true, experience: true }});
        closeNotice(notice);
      }}

      if (action === "reject") {{
        writeConsent(key, {{ analytics: false, experience: false }});
        closeNotice(notice);
      }}

      if (action === "manage") {{
        const isHidden = panel?.hasAttribute("hidden");
        if (isHidden) {{
          panel.removeAttribute("hidden");
          button.setAttribute("aria-expanded", "true");
        }} else {{
          panel?.setAttribute("hidden", "");
          button.setAttribute("aria-expanded", "false");
        }}
      }}

      if (action === "save") {{
        writeConsent(key, {{
          analytics: Boolean(analyticsToggle?.checked),
          experience: Boolean(experienceToggle?.checked),
        }});
        closeNotice(notice);
      }}
    }});
  }}

  notices.forEach(setupNotice);
}})();
{JS_END}
"""


def backup_file(path: Path) -> None:
    if path.exists():
        backup = path.with_suffix(path.suffix + ".cookie-v1.bak")
        shutil.copy2(path, backup)


def write_text(path: Path, content: str, apply: bool) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == content:
        return False

    if apply:
        path.parent.mkdir(parents=True, exist_ok=True)
        backup_file(path)
        path.write_text(content, encoding="utf-8")

    return True


def git_is_dirty(root: Path) -> bool:
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def assert_unique_recipes() -> None:
    seen: dict[tuple[str, str, str, str, str], int] = {}
    for number, recipe in COOKIE_RECIPES.items():
        signature = (
            recipe.layout,
            recipe.bg,
            recipe.accent,
            recipe.radius,
            recipe.icon_style,
        )
        if signature in seen:
            raise ValueError(f"Cookie recipe {number} duplicates recipe {seen[signature]}")
        seen[signature] = number


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository root.")
    parser.add_argument("--apply", action="store_true", help="Write changes. Without this, dry run only.")
    parser.add_argument("--force", action="store_true", help="Allow running on a dirty Git tree.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    concepts_dir = root / "concepts"

    assert_unique_recipes()

    if git_is_dirty(root) and not args.force:
        print("Git tree has changes. Commit/stash first, or rerun with --force.")
        return

    js_block = render_cookie_js()
    audit_lines = [
        "# Sofiati Cookie Notice Variation Audit",
        "",
        "- Same notice meaning across all concepts.",
        "- 50 different layouts/colour systems.",
        "- Per-concept localStorage keys for demo purposes.",
        "- Essential cookies always on.",
        "- Optional analytics/experience choices are stored locally.",
        "",
    ]

    changed_concepts = 0
    changed_pages = 0

    for concept in concept_dirs(concepts_dir):
        number = concept_number(concept)
        recipe = COOKIE_RECIPES.get(number)

        if not recipe:
            print(f"Skipping {concept.name}: no cookie recipe.")
            continue

        code = f"{number:02d}"
        html_block = render_cookie_html(recipe, code)
        css_block = render_cookie_css(recipe, code)

        css_path = find_css_file(concept)
        js_path = find_js_file(concept)

        existing_css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
        new_css = replace_between_markers(existing_css, CSS_START, CSS_END, css_block)

        existing_js = js_path.read_text(encoding="utf-8") if js_path.exists() else ""
        new_js = replace_between_markers(existing_js, JS_START, JS_END, js_block)

        css_changed = write_text(css_path, new_css, args.apply)
        js_changed = write_text(js_path, new_js, args.apply)

        page_count = 0
        for page in page_files(concept):
            old_html = page.read_text(encoding="utf-8")
            new_html = inject_html_block(old_html, html_block)
            if write_text(page, new_html, args.apply):
                page_count += 1

        if css_changed or js_changed or page_count:
            changed_concepts += 1
            changed_pages += page_count

        audit_lines.extend([
            f"## {concept.name}",
            "",
            f"- Recipe: `{recipe.slug}`",
            f"- Layout: `{recipe.layout}`",
            f"- Background: `{recipe.bg}`",
            f"- Accent: `{recipe.accent}`",
            f"- Width: `{recipe.width}`",
            f"- Radius: `{recipe.radius}`",
            f"- Icon style: `{recipe.icon_style}`",
            f"- Motion: `{recipe.motion}`",
            f"- CSS path: `{css_path.relative_to(root)}`",
            f"- JS path: `{js_path.relative_to(root)}`",
            f"- HTML pages updated in dry/apply pass: `{page_count}`",
            "",
        ])

        print(f"{'Would update' if not args.apply else 'Updated'} {concept.name}: {page_count} pages")

    audit_path = root / "audit" / "cookie-notice-variation-audit.md"
    if args.apply:
        audit_path.parent.mkdir(parents=True, exist_ok=True)
        audit_path.write_text("\n".join(audit_lines).rstrip() + "\n", encoding="utf-8")

    if args.apply:
        print(f"Done. Updated {changed_concepts} concepts and {changed_pages} pages.")
        print("Audit written to audit/cookie-notice-variation-audit.md")
    else:
        print(f"Dry run complete. {changed_concepts} concepts and {changed_pages} pages would change.")
        print("Rerun with --apply to write files.")


if __name__ == "__main__":
    main()