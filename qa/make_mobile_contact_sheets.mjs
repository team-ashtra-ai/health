#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { chromium } from "playwright";

const ROOT = process.cwd();
const IN = path.join(ROOT, "docs/qa/mobile-screenshots");
const OUT = path.join(ROOT, "docs/qa/mobile-contact-sheets");

fs.mkdirSync(OUT, { recursive: true });

function listImages(type) {
  if (!fs.existsSync(IN)) {
    console.error("Input folder not found:", IN);
    process.exit(1);
  }

  return fs.readdirSync(IN)
    .filter(f => f.endsWith(`-${type}.png`))
    .sort((a, b) => {
      const na = Number((a.match(/^(\d+)/) || [])[1] || 9999);
      const nb = Number((b.match(/^(\d+)/) || [])[1] || 9999);
      return na - nb || a.localeCompare(b);
    });
}

function batch(files, start, end) {
  return files.filter(f => {
    const n = Number((f.match(/^(\d+)/) || [])[1] || 0);
    return n >= start && n <= end;
  });
}

function makeHtml(files, title, type) {
  const cards = files.map(file => {
    const label = file.replace(".png", "");
    const src = "../mobile-screenshots/" + file;
    return `
      <article class="card">
        <h2>${label}</h2>
        <img src="${src}">
      </article>
    `;
  }).join("\n");

  return `
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>${title}</title>
<style>
  * { box-sizing: border-box; }
  body {
    margin: 0;
    background: #f4efe5;
    color: #252321;
    font-family: Arial, sans-serif;
  }
  header {
    position: sticky;
    top: 0;
    z-index: 10;
    background: #252321;
    color: #f8f7f2;
    padding: 18px 24px;
    border-bottom: 4px solid #cdaa78;
  }
  header h1 {
    margin: 0;
    font-size: 28px;
    letter-spacing: .02em;
  }
  header p {
    margin: 6px 0 0;
    font-size: 14px;
    opacity: .8;
  }
  .grid {
    padding: 24px;
    display: grid;
    grid-template-columns: repeat(5, 390px);
    gap: 24px;
    align-items: start;
  }
  .card {
    background: white;
    border: 1px solid #d8cdbb;
    box-shadow: 0 10px 30px rgba(0,0,0,.08);
    overflow: hidden;
  }
  .card h2 {
    margin: 0;
    padding: 10px 12px;
    font-size: 13px;
    line-height: 1.2;
    background: #485041;
    color: #fff;
    min-height: 42px;
  }
  .card img {
    display: block;
    width: 390px;
    height: auto;
    background: #eee;
  }
</style>
</head>
<body>
<header>
  <h1>${title}</h1>
  <p>Type: ${type}. Review mobile header, hero, footer, widgets and menu problems visually.</p>
</header>
<main class="grid">
${cards}
</main>
</body>
</html>
`;
}

async function renderSheet(files, title, type, outputName) {
  const htmlPath = path.join(OUT, `${outputName}.html`);
  const pngPath = path.join(OUT, `${outputName}.png`);

  fs.writeFileSync(htmlPath, makeHtml(files, title, type));

  const browser = await chromium.launch({ headless: true });
  const page = await browser.newPage({
    viewport: { width: 2100, height: 2600 },
    deviceScaleFactor: 1
  });

  await page.goto("file://" + htmlPath, { waitUntil: "networkidle" });
  await page.screenshot({ path: pngPath, fullPage: true });

  await browser.close();

  console.log("Created:", pngPath);
}

async function main() {
  const types = [
    "mobile-full",
    "mobile-menu-open-full",
    "mobile-header",
    "mobile-hero",
    "mobile-footer",
    "mobile-widgets"
  ];

  let made = 0;

  for (const type of types) {
    const files = listImages(type);

    if (!files.length) {
      console.log("No files for:", type);
      continue;
    }

    const groups = [
      [1, 20, "01-20"],
      [21, 40, "21-40"],
      [41, 50, "41-50"]
    ];

    for (const [start, end, label] of groups) {
      const selected = batch(files, start, end);
      if (!selected.length) continue;

      await renderSheet(
        selected,
        `Sofiati Mobile ${type} ${label}`,
        type,
        `sofiati-${type}-${label}`
      );

      made++;
    }
  }

  console.log("");
  console.log("DONE.");
  console.log("Output folder:", OUT);
  console.log("Contact sheets created:", made);
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
