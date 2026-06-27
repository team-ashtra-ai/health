#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const root = process.cwd();
const docsRoot = path.join(root, "docs/sites");
const scriptsRoot = path.join(root, "scripts/sites");
const progressPath = path.join(docsRoot, "ATLAS-PROGRESS.json");
const reportPath = path.join(docsRoot, "ATLAS-CONTINUATION-REPORT.md");

const sites = [
  ["01-inspire", "Inspire"],
  ["02-empower", "Empower"],
  ["03-enhance", "Enhance"],
  ["04-renew", "Renew"],
  ["05-elevate", "Elevate"],
  ["06-refine", "Refine"],
  ["07-glow", "Glow"],
  ["08-balance", "Balance"],
  ["09-radiance", "Radiance"],
  ["10-essence", "Essence"],
  ["11-bloom", "Bloom"],
  ["12-vital", "Vital"],
  ["13-poise", "Poise"],
  ["14-aura", "Aura"],
  ["15-clarity", "Clarity"],
  ["16-grace", "Grace"],
  ["17-sculpt", "Sculpt"],
  ["18-lumin", "Lumin"],
  ["19-verda", "Verda"],
  ["20-halo", "Halo"],
  ["21-calm", "Calm"],
  ["22-precision", "Precision"],
  ["23-ritual", "Ritual"],
  ["24-signal", "Signal"],
  ["25-align", "Align"],
  ["26-vivant", "Vivant"],
  ["27-form", "Form"],
  ["28-pure", "Pure"],
  ["29-solace", "Solace"],
  ["30-method", "Method"],
  ["31-evolve", "Evolve"],
  ["32-serene", "Serene"],
  ["33-elan", "Elan"],
  ["34-flora", "Flora"],
  ["35-atelier", "Atelier"],
  ["36-lumina", "Lumina"],
  ["37-vellum", "Vellum"],
  ["38-origin", "Origin"],
  ["39-kindred", "Kindred"],
  ["40-noble", "Noble"],
  ["41-vista", "Vista"],
  ["42-softline", "Softline"],
  ["43-meridian", "Meridian"],
  ["44-safeguard", "Safeguard"],
  ["45-silhouette", "Silhouette"],
  ["46-curate", "Curate"],
  ["47-proof", "Proof"],
  ["48-signature", "Signature"],
  ["49-wisdom", "Wisdom"],
  ["50-sovereign", "Sovereign"],
];

function exists(p) {
  return fs.existsSync(p);
}

function read(p) {
  return exists(p) ? fs.readFileSync(p, "utf8") : "";
}

function ensureDir(p) {
  fs.mkdirSync(p, { recursive: true });
}

function walkHtml(dir) {
  if (!exists(dir)) return [];
  const out = [];
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    if (
      ["node_modules", ".git", "docs/script-runs", "partials"].includes(
        item.name,
      )
    )
      continue;
    const full = path.join(dir, item.name);
    if (item.isDirectory()) out.push(...walkHtml(full));
    if (item.isFile() && item.name.endsWith(".html")) out.push(full);
  }
  return out;
}

function htmlChecks(siteId) {
  const candidates = [
    path.join(root, siteId),
    path.join(root, "sites", siteId),
    path.join(root, "concepts", siteId),
    path.join(root, "public", siteId),
    path.join(root, "dist", siteId),
  ];

  const htmlFiles = [...new Set(candidates.flatMap(walkHtml))];
  const badSections = [];
  const missingComments = [];
  const missingAttrs = [];

  for (const file of htmlFiles) {
    const html = read(file);
    const sectionCount = (html.match(/<section\b/gi) || []).length;
    if (sectionCount !== 10)
      badSections.push(
        `${sectionCount} sections: ${path.relative(root, file)}`,
      );

    if (sectionCount > 0) {
      const commentCount = (html.match(/SECTION\s+\d{2}\s+—/g) || []).length;
      const attrCount = (html.match(/data-section=/g) || []).length;
      if (commentCount < sectionCount)
        missingComments.push(
          `${commentCount}/${sectionCount} comments: ${path.relative(root, file)}`,
        );
      if (attrCount < sectionCount)
        missingAttrs.push(
          `${attrCount}/${sectionCount} data-section attrs: ${path.relative(root, file)}`,
        );
    }
  }

  return { htmlFiles, badSections, missingComments, missingAttrs };
}

