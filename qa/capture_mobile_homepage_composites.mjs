#!/usr/bin/env node

import fs from "fs";
import path from "path";
import http from "http";

const ROOT = process.cwd();
const OUT = path.join(ROOT, "docs/qa/mobile-homepage-composites");

const WIDTH = 430;
const HEIGHT = 932;
const LIMIT = 50;
const SECTION_GAP = 24;
const SIDE_PAD = 24;
const TOP_PAD = 24;
const BOTTOM_PAD = 24;
const LABEL_HEIGHT = 44;
const TITLE_HEIGHT = 56;
const BG = { r: 243, g: 240, b: 234, alpha: 1 };

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
      ".json": "application/json",
      ".woff": "font/woff",
      ".woff2": "font/woff2"
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
    console.error("\nMissing dependency: playwright\nRun: npm install -D playwright sharp\n");
    process.exit(2);
  }
}

async function loadSharp() {
  try {
    const mod = await import("sharp");
    return mod.default;
  } catch {
    console.error("\nMissing dependency: sharp\nRun: npm install -D playwright sharp\n");
    process.exit(2);
  }
}

function fileExists(p) {
  try {
    return fs.existsSync(p);
  } catch {
    return false;
  }
}

async function saveElementShot(page, selectors, outFile, fallbackClip = null) {
  for (const selector of selectors) {
    try {
      const els = await page.$$(selector);
      for (const el of els) {
        const box = await el.boundingBox();
        if (!box || box.width < 20 || box.height < 20) continue;

        await el.scrollIntoViewIfNeeded();
        await page.waitForTimeout(350);

        const newBox = await el.boundingBox();
        if (!newBox || newBox.width < 20 || newBox.height < 20) continue;

        await el.screenshot({ path: outFile });
        if (fileExists(outFile)) return true;
      }
    } catch {}
  }

  if (fallbackClip) {
    try {
      await page.screenshot({
        path: outFile,
        clip: fallbackClip
      });
      if (fileExists(outFile)) return true;
    } catch {}
  }

  return false;
}

async function findFirstVisibleBox(page, selectors) {
  for (const selector of selectors) {
    try {
      const els = await page.$$(selector);
      for (const el of els) {
        const box = await el.boundingBox();
        if (box && box.width > 20 && box.height > 20) {
          return { el, box, selector };
        }
      }
    } catch {}
  }
  return null;
}

async function openMobileMenu(page) {
  const candidates = [
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
    "header button",
    "nav button",
    "button"
  ];

  for (const selector of candidates) {
    try {
      const els = await page.$$(selector);
      for (const el of els) {
        const box = await el.boundingBox();
        if (!box || box.width < 10 || box.height < 10) continue;
        if (box.y > 260) continue;

        const text = String(
          await el.evaluate(node =>
            node.getAttribute("aria-label") ||
            node.innerText ||
            node.textContent ||
            node.className ||
            ""
          )
        ).toLowerCase();

        const cls = text || "";

        const looksLikeMenu =
          cls.includes("menu") ||
          cls.includes("nav") ||
          cls.includes("hamburger") ||
          cls.includes("toggle") ||
          box.width <= 90;

        if (!looksLikeMenu) continue;

        try {
          await el.click({ force: true });
          await page.waitForTimeout(1200);
          return true;
        } catch {}
      }
    } catch {}
  }

  return false;
}

async function captureOpenMenu(page, outFile) {
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
    "[class*='mobile-menu' i]",
    "[class*='mobile-nav' i]",
    "nav"
  ];

  const found = await findFirstVisibleBox(page, menuSelectors);

  if (found?.el) {
    try {
      await found.el.scrollIntoViewIfNeeded();
      await page.waitForTimeout(300);
      await found.el.screenshot({ path: outFile });
      if (fileExists(outFile)) return true;
    } catch {}
  }

  try {
    await page.screenshot({
      path: outFile,
      clip: { x: 0, y: 0, width: WIDTH, height: HEIGHT }
    });
    return true;
  } catch {}

  return false;
}

async function captureSections(page, tmpDir) {
  const shots = [];

  // HEADER
  const headerFile = path.join(tmpDir, "01-header.png");
  await saveElementShot(
    page,
    [
      "header",
      ".site-header",
      "#header",
      "[data-partial*='header' i]",
      "[class*='header' i]",
      "nav"
    ],
    headerFile,
    { x: 0, y: 0, width: WIDTH, height: Math.min(260, HEIGHT) }
  );
  if (fileExists(headerFile)) shots.push({ label: "HEADER / NAVIGATION", file: headerFile });

  // MENU OPEN
  const menuFile = path.join(tmpDir, "02-menu-open.png");
  const opened = await openMobileMenu(page);
  if (opened) {
    await captureOpenMenu(page, menuFile);
    if (fileExists(menuFile)) shots.push({ label: "MOBILE MENU", file: menuFile });
  }

  // RELOAD AFTER MENU
  await page.reload({ waitUntil: "networkidle", timeout: 30000 });
  await page.waitForTimeout(1200);

  // HERO
  const heroFile = path.join(tmpDir, "03-hero.png");
  await saveElementShot(
    page,
    [
      ".hero",
      "section.hero",
      "[data-section*='hero' i]",
      "[class*='hero' i]",
      "main section:first-of-type",
      "section:first-of-type"
    ],
    heroFile
  );
  if (fileExists(heroFile)) shots.push({ label: "HERO", file: heroFile });

  // WIDGETS
  const widgetsFile = path.join(tmpDir, "04-widgets.png");
  await saveElementShot(
    page,
    [
      "[class*='widget' i]",
      "[id*='widget' i]",
      "[class*='floating' i]",
      "[id*='floating' i]",
      "[data-component*='floating' i]",
      "[data-partial*='widget' i]"
    ],
    widgetsFile
  );
  if (fileExists(widgetsFile)) shots.push({ label: "WIDGETS / FLOATING ACTIONS", file: widgetsFile });

  // FOOTER
  const footerFile = path.join(tmpDir, "05-footer.png");
  await saveElementShot(
    page,
    [
      "footer",
      ".site-footer",
      "#footer",
      "[data-partial*='footer' i]",
      "[class*='footer' i]"
    ],
    footerFile
  );
  if (fileExists(footerFile)) shots.push({ label: "FOOTER", file: footerFile });

  return shots;
}

