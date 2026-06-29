#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import socket
import subprocess
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from threading import Thread


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
DEFAULT_OUT_ROOT = ROOT / "final" / "homepage-screenshots"


def find_free_port() -> int:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("127.0.0.1", 0))
    port = int(s.getsockname()[1])
    s.close()
    return port


def port_is_open(port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.3)
    try:
        s.connect(("127.0.0.1", port))
        return True
    except OSError:
        return False
    finally:
        s.close()


def list_concepts(limit: int | None = None) -> list[str]:
    concepts = sorted(
        p.name
        for p in CONCEPTS_DIR.iterdir()
        if p.is_dir() and p.name[:2].isdigit() and (p / "index.html").exists()
    )
    if limit:
        return concepts[:limit]
    return concepts


def start_server(port: int) -> ThreadingHTTPServer:
    os.chdir(ROOT)

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def wait_for_server(port: int, timeout: float = 8.0) -> None:
    started = time.time()
    while time.time() - started < timeout:
        if port_is_open(port):
            return
        time.sleep(0.15)
    raise RuntimeError(f"Server did not start on port {port}")


def require_playwright() -> None:
    check = subprocess.run(
        ["node", "-e", "require('playwright'); console.log('ok')"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if check.returncode != 0:
        print("ERROR: Node Playwright is not available.")
        print(check.stdout)
        print("Try this:")
        print("npm install playwright")
        raise SystemExit(1)


def write_node_runner(path: Path) -> None:
    path.write_text(
        r'''
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

const port = Number(process.argv[2]);
const outDir = process.argv[3];
const headed = process.argv[4] === "true";
const modes = JSON.parse(process.argv[5]);
const concepts = JSON.parse(process.argv[6]);

function urlFor(concept) {
  return `http://localhost:${port}/concepts/${encodeURIComponent(concept)}/index.html`;
}

(async () => {
  fs.mkdirSync(outDir, { recursive: true });

  console.log(`Found ${concepts.length} concept homepages.`);
  console.log(`Port: ${port}`);
  console.log(`Output: ${outDir}`);
  console.log("");

  const browser = await chromium.launch({ headless: !headed });

  let completed = 0;
  let failed = 0;
  const failures = [];
  const totalJobs = concepts.length * modes.length;

  const contexts = {};

  if (modes.includes("desktop")) {
    contexts.desktop = await browser.newContext({
      viewport: { width: 1440, height: 1800 },
      deviceScaleFactor: 1,
    });
  }

  if (modes.includes("mobile")) {
    contexts.mobile = await browser.newContext({
      viewport: { width: 390, height: 1200 },
      isMobile: true,
      deviceScaleFactor: 1,
    });
  }

  for (const concept of concepts) {
    for (const mode of modes) {
      const jobNumber = completed + failed + 1;
      const url = urlFor(concept);
      const page = await contexts[mode].newPage();
      const screenshotPath = path.join(outDir, `${concept}-${mode}-full.png`);

      console.log(`[${jobNumber}/${totalJobs}] capturing ${concept} ${mode}...`);

      try {
        await page.goto(url, { waitUntil: "networkidle", timeout: 45000 });
        await page.screenshot({ path: screenshotPath, fullPage: true });
        completed += 1;
        console.log(`[${jobNumber}/${totalJobs}] done ${concept} ${mode} -> ${screenshotPath}`);
      } catch (error) {
        failed += 1;
        failures.push({
          concept,
          mode,
          url,
          error: String(error && error.message ? error.message : error),
        });
        console.error(`[${jobNumber}/${totalJobs}] FAILED ${concept} ${mode}: ${error.message || error}`);
      } finally {
        await page.close().catch(() => {});
      }
    }
  }

  for (const context of Object.values(contexts)) {
    await context.close();
  }

  await browser.close();

  const report = {
    generatedAt: new Date().toISOString(),
    port,
    outDir,
    totalConcepts: concepts.length,
    modes,
    totalJobs,
    completed,
    failed,
    failures,
  };

  fs.writeFileSync(path.join(outDir, "capture-report.json"), JSON.stringify(report, null, 2));

  console.log("");
  console.log("Capture complete.");
  console.log(`Completed jobs: ${completed}/${totalJobs}`);
  console.log(`Failed jobs: ${failed}`);
  console.log(`Report: ${path.join(outDir, "capture-report.json")}`);

  if (failed > 0) {
    process.exitCode = 1;
  }
})();
'''.strip()
        + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="auto", help="Use a specific port, or auto. Default: auto.")
    parser.add_argument("--out-dir", default="", help="Output directory. Default: final/homepage-screenshots/full-TIMESTAMP")
    parser.add_argument("--headed", action="store_true", help="Show browser window.")
    parser.add_argument("--limit", type=int, default=None, help="Capture only the first N concepts.")
    parser.add_argument("--desktop-only", action="store_true", help="Capture desktop only.")
    parser.add_argument("--mobile-only", action="store_true", help="Capture mobile only.")
    args = parser.parse_args()

    require_playwright()

    port = find_free_port() if args.port == "auto" else int(args.port)

    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path(args.out_dir).resolve() if args.out_dir else DEFAULT_OUT_ROOT / f"full-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)

    concepts = list_concepts(args.limit)
    if not concepts:
        print("ERROR: no concept homepages found in concepts/*/index.html")
        return 1

    if args.desktop_only and args.mobile_only:
        print("ERROR: choose only one of --desktop-only or --mobile-only")
        return 1

    if args.desktop_only:
        modes = ["desktop"]
    elif args.mobile_only:
        modes = ["mobile"]
    else:
        modes = ["desktop", "mobile"]

    print("Starting local server...")
    print(f"Selected free port: {port}")

    server = start_server(port)

    try:
        wait_for_server(port)
        print(f"Server ready: http://localhost:{port}/select.html")
        print("")

        runner = ROOT / "qa" / "capture_homepages_progress_runner.cjs"
        runner.parent.mkdir(parents=True, exist_ok=True)
        write_node_runner(runner)

        cmd = [
            "node",
            str(runner),
            str(port),
            str(out_dir),
            "true" if args.headed else "false",
            json.dumps(modes),
            json.dumps(concepts),
        ]

        result = subprocess.run(cmd, cwd=ROOT)

        print("")
        print(f"Screenshots saved to: {out_dir}")
        print(f"Preview URL used: http://localhost:{port}/select.html")

        return int(result.returncode)

    finally:
        server.shutdown()
        server.server_close()
        print("Temporary server stopped.")


if __name__ == "__main__":
    raise SystemExit(main())
