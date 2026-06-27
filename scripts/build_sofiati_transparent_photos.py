#!/usr/bin/env python3
"""Create verified transparent Franciele cutouts from assets/photos."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from PIL import Image, ImageOps
from rembg import new_session, remove


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "assets" / "brand-photos" / "image-manifest.json"
TRANSPARENT_DIR = ROOT / "assets" / "brand-photos" / "transparent"
MAX_LONG_EDGE = 1900


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def load_source(path: Path) -> Image.Image:
    image = Image.open(path)
    image = ImageOps.exif_transpose(image).convert("RGB")
    width, height = image.size
    scale = min(1.0, MAX_LONG_EDGE / max(width, height))
    if scale < 1:
        image = image.resize((round(width * scale), round(height * scale)), Image.Resampling.LANCZOS)
    return image


def verify_alpha(path: Path) -> dict[str, object]:
    image = Image.open(path).convert("RGBA")
    alpha = image.getchannel("A")
    extrema = alpha.getextrema()
    bbox = alpha.getbbox()
    transparent_pixels = sum(1 for value in alpha.getdata() if value < 8)
    opaque_pixels = sum(1 for value in alpha.getdata() if value > 247)
    total = image.width * image.height
    return {
        "has_alpha": image.mode == "RGBA",
        "alpha_min": extrema[0],
        "alpha_max": extrema[1],
        "transparent_pixel_ratio": round(transparent_pixels / total, 4),
        "opaque_pixel_ratio": round(opaque_pixels / total, 4),
        "subject_bbox": bbox,
        "verified": extrema[0] == 0 and extrema[1] == 255 and transparent_pixels > total * 0.08 and opaque_pixels > total * 0.05 and bbox is not None,
        "width": image.width,
        "height": image.height,
    }


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    TRANSPARENT_DIR.mkdir(parents=True, exist_ok=True)
    session = new_session("u2net_human_seg")
    failures: list[dict[str, object]] = []
    processed = 0
    verified = 0

    for entry in manifest["entries"]:
        source = ROOT / entry["source_original"]
        image_id = entry["id"]
        png_path = TRANSPARENT_DIR / f"{image_id}-transparent.png"
        webp_path = TRANSPARENT_DIR / f"{image_id}-transparent.webp"
        try:
            source_image = load_source(source)
            cutout = remove(
                source_image,
                session=session,
                alpha_matting=True,
                alpha_matting_foreground_threshold=235,
                alpha_matting_background_threshold=15,
                alpha_matting_erode_size=4,
                post_process_mask=True,
            ).convert("RGBA")
            cutout.save(png_path, optimize=True)
            cutout.save(webp_path, "WEBP", lossless=True, quality=92, method=6)
            alpha_report = verify_alpha(png_path)
            processed += 1
            if alpha_report["verified"]:
                verified += 1
            else:
                failures.append(
                    {
                        "id": image_id,
                        "source": entry["source_original"],
                        "reason": "alpha verification did not meet transparent/opaque coverage thresholds",
                        "alpha_report": alpha_report,
                    }
                )
            entry["transparent_file"] = rel(png_path)
            entry["transparent_webp"] = rel(webp_path)
            entry["transparent_alpha_verified"] = bool(alpha_report["verified"])
            entry["transparent_alpha_report"] = alpha_report
            entry["transparent_method"] = "rembg u2net_human_seg with softer alpha matting on resized source"
        except Exception as error:
            failures.append({"id": image_id, "source": entry["source_original"], "reason": repr(error)})
            entry["transparent_file"] = None
            entry["transparent_webp"] = None
            entry["transparent_alpha_verified"] = False
            entry["transparent_method"] = "failed"

    manifest["transparent_cutouts"] = {
        "status": "complete" if processed == len(manifest["entries"]) and verified == processed else "partial",
        "folder": "assets/brand-photos/transparent",
        "generated_at": date.today().isoformat(),
        "method": "rembg u2net_human_seg in .continue/photo-rebuild-venv; softer alpha matting; PNG and lossless WebP alpha outputs",
        "source_photos": len(manifest["entries"]),
        "transparent_versions_created": processed,
        "transparent_versions_alpha_verified": verified,
        "failures": failures,
    }
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    report = {
        "source_photos": len(manifest["entries"]),
        "transparent_versions_created": processed,
        "transparent_versions_alpha_verified": verified,
        "failures": failures,
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
