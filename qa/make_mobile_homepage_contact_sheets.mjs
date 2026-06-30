#!/usr/bin/env node

import fs from "fs";
import path from "path";
import { chromium } from "playwright";

const ROOT = process.cwd();
const IN = path.join(ROOT, "docs/qa/mobile-homepage-composites");
const OUT = path.join(ROOT, "docs/qa/mobile-homepage-contact-sheets");

fs.mkdirSync(OUT, { recursive: true });

if (!fs.existsSync(IN)) {
  console.error("Input folder not found:", IN);
  process.exit(1);
}

function getNumber(file) {
  return Number((file.match(/^(\d+)/) || [])[1] || 9999);
}

function listImages() {
  return fs.readdirSync(IN)
    .filter(f => /\.(png|jpg|jpeg|webp)$/i.test(f))
    .sort((a, b) => getNumber(a) - getNumber(b) || a.localeCompare(b));
}

function batch(files, start, end) {
  return files.filter(f => {
    const n = getNumber(f);
    return n >= start && n <= end;
  });
}

function makeHtml(files, title) {
  const cards = files.map(file => {
    const label = file.replace(/\.(png|jpg|jpeg|webp)$/i, "");
    const src = "../mobile-homepage-composites/" + file;

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
  <p>Combined mobile homepage screenshots. Review header, hero, widgets, footer and menu problems visually.</p>
</header>
<main class="grid">
${cards}
</main>
</body>
</html>
`;
}

async function renderSheet(files, title, outputName) {
  if (!files.length) {
    console.log("No files for:", outputName);
    return;
  }

  const htmlPath = path.join(OUT, `${outputName}.html`);
  const pngPath = path.join(OUT, `${outputName}.png`);

  fs.writeFileSync(htmlPath, makeHtml(files, title));

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
  const files = listImages();

  console.log("Found images:", files.length);

  await renderSheet(batch(files, 1, 20), "Sofiati Mobile Homepage 01–20", "sofiati-mobile-homepage-01-20");
  await renderSheet(batch(files, 21, 40), "Sofiati Mobile Homepage 21–40", "sofiati-mobile-homepage-21-40");
  await renderSheet(batch(files, 41, 50), "Sofiati Mobile Homepage 41–50", "sofiati-mobile-homepage-41-50");

  console.log("");
  console.log("DONE.");
  console.log("Upload these:");
  console.log("docs/qa/mobile-homepage-contact-sheets/sofiati-mobile-homepage-01-20.png");
  console.log("docs/qa/mobile-homepage-contact-sheets/sofiati-mobile-homepage-21-40.png");
  console.log("docs/qa/mobile-homepage-contact-sheets/sofiati-mobile-homepage-41-50.png");
}

main().catch(err => {
  console.error(err);
  process.exit(1);
});
