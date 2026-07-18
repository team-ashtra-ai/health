#!/usr/bin/env node

import { createHash } from 'node:crypto';
import {
  copyFile,
  mkdir,
  readFile,
  readdir,
  rm,
  stat,
  writeFile
} from 'node:fs/promises';
import { basename, dirname, extname, relative, resolve } from 'node:path';
import { build as esbuild, transform } from 'esbuild';
import { minify as minifyHtml } from 'html-minifier-terser';
import sharp from 'sharp';

const ROOT = resolve('.');
const DIST = resolve('dist');
const BUILD_ASSETS = resolve(DIST, 'assets/build');
const GENERATED_ASSETS = resolve(DIST, 'assets/generated');
const RASTER_EXTENSIONS = new Set(['.jpeg', '.jpg', '.png', '.webp']);
const PARTIAL_FILENAMES = Object.freeze({
  topbar: 'top-bar.html',
  header: 'header.html',
  'mobile-menu': 'mobile-menu.html',
  footer: 'footer.html',
  'cookie-banner': 'cookie-banner.html',
  'floating-widgets': 'floating-widgets.html'
});
const HERO_FILES = Object.freeze({
  // The homepage's visible LCP scene is the clinic image in the source HTML.
  // Keep this aligned with the actual hero so preload never fetches an unused portrait.
  home: 'assets/hero/clinic/hero 11.png',
  about: 'assets/hero/hero-final/hero 2.png',
  mission: 'assets/hero/hero-final/hero 3.png',
  treatments: 'assets/hero/hero-final/hero 4.png',
  care: 'assets/hero/hero-final/hero 6.png',
  'thank-you': 'assets/hero/hero-final/hero 7.png',
  skin: 'assets/hero/hero-final/hero 8.png',
  laser: 'assets/hero/hero-final/hero 9.png',
  values: 'assets/hero/hero-final/hero 11.png',
  legal: 'assets/hero/hero-final/hero 13.png',
  journal: 'assets/hero/hero-final/hero 14.png',
  blog: 'assets/hero/hero-final/hero 15.png',
  testimonials: 'assets/hero/hero-final/hero 17.png',
  consultation: 'assets/hero/hero-final/hero 18.png',
  results: 'assets/hero/hero-final/hero 19.png',
  faq: 'assets/hero/hero-final/hero 20.png',
  privacy: 'assets/hero/hero-final/hero 21.png',
  cookies: 'assets/hero/hero-final/hero 22.png',
  'not-found': 'assets/hero/hero-final/hero 23.png',
  accessibility: 'assets/hero/hero-final/hero 24.png'
});

const imageMetadata = new Map();
const generatedImages = new Map();
const generatedManifest = [];

async function walk(directory, predicate = () => true) {
  const files = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    if (['.git', 'dist', 'node_modules', 'performance-reports', 'test-results', 'validation-artifacts'].includes(entry.name)) {
      continue;
    }
    const absolute = resolve(directory, entry.name);
    if (entry.isDirectory()) files.push(...await walk(absolute, predicate));
    else if (predicate(absolute)) files.push(absolute);
  }
  return files;
}

function shortHash(value) {
  return createHash('sha256').update(value).digest('hex').slice(0, 12);
}

function toPosix(value) {
  return value.replaceAll('\\', '/');
}

function publicHtmlFiles() {
  return walk(ROOT, (file) => {
    const rel = toPosix(relative(ROOT, file));
    return extname(file).toLowerCase() === '.html'
      && (/^[^/]+\.html$/.test(rel) || /^(?:pt|journal)\/[^/]+\.html$/.test(rel));
  });
}

