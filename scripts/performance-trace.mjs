#!/usr/bin/env node

import { gzipSync } from 'node:zlib';
import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import process from 'node:process';
import { chromium } from 'playwright-core';
import { startStaticServer } from './lib/static-server.mjs';

const ROUTES = (process.env.PERF_TRACE_ROUTES || [
  'index.html',
  'treatments.html',
  'contact.html',
  'faq.html',
  'journal/why-aesthetic-care-begins-with-consultation.html'
].join(',')).split(',').filter(Boolean);

const args = Object.fromEntries(
  process.argv.slice(2).reduce((pairs, value, index, all) => {
    if (value.startsWith('--')) pairs.push([value.slice(2), all[index + 1]]);
    return pairs;
  }, [])
);
const source = resolve(args.source || 'dist');
const label = args.label || 'final';
const output = resolve('performance-reports', label, 'devtools');

function slug(route) {
  return route.replace(/index\.html$/, 'home').replace(/\.html$/, '').replaceAll('/', '--');
}

function unionLength(ranges) {
  const sorted = ranges
    .filter((range) => range.endOffset > range.startOffset)
    .sort((left, right) => left.startOffset - right.startOffset);
  let total = 0;
  let start = -1;
  let end = -1;
  for (const range of sorted) {
    if (range.startOffset > end) {
      if (end > start) total += end - start;
      start = range.startOffset;
      end = range.endOffset;
    } else {
      end = Math.max(end, range.endOffset);
    }
  }
  return total + (end > start ? end - start : 0);
}

async function readTraceStream(cdp, handle) {
  const chunks = [];
  while (true) {
    const result = await cdp.send('IO.read', { handle });
    chunks.push(result.base64Encoded ? Buffer.from(result.data, 'base64') : Buffer.from(result.data));
    if (result.eof) break;
  }
  await cdp.send('IO.close', { handle });
  return Buffer.concat(chunks);
}

