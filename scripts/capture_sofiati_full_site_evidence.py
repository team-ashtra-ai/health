#!/usr/bin/env python3
"""Capture all Sofiati public pages at the required QA breakpoints."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import socket
import subprocess
import sys
import threading
import time
from collections import Counter, defaultdict
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

try:
    from PIL import Image, ImageStat
except ImportError:  # pragma: no cover - reported cleanly at runtime.
    Image = None
    ImageStat = None


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
OUTPUT_ROOT = ROOT / "docs" / "qa" / "full-site-visual-evidence"
SCRIPT_RUNS = ROOT / "docs" / "script-runs"
VIEWPORTS = [1440, 1280, 1024, 768, 430, 390, 360]
VIEW_HEIGHT = 980


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        return


def free_port(start: int = 8200) -> int:
    for port in range(start, start + 120):
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


def parse_viewports(value: str) -> list[int]:
    if not value:
        return VIEWPORTS
    widths = [int(part.strip()) for part in value.split(",") if part.strip()]
    unknown = [width for width in widths if width not in VIEWPORTS]
    if unknown:
        raise SystemExit(f"Unsupported viewport(s): {unknown}. Expected values from {VIEWPORTS}.")
    return widths


def run_node_capture(*, port: int, pages: list[str], widths: list[int], output_dir: Path, quality: int) -> None:
    payload = {
        "port": port,
        "pages": pages,
        "widths": widths,
        "viewHeight": VIEW_HEIGHT,
        "outputDir": str(output_dir),
        "quality": quality,
    }
    node_script = r"""
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const payload = JSON.parse(process.env.SOFIATI_EVIDENCE_PAYLOAD);

function safeName(value) {
  return value.replace(/[^a-zA-Z0-9._-]/g, '_');
}

function outPath(rel, width, kind) {
  const parts = rel.split('/');
  const concept = safeName(parts[1] || 'root');
  const page = safeName((parts[2] || 'index.html').replace(/\.html$/, ''));
  const dir = path.join(payload.outputDir, 'images', String(width), concept);
  fs.mkdirSync(dir, { recursive: true });
  return path.join(dir, `${page}-${kind}.jpg`);
}

async function waitForPartials(page) {
  await page.waitForFunction(() => {
    const names = ['header', 'mobile-menu', 'footer', 'cookie-banner', 'floating-widgets'];
    return names.every((name) => document.querySelector(`[data-sofiati-partial="${name}"]`)?.dataset.partialLoaded === 'true');
  }, null, { timeout: 12000 });
  await page.waitForLoadState('networkidle', { timeout: 5000 }).catch(() => {});
  await page.waitForFunction(() => {
    const logos = [...document.querySelectorAll('.sf-logo-img')];
    return logos.length >= 3 && logos.every((img) => img.complete && img.naturalWidth > 0);
  }, null, { timeout: 5000 }).catch(() => {});
  await page.evaluate(() => document.fonts?.ready).catch(() => {});
}

async function waitForVisibleImages(page) {
  await page.waitForFunction(() => {
    const visibleImages = [...document.images].filter((img) => {
      const rect = img.getBoundingClientRect();
      const style = getComputedStyle(img);
      return (
        rect.width > 4 &&
        rect.height > 4 &&
        rect.bottom >= 0 &&
        rect.top <= window.innerHeight &&
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        Number(style.opacity || 1) > 0.01
      );
    });
    return visibleImages.every((img) => img.complete && img.naturalWidth > 0);
  }, null, { timeout: 8000 }).catch(() => {});
}

async function captureViewport(page, filePath) {
  await page.screenshot({
    path: filePath,
    type: 'jpeg',
    quality: payload.quality,
    fullPage: false,
    scale: 'css',
  });
}

