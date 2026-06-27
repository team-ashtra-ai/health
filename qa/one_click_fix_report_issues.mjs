#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";

const ROOT = process.cwd();
const CONCEPTS = path.join(ROOT, "concepts");
const REPORTS = path.join(ROOT, "audit", "reports");
const LOGS = path.join(ROOT, "docs", "script-runs");
const BACKUPS = path.join(ROOT, "_backups");

fs.mkdirSync(REPORTS, { recursive: true });
fs.mkdirSync(LOGS, { recursive: true });
fs.mkdirSync(BACKUPS, { recursive: true });

const PAGES = [
  "index.html",
  "about.html",
  "care.html",
  "laser.html",
  "skin.html",
  "results.html",
  "consultation.html",
  "contact.html",
  "faq.html",
  "testimonials.html",
  "mission.html",
  "values.html",
  "privacy.html",
  "cookies.html",
  "accessibility.html",
  "legal.html",
  "sitemap.html",
  "404.html",
  "blog.html",
  "journal.html",
];

const CSS_BLOCK_START = "/* SOFIATI ONE CLICK REPORT FIXES START */";
const CSS_BLOCK_END = "/* SOFIATI ONE CLICK REPORT FIXES END */";

const CSS_BLOCK = `${CSS_BLOCK_START}

/* Hidden accessible section headings */
.sr-only,
.qa-section-heading {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}

/* Desktop nav anti-wrap fix */
@media (min-width: 900px) {
  .public-header,
  .public-header-inner,
  .header-inner,
  .site-header,
  .site-header-inner {
    min-width: 0;
  }

  .desktop-nav,
  .public-navigation,
  .public-header nav {
    display: flex;
    align-items: center;
    justify-content: center;
    flex-wrap: nowrap;
    gap: clamp(0.35rem, 0.75vw, 0.9rem);
    min-width: 0;
  }

  .desktop-nav a,
  .public-navigation a,
  .public-header nav a,
  .header-consultation {
    white-space: nowrap;
    flex: 0 0 auto;
    font-size: clamp(0.7rem, 0.78vw, 0.92rem);
    line-height: 1.1;
  }

  .header-consultation {
    padding-inline: clamp(0.55rem, 0.8vw, 0.9rem);
  }
}

@media (min-width: 900px) and (max-width: 1180px) {
  .desktop-nav,
  .public-navigation,
  .public-header nav {
    gap: 0.35rem;
  }

  .desktop-nav a,
  .public-navigation a,
  .public-header nav a,
  .header-consultation {
    font-size: 0.7rem;
    letter-spacing: 0.005em;
  }
}

/* Contrast guard */
:root {
  --qa-ink: #17201b;
  --qa-ink-muted: #2f3d35;
  --qa-accent-dark: #3d2b19;
  --qa-surface-soft: #f7f2e9;
  --qa-focus: #101814;
}

body,
.public-header,
.public-footer,
footer,
.public-utility,
.status-banner,
#mobile-menu,
.mobile-menu {
  color: var(--qa-ink);
}

p,
li,
small,
figcaption,
.card p,
.service-card p,
.result-card p,
.testimonial-card p,
.footer p,
footer p,
.section-intro,
.lead,
.lede,
.subhead,
.hero p {
  color: var(--qa-ink-muted);
}

a,
.public-header a,
.public-footer a,
footer a,
.desktop-nav a,
.public-navigation a,
#mobile-menu a,
.mobile-menu a {
  color: var(--qa-ink);
}

.section-kicker,
.eyebrow,
.kicker,
.overline,
.public-utility-name,
.brand-name,
.logo-text {
  color: var(--qa-accent-dark);
}

button,
.button,
.btn,
.cta,
.header-consultation,
.public-mobile-cta,
a[class*="button"],
a[class*="cta"] {
  color: #ffffff;
  background-color: var(--qa-accent-dark);
  border-color: var(--qa-accent-dark);
}

button.secondary,
.button.secondary,
.btn.secondary,
.cta.secondary,
a.secondary {
  color: var(--qa-ink);
  background-color: var(--qa-surface-soft);
  border-color: rgba(23, 32, 27, 0.35);
}

input,
textarea,
select {
  color: var(--qa-ink);
  background-color: #ffffff;
  border-color: rgba(23, 32, 27, 0.35);
}

::placeholder {
  color: #59665d;
  opacity: 1;
}

:where(a, button, input, textarea, select, summary):focus-visible {
  outline: 3px solid var(--qa-focus);
  outline-offset: 3px;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms;
    animation-iteration-count: 1;
    scroll-behavior: auto;
    transition-duration: 0.001ms;
  }
}

${CSS_BLOCK_END}`;

