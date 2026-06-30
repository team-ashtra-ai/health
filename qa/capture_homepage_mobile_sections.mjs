#!/usr/bin/env node

import fs from "fs";
import path from "path";
import http from "http";

const ROOT = process.cwd();
const OUT = path.join(ROOT, "docs/qa/homepage-mobile-sections");

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
    else if (entry.isFile() && entry.name.toLowerCase() === "index.html") {
      results.push(full);
    }
  }

  return results;
}

function discoverHomepages() {
  const pages = walk(ROOT);

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

    res.writeHead(200, {
      "Content-Type": types[ext] || "application/octet-stream"
    });

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
Playwright is not installed.

Run:
  npm install -D playwright

Then run:
  node qa/capture_homepage_mobile_sections.mjs
`);
    process.exit(2);
  }
}

async function screenshotElement(page, selectors, file) {
  for (const selector of selectors) {
    const elements = await page.$$(selector);

    for (const el of elements) {
      try {
        const box = await el.boundingBox();

        if (!box || box.width < 20 || box.height < 20) continue;

        await el.scrollIntoViewIfNeeded();
        await page.waitForTimeout(350);

        await el.screenshot({ path: file });

        return true;
      } catch {}
    }
  }

  return false;
}

async function clickMobileMenu(page) {
  const selectors = [
    "button[aria-label*='menu' i]",
    "button[aria-label*='nav' i]",
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

  for (const selector of selectors) {
    const buttons = await page.$$(selector);

    for (const btn of buttons) {
      try {
        const box = await btn.boundingBox();

        if (!box || box.y > 320 || box.width < 10 || box.height < 10) continue;

        const text = String(
          await btn.evaluate(el =>
            el.innerText ||
            el.textContent ||
            el.getAttribute("aria-label") ||
            el.className ||
            ""
          )
        ).toLowerCase();

        if (
          text.includes("menu") ||
          text.includes("nav") ||
          text.includes("☰") ||
          text.includes("hamburger") ||
          box.width < 80
        ) {
          await btn.click();
          await page.waitForTimeout(1000);
          return true;
        }
      } catch {}
    }
  }

  return false;
}

async function screenshotOpenMenu(page, file) {
  const menuSelectors = [
    "[aria-modal='true']",
    "[role='dialog']",
    ".mobile-menu",
    ".mobile-nav",
    ".menu-open",
    ".nav-open",
    ".is-open",
    ".open",
    "[class*='drawer' i]",
    "[class*='overlay' i]",
    "[class*='menu' i]"
  ];

  const captured = await screenshotElement(page, menuSelectors, file);

  if (captured) return true;

  // fallback: capture the visible viewport after menu opens
  await page.screenshot({ path: file, fullPage: false });
  return true;
}

async function run() {
  const pages = discoverHomepages();

  if (!pages.length) {
    console.error("No homepage index.html files found.");
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

  const index = [];

  for (let i = 0; i < pages.length; i++) {
    const file = pages[i];
    const rel = path.relative(ROOT, file).replaceAll(path.sep, "/");
    const folder = path.basename(path.dirname(file));
    const name = `${String(i + 1).padStart(2, "0")}-${slugify(folder)}`;
    const url = `http://127.0.0.1:${port}/${rel}`;

    console.log(`[${i + 1}/${pages.length}] Capturing homepage mobile sections: ${rel}`);

    const page = await context.newPage();

    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(1500);

    await screenshotElement(
      page,
      [
        "header",
        ".site-header",
        "#header",
        "[data-partial*='header' i]",
        "[class*='header' i]",
        "nav"
      ],
      path.join(OUT, `${name}-01-header.png`)
    );

    const opened = await clickMobileMenu(page);

    if (opened) {
      await screenshotOpenMenu(
        page,
        path.join(OUT, `${name}-02-menu-open.png`)
      );
    } else {
      console.log(`  menu not opened: ${rel}`);
    }

    // close/reload so the open menu does not cover hero/footer screenshots
    await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
    await page.waitForTimeout(1000);

    await screenshotElement(
      page,
      [
        ".hero",
        "section.hero",
        "[data-section*='hero' i]",
        "[class*='hero' i]",
        "main section:first-of-type",
        "section:first-of-type"
      ],
      path.join(OUT, `${name}-03-hero.png`)
    );

    await screenshotElement(
      page,
      [
        "[class*='widget' i]",
        "[id*='widget' i]",
        "[class*='floating' i]",
        "[id*='floating' i]",
        "[data-component*='floating' i]",
        "[data-partial*='widget' i]"
      ],
      path.join(OUT, `${name}-04-widgets.png`)
    );

    await screenshotElement(
      page,
      [
        "footer",
        ".site-footer",
        "#footer",
        "[data-partial*='footer' i]",
        "[class*='footer' i]"
      ],
      path.join(OUT, `${name}-05-footer.png`)
    );

    index.push(`${name} -> ${rel}`);

    await page.close();
  }

  fs.writeFileSync(path.join(OUT, "screenshot-index.txt"), index.join("\n"));

  await context.close();
  await browser.close();
  server.close();

  console.log("");
  console.log("DONE.");
  console.log("Only these homepage mobile section screenshots were created:");
  console.log("- header");
  console.log("- open menu");
  console.log("- hero");
  console.log("- widgets");
  console.log("- footer");
  console.log("");
  console.log(`Output folder: ${OUT}`);
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
