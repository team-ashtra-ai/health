#!/usr/bin/env python3
"""
Capture Sofiati concept partials into one composite image per concept.

What it captures:
- top EN/PT identity banner, if present
- header / navigation
- hero
- cookie banner / preferences
- floating widgets / utility widgets
- footer

It creates one combined PNG per concept so you can quickly audit whether
the header, hero, footer and widgets are visually distinct.

Usage:
  /usr/bin/python3 scripts/capture_header_hero_footer_widgets.py
  /usr/bin/python3 scripts/capture_header_hero_footer_widgets.py --mode both
  /usr/bin/python3 scripts/capture_header_hero_footer_widgets.py --mode all
  /usr/bin/python3 scripts/capture_header_hero_footer_widgets.py --port 8001
  /usr/bin/python3 scripts/capture_header_hero_footer_widgets.py --concepts 01-inspire,02-empower
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Missing dependency: Pillow")
    print("Install it with:")
    print("  /usr/bin/python3 -m pip install pillow")
    raise SystemExit(1)


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"


BANNER_SELECTORS = [
    ".sf-identity-banner",
    ".language-banner",
    ".top-language-banner",
    ".identity-language-banner",
    ".micro-language-banner",
    ".lang-banner",
    ".locale-banner",
    "[data-partial='language-banner']",
    "[data-component='language-banner']",
    "[data-language-banner]",
]

HEADER_SELECTORS = [
    ".sf-public-header",
    "header",
    ".site-header",
    ".main-header",
    ".concept-header",
    "[data-partial='header']",
    "[data-component='header']",
    "#site-header",
]

HERO_SELECTORS = [
    ".hero",
    ".site-hero",
    ".page-hero",
    ".home-hero",
    "[data-section='hero']",
    "#hero",
    "main section:first-of-type",
]

FOOTER_SELECTORS = [
    ".sf-public-footer",
    "footer",
    ".site-footer",
    ".main-footer",
    ".concept-footer",
    "[data-partial='footer']",
    "[data-component='footer']",
    "#site-footer",
]

WIDGET_SELECTORS = [
    ".sf-floating-tools",
]

COOKIE_SELECTORS = [
    ".sf-cookie-banner",
    "[data-cookie-banner]",
]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return


def check_node_playwright() -> None:
    if shutil.which("node") is None:
        print("Node.js was not found. This script needs Node because the repo already uses Playwright through Node.")
        raise SystemExit(1)

    check = subprocess.run(
        ["node", "-e", "require('playwright'); console.log('ok')"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    if check.returncode != 0:
        print("Node Playwright is not available.")
        print("Install it in the repo with something like:")
        print("  npm install playwright")
        print("  npx playwright install chromium")
        print()
        print(check.stderr)
        raise SystemExit(1)


def start_server(port: int) -> ThreadingHTTPServer:
    handler = partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    return server


def discover_concepts() -> list[str]:
    if not CONCEPTS_DIR.exists():
        print(f"Concepts folder not found: {CONCEPTS_DIR}")
        raise SystemExit(1)

    concepts = []
    for folder in sorted(CONCEPTS_DIR.iterdir()):
        if folder.is_dir() and (folder / "index.html").exists():
            concepts.append(folder.name)

    if not concepts:
        print(f"No concept index.html files found in: {CONCEPTS_DIR}")
        raise SystemExit(1)

    return concepts


def run_node_capture(
    *,
    port: int,
    concepts: list[str],
    mode: str,
    temp_dir: Path,
    headed: bool,
    wait_ms: int,
) -> None:
    node_payload = {
        "port": port,
        "concepts": concepts,
        "mode": mode,
        "tempDir": str(temp_dir),
        "headed": headed,
        "waitMs": wait_ms,
        "selectors": {
            "banner": BANNER_SELECTORS,
            "header": HEADER_SELECTORS,
            "hero": HERO_SELECTORS,
            "footer": FOOTER_SELECTORS,
            "widgets": WIDGET_SELECTORS,
            "cookie": COOKIE_SELECTORS,
        },
    }

    node_script = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const payload = JSON.parse(process.env.SOFIATI_CAPTURE_PAYLOAD);

const desktopViewport = { width: 1440, height: 1800 };
const tabletViewport = { width: 768, height: 1300 };
const mobileViewport = { width: 390, height: 1200 };

function buildUrl(conceptId) {
  return `http://127.0.0.1:${payload.port}/concepts/${encodeURIComponent(conceptId)}/index.html`;
}

function safeName(value) {
  return value.replace(/[^a-zA-Z0-9._-]/g, "_");
}

async function getPageBoxes(page) {
  return await page.evaluate((selectors) => {
    function visible(el) {
      const rect = el.getBoundingClientRect();
      const style = window.getComputedStyle(el);
      return (
        rect.width > 4 &&
        rect.height > 4 &&
        style.display !== "none" &&
        style.visibility !== "hidden" &&
        Number(style.opacity || 1) > 0.01
      );
    }

    function boxFor(el, selector) {
      const rect = el.getBoundingClientRect();
      return {
        selector,
        x: Math.max(0, rect.left + window.scrollX),
        y: Math.max(0, rect.top + window.scrollY),
        width: rect.width,
        height: rect.height,
      };
    }

    function firstBox(list) {
      for (const selector of list) {
        const els = Array.from(document.querySelectorAll(selector));
        for (const el of els) {
          if (visible(el)) return boxFor(el, selector);
        }
      }
      return null;
    }

    function allBoxes(list) {
      const seen = new Set();
      const boxes = [];

      for (const selector of list) {
        const els = Array.from(document.querySelectorAll(selector));
        for (const el of els) {
          if (!visible(el)) continue;

          const rect = el.getBoundingClientRect();
          const key = [
            Math.round(rect.left),
            Math.round(rect.top),
            Math.round(rect.width),
            Math.round(rect.height),
          ].join(":");

          if (seen.has(key)) continue;
          seen.add(key);

          boxes.push(boxFor(el, selector));
        }
      }

      return boxes;
    }

    return {
      page: {
        width: Math.max(
          document.documentElement.scrollWidth,
          document.body ? document.body.scrollWidth : 0
        ),
        height: Math.max(
          document.documentElement.scrollHeight,
          document.body ? document.body.scrollHeight : 0
        ),
      },
      banner: firstBox(selectors.banner),
      header: firstBox(selectors.header),
      hero: firstBox(selectors.hero),
      cookie: firstBox(selectors.cookie),
      footer: firstBox(selectors.footer),
      widgets: allBoxes(selectors.widgets),
    };
  }, payload.selectors);
}

async function captureOne(browser, conceptId, viewportName, viewport) {
  const context = await browser.newContext({
    viewport,
    deviceScaleFactor: 1,
  });

  const page = await context.newPage();
  const url = buildUrl(conceptId);

  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForFunction(() => {
      const names = ["header", "mobile-menu", "footer", "cookie-banner", "floating-widgets"];
      return names.every((name) => document.querySelector(`[data-sofiati-partial="${name}"]`)?.dataset.partialLoaded === "true");
    }, null, { timeout: 12000 });
    await page.waitForFunction(() => {
      const logos = Array.from(document.querySelectorAll(".sf-logo-img"));
      return logos.length >= 3 && logos.every((img) => img.complete && img.naturalWidth > 0);
    }, null, { timeout: 5000 }).catch(() => {});
    await page.waitForFunction(() => {
      const firstImage = document.querySelector("main img");
      return !firstImage || (firstImage.complete && firstImage.naturalWidth > 0);
    }, null, { timeout: 7000 }).catch(() => {});
    await page.waitForTimeout(payload.waitMs);

    const prefix = `${safeName(conceptId)}-${viewportName}`;
    const fullPath = path.join(payload.tempDir, `${prefix}-full.png`);
    const metaPath = path.join(payload.tempDir, `${prefix}-meta.json`);

    await page.screenshot({
      path: fullPath,
      fullPage: true,
      animations: "disabled",
    });

    const boxes = await getPageBoxes(page);

    fs.writeFileSync(
      metaPath,
      JSON.stringify(
        {
          conceptId,
          viewportName,
          viewport,
          url,
          fullPath,
          boxes,
        },
        null,
        2
      )
    );

    console.log(`captured ${conceptId} ${viewportName}`);
  } catch (error) {
    console.error(`FAILED ${conceptId} ${viewportName}`);
    console.error(error);
    process.exitCode = 1;
  } finally {
    await context.close();
  }
}

(async () => {
  const browser = await chromium.launch({ headless: !payload.headed });

  const modes =
    payload.mode === "all"
      ? [["desktop", desktopViewport], ["tablet", tabletViewport], ["mobile", mobileViewport]]
      : payload.mode === "both"
      ? [["desktop", desktopViewport], ["mobile", mobileViewport]]
      : payload.mode === "tablet"
      ? [["tablet", tabletViewport]]
      : payload.mode === "mobile"
      ? [["mobile", mobileViewport]]
      : [["desktop", desktopViewport]];

  for (const conceptId of payload.concepts) {
    for (const [viewportName, viewport] of modes) {
      await captureOne(browser, conceptId, viewportName, viewport);
    }
  }

  await browser.close();

  if (process.exitCode) process.exit(process.exitCode);
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""

    env = os.environ.copy()
    env["SOFIATI_CAPTURE_PAYLOAD"] = json.dumps(node_payload)

    subprocess.run(["node", "-e", node_script], cwd=ROOT, env=env, check=True)


def int_box(box: dict[str, Any], img_w: int, img_h: int, pad: int = 16) -> tuple[int, int, int, int]:
    x1 = max(0, int(box["x"]) - pad)
    y1 = max(0, int(box["y"]) - pad)
    x2 = min(img_w, int(box["x"] + box["width"]) + pad)
    y2 = min(img_h, int(box["y"] + box["height"]) + pad)
    return x1, y1, max(x1 + 1, x2), max(y1 + 1, y2)


def crop_region(
    img: Image.Image,
    box: dict[str, Any] | None,
    *,
    label: str,
    max_height: int | None,
    pad: int = 18,
) -> tuple[str, Image.Image] | None:
    if not box:
        return None

    crop = img.crop(int_box(box, img.width, img.height, pad=pad))

    if max_height and crop.height > max_height:
        crop = crop.crop((0, 0, crop.width, max_height))

    return label, crop


def crop_widget_regions(
    img: Image.Image,
    widgets: list[dict[str, Any]],
    *,
    max_widgets: int = 8,
) -> tuple[str, Image.Image] | None:
    if not widgets:
        return None

    crops = []
    for widget in widgets[:max_widgets]:
        crop = img.crop(int_box(widget, img.width, img.height, pad=12))
        if crop.width < 8 or crop.height < 8:
            continue

        # Prevent absurdly large accidental captures.
        if crop.width > 600 or crop.height > 600:
            crop.thumbnail((420, 420))

        crops.append(crop)

    if not crops:
        return None

    gap = 18
    padding = 18
    row_h = max(c.height for c in crops)
    row_w = sum(c.width for c in crops) + gap * (len(crops) - 1) + padding * 2
    row_w = max(row_w, 280)

    canvas = Image.new("RGB", (row_w, row_h + padding * 2), "white")
    x = padding

    for crop in crops:
        y = padding + (row_h - crop.height) // 2
        canvas.paste(crop.convert("RGB"), (x, y))
        x += crop.width + gap

    return "WIDGETS / FLOATING ACTIONS", canvas


def fit_width(img: Image.Image, max_width: int) -> Image.Image:
    if img.width <= max_width:
        return img.convert("RGB")

    ratio = max_width / img.width
    new_size = (max_width, max(1, int(img.height * ratio)))
    return img.convert("RGB").resize(new_size, Image.Resampling.LANCZOS)


def add_label(draw: ImageDraw.ImageDraw, text: str, x: int, y: int, width: int, font: ImageFont.ImageFont) -> int:
    label_h = 38
    draw.rectangle((x, y, x + width, y + label_h), fill=(35, 35, 35))
    draw.text((x + 14, y + 11), text.upper(), fill=(255, 255, 255), font=font)
    return label_h


def build_composite(meta_path: Path, out_dir: Path, max_width: int) -> Path:
    meta = json.loads(meta_path.read_text())
    full_img = Image.open(meta["fullPath"]).convert("RGB")
    boxes = meta["boxes"]

    viewport = meta["viewportName"]
    concept = meta["conceptId"]

    max_header = 520 if viewport == "desktop" else 420 if viewport == "tablet" else 360
    max_hero = 760 if viewport == "desktop" else 680 if viewport == "tablet" else 620
    max_footer = None

    regions: list[tuple[str, Image.Image]] = []

    for item in [
        crop_region(full_img, boxes.get("banner"), label="Top EN/PT identity banner", max_height=180),
        crop_region(full_img, boxes.get("header"), label="Header / navigation", max_height=max_header),
        crop_region(full_img, boxes.get("hero"), label="Hero", max_height=max_hero),
        crop_region(full_img, boxes.get("cookie"), label="Cookie banner", max_height=260),
        crop_widget_regions(full_img, boxes.get("widgets") or []),
        crop_region(full_img, boxes.get("footer"), label="Footer", max_height=max_footer),
    ]:
        if item:
            regions.append(item)

    if not regions:
        regions.append(("Viewport fallback", full_img.crop((0, 0, min(full_img.width, 1440), min(full_img.height, 1200)))))

    font = ImageFont.load_default()
    outer_pad = 28
    gap = 30
    label_h = 38

    fitted = [(label, fit_width(img, max_width)) for label, img in regions]
    content_w = max(img.width for _, img in fitted)
    canvas_w = content_w + outer_pad * 2
    canvas_h = outer_pad

    title_h = 62
    canvas_h += title_h

    for _, img in fitted:
        canvas_h += label_h + img.height + gap

    canvas_h += outer_pad

    canvas = Image.new("RGB", (canvas_w, canvas_h), (245, 242, 235))
    draw = ImageDraw.Draw(canvas)

    y = outer_pad
    title = f"{concept} — {viewport} partial audit: banner, header, hero, cookies, widgets, footer"
    draw.rectangle((outer_pad, y, canvas_w - outer_pad, y + title_h), fill=(252, 250, 244))
    draw.text((outer_pad + 16, y + 20), title, fill=(35, 35, 35), font=font)
    y += title_h + gap

    for label, img in fitted:
        x = outer_pad + (content_w - img.width) // 2
        add_label(draw, label, x, y, img.width, font)
        y += label_h
        canvas.paste(img, (x, y))
        y += img.height + gap

    out_path = out_dir / f"{concept}-{viewport}-header-hero-footer-widgets.png"
    canvas.save(out_path, optimize=True)
    return out_path


def build_all_composites(temp_dir: Path, out_dir: Path, max_width: int) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    outputs = []

    for meta_path in sorted(temp_dir.glob("*-meta.json")):
        outputs.append(build_composite(meta_path, out_dir, max_width))

    return outputs


def write_contact_sheet(outputs: list[Path], out_dir: Path) -> Path:
    groups = {"desktop": [], "tablet": [], "mobile": []}
    for path in sorted(outputs):
        for viewport in groups:
            if f"-{viewport}-" in path.name:
                groups[viewport].append(path.name)
                break

    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '  <meta charset="utf-8" />',
        '  <meta name="viewport" content="width=device-width, initial-scale=1" />',
        "  <title>Sofiati Partial Screenshot Contact Sheet</title>",
        "  <style>",
        "    body { margin: 0; background: #f3efe5; color: #252321; font-family: Inter, system-ui, sans-serif; }",
        "    main { width: min(1600px, calc(100% - 32px)); margin: auto; padding: 32px 0 64px; }",
        "    h1 { font-family: Georgia, serif; font-weight: 400; font-size: clamp(2rem, 5vw, 5rem); margin: 0 0 24px; }",
        "    h2 { margin: 42px 0 14px; font-size: 1rem; text-transform: uppercase; letter-spacing: .12em; color: #596653; }",
        "    .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; align-items: start; }",
        "    figure { margin: 0; background: #fffdf8; border: 1px solid rgba(37,35,33,.14); border-radius: 8px; padding: 10px; }",
        "    img { display: block; width: 100%; height: auto; border-radius: 4px; }",
        "    figcaption { padding: 8px 2px 0; font-size: .76rem; color: #706b63; word-break: break-word; }",
        "  </style>",
        "</head>",
        "<body>",
        "  <main>",
        "    <h1>Sofiati partial screenshot comparison</h1>",
    ]
    for viewport, names in groups.items():
        if not names:
            continue
        lines.append(f"    <h2>{viewport} ({len(names)})</h2>")
        lines.append('    <div class="grid">')
        for name in names:
            caption = name.replace("-header-hero-footer-widgets.png", "")
            lines.append(f'      <figure><a href="{name}"><img src="{name}" loading="lazy" alt="{caption}" /></a><figcaption>{caption}</figcaption></figure>')
        lines.append("    </div>")
    lines.extend(["  </main>", "</body>", "</html>"])
    path = out_dir / "index.html"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def parse_args() -> argparse.Namespace:
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--mode", choices=["desktop", "tablet", "mobile", "both", "all"], default="desktop")
    parser.add_argument("--headed", action="store_true")
    parser.add_argument("--wait-ms", type=int, default=800)
    parser.add_argument("--max-width", type=int, default=1360)
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "final" / "homepage-screenshots" / f"header-hero-footer-widgets-{stamp}"),
    )
    parser.add_argument(
        "--concepts",
        default="",
        help="Comma-separated concept folders, for example: 01-inspire,02-empower",
    )
    parser.add_argument(
        "--no-server",
        action="store_true",
        help="Do not start an internal Python server. Use this only if you already have localhost running.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    check_node_playwright()

    if args.concepts.strip():
        concepts = [item.strip() for item in args.concepts.split(",") if item.strip()]
    else:
        concepts = discover_concepts()

    missing = [c for c in concepts if not (CONCEPTS_DIR / c / "index.html").exists()]
    if missing:
        print("These concept folders do not have index.html:")
        for item in missing:
            print(f"  - {item}")
        return 1

    server = None
    if not args.no_server:
        try:
            server = start_server(args.port)
            print(f"Started local server at http://127.0.0.1:{args.port}")
        except OSError as error:
            print(f"Could not start server on port {args.port}: {error}")
            print("Try another port, for example:")
            print("  /usr/bin/python3 scripts/capture_header_hero_footer_widgets.py --port 8001")
            return 1

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="sofiati-parts-") as temp:
        temp_dir = Path(temp)

        print(f"Capturing {len(concepts)} concept(s) in {args.mode} mode...")
        run_node_capture(
            port=args.port,
            concepts=concepts,
            mode=args.mode,
            temp_dir=temp_dir,
            headed=args.headed,
            wait_ms=args.wait_ms,
        )

        outputs = build_all_composites(temp_dir, out_dir, args.max_width)
        contact_sheet = write_contact_sheet(outputs, out_dir)

    if server:
        server.shutdown()

    print()
    print(f"Done. Created {len(outputs)} composite image(s).")
    print(f"Output folder:")
    print(f"  {out_dir}")
    print(f"Contact sheet:")
    print(f"  {contact_sheet}")

    for path in outputs[:10]:
        print(f"  - {path.name}")

    if len(outputs) > 10:
        print(f"  ... and {len(outputs) - 10} more")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
