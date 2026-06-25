#!/usr/bin/env python3
"""Build the asset-led Sofiati visual system across all 50 concepts.

The base concepts are static HTML/CSS/JS builds. This script adds the
brand-audited asset layer: shared brand assets, per-concept icon and
botanical systems, portrait treatments, audit documents and page integration.
"""

from __future__ import annotations

import json
import math
import shutil
import sys
from dataclasses import asdict
from pathlib import Path
from textwrap import dedent

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, features

sys.path.insert(0, str(Path(__file__).resolve().parent))

from generate_concepts import BRAND, CONCEPTS, PAGE_SPECS, Concept, esc  # noqa: E402


ROOT = Path(__file__).resolve().parents[1]
BRAND_DIR = ROOT / "brand identity"
CONCEPTS_DIR = ROOT / "concepts"
ROOT_ASSETS = ROOT / "assets"
ROOT_CSS = ROOT / "css"
DATA_DIR = ROOT / "data"
PORTRAIT_EXT = "webp" if features.check("webp") else "png"

ICON_NAMES = [
    "consultation",
    "laser",
    "skin",
    "care",
    "evaluation",
    "safety",
    "aftercare",
    "results",
    "journal",
    "mission",
    "values",
    "contact",
    "technology",
    "credentials",
    "whatsapp",
    "back-to-top",
]

PAGE_ICON = {
    "index": "consultation",
    "about": "credentials",
    "mission": "mission",
    "values": "values",
    "care": "care",
    "laser": "laser",
    "skin": "skin",
    "results": "results",
    "testimonials": "journal",
    "journal": "journal",
    "blog": "journal",
    "faq": "evaluation",
    "contact": "contact",
    "consultation": "consultation",
    "legal": "safety",
    "privacy": "safety",
    "cookies": "evaluation",
    "accessibility": "care",
    "404": "back-to-top",
}

ASSET_ARCHETYPES = [
    "pressed botanical editorial",
    "business-card seal system",
    "clinical magazine linework",
    "laser dossier geometry",
    "quiet luxury watermark",
    "mobile story botanical path",
    "proof-grid bronze markers",
    "round monogram sanctuary",
    "consultation studio badges",
    "minimal appointment stationery",
    "institutional credential atlas",
    "dermatology portal pictograms",
    "private column frames",
    "champagne ritual overlays",
    "procedure atlas symbols",
    "service shelf labels",
    "local branch contact marks",
    "high-contrast clinic strokes",
    "local search direction tags",
    "physician profile stamp",
    "concierge clinic panels",
    "signature consultant trace",
    "medical skin disclosure set",
    "fine-list micro glyphs",
    "treatment explorer chips",
    "editorial authority plaques",
    "procedure library tabs",
    "single-service education marks",
    "doctor journal notecards",
    "booking concierge steps",
    "confidence timeline leaves",
    "natural result privacy frames",
    "destination journey pins",
    "artisan botanical craft",
    "laser studio membership passes",
    "skincare bar progress marks",
    "treatment pass slots",
    "doctor shop editorial labels",
    "science ingredient diagrams",
    "prestige formula shimmer",
    "ritual story seals",
    "apothecary text stamps",
    "maison collection crests",
    "cream commerce labels",
    "clinical drop capsules",
    "spa menu botanical tabs",
    "expert routine sequence",
    "botanical serum line growth",
    "farm-clean field notes",
    "ingredient lab minimal grid",
]

PALETTES = [
    {"sage": "#A2AEA0", "deep": "#485041", "ivory": "#F3EFE4", "cream": "#F8F7F2", "bronze": "#9A6B35", "gold": "#CDAA78"},
    {"sage": "#9DA799", "deep": "#344039", "ivory": "#F2EEE3", "cream": "#F8F4EA", "bronze": "#8F745F", "gold": "#D2C5A7"},
    {"sage": "#7A8B81", "deep": "#273332", "ivory": "#EEE8DC", "cream": "#F7F2E8", "bronze": "#B79869", "gold": "#E0C58E"},
    {"sage": "#A3AFA1", "deep": "#3A4739", "ivory": "#F1ECE0", "cream": "#F8F7F2", "bronze": "#8E7B56", "gold": "#DACCB7"},
    {"sage": "#B8C1B6", "deep": "#596858", "ivory": "#F4F0E6", "cream": "#FAF8F2", "bronze": "#734011", "gold": "#C7A56D"},
]

PORTRAIT_IDEAS = [
    "arched ivory portrait with bronze pressed-leaf edge",
    "round monogram-backed portrait stamp",
    "sage duotone editorial profile tile",
    "business-card portrait with signature line",
    "full-height consultation portrait badge",
    "soft oval botanical frame",
    "clinical credential portrait card",
    "champagne line portrait seal",
    "mobile avatar with FS watermark",
    "journal-side portrait notecard",
]

BOTANICAL_IDEAS = [
    "gold leaf divider",
    "sage line-art branch",
    "bronze corner frame",
    "monogram wreath",
    "botanical section separator",
    "soft leaf watermark",
    "animated leaf path",
    "quote-mark branch",
    "mobile-menu botanical field",
    "footer botanical stamp",
]

FORM_IDEAS = [
    "minimal ivory form",
    "sage panel form",
    "botanical framed form",
    "gold line form",
    "step-style consultation form",
    "sidebar form",
    "floating editorial form",
    "business-card form",
    "mobile-first bottom form",
    "portrait-led consultation form",
]

FOOTER_IDEAS = [
    "business-card footer",
    "large monogram ledger",
    "signature seal footer",
    "clinical column footer",
    "botanical map footer",
    "concierge contact footer",
    "apothecary fine-print footer",
    "bronze strip footer",
    "story-background footer",
    "credential stamp footer",
]

MOTION_IDEAS = [
    "line reveal",
    "leaf orbit",
    "portrait lift",
    "icon tilt",
    "gold shimmer",
    "menu bloom",
    "divider trace",
    "form focus glow",
    "journal card rise",
    "service badge pulse",
]


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def write(path: Path, text: str) -> None:
    ensure_dir(path.parent)
    path.write_text(text.strip() + "\n", encoding="utf-8")


def copy_if_exists(source: Path, target: Path) -> None:
    ensure_dir(target.parent)
    if source.exists():
        shutil.copy2(source, target)


def palette_for(concept: Concept) -> dict[str, str]:
    return PALETTES[concept.accent_index % len(PALETTES)]


def asset_slug(concept: Concept) -> str:
    return f"{concept.number}-{concept.slug}"


def svg(body: str, width: int = 240, height: int = 240, extra: str = "") -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" fill="none" role="img" {extra}>'
        f"{body}</svg>"
    )


def leaf_path(cx: float, cy: float, scale: float, rotate: float = 0) -> str:
    return (
        f'<g transform="translate({cx:.2f} {cy:.2f}) rotate({rotate:.2f}) scale({scale:.2f})">'
        '<path d="M0 0 C18 -18 42 -18 58 0 C42 14 18 14 0 0Z" />'
        '<path d="M4 0 C22 -3 38 -2 55 0" />'
        "</g>"
    )


def brand_sources() -> dict[str, str]:
    return {
        "sofiati-logo-primary-sage.png": "LOGOTIPO PRINCIPAL VERDE PNG.png",
        "sofiati-logo-primary-white.png": "LOGOTIPO PRINCIPAL BRANCO PNG.png",
        "sofiati-logo-primary-bronze.png": "LOGOTIPO PRINCIPAL PNG.png",
        "sofiati-monogram-sage.png": "SUB LOGOTIPO VERDE PNG.png",
        "sofiati-monogram-white.png": "SUB LOGOTIPO BRANCO PNG.png",
        "sofiati-monogram-bronze.png": "SUB LOGOTIPO PNG.png",
        "sofiati-signature-sage.png": "ASSINATURA VERDE PNG.png",
        "sofiati-signature-white.png": "ASSINATURA BRANCO PNG.png",
    }


def favicon_svg() -> str:
    return svg(
        '<rect width="240" height="240" rx="46" fill="#A2AEA0"/>'
        '<circle cx="120" cy="120" r="78" stroke="#F3EFE4" stroke-width="4"/>'
        '<text x="120" y="137" text-anchor="middle" font-family="Georgia, serif" '
        'font-size="78" fill="#F3EFE4">FS</text>',
        extra='aria-label="Sofiati FS monogram"',
    )


