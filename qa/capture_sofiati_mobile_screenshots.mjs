#!/usr/bin/env node

import fs from "fs";
import path from "path";
import http from "http";

const ROOT = process.cwd();
const OUT = path.join(ROOT, "docs/qa/mobile-screenshots");
const WIDTH = 390;
const HEIGHT = 844;
const LIMIT = 50;

fs.mkdirSync(OUT, { recursive: true });

function slugify(s) {
  return String(s)
    .replace(/[^a-zA-Z0-9._-]+/g, "-")
    .replace(/-+/g, "-")
    .replace(/^-|-$/g, "")
    .slice(0, 100) || "page";
}

function walk(dir, results = []) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    const rel = path.relative(ROOT, full);

    if (
      entry.isDirectory() &&
      [".git", "node_modules", ".venv", "venv", "__pycache__", ".cache", "docs"].includes(entry.name)
    ) continue;

    if (entry.isDirectory()) walk(full, results);
    else if (entry.isFile() && entry.name.endsWith(".html")) results.push(full);
  }
  return results;
}

function discoverPages() {
  const all = walk(ROOT);
  let pages = all.filter(p => ["index.html", "home.html"].includes(path.basename(p).toLowerCase()));
  if (!pages.length) pages = all;

  pages.sort((a, b) => {
    const ra = path.relative(ROOT, a).replaceAll(path.sep, "/");
    const rb = path.relative(ROOT, b).replaceAll(path.sep, "/");

    const na = Number((ra.match(/(^|\/)(\d{1,3})[-_]/) || [])[2] || 9999);
    const nb = Number((rb.match(/(^|\/)(\d{1,3})[-_]/) || [])[2] || 9999);

    return na - nb || ra.localeCompare(rb);
  });

  return pages.slice(0, LIMIT);
}

function serveStatic(root) {
  const server = http.createServer((req, res) => {
    const cleanUrl = decodeURIComponent(req.url.split("?")[0]);
    let filePath = path.join(root, cleanUrl);

    if (fs.existsSync(filePath) && fs.statSync(filePath).isDirectory()) {
      filePath = path.join(filePath, "index.html");
    }

    if (!fs.existsSync(filePath)) {
      res.writeHead(404);
      res.end("Not found");
      return;
    }

    const ext = path.extname(filePath).toLowerCase();
    const types = {
      ".html": "text/html",
      ".css": "text/css",
      ".js": "text/javascript",
      ".png": "image/png",
      ".jpg": "image/jpeg",
      ".jpeg": "image/jpeg",
      ".webp": "image/webp",
      ".svg": "image/svg+xml",
      ".json": "application/json"
    };

    res.writeHead(200, { "Content-Type": types[ext] || "application/octet-stream" });
    fs.createReadStream(filePath).pipe(res);
  });

  return new Promise(resolve => {
    server.listen(0, "127.0.0.1", () => {
      resolve({ server, port: server.address().port });
    });
  });
}

async function loadPlaywright() {
  try {
    const mod = await import("playwright");
    return mod.chromium;
  } catch {
    console.error(`
Playwright is not installed for Node.

Run:
  npm install -D playwright

Then run:
  node qa/capture_sofiati_mobile_screenshots.mjs
`);
    process.exit(2);
  }
}

async function screenshotFirst(page, selectors, file) {
  for (const sel of selectors) {
    const el = await page.$(sel);
    if (!el) continue;

    try {
      await el.scrollIntoViewIfNeeded();
      await page.waitForTimeout(300);
      await el.screenshot({ path: file });
      return true;
    } catch {}
  }

  return false;
}

async function clickMobileMenu(page) {
  const selectors = [
    "button[aria-label*='menu' i]",
    "button[aria-controls]",
    "[data-menu-toggle]",
    "[data-nav-toggle]",
    "[data-mobile-menu-toggle]",
    ".menu-toggle",
    ".nav-toggle",
    ".hamburger",
    ".mobile-menu-toggle",
    ".mobile-nav-toggle",
    "button"
  ];

  for (const sel of selectors) {
    const handles = await page.$$(sel);

    for (const h of handles) {
      try {
        const box = await h.boundingBox();
        const text = String(
          await h.evaluate(el =>
            el.innerText ||
            el.textContent ||
            el.getAttribute("aria-label") ||
            el.className ||
            ""
          )
        ).toLowerCase();

        if (
          box &&
          box.y < 260 &&
          (
            text.includes("menu") ||
            text.includes("☰") ||
            text.includes("hamburger") ||
            text.includes("nav")
          )
        ) {
          await h.click();
          await page.waitForTimeout(900);
          return true;
        }
      } catch {}
    }
  }

  return false;
}

async function run() {
  const pages = discoverPages();

  if (!pages.length) {
    console.error("No HTML pages found.");
    process.exit(1);
  }

  const { server, port } = await serveStatic(ROOT);
  const chromium = await loadPlaywright();

  const browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: WIDTH, height: HEIGHT },
    deviceScaleFactor: 2,
    isMobile: true,
    hasTouch: true,
    userAgent:
      "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
  });

  const indexLines = [];

  for (let i = 0; i < pages.length; i++) {
    const file = pages[i];
    const rel = path.relative(ROOT, file).replaceAll(path.sep, "/");
    const folder = path.basename(path.dirname(file));
    const name = `${String(i + 1).padStart(2, "0")}-${slugify(folder || path.basename(file, ".html"))}`;
    const url = `http://127.0.0.1:${port}/${rel}`;

    console.log(`[${i + 1}/${pages.length}] Capturing mobile screenshots: ${rel}`);

    const page = await context.newPage();

    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(1500);

    await page.screenshot({
      path: path.join(OUT, `${name}-mobile-full.png`),
      fullPage: true
    });

    await screenshotFirst(
      page,
      ["header", ".site-header", "#header", "[class*='header' i]", "nav"],
      path.join(OUT, `${name}-mobile-header.png`)
    );

    await screenshotFirst(
      page,
      [".hero", "section.hero", "[class*='hero' i]", "main section:first-of-type"],
      path.join(OUT, `${name}-mobile-hero.png`)
    );

    await screenshotFirst(
      page,
      ["[class*='widget' i]", "[class*='floating' i]", "[id*='widget' i]", "[id*='floating' i]"],
      path.join(OUT, `${name}-mobile-widgets.png`)
    );

    await screenshotFirst(
      page,
      ["footer", ".site-footer", "#footer", "[class*='footer' i]"],
      path.join(OUT, `${name}-mobile-footer.png`)
    );

    const opened = await clickMobileMenu(page);

    if (opened) {
      await page.screenshot({
        path: path.join(OUT, `${name}-mobile-menu-open-full.png`),
        fullPage: true
      });

      await screenshotFirst(
        page,
        [
          "[aria-modal='true']",
          "[role='dialog']",
          ".mobile-menu",
          ".mobile-nav",
          ".menu-open",
          ".nav-open",
          "[class*='drawer' i]",
          "[class*='overlay' i]",
          "nav"
        ],
        path.join(OUT, `${name}-mobile-menu-open-crop.png`)
      );
    }

    indexLines.push(`${name} -> ${rel}`);
    await page.close();
  }

  fs.writeFileSync(path.join(OUT, "screenshot-index.txt"), indexLines.join("\n"));

  await context.close();
  await browser.close();
  server.close();

  console.log("");
  console.log("DONE — screenshots only.");
  console.log(`Output folder: ${OUT}`);
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
