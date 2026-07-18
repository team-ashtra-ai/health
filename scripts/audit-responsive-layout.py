#!/usr/bin/env python3
"""Audit every public route at release viewports and zoom-equivalent reflow.

Browser zoom changes the CSS viewport available to a page. The audit models
80%, 100%, 125% and 150% zoom by dividing each physical viewport by the zoom
factor, while retaining the physical viewport and zoom in its report label.
It checks overflow, broken imagery, undersized controls, unreadably small copy,
uncontained headings and missing shared page regions.
"""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import tempfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from functools import partial


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = (ROOT / os.environ.get("SOFIATI_SITE_ROOT", ".")).resolve()
REPORT = ROOT / os.environ.get("SOFIATI_REPORT", "screenshots/responsive-audit.json")
DEFAULT_VIEWPORTS = (320, 375, 390, 430, 768, 1024, 1280, 1440, 1920, 2560)
DEFAULT_ZOOMS = (0.8, 1.0, 1.25, 1.5, 2.0)


def configured_numbers(name: str, defaults: tuple, cast):
    configured = os.environ.get(name, "").strip()
    if not configured:
        return defaults
    return tuple(cast(value.strip()) for value in configured.split(",") if value.strip())


VIEWPORTS = configured_numbers("SOFIATI_WIDTHS", DEFAULT_VIEWPORTS, int)
ZOOMS = configured_numbers("SOFIATI_ZOOMS", DEFAULT_ZOOMS, float)