def botanical_line_mark(colors: dict[str, str], seed: int) -> str:
    leaves = []
    for i in range(6):
        x = 46 + i * 25
        y = 116 + math.sin(seed + i) * 16
        leaves.append(leaf_path(x, y, 0.34 + (i % 3) * 0.04, -36 + i * 13))
    return svg(
        f'<path d="M28 148 C82 84 156 82 214 52" stroke="{colors["bronze"]}" stroke-width="3" '
        'stroke-linecap="round"/>'
        f'<g stroke="{colors["bronze"]}" fill="{colors["gold"]}" stroke-width="2" opacity=".86">'
        + "".join(leaves)
        + "</g>",
        extra='aria-label="Sofiati botanical line mark"',
    )


def create_root_brand_assets() -> None:
    brand_root = ROOT_ASSETS / "brand"
    ensure_dir(brand_root)
    for target, source in brand_sources().items():
        copy_if_exists(BRAND_DIR / source, brand_root / target)
    write(brand_root / "sofiati-favicon.svg", favicon_svg())
    write(brand_root / "sofiati-botanical-line-mark.svg", botanical_line_mark(PALETTES[0], 1))

    shared_botanical = brand_root / "botanical"
    icon_botanical = ROOT_ASSETS / "icons" / "botanical"
    ensure_dir(shared_botanical)
    ensure_dir(icon_botanical)
    for idx, name in enumerate(["gold-leaf-divider", "sage-branch", "bronze-corner", "monogram-wreath", "section-separator", "quote-leaf"]):
        colors = PALETTES[idx % len(PALETTES)]
        write(shared_botanical / f"{name}.svg", botanical_asset_svg(colors, idx, name))
    for idx, icon in enumerate(["leaf", "branch", "wreath", "sprout", "gold-detail", "section-line"]):
        write(icon_botanical / f"{icon}.svg", icon_svg(icon, PALETTES[idx % len(PALETTES)], idx, global_icon=True))


def icon_body(name: str, colors: dict[str, str], seed: int, global_icon: bool = False) -> str:
    stroke = colors["bronze"] if seed % 2 else colors["deep"]
    fill = colors["cream"] if seed % 3 else colors["ivory"]
    sage = colors["sage"]
    gold = colors["gold"]
    sw = 4 if seed % 4 in {0, 3} else 3
    radius_shape = [
        f'<circle cx="120" cy="120" r="82" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
        f'<rect x="42" y="42" width="156" height="156" rx="{20 + seed % 42}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
        f'<path d="M120 30 L198 84 L168 190 L72 190 L42 84 Z" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
        f'<ellipse cx="120" cy="120" rx="86" ry="{68 + seed % 18}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>',
    ][seed % 4]
    accent = (
        f'<g stroke="{gold}" fill="{colors["ivory"]}" stroke-width="2" opacity=".9">'
        f'{leaf_path(142, 52, .27, 18 + seed)}{leaf_path(82, 186, .22, 198 - seed)}</g>'
    )
    path_map = {
        "consultation": '<path d="M74 92 H166 Q178 92 178 104 V142 Q178 154 166 154 H122 L92 176 V154 H74 Q62 154 62 142 V104 Q62 92 74 92Z"/>',
        "laser": '<path d="M72 148 L136 84 M134 82 L168 48 M118 102 L176 160 M80 154 H158"/>',
        "skin": '<path d="M83 143 C84 96 105 72 124 68 C146 80 158 106 154 143 C149 174 93 174 83 143Z"/><circle cx="111" cy="125" r="4"/><circle cx="133" cy="112" r="4"/>',
        "care": '<path d="M70 142 C92 126 108 126 126 144 C144 126 164 124 184 142 M86 116 C96 84 126 76 154 102 C134 128 106 132 86 116Z"/>',
        "evaluation": '<path d="M78 70 H162 V174 H78 Z"/><path d="M96 106 L114 124 L148 88 M96 146 H144"/>',
        "safety": '<path d="M120 58 L170 78 V116 C170 148 148 172 120 184 C92 172 70 148 70 116 V78 Z"/><path d="M96 120 L114 138 L146 102"/>',
        "aftercare": '<path d="M120 68 A56 56 0 1 1 119 68 M120 94 V126 L144 144"/><path d="M86 78 L72 62 M154 78 L168 62"/>',
        "results": '<path d="M74 164 H170"/><path d="M88 164 V126 M120 164 V96 M152 164 V112"/><path d="M86 110 C112 84 136 130 166 82"/>',
        "journal": '<path d="M78 72 H132 Q154 72 162 90 V172 H104 Q88 172 78 158Z"/><path d="M132 72 V172 M96 104 H118 M96 128 H120"/>',
        "mission": '<path d="M120 62 L135 105 L180 106 L144 132 L156 176 L120 150 L84 176 L96 132 L60 106 L105 105Z"/>',
        "values": '<path d="M120 170 C80 140 66 112 82 88 C98 68 122 86 120 106 C124 86 148 68 164 88 C182 112 160 142 120 170Z"/>',
        "contact": '<path d="M70 88 H170 V154 H70 Z"/><path d="M72 90 L120 128 L168 90"/>',
        "technology": '<path d="M90 88 H150 V148 H90 Z"/><path d="M120 58 V88 M120 148 V182 M58 118 H90 M150 118 H182 M76 74 L90 88 M164 74 L150 88 M76 164 L90 148 M164 164 L150 148"/>',
        "credentials": '<path d="M120 58 L154 76 L154 118 Q154 148 120 174 Q86 148 86 118 L86 76 Z"/><path d="M100 112 H140 M120 92 V132"/><circle cx="120" cy="152" r="10"/>',
        "whatsapp": '<path d="M76 168 L86 140 A54 54 0 1 1 106 160 Z"/><path d="M103 98 C112 126 126 139 148 144"/>',
        "back-to-top": '<path d="M120 174 V72 M82 110 L120 72 L158 110"/>',
        "leaf": '<path d="M70 132 C96 72 148 60 178 82 C158 140 106 154 70 132Z"/><path d="M78 130 C112 112 142 94 172 84"/>',
        "branch": '<path d="M62 164 C94 112 132 86 178 70"/><path d="M94 120 C82 98 94 78 120 74 M126 96 C136 72 156 64 180 72"/>',
        "wreath": '<circle cx="120" cy="120" r="60"/><path d="M86 80 C68 108 68 136 88 162 M154 80 C174 108 172 138 152 162"/>',
        "sprout": '<path d="M120 168 V108"/><path d="M120 124 C88 124 72 98 78 76 C112 76 124 94 120 124Z"/><path d="M120 132 C152 132 168 106 162 84 C128 84 116 102 120 132Z"/>',
        "gold-detail": '<path d="M62 120 H178"/><path d="M88 120 C102 92 128 92 142 120 C128 148 102 148 88 120Z"/>',
        "section-line": '<path d="M52 120 C82 90 108 150 138 120 C158 100 172 100 188 120"/><path d="M80 110 C90 88 110 82 130 94"/>',
    }
    symbol = path_map.get(name, path_map["leaf"])
    mono = "FS" if name == "credentials" and seed % 5 == 0 else ""
    text = (
        f'<text x="120" y="135" text-anchor="middle" font-family="Georgia, serif" font-size="38" fill="{stroke}">{mono}</text>'
        if mono
        else ""
    )
    return (
        radius_shape
        + accent
        + f'<g stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round">'
        + symbol
        + "</g>"
        + f'<circle cx="178" cy="64" r="{8 + seed % 8}" fill="{sage}" opacity=".28"/>'
        + text
    )


def icon_svg(name: str, colors: dict[str, str], seed: int, global_icon: bool = False) -> str:
    label = f"Sofiati {name.replace('-', ' ')} icon"
    return svg(icon_body(name, colors, seed, global_icon), extra=f'aria-label="{esc(label)}"')


