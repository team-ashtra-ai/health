#!/usr/bin/env python3
"""Build contact sheet images from final Sofiati full-page screenshots."""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path
from typing import Iterable

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
OUTPUT_ROOT = ROOT / "final" / "screenshots"
SOURCE_DIR = OUTPUT_ROOT / "full-pages"
SHEETS_DIR = OUTPUT_ROOT / "full-page-contact-sheets"


def concept_dirs() -> list[Path]:
    return sorted(
        [path for path in CONCEPTS_DIR.iterdir() if path.is_dir() and path.name[:2].isdigit()],
        key=lambda path: path.name,
    )


def page_stems(concept: Path) -> list[str]:
    return [path.stem for path in sorted(concept.glob("*.html")) if ".bak" not in path.name]


def resize_to_width(image: Image.Image, width: int) -> Image.Image:
    ratio = width / image.width
    height = max(1, int(image.height * ratio))
    return image.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)


def draw_label(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, font: ImageFont.ImageFont) -> None:
    x, y = xy
    draw.rectangle((x, y, x + 230, y + 26), fill=(34, 32, 28))
    draw.text((x + 8, y + 7), text, fill=(255, 255, 255), font=font)


def build_concept_sheet(concept: Path, viewport: str, thumb_width: int, columns: int) -> tuple[Path | None, list[str]]:
    font = ImageFont.load_default()
    missing: list[str] = []
    tiles: list[tuple[str, Image.Image]] = []

    for stem in page_stems(concept):
        image_path = SOURCE_DIR / viewport / concept.name / f"{stem}.jpg"
        if not image_path.exists():
            missing.append(f"{concept.name}/{stem}.html")
            continue
        with Image.open(image_path) as image:
            tiles.append((stem, resize_to_width(image, thumb_width)))

    if not tiles:
        return None, missing

    gap = 18
    pad = 28
    label_h = 26
    title_h = 48
    rows = [tiles[index : index + columns] for index in range(0, len(tiles), columns)]
    row_heights = [max(tile.height for _, tile in row) + label_h for row in rows]
    canvas_w = pad * 2 + columns * thumb_width + (columns - 1) * gap
    canvas_h = pad * 2 + title_h + sum(row_heights) + gap * (len(rows) - 1)

    canvas = Image.new("RGB", (canvas_w, canvas_h), (245, 242, 236))
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((pad, pad, canvas_w - pad, pad + title_h), fill=(255, 253, 248))
    draw.text((pad + 14, pad + 17), f"{concept.name} - {viewport} full-page contact sheet", fill=(34, 32, 28), font=font)

    y = pad + title_h
    for row, row_h in zip(rows, row_heights):
        x = pad
        for name, tile in row:
            draw_label(draw, (x, y), name, font)
            canvas.paste(tile, (x, y + label_h))
            x += thumb_width + gap
        y += row_h + gap

    out_dir = SHEETS_DIR / viewport
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{concept.name}-{viewport}-full-pages.jpg"
    canvas.save(out_path, quality=82, optimize=True)
    return out_path, missing


def write_index(outputs: Iterable[Path], missing: list[str]) -> None:
    outputs = sorted(outputs)
    css = """
body { margin: 0; background: #f5f2ec; color: #24221f; font-family: Inter, system-ui, sans-serif; }
header { position: sticky; top: 0; z-index: 2; background: rgba(245,242,236,.95); border-bottom: 1px solid rgba(36,34,31,.14); padding: 18px 24px; }
h1 { margin: 0 0 8px; font-size: 24px; }
h2 { margin: 32px 0 12px; font-size: 17px; }
main { width: min(1500px, calc(100% - 32px)); margin: 0 auto 56px; }
.summary { display: flex; flex-wrap: wrap; gap: 8px; }
.summary span { padding: 6px 10px; border: 1px solid rgba(36,34,31,.16); border-radius: 999px; background: rgba(255,255,255,.58); font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 14px; align-items: start; }
figure { margin: 0; padding: 8px; background: #fffdf8; border: 1px solid rgba(36,34,31,.14); border-radius: 8px; }
img { display: block; width: 100%; height: auto; border-radius: 4px; }
figcaption { padding-top: 7px; font-size: 12px; color: rgba(36,34,31,.72); word-break: break-word; }
.fail { color: #8c2f22; }
""".strip()
    groups: dict[str, list[Path]] = {"desktop": [], "mobile": []}
    for path in outputs:
        groups.setdefault(path.parent.name, []).append(path)

    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1" />',
        "<title>Sofiati Full-Page Contact Sheets</title>",
        f"<style>{css}</style>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>Sofiati Full-Page Contact Sheets</h1>",
        '<div class="summary">',
        f"<span>{len(outputs)} sheet images</span>",
        f"<span>{len(missing)} missing source screenshots</span>",
        "</div>",
        "</header>",
        "<main>",
    ]
    for viewport, paths in groups.items():
        if not paths:
            continue
        lines.append(f"<h2>{viewport}</h2>")
        lines.append('<div class="grid">')
        for path in paths:
            rel = path.relative_to(SHEETS_DIR)
            lines.append("<figure>")
            lines.append(f'<a href="{rel}"><img src="{rel}" loading="lazy" alt="{path.stem}" /></a>')
            lines.append(f"<figcaption>{path.name}</figcaption>")
            lines.append("</figure>")
        lines.append("</div>")
    if missing:
        lines.append('<h2 class="fail">Missing source screenshots</h2>')
        lines.append("<ul>")
        for item in missing[:300]:
            lines.append(f"<li>{item}</li>")
        if len(missing) > 300:
            lines.append(f"<li>... {len(missing) - 300} more</li>")
        lines.append("</ul>")
    lines.extend(["</main>", "</body>", "</html>"])
    SHEETS_DIR.mkdir(parents=True, exist_ok=True)
    (SHEETS_DIR / "index.html").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Sofiati full-page contact sheets.")
    parser.add_argument("--clean-source", action="store_true", help="Remove individual screenshot source folders after sheets are built.")
    args = parser.parse_args()

    outputs: list[Path] = []
    missing: list[str] = []
    for viewport, thumb_width, columns in [("desktop", 220, 3), ("mobile", 160, 4)]:
        for concept in concept_dirs():
            out_path, concept_missing = build_concept_sheet(concept, viewport, thumb_width, columns)
            if out_path:
                outputs.append(out_path)
            missing.extend(f"{viewport}/{item}" for item in concept_missing)

    write_index(outputs, missing)
    (SHEETS_DIR / "manifest.json").write_text(
        json.dumps(
            {
                "sheets": [str(path.relative_to(OUTPUT_ROOT)) for path in outputs],
                "missing": missing,
                "sheet_count": len(outputs),
                "missing_count": len(missing),
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    if args.clean_source and SOURCE_DIR.exists() and not missing:
        shutil.rmtree(SOURCE_DIR)

    print(f"Built {len(outputs)} contact sheets in {SHEETS_DIR}")
    print(f"Missing source screenshots: {len(missing)}")
    return 1 if missing else 0


if __name__ == "__main__":
    raise SystemExit(main())