function attrs(source) {
  return Object.fromEntries(
    [...source.matchAll(/([\w:-]+)\s*=\s*(?:"([^"]*)"|'([^']*)')/g)]
      .map((match) => [match[1].toLowerCase(), match[2] ?? match[3] ?? ''])
  );
}

function setAttribute(tag, name, value) {
  const pattern = new RegExp(`\\s${name}\\s*=\\s*(?:"[^"]*"|'[^']*')`, 'i');
  const encoded = String(value).replaceAll('&', '&amp;').replaceAll('"', '&quot;');
  if (pattern.test(tag)) return tag.replace(pattern, ` ${name}="${encoded}"`);
  return tag.replace(/\s*\/?>$/, (ending) => ` ${name}="${encoded}"${ending}`);
}

function removeAttribute(tag, name) {
  return tag.replace(new RegExp(`\\s${name}\\s*=\\s*(?:"[^"]*"|'[^']*')`, 'gi'), '');
}

function isRelativeSitePath(value) {
  return Boolean(value)
    && !value.startsWith('#')
    && !value.startsWith('/')
    && !value.startsWith('?')
    && !/^[a-z][a-z\d+.-]*:/i.test(value)
    && !value.startsWith('../');
}

function prefixPartialPaths(fragment, rootPrefix) {
  if (!rootPrefix) return fragment;
  return fragment.replace(
    /\b(href|src|action)=(["'])([^"']+)\2/gi,
    (whole, attribute, quote, value) => (
      isRelativeSitePath(value)
        ? `${attribute}=${quote}${rootPrefix}${value}${quote}`
        : whole
    )
  );
}

function setLinkHrefByLanguage(fragment, language, href) {
  const pattern = new RegExp(`<a\\b([^>]*\\bdata-lang=(["'])${language}\\2[^>]*)>`, 'i');
  return fragment.replace(pattern, (whole) => setAttribute(whole, 'href', href));
}

function addTranslateNo(fragment) {
  return fragment.replace(/^(\s*<[\w:-]+\b)(?![^>]*\btranslate=)/, '$1 translate="no"');
}

function pagePair(pagePairs, relativePage, portuguese) {
  const filename = basename(relativePage);
  return pagePairs.find((pair) => {
    const candidate = portuguese ? pair['pt-BR'] : pair.en;
    return typeof candidate === 'string' && basename(candidate) === filename;
  });
}

async function composePartials(html, relativePage, pagePairs) {
  const portuguese = relativePage.startsWith('pt/');
  const depth = relativePage.split('/').length - 1;
  const rootPrefix = portuguese ? '' : '../'.repeat(depth);
  const pair = pagePair(pagePairs, relativePage, portuguese);
  const partialDirectory = resolve(ROOT, 'partials', portuguese ? 'pt-BR' : '');
  const pattern = /<template\b[^>]*data-sf-partial=(["'])([^"']+)\1[^>]*>\s*<\/template>/gi;
  const matches = [...html.matchAll(pattern)];
  let output = html;

  for (const match of matches) {
    const name = match[2];
    const filename = PARTIAL_FILENAMES[name];
    if (!filename) throw new Error(`Unknown partial "${name}" in ${relativePage}.`);
    let fragment = await readFile(resolve(partialDirectory, filename), 'utf8');
    fragment = fragment.replace(/<script\b[^>]*data-id=["']five-server["'][^>]*>\s*<\/script>/gi, '');
    fragment = prefixPartialPaths(fragment, rootPrefix);
    if (name === 'topbar') {
      if (!pair) throw new Error(`No language page pair found for ${relativePage}.`);
      const englishHref = portuguese ? `../${pair.en}` : `${rootPrefix}${pair.en}`;
      const portugueseHref = portuguese ? basename(pair['pt-BR']) : `${rootPrefix}${pair['pt-BR']}`;
      fragment = setLinkHrefByLanguage(fragment, 'en', englishHref);
      fragment = setLinkHrefByLanguage(fragment, 'pt', portugueseHref);
    }
    fragment = addTranslateNo(fragment.trim());
    output = output.replace(match[0], fragment);
  }
  return output;
}

async function metadataFor(source) {
  if (!imageMetadata.has(source)) {
    imageMetadata.set(source, await sharp(source, { animated: false }).metadata());
  }
  return imageMetadata.get(source);
}

async function generateImage(source, requestedWidth, format, quality) {
  const metadata = await metadataFor(source);
  const width = Math.max(1, Math.min(metadata.width || requestedWidth, requestedWidth));
  const key = `${source}|${width}|${format}|${quality}`;
  if (generatedImages.has(key)) return generatedImages.get(key);
  const sourceBuffer = await readFile(source);
  const hash = shortHash(Buffer.concat([sourceBuffer, Buffer.from(`|${width}|${format}|${quality}`)]));
  const stem = basename(source, extname(source))
    .normalize('NFKD')
    .replace(/[^\w-]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .toLowerCase()
    .slice(0, 58) || 'image';
  const outputRelative = `assets/generated/${stem}-${width}-${hash}.${format}`;
  const output = resolve(DIST, outputRelative);
  await mkdir(dirname(output), { recursive: true });
  let pipeline = sharp(source, { animated: false })
    .rotate()
    .resize({ width, withoutEnlargement: true, fit: 'inside' });
  if (format === 'avif') {
    pipeline = pipeline.avif({ quality, effort: 4, chromaSubsampling: '4:2:0' });
  } else {
    pipeline = pipeline.webp({ quality, effort: 4, smartSubsample: true });
  }
  await pipeline.toFile(output);
  const outputStat = await stat(output);
  const result = {
    relative: outputRelative,
    width,
    bytes: outputStat.size,
    source: toPosix(relative(ROOT, source)),
    format
  };
  generatedImages.set(key, result);
  generatedManifest.push(result);
  return result;
}

function pageRelativeAsset(relativePage, assetRelative) {
  const depth = relativePage.split('/').length - 1;
  return `${'../'.repeat(depth)}${assetRelative}`;
}

function imageWidths(metadata, declaredWidth) {
  const sourceWidth = metadata.width || declaredWidth || 960;
  const renderedWidth = declaredWidth || Math.min(sourceWidth, 840);
  const maximum = Math.min(sourceWidth, Math.max(renderedWidth * 2, renderedWidth));
  if (renderedWidth <= 128) return [Math.min(sourceWidth, Math.max(renderedWidth * 2, 64))];
  return [...new Set(
    [320, 480, 720, 960, 1280, 1600, Math.round(maximum)]
      .filter((width) => width <= maximum && width <= sourceWidth)
  )].sort((left, right) => left - right);
}

async function optimizeHtmlImages(html, relativePage) {
  const matches = [...html.matchAll(/<img\b[^>]*>/gi)];
  let output = html;
  for (const match of matches) {
    const tag = match[0];
    const imageAttrs = attrs(tag);
    const sourceValue = imageAttrs.src;
    if (!sourceValue || /^(?:data:|https?:|\/\/)/i.test(sourceValue)) continue;
    const cleanSource = decodeURIComponent(sourceValue.split(/[?#]/, 1)[0]);
    const source = resolve(ROOT, dirname(relativePage), cleanSource);
    if (!source.startsWith(resolve(ROOT, 'assets')) || !RASTER_EXTENSIONS.has(extname(source).toLowerCase())) continue;
    let sourceStat;
    try {
      sourceStat = await stat(source);
    } catch {
      continue;
    }
    if (!sourceStat.isFile()) continue;

    const metadata = await metadataFor(source);
    const declaredWidth = Number(imageAttrs.width) || metadata.width || 0;
    const widths = imageWidths(metadata, declaredWidth);
    const webp = [];
    const avif = [];
    for (const width of widths) {
      webp.push(await generateImage(source, width, 'webp', declaredWidth <= 128 ? 76 : 72));
      avif.push(await generateImage(source, width, 'avif', declaredWidth <= 128 ? 58 : 52));
    }
    const largestWebp = webp.at(-1);
    let optimizedTag = setAttribute(tag, 'src', pageRelativeAsset(relativePage, largestWebp.relative));
    optimizedTag = removeAttribute(optimizedTag, 'srcset');
    optimizedTag = removeAttribute(optimizedTag, 'sizes');
    if (!imageAttrs.loading) {
      optimizedTag = setAttribute(optimizedTag, 'loading', 'lazy');
    }
    if (imageAttrs.loading !== 'eager') {
      optimizedTag = setAttribute(optimizedTag, 'decoding', 'async');
    }
    if (widths.length === 1) {
      output = output.replace(tag, optimizedTag);
      continue;
    }
    const sizes = declaredWidth <= 128
      ? `${declaredWidth}px`
      : `(max-width: 47.999rem) calc(100vw - 2rem), (max-width: 74.999rem) 50vw, ${Math.min(declaredWidth, 840)}px`;
    const avifSet = avif
      .map((item) => `${pageRelativeAsset(relativePage, item.relative)} ${item.width}w`)
      .join(', ');
    const webpSet = webp
      .map((item) => `${pageRelativeAsset(relativePage, item.relative)} ${item.width}w`)
      .join(', ');
    const picture = `<picture><source type="image/avif" srcset="${avifSet}" sizes="${sizes}">`
      + `<source type="image/webp" srcset="${webpSet}" sizes="${sizes}">${optimizedTag}</picture>`;
    output = output.replace(tag, picture);
  }
  return output;
}

function cssTargetWidth(source) {
  const rel = toPosix(relative(ROOT, source));
  if (rel.includes('/hero/hero-final/')) return 1600;
  if (rel.includes('site-panorama')) return 1920;
  if (rel.includes('/cta-concepts/')) return 960;
  if (rel.includes('/icons/')) return 480;
  if (rel.includes('/brand/')) return 960;
  return 1440;
}

async function optimizeCssImages(css) {
  const matches = [...css.matchAll(/url\(\s*(['"]?)([^'")]+)\1\s*\)/gi)];
  let output = css;
  for (const match of matches) {
    const value = match[2];
    if (/^(?:data:|https?:|#)/i.test(value) || extname(value).toLowerCase() === '.svg') continue;
    const source = value.startsWith('/')
      ? resolve(ROOT, value.slice(1))
      : resolve(ROOT, 'css', decodeURIComponent(value));
    if (!source.startsWith(resolve(ROOT, 'assets')) || !RASTER_EXTENSIONS.has(extname(source).toLowerCase())) continue;
    try {
      const optimized = await generateImage(source, cssTargetWidth(source), 'webp', 70);
      output = output.replace(match[0], `url("../generated/${basename(optimized.relative)}")`);
    } catch {
      // Keep the authored URL if an unusual asset cannot be decoded.
    }
  }

  const mobileRules = [];
  for (const [page, sourceRelative] of Object.entries(HERO_FILES)) {
    const mobile = await generateImage(resolve(ROOT, sourceRelative), 900, 'webp', 68);
    mobileRules.push(
      `.sf-page[data-page="${page}"] [data-pattern="hero"]{`
      + `--hero-scene-image:url("../generated/${basename(mobile.relative)}")}`
    );
  }
  output += `\n@layer performance{`
    + `.sf-main>.sf-section[data-track-section]:not([data-pattern="hero"]){`
    + `content-visibility:auto;contain-intrinsic-block-size:auto 52rem}`
    + `@media(max-width:47.999rem){${mobileRules.join('')}`
    + `.sf-page[data-page="home"] :is(#decision-flow,#treatment-pathways,#responsible-pauses,#meet-franciele)::before,`
    + `.sf-page[data-page="home"] :is(#decision-flow,#treatment-pathways,#responsible-pauses,#meet-franciele)::after{`
    + `background-image:none!important}}`
    + `@media print{.sf-main>.sf-section{content-visibility:visible!important;contain:none!important}}`
    + `}`;
  return output;
}

async function buildCss() {
  const source = await readFile(resolve(ROOT, 'css/site.css'), 'utf8');
  const optimized = await optimizeCssImages(source);
  const result = await transform(optimized, {
    loader: 'css',
    minify: true,
    target: 'chrome100'
  });
  const hash = shortHash(result.code);
  const relativePath = `assets/build/site.${hash}.css`;
  await writeFile(resolve(DIST, relativePath), result.code);
  return relativePath;
}

async function buildJavascript() {
  const mainTemporary = resolve(BUILD_ASSETS, 'main.tmp.js');
  await esbuild({
    entryPoints: [resolve(ROOT, 'js/main.js')],
    outfile: mainTemporary,
    bundle: true,
    minify: true,
    format: 'esm',
    target: 'es2020',
    legalComments: 'none'
  });
  const mainCode = await readFile(mainTemporary, 'utf8');
  const mainRelative = `assets/build/main.${shortHash(mainCode)}.js`;
  await writeFile(resolve(DIST, mainRelative), mainCode);
  await rm(mainTemporary);

  const measurementSources = await Promise.all([
    'js/analytics-config.js',
    'js/consent-manager.js',
    'js/analytics.js'
  ].map((file) => readFile(resolve(ROOT, file), 'utf8')));
  const measurement = await transform(measurementSources.join('\n;\n'), {
    loader: 'js',
    minify: true,
    target: 'es2020',
    legalComments: 'none'
  });
  const measurementRelative = `assets/build/measurement.${shortHash(measurement.code)}.js`;
  await writeFile(resolve(DIST, measurementRelative), measurement.code);
  return { mainRelative, measurementRelative };
}

function replaceBuiltResources(html, relativePage, resources) {
  const cssHref = pageRelativeAsset(relativePage, resources.css);
  const mainSrc = pageRelativeAsset(relativePage, resources.main);
  const measurementSrc = pageRelativeAsset(relativePage, resources.measurement);
  let output = html.replace(
    /<link\b(?=[^>]*\brel=(["'])stylesheet\1)(?=[^>]*\bhref=(["'])(?:\.\.\/)*css\/site\.css\2)[^>]*>/i,
    `<link rel="stylesheet" href="${cssHref}">`
  );
  output = output.replace(
    /(?:\s*<script\b[^>]*\bsrc=(["'])(?:\.\.\/)*js\/(?:analytics-config|consent-manager|analytics)\.js\1[^>]*>\s*<\/script>){3}/i,
    `\n<script src="${measurementSrc}" defer></script>`
  );
  output = output.replace(
    /<script\b(?=[^>]*\btype=(["'])module\1)(?=[^>]*\bsrc=(["'])(?:\.\.\/)*js\/main\.js\2)[^>]*>\s*<\/script>/i,
    `<script type="module" src="${mainSrc}"></script>`
  );
  return output;
}

async function heroPreloads(relativePage, html) {
  const page = html.match(/<body\b[^>]*\bdata-page=(["'])([^"']+)\1/i)?.[2];
  const sourceRelative = HERO_FILES[page];
  if (!sourceRelative) return '';
  const source = resolve(ROOT, sourceRelative);
  const mobile = await generateImage(source, 900, 'webp', 68);
  const desktop = await generateImage(source, 1600, 'webp', 70);
  return `\n<!-- Performance: preload only the page's visible hero scene; other imagery remains demand-loaded. -->`
    + `\n<link rel="preload" as="image" type="image/webp" media="(max-width: 47.999rem)" `
    + `href="${pageRelativeAsset(relativePage, mobile.relative)}" fetchpriority="high">`
    + `\n<link rel="preload" as="image" type="image/webp" media="(min-width: 48rem)" `
    + `href="${pageRelativeAsset(relativePage, desktop.relative)}" fetchpriority="high">`;
}

async function minifyPage(html) {
  return minifyHtml(html, {
    collapseWhitespace: 'conservative',
    collapseBooleanAttributes: true,
    decodeEntities: false,
    keepClosingSlash: true,
    minifyCSS: false,
    minifyJS: false,
    preserveLineBreaks: true,
    removeAttributeQuotes: false,
    removeComments: false,
    removeEmptyAttributes: false,
    sortAttributes: false,
    sortClassName: false
  });
}

async function copyReferencedAssets() {
  const files = await walk(DIST, (file) => ['.html', '.css', '.json', '.webmanifest'].includes(extname(file).toLowerCase()));
  const references = new Set();
  for (const file of files) {
    const content = await readFile(file, 'utf8');
    for (const match of content.matchAll(/(?:https:\/\/www\.francielesofiati\.com\/)?(?:\.\.\/)*assets\/[^"'()<>\s,}]+/g)) {
      const normalized = decodeURIComponent(match[0])
        .replace('https://www.francielesofiati.com/', '')
        .replace(/^(?:\.\.\/)+/, '');
      references.add(normalized);
    }
  }
  for (const asset of references) {
    if (asset.startsWith('assets/build/') || asset.startsWith('assets/generated/')) continue;
    const source = resolve(ROOT, asset);
    try {
      if (!(await stat(source)).isFile()) continue;
    } catch {
      continue;
    }
    const destination = resolve(DIST, asset);
    await mkdir(dirname(destination), { recursive: true });
    await copyFile(source, destination);
  }
}

async function copySupportFiles() {
  for (const file of ['robots.txt', 'sitemap.xml', 'site.webmanifest', 'favicon.ico']) {
    await copyFile(resolve(ROOT, file), resolve(DIST, file));
  }
  await mkdir(resolve(DIST, 'data'), { recursive: true });
  for (const file of ['page-pairs.json', 'shared-site.json', 'forms.json']) {
    try {
      await copyFile(resolve(ROOT, 'data', file), resolve(DIST, 'data', file));
    } catch {
      // Only copy data files that exist in this repository.
    }
  }
  const headers = [
    '/*',
    '  Cache-Control: public, max-age=0, must-revalidate',
    '  X-Content-Type-Options: nosniff',
    '  Referrer-Policy: strict-origin-when-cross-origin',
    '',
    '/assets/build/*',
    '  Cache-Control: public, max-age=31536000, immutable',
    '',
    '/assets/generated/*',
    '  Cache-Control: public, max-age=31536000, immutable',
    '',
    '/assets/favicons/*',
    '  Cache-Control: public, max-age=604800, stale-while-revalidate=86400',
    '',
    '/assets/social/*',
    '  Cache-Control: public, max-age=604800, stale-while-revalidate=86400',
    '',
    '/data/*',
    '  Cache-Control: public, max-age=0, must-revalidate',
    '',
    '/thank-you.html',
    '  Cache-Control: private, no-store',
    '',
    '/pt/thank-you.html',
    '  Cache-Control: private, no-store',
    ''
  ].join('\n');
  await writeFile(resolve(DIST, '_headers'), headers);
}

async function main() {
  await rm(DIST, { recursive: true, force: true });
  await mkdir(BUILD_ASSETS, { recursive: true });
  await mkdir(GENERATED_ASSETS, { recursive: true });
  const pagePairs = JSON.parse(await readFile(resolve(ROOT, 'data/page-pairs.json'), 'utf8')).pages;
  const [css, javascript, pages] = await Promise.all([
    buildCss(),
    buildJavascript(),
    publicHtmlFiles()
  ]);
  const resources = {
    css,
    main: javascript.mainRelative,
    measurement: javascript.measurementRelative
  };

  for (const page of pages.sort()) {
    const relativePage = toPosix(relative(ROOT, page));
    let html = await readFile(page, 'utf8');
    html = await composePartials(html, relativePage, pagePairs);
    html = await optimizeHtmlImages(html, relativePage);
    html = replaceBuiltResources(html, relativePage, resources);
    html = html.replace('</head>', `${await heroPreloads(relativePage, html)}\n</head>`);
    html = await minifyPage(html);
    const destination = resolve(DIST, relativePage);
    await mkdir(dirname(destination), { recursive: true });
    await writeFile(destination, `${html}\n`);
  }

  await copySupportFiles();
  await copyReferencedAssets();
  const buildManifest = {
    generatedAt: new Date().toISOString(),
    sourcePages: pages.length,
    resources,
    generatedImages: generatedManifest.length,
    generatedImageBytes: generatedManifest.reduce((sum, image) => sum + image.bytes, 0),
    sourceCommit: process.env.GITHUB_SHA || null,
    notes: [
      'Shared partials are composed into HTML at build time.',
      'GA4 remains delivered only through consent-gated GTM.',
      'Readable source files remain outside dist; do not edit dist directly.'
    ]
  };
  await writeFile(resolve(DIST, '.performance-build.json'), `${JSON.stringify(buildManifest, null, 2)}\n`);
  process.stdout.write(
    `Built ${pages.length} pages with ${generatedManifest.length} responsive/optimized image files.\n`
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