def botanical_asset_svg(colors: dict[str, str], seed: int, name: str) -> str:
    stroke = colors["bronze"] if seed % 2 else colors["deep"]
    gold = colors["gold"]
    sage = colors["sage"]
    if "divider" in name:
        body = (
            f'<path d="M18 120 H222" stroke="{gold}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M42 120 C84 82 156 82 198 120" stroke="{stroke}" stroke-width="2" opacity=".65"/>'
            f'<g stroke="{stroke}" fill="{colors["ivory"]}" stroke-width="2">{leaf_path(82, 104, .27, -24)}{leaf_path(154, 103, .27, 204)}</g>'
        )
    elif "corner" in name:
        body = (
            f'<path d="M42 198 V42 H198" stroke="{gold}" stroke-width="4"/>'
            f'<path d="M62 176 C62 104 104 62 176 62" stroke="{stroke}" stroke-width="2"/>'
            f'<g stroke="{stroke}" fill="{colors["cream"]}" stroke-width="2">{leaf_path(70, 126, .22, -72)}{leaf_path(122, 70, .24, 18)}</g>'
        )
    elif "wreath" in name:
        body = (
            f'<circle cx="120" cy="120" r="72" stroke="{gold}" stroke-width="3"/>'
            f'<text x="120" y="134" text-anchor="middle" font-family="Georgia, serif" font-size="52" fill="{stroke}">FS</text>'
            f'<path d="M78 72 C46 118 52 158 92 190 M162 72 C194 118 188 158 148 190" stroke="{stroke}" stroke-width="2"/>'
        )
    elif "separator" in name:
        body = (
            f'<path d="M22 132 C64 84 94 176 130 126 C160 84 178 116 218 82" stroke="{stroke}" stroke-width="3" stroke-linecap="round"/>'
            f'<path d="M34 156 H206" stroke="{gold}" stroke-width="2" opacity=".58"/>'
            f'<circle cx="120" cy="120" r="24" fill="{sage}" opacity=".18"/>'
        )
    else:
        body = (
            f'<rect x="34" y="34" width="172" height="172" rx="{22 + seed % 32}" fill="{colors["cream"]}" opacity=".55"/>'
            f'<path d="M62 152 C88 94 144 74 184 96 C162 152 100 172 62 152Z" stroke="{stroke}" fill="{colors["ivory"]}" stroke-width="2"/>'
            f'<path d="M68 150 C108 132 144 110 180 98" stroke="{gold}" stroke-width="2"/>'
        )
    return svg(body, extra=f'aria-label="Sofiati {esc(name.replace("-", " "))}"')


def pattern_svg(colors: dict[str, str], seed: int, kind: str) -> str:
    dots = []
    for row in range(5):
        for col in range(7):
            cx = 24 + col * 32 + (row % 2) * 14
            cy = 28 + row * 38
            dots.append(
                f'<circle cx="{cx}" cy="{cy}" r="{2 + (seed + row + col) % 4}" fill="{colors["bronze"]}" opacity=".16"/>'
            )
            if (row + col + seed) % 3 == 0:
                dots.append(
                    f'<path d="M{cx - 8} {cy + 8} C{cx} {cy - 12} {cx + 18} {cy - 8} {cx + 22} {cy + 4}" '
                    f'stroke="{colors["sage"]}" stroke-width="1.4" fill="none" opacity=".42"/>'
                )
    text = ""
    if kind == "generated":
        text = (
            f'<text x="120" y="132" text-anchor="middle" font-family="Georgia, serif" '
            f'font-size="68" fill="{colors["deep"]}" opacity=".12">FS</text>'
        )
    return svg(
        f'<rect width="240" height="240" fill="{colors["cream"]}"/>'
        f'<path d="M-20 206 C44 138 88 250 144 172 C184 118 210 144 260 92" '
        f'stroke="{colors["gold"]}" stroke-width="2" opacity=".5"/>'
        + "".join(dots)
        + text,
        extra=f'aria-label="Sofiati {esc(kind)} pattern"',
    )


def form_frame_svg(colors: dict[str, str], seed: int) -> str:
    return svg(
        f'<rect x="20" y="20" width="200" height="200" rx="{18 + seed % 36}" stroke="{colors["bronze"]}" stroke-width="3" opacity=".72"/>'
        f'<path d="M40 188 C84 132 146 132 200 76" stroke="{colors["gold"]}" stroke-width="3" stroke-linecap="round"/>'
        f'<g stroke="{colors["deep"]}" fill="{colors["ivory"]}" stroke-width="2">{leaf_path(82, 160, .23, -18)}{leaf_path(168, 92, .22, 196)}</g>'
        f'<circle cx="196" cy="44" r="18" fill="{colors["sage"]}" opacity=".18"/>',
        extra='aria-label="Sofiati consultation form botanical frame"',
    )


def service_svg(colors: dict[str, str], seed: int, label: str) -> str:
    beams = []
    for i in range(5):
        angle = -24 + i * 12 + seed % 7
        beams.append(
            f'<path d="M120 124 L{44 + i * 38} {58 + (i % 2) * 26}" stroke="{colors["gold"]}" stroke-width="2" opacity=".78"/>'
        )
    return svg(
        f'<rect x="22" y="34" width="196" height="172" rx="{20 + seed % 34}" fill="{colors["cream"]}" stroke="{colors["bronze"]}" stroke-width="2"/>'
        + "".join(beams)
        + f'<circle cx="120" cy="124" r="42" fill="{colors["sage"]}" opacity=".20"/>'
        + f'<path d="M82 142 C104 98 140 92 164 112 C148 150 112 160 82 142Z" stroke="{colors["deep"]}" fill="{colors["ivory"]}" stroke-width="2"/>'
        + f'<text x="120" y="196" text-anchor="middle" font-family="Inter, sans-serif" font-size="13" fill="{colors["deep"]}">{esc(label.upper())}</text>',
        extra=f'aria-label="Sofiati {esc(label)} service visual"',
    )


def motion_svg(colors: dict[str, str], seed: int) -> str:
    path = "M28 168 C66 74 112 214 154 112 C178 58 198 88 218 54"
    if seed % 4 == 1:
        path = "M32 120 C70 88 96 88 124 120 C152 152 178 152 210 120"
    elif seed % 4 == 2:
        path = "M50 190 C50 86 190 86 190 190"
    elif seed % 4 == 3:
        path = "M42 70 H198 V170 H42 Z"
    return svg(
        f'<path d="{path}" stroke="{colors["gold"]}" stroke-width="4" stroke-linecap="round"/>'
        f'<path d="{path}" stroke="{colors["deep"]}" stroke-width="1.5" stroke-dasharray="8 10" opacity=".75"/>'
        f'<circle cx="{62 + seed % 100}" cy="{78 + seed % 80}" r="16" fill="{colors["sage"]}" opacity=".22"/>',
        extra='aria-label="Sofiati animation path asset"',
    )