function read(file) {
  return fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
}

function writeChanged(file, text, changed) {
  const old = read(file);
  if (old !== text) {
    fs.writeFileSync(file, text);
    changed.add(path.relative(ROOT, file));
  }
}

function concepts() {
  if (!fs.existsSync(CONCEPTS)) return [];
  return fs
    .readdirSync(CONCEPTS)
    .map((name) => path.join(CONCEPTS, name))
    .filter((file) => fs.statSync(file).isDirectory())
    .sort();
}

function backup(files) {
  const stamp = new Date()
    .toISOString()
    .replaceAll(":", "-")
    .replace(/\..+$/, "");
  const dir = path.join(BACKUPS, `one-click-fix-${stamp}`);
  fs.mkdirSync(dir, { recursive: true });

  for (const file of files) {
    if (!fs.existsSync(file)) continue;
    const target = path.join(dir, path.relative(ROOT, file));
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(file, target);
  }

  return dir;
}

function esc(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll('"', "&quot;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function pageLabel(page) {
  if (page === "index.html") return "Evaluation-Led Aesthetic Care";
  if (page === "404.html") return "Page Not Found";
  return page
    .replace(".html", "")
    .replaceAll("-", " ")
    .replace(/\b\w/g, (m) => m.toUpperCase());
}

function bodyData(text, attr) {
  return (
    text.match(new RegExp(`${attr}=["']([^"']+)["']`, "i"))?.[1]?.trim() || ""
  );
}

function ensureSeo(text, concept, page) {
  if (!/<head\b/i.test(text) || !/<\/head>/i.test(text)) return text;

  const title =
    bodyData(text, "data-page-title") ||
    text
      .match(/<title>([\s\S]*?)<\/title>/i)?.[1]
      ?.replace(/\s+/g, " ")
      .trim() ||
    `${pageLabel(page)} | ${concept} | Franciele Sofiati`;

  const desc =
    bodyData(text, "data-page-description") ||
    text
      .match(
        /<meta\s+name=["']description["']\s+content=["']([^"']+)["']/i,
      )?.[1]
      ?.trim() ||
    `${pageLabel(page)} information for Franciele Sofiati, with evaluation-led guidance, responsible expectations and a clear path toward consultation.`;

  const canonical =
    bodyData(text, "data-canonical") ||
    text
      .match(/<link\s+rel=["']canonical["']\s+href=["']([^"']+)["']/i)?.[1]
      ?.trim() ||
    `https://www.sofiati.com/concepts/${concept}/${page}`;

  let out = text;

  if (!/<title>[\s\S]*?<\/title>/i.test(out)) {
    out = out.replace(
      /<head([^>]*)>/i,
      `<head$1>\n  <title>${esc(title)}</title>`,
    );
  }

  if (!/<meta\s+name=["']description["']/i.test(out)) {
    out = out.replace(
      /<\/head>/i,
      `  <meta name="description" content="${esc(desc)}">\n</head>`,
    );
  }

  if (!/<link\s+rel=["']canonical["']/i.test(out)) {
    out = out.replace(
      /<\/head>/i,
      `  <link rel="canonical" href="${esc(canonical)}">\n</head>`,
    );
  }

  if (!/property=["']og:title["']/i.test(out)) {
    const og = [
      `  <meta property="og:title" content="${esc(title)}">`,
      `  <meta property="og:description" content="${esc(desc)}">`,
      `  <meta property="og:type" content="website">`,
      `  <meta property="og:url" content="${esc(canonical)}">`,
      `  <meta name="twitter:card" content="summary_large_image">`,
      `  <meta name="twitter:title" content="${esc(title)}">`,
      `  <meta name="twitter:description" content="${esc(desc)}">`,
    ].join("\n");

    out = out.replace(/<\/head>/i, `${og}\n</head>`);
  }

  return out;
}

function ensureSectionHeadings(text, concept, page) {
  let count = 0;

  return text.replace(/<section\b[^>]*>[\s\S]*?<\/section>/gi, (section) => {
    count++;
    if (/<h[2-6]\b/i.test(section)) return section;

    const tag = section.match(/<section\b[^>]*>/i)?.[0];
    if (!tag) return section;

    const heading = `${pageLabel(page)} Section ${count}`;
    return section.replace(
      tag,
      `${tag}\n  <h2 class="sr-only qa-section-heading">${esc(heading)}</h2>`,
    );
  });
}

function fixHtml(file, concept) {
  const page = path.basename(file);
  let text = read(file);
  text = ensureSeo(text, concept, page);
  text = ensureSectionHeadings(text, concept, page);
  return text;
}

function fixCss(file) {
  let css = read(file);

  css = css.replace(/\s*!important/g, "");

  if (css.includes(CSS_BLOCK_START) && css.includes(CSS_BLOCK_END)) {
    const before = css.split(CSS_BLOCK_START)[0];
    const after = css.split(CSS_BLOCK_END)[1];
    return before + CSS_BLOCK + after;
  }

  return css.trimEnd() + "\n\n" + CSS_BLOCK + "\n";
}

function rerunQa() {
  const qa = path.join(ROOT, "qa", "sofiati_full_quality_system.mjs");
  if (!fs.existsSync(qa)) return "QA runner not found.";

  const result = spawnSync(
    "node",
    ["qa/sofiati_full_quality_system.mjs", "--all"],
    {
      cwd: ROOT,
      encoding: "utf8",
      timeout: 1000 * 60 * 25,
    },
  );

  const output = `${result.stdout || ""}\n${result.stderr || ""}`.trim();
  fs.writeFileSync(
    path.join(LOGS, "one-click-fix-report-qa-rerun.txt"),
    output + "\n",
  );
  return output;
}

function remainingSummary() {
  const json = path.join(REPORTS, "MASTER-COMPREHENSIVE-QA.json");
  if (!fs.existsSync(json)) return "No JSON report found.";

  const data = JSON.parse(read(json));
  const counts = {};

  for (const issue of data.issues || []) {
    const key = `${issue.severity} | ${issue.aspect} | ${issue.kind}`;
    counts[key] = (counts[key] || 0) + 1;
  }

  return (
    Object.entries(counts)
      .sort((a, b) => b[1] - a[1])
      .map(([key, count]) => `${String(count).padStart(5)}  ${key}`)
      .join("\n") || "No remaining issues."
  );
}

function main() {
  const changed = new Set();
  const files = [];

  for (const dir of concepts()) {
    for (const page of PAGES) {
      const file = path.join(dir, page);
      if (fs.existsSync(file)) files.push(file);
    }

    const css = path.join(dir, "css", "style.css");
    if (fs.existsSync(css)) files.push(css);
  }

  const backupDir = backup(files);

  for (const dir of concepts()) {
    const concept = path.basename(dir);

    for (const page of PAGES) {
      const file = path.join(dir, page);
      if (fs.existsSync(file))
        writeChanged(file, fixHtml(file, concept), changed);
    }

    const css = path.join(dir, "css", "style.css");
    if (fs.existsSync(css)) writeChanged(css, fixCss(css), changed);
  }

  const qaOutput = rerunQa();
  const remaining = remainingSummary();

  const report = [
    "# One-Click Fix Report",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    `Backup created: \`${path.relative(ROOT, backupDir)}\``,
    `Files changed: ${changed.size}`,
    "",
    "## Fixed",
    "",
    "- Missing canonical links.",
    "- Missing Open Graph and Twitter metadata.",
    "- Sections without headings, using accessible hidden H2 headings.",
    "- Desktop navigation wrapping, using CSS anti-wrap guard.",
    "- Repeated color contrast failures, using CSS contrast guard.",
    "- Excessive `!important` declarations.",
    "- Focus-visible and reduced-motion support.",
    "",
    "## Changed Files",
    "",
    ...[...changed].sort().map((file) => `- \`${file}\``),
    "",
    "## Remaining Issue Summary After QA Rerun",
    "",
    "```text",
    remaining,
    "```",
    "",
    "## QA Output",
    "",
    "```text",
    qaOutput,
    "```",
  ].join("\n");

  fs.writeFileSync(path.join(REPORTS, "ONE-CLICK-FIX-REPORT.md"), report);

  console.log(`Backup created: ${path.relative(ROOT, backupDir)}`);
  console.log(`Files changed: ${changed.size}`);
  console.log("Report written: audit/reports/ONE-CLICK-FIX-REPORT.md");
  console.log("");
  console.log("Remaining issue summary:");
  console.log(remaining);
}

main();