function escapeSvg(text) {
  return String(text)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function makeTextSvg(width, height, text, fontSize = 18, fill = "#26231f", align = "left", weight = 600) {
  const safe = escapeSvg(text);
  const x = align === "center" ? width / 2 : 14;
  const anchor = align === "center" ? "middle" : "start";

  return Buffer.from(`
    <svg width="${width}" height="${height}" xmlns="http://www.w3.org/2000/svg">
      <rect width="100%" height="100%" fill="#f4f0ea"/>
      <text
        x="${x}"
        y="${Math.round(height / 2) + 6}"
        font-size="${fontSize}"
        font-family="Arial, Helvetica, sans-serif"
        font-weight="${weight}"
        text-anchor="${anchor}"
        fill="${fill}"
      >${safe}</text>
    </svg>
  `);
}

async function stitchComposite(sharp, title, shots, outFile) {
  const metaList = [];
  let maxWidth = 0;

  for (const shot of shots) {
    const meta = await sharp(shot.file).metadata();
    metaList.push({ ...shot, width: meta.width, height: meta.height });
    if (meta.width > maxWidth) maxWidth = meta.width;
  }

  const canvasWidth = Math.max(540, maxWidth + SIDE_PAD * 2);

  let totalHeight = TOP_PAD + TITLE_HEIGHT;

  for (const item of metaList) {
    totalHeight += LABEL_HEIGHT + item.height + SECTION_GAP;
  }

  totalHeight += BOTTOM_PAD;

  let top = TOP_PAD;
  const composites = [];

  // Title
  composites.push({
    input: makeTextSvg(canvasWidth - SIDE_PAD * 2, TITLE_HEIGHT, title, 20, "#171717", "left", 700),
    left: SIDE_PAD,
    top
  });
  top += TITLE_HEIGHT;

  for (const item of metaList) {
    composites.push({
      input: makeTextSvg(canvasWidth - SIDE_PAD * 2, LABEL_HEIGHT, item.label, 14, "#232323", "left", 700),
      left: SIDE_PAD,
      top
    });

    top += LABEL_HEIGHT;

    const left = Math.round((canvasWidth - item.width) / 2);

    composites.push({
      input: item.file,
      left,
      top
    });

    top += item.height + SECTION_GAP;
  }

  await sharp({
    create: {
      width: canvasWidth,
      height: totalHeight,
      channels: 4,
      background: BG
    }
  })
    .composite(composites)
    .png()
    .toFile(outFile);
}

async function run() {
  const pages = discoverHomepages();
  if (!pages.length) {
    console.error("No homepage index.html files found.");
    process.exit(1);
  }

  const chromium = await loadPlaywright();
  const sharp = await loadSharp();
  const { server, port } = await serveStatic(ROOT);

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
    const num = String(i + 1).padStart(2, "0");
    const slug = slugify(folder);
    const baseName = `${num}-${slug}`;
    const url = `http://127.0.0.1:${port}/${rel}`;
    const tmpDir = path.join(OUT, `_tmp_${baseName}`);

    fs.mkdirSync(tmpDir, { recursive: true });

    console.log(`[${i + 1}/${pages.length}] ${rel}`);

    const page = await context.newPage();

    try {
      await page.goto(url, { waitUntil: "networkidle", timeout: 30000 });
      await page.waitForTimeout(1500);

      const shots = await captureSections(page, tmpDir);

      const outFile = path.join(OUT, `${baseName}-mobile-home-sections.png`);
      const title = `${baseName} | mobile homepage partial audit | header, menu, hero, widgets, footer`;

      await stitchComposite(sharp, title, shots, outFile);

      indexLines.push(`${baseName} -> ${rel}`);
      console.log(`  saved: ${path.relative(ROOT, outFile)}`);
    } catch (err) {
      console.error(`  failed: ${rel}`);
      console.error(`  ${err.message}`);
    } finally {
      await page.close();
      fs.rmSync(tmpDir, { recursive: true, force: true });
    }
  }

  fs.writeFileSync(path.join(OUT, "screenshot-index.txt"), indexLines.join("\n"));

  await context.close();
  await browser.close();
  server.close();

  console.log("\nDONE");
  console.log(`Output folder: ${path.relative(ROOT, OUT)}`);
  console.log("Each homepage now has ONE combined mobile image.");
}

run().catch(err => {
  console.error(err);
  process.exit(1);
});