def create_portrait(concept: Concept, target: Path) -> None:
    colors = palette_for(concept)
    ensure_dir(target.parent)
    source = Image.open(BRAND_DIR / "Dr Fran.png").convert("RGB")
    size = (640, 820)
    canvas = Image.new("RGB", size, colors["cream"])
    draw = ImageDraw.Draw(canvas)
    idx = concept.accent_index

    for y in range(size[1]):
        blend = y / size[1]
        r1, g1, b1 = Image.new("RGB", (1, 1), colors["cream"]).getpixel((0, 0))
        r2, g2, b2 = Image.new("RGB", (1, 1), colors["sage"]).getpixel((0, 0))
        color = (
            int(r1 * (1 - blend * .32) + r2 * blend * .32),
            int(g1 * (1 - blend * .32) + g2 * blend * .32),
            int(b1 * (1 - blend * .32) + b2 * blend * .32),
        )
        draw.line((0, y, size[0], y), fill=color)

    for i in range(10):
        x = 54 + i * 56 + (idx % 3) * 8
        draw.arc((x - 26, 76 + (i % 3) * 20, x + 70, 190 + (i % 4) * 18), 205, 318, fill=colors["gold"], width=2)

    portrait = ImageEnhance.Color(source.resize((424, 424), Image.Resampling.LANCZOS)).enhance(0.82 + (idx % 4) * 0.06)
    portrait = ImageEnhance.Contrast(portrait).enhance(0.96 + (idx % 5) * 0.025)
    if idx % 3 == 1:
        overlay = Image.new("RGB", portrait.size, colors["sage"])
        portrait = Image.blend(portrait, overlay, 0.12)
    if idx % 3 == 2:
        overlay = Image.new("RGB", portrait.size, colors["gold"])
        portrait = Image.blend(portrait, overlay, 0.09)

    mask = Image.new("L", portrait.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    if idx % 5 == 0:
        mask_draw.rounded_rectangle((0, 0, 424, 424), radius=212, fill=255)
    elif idx % 5 == 1:
        mask_draw.rounded_rectangle((0, 0, 424, 424), radius=72, fill=255)
    elif idx % 5 == 2:
        mask_draw.rounded_rectangle((0, 0, 424, 424), radius=190, fill=255)
        mask_draw.rectangle((0, 212, 424, 424), fill=255)
    elif idx % 5 == 3:
        mask_draw.polygon([(28, 0), (424, 34), (390, 424), (0, 396)], fill=255)
    else:
        mask_draw.rounded_rectangle((0, 0, 424, 424), radius=26, fill=255)

    px = 108
    py = 92
    shadow = Image.new("RGBA", portrait.size, (0, 0, 0, 0))
    sh_draw = ImageDraw.Draw(shadow)
    sh_draw.bitmap((0, 0), mask.filter(ImageFilter.GaussianBlur(16)), fill=(37, 35, 33, 70))
    canvas.paste(shadow.convert("RGB"), (px + 10, py + 18), shadow)
    canvas.paste(portrait, (px, py), mask)
    draw.rounded_rectangle((px - 18, py - 18, px + 442, py + 442), radius=46 + idx % 70, outline=colors["bronze"], width=4)
    draw.arc((58, 64, 584, 590), 42 + idx, 138 + idx, fill=colors["gold"], width=3)
    draw.arc((58, 64, 584, 590), 222 + idx, 318 + idx, fill=colors["gold"], width=3)

    try:
        title_font = ImageFont.truetype("DejaVuSerif.ttf", 36)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 18)
    except Exception:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    draw.text((72, 578), "Franciele Sofiati", fill=colors["deep"], font=title_font)
    draw.text((74, 628), "CRBM 6277 - Advanced Aesthetic Biomedicine", fill=colors["deep"], font=small_font)
    draw.text((74, 660), concept.name.upper(), fill=colors["bronze"], font=small_font)
    draw.line((74, 704, 566, 704), fill=colors["gold"], width=3)
    draw.text((74, 728), "Londrina, PR", fill=colors["deep"], font=small_font)
    draw.text((414, 756), "FS", fill=colors["bronze"], font=title_font)

    if PORTRAIT_EXT == "webp":
        canvas.save(target, "WEBP", quality=88, method=6)
    else:
        canvas.save(target, "PNG", optimize=True)


def create_concept_assets(concept: Concept) -> dict[str, object]:
    concept_dir = CONCEPTS_DIR / concept.folder
    assets = concept_dir / "assets"
    colors = palette_for(concept)
    seed = concept.accent_index + 1

    required_dirs = ["icons", "botanical", "portrait", "backgrounds", "textures", "forms", "animations", "journal", "service", "generated"]
    for name in required_dirs:
        ensure_dir(assets / name)

    for icon_index, icon_name in enumerate(ICON_NAMES):
        write(assets / "icons" / f"{icon_name}.svg", icon_svg(icon_name, colors, seed * 11 + icon_index))

    botanical_files = {
        "gold-leaf-divider.svg": "divider",
        "sage-botanical-corner.svg": "corner",
        "bronze-branch.svg": "branch",
        "monogram-wreath.svg": "wreath",
        "section-separator.svg": "separator",
        "botanical-quote.svg": "quote",
        "footer-botanical-stamp.svg": "footer stamp",
    }
    for offset, (filename, kind) in enumerate(botanical_files.items()):
        write(assets / "botanical" / filename, botanical_asset_svg(colors, seed + offset, kind))

    write(assets / "backgrounds" / "botanical-background.svg", pattern_svg(colors, seed, "botanical background"))
    write(assets / "backgrounds" / "mobile-menu-background.svg", pattern_svg(colors, seed + 8, "mobile menu background"))
    write(assets / "textures" / "soft-skin-texture.svg", pattern_svg(colors, seed + 16, "soft skin texture"))
    write(assets / "textures" / "clinical-paper-texture.svg", pattern_svg(colors, seed + 22, "clinical paper texture"))
    write(assets / "forms" / "consultation-form-frame.svg", form_frame_svg(colors, seed))
    write(assets / "animations" / "motion-path.svg", motion_svg(colors, seed))
    for journal_index in range(1, 4):
        write(assets / "journal" / f"journal-thumbnail-{journal_index}.svg", service_svg(colors, seed + journal_index * 5, f"Journal {journal_index}"))
    for service_name in ["laser", "skin", "care", "results"]:
        write(assets / "service" / f"{service_name}-service-visual.svg", service_svg(colors, seed + len(service_name), service_name))
    write(assets / "generated" / "homepage-asset-composition.svg", pattern_svg(colors, seed + 42, "generated"))

    portrait_path = assets / "portrait" / f"franciele-portrait-{concept.slug}.{PORTRAIT_EXT}"
    create_portrait(concept, portrait_path)

    summary = {
        "concept": concept.folder,
        "assetArchetype": ASSET_ARCHETYPES[concept.accent_index],
        "palette": colors,
        "portrait": portrait_path.relative_to(concept_dir).as_posix(),
        "iconCount": len(ICON_NAMES),
        "botanicalCount": len(botanical_files),
        "folders": required_dirs,
    }
    write(assets / "generated" / "asset-system-summary.json", json.dumps(summary, indent=2))
    return summary


def asset_strip(concept: Concept, page_key: str, label: str) -> str:
    icon = PAGE_ICON.get(page_key, "consultation")
    n = concept.accent_index
    motion = MOTION_IDEAS[n % len(MOTION_IDEAS)].replace(" ", "-")
    if page_key == "index":
        icons = ["consultation", "laser", "skin", "safety", "aftercare", "results"]
    elif page_key in {"laser", "skin", "care", "results"}:
        icons = [icon, "evaluation", "safety", "aftercare"]
    elif page_key in {"journal", "blog", "faq"}:
        icons = [icon, "mission", "values", "consultation"]
    else:
        icons = [icon, "credentials", "contact", "care"]
    icon_html = "\n".join(
        f'<span><img class="asset-icon" src="assets/icons/{name}.svg" alt="Sofiati {name.replace("-", " ")} icon"><b>{name.replace("-", " ").title()}</b></span>'
        for name in icons
    )
    return dedent(
        f"""
        <!-- Sofiati Asset System Strip -->
        <section class="asset-signature-strip asset-strip-{concept.number}" data-asset-system="{concept.folder}" data-asset-motion="{motion}">
          <img class="asset-strip-divider" src="assets/botanical/gold-leaf-divider.svg" alt="" aria-hidden="true">
          <div class="asset-strip-copy">
            <p class="eyebrow">{esc(ASSET_ARCHETYPES[n])}</p>
            <h2>{esc(label)} visual system</h2>
            <p>Logo, FS monogram, portrait treatment, botanical detail and custom icons are built as a local Sofiati asset pack for this page.</p>
          </div>
          <div class="asset-icon-ribbon" aria-label="Custom Sofiati icon group">
            {icon_html}
          </div>
        </section>
        """
    ).strip()


def doctor_presence(concept: Concept) -> str:
    return dedent(
        f"""
            <aside class="doctor-presence doctor-presence-{concept.number}" data-doctor-presence>
              <img src="assets/portrait/franciele-portrait-{concept.slug}.{PORTRAIT_EXT}" alt="Franciele Sofiati, CRBM 6277, advanced aesthetic biomedicine specialist in Londrina, PR">
              <div>
                <p>Franciele Sofiati</p>
                <span>CRBM 6277 · Londrina, PR</span>
              </div>
            </aside>
            <img class="hero-botanical-accent" src="assets/botanical/sage-botanical-corner.svg" alt="" aria-hidden="true">
        """
    ).rstrip()


