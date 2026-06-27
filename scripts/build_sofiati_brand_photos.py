#!/usr/bin/env python3
"""Build the Sofiati real-photo brand asset system from assets/photos."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "photos"
OUT_DIR = ROOT / "assets" / "brand-photos"


@dataclass(frozen=True)
class PhotoSpec:
    source: str
    slug: str
    scene: str
    mood: str
    use_cases: tuple[str, ...]
    object_position: str
    mobile_notes: str
    alt: str
    gravity: str = "North"


PHOTOS: tuple[PhotoSpec, ...] = (
    PhotoSpec(
        "IMG_1449.jpg.jpeg",
        "studio-seated-soft-smile",
        "dark studio seated portrait",
        "warm, composed, professional",
        ("hero", "about", "profile", "journal", "decorative"),
        "50% 34%",
        "Keep face in the upper third; avoid cropping the seated hand line too tightly.",
        "Franciele Sofiati in a warm studio portrait wearing a white suit",
    ),
    PhotoSpec(
        "IMG_1452.jpg.jpeg",
        "studio-seated-laughing",
        "dark studio seated portrait",
        "open, human, approachable",
        ("profile", "contact", "journal", "decorative"),
        "50% 33%",
        "Use as a smaller trust or contact image so the smile stays clear.",
        "Franciele Sofiati smiling in a professional studio portrait",
    ),
    PhotoSpec(
        "IMG_1453.jpg.jpeg",
        "studio-seated-joyful",
        "dark studio seated portrait",
        "expressive, editorial, confident",
        ("journal", "decorative", "CTA"),
        "50% 30%",
        "Best in editorial crops; keep enough headroom for the upward gaze.",
        "Editorial portrait of Franciele Sofiati laughing in a studio setting",
    ),
    PhotoSpec(
        "IMG_1467.jpg.jpeg",
        "studio-full-poised",
        "dark studio full-body portrait",
        "structured, precise, premium",
        ("hero", "laser", "service-support", "journal"),
        "50% 42%",
        "Use taller frames on mobile; wide crops should keep the full seated posture legible.",
        "Franciele Sofiati in a poised full-body studio portrait",
        "Center",
    ),
    PhotoSpec(
        "IMG_1470.jpg.jpeg",
        "studio-full-direct",
        "dark studio full-body portrait",
        "formal, direct, clinical",
        ("laser", "results", "service-support", "decorative"),
        "50% 43%",
        "Avoid tight square face crops; this works best as a vertical panel.",
        "Franciele Sofiati in a direct full-body studio portrait",
        "Center",
    ),
    PhotoSpec(
        "IMG_1474.jpg.jpeg",
        "studio-crossed-smile",
        "dark studio seated portrait",
        "credible, friendly, polished",
        ("contact", "profile", "journal", "decorative"),
        "50% 36%",
        "Keep knees and hand line secondary; use upper-body crop for contact cards.",
        "Franciele Sofiati smiling in a seated professional portrait",
    ),
    PhotoSpec(
        "IMG_1476.jpg.jpeg",
        "studio-crossed-composed",
        "dark studio seated portrait",
        "calm, restrained, responsible",
        ("results", "profile", "journal", "decorative"),
        "50% 35%",
        "Good for results pages where the image should suggest trust, not outcome proof.",
        "Franciele Sofiati in a calm seated studio portrait",
    ),
    PhotoSpec(
        "IMG_1477.jpg.jpeg",
        "studio-front-composed",
        "dark studio seated portrait",
        "balanced, professional, editorial",
        ("hero", "about", "profile", "footer", "journal"),
        "50% 34%",
        "Works well in oval or square crops; keep eyes above center on mobile.",
        "Franciele Sofiati in a composed front-facing studio portrait",
    ),
    PhotoSpec(
        "IMG_1483.jpg.jpeg",
        "studio-seated-bright-smile",
        "dark studio seated portrait",
        "inviting, warm, high-trust",
        ("contact", "consultation", "profile", "journal"),
        "50% 32%",
        "Use for human contact moments; crop around the face and upper torso.",
        "Franciele Sofiati smiling in a warm consultation-style portrait",
    ),
    PhotoSpec(
        "IMG_1493.jpg.jpeg",
        "studio-close-smile",
        "dark studio close portrait",
        "friendly, intimate, reassuring",
        ("contact", "profile", "consultation", "footer"),
        "50% 30%",
        "Strong small portrait; avoid wide hero crops where the chair dominates.",
        "Close professional portrait of Franciele Sofiati smiling",
    ),
    PhotoSpec(
        "IMG_1495.jpg.jpeg",
        "studio-chair-angled",
        "dark studio seated portrait",
        "editorial, poised, softly confident",
        ("about", "journal", "decorative", "profile"),
        "50% 34%",
        "Use as a vertical editorial crop; keep the shoulder line visible.",
        "Editorial seated portrait of Franciele Sofiati in a white suit",
    ),
    PhotoSpec(
        "IMG_1497.jpg.jpeg",
        "studio-close-composed",
        "dark studio close portrait",
        "serious, responsible, premium",
        ("results", "about", "profile", "journal"),
        "50% 31%",
        "Good for restrained pages; keep the face crop generous and avoid chin clipping.",
        "Composed close portrait of Franciele Sofiati in a professional studio setting",
    ),
    PhotoSpec(
        "IMG_1528.jpg.jpeg",
        "balcony-orange-soft-smile",
        "bright balcony portrait",
        "sunlit, optimistic, skin-care editorial",
        ("hero", "care", "skin", "consultation", "CTA", "journal"),
        "47% 30%",
        "Keep the window glow soft; mobile crop should hold face and orange blouse.",
        "Franciele Sofiati in a bright editorial portrait for aesthetic care",
    ),
    PhotoSpec(
        "IMG_1529.jpg.jpeg",
        "balcony-orange-side-smile",
        "bright balcony side portrait",
        "airy, refined, approachable",
        ("hero", "skin", "journal", "decorative", "CTA"),
        "44% 31%",
        "Best with copy on the right or as a right-looking editorial panel.",
        "Franciele Sofiati smiling beside a bright window in an editorial portrait",
    ),
    PhotoSpec(
        "IMG_1537.jpg.jpeg",
        "balcony-orange-direct",
        "bright balcony direct portrait",
        "confident, colourful, modern",
        ("hero", "about", "skin", "journal", "decorative"),
        "54% 32%",
        "Use strong top-safe crops; the diagonal window gives movement.",
        "Franciele Sofiati in a colourful window-lit editorial portrait",
    ),
    PhotoSpec(
        "IMG_1539.jpg.jpeg",
        "balcony-orange-tilt-smile",
        "bright balcony angled portrait",
        "playful, soft, inviting",
        ("contact", "journal", "decorative"),
        "50% 30%",
        "Best as a journal or small trust image where the angled pose can breathe.",
        "Franciele Sofiati smiling in an angled editorial portrait",
    ),
    PhotoSpec(
        "IMG_1579.jpg.jpeg",
        "balcony-orange-laughing",
        "bright balcony portrait",
        "joyful, human, warm",
        ("consultation", "contact", "journal", "CTA"),
        "52% 31%",
        "Keep hands and face together; avoid tight wide crops.",
        "Franciele Sofiati laughing in a warm consultation-style portrait",
    ),
    PhotoSpec(
        "IMG_1582.jpg.jpeg",
        "balcony-orange-looking-up",
        "bright balcony upward portrait",
        "aspirational, light, editorial",
        ("skin", "journal", "decorative", "CTA"),
        "51% 29%",
        "Keep headroom for the upward gaze; use with airy cream or sage backgrounds.",
        "Franciele Sofiati in an airy editorial portrait looking upward",
    ),
    PhotoSpec(
        "IMG_1609.jpg.jpeg",
        "ivory-room-standing-direct",
        "warm ivory-room portrait",
        "premium, clinical, grounded",
        ("hero", "about", "laser", "service-support", "footer"),
        "50% 32%",
        "Strong for hero panels; keep the blazer and pampas accent in frame.",
        "Franciele Sofiati in a polished ivory-room professional portrait",
    ),
    PhotoSpec(
        "IMG_1612.jpg.jpeg",
        "ivory-room-standing-calm",
        "warm ivory-room portrait",
        "calm, expert, restrained",
        ("hero", "about", "laser", "results", "service-support"),
        "50% 32%",
        "Works well in vertical hero frames and structured clinical pages.",
        "Franciele Sofiati in a calm professional portrait with ivory styling",
    ),
    PhotoSpec(
        "IMG_1626.jpg.jpeg",
        "ivory-room-side-gaze",
        "warm ivory-room side portrait",
        "precise, editorial, contemplative",
        ("laser", "results", "service-support", "journal"),
        "48% 31%",
        "Use where gaze can lead into copy; avoid central text overlays.",
        "Editorial side portrait of Franciele Sofiati in a white blazer",
    ),
    PhotoSpec(
        "IMG_1634.jpg.jpeg",
        "ivory-room-arms-crossed",
        "warm ivory-room direct portrait",
        "authoritative, confident, professional",
        ("hero", "about", "consultation", "laser", "CTA", "footer"),
        "51% 31%",
        "Ideal for high-trust sections; keep shoulders visible on mobile.",
        "Franciele Sofiati in a confident professional portrait wearing a white blazer",
    ),
    PhotoSpec(
        "IMG_1651.jpg.jpeg",
        "ivory-room-arms-crossed-close",
        "warm ivory-room close portrait",
        "direct, trustworthy, premium",
        ("hero", "consultation", "contact", "profile", "CTA"),
        "51% 29%",
        "Strong small portrait and contact image; crop face and shoulders generously.",
        "Close confident portrait of Franciele Sofiati for professional consultation",
    ),
    PhotoSpec(
        "IMG_1661.jpg.jpeg",
        "ivory-room-window-side",
        "warm window side portrait",
        "thoughtful, refined, editorial",
        ("about", "journal", "decorative", "profile"),
        "47% 30%",
        "Best in vertical panels with the window line as a design accent.",
        "Franciele Sofiati in a refined window-lit professional portrait",
    ),
    PhotoSpec(
        "IMG_1662.jpg.jpeg",
        "ivory-room-window-touch",
        "warm window side portrait",
        "soft, sophisticated, reassuring",
        ("care", "consultation", "journal", "decorative"),
        "48% 30%",
        "Use for softer care sections; keep hand gesture visible if possible.",
        "Franciele Sofiati in a soft window-lit consultation portrait",
    ),
    PhotoSpec(
        "IMG_1666.jpg.jpeg",
        "ivory-room-window-composed",
        "warm window side portrait",
        "quiet, reflective, premium",
        ("skin", "results", "journal", "decorative"),
        "48% 30%",
        "Use in calmer editorial moments; avoid over-dark overlays.",
        "Franciele Sofiati in a quiet professional portrait by a window",
    ),
    PhotoSpec(
        "IMG_1667.jpg.jpeg",
        "ivory-room-window-attentive",
        "warm window side portrait",
        "attentive, expert, gentle",
        ("consultation", "contact", "journal", "profile"),
        "49% 30%",
        "Good for consultation prompts; preserve the face and hand position.",
        "Franciele Sofiati in an attentive consultation-style portrait",
    ),
    PhotoSpec(
        "IMG_1669.jpg.jpeg",
        "ivory-room-window-profile",
        "warm window profile portrait",
        "editorial, precise, serene",
        ("laser", "results", "journal", "decorative"),
        "48% 30%",
        "Let the side gaze breathe; use as support imagery rather than contact portrait.",
        "Serene editorial side portrait of Franciele Sofiati beside a window",
    ),
    PhotoSpec(
        "IMG_1750.jpg.jpeg",
        "ivory-room-seated-side",
        "warm ivory-room seated portrait",
        "elegant, intimate, premium",
        ("hero", "about", "consultation", "contact", "CTA", "footer"),
        "50% 31%",
        "Use as a vertical hero or consultation panel; keep face and shoulder line intact.",
        "Elegant seated portrait of Franciele Sofiati in an ivory professional setting",
    ),
)


CATEGORY_SOURCE = {
    "hero": "portrait-4x5",
    "about": "portrait-4x5",
    "profile": "square",
    "consultation": "portrait-4x5",
    "contact": "square",
    "journal": "card-5x4",
    "decorative": "card-5x4",
    "service-support": "card-5x4",
    "CTA": "portrait-4x5",
    "footer": "square",
    "care": "card-5x4",
    "skin": "card-5x4",
    "laser": "card-5x4",
    "results": "card-5x4",
}


CATEGORY_DIR = {
    "CTA": "cta",
    "service-support": "service-support",
}


CROP_SPECS = {
    "hero-wide": (1600, 1000),
    "portrait-4x5": (1200, 1500),
    "square": (900, 900),
    "journal-3x2": (1200, 800),
    "card-5x4": (1100, 880),
}


def run_magick(args: list[str]) -> None:
    subprocess.run(["magick", *args], check=True)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def image_orientation(path: Path) -> str:
    with Image.open(path) as image:
        normalized = ImageOps.exif_transpose(image)
        width, height = normalized.size
    if width == height:
        return "square"
    return "landscape" if width > height else "portrait"


def webp_copy(source: Path, destination: Path, max_size: int = 1800) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    run_magick(
        [
            str(source),
            "-auto-orient",
            "-resize",
            f"{max_size}x{max_size}>",
            "-quality",
            "84",
            "-define",
            "webp:method=6",
            "-strip",
            str(destination),
        ]
    )


def crop_webp(source: Path, destination: Path, size: tuple[int, int], gravity: str) -> None:
    width, height = size
    destination.parent.mkdir(parents=True, exist_ok=True)
    run_magick(
        [
            str(source),
            "-auto-orient",
            "-resize",
            f"{width}x{height}^",
            "-gravity",
            gravity,
            "-extent",
            f"{width}x{height}",
            "-quality",
            "84",
            "-define",
            "webp:method=6",
            "-strip",
            str(destination),
        ]
    )


def main() -> None:
    required_dirs = [
        "original",
        "optimized",
        "crops",
        "transparent",
        "hero",
        "profile",
        "consultation",
        "contact",
        "journal",
        "decorative",
        "about",
        "service-support",
        "cta",
        "footer",
        "care",
        "skin",
        "laser",
        "results",
    ]
    for directory in required_dirs:
        (OUT_DIR / directory).mkdir(parents=True, exist_ok=True)

    entries: list[dict[str, object]] = []
    category_pools: dict[str, list[str]] = {category: [] for category in CATEGORY_SOURCE}

    for index, spec in enumerate(PHOTOS, 1):
        source = SOURCE_DIR / spec.source
        if not source.exists():
            raise FileNotFoundError(source)

        image_id = f"franciele-sofiati-{index:02d}-{spec.slug}"
        original_copy = OUT_DIR / "original" / spec.source
        shutil.copy2(source, original_copy)

        optimized = OUT_DIR / "optimized" / f"{image_id}.webp"
        webp_copy(source, optimized)

        crop_files: dict[str, str] = {}
        crop_paths: dict[str, Path] = {}
        for crop_name, size in CROP_SPECS.items():
            crop_path = OUT_DIR / "crops" / f"{image_id}-{crop_name}.webp"
            crop_webp(source, crop_path, size, spec.gravity)
            crop_files[crop_name] = rel(crop_path)
            crop_paths[crop_name] = crop_path

        category_files: dict[str, str] = {}
        for category in spec.use_cases:
            crop_name = CATEGORY_SOURCE[category]
            category_dir = CATEGORY_DIR.get(category, category)
            destination = OUT_DIR / category_dir / f"{image_id}-{category_dir}.webp"
            shutil.copy2(crop_paths[crop_name], destination)
            category_files[category] = rel(destination)
            category_pools[category].append(rel(destination))

        entries.append(
            {
                "id": image_id,
                "source_original": rel(source),
                "preserved_original": rel(original_copy),
                "optimized_file": rel(optimized),
                "crop_files": crop_files,
                "category_files": category_files,
                "transparent_file": None,
                "orientation": image_orientation(source),
                "scene": spec.scene,
                "recommended_use": list(spec.use_cases),
                "alt_text": spec.alt,
                "object_position": spec.object_position,
                "mobile_crop_notes": spec.mobile_notes,
                "mood_style_notes": spec.mood,
                "repetition_notes": "Rotate with other entries from the same use-case pool; avoid using this same portrait in both hero and contact card on the same page.",
            }
        )

    transparent_readme = OUT_DIR / "transparent" / "README.md"
    transparent_readme.write_text(
        "# Transparent Cutouts\n\n"
        "Transparent Franciele cutouts are pending. Reliable local background-removal tooling "
        "(`rembg`, `transparent_background`, or an equivalent audited workflow) was not available "
        "during the 2026-06-27 refactor, so the sites use optimized original-background photos and "
        "premium crops instead of blocking the rebuild.\n",
        encoding="utf-8",
    )

    manifest = {
        "generated_at": date.today().isoformat(),
        "source_directory": "assets/photos",
        "asset_root": "assets/brand-photos",
        "transparent_cutouts": {
            "status": "pending",
            "folder": "assets/brand-photos/transparent",
            "reason": "No reliable local background-removal tool was available; transparent versions should be created later with reviewed edges before production use.",
        },
        "usage_categories": [
            "hero",
            "about",
            "profile",
            "consultation",
            "contact",
            "journal",
            "decorative",
            "service-support",
            "CTA",
            "footer",
        ],
        "usage_pools": category_pools,
        "entries": entries,
    }
    (OUT_DIR / "image-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "sources": len(PHOTOS),
                "optimized": len(PHOTOS),
                "crops": len(PHOTOS) * len(CROP_SPECS),
                "category_files": sum(len(entry["category_files"]) for entry in entries),
                "manifest": rel(OUT_DIR / "image-manifest.json"),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
