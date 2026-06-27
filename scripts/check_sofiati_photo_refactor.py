#!/usr/bin/env python3
"""Static QA for the Sofiati real-photo refactor."""

from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
MANIFEST_PATH = ROOT / "assets" / "brand-photos" / "image-manifest.json"

IMAGE_EXTENSIONS = (".avif", ".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp")


def is_external(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https", "mailto", "tel", "data"}


def image_like(value: str) -> bool:
    clean = value.split("#", 1)[0].split("?", 1)[0].lower()
    return clean.endswith(IMAGE_EXTENSIONS)


def concept_base_for_html(path: Path) -> Path:
    parts = path.relative_to(CONCEPTS_DIR).parts
    return CONCEPTS_DIR / parts[0]


def resolve_html_path(path: Path, value: str) -> Path:
    base = concept_base_for_html(path) if "partials" in path.parts else path.parent
    return (base / value).resolve()


def local_exists(path: Path, value: str) -> bool:
    if value.startswith("#") or is_external(value):
        return True
    target = resolve_html_path(path, value) if path.suffix == ".html" else (path.parent / value).resolve()
    return target.exists()


def img_attrs(tag: str) -> dict[str, str]:
    return {name: value for name, value in re.findall(r'([a-zA-Z0-9:_-]+)="([^"]*)"', tag)}


def main() -> None:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    html_files = sorted(CONCEPTS_DIR.rglob("*.html"))
    css_files = sorted(CONCEPTS_DIR.rglob("*.css"))

    missing_images: list[str] = []
    alt_issues: list[str] = []
    brand_refs = 0
    old_generic_refs = 0
    direct_original_refs = 0

    for path in html_files:
        text = path.read_text(encoding="utf-8")
        old_generic_refs += len(re.findall(r"assets/(?:images|portrait)/[^\"']+\.webp", text))
        direct_original_refs += len(re.findall(r"assets/(?:photos|brand-photos/original)/[^\"']+", text))
        for match in re.finditer(r"<img\b[^>]*>", text):
            tag = match.group(0)
            attrs = img_attrs(tag)
            src = attrs.get("src", "")
            if "assets/brand-photos/" in src:
                brand_refs += 1
            if src and image_like(src) and not local_exists(path, src):
                missing_images.append(f"{path.relative_to(ROOT)} -> {src}")
            decorative = attrs.get("aria-hidden") == "true" or attrs.get("role") == "presentation"
            alt = attrs.get("alt")
            if alt is None:
                alt_issues.append(f"{path.relative_to(ROOT)} missing alt on {src}")
            elif "assets/brand-photos/" in src and not decorative and not alt.strip():
                alt_issues.append(f"{path.relative_to(ROOT)} empty meaningful brand-photo alt on {src}")

    missing_css_assets: list[str] = []
    for path in css_files:
        text = path.read_text(encoding="utf-8")
        for value in re.findall(r"url\((?:\"|')?([^\"')]+)(?:\"|')?\)", text):
            if value.startswith("#") or is_external(value):
                continue
            if not (path.parent / value).resolve().exists():
                missing_css_assets.append(f"{path.relative_to(ROOT)} -> {value}")

    concept_count = len([path for path in CONCEPTS_DIR.iterdir() if path.is_dir()])
    report = {
        "concepts": concept_count,
        "html_files_checked": len(html_files),
        "css_files_checked": len(css_files),
        "manifest_entries": len(manifest["entries"]),
        "brand_photo_html_references": brand_refs,
        "old_generic_webp_references": old_generic_refs,
        "direct_original_photo_references": direct_original_refs,
        "missing_html_images": missing_images,
        "missing_css_assets": missing_css_assets,
        "brand_photo_alt_issues": alt_issues,
        "transparent_status": manifest["transparent_cutouts"]["status"],
    }
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
