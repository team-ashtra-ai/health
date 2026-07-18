#!/usr/bin/env node

import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import sharp from 'sharp';
import { chromium } from 'playwright-core';
import { startStaticServer } from '../lib/static-server.mjs';

const VIEWPORTS = [
  [320, 800],
  [375, 812],
  [390, 844],
  [430, 932],
  [768, 1024],
  [1024, 768],
  [1366, 768],
  [1440, 900],
  [1920, 1080]
];
const ROUTES = (process.env.VISUAL_ROUTES || 'index.html,about.html,treatments.html,contact.html,faq.html,journal.html')
  .split(',')
  .filter(Boolean);
const OUTPUT = resolve('performance-reports/visual');

function slug(route) {
  return route.replace(/index\.html$/, 'home').replace(/\.html$/, '').replaceAll('/', '--');
}

async function screenshot(browser, baseUrl, route, viewport, destination, reducedMotion = 'no-preference') {
  const page = await browser.newPage({ viewport, reducedMotion });
  await page.goto(`${baseUrl}/${route}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(300);
  await page.screenshot({ path: destination, fullPage: true, animations: 'disabled' });
  await page.close();
}

async function visualDifference(baselinePath, finalPath) {
  const baselineMeta = await sharp(baselinePath).metadata();
  const finalMeta = await sharp(finalPath).metadata();
  if (baselineMeta.width !== finalMeta.width || baselineMeta.height !== finalMeta.height) {
    return {
      comparable: false,
      baselineDimensions: `${baselineMeta.width}x${baselineMeta.height}`,
      finalDimensions: `${finalMeta.width}x${finalMeta.height}`,
      mismatchPercent: 100
    };
  }
  const width = Math.max(1, Math.round(baselineMeta.width / 4));
  const height = Math.max(1, Math.round(baselineMeta.height / 4));
  const baseline = await sharp(baselinePath).resize(width, height).removeAlpha().raw().toBuffer();
  const final = await sharp(finalPath).resize(width, height).removeAlpha().raw().toBuffer();
  let mismatched = 0;
  const pixelCount = width * height;
  for (let index = 0; index < baseline.length; index += 3) {
    const difference = Math.abs(baseline[index] - final[index])
      + Math.abs(baseline[index + 1] - final[index + 1])
      + Math.abs(baseline[index + 2] - final[index + 2]);
    if (difference > 90) mismatched += 1;
  }
  return {
    comparable: true,
    baselineDimensions: `${baselineMeta.width}x${baselineMeta.height}`,
    finalDimensions: `${finalMeta.width}x${finalMeta.height}`,
    mismatchPercent: Math.round((mismatched / pixelCount) * 10000) / 100
  };
}

await mkdir(resolve(OUTPUT, 'baseline'), { recursive: true });
await mkdir(resolve(OUTPUT, 'final'), { recursive: true });
const [sourceServer, finalServer] = await Promise.all([
  startStaticServer(resolve('.')),
  startStaticServer(resolve('dist'))
]);
const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', headless: true });
const results = [];
try {
  for (const route of ROUTES) {
    for (const [width, height] of VIEWPORTS) {
      const name = `${slug(route)}--${width}x${height}.png`;
      const baselinePath = resolve(OUTPUT, 'baseline', name);
      const finalPath = resolve(OUTPUT, 'final', name);
      process.stdout.write(`Comparing ${route} at ${width}x${height}\n`);
      await screenshot(browser, sourceServer.baseUrl, route, { width, height }, baselinePath);
      await screenshot(browser, finalServer.baseUrl, route, { width, height }, finalPath);
      results.push({
        route,
        viewport: `${width}x${height}`,
        ...await visualDifference(baselinePath, finalPath)
      });
    }
  }
  const reducedName = 'home--390x844--reduced-motion.png';
  await screenshot(
    browser,
    sourceServer.baseUrl,
    'index.html',
    { width: 390, height: 844 },
    resolve(OUTPUT, 'baseline', reducedName),
    'reduce'
  );
  await screenshot(
    browser,
    finalServer.baseUrl,
    'index.html',
    { width: 390, height: 844 },
    resolve(OUTPUT, 'final', reducedName),
    'reduce'
  );
} finally {
  await browser.close();
  await sourceServer.close();
  await finalServer.close();
}

await writeFile(resolve(OUTPUT, 'summary.json'), `${JSON.stringify({
  generatedAt: new Date().toISOString(),
  viewportCount: VIEWPORTS.length,
  routes: ROUTES,
  cases: results,
  reviewRequired: results.filter((result) => !result.comparable || result.mismatchPercent > 8)
}, null, 2)}\n`);
console.log(`Saved ${results.length * 2 + 2} screenshots and the comparison summary.`);