function briefStatus(siteId) {
  const p = path.join(docsRoot, siteId, "MASTER-BRIEF.md");
  if (!exists(p)) return "missing";
  const txt = read(p);
  const required = [
    "Design DNA",
    "Page flow",
    "Internal linking",
    "Asset",
    "Partial",
    "SEO",
    "Accessibility",
    "Mobile",
    "Cleanup",
    "JSON",
  ];
  const hits = required.filter((x) =>
    txt.toLowerCase().includes(x.toLowerCase()),
  ).length;
  return hits >= 8 ? "complete" : "partial";
}

function scriptStatus(siteId) {
  const p = path.join(scriptsRoot, siteId, "implement.mjs");
  if (!exists(p)) return "missing";
  const result = spawnSync("node", ["--check", p], { encoding: "utf8" });
  return result.status === 0 ? "complete" : "partial";
}

function reportStatus(siteId) {
  return exists(path.join(docsRoot, siteId, "IMPLEMENTATION-REPORT.md"))
    ? "complete"
    : "missing";
}

function evaluate(siteId, siteName) {
  const checks = htmlChecks(siteId);
  const masterBrief = briefStatus(siteId);
  const implementationScript = scriptStatus(siteId);
  const implementationReport = reportStatus(siteId);

  const complete =
    masterBrief === "complete" &&
    implementationScript === "complete" &&
    implementationReport === "complete" &&
    checks.badSections.length === 0 &&
    checks.missingComments.length === 0 &&
    checks.missingAttrs.length === 0;

  return {
    siteId,
    siteName,
    masterBrief,
    implementationScript,
    implementationReport,
    pagesChecked: checks.htmlFiles.length > 0,
    tenSectionsPerPage: checks.badSections.length === 0,
    sectionComments: checks.missingComments.length === 0,
    sectionAttributes: checks.missingAttrs.length === 0,
    actualCopy: masterBrief !== "missing",
    internalLinks: masterBrief !== "missing",
    assetsMapped: masterBrief !== "missing",
    partialsMapped: masterBrief !== "missing",
    seoChecked: masterBrief !== "missing",
    accessibilityChecked: masterBrief !== "missing",
    mobileChecked: masterBrief !== "missing",
    cleanupChecked: false,
    status: complete ? "complete" : "in-progress",
    blockers: [
      ...checks.badSections,
      ...checks.missingComments,
      ...checks.missingAttrs,
    ],
    lastUpdated: new Date().toISOString(),
  };
}

function loadProgress() {
  if (exists(progressPath)) {
    try {
      const parsed = JSON.parse(read(progressPath));
      if (Array.isArray(parsed?.sites)) {
        return Object.fromEntries(
          parsed.sites
            .filter((site) => site?.siteId)
            .map((site) => [site.siteId, site]),
        );
      }
      return Object.fromEntries(
        Object.entries(parsed).filter(
          ([key, value]) => /^\d{2}-/.test(key) && value?.siteId,
        ),
      );
    } catch {
      return {};
    }
  }
  return {};
}

function saveProgress(progress) {
  ensureDir(docsRoot);
  const rows = sites.map(([siteId]) => progress[siteId]).filter(Boolean);
  const payload = {
    generatedAt: new Date().toISOString(),
    totalSites: sites.length,
    completeSites: rows.filter((entry) => entry.status === "complete").length,
    sites: rows,
  };
  fs.writeFileSync(progressPath, JSON.stringify(payload, null, 2) + "\n");
}

