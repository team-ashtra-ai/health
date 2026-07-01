#!/usr/bin/env python3
"""Capture final Sofiati screenshots for all concept pages."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
import socket
import subprocess
import threading
import time
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
OUTPUT_ROOT = ROOT / "final" / "screenshots"
FULL_PAGES_DIR = OUTPUT_ROOT / "full-pages"
COMPONENTS_DIR = OUTPUT_ROOT / "header-footer-hero-widgets-cookies"

DEFAULT_VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1100},
    "mobile": {"width": 390, "height": 1100},
}


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return


def free_port(start: int = 8300) -> int:
    for port in range(start, start + 160):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free local port found")


def start_server(port: int) -> ThreadingHTTPServer:
    handler = partial(QuietHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.5)
    return server


def concept_dirs() -> list[Path]:
    return sorted(
        [path for path in CONCEPTS_DIR.iterdir() if path.is_dir() and path.name[:2].isdigit()],
        key=lambda path: path.name,
    )


def page_paths() -> list[Path]:
    pages: list[Path] = []
    for concept in concept_dirs():
        pages.extend(sorted(path for path in concept.glob("*.html") if ".bak" not in path.name))
    return pages


def check_playwright() -> None:
    if shutil.which("node") is None:
        raise SystemExit("Node.js is required for Playwright screenshot capture.")
    check = subprocess.run(
        ["node", "-e", "require('playwright'); console.log('ok')"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if check.returncode != 0:
        print(check.stderr)
        raise SystemExit("Node Playwright is not available in this repo.")


def run_capture(
    *,
    port: int,
    pages: list[str],
    output_dir: Path,
    quality: int,
    concurrency: int,
    viewports: dict[str, dict[str, int]],
) -> None:
    payload = {
        "port": port,
        "pages": pages,
        "outputDir": str(output_dir),
        "quality": quality,
        "viewports": viewports,
        "concurrency": concurrency,
    }
    node_script = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const payload = JSON.parse(process.env.SOFIATI_FINAL_SCREENSHOT_PAYLOAD);

function safeName(value) {
  return value.replace(/[^a-zA-Z0-9._-]/g, '_');
}

function screenshotPath(rel, viewportName) {
  const parts = rel.split('/');
  const concept = safeName(parts[1] || 'root');
  const page = safeName((parts[2] || 'index.html').replace(/\.html$/, ''));
  const dir = path.join(payload.outputDir, 'full-pages', viewportName, concept);
  fs.mkdirSync(dir, { recursive: true });
  return path.join(dir, `${page}.jpg`);
}

function pathExists(filePath) {
  try {
    return fs.statSync(filePath).size > 0;
  } catch (_error) {
    return false;
  }
}

async function waitForPartials(page) {
  await page.waitForFunction(() => {
    const names = ['header', 'mobile-menu', 'footer', 'cookie-banner', 'floating-widgets'];
    return names.every((name) => document.querySelector(`[data-sofiati-partial="${name}"]`)?.dataset.partialLoaded === 'true');
  }, null, { timeout: 14000 });
  await page.waitForLoadState('networkidle', { timeout: 6000 }).catch(() => {});
  await page.evaluate(() => document.fonts?.ready).catch(() => {});
  await page.waitForFunction(() => {
    const visibleImages = [...document.images].filter((img) => {
      const rect = img.getBoundingClientRect();
      const style = getComputedStyle(img);
      return rect.width > 4 && rect.height > 4 && style.display !== 'none' && style.visibility !== 'hidden';
    });
    return visibleImages.every((img) => img.complete && img.naturalWidth > 0);
  }, null, { timeout: 9000 }).catch(() => {});
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const records = [];
  const viewportEntries = Object.entries(payload.viewports);
  const total = payload.pages.length * viewportEntries.length;
  let done = 0;

  for (const [viewportName, viewport] of viewportEntries) {
    const context = await browser.newContext({
      viewport,
      deviceScaleFactor: 1,
    });
    let index = 0;

    async function worker() {
      const page = await context.newPage();
      while (index < payload.pages.length) {
        const rel = payload.pages[index++];
      const url = `http://127.0.0.1:${payload.port}/${rel}`;
      const filePath = screenshotPath(rel, viewportName);
      const record = {
        page: rel,
        viewport: viewportName,
        width: viewport.width,
        height: viewport.height,
        screenshot: path.relative(payload.outputDir, filePath),
        failures: [],
      };

      try {
        if (pathExists(filePath)) {
          record.skipped = true;
        } else {
          await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 24000 });
          await waitForPartials(page);
          await page.evaluate(() => window.scrollTo(0, 0));
          await page.waitForTimeout(120);
          await page.screenshot({
            path: filePath,
            type: 'jpeg',
            quality: payload.quality,
            fullPage: true,
            animations: 'disabled',
            scale: 'css',
          });
        }
      } catch (error) {
        record.failures.push(String(error.message || error));
      }

      records.push(record);
      done += 1;
      if (done === 1 || done % 50 === 0 || done === total) {
        process.stderr.write(`full-page screenshots ${done}/${total}\n`);
      }
    }
      await page.close();
    }

    const workerCount = Math.max(1, Math.min(payload.concurrency || 1, payload.pages.length));
    await Promise.all(Array.from({ length: workerCount }, () => worker()));
    await context.close();
  }

  await browser.close();
  fs.writeFileSync(path.join(payload.outputDir, 'full-pages-manifest.json'), JSON.stringify(records, null, 2));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""
    completed = subprocess.run(
        ["node", "-e", node_script],
        cwd=ROOT,
        env={**os.environ, "SOFIATI_FINAL_SCREENSHOT_PAYLOAD": json.dumps(payload)},
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def write_index(output_dir: Path, pages: list[str]) -> None:
    manifest_path = output_dir / "full-pages-manifest.json"
    records = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = [record for record in records if record.get("failures")]
    grouped: dict[str, dict[str, list[dict[str, Any]]]] = {}
    for record in records:
        viewport = record["viewport"]
        concept = record["page"].split("/")[1]
        grouped.setdefault(viewport, {}).setdefault(concept, []).append(record)

    css = """
