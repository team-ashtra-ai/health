#!/usr/bin/env python3
"""Capture visual QA screenshots and build review contact sheets.

This script favors reliability over speed: it invokes Chrome separately for each
capture so one heavy page cannot take down the whole batch.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
OUTPUT_DIR = ROOT / "audit" / "screenshots" / "design-qa"
PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
VIEWPORTS = {
    "desktop": (1440, 1100),
    "mobile": (390, 844),
}
PAGES = ["index.html", "care.html", "laser.html", "skin.html", "results.html"]


def concept_dirs() -> list[Path]:
    return sorted(path for path in CONCEPTS_DIR.iterdir() if path.is_dir() and path.name[:2].isdigit())


def server_ready() -> bool:
    try:
        urllib.request.urlopen(BASE_URL, timeout=1).read(64)
        return True
    except (urllib.error.URLError, TimeoutError):
        return False


def ensure_server() -> subprocess.Popen[bytes] | None:
    if server_ready():
        return None
    process = subprocess.Popen(
        ["python3", "-m", "http.server", str(PORT)],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    for _ in range(60):
        if server_ready():
            return process
        time.sleep(0.2)
    process.terminate()
    raise RuntimeError("Local server did not start")


def chrome_binary() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found
    raise RuntimeError("Chrome or Chromium is required for screenshot QA")


def capture(chrome: str, concept: Path, page: str, viewport: str, width: int, height: int) -> Path:
    out_dir = OUTPUT_DIR / viewport / page.replace(".html", "")
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{concept.name}-{viewport}-{page.replace('.html', '')}.png"
    url = f"{BASE_URL}/concepts/{concept.name}/{page}"
    command = [
        chrome,
        "--headless=new",
        "--disable-gpu",
        "--disable-dev-shm-usage",
        "--no-sandbox",
        "--hide-scrollbars",
        "--disable-background-networking",
        f"--window-size={width},{height}",
        f"--screenshot={output}",
        url,
    ]
    subprocess.run(command, cwd=ROOT, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=60)
    return output


def make_contact_sheets(captures: list[dict[str, str]]) -> list[str]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return []

    sheets: list[str] = []
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 12)
    except Exception:
        font = None
    for viewport in VIEWPORTS:
        for page in PAGES:
            entries = [item for item in captures if item["viewport"] == viewport and item["page"] == page]
            if not entries:
                continue
            thumb_w = 260 if viewport == "desktop" else 150
            thumb_h = 210 if viewport == "desktop" else 300
            label_h = 30
            cols = 5 if viewport == "desktop" else 10
            rows = (len(entries) + cols - 1) // cols
            sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "#F3EFE5")
            draw = ImageDraw.Draw(sheet)
            for index, entry in enumerate(entries):
                src = ROOT / entry["file"]
                with Image.open(src) as image:
                    image = image.convert("RGB")
                    image.thumbnail((thumb_w, thumb_h))
                    x = (index % cols) * thumb_w
                    y = (index // cols) * (thumb_h + label_h)
                    bg = Image.new("RGB", (thumb_w, thumb_h), "#F8F7F2")
                    bg.paste(image, ((thumb_w - image.width) // 2, 0))
                    sheet.paste(bg, (x, y))
                    draw.text((x + 8, y + thumb_h + 8), entry["concept"], fill="#252321", font=font)
            output = OUTPUT_DIR / f"{viewport}-{page.replace('.html', '')}-contact-sheet.jpg"
            sheet.save(output, quality=88)
            sheets.append(output.relative_to(ROOT).as_posix())
    return sheets


def write_manifest(captures: list[dict[str, str]], sheets: list[str]) -> None:
    manifest = {
        "baseUrl": BASE_URL,
        "viewports": VIEWPORTS,
        "pages": PAGES,
        "count": len(captures),
        "captures": captures,
        "contactSheets": sheets,
    }
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def main() -> None:
    server = ensure_server()
    chrome = chrome_binary()
    captures: list[dict[str, str]] = []
    try:
        if OUTPUT_DIR.exists():
            shutil.rmtree(OUTPUT_DIR)
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        concepts = concept_dirs()
        total = len(concepts) * len(PAGES) * len(VIEWPORTS)
        done = 0
        for concept in concepts:
            for page in PAGES:
                if not (concept / page).exists():
                    continue
                for viewport, (width, height) in VIEWPORTS.items():
                    output = capture(chrome, concept, page, viewport, width, height)
                    done += 1
                    rel = output.relative_to(ROOT).as_posix()
                    captures.append({"concept": concept.name, "page": page, "viewport": viewport, "file": rel})
                    print(f"[{done:03d}/{total:03d}] {rel}")
        sheets = make_contact_sheets(captures)
        write_manifest(captures, sheets)
    finally:
        if server:
            server.terminate()


if __name__ == "__main__":
    main()