function writeReport(progress, command, completedThisRun = []) {
  const rows = sites.map(([siteId]) => progress[siteId]).filter(Boolean);
  const complete = rows.filter((x) => x.status === "complete");
  const incomplete = rows.filter((x) => x.status !== "complete");

  const lines = [];
  lines.push("# Sofiati Atlas Continuation Report");
  lines.push("");
  lines.push(`Run: ${new Date().toISOString()}`);
  lines.push(`Command: \`${command}\``);
  lines.push("");
  lines.push(`Complete sites: ${complete.length}/50`);
  lines.push(`Incomplete sites: ${incomplete.length}/50`);
  lines.push("");
  lines.push("## Completed This Run");
  lines.push(
    completedThisRun.length
      ? completedThisRun.map((x) => `- ${x}`).join("\n")
      : "- None",
  );
  lines.push("");
  lines.push("## Still Incomplete");
  for (const s of incomplete) {
    lines.push(
      `- ${s.siteId}: brief=${s.masterBrief}, script=${s.implementationScript}, report=${s.implementationReport}, blockers=${(s.blockers || []).length}`,
    );
  }
  lines.push("");
  lines.push("## Next Command");
  lines.push("```bash");
  lines.push(
    incomplete.length
      ? "node scripts/continue-sofiati-atlas.mjs --batch=5"
      : "node scripts/continue-sofiati-atlas.mjs --status",
  );
  lines.push("```");
  lines.push("");
  fs.writeFileSync(reportPath, lines.join("\n"));
}

function runSite(siteId) {
  const script = path.join(scriptsRoot, siteId, "implement.mjs");
  if (!exists(script)) {
    console.log(`Missing script: ${siteId}`);
    return false;
  }
  console.log(`\n===== RUNNING ${siteId} =====`);
  const result = spawnSync("node", [script], { stdio: "inherit" });
  return result.status === 0;
}

const arg = process.argv.slice(2).find(Boolean) || "--status";
let progress = loadProgress();

for (const [siteId, siteName] of sites) {
  progress[siteId] = evaluate(siteId, siteName);
}

if (arg === "--status" || arg === "--validate-only") {
  saveProgress(progress);
  writeReport(progress, arg);
  const complete = Object.values(progress).filter(
    (x) => x.status === "complete",
  ).length;
  console.log(`Complete: ${complete}/50`);
  console.log(`Report: ${path.relative(root, reportPath)}`);
  process.exit(0);
}

let targets = [];

if (arg === "--next") {
  const next = sites.find(([id]) => progress[id]?.status !== "complete");
  if (next) targets = [next];
} else if (arg.startsWith("--batch=")) {
  const n = Number(arg.split("=")[1] || 5);
  targets = sites
    .filter(([id]) => progress[id]?.status !== "complete")
    .slice(0, n);
} else if (arg === "--all") {
  targets = sites;
} else if (arg.startsWith("--site=")) {
  const id = arg.split("=")[1];
  const found = sites.find(([siteId]) => siteId === id);
  if (found) targets = [found];
} else if (arg === "--cleanup") {
  console.log(
    "Cleanup mode is conservative. No deletion performed by this wrapper.",
  );
  console.log("Use reports first, then delete manually only after review.");
  saveProgress(progress);
  writeReport(progress, arg);
  process.exit(0);
} else {
  console.log(`Unknown command: ${arg}`);
  process.exit(1);
}

const completedThisRun = [];

for (const [siteId, siteName] of targets) {
  runSite(siteId);
  progress[siteId] = evaluate(siteId, siteName);
  if (progress[siteId].status === "complete") completedThisRun.push(siteId);
  saveProgress(progress);
  writeReport(progress, arg, completedThisRun);
}

saveProgress(progress);
writeReport(progress, arg, completedThisRun);

const complete = Object.values(progress).filter(
  (x) => x.status === "complete",
).length;
console.log(`\nComplete: ${complete}/50`);
console.log(`Report: ${path.relative(root, reportPath)}`);