def pages() -> list[str]:
    found = [path.name for path in SOURCE_ROOT.glob("*.html")]
    found.extend(
        path.relative_to(SOURCE_ROOT).as_posix()
        for path in (SOURCE_ROOT / "journal").glob("*.html")
    )
    if os.environ.get("SOFIATI_ENGLISH_ONLY", "").lower() not in {"1", "true", "yes"}:
        found.extend(
            f"pt/{path.name}" for path in (SOURCE_ROOT / "pt").glob("*.html")
        )
    found = sorted(found, key=lambda value: (value.count("/"), value))
    selected = os.environ.get("SOFIATI_PAGES", "").strip()
    if selected:
        requested = {value.strip() for value in selected.split(",") if value.strip()}
        found = [value for value in found if value in requested]
    return found


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def main() -> int:
    os.chdir(ROOT)

    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

    class QuietServer(ThreadingHTTPServer):
        def handle_error(self, request: object, client_address: object) -> None:
            if isinstance(sys.exception(), (BrokenPipeError, ConnectionResetError)):
                return
            super().handle_error(request, client_address)

    port = free_port()
    server = QuietServer(("127.0.0.1", port), partial(Quiet, directory=SOURCE_ROOT))
    Thread(target=server.serve_forever, daemon=True).start()

    runner = r'''
const { chromium } = require("playwright");
const base = process.argv[2];
const routes = JSON.parse(process.argv[3]);
const widths = JSON.parse(process.argv[4]);
const zooms = JSON.parse(process.argv[5]);

(async () => {
  const browser = await chromium.launch({headless: true, args: ["--disable-dev-shm-usage", "--disable-gpu"]});
  const results = [];
  for (const zoom of zooms) {
    const context = await browser.newContext({
      viewport: {width: 390, height: 900},
      deviceScaleFactor: zoom,
    });
    const page = await context.newPage();
    let runtimeErrors = [];
    page.on("pageerror", error => runtimeErrors.push(error.message));
    page.on("console", message => {
      if (message.type() === "error") runtimeErrors.push(message.text());
    });
    await page.addInitScript(() => localStorage.setItem(
      "sofiati_cookie_preferences_v3",
      JSON.stringify({essential: true, analytics: false, preferences: false, externalMedia: false})
    ));
    for (const physicalWidth of widths) {
      for (const route of routes) {
        const cssWidth = Math.max(320, Math.round(physicalWidth / zoom));
        await page.setViewportSize({width: cssWidth, height: 900});
        runtimeErrors = [];
        await page.goto(`${base}/${route}`, {waitUntil: "load", timeout: 30000});
        await page.waitForFunction(() =>
          document.querySelector("#sf-header-inline") && document.querySelector("#sf-footer-inline"),
          null, {timeout: 2000}
        ).catch(() => {});
        const metrics = await page.evaluate(() => {
          const root = document.documentElement;
          const body = document.body;
          const visible = element => {
            const style = getComputedStyle(element);
            return style.display !== "none" && style.visibility !== "hidden" && element.getClientRects().length;
          };
          const controls = [...document.querySelectorAll("a.sf-button, button, input:not([type=hidden]), select, textarea")]
            .filter(element => visible(element) && !element.closest(".sf-honeypot, [aria-hidden=true]"))
            .map(element => ({
              tag: element.tagName.toLowerCase(),
              text: (element.textContent || element.getAttribute("aria-label") || element.name || "").trim().slice(0, 60),
              width: Math.round((["checkbox", "radio"].includes(element.type) ? element.closest("label") : element).getBoundingClientRect().width),
              height: Math.round((["checkbox", "radio"].includes(element.type) ? element.closest("label") : element).getBoundingClientRect().height),
            }));
          const smallCopy = [...document.querySelectorAll("main p, main li, main label, main summary")]
            .filter(element => visible(element)
              && !element.matches(".sf-eyebrow, .sf-meta")
              && !element.closest(".sf-breadcrumbs, [data-compact-copy]"))
            .map(element => ({
              text: (element.textContent || "").trim().slice(0, 60),
              size: parseFloat(getComputedStyle(element).fontSize),
            })).filter(item => item.text && item.size < 14);
          const brokenImages = [...document.images]
            .filter(image => image.complete && image.naturalWidth === 0)
            .map(image => image.getAttribute("src"));
          const escapedHeadings = [...document.querySelectorAll("main h1, main h2, main h3")]
            .filter(visible).filter(heading => {
              const box = heading.getBoundingClientRect();
              return box.left < -4 || box.right > innerWidth + 4;
            }).map(heading => heading.textContent.trim().slice(0, 80));
          return {
            title: document.title,
            scrollWidth: Math.max(root.scrollWidth, body.scrollWidth),
            clientWidth: root.clientWidth,
            scrollHeight: Math.max(root.scrollHeight, body.scrollHeight),
            missingRegions: ["main", "#sf-header-inline", "#sf-footer-inline"]
              .filter(selector => !document.querySelector(selector)),
            brokenImages,
            escapedHeadings,
            smallCopy,
            undersizedControls: controls.filter(control => control.height < 44 || control.width < 44),
          };
        });
        const failures = [];
        if (metrics.scrollWidth > metrics.clientWidth + 1) failures.push("horizontal-overflow");
        if (metrics.brokenImages.length) failures.push("broken-images");
        if (metrics.escapedHeadings.length) failures.push("escaped-headings");
        if (metrics.smallCopy.length) failures.push("small-copy");
        if (metrics.undersizedControls.length) failures.push("undersized-controls");
        if (metrics.missingRegions.length) failures.push("missing-regions");
        if (runtimeErrors.length) failures.push("runtime-errors");
        results.push({route, physicalWidth, zoom, cssWidth, failures, runtimeErrors, ...metrics});
      }
    }
    await context.close();
  }
  await browser.close();
  process.stdout.write(JSON.stringify(results));
})().catch(error => { console.error(error); process.exit(1); });
'''

    with tempfile.NamedTemporaryFile("w", suffix=".cjs", dir=ROOT, delete=False) as handle:
        handle.write(runner)
        runner_path = handle.name
    try:
        completed = subprocess.run(
            [
                "node", runner_path, f"http://127.0.0.1:{port}",
                json.dumps(pages()), json.dumps(VIEWPORTS), json.dumps(ZOOMS),
            ], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
    finally:
        Path(runner_path).unlink(missing_ok=True)
        server.shutdown()

    if completed.returncode:
        print(completed.stderr)
        return completed.returncode
    results = json.loads(completed.stdout)
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    failed = [result for result in results if result["failures"]]
    print(f"Audited {len(pages())} routes across {len(VIEWPORTS)} widths and {len(ZOOMS)} zoom levels ({len(results)} cases).")
    print(f"Failures: {len(failed)}")
    for result in failed[:40]:
        print(f"- {result['route']} · {result['physicalWidth']}px · {result['zoom']:.0%}: {', '.join(result['failures'])}")
    print(f"Report: {REPORT}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
