#!/usr/bin/env python3
"""Capture full-page homepage screenshots at mobile, tablet, and desktop sizes."""

from __future__ import annotations

import argparse
import json
import os
import socket
import subprocess
import tempfile
import time
from datetime import datetime
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_ROOT = ROOT / "screenshots"

VIEWPORTS = {
    "mobile": {"width": 390, "height": 844, "isMobile": True},
    "tablet": {"width": 820, "height": 1180, "isMobile": True},
    "desktop": {"width": 1440, "height": 1200, "isMobile": False},
}


def find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def start_server(port: int) -> ThreadingHTTPServer:
    os.chdir(ROOT)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def wait_for_server(port: int, timeout: float = 8.0) -> None:
    started = time.time()
    while time.time() - started < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.25)
            if sock.connect_ex(("127.0.0.1", port)) == 0:
                return
        time.sleep(0.1)
    raise RuntimeError(f"Local server did not start on port {port}.")


def require_node_playwright() -> None:
    result = subprocess.run(
        ["node", "-e", "require('playwright');"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.returncode != 0:
        raise SystemExit(
            "Playwright is not installed for Node. Run `npm install` first, then try again."
        )


def capture_with_playwright(url: str, output_root: Path, stamp: str, headed: bool) -> dict[str, object]:
    runner = """
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const url = process.argv[2];
const outputRoot = process.argv[3];
const stamp = process.argv[4];
const headed = process.argv[5] === "true";
const viewports = JSON.parse(process.argv[6]);

(async () => {
  fs.mkdirSync(outputRoot, { recursive: true });
  const browser = await chromium.launch({
    headless: !headed,
    args: ["--disable-dev-shm-usage"],
  });
  const captures = [];

  for (const [name, viewport] of Object.entries(viewports)) {
    const context = await browser.newContext({
      viewport: { width: viewport.width, height: viewport.height },
      isMobile: viewport.isMobile,
      deviceScaleFactor: 1,
    });
    const page = await context.newPage();
    const deviceDir = path.join(outputRoot, name);
    fs.mkdirSync(deviceDir, { recursive: true });
    const fileName = `homepage-fullpage-${stamp}.png`;
    const filePath = path.join(deviceDir, fileName);

    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 45000 });
    await page.waitForLoadState("networkidle", { timeout: 10000 }).catch(() => {});
    await page.waitForTimeout(500);

    const size = await page.evaluate(() => {
      const documentElement = document.documentElement;
      const body = document.body;
      return {
        width: Math.max(
          documentElement.scrollWidth,
          documentElement.offsetWidth,
          body ? body.scrollWidth : 0,
          body ? body.offsetWidth : 0
        ),
        height: Math.max(
          documentElement.scrollHeight,
          documentElement.offsetHeight,
          body ? body.scrollHeight : 0,
          body ? body.offsetHeight : 0
        ),
      };
    });

    await page.setViewportSize({
      width: viewport.width,
      height: Math.min(Math.max(size.height, viewport.height), 16000),
    });
    await page.screenshot({
      path: filePath,
      clip: {
        x: 0,
        y: 0,
        width: viewport.width,
        height: Math.min(Math.max(size.height, viewport.height), 16000),
      },
    });

    captures.push({
      name,
      width: viewport.width,
      height: viewport.height,
      capturedHeight: Math.min(Math.max(size.height, viewport.height), 16000),
      file: path.join(name, fileName),
    });

    await context.close();
  }

  await browser.close();
  console.log(JSON.stringify({ captures }, null, 2));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
"""

    with tempfile.NamedTemporaryFile("w", suffix=".cjs", dir=ROOT, delete=False) as temp:
        temp.write(runner)
        temp_path = Path(temp.name)

    try:
        result = subprocess.run(
            [
                "node",
                str(temp_path),
                url,
                str(output_root),
                stamp,
                "true" if headed else "false",
                json.dumps(VIEWPORTS),
            ],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
    finally:
        temp_path.unlink(missing_ok=True)

    if result.returncode != 0:
        print(result.stdout)
        raise SystemExit(result.returncode)

    print(result.stdout.rstrip())
    return json.loads(result.stdout)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=0, help="Local server port. Default: auto.")
    parser.add_argument(
        "--path",
        default="/index.html",
        help="Homepage path to capture from the local server. Default: /index.html.",
    )
    parser.add_argument(
        "--out-dir",
        default="",
        help="Output root directory. Default: screenshots/.",
    )
    parser.add_argument("--headed", action="store_true", help="Show the browser while capturing.")
    args = parser.parse_args()

    require_node_playwright()

    port = args.port or find_free_port()
    stamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_root = Path(args.out_dir).resolve() if args.out_dir else DEFAULT_OUTPUT_ROOT
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "archive").mkdir(parents=True, exist_ok=True)

    server = start_server(port)
    try:
        wait_for_server(port)
        path = args.path if args.path.startswith("/") else f"/{args.path}"
        url = f"http://127.0.0.1:{port}{path}"
        result = capture_with_playwright(url, output_root, stamp, args.headed)

        manifest = {
            "generatedAt": datetime.now().isoformat(timespec="seconds"),
            "url": url,
            "outputRoot": str(output_root),
            **result,
        }
        manifest_path = output_root / "archive" / f"homepage-{stamp}-manifest.json"
        manifest_path.write_text(
            json.dumps(manifest, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Screenshots saved under: {output_root}")
        print(f"Manifest: {manifest_path}")
    finally:
        server.shutdown()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