def patch_page(concept: Concept, page_key: str, label: str, filename: str) -> None:
    path = CONCEPTS_DIR / concept.folder / filename
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    hero_start = raw.find('<section class="hero')
    if hero_start == -1:
        return
    hero_end = raw.find("          </section>", hero_start)
    if hero_end == -1:
        return

    if "data-doctor-presence" not in raw:
        raw = raw[:hero_end] + doctor_presence(concept) + "\n" + raw[hero_end:]
        hero_end = raw.find("          </section>", hero_start)

    if "Sofiati Asset System Strip" not in raw:
        insert_at = hero_end + len("          </section>")
        raw = raw[:insert_at] + "\n" + asset_strip(concept, page_key, label) + raw[insert_at:]

    path.write_text(raw, encoding="utf-8")


def patch_partials(concept: Concept) -> None:
    partials = CONCEPTS_DIR / concept.folder / "partials"

    form = partials / "consultation-form.html"
    raw = form.read_text(encoding="utf-8")
    if "form-botanical-frame" not in raw:
        raw = raw.replace(
            f'<form class="consultation-form consultation-form-{concept.number}"',
            f'<form class="consultation-form consultation-form-{concept.number}"',
            1,
        )
        marker = 'novalidate>'
        raw = raw.replace(
            marker,
            marker + '\n  <img class="form-botanical-frame" src="assets/forms/consultation-form-frame.svg" alt="" aria-hidden="true">',
            1,
        )
    form.write_text(raw, encoding="utf-8")

    whatsapp = partials / "floating-whatsapp.html"
    raw = whatsapp.read_text(encoding="utf-8")
    if "assets/icons/whatsapp.svg" not in raw:
        raw = raw.replace(
            '<span aria-hidden="true">WA</span>',
            '<img src="assets/icons/whatsapp.svg" alt="" aria-hidden="true">',
        )
    whatsapp.write_text(raw, encoding="utf-8")

    top = partials / "back-to-top.html"
    raw = top.read_text(encoding="utf-8")
    if "assets/icons/back-to-top.svg" not in raw:
        raw = raw.replace(
            '<span aria-hidden="true">↑</span>',
            '<img src="assets/icons/back-to-top.svg" alt="" aria-hidden="true">',
        )
    top.write_text(raw, encoding="utf-8")

    footer = partials / "footer.html"
    raw = footer.read_text(encoding="utf-8")
    if "footer-botanical-mark" not in raw:
        raw = raw.replace(
            ">",
            '>\n  <img class="footer-botanical-mark" src="assets/botanical/monogram-wreath.svg" alt="" aria-hidden="true">',
            1,
        )
    footer.write_text(raw, encoding="utf-8")

    menu = partials / "mobile-menu.html"
    raw = menu.read_text(encoding="utf-8")
    if "mobile-menu-asset-bg" not in raw:
        raw = raw.replace(
            '<div class="mobile-menu-top">',
            '<img class="mobile-menu-asset-bg" src="assets/backgrounds/mobile-menu-background.svg" alt="" aria-hidden="true">\n'
            f'<img class="mobile-menu-avatar" src="assets/portrait/franciele-portrait-{concept.slug}.{PORTRAIT_EXT}" alt="Franciele Sofiati portrait">\n'
            '<div class="mobile-menu-top">',
            1,
        )
    menu.write_text(raw, encoding="utf-8")

    contact = partials / "contact-card.html"
    raw = contact.read_text(encoding="utf-8")
    if "contact-card-portrait" not in raw:
        raw = raw.replace(
            f'<article class="contact-card contact-card-{concept.number}" data-contact-card>',
            f'<article class="contact-card contact-card-{concept.number}" data-contact-card>\n'
            f'  <img class="contact-card-portrait" src="assets/portrait/franciele-portrait-{concept.slug}.{PORTRAIT_EXT}" alt="Franciele Sofiati portrait">\n'
            '  <img class="contact-card-botanical" src="assets/botanical/bronze-branch.svg" alt="" aria-hidden="true">',
            1,
        )
        raw = raw.replace(
            '<div>',
            '<div class="contact-card-routes">',
            1,
        )
    contact.write_text(raw, encoding="utf-8")


