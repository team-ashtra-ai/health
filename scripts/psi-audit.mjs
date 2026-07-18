#!/usr/bin/env node

import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import process from 'node:process';

const PRODUCTION_ORIGIN = 'https://www.francielesofiati.com';
const OUTPUT = resolve('performance-reports/psi');

function argumentsFrom(argv) {
  const result = { strategies: ['mobile', 'desktop'], limit: Infinity, paths: [] };
  for (let index = 0; index < argv.length; index += 1) {
    if (argv[index] === '--strategy') result.strategies = [argv[++index]];
    else if (argv[index] === '--limit') result.limit = Number(argv[++index]);
    else if (argv[index] === '--paths') result.paths = argv[++index].split(',').filter(Boolean);
  }
  return result;
}

function sitemapUrls(xml) {
  return [...xml.matchAll(/<loc>([^<]+)<\/loc>/g)].map((match) => match[1]);
}

function metric(audits, id) {
  return audits?.[id]?.numericValue ?? null;
}

function fieldScope(payload) {
  if (payload.loadingExperience?.metrics && Object.keys(payload.loadingExperience.metrics).length) return 'url';
  if (payload.originLoadingExperience?.metrics && Object.keys(payload.originLoadingExperience.metrics).length) return 'origin';
  return 'unavailable';
}

async function requestPsi(url, strategy, key) {
  const endpoint = new URL('https://www.googleapis.com/pagespeedonline/v5/runPagespeed');
  endpoint.searchParams.set('url', url);
  endpoint.searchParams.set('strategy', strategy);
  for (const category of ['performance', 'accessibility', 'best-practices', 'seo']) {
    endpoint.searchParams.append('category', category);
  }
  if (key) endpoint.searchParams.set('key', key);
  const response = await fetch(endpoint, { headers: { Accept: 'application/json' } });
  if (!response.ok) {
    const retryAfter = response.headers.get('retry-after');
    throw new Error(`PSI ${response.status} for ${url} (${strategy})${retryAfter ? `; retry after ${retryAfter}s` : ''}`);
  }
  return response.json();
}

const args = argumentsFrom(process.argv.slice(2));
const key = process.env.PAGESPEED_API_KEY || '';
const sitemap = await readFile(resolve('sitemap.xml'), 'utf8');
let urls = sitemapUrls(sitemap).filter((url) => url.startsWith(PRODUCTION_ORIGIN));
if (args.paths.length) {
  const wanted = new Set(args.paths.map((path) => new URL(path, `${PRODUCTION_ORIGIN}/`).href));
  urls = urls.filter((url) => wanted.has(url));
}
urls = urls.slice(0, args.limit);
await mkdir(OUTPUT, { recursive: true });

const rows = [];
for (const url of urls) {
  for (const strategy of args.strategies) {
    const name = `${new URL(url).pathname.replace(/^\/|\/$/g, '').replaceAll('/', '--') || 'home'}--${strategy}`;
    try {
      const payload = await requestPsi(url, strategy, key);
      await writeFile(resolve(OUTPUT, `${name}.json`), `${JSON.stringify(payload, null, 2)}\n`);
      const lighthouse = payload.lighthouseResult;
      const audits = lighthouse?.audits;
      rows.push({
        url,
        strategy,
        status: 'ok',
        fieldDataScope: fieldScope(payload),
        performance: Math.round((lighthouse?.categories?.performance?.score || 0) * 100),
        lcpMs: metric(audits, 'largest-contentful-paint'),
        cls: metric(audits, 'cumulative-layout-shift'),
        tbtMs: metric(audits, 'total-blocking-time'),
        fcpMs: metric(audits, 'first-contentful-paint')
      });
    } catch (error) {
      rows.push({ url, strategy, status: 'failed', error: error.message, fieldDataScope: 'unavailable' });
    }
  }
}

const headers = ['url', 'strategy', 'status', 'field_data_scope', 'performance', 'lcp_ms', 'cls', 'tbt_ms', 'fcp_ms', 'error'];
const csvCell = (value) => `"${String(value ?? '').replaceAll('"', '""')}"`;
const csvRows = rows.map((row) => [
  row.url,
  row.strategy,
  row.status,
  row.fieldDataScope,
  row.performance,
  row.lcpMs,
  row.cls,
  row.tbtMs,
  row.fcpMs,
  row.error
].map(csvCell).join(','));
await writeFile(resolve(OUTPUT, 'summary.csv'), `${headers.map(csvCell).join(',')}\n${csvRows.join('\n')}\n`);
await writeFile(
  resolve(OUTPUT, 'summary.md'),
  `# PageSpeed Insights audit\n\n`
  + `Generated: ${new Date().toISOString()}\n\n`
  + `URLs requested: ${urls.length}; tests recorded: ${rows.length}.\n\n`
  + `Field data scope is reported as URL, origin or unavailable. Missing CrUX data is not treated as a failure.\n`
);
console.log(`Saved ${rows.length} PSI results to performance-reports/psi.`);
