#!/usr/bin/env node

import { readdir, readFile, stat, writeFile } from 'node:fs/promises';
import { dirname, extname, relative, resolve } from 'node:path';
import sharp from 'sharp';

const ROOT = resolve('.');
const RASTER_EXTENSIONS = new Set(['.avif', '.gif', '.jpeg', '.jpg', '.png', '.webp']);
const EXCLUDED_DIRECTORIES = new Set([
  '.git',
  'dist',
  'node_modules',
  'performance-reports',
  'test-results',
  'validation-artifacts',
  'visual-regression'
]);

async function walk(directory, predicate = () => true) {
  const found = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (entry.isDirectory() && EXCLUDED_DIRECTORIES.has(entry.name)) continue;
    const absolute = resolve(directory, entry.name);
    if (entry.isDirectory()) found.push(...await walk(absolute, predicate));
    else if (predicate(absolute)) found.push(absolute);
  }
  return found;
}

function attributes(source) {
  return Object.fromEntries(
    [...source.matchAll(/([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g)]
      .map((match) => [match[1].toLowerCase(), match[2] ?? match[3] ?? ''])
  );
}

function localAssetPath(pagePath, source) {
  if (!source || /^(?:[a-z][a-z\d+.-]*:|\/\/|data:|#)/i.test(source)) return null;
  const clean = decodeURIComponent(source.split(/[?#]/, 1)[0]);
  const absolute = resolve(dirname(pagePath), clean);
  return absolute.startsWith(resolve(ROOT, 'assets')) ? absolute : null;
}

async function usagesByAsset() {
  const usages = new Map();
  const htmlFiles = await walk(ROOT, (file) => extname(file).toLowerCase() === '.html');
  for (const page of htmlFiles) {
    const html = await readFile(page, 'utf8');
    for (const match of html.matchAll(/<img\b([^>]*)>/gi)) {
      const attrs = attributes(match[1]);
      const asset = localAssetPath(page, attrs.src);
      if (!asset) continue;
      const pageName = relative(ROOT, page).replaceAll('\\', '/');
      const beforeImage = html.slice(0, match.index);
      const heroStart = beforeImage.lastIndexOf('data-pattern="hero"');
      const heroEnd = beforeImage.lastIndexOf('</section>');
      const usage = {
        page: pageName,
        context: heroStart > heroEnd || attrs.loading === 'eager' ? 'above fold candidate' : 'below fold',
        display: attrs.width && attrs.height ? `${attrs.width}x${attrs.height}` : 'not declared',
        purpose: attrs.alt ? 'meaningful' : 'decorative',
        loading: attrs.loading || 'browser default'
      };
      if (!usages.has(asset)) usages.set(asset, []);
      usages.get(asset).push(usage);
    }
  }

  const cssFiles = await walk(resolve(ROOT, 'css'), (file) => extname(file).toLowerCase() === '.css');
  for (const cssFile of cssFiles) {
    const css = await readFile(cssFile, 'utf8');
    for (const match of css.matchAll(/url\(\s*(['"]?)([^'")]+)\1\s*\)/gi)) {
      const source = match[2];
      if (/^(?:data:|https?:|#)/i.test(source)) continue;
      const asset = resolve(dirname(cssFile), decodeURIComponent(source));
      if (!asset.startsWith(resolve(ROOT, 'assets'))) continue;
      if (!usages.has(asset)) usages.set(asset, []);
      usages.get(asset).push({
        page: relative(ROOT, cssFile).replaceAll('\\', '/'),
        context: 'CSS-dependent',
        display: 'CSS-dependent',
        purpose: 'decorative unless surrounding content establishes meaning',
        loading: 'CSS resource discovery'
      });
    }
  }
  return usages;
}

function responsiveWidths(width, usage) {
  if (!Number.isFinite(width)) return [];
  const declaredWidths = usage
    .map((item) => Number(item.display.split('x', 1)[0]))
    .filter(Number.isFinite);
  const maximumDisplay = declaredWidths.length ? Math.max(...declaredWidths) : width;
  const upper = Math.min(width, Math.max(maximumDisplay * 2, 640));
  return [320, 480, 640, 768, 960, 1280, 1600, 1920]
    .filter((candidate) => candidate < upper)
    .concat(Math.round(upper))
    .filter((value, index, values) => value > 0 && values.indexOf(value) === index);
}

export async function createAssetInventory() {
  const usageMap = await usagesByAsset();
  const files = await walk(resolve(ROOT, 'assets'), (file) => RASTER_EXTENSIONS.has(extname(file).toLowerCase()));
  const images = [];
  for (const file of files) {
    const fileStat = await stat(file);
    let metadata = {};
    try {
      metadata = await sharp(file, { animated: false }).metadata();
    } catch {
      metadata = {};
    }
    const usage = usageMap.get(file) || [];
    images.push({
      source: relative(ROOT, file).replaceAll('\\', '/'),
      format: metadata.format || extname(file).slice(1).toLowerCase(),
      width: metadata.width || null,
      height: metadata.height || null,
      bytes: fileStat.size,
      transparency: Boolean(metadata.hasAlpha),
      pagesUsed: [...new Set(usage.map((item) => item.page))],
      displayDimensions: [...new Set(usage.map((item) => item.display))],
      foldContext: [...new Set(usage.map((item) => item.context))],
      purpose: [...new Set(usage.map((item) => item.purpose))],
      loading: [...new Set(usage.map((item) => item.loading))],
      candidateFormats: metadata.format === 'avif'
        ? ['AVIF']
        : metadata.format === 'webp'
          ? ['WebP', 'AVIF where measured smaller']
          : ['AVIF', 'WebP', 'retain source fallback where needed'],
      responsiveWidths: responsiveWidths(metadata.width, usage),
      referenced: usage.length > 0
    });
  }
  images.sort((left, right) => right.bytes - left.bytes);
  return {
    generatedAt: new Date().toISOString(),
    imageCount: images.length,
    totalBytes: images.reduce((sum, image) => sum + image.bytes, 0),
    referencedImageCount: images.filter((image) => image.referenced).length,
    unreferencedImageCount: images.filter((image) => !image.referenced).length,
    images
  };
}

async function main() {
  const inventory = await createAssetInventory();
  await writeFile(
    resolve('performance-reports/asset-inventory.json'),
    `${JSON.stringify(inventory, null, 2)}\n`
  );
  process.stdout.write(
    `Inventoried ${inventory.imageCount} raster assets `
    + `(${(inventory.totalBytes / 1024 / 1024).toFixed(1)} MB).\n`
  );
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(new URL(import.meta.url).pathname)) {
  main().catch((error) => {
    console.error(error);
    process.exitCode = 1;
  });
}