def append_css(concept: Concept) -> None:
    path = CONCEPTS_DIR / concept.folder / "css" / "style.css"
    raw = path.read_text(encoding="utf-8")
    if "Sofiati AI Asset System Overlay" in raw:
        return
    colors = palette_for(concept)
    idx = concept.accent_index
    portrait_place = [
        "right:clamp(16px,4vw,56px);bottom:clamp(16px,4vw,48px);",
        "left:clamp(16px,4vw,56px);bottom:clamp(16px,4vw,48px);",
        "right:8%;top:16%;",
        "left:8%;top:18%;",
        "right:50%;bottom:34px;transform:translateX(50%);",
    ][idx % 5]
    strip_grid = [
        ".asset-signature-strip{grid-template-columns:.42fr .86fr 1fr}",
        ".asset-signature-strip{grid-template-columns:1fr}.asset-icon-ribbon{grid-template-columns:repeat(6,minmax(0,1fr))}",
        ".asset-signature-strip{grid-template-columns:.9fr 1.1fr}.asset-strip-divider{grid-column:1/-1}",
        ".asset-signature-strip{grid-template-columns:280px 1fr}.asset-icon-ribbon{grid-column:1/-1}",
        ".asset-signature-strip{grid-template-columns:1.1fr .9fr}.asset-strip-copy{order:2}.asset-icon-ribbon{order:1}",
        ".asset-signature-strip{grid-template-columns:1fr 1fr 1fr}",
        ".asset-signature-strip{grid-template-columns:.7fr 1.3fr}.asset-strip-divider{display:none}",
        ".asset-signature-strip{grid-template-columns:1fr}.asset-strip-copy{text-align:center;justify-items:center}.asset-icon-ribbon{justify-content:center}",
        ".asset-signature-strip{grid-template-columns:.6fr .8fr 1.2fr}.asset-icon-ribbon span:nth-child(even){transform:translateY(18px)}",
        ".asset-signature-strip{grid-template-columns:1.25fr .75fr}.asset-strip-divider{position:absolute;inset:auto 8% 16px auto;width:min(280px,46vw);opacity:.42}",
    ][idx % 10]
    widget_shape = [
        "border-radius:999px;",
        "border-radius:12px;",
        "border-radius:28px 8px 28px 8px;",
        "border-radius:8px 28px 8px 28px;",
        "border-radius:50%;",
    ][idx % 5]
    css = f"""

/* Sofiati AI Asset System Overlay - {concept.number} {concept.name} */
:root {{
  --asset-sage:{colors["sage"]};
  --asset-deep:{colors["deep"]};
  --asset-ivory:{colors["ivory"]};
  --asset-cream:{colors["cream"]};
  --asset-bronze:{colors["bronze"]};
  --asset-gold:{colors["gold"]};
  --asset-divider:url("../assets/botanical/gold-leaf-divider.svg");
  --asset-bg:url("../assets/backgrounds/botanical-background.svg");
  --asset-texture:url("../assets/textures/soft-skin-texture.svg");
  --asset-form:url("../assets/forms/consultation-form-frame.svg");
  --asset-generated:url("../assets/generated/homepage-asset-composition.svg");
}}
body::before{{content:"";position:fixed;inset:0;z-index:-1;pointer-events:none;background-image:var(--asset-bg);background-size:{180 + idx * 7}px {180 + idx * 7}px;opacity:{0.035 + (idx % 6) * 0.008:.3f};mix-blend-mode:multiply}}
.hero{{isolation:isolate}}
.hero::before{{content:"";position:absolute;inset:{6 + idx % 9}% {4 + idx % 7}% auto auto;width:min({150 + idx * 3}px,28vw);aspect-ratio:1;background:var(--asset-generated) center/contain no-repeat;opacity:.18;z-index:-1;pointer-events:none}}
.hero-botanical-accent{{position:absolute;z-index:4;width:min({140 + idx * 4}px,30vw);{["right:4%;top:14%;","left:4%;top:18%;","right:12%;bottom:10%;","left:10%;bottom:12%;"][idx % 4]}opacity:.66;filter:drop-shadow(0 12px 24px rgba(37,35,33,.08));pointer-events:none}}
.doctor-presence{{position:absolute;{portrait_place}z-index:6;width:min({150 + (idx % 8) * 12}px,36vw);display:grid;gap:8px;padding:8px;background:rgba(248,247,242,.9);border:1px solid color-mix(in srgb,var(--asset-bronze) 48%,transparent);box-shadow:0 18px 44px rgba(37,35,33,.14);backdrop-filter:blur(14px);border-radius:{[999, 8, 28, 80, 18][idx % 5]}px}}
.doctor-presence img{{width:100%;aspect-ratio:{["1/1","4/5","3/4","1/1","5/6"][idx % 5]};object-fit:cover;border-radius:inherit}}
.doctor-presence div{{display:grid;gap:2px;padding:0 4px 4px}}
.doctor-presence p{{font-family:Georgia,serif;color:var(--asset-deep);font-size:.95rem}}
.doctor-presence span{{font-size:.64rem;text-transform:uppercase;letter-spacing:.11em;color:var(--muted)}}
.asset-signature-strip{{position:relative;width:var(--page);margin:auto;padding:clamp(32px,6vw,78px) 0;display:grid;gap:clamp(16px,4vw,44px);align-items:center;border-top:1px solid var(--line);border-bottom:1px solid var(--line);background-image:linear-gradient(90deg,color-mix(in srgb,var(--asset-sage) {8 + idx % 12}%,transparent),transparent),var(--asset-texture);background-size:auto,{220 + idx * 3}px {220 + idx * 3}px}}
{strip_grid}
.asset-strip-divider{{width:min(260px,54vw);opacity:.88;align-self:center}}
.asset-strip-copy{{display:grid;gap:12px;max-width:640px}}
.asset-strip-copy h2{{font-size:clamp(1.8rem,3.5vw,3.8rem)}}
.asset-strip-copy p:not(.eyebrow){{color:var(--muted);max-width:58ch}}
.asset-icon-ribbon{{display:grid;grid-template-columns:repeat(auto-fit,minmax(92px,1fr));gap:10px}}
.asset-icon-ribbon span{{min-height:112px;display:grid;align-content:center;justify-items:center;gap:8px;padding:12px;border:1px solid color-mix(in srgb,var(--asset-bronze) 24%,var(--line));background:rgba(255,255,255,.58);border-radius:{[8, 18, 999, 28, 4][idx % 5]}px;box-shadow:0 12px 30px rgba(37,35,33,.055);transition:transform .28s ease,background .28s ease,border-color .28s ease}}
.asset-icon-ribbon span:hover{{transform:translateY(-4px) rotate({[-1.5, 1.2, -.8, 1.8, 0][idx % 5]}deg);background:color-mix(in srgb,var(--asset-gold) 18%,white);border-color:var(--asset-bronze)}}
.asset-icon{{width:52px;aspect-ratio:1;object-fit:contain}}
.asset-icon-ribbon b{{font-size:.68rem;text-transform:uppercase;letter-spacing:.1em;text-align:center;color:var(--muted)}}
.home-route{{position:relative;overflow:hidden}}
.home-route::before{{content:"";position:absolute;inset:auto 14px 14px auto;width:72px;aspect-ratio:1;background:var(--asset-divider) center/contain no-repeat;opacity:.18}}
.home-index-journal,.page-journal .content-system,.page-blog .content-system{{background-image:url("../assets/journal/journal-thumbnail-{(idx % 3) + 1}.svg");background-repeat:no-repeat;background-position:right clamp(16px,5vw,80px) top clamp(16px,5vw,70px);background-size:min(180px,32vw)}}
.service-architecture{{position:relative}}
.service-architecture::after{{content:"";position:absolute;right:0;bottom:clamp(24px,6vw,80px);width:min(220px,36vw);aspect-ratio:1;background:url("../assets/service/{["laser","skin","care","results"][idx % 4]}-service-visual.svg") center/contain no-repeat;opacity:.32;pointer-events:none}}
.form-section{{position:relative;background-image:linear-gradient(135deg,color-mix(in srgb,var(--asset-sage) {10 + idx % 10}%,transparent),transparent 56%),url("../assets/textures/clinical-paper-texture.svg");background-size:auto,{240 + idx * 2}px {240 + idx * 2}px}}
.consultation-form{{isolation:isolate}}
.form-botanical-frame{{position:absolute;right:{8 + idx % 12}px;top:{8 + idx % 16}px;width:min(150px,34vw);opacity:.2;z-index:-1;pointer-events:none}}
.consultation-form input:focus,.consultation-form select:focus,.consultation-form textarea:focus{{outline:2px solid color-mix(in srgb,var(--asset-gold) 78%,white);outline-offset:2px;box-shadow:0 0 0 6px color-mix(in srgb,var(--asset-sage) 16%,transparent)}}
.mobile-menu{{background-image:linear-gradient({120 + idx * 9}deg,rgba(37,35,33,.54),rgba(37,35,33,.1)),url("../assets/backgrounds/mobile-menu-background.svg"),linear-gradient(135deg,var(--deep-sage),var(--ink));background-size:auto,{320 + idx * 6}px {320 + idx * 6}px,auto}}
.mobile-menu-asset-bg{{position:absolute;inset:auto 4% 8% auto;width:min(380px,74vw);opacity:.18;pointer-events:none}}
.mobile-menu-avatar{{position:absolute;right:clamp(18px,6vw,68px);top:clamp(82px,14vw,142px);width:min(116px,26vw);aspect-ratio:1;object-fit:cover;border-radius:{[999, 18, 8, 42, 70][idx % 5]}px;border:1px solid rgba(255,255,255,.34);box-shadow:0 18px 46px rgba(0,0,0,.18)}}
.footer-botanical-mark{{width:min(220px,45vw);opacity:.26;align-self:start;filter:{["none","saturate(.7) brightness(1.15)","sepia(.15)","contrast(.9)","brightness(1.08)"][idx % 5]}}}
.site-footer{{position:relative;overflow:hidden}}
.site-footer::after{{content:"";position:absolute;right:clamp(18px,6vw,92px);bottom:clamp(18px,6vw,92px);width:min(300px,44vw);aspect-ratio:1;background:url("../assets/botanical/footer-botanical-stamp.svg"),url("../assets/botanical/monogram-wreath.svg") center/contain no-repeat;opacity:.10;pointer-events:none}}
.contact-card{{position:relative;overflow:hidden}}
.contact-card-portrait{{width:min(132px,36vw);aspect-ratio:1;object-fit:cover;border-radius:{[999, 16, 64, 8, 28][idx % 5]}px;box-shadow:0 14px 34px rgba(37,35,33,.1)}}
.contact-card-botanical{{position:absolute;right:18px;top:18px;width:120px;opacity:.16;pointer-events:none}}
.contact-card-routes a{{display:inline-flex;align-items:center;gap:8px}}
.floating-whatsapp,.back-to-top{{{widget_shape}background:color-mix(in srgb,var(--asset-gold) {18 + idx % 24}%,white);border-color:color-mix(in srgb,var(--asset-bronze) 42%,var(--line))}}
.floating-whatsapp img,.back-to-top img{{width:30px;height:30px;object-fit:contain}}
.asset-ready .hero-botanical-accent{{animation:asset-sway-{concept.number} {5 + idx % 5}s ease-in-out infinite alternate}}
@keyframes asset-sway-{concept.number}{{from{{transform:translateY(0) rotate({-(idx % 4)}deg)}}to{{transform:translateY({8 + idx % 10}px) rotate({2 + idx % 5}deg)}}}}
@media(max-width:780px){{
  .doctor-presence{{position:relative;inset:auto!important;right:auto!important;left:auto!important;top:auto!important;bottom:auto!important;transform:none!important;width:min(220px,72vw);margin:12px 0 0;grid-template-columns:72px 1fr;align-items:center;border-radius:18px}}
  .doctor-presence img{{aspect-ratio:1}}
  .hero-botanical-accent{{width:120px;opacity:.34}}
  .asset-signature-strip{{grid-template-columns:1fr!important}}
  .asset-icon-ribbon{{grid-template-columns:repeat(2,minmax(0,1fr))!important}}
  .mobile-menu-avatar{{position:relative;right:auto;top:auto;width:86px}}
}}
"""
    path.write_text(raw.rstrip() + css + "\n", encoding="utf-8")


