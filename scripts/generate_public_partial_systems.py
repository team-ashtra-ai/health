#!/usr/bin/env python3
"""Generate the final Sofiati public partial systems across all 50 concepts."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

try:
    from PIL import Image, ImageColor
except ImportError:  # pragma: no cover - reported cleanly at runtime.
    Image = None
    ImageColor = None


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
DOCS_DIR = ROOT / "docs" / "script-runs"
DESIGN_DOC = ROOT / "docs" / "design-destination-bible" / "12-partial-redesign-destinations.md"
BRAND_DIR = ROOT / "assets" / "brand"
APPROVED_LOGO_SOURCE = ROOT / "logo.png"

MAIN_LINKS = [
    ("Home", "index.html"),
    ("About", "about.html"),
    ("Care", "care.html"),
    ("Laser", "laser.html"),
    ("Skin", "skin.html"),
    ("Results", "results.html"),
    ("Journal", "journal.html"),
    ("Contact", "contact.html"),
]

FOOTER_LINKS = [
    ("Home", "index.html"),
    ("About", "about.html"),
    ("Care", "care.html"),
    ("Laser", "laser.html"),
    ("Skin", "skin.html"),
    ("Results", "results.html"),
    ("Journal", "journal.html"),
    ("Contact", "contact.html"),
    ("Consultation", "consultation.html"),
    ("Values", "values.html"),
    ("Mission", "mission.html"),
    ("Testimonials", "testimonials.html"),
    ("FAQ", "faq.html"),
    ("Privacy", "privacy.html"),
    ("Cookies", "cookies.html"),
    ("Accessibility", "accessibility.html"),
    ("Sitemap", "sitemap.html"),
]

BRAND_NAME = "Franciele Sofiati Biomédica"
DESCRIPTION = "Biomedicine-led skin, laser and aesthetic care with calm, consultation-first guidance."
WHATSAPP_URL = "https://wa.me/5543991043536"
INSTAGRAM_URL = "https://www.instagram.com/fransofiati_biomedica/"

CSS_START = "/* SOFIATI FINAL PUBLIC PARTIAL SYSTEM START */"
CSS_END = "/* SOFIATI FINAL PUBLIC PARTIAL SYSTEM END */"

APPROVED_LOGO_FILES = [
    "sofiati-logo-primary.svg",
    "sofiati-logo-primary.png",
    "sofiati-logo-dark.svg",
    "sofiati-logo-light.svg",
    "sofiati-logo-sage.svg",
    "sofiati-logo-gold.svg",
    "sofiati-logo-monogram.svg",
    "sofiati-logo-monogram-light.svg",
    "sofiati-logo-monogram-dark.svg",
    "sofiati-logo-primary-transparent.png",
    "sofiati-logo-dark-transparent.png",
    "sofiati-logo-light-transparent.png",
    "sofiati-logo-sage-transparent.png",
    "sofiati-logo-gold-transparent.png",
    "sofiati-logo-monogram-transparent.png",
    "sofiati-logo-monogram-light-transparent.png",
    "sofiati-logo-monogram-dark-transparent.png",
]

APPROVED_LOGO_WEBP_FILES = [
    "sofiati-logo-primary-transparent.webp",
    "sofiati-logo-dark-transparent.webp",
    "sofiati-logo-light-transparent.webp",
    "sofiati-logo-sage-transparent.webp",
    "sofiati-logo-gold-transparent.webp",
    "sofiati-logo-monogram-transparent.webp",
    "sofiati-logo-monogram-light-transparent.webp",
    "sofiati-logo-monogram-dark-transparent.webp",
]


@dataclass(frozen=True)
class PartialSpec:
    number: int
    signature: str
    header: str
    mobile: str
    footer: str
    banner: str
    cookie: str
    floating: str
    palette: tuple[str, str, str, str, str, str]
    motif: str
    note: str

    @property
    def code(self) -> str:
        return f"{self.number:02d}"


SPECS = [
    PartialSpec(1, "Couture Editorial Masthead", "editorial-masthead", "editorial-contents", "editorial-index", "right-rule", "editorial", "fine-rule", ("#252321", "#fbfaf5", "#9a6b35", "#a2aea0", "#f3efe5", "#403a32"), "numbered index", "A calm publication-like navigation with broad spacing."),
    PartialSpec(2, "Floating Capsule Navigation", "floating-capsule", "bottom-sheet", "rounded-card", "capsule", "capsule", "soft-capsule", ("#f8f7f2", "#263026", "#87927f", "#d8cbb7", "#fffdf8", "#596653"), "capsules", "Separated capsule navigation and detached actions."),
    PartialSpec(3, "Left Atelier Rail", "atelier-rail", "left-drawer", "vertical-directory", "thin-left", "atelier", "atelier-tab", ("#f2eee3", "#252321", "#b88954", "#798a80", "#fbfaf5", "#3a3631"), "atelier rail", "Private studio rail with a narrow vertical rhythm."),
    PartialSpec(4, "Mobile App Dock", "app-dock", "app-sheet", "settings-list", "micro-strip", "app", "dock-dot", ("#eef3ee", "#263026", "#6f7b68", "#c39b6a", "#fffdf8", "#485041"), "mobile dock", "Mobile-first chrome with large thumb-friendly controls."),
    PartialSpec(5, "Split Utility and Main Navigation", "split-utility", "utility-sheet", "structured-zones", "top-line", "split", "split-stack", ("#fbfaf5", "#252321", "#9a6b35", "#dce5da", "#f8f7f2", "#5e5548"), "split strips", "Utility, navigation, and CTA are visibly separated."),
    PartialSpec(6, "Monogram Axis", "monogram-axis", "centered-axis", "monogram-watermark", "monogram", "monogram", "axis-button", ("#263026", "#fbfaf5", "#cdaa78", "#a2aea0", "#f2eee3", "#1f261f"), "monogram axis", "A large identity mark anchors the system."),
    PartialSpec(7, "Command Bar Interface", "command-bar", "command-palette", "command-footer", "command", "command", "command-key", ("#f8f7f2", "#252321", "#87927f", "#9a6b35", "#fffdf8", "#4a4640"), "command rows", "Soft command rows feel interface-like without becoming cold."),
    PartialSpec(8, "Botanical Drawer With Visible Nav", "botanical-drawer", "botanical-drawer", "botanical-groups", "leaf-line", "botanical", "leaf-button", ("#eef3ee", "#263026", "#798a80", "#b88954", "#fbfaf5", "#485041"), "botanical dividers", "Fine botanical separators keep the structure tactile."),
    PartialSpec(9, "Concierge Guidance System", "concierge-guide", "concierge-cards", "concierge-footer", "guide", "concierge", "guide-pin", ("#fff7f6", "#252321", "#b86a63", "#a2aea0", "#fffdf8", "#743b37"), "guidance cards", "Human guidance cards complement the stable navigation."),
    PartialSpec(10, "Care Pathway Timeline", "pathway-timeline", "timeline-menu", "journey-footer", "pathway", "journey", "timeline-dot", ("#f3efe5", "#252321", "#9a6b35", "#798a80", "#fbfaf5", "#5f3f1f"), "timeline", "A light pathway line makes the route feel guided."),
    PartialSpec(11, "Layered Editorial Panels", "layered-panels", "layered-cards", "paper-blocks", "paper", "paper", "paper-corner", ("#fbfaf5", "#252321", "#b88954", "#dce5da", "#fffdf8", "#706b63"), "paper layers", "Paper-like panels create editorial depth."),
    PartialSpec(12, "Ink Fashion Editorial", "ink-editorial", "ink-menu", "ink-index", "ink", "ink", "ink-arrow", ("#161513", "#fbfaf5", "#c39b6a", "#87927f", "#252321", "#f2eee3"), "ink contrast", "High contrast, uppercase, and disciplined spacing."),
    PartialSpec(13, "Portal Dashboard Tiles", "portal-tiles", "tile-grid", "module-footer", "portal", "module", "tile-button", ("#eef3ee", "#263026", "#6f7b68", "#cdaa78", "#fbfaf5", "#485041"), "portal tiles", "Modular portal tiles keep dense links scannable."),
    PartialSpec(14, "Asymmetric Studio Composition", "asymmetric-studio", "staggered-menu", "asymmetric-footer", "offset", "studio", "offset-button", ("#f8f7f2", "#252321", "#9a6b35", "#b6aa98", "#fffdf8", "#5e5548"), "asymmetry", "Intentional offset alignment without broken spacing."),
    PartialSpec(15, "Transparent Hero Overlay", "transparent-overlay", "frosted-overlay", "image-led", "overlay", "frosted", "glass-circle", ("#252321", "#fbfaf5", "#cdaa78", "#a2aea0", "#f8f7f2", "#3a3631"), "transparent layer", "Frosted chrome over a solid readable surface."),
    PartialSpec(16, "Card Preview Navigation", "preview-cards", "preview-menu", "card-footer", "preview", "card", "card-notch", ("#fbfaf5", "#263026", "#b88954", "#dce5da", "#fffdf8", "#596653"), "preview cards", "Context cards support the page links."),
    PartialSpec(17, "Refined Icon Tile System", "icon-tiles", "icon-grid", "icon-footer", "icon", "icon", "icon-tile", ("#f2eee3", "#252321", "#798a80", "#c39b6a", "#fbfaf5", "#485041"), "icon tiles", "Tiny icon cells give the system quick scan points."),
    PartialSpec(18, "Premium Tabbed Interface", "tabbed-interface", "tabbed-menu", "tabbed-footer", "tabbed", "tabbed", "tab-button", ("#eef3ee", "#252321", "#6f7b68", "#b88954", "#fffdf8", "#3a3631"), "tabs", "Tabs organize the sitemap without hiding required links."),
    PartialSpec(19, "Luxury Ribbon Navigation", "ribbon-nav", "ribbon-menu", "ribbon-footer", "ribbon", "ribbon", "ribbon-tail", ("#f8f7f2", "#252321", "#9a6b35", "#edc6c0", "#fffdf8", "#743b37"), "ribbons", "Subtle ribbon bands add a premium ceremonial feel."),
    PartialSpec(20, "Botanical Frame Navigation", "botanical-frame", "framed-menu", "framed-footer", "frame", "frame", "frame-corner", ("#eef3ee", "#263026", "#87927f", "#c39b6a", "#fbfaf5", "#485041"), "botanical frame", "Fine frames and corner marks wrap the chrome."),
    PartialSpec(21, "Floating Island Header", "floating-islands", "floating-card", "island-footer", "island", "island", "island-stack", ("#fbfaf5", "#252321", "#6f7b68", "#d8cbb7", "#fffdf8", "#4a4640"), "islands", "Detached islands align to one calm grid."),
    PartialSpec(22, "Scroll Progress Navigation", "progress-nav", "progress-menu", "explore-footer", "progress", "progress", "progress-button", ("#f3efe5", "#252321", "#798a80", "#9a6b35", "#fbfaf5", "#5e5548"), "progress line", "A subtle progress line guides reading."),
    PartialSpec(23, "Oversized Wordmark Architecture", "oversized-wordmark", "oversized-menu", "typographic-footer", "wordmark", "type", "type-square", ("#252321", "#fbfaf5", "#c39b6a", "#a2aea0", "#f8f7f2", "#161513"), "oversized type", "Large type anchors the chrome architecture."),
    PartialSpec(24, "Formal Clinical Authority", "formal-clinical", "clinical-menu", "professional-footer", "formal", "clinical", "clinical-square", ("#fbfaf5", "#252321", "#485041", "#9a6b35", "#fffdf8", "#263026"), "clinical order", "The most conservative, formally ordered system."),
    PartialSpec(25, "Image Strip Chrome", "image-strip", "image-strip-menu", "image-divider-footer", "image", "image", "strip-button", ("#f8f7f2", "#252321", "#b88954", "#dce5da", "#fffdf8", "#596653"), "image strip", "A tactile strip separates image detail from readable nav."),
    PartialSpec(26, "Accordion Hierarchy System", "accordion-header", "accordion-menu", "accordion-footer", "accordion", "accordion", "accordion-button", ("#eef3ee", "#252321", "#6f7b68", "#c39b6a", "#fbfaf5", "#485041"), "accordion", "Hierarchy panels are visible without hiding required links."),
    PartialSpec(27, "Footer-First Luxury System", "quiet-header", "simple-menu", "footer-hero", "quiet", "quiet", "footer-dot", ("#fbfaf5", "#252321", "#9a6b35", "#a2aea0", "#fffdf8", "#5f3f1f"), "footer hero", "The header is restrained so the closing footer can lead."),
    PartialSpec(28, "Dual Contact CTA", "dual-cta", "dual-cta-menu", "dual-cta-footer", "dual", "dual", "dual-button", ("#fff7f6", "#252321", "#b86a63", "#798a80", "#fffdf8", "#743b37"), "dual contact", "WhatsApp and consultation are paired but distinct."),
    PartialSpec(29, "Consultation Dossier System", "dossier-tabs", "dossier-menu", "packet-footer", "dossier", "dossier", "dossier-tab", ("#f3efe5", "#252321", "#9a6b35", "#b6aa98", "#fbfaf5", "#5e5548"), "dossier tabs", "Folder-like panels keep consultation information orderly."),
    PartialSpec(30, "Numbered Archive Index", "archive-index", "numbered-menu", "archive-footer", "archive", "archive", "number-button", ("#252321", "#fbfaf5", "#c39b6a", "#87927f", "#f8f7f2", "#3a3631"), "numbered archive", "Numbers create a precise editorial index."),
    PartialSpec(31, "Split-Screen Navigation Expansion", "split-screen", "split-screen-menu", "split-footer", "split-screen", "split-screen", "split-button", ("#eef3ee", "#252321", "#798a80", "#b88954", "#fffdf8", "#485041"), "split screen", "Visible nav is supported by a richer split guide."),
    PartialSpec(32, "Circular Control System", "circular-controls", "round-tile-menu", "round-module-footer", "circle", "circle", "circle-button", ("#fbfaf5", "#252321", "#6f7b68", "#cdaa78", "#fffdf8", "#596653"), "circular controls", "Rounded controls soften the interface."),
    PartialSpec(33, "Split Logo 4/4 Navigation", "split-logo", "grouped-menu", "balanced-footer", "balanced", "balanced", "split-logo-button", ("#f8f7f2", "#252321", "#9a6b35", "#dce5da", "#fffdf8", "#4a4640"), "split logo", "Four links balance on either side of the brand."),
    PartialSpec(34, "Right Utility Rail", "right-rail", "utility-block-menu", "utility-aware-footer", "rail", "rail", "rail-button", ("#eef3ee", "#263026", "#87927f", "#c39b6a", "#fbfaf5", "#485041"), "right rail", "A separate utility rail keeps actions out of the nav."),
    PartialSpec(35, "Soft Glass Layer", "soft-glass", "glass-panel-menu", "solid-contrast-footer", "glass", "glass", "glass-button", ("#fbfaf5", "#252321", "#798a80", "#cdaa78", "#fffdf8", "#596653"), "glass layer", "Glass appears in chrome only, not the full footer."),
    PartialSpec(36, "Soft Spa Symmetry", "spa-symmetry", "centered-menu", "centered-spa-footer", "spa", "spa", "spa-button", ("#f6f8f5", "#252321", "#87927f", "#b88954", "#fffdf8", "#485041"), "spa symmetry", "Centered balance and calm spacing lead the system."),
    PartialSpec(37, "Soft Brutalist Grid", "soft-brutalist", "grid-menu", "boxed-grid-footer", "grid", "grid", "grid-button", ("#f3efe5", "#252321", "#485041", "#9a6b35", "#fbfaf5", "#3a3631"), "soft grid", "A precise grid softened by Sofiati materials."),
    PartialSpec(38, "Quiet Luxury Minimal", "quiet-minimal", "spacious-menu", "minimal-complete-footer", "minimal", "minimal", "minimal-button", ("#fbfaf5", "#252321", "#9a6b35", "#d8cbb7", "#fffdf8", "#706b63"), "quiet minimal", "Whitespace and tiny details carry the structure."),
    PartialSpec(39, "Human Note System", "human-note", "human-note-menu", "personal-footer", "human", "human", "note-button", ("#fff7f6", "#252321", "#b86a63", "#a2aea0", "#fffdf8", "#743b37"), "human note", "A short warm note adds personal reassurance."),
    PartialSpec(40, "Consultation Funnel", "consultation-funnel", "funnel-menu", "funnel-footer", "funnel", "funnel", "funnel-button", ("#eef3ee", "#263026", "#798a80", "#c39b6a", "#fbfaf5", "#485041"), "funnel path", "A tasteful route guides users toward consultation."),
    PartialSpec(41, "Journal-Led Learning Index", "journal-led", "learning-menu", "learning-footer", "learning", "learning", "journal-button", ("#f8f7f2", "#252321", "#9a6b35", "#dce5da", "#fffdf8", "#5e5548"), "learning index", "Education is emphasized while main nav remains balanced."),
    PartialSpec(42, "Treatment Matrix", "treatment-matrix", "matrix-menu", "matrix-footer", "matrix", "matrix", "matrix-button", ("#fbfaf5", "#252321", "#6f7b68", "#cdaa78", "#fffdf8", "#485041"), "treatment matrix", "Care, Laser, Skin, and Results form a useful cluster."),
    PartialSpec(43, "Calm Medical Portal", "medical-portal", "portal-card-menu", "portal-footer", "portal-calm", "portal", "portal-button", ("#eef3ee", "#252321", "#485041", "#b88954", "#fbfaf5", "#263026"), "portal controls", "Practical portal controls stay calm and soft."),
    PartialSpec(44, "Floating Consultation Corner", "consultation-corner", "safe-button-menu", "appointment-card-footer", "corner", "corner", "corner-button", ("#f3efe5", "#252321", "#9a6b35", "#edc6c0", "#fffdf8", "#743b37"), "corner card", "A detached consultation card uses generous safe margins."),
    PartialSpec(45, "Premium Service Directory", "service-directory", "directory-menu", "directory-footer", "directory", "directory", "directory-button", ("#fbfaf5", "#252321", "#798a80", "#c39b6a", "#fffdf8", "#596653"), "directory", "The clearest navigation and sitemap concept."),
    PartialSpec(46, "Framed Portrait Trust", "portrait-trust", "portrait-menu", "portrait-footer", "portrait", "portrait", "portrait-button", ("#fff7f6", "#252321", "#b86a63", "#87927f", "#fffdf8", "#743b37"), "portrait trust", "A subtle portrait badge supports human trust."),
    PartialSpec(47, "Editorial Sidebar Index", "sidebar-index", "index-menu", "expanded-index-footer", "sidebar", "sidebar", "index-button", ("#252321", "#fbfaf5", "#c39b6a", "#a2aea0", "#f8f7f2", "#3a3631"), "sidebar index", "A numbered editorial index leads the structure."),
    PartialSpec(48, "Modular Island Footer System", "simple-complete", "simple-island-menu", "modular-island-footer", "island-footer", "island-footer", "modular-button", ("#eef3ee", "#252321", "#6f7b68", "#d8cbb7", "#fbfaf5", "#485041"), "modular islands", "The footer becomes the main identity surface."),
    PartialSpec(49, "Scroll Chip Navigation", "scroll-chips", "chip-menu", "chip-footer", "chip", "chip", "chip-button", ("#f8f7f2", "#252321", "#9a6b35", "#dce5da", "#fffdf8", "#5e5548"), "chips", "Tactile chips wrap cleanly without horizontal overflow."),
    PartialSpec(50, "Architectural Premium Grid", "architectural-grid", "modular-grid-menu", "architectural-footer", "architectural", "architectural", "architectural-button", ("#fbfaf5", "#252321", "#485041", "#c39b6a", "#fffdf8", "#263026"), "architectural grid", "The most controlled and precise public chrome."),
]


def concept_dirs() -> list[Path]:
    dirs = sorted(
        [p for p in CONCEPTS_DIR.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name)],
        key=lambda p: p.name,
    )
    if len(dirs) != 50:
        raise SystemExit(f"Expected 50 concept directories, found {len(dirs)}")
    return dirs


def require_pillow() -> None:
    if Image is None or ImageColor is None:
        raise SystemExit("Pillow is required to generate approved transparent Sofiati logo assets.")
    if not APPROVED_LOGO_SOURCE.exists():
        raise SystemExit(f"Approved logo source not found: {APPROVED_LOGO_SOURCE}")


def approved_logo_rel(filename: str) -> str:
    return f"../../assets/brand/{filename}"


def remove_dark_logo_background(path: Path) -> "Image.Image":
    require_pillow()
    source = Image.open(path).convert("RGBA")
    pixels = source.load()
    for y in range(source.height):
        for x in range(source.width):
            red, green, blue, alpha = pixels[x, y]
            strongest = max(red, green, blue)
            if strongest < 26:
                next_alpha = 0
            elif strongest < 82:
                next_alpha = int(alpha * ((strongest - 26) / 56))
            else:
                next_alpha = alpha
            pixels[x, y] = (red, green, blue, max(0, min(255, next_alpha)))

    bbox = source.getbbox()
    if not bbox:
        return source
    pad = 34
    left = max(0, bbox[0] - pad)
    top = max(0, bbox[1] - pad)
    right = min(source.width, bbox[2] + pad)
    bottom = min(source.height, bbox[3] + pad)
    return source.crop((left, top, right, bottom))


def tint_logo(base: "Image.Image", color: str) -> "Image.Image":
    require_pillow()
    target = ImageColor.getrgb(color)
    tinted = Image.new("RGBA", base.size)
    in_pixels = base.load()
    out_pixels = tinted.load()
    for y in range(base.height):
        for x in range(base.width):
            red, green, blue, alpha = in_pixels[x, y]
            if alpha == 0:
                out_pixels[x, y] = (0, 0, 0, 0)
                continue
            luminance = (0.2126 * red + 0.7152 * green + 0.0722 * blue) / 255
            lift = 0.58 + (0.42 * luminance)
            out_pixels[x, y] = (
                min(255, int(target[0] * lift + 255 * (1 - lift) * 0.08)),
                min(255, int(target[1] * lift + 255 * (1 - lift) * 0.08)),
                min(255, int(target[2] * lift + 255 * (1 - lift) * 0.08)),
                alpha,
            )
    return tinted


def write_svg_wrapper(svg_path: Path, image_name: str, width: int, height: int) -> None:
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Franciele Sofiati">
  <image href="{image_name}" width="{width}" height="{height}" preserveAspectRatio="xMidYMid meet"/>
</svg>
"""
    svg_path.write_text(svg, encoding="utf-8")


