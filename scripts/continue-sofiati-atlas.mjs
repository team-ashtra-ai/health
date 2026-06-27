#!/usr/bin/env node
import {
  atlasStatus,
  bootstrapAtlas,
  normalizeAtlas,
  runAtlas
} from "./lib/sofiati-atlas-core.mjs";

const FULL_ATLAS = [
  { id: "01-inspire", name: "Inspire" },
  { id: "02-empower", name: "Empower" },
  { id: "03-enhance", name: "Enhance" },
  { id: "04-renew", name: "Renew" },
  { id: "05-elevate", name: "Elevate" },
  { id: "06-refine", name: "Refine" },
  { id: "07-glow", name: "Glow" },
  { id: "08-balance", name: "Balance" },
  { id: "09-radiance", name: "Radiance" },
  { id: "10-essence", name: "Essence" },
  { id: "11-bloom", name: "Bloom" },
  { id: "12-vital", name: "Vital" },
  { id: "13-poise", name: "Poise" },
  { id: "14-aura", name: "Aura" },
  { id: "15-clarity", name: "Clarity" },
  { id: "16-grace", name: "Grace" },
  { id: "17-sculpt", name: "Sculpt" },
  { id: "18-lumin", name: "Lumin" },
  { id: "19-verda", name: "Verda" },
  { id: "20-halo", name: "Halo" },
  { id: "21-calm", name: "Calm" },
  { id: "22-precision", name: "Precision" },
  { id: "23-ritual", name: "Ritual" },
  { id: "24-signal", name: "Signal" },
  { id: "25-align", name: "Align" },
  { id: "26-vivant", name: "Vivant" },
  { id: "27-form", name: "Form" },
  { id: "28-pure", name: "Pure" },
  { id: "29-solace", name: "Solace" },
  { id: "30-method", name: "Method" },
  { id: "31-evolve", name: "Evolve" },
  { id: "32-serene", name: "Serene" },
  { id: "33-elan", name: "Elan" },
  { id: "34-flora", name: "Flora" },
  { id: "35-atelier", name: "Atelier" },
  { id: "36-lumina", name: "Lumina" },
  { id: "37-vellum", name: "Vellum" },
  { id: "38-origin", name: "Origin" },
  { id: "39-kindred", name: "Kindred" },
  { id: "40-noble", name: "Noble" },
  { id: "41-vista", name: "Vista" },
  { id: "42-softline", name: "Softline" },
  { id: "43-meridian", name: "Meridian" },
  { id: "44-safeguard", name: "Safeguard" },
  { id: "45-silhouette", name: "Silhouette" },
  { id: "46-curate", name: "Curate" },
  { id: "47-proof", name: "Proof" },
  { id: "48-signature", name: "Signature" },
  { id: "49-wisdom", name: "Wisdom" },
  { id: "50-sovereign", name: "Sovereign" }
];

function parseArgs(argv) {
  const options = {
    command: `node scripts/continue-sofiati-atlas.mjs ${argv.join(" ")}`.trim()
  };
  for (const arg of argv) {
    if (arg === "--status") options.status = true;
    else if (arg === "--next") options.next = true;
    else if (arg === "--all") options.all = true;
    else if (arg === "--validate-only") options.validateOnly = true;
    else if (arg === "--cleanup") options.cleanup = true;
    else if (arg === "--init") options.init = true;
    else if (arg.startsWith("--batch=")) options.batch = Number(arg.slice("--batch=".length));
    else if (arg.startsWith("--site=")) options.site = arg.slice("--site=".length);
  }
  return options;
}

function printUsage() {
  console.log(`Sofiati atlas continuation

Commands:
  node scripts/continue-sofiati-atlas.mjs --status
  node scripts/continue-sofiati-atlas.mjs --next
  node scripts/continue-sofiati-atlas.mjs --batch=5
  node scripts/continue-sofiati-atlas.mjs --all
  node scripts/continue-sofiati-atlas.mjs --site=01-inspire
  node scripts/continue-sofiati-atlas.mjs --validate-only
  node scripts/continue-sofiati-atlas.mjs --cleanup

Bootstrap:
  node scripts/continue-sofiati-atlas.mjs --init
`);
}

const root = process.cwd();
const options = parseArgs(process.argv.slice(2));
const atlas = normalizeAtlas(FULL_ATLAS);

if (options.status) {
  const status = atlasStatus(root, FULL_ATLAS);
  for (const line of status.lines) console.log(line);
  process.exit(status.complete === status.total ? 0 : 1);
}

if (options.init) {
  await bootstrapAtlas(root, atlas);
  console.log("Atlas progress and continuation report are initialized.");
  process.exit(0);
}

if (!options.next && !options.batch && !options.all && !options.site && !options.validateOnly && !options.cleanup) {
  printUsage();
  process.exit(0);
}

if (options.batch && (!Number.isInteger(options.batch) || options.batch < 1)) {
  console.error("--batch must be a positive integer.");
  process.exit(2);
}

const result = await runAtlas(root, FULL_ATLAS, options);
console.log(`Selected sites: ${result.selected.map((site) => site.siteId).join(", ") || "none"}`);
console.log(`Completed during this run: ${result.completedDuring.join(", ") || "none"}`);
console.log(`Atlas complete: ${result.progress.completeSites}/${result.progress.totalSites}`);
if (result.aggregate.unusedFilesRemoved.length) {
  console.log(`Unused files removed: ${result.aggregate.unusedFilesRemoved.length}`);
}

process.exit(result.progress.completeSites === result.progress.totalSites ? 0 : 1);