def append_js(concept: Concept) -> None:
    path = CONCEPTS_DIR / concept.folder / "js" / "main.js"
    raw = path.read_text(encoding="utf-8")
    if "Sofiati AI asset motion overlay" in raw:
        return
    idx = concept.accent_index
    motion = MOTION_IDEAS[idx % len(MOTION_IDEAS)].replace(" ", "-")
    js = f"""

/* Sofiati AI asset motion overlay - {concept.number} {concept.name} */
(() => {{
  const motion = "{motion}";
  const concept = "{concept.folder}";
  const boot = () => {{
    document.body.classList.add("asset-ready", "asset-motion-" + motion);
    document.body.dataset.assetSystem = concept;
    const root = document.documentElement;
    const onScroll = () => {{
      const max = Math.max(1, document.documentElement.scrollHeight - window.innerHeight);
      root.style.setProperty("--asset-scroll", (window.scrollY / max).toFixed(4));
    }};
    onScroll();
    window.addEventListener("scroll", onScroll, {{ passive: true }});
    document.querySelectorAll(".asset-icon-ribbon span").forEach((item, index) => {{
      item.style.setProperty("--asset-index", index);
      item.addEventListener("pointerenter", () => {{
        item.animate([
          {{ transform: "translateY(0) rotate(0deg)" }},
          {{ transform: "translateY({-4 - idx % 8}px) rotate({-3 + idx % 7}deg)" }}
        ], {{ duration: {260 + idx * 5}, easing: "ease-out", fill: "forwards" }});
      }});
      item.addEventListener("pointerleave", () => {{
        item.animate([
          {{ transform: "translateY({-4 - idx % 8}px) rotate({-3 + idx % 7}deg)" }},
          {{ transform: "translateY(0) rotate(0deg)" }}
        ], {{ duration: {220 + idx * 3}, easing: "ease-out", fill: "forwards" }});
      }});
    }});
    document.querySelectorAll("[data-asset-motion]").forEach((strip) => {{
      const divider = strip.querySelector(".asset-strip-divider");
      if (!divider || !("IntersectionObserver" in window)) return;
      const io = new IntersectionObserver((entries) => {{
        entries.forEach((entry) => {{
          if (!entry.isIntersecting) return;
          divider.animate([
            {{ opacity: .18, transform: "scaleX(.72) translateY(10px)" }},
            {{ opacity: .92, transform: "scaleX(1) translateY(0)" }}
          ], {{ duration: {720 + idx * 11}, easing: "cubic-bezier(.22,.61,.36,1)", fill: "forwards" }});
          io.unobserve(strip);
        }});
      }}, {{ threshold: .22 }});
      io.observe(strip);
    }});
    const portrait = document.querySelector("[data-doctor-presence]");
    if (portrait) {{
      portrait.addEventListener("pointermove", (event) => {{
        const rect = portrait.getBoundingClientRect();
        const dx = ((event.clientX - rect.left) / rect.width - .5) * {4 + idx % 8};
        const dy = ((event.clientY - rect.top) / rect.height - .5) * {4 + idx % 8};
        portrait.style.transform = `translate3d(${{dx}}px, ${{dy}}px, 0)`;
      }});
      portrait.addEventListener("pointerleave", () => portrait.style.transform = "");
    }}
  }};
  if (window.SofiatiPartialsReady) {{
    window.SofiatiPartialsReady.then(boot);
  }} else if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", boot, {{ once: true }});
  }} else {{
    boot();
  }}
}})();
"""
    path.write_text(raw.rstrip() + js + "\n", encoding="utf-8")


def write_design_files(concept: Concept, summary: dict[str, object]) -> None:
    idx = concept.accent_index
    folder = CONCEPTS_DIR / concept.folder
    dna = f"""
    # {concept.number} {concept.name} Design DNA

    Concept name: {concept.name}

    Visual idea: {concept.archetype} translated into a Sofiati visual world, using {ASSET_ARCHETYPES[idx]} as the governing asset language.

    Asset idea: Local assets combine the approved logo, FS monogram, signature mark, a custom Franciele portrait treatment, botanical dividers, service visuals, form framing and an icon pack.

    Colour usage idea: Sage and ivory hold the quiet clinical base, bronze and champagne gold draw attention to credentials, dividers and micro-details, and deep green-black gives professional contrast.

    Typography idea: Elegant serif display rhythm for trust and editorial calm, paired with restrained sans-serif labels for clinical clarity.

    Navigation idea: {concept.header} on desktop and {concept.menu} on mobile, with botanical background assets and a small portrait cue in the menu.

    Hero idea: The first viewport mixes the existing image-led Sofiati composition with the FS monogram, a custom botanical accent and a concept-specific portrait module for Franciele.

    Doctor portrait idea: {PORTRAIT_IDEAS[idx % len(PORTRAIT_IDEAS)]}, generated from `brand identity/Dr Fran.png` and saved as `{summary["portrait"]}`.

    Botanical/gold idea: {BOTANICAL_IDEAS[idx % len(BOTANICAL_IDEAS)]} appears in the hero, section strip, mobile menu, form and footer.

    Icon idea: A custom {ASSET_ARCHETYPES[idx]} SVG icon pack covers consultation, laser, skin, care, evaluation, safety, aftercare, results, journal, mission, values, contact, technology, credentials, WhatsApp and back to top.

    Animation idea: {MOTION_IDEAS[idx % len(MOTION_IDEAS)]} controls strip dividers, icon hover behaviour, portrait movement and scroll CSS variables.

    Form idea: {FORM_IDEAS[idx % len(FORM_IDEAS)]} with a botanical frame, focus glow, privacy acknowledgement, honeypot, loading, success and error states.

    Footer idea: {FOOTER_IDEAS[idx % len(FOOTER_IDEAS)]} using the white logo, monogram wreath, public contact routes and Londrina, PR only.

    How this concept differs from the other 49: It is identified by `{ASSET_ARCHETYPES[idx]}`, portrait treatment `{PORTRAIT_IDEAS[idx % len(PORTRAIT_IDEAS)]}`, motion `{MOTION_IDEAS[idx % len(MOTION_IDEAS)]}`, form `{FORM_IDEAS[idx % len(FORM_IDEAS)]}` and footer `{FOOTER_IDEAS[idx % len(FOOTER_IDEAS)]}`. The HTML, CSS and JS include unique markers for this concept.
    """
    write(folder / "design-dna.md", dedent(dna))

    notes = f"""
    # {concept.number} {concept.name} Asset Notes

    Approved source assets: the concept keeps the Sofiati logo, FS monogram, signature mark and colour language from `brand identity/`.

    Local asset pack:
    - `assets/icons/`: {len(ICON_NAMES)} custom SVG icons in this concept's style.
    - `assets/botanical/`: gold and sage dividers, branches, corner frames, separators and monogram wreaths.
    - `assets/portrait/`: Franciele portrait treatment from `Dr Fran.png`.
    - `assets/backgrounds/`: botanical page and mobile-menu backgrounds.
    - `assets/textures/`: soft skin texture and clinical paper texture.
    - `assets/forms/`: consultation form frame.
    - `assets/animations/`: motion path SVG used by the concept movement language.
    - `assets/journal/`: editorial thumbnails for journal/blog sections.
    - `assets/service/`: laser, skin, care and results service visuals.
    - `assets/generated/`: homepage composition and machine-readable asset summary.

    Usage:
    Assets are referenced in page hero modules, asset strips, the consultation form partial, contact card, floating widgets, mobile menu, section backgrounds, footer and JavaScript motion overlay.

    Brand safety:
    No fake patients, fake procedures, before-and-after scenes or medical result claims are generated. The portrait asset is a replaceable treatment of the approved `Dr Fran.png` reference.
    """
    write(folder / "asset-notes.md", dedent(notes))