body { margin: 0; background: #f5f2ec; color: #24221f; font-family: Inter, system-ui, sans-serif; }
header { position: sticky; top: 0; z-index: 2; padding: 18px 24px; background: rgba(245,242,236,.95); border-bottom: 1px solid rgba(36,34,31,.14); }
h1 { margin: 0 0 8px; font-size: 24px; }
h2 { margin: 30px 0 12px; font-size: 18px; }
a { color: #285948; }
main { width: min(1500px, calc(100% - 32px)); margin: 0 auto 56px; }
nav, .summary { display: flex; flex-wrap: wrap; gap: 8px; }
nav a, .summary span { padding: 6px 10px; border: 1px solid rgba(36,34,31,.16); border-radius: 999px; background: rgba(255,255,255,.58); font-size: 13px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 14px; }
figure { margin: 0; padding: 8px; background: #fffdf8; border: 1px solid rgba(36,34,31,.14); border-radius: 8px; }
img { display: block; width: 100%; height: auto; border-radius: 4px; background: #eee8de; }
figcaption { padding-top: 7px; font-size: 12px; color: rgba(36,34,31,.72); word-break: break-word; }
.fail { color: #8c2f22; font-weight: 700; }
""".strip()

    lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1" />',
        "<title>Sofiati Final Full-Page Screenshots</title>",
        f"<style>{css}</style>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>Sofiati Final Full-Page Screenshots</h1>",
        '<div class="summary">',
        f"<span>{len(pages)} pages</span>",
        f"<span>{len(records)} screenshots</span>",
        f"<span>{len(failures)} failures</span>",
        "</div>",
        "<nav>",
    ]
    for viewport in grouped:
        lines.append(f'<a href="#{viewport}">{viewport}</a>')
    lines.extend(["</nav>", "</header>", "<main>"])

    for viewport, concepts in grouped.items():
        lines.append(f'<section id="{viewport}">')
        lines.append(f"<h2>{viewport}</h2>")
        for concept, rows in concepts.items():
            lines.append(f"<h2>{concept}</h2>")
            lines.append('<div class="grid">')
            for record in rows:
                page_name = Path(record["page"]).name
                rel = record["screenshot"]
                status = "FAIL" if record.get("failures") else ""
                lines.append("<figure>")
                lines.append(f'<a href="{rel}"><img src="{rel}" loading="lazy" alt="{record["page"]} {viewport}" /></a>')
                lines.append(f"<figcaption>{page_name} {status}</figcaption>")
                if record.get("failures"):
                    lines.append(f'<figcaption class="fail">{"; ".join(record["failures"])}</figcaption>')
                lines.append("</figure>")
            lines.append("</div>")
        lines.append("</section>")

    lines.extend(["</main>", "</body>", "</html>"])
    (output_dir / "index.html").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture final full-page screenshots for all Sofiati pages.")
    parser.add_argument("--limit", type=int, default=0, help="Limit pages for a smoke run.")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--quality", type=int, default=70)
    parser.add_argument("--concurrency", type=int, default=4)
    parser.add_argument(
        "--viewports",
        default="desktop,mobile",
        help="Comma-separated viewport names: desktop,mobile",
    )
    args = parser.parse_args()

    check_playwright()
    pages = [str(path.relative_to(ROOT)) for path in page_paths()]
    if args.limit:
        pages = pages[: args.limit]

    requested_viewports = {
        name.strip(): DEFAULT_VIEWPORTS[name.strip()]
        for name in args.viewports.split(",")
        if name.strip() in DEFAULT_VIEWPORTS
    }
    if not requested_viewports:
        raise SystemExit("No valid viewports requested. Use desktop, mobile, or desktop,mobile.")

    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    FULL_PAGES_DIR.mkdir(parents=True, exist_ok=True)
    COMPONENTS_DIR.mkdir(parents=True, exist_ok=True)

    port = args.port or free_port()
    server = start_server(port)
    try:
        run_capture(
            port=port,
            pages=pages,
            output_dir=OUTPUT_ROOT,
            quality=args.quality,
            concurrency=args.concurrency,
            viewports=requested_viewports,
        )
    finally:
        server.shutdown()
        server.server_close()

    write_index(OUTPUT_ROOT, pages)

    report = {
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "output": str(OUTPUT_ROOT.relative_to(ROOT)),
        "full_pages": str(FULL_PAGES_DIR.relative_to(ROOT)),
        "component_shots": str(COMPONENTS_DIR.relative_to(ROOT)),
        "pages": len(pages),
        "viewports": requested_viewports,
    }
    (OUTPUT_ROOT / "capture-summary.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"Captured {len(pages) * len(requested_viewports)} full-page screenshots in {FULL_PAGES_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
