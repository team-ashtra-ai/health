#!/usr/bin/env node

import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, resolve } from 'node:path';
import { spawn } from 'node:child_process';
import process from 'node:process';
import { startStaticServer } from './lib/static-server.mjs';

const REPRESENTATIVE_ROUTES = Object.freeze([
  'index.html',
  'about.html',
  'treatments.html',
  'skin.html',
  'laser.html',
  'consultation.html',
  'contact.html',
  'faq.html',
  'journal.html',
  'journal/why-aesthetic-care-begins-with-consultation.html',
  'results.html',
  'care.html',
  'mission.html',
  'thank-you.html'
]);

function parseArguments(argv) {
  const parsed = {
    source: '.',
    label: 'baseline',
    profile: 'both',
    runs: Number(process.env.PERF_RUNS || 5),
    routes: process.env.PERF_ROUTES
      ? process.env.PERF_ROUTES.split(',').map((value) => value.trim()).filter(Boolean)
      : [...REPRESENTATIVE_ROUTES]
  };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--source') parsed.source = argv[++index];
    else if (value === '--label') parsed.label = argv[++index];
    else if (value === '--profile') parsed.profile = argv[++index];
    else if (value === '--runs') parsed.runs = Number(argv[++index]);
    else if (value === '--routes') parsed.routes = argv[++index].split(',').filter(Boolean);
  }
  if (!['baseline', 'final'].includes(parsed.label)) throw new Error('--label must be baseline or final.');
  if (!['mobile', 'desktop', 'both'].includes(parsed.profile)) {
    throw new Error('--profile must be mobile, desktop or both.');
  }
  if (!Number.isInteger(parsed.runs) || parsed.runs < 1) throw new Error('--runs must be a positive integer.');
  return parsed;
}

function slug(route) {
  return route.replace(/index\.html$/, 'home').replace(/\.html$/, '').replaceAll('/', '--');
}