def write_project_audits(matrix: list[dict[str, object]]) -> None:
    DATA_DIR.mkdir(exist_ok=True)
    write(
        DATA_DIR / "brand-identity-audit.md",
        """
        # Sofiati Brand Identity Audit

        Approved source folder: `brand identity/`.

        Existing assets:
        - Primary logo family: sage, white, bronze/full-colour and JPG variants.
        - Secondary/sub-logo family: FS monogram inside a circular botanical seal, including sage, white and bronze PNG variants.
        - Signature mark: handwritten Franciele Sofiati signature in sage, white and PNG/JPG variants.
        - Story background: tall sage field with signature lockup and a fine bronze vertical line.
        - Pattern assets: repeating FS monogram pattern and ivory pattern variants.
        - Moodboard: sage botanical imagery, soft skin/leaf references, champagne gold, ivory and calm clinical composition.
        - Typography/palette board: serif display direction, handwritten signature, Montserrat-like sans-serif labels and palette swatches.
        - Portrait reference: `Dr Fran.png`, a professional editorial doctor portrait.

        Visual language:
        The identity is soft, professional, feminine and clinical without becoming generic spa design. It uses sage as the main field colour, ivory and cream as breathing space, bronze/champagne gold as refined detail, and dark green-black for authority. Botanical linework is delicate and precise, not lush or messy. The FS monogram is central and should work as a watermark, seal, avatar, footer stamp and credential cue.

        Colour direction:
        Extracted colours include sage `#A2AEA0`, `#A3AFA1`, muted sage `#7A8B81`, ivory `#F2EEE3`, cream `#F8F7F2`, deep green `#485041`, bronze `#9A6B35`, warm clay `#8F745F`, and champagne gold `#CDAA78`.

        Typography direction:
        Use an elegant high-trust serif for headlines and a clean modern sans-serif for labels/forms/navigation. Preserve the signature mark as a graphic accent rather than imitating it in body text.

        Botanical/gold direction:
        Create pressed-leaf dividers, sage line branches, bronze corner frames, monogram wreaths, section separators and subtle pattern overlays. Gold should be a line/detail material, not heavy black-and-gold luxury.

        Asset gaps:
        The approved folder does not include enough web-ready icons, page-specific botanical dividers, form visuals, responsive background systems, motion assets, service visuals, ethical results graphics, mobile menu backgrounds, footer stamps or concept-specific portrait treatments.

        AI-assisted assets needed:
        This build creates brand-safe SVG/CSS/PIL-generated assets for icon systems, botanical details, portrait treatments, abstract skin texture, clinical technology graphics, consultation form frames, journal thumbnails, service visuals and motion paths.

        Usage across 50 sites:
        Every concept keeps the shared Sofiati identity but receives its own local asset pack, design DNA, portrait treatment, icon style, botanical/gold strategy, CSS asset integration and JavaScript motion language.
        """,
    )
    write(
        DATA_DIR / "brand-colour-audit.md",
        """
        # Sofiati Brand Colour Audit

        Core palette:
        - Sage: `#A2AEA0`, `#A3AFA1`
        - Muted/deep sage: `#7A8B81`, `#728479`, `#485041`
        - Ivory/cream: `#F2EEE3`, `#F3EFE4`, `#F8F7F2`, `#F4F0E6`
        - Bronze: `#9A6B35`, `#8F745F`, `#734011`
        - Champagne gold: `#CDAA78`, `#D2C5A7`, `#DACCB7`
        - Professional dark: `#192018`, `#252321`, `#344039`

        Application rules:
        Sage should carry background fields, menus and calm brand surfaces. Ivory and cream should protect spacing and readability. Bronze and gold should appear as lines, borders, botanical details, credential marks and icons. Deep green-black should be reserved for text authority, CTAs and high-contrast editorial sections.

        Avoid:
        Hospital blue, neon, pink salon palettes, heavy black-gold luxury and one-note beige layouts.
        """,
    )
    write(
        DATA_DIR / "brand-typography-audit.md",
        """
        # Sofiati Brand Typography Audit

        Observed direction:
        The identity combines an elegant serif/logo structure, handwritten signature mark and modern sans-serif support typography. The palette/type board suggests premium clinical calm rather than fashion spectacle.

        Website direction:
        - Use Georgia or a similar refined serif fallback for editorial headings.
        - Use Inter/system sans-serif for navigation, labels, forms and dense clinical information.
        - Use uppercase micro-labels sparingly for credentials, concept numbers and small navigation cues.
        - Use the approved signature asset as an image mark in footers, forms or profile moments.

        Spacing:
        Soft premium spacing, readable line lengths and calm section rhythm should matter more than dense content.
        """,
    )
    write(ROOT_CSS / "brand-colours.css", """:root{--sofiati-sage:#A2AEA0;--sofiati-sage-deep:#485041;--sofiati-ivory:#F2EEE3;--sofiati-cream:#F8F7F2;--sofiati-bronze:#9A6B35;--sofiati-gold:#CDAA78;--sofiati-ink:#252321}""")
    write(ROOT_CSS / "brand-typography.css", """:root{--sofiati-serif:Georgia,"Times New Roman",serif;--sofiati-sans:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;--sofiati-label-spacing:.12em}""")

    matrix_json = {"conceptCount": len(matrix), "assetsPerConcept": matrix}
    write(DATA_DIR / "asset-usage-matrix.json", json.dumps(matrix_json, indent=2))
    rows = [
        "| Concept | Asset strategy | Portrait | Icon style | Botanical/gold | Motion | Form | Footer |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for item in matrix:
        rows.append(
            "| {concept} | {assetArchetype} | {portraitIdea} | {iconStyle} | {botanicalIdea} | {motionIdea} | {formIdea} | {footerIdea} |".format(
                **item
            )
        )
    write(DATA_DIR / "asset-usage-matrix.md", "# Sofiati Asset Usage Matrix\n\n" + "\n".join(rows))
    write(
        DATA_DIR / "final-asset-audit.md",
        f"""
        # Final Sofiati Asset Audit

        Generated concept asset systems: {len(matrix)}

        Per concept:
        - 16 SVG icons.
        - 6 botanical/gold SVG assets.
        - 1 custom Franciele portrait treatment.
        - 2 background systems.
        - 2 texture systems.
        - 1 form frame.
        - 1 motion path.
        - 3 journal thumbnails.
        - 4 service visuals.
        - 1 generated homepage composition.

        Integration checks:
        - Every page includes the hero doctor presence and an asset system strip.
        - Every homepage visibly includes logo, FS monogram, portrait, botanical detail, icon group, image-led services, consultation form, contact card and premium footer.
        - Every inner page includes page-specific iconography, botanical/gold detail, form/contact prompt and footer identity.
        - CSS references local backgrounds, textures, forms, journal, service, generated, botanical and icon assets.
        - JavaScript adds concept-specific asset motion, scroll variables, icon hover movement and portrait interaction.

        Safety checks:
        - No fake patients, fake procedures, fake before-and-after images or invented result claims were created.
        - Portrait treatments are generated from the approved `brand identity/Dr Fran.png` and are replaceable.
        - Contact location remains Londrina, PR only.
        """,
    )


def build() -> None:
    create_root_brand_assets()
    matrix: list[dict[str, object]] = []
    concepts = [Concept(*item) for item in CONCEPTS]
    for concept in concepts:
        summary = create_concept_assets(concept)
        patch_partials(concept)
        append_css(concept)
        append_js(concept)
        for page_key, label, filename, *_ in PAGE_SPECS:
            patch_page(concept, page_key, label, filename)
        write_design_files(concept, summary)
        idx = concept.accent_index
        matrix.append(
            {
                "concept": concept.folder,
                "name": concept.name,
                "assetArchetype": ASSET_ARCHETYPES[idx],
                "portrait": summary["portrait"],
                "portraitIdea": PORTRAIT_IDEAS[idx % len(PORTRAIT_IDEAS)],
                "iconStyle": f"{ASSET_ARCHETYPES[idx]} icon pack",
                "botanicalIdea": BOTANICAL_IDEAS[idx % len(BOTANICAL_IDEAS)],
                "motionIdea": MOTION_IDEAS[idx % len(MOTION_IDEAS)],
                "formIdea": FORM_IDEAS[idx % len(FORM_IDEAS)],
                "footerIdea": FOOTER_IDEAS[idx % len(FOOTER_IDEAS)],
                "directories": summary["folders"],
            }
        )
    write_project_audits(matrix)
    print(f"Built Sofiati asset systems for {len(concepts)} concepts")


if __name__ == "__main__":
    build()