async function tracePage(browser, baseUrl, route, profile) {
  const context = await browser.newContext({
    viewport: profile === 'mobile' ? { width: 390, height: 844 } : { width: 1440, height: 900 },
    deviceScaleFactor: profile === 'mobile' ? 2 : 1,
    isMobile: profile === 'mobile',
    hasTouch: profile === 'mobile',
    reducedMotion: 'no-preference'
  });
  const page = await context.newPage();
  await page.addInitScript(() => {
    window.__SF_PERF_TRACE__ = { lcp: 0, cls: 0, longTasks: [], interactions: [] };
    try {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        window.__SF_PERF_TRACE__.lcp = entries.at(-1)?.startTime || window.__SF_PERF_TRACE__.lcp;
      }).observe({ type: 'largest-contentful-paint', buffered: true });
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (!entry.hadRecentInput) window.__SF_PERF_TRACE__.cls += entry.value;
        }
      }).observe({ type: 'layout-shift', buffered: true });
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          window.__SF_PERF_TRACE__.longTasks.push({ start: entry.startTime, duration: entry.duration });
        }
      }).observe({ type: 'longtask', buffered: true });
      new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          window.__SF_PERF_TRACE__.interactions.push({
            name: entry.name,
            duration: entry.duration,
            interactionId: entry.interactionId || 0
          });
        }
      }).observe({ type: 'event', buffered: true, durationThreshold: 16 });
    } catch {
      // Unsupported observers are reported as missing rather than breaking the trace.
    }
  });

  const cdp = await context.newCDPSession(page);
  await cdp.send('Network.enable');
  await cdp.send('Profiler.enable');
  await cdp.send('Profiler.startPreciseCoverage', { callCount: true, detailed: true });
  await cdp.send('DOM.enable');
  await cdp.send('CSS.enable');
  await cdp.send('CSS.startRuleUsageTracking');
  const requests = new Map();
  cdp.on('Network.responseReceived', ({ requestId, response, type }) => {
    requests.set(requestId, { url: response.url, type, status: response.status, encodedBytes: 0 });
  });
  cdp.on('Network.loadingFinished', ({ requestId, encodedDataLength }) => {
    if (requests.has(requestId)) requests.get(requestId).encodedBytes = encodedDataLength;
  });

  await cdp.send('Tracing.start', {
    categories: [
      'devtools.timeline',
      'disabled-by-default-devtools.timeline',
      'blink.user_timing',
      'loading',
      'v8.execute'
    ].join(','),
    options: 'sampling-frequency=10000',
    transferMode: 'ReturnAsStream'
  });
  await page.goto(`${baseUrl}/${route}`, { waitUntil: 'networkidle' });
  await page.waitForTimeout(1500);

  // Exercise representative interactions while the performance trace is active.
  const menu = page.locator('[data-sf-mobile-open]').first();
  if (profile === 'mobile' && await menu.count()) {
    await menu.click();
    await page.waitForTimeout(80);
    await page.keyboard.press('Escape');
  }
  const faq = page.locator('details').first();
  if (await faq.count()) {
    await faq.locator('summary').click();
    await page.waitForTimeout(80);
  }
  const cookieSettings = page.locator('[data-consent-action="settings"]').first();
  if (await cookieSettings.count() && await cookieSettings.isVisible()) {
    await cookieSettings.click();
    await page.waitForTimeout(80);
    await page.keyboard.press('Escape');
  }

  const traceFinished = new Promise((resolveTrace) => {
    cdp.once('Tracing.tracingComplete', resolveTrace);
  });
  await cdp.send('Tracing.end');
  const { stream } = await traceFinished;
  const trace = await readTraceStream(cdp, stream);

  const jsCoverage = await cdp.send('Profiler.takePreciseCoverage');
  const cssCoverage = await cdp.send('CSS.stopRuleUsageTracking');
  await cdp.send('Profiler.stopPreciseCoverage');

  let jsTotal = 0;
  let jsUsed = 0;
  for (const script of jsCoverage.result) {
    const total = Math.max(0, ...script.functions.flatMap((fn) => fn.ranges.map((range) => range.endOffset)));
    const used = unionLength(
      script.functions.flatMap((fn) => fn.ranges.filter((range) => range.count > 0))
    );
    jsTotal += total;
    jsUsed += Math.min(total, used);
  }

  const cssBySheet = new Map();
  for (const range of cssCoverage.ruleUsage) {
    if (!cssBySheet.has(range.styleSheetId)) cssBySheet.set(range.styleSheetId, []);
    if (range.used) cssBySheet.get(range.styleSheetId).push(range);
  }
  let cssTotal = 0;
  let cssUsed = 0;
  for (const [styleSheetId, ranges] of cssBySheet) {
    try {
      const { text } = await cdp.send('CSS.getStyleSheetText', { styleSheetId });
      cssTotal += text.length;
      cssUsed += Math.min(text.length, unionLength(ranges));
    } catch {
      // Cross-origin or browser-owned stylesheets may not expose their text.
    }
  }

  const browserMetrics = await page.evaluate(() => {
    const navigation = performance.getEntriesByType('navigation')[0];
    const resources = performance.getEntriesByType('resource');
    return {
      observed: window.__SF_PERF_TRACE__,
      navigation: navigation ? {
        type: navigation.type,
        ttfbMs: navigation.responseStart,
        domContentLoadedMs: navigation.domContentLoadedEventEnd,
        loadMs: navigation.loadEventEnd,
        transferBytes: navigation.transferSize
      } : null,
      resources: resources.map((entry) => ({
        name: entry.name,
        initiatorType: entry.initiatorType,
        transferBytes: entry.transferSize,
        durationMs: entry.duration
      })),
      domNodes: document.getElementsByTagName('*').length,
      gtmLoaded: Boolean(window.google_tag_manager),
      dataLayerEvents: Array.isArray(window.dataLayer)
        ? window.dataLayer.map((item) => item?.event).filter(Boolean)
        : []
    };
  });
  const requestList = [...requests.values()];
  const result = {
    route,
    profile,
    capturedAt: new Date().toISOString(),
    ...browserMetrics,
    network: {
      requests: requestList.length,
      transferBytes: requestList.reduce((sum, request) => sum + request.encodedBytes, 0),
      largest: requestList.sort((left, right) => right.encodedBytes - left.encodedBytes).slice(0, 12)
    },
    coverage: {
      javascript: {
        totalBytes: jsTotal,
        usedBytes: jsUsed,
        unusedPercent: jsTotal ? Math.round((1 - (jsUsed / jsTotal)) * 1000) / 10 : 0
      },
      css: {
        totalBytes: cssTotal,
        usedBytes: cssUsed,
        unusedPercent: cssTotal ? Math.round((1 - (cssUsed / cssTotal)) * 1000) / 10 : 0
      }
    }
  };
  await context.close();
  return { result, trace };
}

await mkdir(output, { recursive: true });
const server = await startStaticServer(source);
const browser = await chromium.launch({ executablePath: '/usr/bin/google-chrome', headless: true });
const results = [];
try {
  for (const route of ROUTES) {
    for (const profile of ['mobile', 'desktop']) {
      process.stdout.write(`Tracing ${route} (${profile})\n`);
      const { result, trace } = await tracePage(browser, server.baseUrl, route, profile);
      results.push(result);
      await writeFile(resolve(output, `${slug(route)}--${profile}.trace.json.gz`), gzipSync(trace));
    }
  }
} finally {
  await browser.close();
  await server.close();
}
await writeFile(resolve(output, 'coverage-and-network.json'), `${JSON.stringify(results, null, 2)}\n`);
console.log(`Saved ${results.length} DevTools traces and coverage summaries to ${output}.`);