function runCommand(command, args, options = {}) {
  return new Promise((resolveRun, reject) => {
    const child = spawn(command, args, {
      ...options,
      stdio: ['ignore', 'pipe', 'pipe']
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', reject);
    child.on('close', (code) => {
      if (code === 0) resolveRun({ stdout, stderr });
      else reject(new Error(`${command} exited ${code}\n${stdout}\n${stderr}`));
    });
  });
}

function auditValue(report, id, fallback = null) {
  const value = report.audits?.[id]?.numericValue;
  return Number.isFinite(value) ? value : fallback;
}

function score(report, category) {
  const value = report.categories?.[category]?.score;
  return Number.isFinite(value) ? Math.round(value * 100) : null;
}

function percentile(values, position = 0.5) {
  const clean = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!clean.length) return null;
  const index = (clean.length - 1) * position;
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  if (lower === upper) return clean[lower];
  return clean[lower] + (clean[upper] - clean[lower]) * (index - lower);
}

function statistics(runs, key) {
  const values = runs.map((run) => run[key]).filter(Number.isFinite);
  if (!values.length) return { median: null, min: null, max: null, variance: null };
  const mean = values.reduce((sum, value) => sum + value, 0) / values.length;
  return {
    median: percentile(values),
    min: Math.min(...values),
    max: Math.max(...values),
    variance: values.reduce((sum, value) => sum + ((value - mean) ** 2), 0) / values.length
  };
}

function networkSummary(report) {
  const items = report.audits?.['network-requests']?.details?.items || [];
  const buckets = {
    script: 0,
    stylesheet: 0,
    image: 0,
    font: 0,
    document: 0,
    other: 0,
    thirdParty: 0
  };
  const localhost = new URL(report.finalDisplayedUrl || report.finalUrl).origin;
  for (const item of items) {
    const size = item.transferSize || 0;
    const type = String(item.resourceType || '').toLowerCase();
    if (type === 'script') buckets.script += size;
    else if (type === 'stylesheet') buckets.stylesheet += size;
    else if (type === 'image') buckets.image += size;
    else if (type === 'font') buckets.font += size;
    else if (type === 'document') buckets.document += size;
    else buckets.other += size;
    try {
      if (new URL(item.url).origin !== localhost) buckets.thirdParty += size;
    } catch {
      // Lighthouse may report synthetic URLs; they stay in the "other" bucket.
    }
  }
  return {
    requestCount: items.length,
    totalTransferBytes: items.reduce((sum, item) => sum + (item.transferSize || 0), 0),
    ...buckets,
    largestResources: [...items]
      .sort((left, right) => (right.transferSize || 0) - (left.transferSize || 0))
      .slice(0, 10)
      .map((item) => ({
        url: item.url,
        resourceType: item.resourceType,
        transferBytes: item.transferSize || 0
      }))
  };
}

function itemCount(report, id) {
  return report.audits?.[id]?.details?.items?.length || 0;
}

function extractRun(report, rawReport) {
  const network = networkSummary(report);
  const lcpNode = report.audits?.['largest-contentful-paint-element']?.details?.items?.[0]?.items?.[0]?.node
    || report.audits?.['largest-contentful-paint-element']?.details?.items?.[0]?.node
    || null;
  const unusedCss = report.audits?.['unused-css-rules']?.details?.overallSavingsBytes
    || report.audits?.['unused-css-rules']?.details?.items?.reduce(
      (sum, item) => sum + (item.wastedBytes || 0), 0
    )
    || 0;
  const unusedJs = report.audits?.['unused-javascript']?.details?.overallSavingsBytes
    || report.audits?.['unused-javascript']?.details?.items?.reduce(
      (sum, item) => sum + (item.wastedBytes || 0), 0
    )
    || 0;
  return {
    performance: score(report, 'performance'),
    accessibility: score(report, 'accessibility'),
    bestPractices: score(report, 'best-practices'),
    seo: score(report, 'seo'),
    lcpMs: auditValue(report, 'largest-contentful-paint'),
    cls: auditValue(report, 'cumulative-layout-shift'),
    tbtMs: auditValue(report, 'total-blocking-time'),
    fcpMs: auditValue(report, 'first-contentful-paint'),
    speedIndexMs: auditValue(report, 'speed-index'),
    ttfbMs: auditValue(report, 'server-response-time'),
    mainThreadMs: auditValue(report, 'mainthread-work-breakdown'),
    longTaskCount: itemCount(report, 'long-tasks'),
    domNodeCount: auditValue(report, 'dom-size'),
    unusedCssBytes: unusedCss,
    unusedJsBytes: unusedJs,
    renderBlockingCount: itemCount(report, 'render-blocking-resources'),
    layoutShiftItemCount: itemCount(report, 'cls-culprits'),
    imageSizingProblemCount: itemCount(report, 'uses-responsive-images')
      + itemCount(report, 'uses-optimized-images')
      + itemCount(report, 'unsized-images'),
    cachePolicyProblemCount: itemCount(report, 'uses-long-cache-ttl'),
    redirectCount: itemCount(report, 'redirects'),
    lcpElement: lcpNode
      ? { selector: lcpNode.selector || null, snippet: lcpNode.snippet || null }
      : null,
    ...network,
    lighthouseVersion: report.lighthouseVersion,
    fetchTime: report.fetchTime,
    finalUrl: report.finalDisplayedUrl || report.finalUrl,
    rawReport
  };
}

function summarizeGroup(group) {
  const metricKeys = [
    'performance',
    'accessibility',
    'bestPractices',
    'seo',
    'lcpMs',
    'cls',
    'tbtMs',
    'fcpMs',
    'speedIndexMs',
    'ttfbMs',
    'totalTransferBytes',
    'requestCount',
    'script',
    'stylesheet',
    'image',
    'font',
    'thirdParty',
    'mainThreadMs',
    'longTaskCount',
    'domNodeCount',
    'unusedCssBytes',
    'unusedJsBytes'
  ];
  return Object.fromEntries(metricKeys.map((key) => [key, statistics(group.runs, key)]));
}

function formatNumber(value, digits = 0) {
  if (!Number.isFinite(value)) return 'n/a';
  return value.toFixed(digits);
}

function markdownReport(result) {
  const lines = [
    `# Performance ${result.label === 'baseline' ? 'Baseline' : 'Final'} Report`,
    '',
    `Generated: ${result.generatedAt}`,
    '',
    `Source: \`${result.source}\``,
    '',
    `Chrome: ${result.environment.chromeVersion || 'unknown'}`,
    '',
    `Lighthouse: ${result.environment.lighthouseVersion || 'unknown'}`,
    '',
    `Runs per route/profile: ${result.runsPerRoute}`,
    '',
    '> These are local laboratory measurements. They do not claim deployed PageSpeed or Search Console field performance.',
    '',
    '| Route | Profile | Performance median (min–max) | LCP ms | CLS | TBT ms | FCP ms | Transfer KB | Requests |',
    '|---|---:|---:|---:|---:|---:|---:|---:|---:|'
  ];
  for (const group of result.groups) {
    const summary = group.summary;
    lines.push(
      `| ${group.route} | ${group.profile} | ${formatNumber(summary.performance.median)} `
      + `(${formatNumber(summary.performance.min)}–${formatNumber(summary.performance.max)}) `
      + `| ${formatNumber(summary.lcpMs.median)} | ${formatNumber(summary.cls.median, 3)} `
      + `| ${formatNumber(summary.tbtMs.median)} | ${formatNumber(summary.fcpMs.median)} `
      + `| ${formatNumber(summary.totalTransferBytes.median / 1024)} `
      + `| ${formatNumber(summary.requestCount.median)} |`
    );
  }
  lines.push('', '## Environment and limitations', '');
  lines.push('- Cold-cache Lighthouse navigation with simulated throttling and a clean headless Chrome profile.');
  lines.push('- Local responses use gzip for compressible resources and revalidation caching for fair source/build comparison.');
  lines.push('- The production domain did not resolve during this audit, so production PSI and CrUX data are not included.');
  lines.push('- Analytics IDs remain placeholders; the performance cost of a future published GTM container cannot yet be measured.');
  return `${lines.join('\n')}\n`;
}

async function main() {
  const args = parseArguments(process.argv.slice(2));
  const source = resolve(args.source);
  const outputRoot = resolve('performance-reports', args.label);
  await mkdir(outputRoot, { recursive: true });
  const server = await startStaticServer(source);
  const profiles = args.profile === 'both' ? ['mobile', 'desktop'] : [args.profile];
  const groups = [];
  let chromeVersion = null;
  let lighthouseVersion = null;

  try {
    const chromeResult = await runCommand('/usr/bin/google-chrome', ['--version']);
    chromeVersion = chromeResult.stdout.trim();
    const lighthouseResult = await runCommand(resolve('node_modules/.bin/lighthouse'), ['--version']);
    lighthouseVersion = lighthouseResult.stdout.trim();

    for (const route of args.routes) {
      for (const profile of profiles) {
        const group = { route, profile, runs: [] };
        for (let runNumber = 1; runNumber <= args.runs; runNumber += 1) {
          const reportName = `${slug(route)}--${profile}--run-${runNumber}.json`;
          const reportPath = resolve(outputRoot, reportName);
          const url = `${server.baseUrl}/${route}`;
          const lighthouseArgs = [
            url,
            '--quiet',
            '--output=json',
            `--output-path=${reportPath}`,
            '--only-categories=performance,accessibility,best-practices,seo',
            '--throttling-method=simulate',
            '--chrome-flags=--headless=new --no-sandbox --disable-dev-shm-usage --disable-background-networking'
          ];
          if (profile === 'desktop') lighthouseArgs.push('--preset=desktop');
          process.stdout.write(`[${args.label}] ${route} ${profile} run ${runNumber}/${args.runs}\n`);
          await runCommand(resolve('node_modules/.bin/lighthouse'), lighthouseArgs, {
            env: { ...process.env, CHROME_PATH: '/usr/bin/google-chrome' }
          });
          const report = JSON.parse(await readFile(reportPath, 'utf8'));
          group.runs.push(extractRun(report, `performance-reports/${args.label}/${reportName}`));
        }
        group.summary = summarizeGroup(group);
        groups.push(group);
      }
    }
  } finally {
    await server.close();
  }

  const result = {
    schemaVersion: 1,
    label: args.label,
    generatedAt: new Date().toISOString(),
    source,
    runsPerRoute: args.runs,
    environment: {
      platform: process.platform,
      node: process.version,
      chromeVersion,
      lighthouseVersion,
      serverCompression: 'gzip',
      cacheState: 'cold navigation',
      productionDomainReachable: false
    },
    groups
  };
  const rootJson = args.label === 'baseline' ? 'PERFORMANCE-BASELINE.json' : 'PERFORMANCE-VALIDATION.json';
  const rootMarkdown = args.label === 'baseline' ? 'PERFORMANCE-BASELINE.md' : 'PERFORMANCE-VALIDATION.md';
  await writeFile(resolve(rootJson), `${JSON.stringify(result, null, 2)}\n`);
  await writeFile(resolve(rootMarkdown), markdownReport(result));
  process.stdout.write(`Wrote ${rootJson}, ${rootMarkdown}, and ${groups.length * args.runs} raw reports.\n`);
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