def save_logo_variant(image: "Image.Image", png_name: str, webp_name: str | None = None) -> None:
    png_path = BRAND_DIR / png_name
    image.save(png_path)
    if webp_name:
        image.save(BRAND_DIR / webp_name, lossless=True, quality=100)


def generate_logo_assets() -> None:
    require_pillow()
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    base = remove_dark_logo_background(APPROVED_LOGO_SOURCE)
    variants = {
        "primary": base,
        "gold": base,
        "dark": tint_logo(base, "#263026"),
        "light": tint_logo(base, "#fbfaf5"),
        "sage": tint_logo(base, "#798a80"),
    }

    save_logo_variant(variants["primary"], "sofiati-logo-primary.png")
    save_logo_variant(variants["primary"], "sofiati-logo-primary-transparent.png", "sofiati-logo-primary-transparent.webp")
    save_logo_variant(variants["gold"], "sofiati-logo-gold-transparent.png", "sofiati-logo-gold-transparent.webp")
    save_logo_variant(variants["dark"], "sofiati-logo-dark-transparent.png", "sofiati-logo-dark-transparent.webp")
    save_logo_variant(variants["light"], "sofiati-logo-light-transparent.png", "sofiati-logo-light-transparent.webp")
    save_logo_variant(variants["sage"], "sofiati-logo-sage-transparent.png", "sofiati-logo-sage-transparent.webp")

    save_logo_variant(variants["primary"], "sofiati-logo-monogram-transparent.png", "sofiati-logo-monogram-transparent.webp")
    save_logo_variant(variants["light"], "sofiati-logo-monogram-light-transparent.png", "sofiati-logo-monogram-light-transparent.webp")
    save_logo_variant(variants["dark"], "sofiati-logo-monogram-dark-transparent.png", "sofiati-logo-monogram-dark-transparent.webp")

    width, height = base.size
    write_svg_wrapper(BRAND_DIR / "sofiati-logo-primary.svg", "sofiati-logo-primary-transparent.png", width, height)
    write_svg_wrapper(BRAND_DIR / "sofiati-logo-gold.svg", "sofiati-logo-gold-transparent.png", width, height)
    write_svg_wrapper(BRAND_DIR / "sofiati-logo-dark.svg", "sofiati-logo-dark-transparent.png", width, height)
    write_svg_wrapper(BRAND_DIR / "sofiati-logo-light.svg", "sofiati-logo-light-transparent.png", width, height)
    write_svg_wrapper(BRAND_DIR / "sofiati-logo-sage.svg", "sofiati-logo-sage-transparent.png", width, height)
    write_svg_wrapper(BRAND_DIR / "sofiati-logo-monogram.svg", "sofiati-logo-monogram-transparent.png", width, height)
    write_svg_wrapper(BRAND_DIR / "sofiati-logo-monogram-light.svg", "sofiati-logo-monogram-light-transparent.png", width, height)
    write_svg_wrapper(BRAND_DIR / "sofiati-logo-monogram-dark.svg", "sofiati-logo-monogram-dark-transparent.png", width, height)
    write_svg_wrapper(BRAND_DIR / "sofiati-favicon.svg", "sofiati-logo-monogram-transparent.png", width, height)

    manifest = {
        "source": str(APPROVED_LOGO_SOURCE.relative_to(ROOT)),
        "transparent_background": True,
        "principal_asset": "assets/brand/sofiati-logo-primary-transparent.png",
        "generated": [*APPROVED_LOGO_FILES, *APPROVED_LOGO_WEBP_FILES],
    }
    (BRAND_DIR / "sofiati-logo-system-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )


def nav_links(klass: str, attr: str = 'data-main-nav="true"', numbered: bool = False) -> str:
    parts = []
    for index, (label, href) in enumerate(MAIN_LINKS, start=1):
        number = f'<span class="sf-link-number" aria-hidden="true">{index:02d}</span>' if numbered else ""
        parts.append(f'      <a class="{klass}" href="{href}" {attr}>{number}<span>{label}</span></a>')
    return "\n".join(parts)


def footer_links(numbered: bool = False) -> str:
    parts = []
    for index, (label, href) in enumerate(FOOTER_LINKS, start=1):
        number = f'<span aria-hidden="true">{index:02d}</span>' if numbered else ""
        parts.append(f'        <li><a href="{href}" data-footer-link="true">{number}{label}</a></li>')
    return "\n".join(parts)


def logo_img(kind: str = "primary", klass: str = "sf-logo-img") -> str:
    sources = {
        "primary": "sofiati-logo-primary-transparent.png",
        "gold": "sofiati-logo-gold-transparent.png",
        "dark": "sofiati-logo-dark-transparent.png",
        "light": "sofiati-logo-light-transparent.png",
        "sage": "sofiati-logo-sage-transparent.png",
        "monogram": "sofiati-logo-monogram.svg",
        "monogram-light": "sofiati-logo-monogram-light.svg",
        "monogram-dark": "sofiati-logo-monogram-dark.svg",
    }
    src = approved_logo_rel(sources.get(kind, sources["primary"]))
    return f'<img class="{klass}" src="{src}" alt="" loading="eager" decoding="async" />'


def banner(spec: PartialSpec) -> str:
    return f"""
<div class="sf-identity-banner language-banner sf-theme-{spec.code} sf-banner--{spec.banner}" data-partial-owner="identity-banner" aria-label="Brand identity and language">
  <a class="sf-banner-brand" href="index.html" aria-label="{BRAND_NAME} home">
    <span class="sf-mini-mark" aria-hidden="true">{logo_img("monogram", "sf-logo-img")}</span>
    <span>{BRAND_NAME}</span>
  </a>
  <div class="sf-language-switcher" aria-label="Language switcher">
    <button type="button" data-lang-switch="en" aria-pressed="true">EN</button>
    <span aria-hidden="true">/</span>
    <button type="button" data-lang-switch="pt-BR" aria-pressed="false">PT</button>
  </div>
</div>""".strip()


def header_feature(spec: PartialSpec) -> str:
    if spec.number in {6, 23, 30, 47}:
        return f'<span class="sf-header-feature sf-feature-mark" aria-hidden="true">{logo_img("monogram", "sf-logo-img")}</span>'
    if spec.number in {10, 22, 40}:
        return '<span class="sf-header-feature sf-feature-path" aria-hidden="true"><i></i><i></i><i></i><i></i></span>'
    if spec.number in {17, 32, 49}:
        return '<span class="sf-header-feature sf-feature-dots" aria-hidden="true"><i></i><i></i><i></i></span>'
    if spec.number in {25, 46}:
        return '<span class="sf-header-feature sf-feature-portrait" aria-hidden="true"></span>'
    if spec.number in {34, 44}:
        return '<span class="sf-header-feature sf-feature-corner" aria-hidden="true"></span>'
    return '<span class="sf-header-feature sf-feature-line" aria-hidden="true"></span>'


def header(spec: PartialSpec) -> str:
    numbered = spec.number in {1, 10, 30, 47}
    split = spec.number == 33
    if split:
        first = "\n".join(
            f'      <a class="sf-nav-link" href="{href}" data-main-nav="true"><span>{label}</span></a>'
            for label, href in MAIN_LINKS[:4]
        )
        second = "\n".join(
            f'      <a class="sf-nav-link" href="{href}" data-main-nav="true"><span>{label}</span></a>'
            for label, href in MAIN_LINKS[4:]
        )
        nav = f'<div class="sf-split-nav-group">{first}</div><div class="sf-split-nav-group">{second}</div>'
    else:
        nav = nav_links("sf-nav-link", numbered=numbered)
    return f"""
{banner(spec)}
<header class="sf-public-header sf-theme-{spec.code} sf-header--{spec.header}" data-partial-owner="header" data-structure="{spec.signature}">
  <div class="sf-header-shell">
    {header_feature(spec)}
    <a class="sf-brand-lockup" href="index.html" aria-label="{BRAND_NAME} home">
      {logo_img("primary")}
      <span>{BRAND_NAME}</span>
    </a>
    <nav class="sf-desktop-nav" aria-label="Primary navigation">
{nav}
    </nav>
    <div class="sf-header-actions" aria-label="Header actions">
      <a class="sf-header-cta" href="consultation.html" data-header-cta="true">Consultation</a>
      <a class="sf-action-link sf-whatsapp-link" href="{WHATSAPP_URL}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="sf-action-link sf-accessibility-link" href="accessibility.html">Accessibility</a>
    </div>
    <button class="sf-menu-button" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-menu" aria-label="Open navigation menu">
      <span>Menu</span>
    </button>
  </div>
</header>""".strip()


def mobile_intro(spec: PartialSpec) -> str:
    copy = {
        9: "Choose a route, then request guidance when you are ready.",
        24: "Care pages and contact actions stay grouped for clarity.",
        39: "Start gently. Read, ask, and move at the pace that feels right.",
        41: "Learning and next-step links stay close to the care journey.",
        46: "Human guidance and careful evaluation come first.",
    }.get(spec.number, "Start with guidance, understand your options, then request a calm next step.")
    return f'<p class="sf-mobile-note">{copy}</p>'


def mobile_menu(spec: PartialSpec) -> str:
    numbered = spec.number in {1, 10, 30, 47}
    return f"""
<aside id="mobile-menu" class="sf-mobile-menu sf-theme-{spec.code} sf-menu--{spec.mobile}" data-partial-owner="mobile-menu" aria-hidden="true">
  <div class="sf-mobile-dialog" role="dialog" aria-modal="true" aria-label="Mobile navigation">
    <div class="sf-mobile-top">
      <a class="sf-mobile-brand" href="index.html" aria-label="{BRAND_NAME} home">
        <span class="sf-mini-mark" aria-hidden="true">{logo_img("monogram", "sf-logo-img")}</span>
        <span>{BRAND_NAME}</span>
      </a>
      <button class="sf-mobile-close" type="button" data-menu-close aria-label="Close navigation menu">Close</button>
    </div>
    {mobile_intro(spec)}
    <nav class="sf-mobile-nav" aria-label="Mobile primary navigation">
{nav_links("sf-mobile-link", numbered=numbered)}
    </nav>
    <div class="sf-mobile-actions" aria-label="Mobile actions">
      <a class="sf-mobile-primary" href="consultation.html">Consultation</a>
      <a href="{WHATSAPP_URL}" target="_blank" rel="noopener">WhatsApp</a>
      <a class="sf-accessibility-link" href="accessibility.html">Accessibility</a>
    </div>
  </div>
</aside>""".strip()


def footer_feature(spec: PartialSpec) -> str:
    if spec.number in {10, 22, 40}:
        return '<div class="sf-footer-feature sf-footer-path" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></div>'
    if spec.number in {28, 44}:
        return '<div class="sf-footer-feature sf-footer-cta-card"><span>Ready for a careful next step?</span><a href="contact.html">Contact route</a></div>'
    if spec.number in {41, 45}:
        return '<div class="sf-footer-feature sf-footer-learning"><a href="journal.html">Journal</a><a href="faq.html">FAQ</a><a href="testimonials.html">Testimonials</a></div>'
    if spec.number in {23, 30, 47}:
        return f'<div class="sf-footer-feature sf-footer-large-mark" aria-hidden="true">{logo_img("monogram", "sf-logo-img")}</div>'
    return '<div class="sf-footer-feature" aria-hidden="true"><span></span></div>'


def footer(spec: PartialSpec) -> str:
    numbered = spec.number in {1, 30, 47}
    return f"""
<footer class="sf-public-footer sf-theme-{spec.code} sf-footer--{spec.footer}" data-partial-owner="footer" data-structure="{spec.signature}">
  {footer_feature(spec)}
  <div class="sf-footer-brand">
    {logo_img("primary")}
    <h2>{BRAND_NAME}</h2>
    <p>{DESCRIPTION}</p>
  </div>
  <address class="sf-footer-contact" aria-label="Contact details">
    <a href="{WHATSAPP_URL}" target="_blank" rel="noopener">WhatsApp</a>
    <a href="{INSTAGRAM_URL}" target="_blank" rel="noopener">Instagram: @fransofiati_biomedica</a>
    <span>Service area: Londrina, PR / Brazil</span>
    <a href="contact.html">Consultation or contact page</a>
  </address>
  <nav class="sf-footer-sitemap" aria-label="Footer sitemap">
    <ul>
{footer_links(numbered=numbered)}
    </ul>
  </nav>
  <div class="sf-footer-close">
    <a class="sf-footer-cta" href="contact.html" data-footer-cta="true">Contact the clinic</a>
    <p>© 2026 {BRAND_NAME}. All rights reserved.</p>
  </div>
</footer>""".strip()


def cookie_banner(spec: PartialSpec) -> str:
    return f"""
<div class="sf-cookie-banner sf-theme-{spec.code} sf-cookie--{spec.cookie}" data-partial-owner="cookie-banner" data-cookie-banner role="region" aria-label="Cookie preferences">
  <p>We use essential cookies to remember language and browsing preferences for a calm site experience.</p>
  <div class="sf-cookie-actions">
    <button type="button" data-cookie-accept>Accept</button>
    <a href="cookies.html">Cookie details</a>
  </div>
</div>""".strip()


WHATSAPP_SVG = """<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path d="M16 4.2c-6.35 0-11.52 4.95-11.52 11.04 0 2.1.63 4.08 1.72 5.75l-1.45 5.03 5.26-1.34a11.92 11.92 0 0 0 5.99 1.61c6.35 0 11.52-4.95 11.52-11.05S22.35 4.2 16 4.2Zm0 19.95c-1.9 0-3.67-.57-5.15-1.55l-.36-.23-3.12.8.86-2.94-.25-.38a8.5 8.5 0 0 1-1.39-4.61c0-4.96 4.22-8.99 9.41-8.99s9.41 4.03 9.41 8.99-4.22 8.91-9.41 8.91Zm5.16-6.67c-.28-.13-1.67-.79-1.93-.88-.26-.1-.45-.13-.64.13-.19.27-.73.88-.9 1.06-.17.18-.33.2-.61.07-.28-.14-1.18-.42-2.24-1.34-.83-.72-1.39-1.6-1.55-1.87-.16-.27-.02-.42.12-.55.12-.12.28-.32.42-.48.14-.16.19-.27.28-.45.09-.18.05-.34-.02-.48-.07-.13-.64-1.48-.88-2.02-.23-.54-.47-.46-.64-.47h-.55c-.19 0-.48.07-.73.34-.26.27-1 1-1 2.43s1.03 2.8 1.18 2.99c.14.18 2.03 2.98 4.93 4.18.69.28 1.23.45 1.65.58.69.21 1.32.18 1.82.11.56-.08 1.67-.65 1.9-1.28.24-.63.24-1.17.17-1.28-.07-.12-.26-.18-.55-.31Z"/></svg>"""

ACCESSIBILITY_SVG = """<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><path d="M16 7.4a2.7 2.7 0 1 0 0-5.4 2.7 2.7 0 0 0 0 5.4Zm9.8 2.1H6.2a1.45 1.45 0 1 0 0 2.9h6.2v5.18l-3.7 9.92a1.48 1.48 0 0 0 .86 1.9c.75.28 1.58-.08 1.87-.83l3.04-8.1h3.06l3.04 8.1a1.46 1.46 0 0 0 1.87.83c.75-.28 1.13-1.12.86-1.9l-3.7-9.92V12.4h6.2a1.45 1.45 0 1 0 0-2.9Z"/></svg>"""


def floating_widgets(spec: PartialSpec) -> str:
    return f"""
<div class="sf-floating-tools sf-theme-{spec.code} sf-floating--{spec.floating}" data-partial-owner="floating-widgets" data-floating-tools aria-label="Quick actions">
  <a class="sf-floating-whatsapp" href="{WHATSAPP_URL}" target="_blank" rel="noopener" aria-label="Open WhatsApp contact">
    {WHATSAPP_SVG}
  </a>
  <a class="sf-floating-accessibility" href="accessibility.html" aria-label="Accessibility options">
    {ACCESSIBILITY_SVG}
  </a>
  <button class="sf-back-to-top" type="button" data-back-to-top aria-label="Back to top" aria-hidden="true" tabindex="-1">
    <span aria-hidden="true">↑</span>
  </button>
</div>""".strip()


def concept_js(concept_id: str, code: str) -> str:
    return f"""(() => {{
  "use strict";

  const profile = {{
    conceptId: {json.dumps(concept_id)},
    partialNames: ["header", "mobile-menu", "footer", "cookie-banner", "floating-widgets"],
  }};
  const cache = new Map();
  let lastMenuTrigger = null;

  const fetchPartial = async (name) => {{
    if (!cache.has(name)) {{
      cache.set(name, fetch(`partials/${{name}}.html`, {{ cache: "no-store" }}).then((response) => {{
        if (!response.ok) throw new Error(`Missing partial ${{name}} for ${{profile.conceptId}}`);
        return response.text();
      }}));
    }}
    return cache.get(name);
  }};

  const mountPartials = async () => {{
    await Promise.all(profile.partialNames.map(async (name) => {{
      const mount = document.querySelector(`[data-sofiati-partial="${{name}}"]`);
      if (!mount) return;
      mount.innerHTML = await fetchPartial(name);
      mount.dataset.partialLoaded = "true";
    }}));
    document.dispatchEvent(new CustomEvent("sofiati:concept-partials-ready", {{ detail: profile }}));
  }};

  const menu = () => document.getElementById("mobile-menu");

  const openMenu = (trigger) => {{
    const panel = menu();
    if (!panel) return;
    lastMenuTrigger = trigger || document.activeElement;
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    document.body.classList.add("public-menu-locked");
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {{
      button.setAttribute("aria-expanded", "true");
      button.setAttribute("aria-controls", "mobile-menu");
    }});
    const first = panel.querySelector("a[href], button:not([disabled])");
    if (first) first.focus({{ preventScroll: true }});
  }};

  const closeMenu = () => {{
    const panel = menu();
    if (!panel) return;
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    document.body.classList.remove("public-menu-locked");
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {{
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", "mobile-menu");
    }});
    if (lastMenuTrigger && typeof lastMenuTrigger.focus === "function") {{
      lastMenuTrigger.focus({{ preventScroll: true }});
    }}
  }};

  const wireMenu = () => {{
    document.addEventListener("click", (event) => {{
      const toggle = event.target.closest("[data-menu-toggle]");
      const close = event.target.closest("[data-menu-close]");
      const panel = menu();
      if (toggle) {{
        event.preventDefault();
        if (panel?.getAttribute("aria-hidden") === "false") closeMenu();
        else openMenu(toggle);
      }}
      if (close) {{
        event.preventDefault();
        closeMenu();
      }}
      if (panel && event.target === panel) closeMenu();
    }});
    document.addEventListener("keydown", (event) => {{
      if (event.key === "Escape") closeMenu();
    }});
  }};

  const wireCookie = () => {{
    const key = `sofiati-cookie-${{profile.conceptId}}`;
    const banner = document.querySelector("[data-cookie-banner]");
    if (!banner) return;
    const setVisible = (visible) => document.body.classList.toggle("public-cookie-visible", visible);
    if (window.localStorage.getItem(key) === "accepted") {{
      banner.classList.add("is-hidden");
      setVisible(false);
    }} else {{
      setVisible(true);
    }}
    banner.querySelector("[data-cookie-accept]")?.addEventListener("click", () => {{
      window.localStorage.setItem(key, "accepted");
      banner.classList.add("is-hidden");
      setVisible(false);
    }});
  }};

  const setLanguage = (value) => {{
    const lang = value === "pt" || value === "pt-BR" ? "pt-BR" : "en";
    const short = lang === "pt-BR" ? "pt" : "en";
    document.documentElement.lang = lang;
    document.documentElement.dataset.activeLang = short;
    document.querySelectorAll("[data-lang-switch]").forEach((button) => {{
      const active = (button.dataset.langSwitch || "en").toLowerCase().startsWith(short);
      button.setAttribute("aria-pressed", active ? "true" : "false");
      button.dataset.active = active ? "true" : "false";
    }});
  }};

  const wireLanguage = () => {{
    document.addEventListener("click", (event) => {{
      const button = event.target.closest("[data-lang-switch]");
      if (!button) return;
      event.preventDefault();
      setLanguage(button.dataset.langSwitch);
    }});
    setLanguage(document.documentElement.lang || "en");
  }};

  const wireFloatingTools = () => {{
    const buttons = document.querySelectorAll("[data-back-to-top]");
    const update = () => {{
      const visible = window.scrollY > Math.min(520, Math.max(220, window.innerHeight * 0.42));
      buttons.forEach((button) => {{
        button.classList.toggle("is-visible", visible);
        button.setAttribute("aria-hidden", visible ? "false" : "true");
        button.tabIndex = visible ? 0 : -1;
      }});
    }};
    buttons.forEach((button) => {{
      if (button.dataset.sofiatiTopReady === "true") return;
      button.dataset.sofiatiTopReady = "true";
      button.addEventListener("click", () => {{
        const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({{ top: 0, behavior: reduced ? "auto" : "smooth" }});
      }});
    }});
    window.addEventListener("scroll", update, {{ passive: true }});
    window.addEventListener("resize", update);
    update();
  }};

  const markCurrentLinks = () => {{
    const current = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll("a[href$='.html']").forEach((link) => {{
      const href = link.getAttribute("href") || "";
      link.removeAttribute("aria-current");
      if (href === current) link.setAttribute("aria-current", "page");
    }});
  }};

  const init = async () => {{
    await mountPartials();
    wireMenu();
    wireCookie();
    wireLanguage();
    wireFloatingTools();
    markCurrentLinks();
    document.body.dataset.partialsReady = "true";
  }};

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", init, {{ once: true }});
  }} else {{
    init();
  }}
}})();
"""


def css_for(spec: PartialSpec) -> str:
    bg, ink, accent, soft, panel, deep = spec.palette
    radius = ["2px", "999px", "14px", "0px", "8px"][spec.number % 5]
    footer_columns = "repeat(12, minmax(0, 1fr))"
    return f"""
{CSS_START}
.sf-theme-{spec.code} {{
  --sf-bg: {bg};
  --sf-ink: {ink};
  --sf-accent: {accent};
  --sf-soft: {soft};
  --sf-panel: {panel};
  --sf-deep: {deep};
  --sf-line: color-mix(in srgb, var(--sf-ink), transparent 82%);
  --sf-radius: {radius};
  --sf-shadow: 0 26px 70px color-mix(in srgb, var(--sf-ink), transparent 86%);
  --sf-max: min(1180px, calc(100vw - 32px));
  --sf-space-1: 4px;
  --sf-space-2: 8px;
  --sf-space-3: 12px;
  --sf-space-4: 16px;
  --sf-space-5: 24px;
  --sf-space-6: 32px;
  --sf-space-7: 48px;
  --sf-space-8: 64px;
  --sf-space-9: 96px;
  --sf-radius-sm: min(8px, var(--sf-radius));
  --sf-radius-md: calc(var(--sf-radius) + 4px);
  --sf-radius-lg: calc(var(--sf-radius) + 8px);
  --sf-radius-pill: 999px;
  --sf-border-hairline: 1px solid var(--sf-line);
  --sf-border-strong: 1px solid color-mix(in srgb, var(--sf-accent), var(--sf-ink) 18%);
  --sf-elevation-soft: 0 18px 40px color-mix(in srgb, var(--sf-ink), transparent 86%);
  --sf-elevation-lifted: 0 26px 70px color-mix(in srgb, var(--sf-ink), transparent 82%);
  --sf-type-ui: clamp(0.76rem, 1vw, 0.88rem);
  --sf-type-small: clamp(0.66rem, 0.8vw, 0.78rem);
  --sf-type-display: clamp(1.55rem, 3.4vw, 2.8rem);
  --sf-leading-tight: 1.06;
  --sf-leading-body: 1.55;
}}

.sf-identity-banner,
.sf-public-header,
.sf-mobile-menu,
.sf-public-footer,
.sf-cookie-banner,
.sf-floating-tools {{
  color: var(--sf-ink);
  font-family: Inter, "Avenir Next", "Segoe UI", Arial, sans-serif;
  letter-spacing: 0;
}}

.sf-identity-banner {{
  position: relative;
  z-index: 75;
  min-height: 30px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: nowrap;
  gap: 0.7rem;
  padding: 0.28rem max(1rem, calc((100vw - 1180px) / 2));
  background: color-mix(in srgb, var(--sf-bg), white 16%);
  border-bottom: 1px solid var(--sf-line);
  font-size: clamp(0.66rem, 1.7vw, 0.76rem);
}}

.language-banner,
.language-banner * {{
  white-space: nowrap;
  writing-mode: horizontal-tb;
  text-orientation: mixed;
  word-break: keep-all;
  overflow-wrap: normal;
}}

.sf-logo-img {{
  display: block;
  width: 100%;
  height: 100%;
  object-fit: contain;
  background: transparent;
}}

.sf-banner-brand,
.sf-mobile-brand,
.sf-brand-lockup {{
  display: inline-flex;
  align-items: center;
  min-width: 0;
  gap: 0.55rem;
  color: inherit;
  text-decoration: none;
}}

.sf-mini-mark {{
  width: 1.6rem;
  height: 1.6rem;
  flex: 0 0 auto;
  display: inline-grid;
  place-items: center;
  border: 1px solid var(--sf-line);
  border-radius: 50%;
  color: var(--sf-accent);
  font-family: Georgia, "Times New Roman", serif;
  font-size: 0.66rem;
  line-height: 1;
}}

.sf-mini-mark .sf-logo-img {{
  width: 1.34rem;
  height: 1.34rem;
}}

.sf-language-switcher {{
  display: inline-flex;
  align-items: center;
  gap: 0.12rem;
  padding: 0.12rem;
  border: 1px solid var(--sf-line);
  border-radius: 999px;
  background: color-mix(in srgb, var(--sf-panel), transparent 10%);
}}

.sf-language-switcher button {{
  min-width: 2rem;
  min-height: 1.55rem;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: inherit;
  cursor: pointer;
  font-size: 0.64rem;
  font-weight: 700;
}}

.sf-language-switcher button[aria-pressed="true"] {{
  background: var(--sf-deep);
  color: var(--sf-panel);
}}

.sf-public-header {{
  position: sticky;
  top: 0;
  z-index: 70;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--sf-bg), white 14%), color-mix(in srgb, var(--sf-panel), var(--sf-soft) 20%));
  border-bottom: 1px solid var(--sf-line);
  box-shadow: 0 14px 38px color-mix(in srgb, var(--sf-ink), transparent 94%);
  backdrop-filter: blur(18px);
}}

.sf-header-shell {{
  width: var(--sf-max);
  margin: 0 auto;
  min-height: 74px;
  display: grid;
  grid-template-columns: minmax(165px, 0.84fr) minmax(0, 1.7fr) auto auto;
  align-items: center;
  gap: clamp(0.55rem, 1.2vw, 1rem);
  padding: 0.68rem 0;
}}

.sf-brand-lockup img {{
  width: clamp(2.65rem, 4.4vw, 4.4rem);
  height: clamp(2.65rem, 4.4vw, 4.4rem);
  object-fit: contain;
}}

.sf-brand-lockup span,
.sf-banner-brand span:last-child,
.sf-mobile-brand span:last-child {{
  min-width: 0;
  overflow-wrap: anywhere;
}}

.sf-banner-brand span:last-child {{
  max-width: calc(100vw - 122px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}}

.sf-brand-lockup span {{
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(0.78rem, 1.5vw, 1rem);
  line-height: 1.08;
}}

.sf-desktop-nav {{
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: clamp(0.22rem, 0.6vw, 0.56rem);
  min-width: 0;
}}

.sf-nav-link,
.sf-action-link,
.sf-header-cta,
.sf-menu-button,
.sf-mobile-link,
.sf-mobile-actions a,
.sf-footer-cta,
.sf-cookie-actions a,
.sf-cookie-actions button {{
  min-height: 2.5rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
  color: inherit;
  text-decoration: none;
  line-height: 1.1;
}}

.sf-nav-link {{
  padding: 0.56rem clamp(0.36rem, 0.7vw, 0.7rem);
  border-radius: var(--sf-radius);
  font-size: clamp(0.66rem, 1vw, 0.79rem);
  font-weight: 750;
  text-transform: uppercase;
}}

.sf-nav-link:hover,
.sf-nav-link:focus-visible,
.sf-nav-link[aria-current="page"] {{
  background: color-mix(in srgb, var(--sf-accent), transparent 76%);
}}

.sf-link-number {{
  color: var(--sf-accent);
  font-size: 0.68em;
}}

.sf-header-actions {{
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.42rem;
  min-width: 0;
}}

.sf-header-cta,
.sf-footer-cta {{
  padding: 0.72rem 1rem;
  border: 1px solid color-mix(in srgb, var(--sf-accent), var(--sf-ink) 18%);
  border-radius: var(--sf-radius);
  background: var(--sf-deep);
  color: var(--sf-panel);
  font-size: 0.78rem;
  font-weight: 800;
}}

.sf-action-link {{
  padding: 0.58rem 0.68rem;
  border: 1px solid var(--sf-line);
  border-radius: var(--sf-radius);
  background: color-mix(in srgb, var(--sf-panel), transparent 12%);
  color: color-mix(in srgb, var(--sf-deep), black 8%);
  font-size: 0.72rem;
  font-weight: 700;
}}

.sf-menu-button,
.sf-mobile-close,
.sf-cookie-actions button,
.sf-back-to-top {{
  border: 0;
  cursor: pointer;
  font: inherit;
}}

.sf-menu-button {{
  display: none;
  padding: 0.68rem 0.86rem;
  border: 1px solid color-mix(in srgb, var(--sf-ink), transparent 72%);
  border-radius: var(--sf-radius);
  background: #fffaf1;
  color: #211f1b;
  font-weight: 800;
  box-shadow: 0 10px 24px rgba(33, 31, 27, 0.1);
}}

.sf-header-feature {{
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 1.75rem;
  min-height: 1.75rem;
  color: var(--sf-accent);
}}

.sf-feature-line {{
  align-self: stretch;
  width: 1px;
  min-height: 42px;
  background: var(--sf-line);
}}

.sf-feature-mark {{
  width: clamp(2.2rem, 4vw, 4.4rem);
  height: clamp(2.2rem, 4vw, 4.4rem);
  border: 1px solid var(--sf-line);
  border-radius: 50%;
  padding: 0.24rem;
}}

.sf-feature-path,
.sf-feature-dots {{
  gap: 0.24rem;
}}

.sf-feature-path i {{
  width: clamp(1.1rem, 3vw, 2.4rem);
  height: 1px;
  background: var(--sf-accent);
}}

.sf-feature-dots i {{
  width: 0.48rem;
  height: 0.48rem;
  border-radius: 50%;
  background: var(--sf-accent);
}}

.sf-feature-portrait,
.sf-feature-corner {{
  width: clamp(2.2rem, 4vw, 4.8rem);
  height: clamp(2.2rem, 4vw, 4.8rem);
  border: 1px solid var(--sf-line);
  border-radius: 35% 65% 55% 45%;
  background:
    radial-gradient(circle at 50% 35%, var(--sf-accent) 0 18%, transparent 19%),
    linear-gradient(135deg, var(--sf-soft), var(--sf-panel));
}}

.sf-feature-corner {{
  border-radius: 0 45% 0 45%;
}}

.sf-header--editorial-masthead .sf-header-shell,
.sf-header--spa-symmetry .sf-header-shell,
.sf-header--quiet-minimal .sf-header-shell {{
  grid-template-columns: 1fr;
  justify-items: center;
  text-align: center;
  padding-block: 0.9rem;
}}

.sf-header--editorial-masthead .sf-header-actions,
.sf-header--spa-symmetry .sf-header-actions,
.sf-header--quiet-minimal .sf-header-actions {{
  justify-content: center;
}}

.sf-header--floating-capsule .sf-desktop-nav,
.sf-header--scroll-chips .sf-desktop-nav {{
  padding: 0.3rem;
  border: 1px solid var(--sf-line);
  border-radius: 999px;
  background: color-mix(in srgb, var(--sf-panel), transparent 4%);
}}

.sf-header--atelier-rail .sf-header-shell,
.sf-header--sidebar-index .sf-header-shell {{
  grid-template-columns: 4.7rem minmax(150px, 0.9fr) minmax(0, 1.4fr) auto;
}}

.sf-header--atelier-rail .sf-desktop-nav,
.sf-header--sidebar-index .sf-desktop-nav {{
  justify-content: flex-start;
  border-left: 1px solid var(--sf-line);
  padding-left: 0.72rem;
}}

.sf-header--split-utility .sf-header-shell,
.sf-header--formal-clinical .sf-header-shell,
.sf-header--service-directory .sf-header-shell {{
  grid-template-columns: minmax(180px, 0.8fr) minmax(0, 1.6fr);
}}

.sf-header--split-utility .sf-header-actions,
.sf-header--formal-clinical .sf-header-actions,
.sf-header--service-directory .sf-header-actions {{
  grid-column: 1 / -1;
  justify-content: center;
  padding-top: 0.45rem;
  border-top: 1px solid var(--sf-line);
}}

.sf-header--monogram-axis .sf-header-shell,
.sf-header--oversized-wordmark .sf-header-shell {{
  grid-template-columns: auto 1fr;
}}

.sf-header--monogram-axis .sf-desktop-nav,
.sf-header--oversized-wordmark .sf-desktop-nav {{
  grid-column: 1 / -1;
  justify-content: center;
}}

.sf-header--portal-tiles .sf-desktop-nav,
.sf-header--soft-brutalist .sf-desktop-nav,
.sf-header--treatment-matrix .sf-desktop-nav,
.sf-header--architectural-grid .sf-desktop-nav {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.36rem;
}}

.sf-header--portal-tiles .sf-nav-link,
.sf-header--soft-brutalist .sf-nav-link,
.sf-header--treatment-matrix .sf-nav-link,
.sf-header--architectural-grid .sf-nav-link {{
  border: 1px solid var(--sf-line);
  background: color-mix(in srgb, var(--sf-panel), transparent 16%);
}}

.sf-header--asymmetric-studio .sf-header-shell,
.sf-header--split-screen .sf-header-shell {{
  grid-template-columns: minmax(170px, 0.62fr) minmax(0, 1fr);
}}

.sf-header--asymmetric-studio .sf-header-actions,
.sf-header--split-screen .sf-header-actions {{
  grid-column: 1;
  grid-row: 2;
  justify-content: flex-start;
}}

.sf-header--asymmetric-studio .sf-desktop-nav,
.sf-header--split-screen .sf-desktop-nav {{
  grid-column: 2;
  grid-row: 1 / span 2;
  justify-content: flex-end;
}}

.sf-header--right-rail .sf-header-actions,
.sf-header--consultation-corner .sf-header-actions {{
  flex-direction: column;
  align-items: stretch;
  padding: 0.44rem;
  border: 1px solid var(--sf-line);
  border-radius: calc(var(--sf-radius) + 4px);
  background: color-mix(in srgb, var(--sf-panel), transparent 8%);
}}

.sf-header--image-strip,
.sf-header--transparent-overlay,
.sf-header--soft-glass {{
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--sf-accent), transparent 74%) 0 18%, transparent 18% 100%),
    color-mix(in srgb, var(--sf-panel), transparent 5%);
}}

.sf-header--split-logo .sf-header-shell {{
  grid-template-columns: 1fr minmax(170px, auto) 1fr auto;
}}

.sf-header--split-logo .sf-desktop-nav {{
  display: contents;
}}

.sf-header--split-logo .sf-split-nav-group {{
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: center;
  gap: 0.36rem;
}}

.sf-header--dual-cta .sf-header-actions,
.sf-header--consultation-funnel .sf-header-actions {{
  padding: 0.28rem;
  border: 1px solid var(--sf-line);
  background: color-mix(in srgb, var(--sf-soft), transparent 60%);
}}

.sf-mobile-menu {{
  position: fixed;
  inset: 0;
  z-index: 120;
  display: grid;
  place-items: center;
  padding: clamp(0.85rem, 3vw, 1.6rem);
  background: rgba(24, 22, 18, 0.82);
  opacity: 0;
  pointer-events: none;
  transition: opacity 190ms ease;
}}

.sf-mobile-menu[aria-hidden="false"],
.sf-mobile-menu.is-open {{
  opacity: 1;
  pointer-events: auto;
}}

.sf-mobile-dialog {{
  width: min(94vw, 620px);
  max-height: min(88vh, 760px);
  overflow: auto;
  display: grid;
  gap: 1rem;
  padding: clamp(1rem, 4vw, 2rem);
  border: 1px solid color-mix(in srgb, var(--sf-accent), transparent 45%);
  border-radius: min(24px, calc(var(--sf-radius) + 8px));
  background:
    radial-gradient(circle at top right, color-mix(in srgb, var(--sf-accent), transparent 82%), transparent 34%),
    #fbf8f0;
  color: #211f1b;
  box-shadow: var(--sf-shadow);
}}

.sf-mobile-top {{
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}}

.sf-mobile-close {{
  min-height: 2.45rem;
  padding: 0.58rem 0.82rem;
  border: 1px solid var(--sf-line);
  border-radius: var(--sf-radius);
  background: #fffdf8;
  color: #211f1b;
}}

.sf-mobile-note {{
  max-width: 34rem;
  margin: 0;
  color: rgba(33, 31, 27, 0.72);
}}

.sf-mobile-nav {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.55rem;
}}

.sf-mobile-link {{
  justify-content: flex-start;
  min-height: 3.25rem;
  padding: 0.84rem 0.9rem;
  border: 1px solid var(--sf-line);
  border-radius: var(--sf-radius);
  background: #fffdf8;
  color: #211f1b;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.05rem, 4.8vw, 1.7rem);
}}

.sf-mobile-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.48rem;
}}

.sf-mobile-actions a {{
  flex: 1 1 9rem;
  padding: 0.78rem 0.92rem;
  border: 1px solid var(--sf-line);
  border-radius: var(--sf-radius);
  background: #f2eadc;
  color: #211f1b;
  font-weight: 800;
}}

.sf-mobile-primary {{
  background: #211f1b !important;
  color: #fffaf1 !important;
}}

.sf-menu--timeline-menu .sf-mobile-nav,
.sf-menu--numbered-menu .sf-mobile-nav,
.sf-menu--index-menu .sf-mobile-nav,
.sf-menu--spacious-menu .sf-mobile-nav {{
  grid-template-columns: 1fr;
}}

.sf-menu--tile-grid .sf-mobile-nav,
.sf-menu--grid-menu .sf-mobile-nav,
.sf-menu--modular-grid-menu .sf-mobile-nav,
.sf-menu--round-tile-menu .sf-mobile-nav {{
  grid-template-columns: repeat(2, minmax(0, 1fr));
}}

.sf-menu--bottom-sheet {{
  align-items: end;
}}

.sf-menu--bottom-sheet .sf-mobile-dialog,
.sf-menu--app-sheet .sf-mobile-dialog {{
  width: min(100%, 760px);
  border-radius: 24px 24px 0 0;
}}

.sf-menu--left-drawer,
.sf-menu--botanical-drawer {{
  justify-items: start;
}}

.sf-menu--left-drawer .sf-mobile-dialog,
.sf-menu--botanical-drawer .sf-mobile-dialog {{
  height: 100%;
  max-height: 100vh;
  width: min(88vw, 430px);
  border-radius: 0 22px 22px 0;
}}

.sf-public-footer {{
  position: relative;
  overflow: hidden;
  display: grid;
  grid-template-columns: {footer_columns};
  gap: clamp(1rem, 2.4vw, 2rem);
  align-items: start;
  padding: clamp(2.5rem, 6vw, 5rem) max(1rem, calc((100vw - 1180px) / 2)) clamp(6rem, 9vw, 8rem);
  background:
    radial-gradient(circle at 90% 10%, color-mix(in srgb, var(--sf-accent), transparent 82%), transparent 30%),
    linear-gradient(135deg, color-mix(in srgb, var(--sf-bg), white 10%), color-mix(in srgb, var(--sf-deep), var(--sf-bg) 62%));
  border-top: 1px solid var(--sf-line);
}}

.sf-public-footer > * {{
  position: relative;
}}

.sf-footer-feature {{
  grid-column: 1 / -1;
  min-height: 0.55rem;
  display: flex;
  align-items: center;
  gap: 0.55rem;
  color: var(--sf-accent);
  font-size: 0.72rem;
  font-weight: 800;
  text-transform: uppercase;
}}

.sf-footer-feature::before,
.sf-footer-feature::after {{
  content: "";
  height: 1px;
  flex: 1;
  background: var(--sf-line);
}}

.sf-footer-feature span {{
  max-width: 20rem;
}}

.sf-footer-brand {{
  grid-column: span 4;
  display: grid;
  gap: 0.8rem;
}}

.sf-footer-brand img {{
  width: clamp(4.4rem, 9vw, 7.4rem);
  height: clamp(4.4rem, 9vw, 7.4rem);
  object-fit: contain;
}}

.sf-footer-brand h2 {{
  margin: 0;
  font-family: Georgia, "Times New Roman", serif;
  font-size: clamp(1.45rem, 3.4vw, 2.8rem);
  line-height: 1.02;
  letter-spacing: 0;
}}

.sf-footer-brand p,
.sf-footer-contact,
.sf-footer-close p {{
  margin: 0;
  color: color-mix(in srgb, var(--sf-ink), transparent 20%);
}}

.sf-footer-contact {{
  grid-column: span 3;
  display: grid;
  gap: 0.55rem;
  font-style: normal;
}}

.sf-footer-contact a,
.sf-footer-sitemap a,
.sf-footer-close a {{
  color: inherit;
  text-decoration: none;
}}

.sf-footer-contact a:hover,
.sf-footer-sitemap a:hover {{
  color: var(--sf-accent);
}}

.sf-footer-sitemap {{
  grid-column: span 5;
}}

.sf-footer-sitemap ul {{
  list-style: none;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.42rem 0.76rem;
  margin: 0;
  padding: 0;
}}

.sf-footer-sitemap a {{
  min-height: 2.05rem;
  display: inline-flex;
  align-items: center;
  gap: 0.38rem;
  border-bottom: 1px solid color-mix(in srgb, var(--sf-line), transparent 24%);
  font-size: 0.88rem;
}}

.sf-footer-sitemap span {{
  color: var(--sf-accent);
  font-size: 0.75rem;
}}

.sf-footer-close {{
  grid-column: 1 / -1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding-top: 1.2rem;
  border-top: 1px solid var(--sf-line);
}}

.sf-footer-cta {{
  background: color-mix(in srgb, var(--sf-accent), var(--sf-panel) 66%);
  color: var(--sf-ink);
}}

.sf-footer--rounded-card .sf-footer-brand,
.sf-footer--rounded-card .sf-footer-contact,
.sf-footer--rounded-card .sf-footer-sitemap,
.sf-footer--settings-list .sf-footer-brand,
.sf-footer--settings-list .sf-footer-contact,
.sf-footer--settings-list .sf-footer-sitemap,
.sf-footer--module-footer .sf-footer-brand,
.sf-footer--module-footer .sf-footer-contact,
.sf-footer--module-footer .sf-footer-sitemap,
.sf-footer--boxed-grid-footer .sf-footer-brand,
.sf-footer--boxed-grid-footer .sf-footer-contact,
.sf-footer--boxed-grid-footer .sf-footer-sitemap,
.sf-footer--architectural-footer .sf-footer-brand,
.sf-footer--architectural-footer .sf-footer-contact,
.sf-footer--architectural-footer .sf-footer-sitemap {{
  padding: clamp(1rem, 2vw, 1.45rem);
  border: 1px solid var(--sf-line);
  border-radius: var(--sf-radius);
  background: color-mix(in srgb, var(--sf-panel), transparent 9%);
}}

.sf-footer--vertical-directory,
.sf-footer--expanded-index-footer,
.sf-footer--archive-footer {{
  grid-template-columns: 0.85fr 1.15fr;
}}

.sf-footer--vertical-directory .sf-footer-brand,
.sf-footer--expanded-index-footer .sf-footer-brand,
.sf-footer--archive-footer .sf-footer-brand {{
  grid-column: 1;
}}

.sf-footer--vertical-directory .sf-footer-contact,
.sf-footer--expanded-index-footer .sf-footer-contact,
.sf-footer--archive-footer .sf-footer-contact {{
  grid-column: 1;
}}

.sf-footer--vertical-directory .sf-footer-sitemap,
.sf-footer--expanded-index-footer .sf-footer-sitemap,
.sf-footer--archive-footer .sf-footer-sitemap {{
  grid-column: 2;
  grid-row: 2 / span 2;
}}

.sf-footer--vertical-directory .sf-footer-sitemap ul,
.sf-footer--expanded-index-footer .sf-footer-sitemap ul,
.sf-footer--archive-footer .sf-footer-sitemap ul,
.sf-footer--minimal-complete-footer .sf-footer-sitemap ul {{
  grid-template-columns: 1fr;
}}

.sf-footer--asymmetric-footer,
.sf-footer--split-footer {{
  grid-template-columns: minmax(0, 0.8fr) minmax(0, 1.2fr);
}}

.sf-footer--asymmetric-footer .sf-footer-brand,
.sf-footer--split-footer .sf-footer-brand,
.sf-footer--footer-hero .sf-footer-brand {{
  grid-column: 1;
  padding: clamp(1.2rem, 2.8vw, 2.4rem);
  border-left: 4px solid var(--sf-accent);
  background: color-mix(in srgb, var(--sf-panel), transparent 8%);
}}

.sf-footer--asymmetric-footer .sf-footer-contact,
.sf-footer--split-footer .sf-footer-contact,
.sf-footer--footer-hero .sf-footer-contact {{
  grid-column: 1;
}}

.sf-footer--asymmetric-footer .sf-footer-sitemap,
.sf-footer--split-footer .sf-footer-sitemap,
.sf-footer--footer-hero .sf-footer-sitemap {{
  grid-column: 2;
  grid-row: 2 / span 2;
}}

.sf-footer--centered-spa-footer,
.sf-footer--minimal-complete-footer,
.sf-footer--quiet-signature {{
  text-align: center;
}}

.sf-footer--centered-spa-footer .sf-footer-brand,
.sf-footer--centered-spa-footer .sf-footer-contact,
.sf-footer--centered-spa-footer .sf-footer-sitemap,
.sf-footer--minimal-complete-footer .sf-footer-brand,
.sf-footer--minimal-complete-footer .sf-footer-contact,
.sf-footer--minimal-complete-footer .sf-footer-sitemap,
.sf-footer--quiet-signature .sf-footer-brand,
.sf-footer--quiet-signature .sf-footer-contact,
.sf-footer--quiet-signature .sf-footer-sitemap {{
  grid-column: 2 / 12;
  justify-items: center;
}}

.sf-footer--chip-footer .sf-footer-sitemap ul,
.sf-footer--modular-island-footer .sf-footer-sitemap ul,
.sf-footer--island-footer .sf-footer-sitemap ul {{
  display: flex;
  flex-wrap: wrap;
}}

.sf-footer--chip-footer .sf-footer-sitemap a,
.sf-footer--modular-island-footer .sf-footer-sitemap a,
.sf-footer--island-footer .sf-footer-sitemap a {{
  padding: 0.45rem 0.7rem;
  border: 1px solid var(--sf-line);
  border-radius: 999px;
  background: color-mix(in srgb, var(--sf-panel), transparent 10%);
}}

.sf-footer-large-mark {{
  grid-column: 1 / -1;
  width: clamp(6rem, 18vw, 13rem);
  min-height: clamp(5rem, 14vw, 11rem);
  padding: clamp(0.4rem, 1.5vw, 1rem);
  color: color-mix(in srgb, var(--sf-accent), transparent 52%);
}}

.sf-footer-large-mark::before,
.sf-footer-large-mark::after {{
  content: none;
}}

.sf-footer-path i {{
  width: 100%;
  height: 2px;
  background: var(--sf-accent);
}}

.sf-footer-cta-card,
.sf-footer-learning {{
  justify-content: flex-start;
  flex-wrap: wrap;
  padding: 0.8rem;
  border: 1px solid var(--sf-line);
  background: color-mix(in srgb, var(--sf-panel), transparent 8%);
}}

.sf-footer-cta-card a,
.sf-footer-learning a {{
  color: inherit;
  text-decoration: none;
  font-weight: 800;
}}

.sf-cookie-banner {{
  position: fixed;
  z-index: 90;
  left: 50%;
  bottom: 1rem;
  transform: translateX(-50%);
  width: min(520px, calc(100vw - 2rem));
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 0.58rem;
  align-items: center;
  padding: 0.72rem 0.78rem;
  border: 1px solid var(--sf-line);
  border-radius: min(22px, calc(var(--sf-radius) + 6px));
  background: color-mix(in srgb, var(--sf-panel), white 5%);
  color: color-mix(in srgb, var(--sf-deep), black 16%);
  box-shadow: var(--sf-shadow);
}}

.sf-cookie-banner p {{
  margin: 0;
  font-size: 0.76rem;
  line-height: 1.35;
}}

.sf-cookie-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.34rem;
}}

.sf-cookie-actions button,
.sf-cookie-actions a {{
  min-height: 2.15rem;
  padding: 0.48rem 0.62rem;
  border-radius: var(--sf-radius);
  border: 1px solid var(--sf-line);
  background: color-mix(in srgb, var(--sf-deep), black 12%);
  color: var(--sf-panel);
  text-decoration: none;
  font-size: 0.72rem;
  font-weight: 800;
}}

.sf-cookie-actions a {{
  background: transparent;
  color: color-mix(in srgb, var(--sf-deep), black 16%);
}}

.sf-cookie-banner.is-hidden {{
  display: none;
}}

body.public-menu-locked .sf-cookie-banner {{
  opacity: 0;
  pointer-events: none;
}}

body.public-menu-locked .sf-floating-tools {{
  opacity: 0;
  pointer-events: none;
}}

.sf-floating-tools {{
  position: fixed;
  right: max(1rem, calc((100vw - 1180px) / 2));
  bottom: 1rem;
  z-index: 95;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.58rem;
}}

.sf-floating-whatsapp,
.sf-floating-accessibility,
.sf-back-to-top {{
  width: 2.95rem;
  height: 2.95rem;
  display: inline-grid;
  place-items: center;
  border-radius: 50%;
  border: 1px solid color-mix(in srgb, var(--sf-panel), transparent 50%);
  box-shadow: 0 18px 40px color-mix(in srgb, var(--sf-ink), transparent 78%);
}}

.sf-floating-whatsapp {{
  order: 1;
  background: #25d366;
  color: #ffffff;
}}

.sf-floating-accessibility {{
  order: 2;
  background: color-mix(in srgb, var(--sf-panel), white 8%);
  color: color-mix(in srgb, var(--sf-deep), black 10%);
}}

.sf-floating-whatsapp svg,
.sf-floating-accessibility svg {{
  width: 1.55rem;
  height: 1.55rem;
  fill: currentColor;
}}

.sf-back-to-top {{
  order: 3;
  background: color-mix(in srgb, var(--sf-ink), var(--sf-accent) 18%);
  color: #fffaf1;
  opacity: 0;
  visibility: hidden;
  pointer-events: none;
  transform: translateY(4px);
  transition: opacity 160ms ease, transform 160ms ease, visibility 160ms ease;
}}

.sf-back-to-top span {{
  display: block;
  font-size: 1.08rem;
  font-weight: 900;
  line-height: 1;
}}

.sf-back-to-top.is-visible {{
  opacity: 1;
  visibility: visible;
  pointer-events: auto;
  transform: none;
}}

.sf-floating--atelier-tab .sf-back-to-top,
.sf-floating--atelier-tab .sf-floating-accessibility,
.sf-floating--rail-button .sf-back-to-top,
.sf-floating--rail-button .sf-floating-accessibility,
.sf-floating--index-button .sf-back-to-top,
.sf-floating--index-button .sf-floating-accessibility {{
  border-radius: 4px;
}}

.sf-floating--soft-capsule .sf-floating-whatsapp,
.sf-floating--soft-capsule .sf-floating-accessibility,
.sf-floating--soft-capsule .sf-back-to-top,
.sf-floating--chip-button .sf-floating-whatsapp,
.sf-floating--chip-button .sf-floating-accessibility,
.sf-floating--chip-button .sf-back-to-top {{
  border-radius: 999px 999px 999px 24px;
}}

.sf-floating--timeline-dot .sf-floating-whatsapp,
.sf-floating--timeline-dot .sf-floating-accessibility,
.sf-floating--timeline-dot .sf-back-to-top,
.sf-floating--progress-button .sf-floating-whatsapp,
.sf-floating--progress-button .sf-floating-accessibility,
.sf-floating--progress-button .sf-back-to-top {{
  outline: 2px solid color-mix(in srgb, var(--sf-accent), transparent 62%);
  outline-offset: 4px;
}}

.sf-floating--corner-button .sf-floating-whatsapp,
.sf-floating--corner-button .sf-floating-accessibility,
.sf-floating--corner-button .sf-back-to-top,
.sf-floating--architectural-button .sf-floating-whatsapp,
.sf-floating--architectural-button .sf-floating-accessibility,
.sf-floating--architectural-button .sf-back-to-top {{
  border-radius: 0 45% 0 45%;
}}

@media (max-width: 1180px) and (min-width: 1025px) {{
  .sf-header-shell {{
    grid-template-columns: minmax(150px, 0.7fr) auto;
  }}
  .sf-desktop-nav {{
    grid-column: 1 / -1;
    order: 4;
    justify-content: center;
  }}
  .sf-header-actions {{
    justify-self: end;
  }}
  .sf-header-feature {{
    display: none;
  }}
  .sf-header--split-logo .sf-header-shell {{
    grid-template-columns: 1fr auto;
  }}
  .sf-header--split-logo .sf-desktop-nav {{
    display: flex;
    grid-column: 1 / -1;
  }}
  .sf-header--split-logo .sf-split-nav-group {{
    display: contents;
  }}
}}

@media (max-width: 1024px) {{
  .sf-identity-banner {{
    justify-content: space-between;
    padding-inline: 0.8rem;
  }}
  .sf-banner-brand span:last-child {{
    font-size: 0.72rem;
  }}
  .sf-header-shell,
  .sf-header--editorial-masthead .sf-header-shell,
  .sf-header--spa-symmetry .sf-header-shell,
  .sf-header--quiet-minimal .sf-header-shell,
  .sf-header--split-logo .sf-header-shell {{
    width: min(100% - 1.4rem, 720px);
    min-height: 64px;
    grid-template-columns: minmax(0, 1fr) auto auto;
    justify-items: stretch;
    text-align: left;
  }}
  .sf-header-feature,
  .sf-desktop-nav,
  .sf-action-link {{
    display: none !important;
  }}
  .sf-brand-lockup img {{
    width: clamp(2.35rem, 7vw, 3.2rem);
    height: clamp(2.35rem, 7vw, 3.2rem);
  }}
  .sf-brand-lockup span {{
    font-size: 0.76rem;
  }}
  .sf-header-actions {{
    justify-content: end;
  }}
  .sf-header-cta {{
    min-height: 2.35rem;
    padding: 0.58rem 0.72rem;
    font-size: 0.72rem;
  }}
  .sf-menu-button {{
    display: inline-flex;
  }}
  .sf-public-footer,
  .sf-footer--vertical-directory,
  .sf-footer--expanded-index-footer,
  .sf-footer--archive-footer,
  .sf-footer--asymmetric-footer,
  .sf-footer--split-footer {{
    grid-template-columns: 1fr;
    padding-inline: 1rem;
  }}
  .sf-public-footer > *,
  .sf-footer--vertical-directory .sf-footer-brand,
  .sf-footer--vertical-directory .sf-footer-contact,
  .sf-footer--vertical-directory .sf-footer-sitemap,
  .sf-footer--expanded-index-footer .sf-footer-brand,
  .sf-footer--expanded-index-footer .sf-footer-contact,
  .sf-footer--expanded-index-footer .sf-footer-sitemap,
  .sf-footer--archive-footer .sf-footer-brand,
  .sf-footer--archive-footer .sf-footer-contact,
  .sf-footer--archive-footer .sf-footer-sitemap,
  .sf-footer--asymmetric-footer .sf-footer-brand,
  .sf-footer--asymmetric-footer .sf-footer-contact,
  .sf-footer--asymmetric-footer .sf-footer-sitemap,
  .sf-footer--split-footer .sf-footer-brand,
  .sf-footer--split-footer .sf-footer-contact,
  .sf-footer--split-footer .sf-footer-sitemap,
  .sf-footer--centered-spa-footer .sf-footer-brand,
  .sf-footer--centered-spa-footer .sf-footer-contact,
  .sf-footer--centered-spa-footer .sf-footer-sitemap,
  .sf-footer--minimal-complete-footer .sf-footer-brand,
  .sf-footer--minimal-complete-footer .sf-footer-contact,
  .sf-footer--minimal-complete-footer .sf-footer-sitemap,
  .sf-footer--quiet-signature .sf-footer-brand,
  .sf-footer--quiet-signature .sf-footer-contact,
  .sf-footer--quiet-signature .sf-footer-sitemap {{
    grid-column: 1 / -1;
    grid-row: auto;
  }}
  .sf-footer-sitemap ul {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }}
  .sf-footer-close {{
    align-items: flex-start;
    flex-direction: column;
  }}
  .sf-cookie-banner {{
    left: 0.75rem;
    right: 0.75rem;
    bottom: 0.75rem;
    transform: none;
    width: auto;
    grid-template-columns: 1fr;
    padding: 0.7rem;
    border-radius: 18px;
  }}
  .sf-floating-tools {{
    right: 0.85rem;
    bottom: 0.85rem;
  }}
  body.public-cookie-visible .sf-floating-tools {{
    bottom: 7.4rem;
  }}
}}

@media (max-width: 430px) {{
  .sf-identity-banner {{
    min-height: 36px;
    gap: 0.35rem;
  }}
  .sf-mini-mark {{
    width: 1.45rem;
    height: 1.45rem;
  }}
  .sf-language-switcher button {{
    min-width: 1.7rem;
  }}
  .sf-header-shell {{
    width: min(100% - 1rem, 420px);
    gap: 0.45rem;
  }}
  .sf-brand-lockup span {{
    max-width: 6.4rem;
    font-size: 0.68rem;
  }}
  .sf-header-cta {{
    max-width: 6.4rem;
    padding-inline: 0.55rem;
  }}
  .sf-mobile-nav,
  .sf-menu--tile-grid .sf-mobile-nav,
  .sf-menu--grid-menu .sf-mobile-nav,
  .sf-menu--modular-grid-menu .sf-mobile-nav,
  .sf-menu--round-tile-menu .sf-mobile-nav {{
    grid-template-columns: 1fr;
  }}
  .sf-mobile-link {{
    min-height: 2.85rem;
    font-size: 1.02rem;
  }}
  .sf-footer-sitemap ul {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }}
  .sf-floating-whatsapp,
  .sf-floating-accessibility,
  .sf-back-to-top {{
    width: 2.55rem;
    height: 2.55rem;
  }}
  body.public-cookie-visible .sf-floating-tools {{
    bottom: 8.1rem;
  }}
}}

@media (prefers-reduced-motion: reduce) {{
  .sf-mobile-menu,
  .sf-back-to-top {{
    transition: none !important;
  }}
}}
{CSS_END}
""".strip()


def replace_generated_css(existing: str, block: str) -> str:
    pattern = re.compile(
        rf"\n?{re.escape(CSS_START)}.*?{re.escape(CSS_END)}\n?",
        flags=re.DOTALL,
    )
    cleaned = pattern.sub("\n", existing).rstrip()
    return f"{cleaned}\n\n{block}\n"


PAGE_LABELS = {
    "index": "Home",
    "about": "About",
    "care": "Care",
    "laser": "Laser",
    "skin": "Skin",
    "results": "Results",
    "journal": "Journal",
    "blog": "Journal",
    "contact": "Contact",
    "consultation": "Consultation",
    "values": "Values",
    "mission": "Mission",
    "testimonials": "Testimonials",
    "faq": "FAQ",
    "privacy": "Privacy",
    "cookies": "Cookies",
    "accessibility": "Accessibility",
    "sitemap": "Sitemap",
    "legal": "Legal",
    "thank-you": "Thank You",
    "404": "Page Not Found",
}

PAGE_H1 = {
    "index": "Biomedicine-led skin, laser and aesthetic care",
    "about": "About Franciele Sofiati",
    "care": "Consultation-first care",
    "laser": "Laser guidance with evaluation",
    "skin": "Skin support with calm planning",
    "results": "Results with realistic expectations",
    "journal": "Journal and care guidance",
    "blog": "Journal and care guidance",
    "contact": "Contact the clinic",
    "consultation": "Request a consultation",
    "values": "Values that guide care",
    "mission": "A calm, responsible care mission",
    "testimonials": "Patient words and care context",
    "faq": "Questions before your appointment",
    "privacy": "Privacy information",
    "cookies": "Cookie preferences",
    "accessibility": "Accessibility",
    "sitemap": "Sitemap",
    "legal": "Legal information",
    "thank-you": "Thank you",
    "404": "Page not found",
}

PUBLIC_META_DESCRIPTION = (
    "Franciele Sofiati offers biomedicine-led skin, laser and aesthetic care in Londrina, "
    "with consultation-first guidance and realistic expectations."
)

OLD_SAFE_BODY_SENTENCE = (
    "Care is presented with calm language, responsible expectations, and a consultation-led path."
)

SAFE_BODY_SENTENCE = (
    "Before any treatment is chosen, the consultation clarifies goals, comfort, timing, and realistic next steps."
)

HEADING_REPLACEMENTS = {
    "Brand trust and human trust": "Trust begins with the consultation",
    "Care route": "A clear path through care",
    "Consultation approach": "How the first conversation works",
    "Safety and reassurance statement": "Safety, comfort and clear expectations",
    "Skin and laser education route": "Skin and laser guidance",
    "Journal and learning route": "Guidance for later reading",
    "Conversion and contact bridge": "When you are ready to talk",
    "Final brand bridge": "A calm next step",
    "Final CTA": "Ready for a careful next step",
    "Final CTA bridge": "Ready for a careful next step",
    "Final redirect": "Find the right page",
    "Final accessibility bridge": "Tell us what would make the site easier",
    "Final reassurance CTA": "Continue with clear expectations",
    "Final contact CTA": "Choose the contact route that feels easiest",
    "Footer bridge": "A clear path back to the clinic",
    "Final cookie bridge": "Questions about cookie preferences",
    "Final legal bridge": "Questions about this information",
    "Final privacy bridge": "Questions about privacy",
    "Final sitemap bridge": "Find the next page",
    "Contact bridge": "A simple way to continue",
    "Feedback route": "Share an accessibility concern",
    "WhatsApp route": "Message the clinic on WhatsApp",
    "Form or WhatsApp route": "Choose form or WhatsApp",
    "Sofiati or WhatsApp route": "Choose form or WhatsApp",
    "Location and service context": "Service area and appointment context",
    "Social and contact route": "Social and direct contact",
    "Contact route": "A direct way to reach the clinic",
    "Consultation bridge": "Talk through the next step",
    "Consultation route": "Consultation before decisions",
    "Education route": "Care education before action",
    "Education and journal route": "Read guidance before deciding",
    "Suitability-first statement": "Suitability comes first",
    "Skin and context evaluation": "Your skin context matters",
    "Individual skin context": "Your skin context matters",
    "Process overview": "How the visit is planned",
    "No guarantee statement": "No promises without evaluation",
    "Patient words and care context": "Patient stories with context",
    "Ethical note on client stories": "Client stories stay responsible",
    "Final reassurance": "Continue at a comfortable pace",
}

PAGE_CONTEXT = {
    "index": "skin, laser and aesthetic care",
    "about": "Franciele Sofiati's professional care philosophy",
    "care": "the care plan",
    "laser": "laser suitability and safety",
    "skin": "skin quality and personal goals",
    "results": "realistic results and follow-up",
    "journal": "care education",
    "blog": "care education",
    "contact": "contact and appointment questions",
    "consultation": "the first consultation",
    "values": "the values behind care",
    "mission": "responsible aesthetic biomedicine",
    "testimonials": "patient stories and responsible context",
    "faq": "common appointment questions",
    "privacy": "privacy and visitor information",
    "cookies": "cookie preferences",
    "accessibility": "accessible browsing",
    "sitemap": "site navigation",
    "legal": "responsible use of site information",
    "thank-you": "what happens after contact",
    "404": "the right next page",
}

PARAGRAPH_REPLACEMENTS = {
    "Trust begins with the consultation": "Trust is built through a careful first conversation, clear limits, and choices that respect your skin, timing, comfort, and expectations.",
    "A clear path through care": "The path is simple: listen first, evaluate carefully, explain the options, and move forward only when the plan makes sense for you.",
    "How the first conversation works": "The consultation gives space for questions, preferences, history, and realistic planning before any procedure is considered.",
    "Safety, comfort and clear expectations": "Safety is treated as part of the experience, from suitability and comfort to aftercare and the pace of each decision.",
    "Skin and laser guidance": "Education helps you understand skin quality, laser suitability, preparation, and what a responsible plan can and cannot promise.",
    "Guidance for later reading": "The journal keeps practical guidance close, so you can read calmly before choosing your next appointment or question.",
    "When you are ready to talk": "When you feel ready, the next step is a direct conversation with the clinic about goals, timing, and what should be evaluated first.",
    "A calm next step": "You can continue with a consultation request, ask a focused question, or read more before deciding what feels right.",
    "Ready for a careful next step": "Start with a consultation request and bring your questions, goals, timing, and any concerns you want clarified.",
    "Find the right page": "Use the main navigation to return to care guidance, contact the clinic, or continue to the page that best fits your question.",
    "Tell us what would make the site easier": "Accessibility feedback is welcome, especially if a page, menu, colour, or interaction makes information harder to use.",
    "Continue with clear expectations": "A responsible plan keeps expectations honest and leaves room for individual response, aftercare, and follow-up questions.",
    "Choose the contact route that feels easiest": "Use WhatsApp for a direct message or the contact page for a calmer written request before scheduling.",
    "A clear path back to the clinic": "The footer keeps contact, care pages, legal information, and accessibility links available without interrupting the page.",
    "Questions about cookie preferences": "Cookie choices can be reviewed through the cookie page, with essential preferences kept simple and transparent.",
    "Questions about this information": "For questions about legal, privacy, accessibility, or educational content, use the contact route so the clinic can review the request.",
    "Questions about privacy": "Privacy questions can be sent through the contact page, especially if you need a correction, clarification, or deletion request.",
    "Find the next page": "The sitemap gathers care pages, contact routes, privacy information, and accessibility resources in one readable place.",
    "A simple way to continue": "The next step can stay simple: read a related page, ask a question, or request a consultation when you feel ready.",
    "Share an accessibility concern": "If something is difficult to read, navigate, or operate, send the concern so the site can be improved with care.",
    "Message the clinic on WhatsApp": "WhatsApp is available for direct questions, appointment guidance, and deciding whether a consultation is the right next step.",
    "Choose form or WhatsApp": "Choose the route that suits the question: WhatsApp for a quick message or the form for more context.",
    "Service area and appointment context": "Care is offered from Londrina, PR, with appointment details and suitability discussed before any treatment decision.",
    "Social and direct contact": "Instagram is available for brand updates, while WhatsApp and the contact page are clearer routes for appointment questions.",
    "A direct way to reach the clinic": "Use the contact page or WhatsApp when you want guidance about timing, suitability, preparation, or the first consultation.",
    "Talk through the next step": "A conversation helps decide whether to read more, schedule an evaluation, or wait until the timing feels better.",
    "Consultation before decisions": "Laser, skin, and aesthetic decisions should begin with evaluation rather than assumptions or quick promises.",
    "Care education before action": "Clear explanations make each option easier to understand before you decide whether to continue.",
    "Read guidance before deciding": "Related journal and FAQ pages help you prepare better questions before requesting an appointment.",
    "Suitability comes first": "Laser planning starts with skin context, goals, contraindications, and the level of comfort needed for a responsible plan.",
    "Your skin context matters": "Skin history, sensitivity, routine, timing, and expectations shape whether a treatment is appropriate and how it should be planned.",
    "How the visit is planned": "The visit moves through listening, evaluation, explanation, decision-making, and aftercare guidance without rushing the process.",
    "No promises without evaluation": "Results cannot be promised without individual evaluation, because response, timing, and aftercare vary from person to person.",
    "Patient stories with context": "Client stories are treated as personal experiences, not guarantees of what another person will see or feel.",
    "Client stories stay responsible": "Testimonials should support reassurance while keeping expectations realistic and avoiding exaggerated claims.",
    "Continue at a comfortable pace": "You can continue with a question, a consultation request, or more reading before choosing any next step.",
}

LOGO_REPLACEMENTS = {
    "sofiati-logo-primary-sage.png": "sofiati-logo-primary-transparent.png",
    "sofiati-logo-primary-white.png": "sofiati-logo-light-transparent.png",
    "sofiati-logo-primary-bronze.png": "sofiati-logo-gold-transparent.png",
    "sofiati-signature-sage.png": "sofiati-logo-primary-transparent.png",
    "sofiati-signature-white.png": "sofiati-logo-light-transparent.png",
    "sofiati-monogram-sage.png": "sofiati-logo-monogram-transparent.png",
    "sofiati-monogram-white.png": "sofiati-logo-monogram-light-transparent.png",
    "sofiati-monogram-bronze.png": "sofiati-logo-monogram-transparent.png",
}


def page_label(path: Path) -> str:
    return PAGE_LABELS.get(path.stem, path.stem.replace("-", " ").title())


def page_h1(path: Path) -> str:
    return PAGE_H1.get(path.stem, page_label(path))


def replace_meta_content(text: str, selector: str, value: str) -> str:
    return re.sub(
        rf'(<meta\s+{selector}\s+content=")[^"]*(")',
        rf"\g<1>{value}\2",
        text,
        flags=re.I,
    )


def remove_damaged_head_paragraphs(text: str) -> str:
    return re.sub(
        r'\n\s*<p>(?:Before any treatment is chosen, the consultation clarifies goals, comfort, timing, and realistic next steps\.|")\s*(?:"\s*)?/>\s*',
        "\n",
        text,
        flags=re.I,
    )


def ensure_meta_name(text: str, name: str, content: str, after_pattern: str) -> str:
    selector = rf'name="{re.escape(name)}"'
    if re.search(rf'<meta\s+{selector}\s+content="', text, flags=re.I):
        return replace_meta_content(text, selector, content)
    return re.sub(
        after_pattern,
        rf'\g<1>\n    <meta name="{name}" content="{content}" />\n    ',
        text,
        count=1,
        flags=re.I,
    )


def ensure_meta_property(text: str, prop: str, content: str, after_pattern: str) -> str:
    selector = rf'property="{re.escape(prop)}"'
    if re.search(rf'<meta\s+{selector}\s+content="', text, flags=re.I):
        return replace_meta_content(text, selector, content)
    return re.sub(
        after_pattern,
        rf'\g<1>\n    <meta property="{prop}" content="{content}" />\n    ',
        text,
        count=1,
        flags=re.I,
    )


def public_heading(value: str) -> str:
    clean = re.sub(r"\s+", " ", value).strip()
    return HEADING_REPLACEMENTS.get(clean, clean)


def paragraph_for_heading(page_stem: str, heading: str) -> str:
    clean = public_heading(heading)
    if clean in PARAGRAPH_REPLACEMENTS:
        return PARAGRAPH_REPLACEMENTS[clean]
    context = PAGE_CONTEXT.get(page_stem, "care")
    lowered = clean[:1].lower() + clean[1:]
    if page_stem in {"privacy", "cookies", "legal", "accessibility", "sitemap"}:
        return f"{clean} is explained in plain language so visitors can find the right information, understand their options, and contact the clinic when a question needs review."
    if page_stem in {"contact", "consultation", "thank-you"}:
        return f"{clean} keeps the next step practical, with space for questions, timing, comfort, and the details needed before a consultation is arranged."
    if page_stem in {"journal", "blog", "faq"}:
        return f"{clean} gives calm, readable guidance so you can prepare better questions before choosing a consultation or treatment path."
    return f"{clean} connects {context} with responsible evaluation, clear expectations, and decisions made at a calm pace."


def rewrite_public_headings(text: str) -> str:
    def replace_heading(match: re.Match[str]) -> str:
        open_tag, value, close_tag = match.groups()
        plain = re.sub(r"<.*?>", "", value, flags=re.S)
        return f"{open_tag}{public_heading(plain)}{close_tag}"

    return re.sub(r"(<h[12]\b[^>]*>)(.*?)(</h[12]>)", replace_heading, text, flags=re.S)


def rewrite_template_paragraphs(text: str, page_stem: str) -> str:
    template = re.compile(
        r"<p>([^<.]+?)\s+is presented with calm language, responsible expectations, and a consultation-led path\.?\s*"
        r"(?:Before any treatment is chosen, the consultation clarifies goals, comfort, timing, and realistic next steps\.)?</p>",
        flags=re.I,
    )

    def replace_template(match: re.Match[str]) -> str:
        heading = match.group(1).strip()
        return f"<p>{paragraph_for_heading(page_stem, heading)}</p>"

    text = template.sub(replace_template, text)
    return text.replace("path.Before", "path. Before")


def sanitize_internal_copy(text: str, concept: Path, spec: PartialSpec) -> str:
    concept_title = concept.name.split("-", 1)[1].replace("-", " ").title()
    escaped_title = re.escape(concept_title)
    escaped_signature = re.escape(spec.signature)

    text = re.sub(rf"\b{escaped_title}\s*/\s*", "", text)
    text = re.sub(rf"\s+with\s+{escaped_title}\b", "", text)
    text = re.sub(rf"\b{escaped_title}\s+expresses this as [^.]+\.?", SAFE_BODY_SENTENCE, text)
    text = re.sub(rf"\b{escaped_title}:\s*[^<]+", SAFE_BODY_SENTENCE, text)
    text = re.sub(rf"\b{escaped_title}\b", "Sofiati", text)
    text = re.sub(rf"\b{escaped_signature}\b", "Sofiati care", text, flags=re.I)
    text = re.sub(r"\bDestination\s+\d+\b", "Sofiati care", text)
    text = re.sub(
        r">(?!<)([^<>.]*\b(?:website|direction|translated into|shapes the pacing|visual\s+note|design\s+direction|concept\s+label|should\s+feel|route\s+system|botanical\s+system)\b[^<>.]*\.)",
        f">{SAFE_BODY_SENTENCE}",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"(<p class=\"c\d+-eyebrow\">)([^<]*)(</p>)",
        lambda match: f"{match.group(1)}{clean_eyebrow(match.group(2))}{match.group(3)}",
        text,
    )
    text = re.sub(
        r"(<div class=\"c\d+-section-note\">\s*<span>).*?(</span>)",
        rf"\1Use the consultation route when you are ready for a focused conversation.\2",
        text,
        flags=re.S,
    )
    text = re.sub(r"\s+with\s+Sofiati\b", "", text)
    text = re.sub(
        r'alt="Franciele Sofiati full portrait for [^"]* section (\d+)"',
        r'alt="Franciele Sofiati portrait for consultation guidance"',
        text,
    )
    text = re.sub(
        r'alt="Franciele Sofiati [^"]* for [^"]* section (\d+)"',
        r'alt="Franciele Sofiati portrait for consultation guidance"',
        text,
    )
    return text


def repair_previous_sanitizer_damage(text: str) -> str:
    bad = re.escape(SAFE_BODY_SENTENCE)
    text = re.sub(
        rf"<{bad}css\" />",
        '<link rel="stylesheet" href="css/concept.css" />',
        text,
    )
    text = re.sub(
        rf"<{bad}js\" defer></script>",
        '<script src="js/concept.js" defer></script>',
        text,
    )
    text = re.sub(rf"<{bad}", f"<p>{SAFE_BODY_SENTENCE}", text)
    return text


def polish_safe_copy(text: str) -> str:
    text = text.replace(OLD_SAFE_BODY_SENTENCE, SAFE_BODY_SENTENCE)
    text = re.sub(r"\s*It should feel[^.]*\.", "", text, flags=re.I)
    safe = re.escape(SAFE_BODY_SENTENCE)
    text = re.sub(rf"({safe})(?:\s*{safe})+", SAFE_BODY_SENTENCE, text)
    text = text.replace(f"{SAFE_BODY_SENTENCE}A calm", f"{SAFE_BODY_SENTENCE} A calm")
    text = text.replace(f"{SAFE_BODY_SENTENCE}Care", f"{SAFE_BODY_SENTENCE} Care")
    def dedupe_paragraph(match: re.Match[str]) -> str:
        content = match.group(1)
        first = content.find(SAFE_BODY_SENTENCE)
        if first == -1:
            return match.group(0)
        before = content[: first + len(SAFE_BODY_SENTENCE)]
        after = content[first + len(SAFE_BODY_SENTENCE) :].replace(SAFE_BODY_SENTENCE, "").strip()
        joined = f"{before} {after}".strip()
        return f"<p>{joined}</p>"

    text = re.sub(r"<p>(.*?)</p>", dedupe_paragraph, text, flags=re.S)
    return text


def clean_eyebrow(value: str) -> str:
    clean = value.split("/")[-1].strip()
    if re.fullmatch(r"Section\s+\d+", clean, flags=re.I):
        return "Care perspective"
    if re.fullmatch(r"Step\s+\d+", clean, flags=re.I):
        return "Guided planning"
    replacements = {
        "Step 02": "Guided planning",
        "Section 03": "Care guidance",
        "Section 08": "Learning",
        "Section 09": "Contact options",
        "Care route": "Care guidance",
        "Learning route": "Learning",
        "Safety and reassurance statement": "Responsible care",
        "Skin and laser education route": "Care education",
        "Journal and learning route": "Learning",
        "Contact bridge": "Contact options",
        "Conversion and contact bridge": "Contact options",
        "Footer bridge": "Contact options",
        "Final CTA": "Next step",
        "Final CTA bridge": "Next step",
        "Final contact CTA": "Contact options",
        "Final legal bridge": "Questions",
        "Final privacy bridge": "Questions",
        "Final cookie bridge": "Questions",
        "Final accessibility bridge": "Feedback",
        "Opening promise": "Care promise",
        "Continue": "Next step",
    }
    return replacements.get(clean, clean or "Sofiati care")


def sanitize_page(path: Path, concept: Path, spec: PartialSpec) -> None:
    text = path.read_text(encoding="utf-8")
    text = repair_previous_sanitizer_damage(text)
    text = remove_damaged_head_paragraphs(text)
    for old, new in LOGO_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = sanitize_internal_copy(text, concept, spec)
    text = rewrite_public_headings(text)
    text = rewrite_template_paragraphs(text, path.stem)
    text = polish_safe_copy(text)
    title = f"{page_label(path)} | {BRAND_NAME}"
    text = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", text, count=1, flags=re.S)
    text = ensure_meta_name(
        text,
        "description",
        PUBLIC_META_DESCRIPTION,
        r'(<meta\s+name="viewport"[^>]*>\s*)',
    )
    text = ensure_meta_property(
        text,
        "og:title",
        title,
        r'(<link\s+rel="canonical"[^>]*>\s*)',
    )
    text = ensure_meta_property(
        text,
        "og:description",
        PUBLIC_META_DESCRIPTION,
        r'(<meta\s+property="og:title"[^>]*>\s*)',
    )
    text = ensure_meta_property(
        text,
        "og:image",
        "../../assets/brand/sofiati-logo-primary-transparent.png",
        r'(<meta\s+property="og:description"[^>]*>\s*)',
    )
    text = re.sub(
        r'(<link\s+rel="apple-touch-icon"\s+href=")[^"]*(")',
        r'\1../../assets/brand/sofiati-logo-monogram-transparent.png\2',
        text,
        flags=re.I,
    )
    text = re.sub(
        r"(<h1\b[^>]*>).*?(</h1>)",
        rf"\1{page_h1(path)}\2",
        text,
        count=1,
        flags=re.S,
    )
    path.write_text(text, encoding="utf-8")


def sanitize_partial_head(path: Path) -> None:
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    for old, new in LOGO_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(
        r'(<meta\s+property="og:image"\s+content=")[^"]*(")',
        r'\1../../assets/brand/sofiati-logo-primary-transparent.png\2',
        text,
        flags=re.I,
    )
    text = re.sub(
        r'(<link\s+rel="apple-touch-icon"\s+href=")[^"]*(")',
        r'\1../../assets/brand/sofiati-logo-monogram-transparent.png\2',
        text,
        flags=re.I,
    )
    path.write_text(text, encoding="utf-8")


def sanitize_concept_pages(concepts: list[Path]) -> None:
    for concept, spec in zip(concepts, SPECS, strict=True):
        sanitize_partial_head(concept / "partials" / "head.html")
        for page in concept.glob("*.html"):
            if ".bak" in page.name:
                continue
            sanitize_page(page, concept, spec)


def sanitize_root_index(concepts: list[Path]) -> None:
    index_path = ROOT / "index.html"
    if not index_path.exists():
        return
    text = index_path.read_text(encoding="utf-8")
    for old, new in LOGO_REPLACEMENTS.items():
        text = text.replace(old, new)
    text = re.sub(
        r"<title>.*?</title>",
        f"<title>{BRAND_NAME}</title>",
        text,
        count=1,
        flags=re.S,
    )
    text = re.sub(
        r'(<meta\s+name="description"\s+content=")[^"]*(")',
        rf"\1{PUBLIC_META_DESCRIPTION}\2",
        text,
        flags=re.I,
    )
    text = text.replace("Sofiati website atlas.", "Franciele Sofiati care pathways.")
    text = text.replace("Atlas of 50 standalone premium website directions for Franciele Sofiati.", PUBLIC_META_DESCRIPTION)
    text = text.replace("Open concept", "Open pathway")
    for concept in concepts:
        number = concept.name[:2]
        concept_title = concept.name.split("-", 1)[1].replace("-", " ").title()
        text = re.sub(
            rf'(<a class="selector-card" href="concepts/{re.escape(concept.name)}/index.html">\s*<span>{number}</span>\s*<strong>){re.escape(concept_title)}(</strong>\s*<small>).*?(</small>)',
            rf"\1Care pathway {number}\2Consultation-led skin and laser guidance\3",
            text,
            flags=re.S,
        )
    index_path.write_text(text, encoding="utf-8")


def update_webmanifest() -> None:
    path = ROOT / "site.webmanifest"
    if not path.exists():
        return
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest["icons"] = [
        {"src": "/assets/brand/sofiati-favicon.svg", "sizes": "any", "type": "image/svg+xml"},
        {"src": "/assets/brand/sofiati-logo-primary-transparent.png", "sizes": "1254x1254", "type": "image/png"},
        {"src": "/assets/brand/sofiati-logo-monogram-transparent.png", "sizes": "1254x1254", "type": "image/png"},
    ]
    path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def write_docs(concepts: list[Path]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Sofiati Final Public Partial Systems",
        "",
        "Generated by `scripts/generate_public_partial_systems.py`.",
        "",
        "Public chrome invariants:",
        "",
        "- Desktop navigation: exactly 8 main links.",
        "- Mobile navigation: exactly 8 main links.",
        "- Footer sitemap: exactly 17 links.",
        "- The EN/PT identity banner is separate from the main header and absent from the mobile menu.",
        "- Header Consultation CTA is separate from the menu button and does not replace a main nav link.",
        "- Floating WhatsApp, accessibility, and back-to-top controls are compact bottom-right actions.",
        "- Header, banner, footer, favicon, and social preview references use the approved `logo.png` system.",
        "- Public partial text uses `Franciele Sofiati Biomédica`, not internal concept names.",
        "",
        "| Concept | Internal Direction | Header | Mobile | Footer | Cookie | Floating |",
        "|---|---|---|---|---|---|---|",
    ]
    manifest = []
    for concept, spec in zip(concepts, SPECS, strict=True):
        lines.append(
            f"| {spec.code} | {spec.signature} | `{spec.header}` | `{spec.mobile}` | `{spec.footer}` | `{spec.cookie}` | `{spec.floating}` |"
        )
        manifest.append(
            {
                "concept": concept.name,
                "number": spec.code,
                "internal_direction": spec.signature,
                "header": spec.header,
                "mobile": spec.mobile,
                "footer": spec.footer,
                "cookie": spec.cookie,
                "floating": spec.floating,
                "main_nav_links": [label for label, _ in MAIN_LINKS],
                "footer_links": [label for label, _ in FOOTER_LINKS],
            }
        )
    (DOCS_DIR / "public-partial-system-manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (DOCS_DIR / "public-partial-system-manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        encoding="utf-8",
    )
    DESIGN_DOC.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    concepts = concept_dirs()
    generate_logo_assets()
    for concept, spec in zip(concepts, SPECS, strict=True):
        partials = concept / "partials"
        partials.mkdir(parents=True, exist_ok=True)
        (partials / "header.html").write_text(header(spec) + "\n", encoding="utf-8")
        (partials / "mobile-menu.html").write_text(mobile_menu(spec) + "\n", encoding="utf-8")
        (partials / "footer.html").write_text(footer(spec) + "\n", encoding="utf-8")
        (partials / "cookie-banner.html").write_text(cookie_banner(spec) + "\n", encoding="utf-8")
        (partials / "floating-widgets.html").write_text(floating_widgets(spec) + "\n", encoding="utf-8")
        (concept / "js" / "concept.js").write_text(concept_js(concept.name, spec.code), encoding="utf-8")

        css_path = concept / "css" / "concept.css"
        css_path.write_text(
            replace_generated_css(css_path.read_text(encoding="utf-8"), css_for(spec)),
            encoding="utf-8",
        )

    sanitize_concept_pages(concepts)
    sanitize_root_index(concepts)
    update_webmanifest()
    write_docs(concepts)
    print(f"Generated approved-logo public partial systems for {len(concepts)} concepts.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
