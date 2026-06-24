#!/usr/bin/env python3
"""Capture desktop and mobile homepage screenshots for every concept."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
FINAL_DIR = ROOT / "final" / "homepage-screenshots"
PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"
VIEWPORTS = {
    "desktop": "1440,1100",
    "mobile": "390,844",
}
CONCEPTS = [
    "01-inspire", "02-empower", "03-enhance", "04-renew", "05-elevate",
    "06-refine", "07-glow", "08-balance", "09-radiance", "10-essence",
    "11-bloom", "12-vital", "13-poise", "14-aura", "15-clarity",
    "16-grace", "17-sculpt", "18-lumin", "19-verda", "20-halo",
    "21-calm", "22-precision", "23-ritual", "24-signal", "25-align",
    "26-vivant", "27-form", "28-pure", "29-solace", "30-method",
    "31-evolve", "32-serene", "33-elan", "34-flora", "35-atelier",
    "36-lumina", "37-vellum", "38-origin", "39-kindred", "40-noble",
    "41-vista", "42-softline", "43-meridian", "44-safeguard", "45-silhouette",
    "46-curate", "47-proof", "48-signature", "49-wisdom", "50-sovereign",
]


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
    for _ in range(50):
        if server_ready():
            return process
        time.sleep(0.2)
    process.terminate()
    raise RuntimeError(f"Local server did not start on port {PORT}")


def chrome_binary() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("Could not find Chrome or Chromium for screenshots")


def pages() -> list[tuple[str, str]]:
    result = [("selector-home", "/")]
    for folder in CONCEPTS:
        result.append((f"concept-{folder}-home", f"/concepts/{folder}/index.html"))
    return result


def capture(chrome: str, profile: Path, slug: str, url_path: str, viewport: str, size: str) -> Path:
    out_dir = FINAL_DIR / viewport
    out_dir.mkdir(parents=True, exist_ok=True)
    output = out_dir / f"{slug}-{viewport}.png"
    subprocess.run(
        [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
            "--hide-scrollbars",
            f"--user-data-dir={profile}",
            f"--window-size={size}",
            "--virtual-time-budget=3200",
            f"--screenshot={output}",
            f"{BASE_URL}{url_path}",
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return output


def maybe_contact_sheets(captured: list[dict[str, str]]) -> list[str]:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except Exception:
        return []

    sheets: list[str] = []
    for viewport in VIEWPORTS:
        entries = [entry for entry in captured if entry["viewport"] == viewport and entry["page"].startswith("concept-")]
        if not entries:
            continue
        thumb_w = 260 if viewport == "desktop" else 150
        thumb_h = 198 if viewport == "desktop" else 324
        label_h = 30
        cols = 5 if viewport == "desktop" else 10
        rows = (len(entries) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * thumb_w, rows * (thumb_h + label_h)), "#F3EFE5")
        draw = ImageDraw.Draw(sheet)
        try:
            font = ImageFont.truetype("DejaVuSans.ttf", 12)
        except Exception:
            font = None
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
                draw.text((x + 8, y + thumb_h + 8), entry["page"].replace("concept-", "").replace("-home", ""), fill="#252321", font=font)
        output = FINAL_DIR / f"{viewport}-contact-sheet.jpg"
        sheet.save(output, quality=88)
        sheets.append(output.relative_to(ROOT).as_posix())
    return sheets


def write_manifest(captured: list[dict[str, str]], sheets: list[str]) -> None:
    manifest = {
        "baseUrl": BASE_URL,
        "viewports": VIEWPORTS,
        "count": len(captured),
        "screenshots": captured,
        "contactSheets": sheets,
    }
    (FINAL_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    (FINAL_DIR / "README.md").write_text(
        "# Homepage Screenshots\n\n"
        "Desktop and mobile first-viewport screenshots for the selector homepage and all 50 standalone concept homepages.\n\n"
        + "\n".join(f"- `{sheet}`" for sheet in sheets)
        + ("\n" if sheets else ""),
        encoding="utf-8",
    )


def main() -> None:
    missing = [folder for folder in CONCEPTS if not (CONCEPTS_DIR / folder / "index.html").exists()]
    if missing:
        raise SystemExit("Missing concept homepages: " + ", ".join(missing))

    server = ensure_server()
    chrome = chrome_binary()
    captured: list[dict[str, str]] = []
    try:
        if FINAL_DIR.exists():
            shutil.rmtree(FINAL_DIR)
        FINAL_DIR.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="sofiati-screenshots-") as tmp:
            profile = Path(tmp) / "chrome-profile"
            all_pages = pages()
            total = len(all_pages) * len(VIEWPORTS)
            done = 0
            for slug, url_path in all_pages:
                for viewport, size in VIEWPORTS.items():
                    output = capture(chrome, profile, slug, url_path, viewport, size)
                    done += 1
                    rel = output.relative_to(ROOT).as_posix()
                    captured.append({"viewport": viewport, "page": slug, "url": url_path, "file": rel})
                    print(f"[{done:03d}/{total:03d}] {rel}")
        sheets = maybe_contact_sheets(captured)
        write_manifest(captured, sheets)
    finally:
        if server:
            server.terminate()


if __name__ == "__main__":
    main()