(async () => {
  const browser = await chromium.launch({ headless: true });
  const records = [];
  let count = 0;
  const total = payload.pages.length * payload.widths.length;

  for (const width of payload.widths) {
    const context = await browser.newContext({
      viewport: { width, height: payload.viewHeight },
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();

    for (const rel of payload.pages) {
      const url = `http://127.0.0.1:${payload.port}/${rel}`;
      const topPath = outPath(rel, width, 'top');
      const footerPath = outPath(rel, width, 'footer');
      const record = {
        page: rel,
        width,
        top: path.relative(payload.outputDir, topPath),
        footer: path.relative(payload.outputDir, footerPath),
        menu: null,
        failures: [],
      };

      try {
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 18000 });
        await waitForPartials(page);
        await page.evaluate(() => window.scrollTo(0, 0));
        await waitForVisibleImages(page);
        await page.waitForTimeout(40);
        await captureViewport(page, topPath);

        await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
        await waitForVisibleImages(page);
        await page.waitForTimeout(70);
        await captureViewport(page, footerPath);

        if (width <= 1024) {
          await page.evaluate(() => window.scrollTo(0, 0));
          await page.click('[data-menu-toggle]');
          await page.waitForTimeout(280);
          const menuPath = outPath(rel, width, 'menu');
          await captureViewport(page, menuPath);
          record.menu = path.relative(payload.outputDir, menuPath);
        }
      } catch (error) {
        record.failures.push(String(error.message || error));
      }

      records.push(record);
      count += 1;
      if (count === 1 || count % 100 === 0 || count === total) {
        process.stderr.write(`captured ${count}/${total}\n`);
      }
    }
    await context.close();
  }

  await browser.close();
  fs.writeFileSync(path.join(payload.outputDir, 'manifest.raw.json'), JSON.stringify(records, null, 2));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""
    completed = subprocess.run(
        ["node", "-e", node_script],
        cwd=ROOT,
        env={**os.environ, "SOFIATI_EVIDENCE_PAYLOAD": json.dumps(payload)},
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def image_stats(path: Path) -> dict[str, Any]:
    exact_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if Image is None or ImageStat is None:
        return {"hash": "", "sha256": exact_hash, "variance": None, "brightness": None, "blank_like": False}
    with Image.open(path) as image:
        gray = image.convert("L")
        stat = ImageStat.Stat(gray.resize((64, 64)))
        variance = float(stat.var[0])
        brightness = float(stat.mean[0])
        small = gray.resize((8, 8))
        if hasattr(small, "get_flattened_data"):
            values = list(small.get_flattened_data())
        else:
            values = list(small.getdata())
        mean = sum(values) / len(values)
        digest = "".join("1" if value >= mean else "0" for value in values)
    return {
        "hash": hex(int(digest, 2))[2:].zfill(16),
        "sha256": exact_hash,
        "variance": round(variance, 2),
        "brightness": round(brightness, 2),
        "blank_like": variance < 3.0,
    }


def enrich_records(output_dir: Path) -> list[dict[str, Any]]:
    records = json.loads((output_dir / "manifest.raw.json").read_text(encoding="utf-8"))
    for record in records:
        record["stats"] = {}
        for kind in ["top", "footer", "menu"]:
            rel = record.get(kind)
            if not rel:
                continue
            path = output_dir / rel
            if path.exists():
                record["stats"][kind] = image_stats(path)
            else:
                record.setdefault("failures", []).append(f"missing screenshot: {kind}")
    return records


def write_html(output_dir: Path, records: list[dict[str, Any]], widths: list[int]) -> None:
    grouped: dict[int, dict[str, list[dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        concept = record["page"].split("/")[1]
        grouped[record["width"]][concept].append(record)

    css = """
html { color-scheme: light; }
body { margin: 0; background: #f5f2ec; color: #211f1b; font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
header { position: sticky; top: 0; z-index: 5; background: rgba(245,242,236,.94); backdrop-filter: blur(14px); border-bottom: 1px solid rgba(45,43,37,.16); padding: 16px 24px; }
h1 { margin: 0 0 8px; font-size: 24px; line-height: 1.2; }
h2 { margin: 36px 0 12px; font-size: 18px; }
a { color: #245a49; }
.summary { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; font-size: 13px; }
.summary span, nav a { border: 1px solid rgba(45,43,37,.16); border-radius: 999px; padding: 6px 10px; background: rgba(255,255,255,.62); }
nav { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }
main { width: min(1480px, calc(100vw - 32px)); margin: 0 auto 48px; }
.concept { border-top: 1px solid rgba(45,43,37,.16); padding-top: 14px; }
.grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 14px; }
.card { background: #fffdf8; border: 1px solid rgba(45,43,37,.14); border-radius: 8px; overflow: hidden; box-shadow: 0 12px 28px rgba(24,22,18,.06); }
.card-title { display: flex; justify-content: space-between; gap: 12px; padding: 9px 10px; border-bottom: 1px solid rgba(45,43,37,.12); font-size: 12px; line-height: 1.35; }
.frame { display: grid; gap: 1px; background: rgba(45,43,37,.16); }
.frame img { display: block; width: 100%; height: auto; background: #eee8dc; }
.frame--menu { grid-template-columns: 1fr; }
.fail { color: #8c2f22; font-weight: 700; }
.muted { color: rgba(33,31,27,.68); }
""".strip()

    failure_count = sum(1 for record in records if record.get("failures"))
    blank_count = sum(
        1
        for record in records
        for stats in record.get("stats", {}).values()
        if stats.get("blank_like")
    )

    index_lines = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8" />',
        '<meta name="viewport" content="width=device-width, initial-scale=1" />',
        "<title>Sofiati Full Site Visual Evidence</title>",
        f"<style>{css}</style>",
        "</head>",
        "<body>",
        "<header>",
        "<h1>Sofiati Full Site Visual Evidence</h1>",
        '<p class="muted">Screenshots are unlabelled page captures; labels live only in this contact sheet.</p>',
        '<div class="summary">',
        f"<span>{len(records)} page-width records</span>",
        f"<span>{len(widths)} breakpoints</span>",
        f"<span>{failure_count} capture failures</span>",
        f"<span>{blank_count} blank-like images</span>",
        "</div>",
        "<nav>",
    ]
    for width in widths:
        index_lines.append(f'<a href="viewport-{width}.html">{width}px</a>')
    index_lines.extend(["</nav>", "</header>", "<main>"])
    index_lines.append("<h2>Viewport Sheets</h2>")
    index_lines.append("<p>Open a viewport sheet to review every concept and every page at that breakpoint.</p>")
    index_lines.append("</main></body></html>")
    (output_dir / "index.html").write_text("\n".join(index_lines) + "\n", encoding="utf-8")

    for width in widths:
        lines = [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8" />',
            '<meta name="viewport" content="width=device-width, initial-scale=1" />',
            f"<title>Sofiati Evidence {width}px</title>",
            f"<style>{css}</style>",
            "</head>",
            "<body>",
            "<header>",
            f"<h1>{width}px Evidence</h1>",
            '<p class="muted">Each card shows the first viewport and footer/widget viewport. Tablet and mobile cards also include the opened menu.</p>',
            '<nav><a href="index.html">Index</a></nav>',
            "</header>",
            "<main>",
        ]
        for concept, rows in grouped[width].items():
            lines.append(f'<section class="concept" id="{concept}">')
            lines.append(f"<h2>{concept}</h2>")
            lines.append('<div class="grid">')
            for record in rows:
                page_name = Path(record["page"]).name
                status = "FAIL" if record.get("failures") else "PASS"
                status_class = "fail" if status == "FAIL" else "muted"
                lines.append('<article class="card">')
                lines.append(
                    f'<div class="card-title"><strong>{page_name}</strong><span class="{status_class}">{status}</span></div>'
                )
                frame_class = "frame frame--menu" if record.get("menu") else "frame"
                lines.append(f'<div class="{frame_class}">')
                lines.append(f'<img src="{record["top"]}" alt="{concept} {page_name} top viewport at {width}px" loading="lazy" />')
                lines.append(f'<img src="{record["footer"]}" alt="{concept} {page_name} footer viewport at {width}px" loading="lazy" />')
                if record.get("menu"):
                    lines.append(f'<img src="{record["menu"]}" alt="{concept} {page_name} opened mobile menu at {width}px" loading="lazy" />')
                lines.append("</div>")
                if record.get("failures"):
                    lines.append(f'<p class="fail">{"; ".join(record["failures"])}</p>')
                lines.append("</article>")
            lines.append("</div></section>")
        lines.append("</main></body></html>")
        (output_dir / f"viewport-{width}.html").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_reports(output_dir: Path, records: list[dict[str, Any]], widths: list[int]) -> None:
    SCRIPT_RUNS.mkdir(parents=True, exist_ok=True)
    failures = [record for record in records if record.get("failures")]
    blank_like = [
        (record["page"], record["width"], kind, stats)
        for record in records
        for kind, stats in record.get("stats", {}).items()
        if stats.get("blank_like")
    ]
    exact_duplicates = Counter()
    coarse_similarity = Counter()
    exact_hashes: dict[tuple[int, str, str, str], list[str]] = defaultdict(list)
    hashes: dict[tuple[int, str, str, str], list[str]] = defaultdict(list)
    for record in records:
        page_name = Path(record["page"]).name
        concept = record["page"].split("/")[1]
        for kind, stats in record.get("stats", {}).items():
            exact = stats.get("sha256")
            if exact:
                exact_hashes[(record["width"], page_name, kind, exact)].append(concept)
            digest = stats.get("hash")
            if digest:
                hashes[(record["width"], page_name, kind, digest)].append(concept)
    for key, concepts in exact_hashes.items():
        if len(concepts) > 1:
            width, page_name, kind, _digest = key
            exact_duplicates[(width, page_name, kind)] += 1
    for key, concepts in hashes.items():
        if len(concepts) > 1:
            width, page_name, kind, _digest = key
            coarse_similarity[(width, page_name, kind)] += 1

    manifest = {
        "created_at": dt.datetime.now().isoformat(timespec="seconds"),
        "output": str(output_dir.relative_to(ROOT)),
        "viewports": widths,
        "records": len(records),
        "capture_failures": len(failures),
        "blank_like_images": len(blank_like),
        "exact_duplicate_groups": sum(exact_duplicates.values()),
        "coarse_similarity_groups": sum(coarse_similarity.values()),
        "records_detail": records,
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Sofiati Full Site Visual Evidence",
        "",
        f"- Output: `{output_dir.relative_to(ROOT)}/index.html`",
        f"- Page-width records: {len(records)}",
        f"- Viewports: {', '.join(str(width) for width in widths)}",
        f"- Capture failures: {len(failures)}",
        f"- Blank-like images: {len(blank_like)}",
        f"- Exact duplicate screenshot groups: {sum(exact_duplicates.values())}",
        f"- Coarse similarity signals: {sum(coarse_similarity.values())}",
        "",
    ]
    if failures:
        lines.extend(["## Capture Failures", ""])
        for record in failures[:100]:
            lines.append(f"- {record['page']} @ {record['width']}px: {'; '.join(record['failures'])}")
        if len(failures) > 100:
            lines.append(f"- ... {len(failures) - 100} more")
        lines.append("")
    if blank_like:
        lines.extend(["## Blank-like Images", ""])
        for page, width, kind, stats in blank_like[:100]:
            lines.append(f"- {page} @ {width}px {kind}: variance {stats.get('variance')}")
        if len(blank_like) > 100:
            lines.append(f"- ... {len(blank_like) - 100} more")
        lines.append("")
    if exact_duplicates:
        lines.extend(["## Exact Duplicate Screenshot Groups", ""])
        for (width, page_name, kind), count in exact_duplicates.most_common(30):
            lines.append(f"- {page_name} @ {width}px {kind}: {count} duplicate group(s)")
        lines.append("")
    if coarse_similarity:
        lines.extend(["## Coarse Similarity Signals", ""])
        lines.append("These are low-resolution hash hints for manual sampling, not pass/fail results.")
        lines.append("")
        for (width, page_name, kind), count in coarse_similarity.most_common(30):
            lines.append(f"- {page_name} @ {width}px {kind}: {count} coarse group(s)")
        lines.append("")
    (SCRIPT_RUNS / "sofiati-full-site-visual-evidence.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Capture full-site Sofiati visual QA evidence.")
    parser.add_argument("--limit", type=int, default=0, help="Limit pages for a smoke capture.")
    parser.add_argument("--viewports", default="", help="Comma-separated subset of required widths.")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--quality", type=int, default=68)
    args = parser.parse_args()

    check_playwright()
    widths = parse_viewports(args.viewports)
    pages = [str(path.relative_to(ROOT)) for path in page_paths()]
    if args.limit:
        pages = pages[: args.limit]

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    suffix = "sample" if args.limit else "all-pages"
    output_dir = OUTPUT_ROOT / f"sofiati-full-site-evidence-{stamp}-{suffix}"
    output_dir.mkdir(parents=True, exist_ok=True)

    port = args.port or free_port()
    server = start_server(port)
    try:
        run_node_capture(port=port, pages=pages, widths=widths, output_dir=output_dir, quality=args.quality)
    finally:
        server.shutdown()
        server.server_close()

    records = enrich_records(output_dir)
    write_html(output_dir, records, widths)
    write_reports(output_dir, records, widths)

    failures = sum(1 for record in records if record.get("failures"))
    blank_like = sum(
        1
        for record in records
        for stats in record.get("stats", {}).values()
        if stats.get("blank_like")
    )
    print(
        f"Sofiati visual evidence: records={len(records)} "
        f"viewports={len(widths)} failures={failures} blank_like={blank_like} "
        f"output={output_dir.relative_to(ROOT)}/index.html"
    )
    return 1 if failures or blank_like else 0


if __name__ == "__main__":
    raise SystemExit(main())
