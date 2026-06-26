#!/usr/bin/env node

import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { spawn, spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { chromium } from "playwright";
import axeCore from "axe-core";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = path.resolve(__dirname, "..");
const CONCEPTS_DIR = path.join(ROOT, "concepts");
const REPORT_DIR = path.join(ROOT, "audit", "reports");
const SCREENSHOT_DIR = path.join(ROOT, "audit", "screenshots", "qa");
const BACKUP_DIR = path.join(ROOT, "_backups");
const PORT = 4173;
const BASE_URL = `http://127.0.0.1:${PORT}`;

const args = new Set(process.argv.slice(2));
const getArg = (name, fallback = "") => {
  const raw = process.argv.find((item) => item.startsWith(`${name}=`));
  return raw ? raw.slice(name.length + 1) : fallback;
};

const RUN_ALL = args.has("--all");
const FIX_SAFE = args.has("--fix-safe");
const FIX_AGGRESSIVE = args.has("--fix-aggressive");
const RUN_RENDERED = RUN_ALL || args.has("--rendered");
const RUN_SCREENSHOTS = RUN_ALL || args.has("--screenshots");
const RUN_LIGHTHOUSE = RUN_ALL || args.has("--lighthouse-selected");
const RUN_LIGHTHOUSE_MORE = args.has("--lighthouse-more");
const RENDER_ALL_PAGES = args.has("--render-all-pages");
const PSI_BASE = getArg("--psi-base", "");

const REQUIRED_PAGES = [
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
];

const OPTIONAL_PAGES = ["blog.html", "journal.html"];

const KEY_RENDER_PAGES = [
  "index.html",
  "about.html",
  "care.html",
  "laser.html",
  "skin.html",
  "results.html",
  "consultation.html",
  "contact.html",
];

const REQUIRED_PARTIALS = [
  "accessibility.html",
  "back-to-top.html",
  "concept-switcher.html",
  "consultation-form.html",
  "contact-card.html",
  "cookie-banner.html",
  "floating-whatsapp.html",
  "floating-widgets.html",
  "footer.html",
  "header.html",
  "head.html",
  "mobile-menu.html",
  "navigation.html",
  "schema.html",
  "status-banner.html",
];

const PRIMARY_NAV = ["Home", "About", "Care", "Laser", "Skin", "Results", "Consultation", "Contact"];

const BAD_TEXT = [
  "lorem ipsum",
  "placeholder",
  "todo",
  "fixme",
  "undefined",
  "null",
  "[insert",
  "coming soon",
  "sample text",
  "dummy text",
];

const MANUAL_KINDS = new Set([
  "duplicate-css-file",
  "duplicate-header",
  "duplicate-mobile",
  "duplicate-footer",
  "thin-page-structure",
  "weak-storytelling",
  "section-without-heading",
  "visual-uniqueness",
  "lighthouse-low-score",
  "pagespeed-low-score",
  "large-css",
  "large-js",
  "large-image",
]);

const LANGUAGE_RUNTIME_START = "/* SOFIATI LANGUAGE TOGGLE RUNTIME START */";
const LANGUAGE_RUNTIME_END = "/* SOFIATI LANGUAGE TOGGLE RUNTIME END */";
const MENU_RUNTIME_START = "/* SOFIATI MOBILE MENU RUNTIME START */";
const MENU_RUNTIME_END = "/* SOFIATI MOBILE MENU RUNTIME END */";
const CSS_BASELINE_START = "/* SOFIATI QA BASELINE FIXES START */";
const CSS_BASELINE_END = "/* SOFIATI QA BASELINE FIXES END */";

const LANGUAGE_RUNTIME = `/* SOFIATI LANGUAGE TOGGLE RUNTIME START */
(function () {
  function normalizeLang(value) {
    return value === "pt" || value === "pt-BR" || value === "pt-br" ? "pt-BR" : "en";
  }

  function shortLang(value) {
    return normalizeLang(value) === "pt-BR" ? "pt" : "en";
  }

  function setLanguage(nextLang) {
    const normalized = normalizeLang(nextLang);
    const short = shortLang(normalized);

    document.documentElement.lang = normalized;
    document.documentElement.setAttribute("data-active-lang", short);

    document.querySelectorAll("[data-lang-switch]").forEach((control) => {
      const controlShort = shortLang(control.getAttribute("data-lang-switch"));
      const active = controlShort === short;
      control.setAttribute("aria-pressed", active ? "true" : "false");
      control.setAttribute("data-active", active ? "true" : "false");
      control.classList.toggle("is-active", active);
      control.classList.toggle("active", active);
    });
  }

  document.addEventListener("click", function (event) {
    const control = event.target.closest("[data-lang-switch]");
    if (!control) return;
    event.preventDefault();
    setLanguage(control.getAttribute("data-lang-switch"));
  });

  function initialiseLanguageState() {
    setLanguage(
      document.documentElement.getAttribute("lang") ||
      document.body?.getAttribute("data-default-lang") ||
      document.documentElement.getAttribute("data-default-lang") ||
      "en"
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiseLanguageState);
  } else {
    initialiseLanguageState();
  }

  window.SofiatiSetLanguage = setLanguage;
})();
 /* SOFIATI LANGUAGE TOGGLE RUNTIME END */`;

const MENU_RUNTIME = `/* SOFIATI MOBILE MENU RUNTIME START */
(function () {
  const MENU_SELECTOR = "#mobile-menu";
  const LOCK_CLASS = "public-menu-locked";
  let lastTrigger = null;

  function getMenu() {
    return document.querySelector(MENU_SELECTOR);
  }

  function openMenu(trigger) {
    const menu = getMenu();
    if (!menu) return;

    lastTrigger = trigger || document.activeElement;
    menu.classList.add("is-open");
    menu.setAttribute("aria-hidden", "false");
    document.body.classList.add(LOCK_CLASS);

    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      button.setAttribute("aria-expanded", "true");
      button.setAttribute("aria-controls", "mobile-menu");
    });

    const firstFocusable = menu.querySelector("a[href], button:not([disabled]), [tabindex]:not([tabindex='-1'])");
    if (firstFocusable) firstFocusable.focus({ preventScroll: true });
  }

  function closeMenu() {
    const menu = getMenu();
    if (!menu) return;

    menu.classList.remove("is-open");
    menu.setAttribute("aria-hidden", "true");
    document.body.classList.remove(LOCK_CLASS);

    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", "mobile-menu");
    });

    if (lastTrigger && typeof lastTrigger.focus === "function") {
      lastTrigger.focus({ preventScroll: true });
    }
  }

  document.addEventListener("click", function (event) {
    const toggle = event.target.closest("[data-menu-toggle]");
    const close = event.target.closest("[data-menu-close]");
    const menu = getMenu();

    if (toggle) {
      event.preventDefault();
      if (menu?.classList.contains("is-open")) closeMenu();
      else openMenu(toggle);
      return;
    }

    if (close) {
      event.preventDefault();
      closeMenu();
      return;
    }

    if (menu?.classList.contains("is-open") && event.target === menu) {
      closeMenu();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeMenu();
  });

  document.addEventListener("DOMContentLoaded", function () {
    const menu = getMenu();
    if (menu && !menu.hasAttribute("aria-hidden")) {
      menu.setAttribute("aria-hidden", "true");
    }

    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      if (!button.hasAttribute("aria-expanded")) button.setAttribute("aria-expanded", "false");
      if (!button.hasAttribute("aria-controls")) button.setAttribute("aria-controls", "mobile-menu");
    });
  });
})();
 /* SOFIATI MOBILE MENU RUNTIME END */`;

const CSS_BASELINE = `/* SOFIATI QA BASELINE FIXES START */
html {
  -webkit-text-size-adjust: 100%;
  text-size-adjust: 100%;
}

*, *::before, *::after {
  box-sizing: border-box;
}

img, svg, video, canvas {
  max-width: 100%;
  height: auto;
}

:where(a, button, input, textarea, select, summary):focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 3px;
}

.public-menu-locked {
  overflow: hidden;
}

#mobile-menu[aria-hidden="true"]:not(.is-open) {
  visibility: hidden;
  pointer-events: none;
}

#mobile-menu.is-open,
#mobile-menu[aria-hidden="false"] {
  visibility: visible;
  pointer-events: auto;
}

@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.001ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.001ms !important;
  }
}
 /* SOFIATI QA BASELINE FIXES END */`;

fs.mkdirSync(REPORT_DIR, { recursive: true });
fs.mkdirSync(SCREENSHOT_DIR, { recursive: true });
fs.mkdirSync(BACKUP_DIR, { recursive: true });

const issues = [];
const changes = [];

function read(file) {
  return fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
}

function writeIfChanged(file, next) {
  const previous = fs.existsSync(file) ? fs.readFileSync(file, "utf8") : "";
  if (previous !== next) {
    fs.mkdirSync(path.dirname(file), { recursive: true });
    fs.writeFileSync(file, next);
    changes.push(path.relative(ROOT, file));
  }
}

function rel(file) {
  return path.relative(ROOT, file).replaceAll("\\", "/");
}

function hash(text) {
  return crypto.createHash("sha256").update(text).digest("hex").slice(0, 14);
}

function normalizeHtml(text) {
  return text.replace(/\s+/g, " ").trim();
}

function addIssue(aspect, severity, kind, concept, file, detail, fix = "") {
  issues.push({
    aspect,
    severity,
    kind,
    concept,
    file: typeof file === "string" ? file : rel(file),
    detail,
    fix,
    autoFixable: !MANUAL_KINDS.has(kind),
  });
}

function conceptDirs() {
  if (!fs.existsSync(CONCEPTS_DIR)) return [];
  return fs.readdirSync(CONCEPTS_DIR)
    .map((name) => path.join(CONCEPTS_DIR, name))
    .filter((item) => fs.statSync(item).isDirectory())
    .sort();
}

function pageFiles(conceptDir, rendered = false) {
  const names = rendered
    ? RENDER_ALL_PAGES
      ? [...REQUIRED_PAGES, ...OPTIONAL_PAGES]
      : KEY_RENDER_PAGES
    : [...REQUIRED_PAGES, ...OPTIONAL_PAGES];

  return names
    .map((name) => path.join(conceptDir, name))
    .filter((file) => fs.existsSync(file));
}

function replaceBlock(text, start, end, block) {
  if (text.includes(start) && text.includes(end)) {
    const before = text.split(start)[0];
    const after = text.split(end)[1];
    return before + block + after;
  }
  return text.trimEnd() + "\n\n" + block + "\n";
}

function createBackup(files) {
  const stamp = new Date().toISOString().replaceAll(":", "-").replace(/\..+$/, "");
  const dest = path.join(BACKUP_DIR, `full-quality-${stamp}`);
  fs.mkdirSync(dest, { recursive: true });

  for (const file of files) {
    if (!fs.existsSync(file)) continue;
    const target = path.join(dest, rel(file));
    fs.mkdirSync(path.dirname(target), { recursive: true });
    fs.copyFileSync(file, target);
  }

  return dest;
}

function cleanDuplicateBodyAttrs(bodyTag) {
  const attrRegex = /\s([a-zA-Z_:][-a-zA-Z0-9_:.]*)=(["'][^"']*["'])/g;
  const attrs = [...bodyTag.matchAll(attrRegex)];
  let rebuilt = bodyTag.replace(attrRegex, "").replace(/>$/, "");
  const seen = new Set();

  for (const match of attrs) {
    const name = match[1];
    const value = match[2];
    if (seen.has(name)) continue;
    seen.add(name);
    rebuilt += ` ${name}=${value}`;
  }

  return rebuilt + ">";
}

function imageAltFromSrc(src) {
  const base = path.basename(src.split("?")[0].split("#")[0], path.extname(src));
  return base.replace(/[-_]+/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());
}

function fixImages(text) {
  return text.replace(/<img\b[^>]*>/gi, (tag) => {
    let next = tag;
    const lower = next.toLowerCase();
    const srcMatch = next.match(/\bsrc=["']([^"']+)["']/i);
    const alt = srcMatch ? imageAltFromSrc(srcMatch[1]) : "Decorative image";

    if (!/\salt=/i.test(next)) {
      next = next.replace(/\/?>$/, ` alt="${alt}">`);
    } else if (/\balt=["']\s*["']/i.test(next)) {
      next = next.replace(/\balt=["']\s*["']/i, `alt="${alt}"`);
    }

    if (!/\sloading=/i.test(next) && !lower.includes("hero")) {
      next = next.replace(/\/?>$/, ` loading="lazy">`);
    }

    if (!/\sdecoding=/i.test(next)) {
      next = next.replace(/\/?>$/, ` decoding="async">`);
    }

    return next;
  });
}

function ensureBodyMetadata(text, pageName) {
  const match = text.match(/<body\b[^>]*>/i);
  if (!match) return text;

  let body = cleanDuplicateBodyAttrs(match[0]);

  if (!/data-page=/.test(body)) {
    const key = pageName.replace(".html", "");
    body = body.replace(/>$/, ` data-page="${key}">`);
  }

  return text.replace(match[0], body);
}

function ensureSectionSignatures(text, concept, pageName) {
  let count = 0;
  return text.replace(/<section\b[^>]*>/gi, (tag) => {
    count += 1;
    if (/data-layout-signature=/i.test(tag)) return tag;
    const page = pageName.replace(".html", "");
    return tag.replace(/>$/, ` data-layout-signature="${concept}-${page}-section-${String(count).padStart(2, "0")}">`);
  });
}

function ensureSeoBasics(text, concept, pageName) {
  if (!/<head\b/i.test(text)) return text;

  const bodyTitle = text.match(/data-page-title=["']([^"']+)["']/i)?.[1];
  const bodyDesc = text.match(/data-page-description=["']([^"']+)["']/i)?.[1];
  const bodyCanonical = text.match(/data-canonical=["']([^"']+)["']/i)?.[1];

  const label = pageName === "index.html"
    ? "Evaluation-Led Aesthetic Care"
    : pageName.replace(".html", "").replace(/-/g, " ").replace(/\b\w/g, (m) => m.toUpperCase());

  const title = bodyTitle || `${label} | ${concept} | Franciele Sofiati`;
  const desc = bodyDesc || `${label} information for Franciele Sofiati, with evaluation-led guidance, responsible expectations and a clear path toward consultation.`;
  const canonical = bodyCanonical || `https://www.sofiati.com/concepts/${concept}/${pageName}`;

  let next = text;

  if (!/<title>[\s\S]*?<\/title>/i.test(next)) {
    next = next.replace(/<head([^>]*)>/i, `<head$1>\n  <title>${title}</title>`);
  }

  if (!/<meta\s+name=["']description["']/i.test(next)) {
    next = next.replace(/<\/head>/i, `  <meta name="description" content="${desc}">\n</head>`);
  }

  if (!/<link\s+rel=["']canonical["']/i.test(next)) {
    next = next.replace(/<\/head>/i, `  <link rel="canonical" href="${canonical}">\n</head>`);
  }

  if (!/property=["']og:title["']/i.test(next)) {
    const og = [
      `  <meta property="og:title" content="${title}">`,
      `  <meta property="og:description" content="${desc}">`,
      `  <meta property="og:type" content="website">`,
      `  <meta property="og:url" content="${canonical}">`,
    ].join("\n");
    next = next.replace(/<\/head>/i, `${og}\n</head>`);
  }

  return next;
}

function fixStatusBanner(file) {
  if (!fs.existsSync(file)) return;
  let text = read(file);
  let next = text.replaceAll("Francielli Sofiati", "Franciele Sofiati");

  if (!/public-utility-name/.test(next)) {
    next = next.replace(/(<[^>]+class=["'][^"']*public-utility[^"']*["'][^>]*>)/i, `$1\n<span class="public-utility-name">Franciele Sofiati</span>`);
  }

  if (!/data-lang-switch=["']en["']/i.test(next) || !/data-lang-switch=["']pt["']/i.test(next)) {
    const switcher = `<div class="language-switcher public-language public-language-utility" aria-label="Site language"><button type="button" data-lang-switch="en" aria-pressed="true">EN</button><button type="button" data-lang-switch="pt" aria-pressed="false">PT</button></div>`;
    next = next.trimEnd() + "\n" + switcher + "\n";
  }

  next = next.replace(/(<button\b[^>]*data-lang-switch=["']en["'][^>]*)(>)/i, (m, before, end) => /aria-pressed=/i.test(before) ? m : `${before} aria-pressed="true"${end}`);
  next = next.replace(/(<button\b[^>]*data-lang-switch=["']pt["'][^>]*)(>)/i, (m, before, end) => /aria-pressed=/i.test(before) ? m : `${before} aria-pressed="false"${end}`);

  writeIfChanged(file, next);
}

function fixMobileMenu(file) {
  if (!fs.existsSync(file)) return;
  let text = read(file);

  let next = text.replace(/\s*<div class=["'][^"']*public-language-menu[^"']*["'][\s\S]*?<\/div>/gi, "");

  if (!/id=["']mobile-menu["']/i.test(next)) {
    next = next.replace(/<([a-z0-9]+)([^>]*class=["'][^"']*mobile[^"']*["'][^>]*)>/i, `<$1 id="mobile-menu"$2>`);
  }

  if (/id=["']mobile-menu["']/i.test(next) && !/aria-hidden=/i.test(next)) {
    next = next.replace(/(<[^>]+id=["']mobile-menu["'][^>]*)>/i, `$1 aria-hidden="true">`);
  }

  if (!/data-menu-close/i.test(next)) {
    next = next.replace(/(<[^>]+id=["']mobile-menu["'][^>]*>)/i, `$1\n<button type="button" class="public-mobile-close" data-menu-close>Close</button>`);
  }

  if (!/public-mobile-cta/i.test(next)) {
    if (/<\/nav>/i.test(next)) {
      next = next.replace(/<\/nav>/i, `<a class="public-mobile-cta" href="consultation.html">Consultation</a>\n</nav>`);
    } else {
      next += `\n<a class="public-mobile-cta" href="consultation.html">Consultation</a>\n`;
    }
  }

  writeIfChanged(file, next);
}

function fixHeader(file) {
  if (!fs.existsSync(file)) return;
  let text = read(file);
  let next = text;

  if (/data-menu-toggle/i.test(next)) {
    next = next.replace(/(<button\b[^>]*data-menu-toggle[^>]*)(>)/i, (m, before, end) => {
      let out = before;
      if (!/aria-controls=/i.test(out)) out += ` aria-controls="mobile-menu"`;
      if (!/aria-expanded=/i.test(out)) out += ` aria-expanded="false"`;
      return out + end;
    });
  }

  writeIfChanged(file, next);
}

function fixJs(file) {
  if (!fs.existsSync(file)) return;
  let text = read(file);
  let next = replaceBlock(text, LANGUAGE_RUNTIME_START, LANGUAGE_RUNTIME_END, LANGUAGE_RUNTIME);
  next = replaceBlock(next, MENU_RUNTIME_START, MENU_RUNTIME_END, MENU_RUNTIME);
  writeIfChanged(file, next);
}

function fixCss(file) {
  if (!fs.existsSync(file)) return;
  let text = read(file);
  let next = replaceBlock(text, CSS_BASELINE_START, CSS_BASELINE_END, CSS_BASELINE);
  writeIfChanged(file, next);
}

function fixHtml(file, concept) {
  if (!fs.existsSync(file)) return;
  const pageName = path.basename(file);
  let text = read(file);
  let next = ensureBodyMetadata(text, pageName);
  next = fixImages(next);
  next = ensureSectionSignatures(next, concept, pageName);

  if (FIX_AGGRESSIVE) {
    next = ensureSeoBasics(next, concept, pageName);
  }

  writeIfChanged(file, next);
}

function applySafeFixes() {
  const files = [];

  for (const conceptDir of conceptDirs()) {
    files.push(path.join(conceptDir, "partials", "status-banner.html"));
    files.push(path.join(conceptDir, "partials", "mobile-menu.html"));
    files.push(path.join(conceptDir, "partials", "header.html"));
    files.push(path.join(conceptDir, "js", "main.js"));
    files.push(path.join(conceptDir, "css", "style.css"));
    for (const page of [...REQUIRED_PAGES, ...OPTIONAL_PAGES]) {
      files.push(path.join(conceptDir, page));
    }
  }

  const backup = createBackup(files);

  for (const conceptDir of conceptDirs()) {
    const concept = path.basename(conceptDir);
    fixStatusBanner(path.join(conceptDir, "partials", "status-banner.html"));
    fixMobileMenu(path.join(conceptDir, "partials", "mobile-menu.html"));
    fixHeader(path.join(conceptDir, "partials", "header.html"));
    fixJs(path.join(conceptDir, "js", "main.js"));
    fixCss(path.join(conceptDir, "css", "style.css"));

    for (const page of [...REQUIRED_PAGES, ...OPTIONAL_PAGES]) {
      fixHtml(path.join(conceptDir, page), concept);
    }
  }

  return backup;
}

function auditInventory() {
  const dirs = conceptDirs();

  if (dirs.length !== 50) {
    addIssue("inventory", "critical", "concept-count", "GLOBAL", CONCEPTS_DIR, `Expected 50 concept folders, found ${dirs.length}.`, "Restore or create missing concept folders.");
  }

  for (const dir of dirs) {
    const concept = path.basename(dir);

    for (const page of REQUIRED_PAGES) {
      const file = path.join(dir, page);
      if (!fs.existsSync(file)) {
        addIssue("inventory", "critical", "missing-page", concept, file, `Missing required page ${page}.`, "Restore or create this page.");
      }
    }

    for (const partial of REQUIRED_PARTIALS) {
      const file = path.join(dir, "partials", partial);
      if (!fs.existsSync(file)) {
        addIssue("inventory", "critical", "missing-partial", concept, file, `Missing required partial ${partial}.`, "Restore or create this partial.");
      }
    }

    for (const asset of ["css/style.css", "js/main.js", "js/partials.js"]) {
      const file = path.join(dir, asset);
      if (!fs.existsSync(file)) {
        addIssue("inventory", "critical", "missing-core-asset", concept, file, `Missing core asset ${asset}.`, "Restore required CSS/JS.");
      }
    }

    for (const doc of ["design-dna.md", "design-notes.md", "asset-plan.md", "internal-link-map.md", "page-flow-map.md"]) {
      const file = path.join(dir, doc);
      if (!fs.existsSync(file)) {
        addIssue("inventory", "medium", "missing-planning-doc", concept, file, `Missing planning document ${doc}.`, "Create concept planning doc.");
      }
    }
  }
}

function auditPartials() {
  for (const dir of conceptDirs()) {
    const concept = path.basename(dir);
    const p = path.join(dir, "partials");

    const status = path.join(p, "status-banner.html");
    const header = path.join(p, "header.html");
    const mobile = path.join(p, "mobile-menu.html");
    const nav = path.join(p, "navigation.html");
    const footer = path.join(p, "footer.html");

    if (fs.existsSync(status)) {
      const text = read(status);
      if (!/public-utility/i.test(text)) addIssue("partials", "high", "utility-class", concept, status, "Status banner missing public utility class.", "Use .public-utility.status-banner.");
      if (!/public-utility-name/i.test(text)) addIssue("partials", "high", "utility-name", concept, status, "Utility name class missing.", "Add .public-utility-name.");
      if (!/Franciele Sofiati/.test(text)) addIssue("partials", "high", "canonical-name", concept, status, "Canonical name not found.", "Use Franciele Sofiati consistently.");
      if ((text.match(/data-lang-switch=["']en["']/gi) || []).length !== 1 || (text.match(/data-lang-switch=["']pt["']/gi) || []).length !== 1) {
        addIssue("partials", "high", "language-switcher-count", concept, status, "Utility should have exactly one EN and one PT language control.", "Keep EN/PT in utility bar.");
      }
      if (!/aria-pressed/i.test(text)) addIssue("partials", "medium", "language-aria", concept, status, "Language controls missing aria-pressed.", "Add aria-pressed.");
    }

    if (fs.existsSync(header)) {
      const text = read(header);
      if (!/public-header/i.test(text)) addIssue("partials", "critical", "header-contract", concept, header, "Header missing .public-header.", "Add required header wrapper.");
      if (!/data-menu-toggle/i.test(text)) addIssue("partials", "critical", "menu-toggle", concept, header, "Header missing data-menu-toggle.", "Add mobile menu trigger.");
      if (!/header-consultation/i.test(text)) addIssue("partials", "high", "header-cta", concept, header, "Header missing consultation CTA class.", "Add .header-consultation.");
    }

    if (fs.existsSync(mobile)) {
      const text = read(mobile);
      if (!/id=["']mobile-menu["']/i.test(text)) addIssue("partials", "critical", "mobile-menu-id", concept, mobile, "Mobile menu missing #mobile-menu.", "Add id.");
      if (!/data-menu-close/i.test(text)) addIssue("partials", "critical", "mobile-close", concept, mobile, "Mobile menu missing close control.", "Add data-menu-close.");
      if (!/public-mobile-primary/i.test(text)) addIssue("partials", "high", "mobile-primary-links", concept, mobile, "Mobile primary link container missing.", "Add .public-mobile-primary.");
      if (!/public-mobile-cta/i.test(text)) addIssue("partials", "high", "mobile-cta", concept, mobile, "Mobile CTA missing.", "Add .public-mobile-cta.");
      if (/public-language-menu/i.test(text)) addIssue("partials", "medium", "duplicate-menu-language", concept, mobile, "Language switcher found inside mobile menu.", "Keep language switcher in utility bar only.");
    }

    if (fs.existsSync(nav)) {
      const text = read(nav).replace(/\s+/g, " ");
      for (const label of PRIMARY_NAV) {
        if (!text.includes(label)) {
          addIssue("partials", "high", "missing-nav-label", concept, nav, `Navigation missing ${label}.`, "Keep required primary nav labels.");
        }
      }
    }

    if (fs.existsSync(footer)) {
      const text = read(footer);
      for (const label of ["Privacy", "Cookies", "Accessibility", "Legal"]) {
        if (!text.includes(label)) {
          addIssue("partials", "medium", "footer-legal-link", concept, footer, `Footer missing ${label}.`, "Add legal/support link.");
        }
      }
    }
  }
}

function auditPagesSections() {
  for (const dir of conceptDirs()) {
    const concept = path.basename(dir);

    for (const file of pageFiles(dir)) {
      const page = path.basename(file);
      const text = read(file);
      const lower = text.toLowerCase();

      if (!/<html\b[^>]*\blang=["'][^"']+["']/i.test(text)) addIssue("pages", "critical", "html-lang", concept, file, "Missing html lang.", "Add lang attribute.");
      if (!/<title>[^<]{15,}<\/title>/i.test(text)) addIssue("pages", "high", "title-missing-weak", concept, file, "Missing or weak title.", "Add descriptive title.");

      const h1Count = (text.match(/<h1\b/gi) || []).length;
      if (h1Count !== 1) addIssue("pages", "high", "h1-count", concept, file, `Expected exactly one H1, found ${h1Count}.`, "Use one clear H1 per page.");

      const body = text.match(/<body\b[^>]*>/i)?.[0] || "";
      if (!body) addIssue("pages", "critical", "missing-body", concept, file, "Missing body tag.", "Restore valid HTML.");
      if (body && !/data-page=/i.test(body)) addIssue("pages", "medium", "missing-data-page", concept, file, "Body missing data-page.", "Add data-page metadata.");

      if (body) {
        const attrs = [...body.matchAll(/\s([a-zA-Z_:][-a-zA-Z0-9_:.]*)=/g)].map((m) => m[1]);
        const dupes = attrs.filter((a, i) => attrs.indexOf(a) !== i);
        for (const attr of [...new Set(dupes)]) {
          addIssue("pages", "medium", "duplicate-body-attribute", concept, file, `Duplicate body attribute ${attr}.`, "Remove duplicate attribute.");
        }
      }

      for (const bad of BAD_TEXT) {
        if (lower.includes(bad)) addIssue("content", "high", "placeholder-text", concept, file, `Suspicious placeholder text found: ${bad}.`, "Replace with final client-facing copy.");
      }

      const sections = [...text.matchAll(/<section\b[^>]*>[\s\S]*?<\/section>/gi)];
      if (!["404.html", "sitemap.html"].includes(page) && sections.length < 3) {
        addIssue("pages", "medium", "thin-page-structure", concept, file, `Only ${sections.length} sections found.`, "Review page storytelling depth manually.");
      }

      sections.forEach((match, index) => {
        const raw = match[0];
        const sectionTag = raw.match(/<section\b[^>]*>/i)?.[0] || "";
        if (!/<h[2-6]\b/i.test(raw)) addIssue("pages", "medium", "section-without-heading", concept, file, `Section ${index + 1} has no H2-H6 heading.`, "Add semantic heading.");
        if (!/data-layout-signature/i.test(sectionTag)) addIssue("pages", "low", "missing-layout-signature", concept, file, `Section ${index + 1} missing data-layout-signature.`, "Add layout signature.");
      });
    }
  }
}

function auditSeoSchema() {
  for (const dir of conceptDirs()) {
    const concept = path.basename(dir);

    for (const file of pageFiles(dir)) {
      const text = read(file);

      const title = text.match(/<title>([\s\S]*?)<\/title>/i)?.[1]?.replace(/\s+/g, " ").trim() || "";
      const desc = text.match(/<meta\s+name=["']description["']\s+content=["']([^"']+)["']/i)?.[1]?.trim() || "";

      if (!title) addIssue("seo", "high", "missing-title", concept, file, "Missing title.", "Add title.");
      else if (title.length < 30 || title.length > 75) addIssue("seo", "medium", "title-length", concept, file, `Title length ${title.length} outside ideal range.`, "Aim around 30-75 characters.");

      if (!desc) addIssue("seo", "high", "missing-description", concept, file, "Missing meta description.", "Add description.");
      else if (desc.length < 70 || desc.length > 180) addIssue("seo", "medium", "description-length", concept, file, `Description length ${desc.length} outside ideal range.`, "Aim around 70-180 characters.");

      if (!/<link\s+rel=["']canonical["']/i.test(text)) addIssue("seo", "medium", "missing-canonical", concept, file, "Missing canonical.", "Add absolute canonical URL.");
      if (!/property=["']og:title["']/i.test(text)) addIssue("seo", "low", "missing-og-title", concept, file, "Missing OG title.", "Add Open Graph metadata.");

      const jsonLdBlocks = [...text.matchAll(/<script[^>]+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)];
      for (const block of jsonLdBlocks) {
        try {
          JSON.parse(block[1]);
        } catch {
          addIssue("schema", "high", "invalid-json-ld", concept, file, "Invalid JSON-LD schema.", "Fix JSON syntax.");
        }
      }

      const schemaPartial = path.join(dir, "partials", "schema.html");
      if (!jsonLdBlocks.length && !fs.existsSync(schemaPartial)) {
        addIssue("schema", "medium", "missing-schema", concept, file, "No JSON-LD or schema partial detected.", "Add schema partial or inline JSON-LD.");
      }
    }
  }

  if (!fs.existsSync(path.join(ROOT, "robots.txt"))) addIssue("seo", "medium", "missing-robots", "GLOBAL", "robots.txt", "robots.txt missing.", "Create robots.txt.");
  if (!fs.existsSync(path.join(ROOT, "sitemap.xml"))) addIssue("seo", "high", "missing-root-sitemap", "GLOBAL", "sitemap.xml", "Root sitemap.xml missing.", "Generate sitemap.xml.");
}

function auditAccessibilityStatic() {
  for (const dir of conceptDirs()) {
    const concept = path.basename(dir);
    const css = path.join(dir, "css", "style.css");
    const cssText = read(css);

    if (!/:focus-visible|:focus/i.test(cssText)) addIssue("accessibility", "medium", "missing-focus-style", concept, css, "No focus/focus-visible style found.", "Add visible focus states.");
    if (!/prefers-reduced-motion/i.test(cssText)) addIssue("accessibility", "medium", "missing-reduced-motion", concept, css, "No reduced-motion handling.", "Add prefers-reduced-motion block.");

    for (const file of pageFiles(dir)) {
      const text = read(file);

      for (const img of text.match(/<img\b[^>]*>/gi) || []) {
        if (!/\balt=["'][^"']+["']/i.test(img)) addIssue("accessibility", "high", "img-alt", concept, file, "Image missing non-empty alt.", "Add meaningful alt or alt='' for decorative.");
        if (/\balt=["']\s*(image|photo|picture|graphic)\s*["']/i.test(img)) addIssue("accessibility", "medium", "weak-alt", concept, file, "Weak generic alt text.", "Write descriptive alt text.");
      }

      for (const button of text.match(/<button\b[^>]*>[\s\S]*?<\/button>/gi) || []) {
        const clean = button.replace(/<[^>]+>/g, "").trim();
        if (!clean && !/aria-label=/i.test(button)) addIssue("accessibility", "high", "button-name", concept, file, "Button has no accessible name.", "Add visible text or aria-label.");
      }

      if (/tabindex=["'][1-9]/i.test(text)) addIssue("accessibility", "medium", "positive-tabindex", concept, file, "Positive tabindex found.", "Avoid positive tabindex.");
    }
  }
}

function auditLinksAssets() {
  for (const dir of conceptDirs()) {
    const concept = path.basename(dir);

    for (const file of pageFiles(dir)) {
      const text = read(file);
      for (const match of text.matchAll(/\b(href|src)=["']([^"']+)["']/gi)) {
        const attr = match[1];
        const value = match[2];

        if (!value || /^(#|mailto:|tel:|http:\/\/|https:\/\/|whatsapp:|javascript:)/i.test(value)) continue;

        const clean = value.split("#")[0].split("?")[0];
        const target = clean.startsWith("/")
          ? path.join(ROOT, clean.replace(/^\//, ""))
          : path.resolve(path.dirname(file), clean);

        if (!fs.existsSync(target)) {
          addIssue("links-assets", "high", "broken-local-reference", concept, file, `Broken ${attr}: ${value}`, "Fix path or restore missing file.");
        }
      }
    }
  }
}

function auditCssJs() {
  const cssHashes = new Map();
  const headerHashes = new Map();
  const mobileHashes = new Map();
  const footerHashes = new Map();
  const nodeAvailable = !!spawnSync("node", ["--version"], { encoding: "utf8" }).stdout;

  for (const dir of conceptDirs()) {
    const concept = path.basename(dir);
    const css = path.join(dir, "css", "style.css");
    const js = path.join(dir, "js", "main.js");
    const partialsJs = path.join(dir, "js", "partials.js");

    if (fs.existsSync(css)) {
      const text = read(css);
      const cssHash = hash(normalizeHtml(text));
      cssHashes.set(cssHash, [...(cssHashes.get(cssHash) || []), concept]);

      const importantCount = (text.match(/!important/g) || []).length;
      if (importantCount > 20) addIssue("css", "medium", "too-many-important", concept, css, `${importantCount} !important rules found.`, "Reduce specificity problems.");
      if (!/@media/i.test(text)) addIssue("css", "critical", "missing-responsive-css", concept, css, "No media queries found.", "Add responsive CSS.");
      if (/body\s*{[^}]*overflow-x\s*:\s*hidden/is.test(text)) addIssue("css", "low", "body-overflow-hidden", concept, css, "body overflow-x hidden may mask layout bugs.", "Fix overflowing elements instead.");
      if (fs.statSync(css).size > 180000) addIssue("performance", "medium", "large-css", concept, css, `CSS is ${Math.round(fs.statSync(css).size / 1024)}KB.`, "Reduce repeated/unused CSS.");
    }

    for (const file of [js, partialsJs]) {
      if (!fs.existsSync(file)) continue;
      const text = read(file);
      if (/console\.log/i.test(text)) addIssue("js", "low", "console-log", concept, file, "console.log found.", "Remove debug logging.");
      if (path.basename(file) === "main.js" && !/data-lang-switch/i.test(text)) addIssue("js", "high", "missing-language-runtime", concept, file, "Language runtime missing.", "Add language state JS.");
      if (path.basename(file) === "main.js" && !/data-menu-toggle|mobile-menu/i.test(text)) addIssue("js", "high", "missing-menu-runtime", concept, file, "Mobile menu runtime missing.", "Add menu open/close JS.");
      if (fs.statSync(file).size > 120000) addIssue("performance", "medium", "large-js", concept, file, `JS is ${Math.round(fs.statSync(file).size / 1024)}KB.`, "Reduce JS.");

      if (nodeAvailable) {
        const result = spawnSync("node", ["--check", file], { encoding: "utf8" });
        if (result.status !== 0) addIssue("js", "critical", "js-syntax-error", concept, file, result.stderr || result.stdout, "Fix JS syntax.");
      }
    }

    const header = path.join(dir, "partials", "header.html");
    const mobile = path.join(dir, "partials", "mobile-menu.html");
    const footer = path.join(dir, "partials", "footer.html");

    if (fs.existsSync(header)) {
      const h = hash(normalizeHtml(read(header)));
      headerHashes.set(h, [...(headerHashes.get(h) || []), concept]);
    }
    if (fs.existsSync(mobile)) {
      const h = hash(normalizeHtml(read(mobile)));
      mobileHashes.set(h, [...(mobileHashes.get(h) || []), concept]);
    }
    if (fs.existsSync(footer)) {
      const h = hash(normalizeHtml(read(footer)));
      footerHashes.set(h, [...(footerHashes.get(h) || []), concept]);
    }
  }

  for (const [h, names] of cssHashes) {
    if (names.length > 1) addIssue("uniqueness", "high", "duplicate-css-file", "GLOBAL", "concepts/*/css/style.css", `Identical CSS shared by ${names.length} concepts: ${names.slice(0, 20).join(", ")}.`, "Make concepts structurally different.");
  }
  for (const [h, names] of headerHashes) {
    if (names.length > 1) addIssue("uniqueness", "high", "duplicate-header", "GLOBAL", "concepts/*/partials/header.html", `Identical header shared by ${names.length} concepts: ${names.slice(0, 20).join(", ")}.`, "Vary header structure/layout.");
  }
  for (const [h, names] of mobileHashes) {
    if (names.length > 1) addIssue("uniqueness", "high", "duplicate-mobile", "GLOBAL", "concepts/*/partials/mobile-menu.html", `Identical mobile menu shared by ${names.length} concepts: ${names.slice(0, 20).join(", ")}.`, "Vary mobile menu design/build.");
  }
  for (const [h, names] of footerHashes) {
    if (names.length > 1) addIssue("uniqueness", "medium", "duplicate-footer", "GLOBAL", "concepts/*/partials/footer.html", `Identical footer shared by ${names.length} concepts: ${names.slice(0, 20).join(", ")}.`, "Vary footer structure/layout.");
  }
}

function auditPerformanceStatic() {
  for (const dir of conceptDirs()) {
    const concept = path.basename(dir);

    const walk = (folder) => {
      for (const item of fs.readdirSync(folder)) {
        const full = path.join(folder, item);
        const stat = fs.statSync(full);
        if (stat.isDirectory()) walk(full);
        else {
          const ext = path.extname(full).toLowerCase();
          const kb = Math.round(stat.size / 1024);
          if ([".png", ".jpg", ".jpeg", ".webp"].includes(ext) && stat.size > 500000) {
            addIssue("performance", "medium", "large-image", concept, full, `Image is ${kb}KB.`, "Compress/resize image.");
          }
          if (ext === ".svg" && stat.size > 150000) {
            addIssue("performance", "low", "large-svg", concept, full, `SVG is ${kb}KB.`, "Optimize SVG.");
          }
        }
      }
    };

    walk(dir);

    for (const file of pageFiles(dir)) {
      const text = read(file);
      for (const img of text.match(/<img\b[^>]*>/gi) || []) {
        if (!/\sloading=/i.test(img) && !/hero/i.test(img)) addIssue("performance", "low", "missing-lazy-loading", concept, file, "Non-hero image missing loading='lazy'.", "Add loading='lazy'.");
        if (!/\sdecoding=/i.test(img)) addIssue("performance", "low", "missing-decoding-async", concept, file, "Image missing decoding='async'.", "Add decoding='async'.");
      }
    }
  }
}

function auditUxStatic() {
  for (const dir of conceptDirs()) {
    const concept = path.basename(dir);
    const header = path.join(dir, "partials", "header.html");
    const mobile = path.join(dir, "partials", "mobile-menu.html");
    const nav = path.join(dir, "partials", "navigation.html");

    if (fs.existsSync(header)) {
      const text = read(header);
      if (!/Consultation|Consulta/i.test(text)) addIssue("ux-ui", "high", "weak-primary-cta", concept, header, "Header does not visibly include consultation CTA.", "Make consultation the primary action.");
      if ((text.match(/<a\b/gi) || []).length > 12) addIssue("ux-ui", "medium", "crowded-header", concept, header, "Header may be crowded.", "Keep desktop nav clear.");
    }

    if (fs.existsSync(mobile)) {
      const text = read(mobile);
      if ((text.match(/<a\b/gi) || []).length < 6) addIssue("ux-ui", "high", "thin-mobile-menu", concept, mobile, "Mobile menu has too few links.", "Include primary nav links.");
      if (!/aria-hidden/i.test(text)) addIssue("ux-ui", "medium", "mobile-menu-aria-hidden", concept, mobile, "Mobile menu missing aria-hidden.", "Add accessible open/closed state.");
    }

    if (fs.existsSync(nav)) {
      const text = read(nav).replace(/\s+/g, " ");
      for (const label of PRIMARY_NAV) {
        if (!text.includes(label)) addIssue("ux-ui", "high", "missing-nav-label", concept, nav, `Missing ${label}.`, "Keep required navigation labels.");
      }
    }
  }
}

async function startServer() {
  const proc = spawn("python3", ["-m", "http.server", String(PORT)], {
    cwd: ROOT,
    stdio: "ignore",
  });

  await new Promise((resolve) => setTimeout(resolve, 1200));
  return proc;
}

async function renderedAudit() {
  const server = await startServer();
  const browser = await chromium.launch({ headless: true });

  try {
    const viewports = [
      { name: "mobile-390", width: 390, height: 844, isMobile: true },
      { name: "desktop-1366", width: 1366, height: 960, isMobile: false },
    ];

    for (const dir of conceptDirs()) {
      const concept = path.basename(dir);
      for (const pageFile of pageFiles(dir, true)) {
        const pageName = path.basename(pageFile);
        for (const vp of viewports) {
          const context = await browser.newContext({
            viewport: { width: vp.width, height: vp.height },
            isMobile: vp.isMobile,
          });

          const page = await context.newPage();
          const consoleErrors = [];
          page.on("console", (msg) => {
            if (msg.type() === "error") consoleErrors.push(msg.text());
          });
          page.on("pageerror", (error) => consoleErrors.push(error.message));

          const url = `${BASE_URL}/concepts/${concept}/${pageName}`;

          try {
            await page.goto(url, { waitUntil: "networkidle", timeout: 25000 });
            await page.waitForTimeout(500);

            const metrics = await page.evaluate(async ({ primaryNav, isMobile }) => {
              const visible = (node) => {
                if (!node) return false;
                const style = getComputedStyle(node);
                const rect = node.getBoundingClientRect();
                return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
              };

              const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

              const html = document.documentElement;
              const body = document.body;
              const pageOverflow = Math.max(html.scrollWidth, body.scrollWidth) - window.innerWidth;
              const header = document.querySelector(".public-header");
              const footer = document.querySelector("footer, .public-footer");
              const utility = document.querySelector(".public-utility, .status-banner");
              const cta = document.querySelector(".header-consultation");
              const h1Count = document.querySelectorAll("h1").length;

              const navLinks = Array.from(document.querySelectorAll(".public-header .desktop-nav a, .desktop-nav a")).filter(visible);
              const navLabels = navLinks.map((a) => (a.textContent || "").trim());
              const navRows = new Set(navLinks.map((a) => Math.round(a.getBoundingClientRect().top))).size;

              let languageWorks = true;
              const pt = document.querySelector('[data-lang-switch="pt"]');
              const en = document.querySelector('[data-lang-switch="en"]');
              if (pt && en) {
                pt.click();
                await wait(180);
                const ptWorks = pt.getAttribute("aria-pressed") === "true" && document.documentElement.lang === "pt-BR";
                en.click();
                await wait(180);
                const enWorks = en.getAttribute("aria-pressed") === "true" && document.documentElement.lang === "en";
                languageWorks = ptWorks && enWorks;
              }

              let mobileMenuWorks = true;
              if (isMobile) {
                const toggle = document.querySelector("[data-menu-toggle]");
                const menu = document.querySelector("#mobile-menu");
                if (toggle && menu) {
                  toggle.click();
                  await wait(180);
                  const open = menu.classList.contains("is-open") && menu.getAttribute("aria-hidden") === "false" && visible(menu);
                  const close = menu.querySelector("[data-menu-close]");
                  close?.click();
                  await wait(180);
                  const closed = !menu.classList.contains("is-open") && menu.getAttribute("aria-hidden") === "true";
                  mobileMenuWorks = open && closed;
                } else {
                  mobileMenuWorks = false;
                }
              }

              return {
                pageOverflow,
                headerVisible: visible(header),
                footerVisible: visible(footer),
                utilityVisible: visible(utility),
                ctaVisible: visible(cta),
                h1Count,
                title: document.title,
                navLabels,
                navRows,
                missingNav: primaryNav.filter((label) => !navLabels.includes(label)),
                languageWorks,
                mobileMenuWorks,
              };
            }, { primaryNav: PRIMARY_NAV, isMobile: vp.isMobile });

            if (metrics.pageOverflow > 2) addIssue("rendered", "critical", "rendered-overflow", concept, `${pageName} ${vp.name}`, `Horizontal overflow ${Math.round(metrics.pageOverflow)}px.`, "Fix layout width.");
            if (!metrics.headerVisible) addIssue("rendered", "critical", "header-not-visible", concept, `${pageName} ${vp.name}`, "Header not visible after render.", "Fix partial loading/header CSS.");
            if (!metrics.footerVisible) addIssue("rendered", "high", "footer-not-visible", concept, `${pageName} ${vp.name}`, "Footer not visible after render.", "Fix footer partial/rendering.");
            if (!metrics.utilityVisible) addIssue("rendered", "high", "utility-not-visible", concept, `${pageName} ${vp.name}`, "Utility/status bar not visible.", "Fix status-banner partial/rendering.");
            if (!metrics.ctaVisible) addIssue("rendered", "high", "cta-not-visible", concept, `${pageName} ${vp.name}`, "Consultation CTA not visible.", "Fix header CTA.");
            if (metrics.h1Count !== 1) addIssue("rendered", "high", "rendered-h1-count", concept, `${pageName} ${vp.name}`, `Rendered H1 count is ${metrics.h1Count}.`, "Keep one rendered H1.");
            if (!metrics.languageWorks) addIssue("rendered", "high", "rendered-language-toggle", concept, `${pageName} ${vp.name}`, "Rendered EN/PT toggle failed.", "Fix language runtime/partials.");
            if (!metrics.mobileMenuWorks) addIssue("rendered", "critical", "rendered-mobile-menu", concept, `${pageName} ${vp.name}`, "Rendered mobile menu failed.", "Fix menu runtime/partials.");
            if (!vp.isMobile && metrics.navRows > 1) addIssue("rendered", "medium", "desktop-nav-wrap", concept, `${pageName} ${vp.name}`, `Desktop nav wraps into ${metrics.navRows} rows.`, "Adjust desktop nav spacing.");
            if (!vp.isMobile && metrics.missingNav.length) addIssue("rendered", "high", "rendered-missing-nav", concept, `${pageName} ${vp.name}`, `Missing nav labels: ${metrics.missingNav.join(", ")}.`, "Fix nav partial.");

            for (const err of consoleErrors.slice(0, 5)) {
              addIssue("rendered", "high", "browser-console-error", concept, `${pageName} ${vp.name}`, err.replace(/\s+/g, " "), "Fix runtime error.");
            }

            await page.addScriptTag({ content: axeCore.source });
            const axe = await page.evaluate(async () => {
              return await axe.run(document, {
                resultTypes: ["violations"],
                runOnly: {
                  type: "tag",
                  values: ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"],
                },
              });
            });

            for (const violation of axe.violations.filter((v) => ["critical", "serious"].includes(v.impact)).slice(0, 12)) {
              addIssue("axe", violation.impact === "critical" ? "critical" : "high", `axe-${violation.id}`, concept, `${pageName} ${vp.name}`, `${violation.help} (${violation.nodes.length} nodes).`, violation.helpUrl);
            }

            if (RUN_SCREENSHOTS && pageName === "index.html") {
              const shotDir = path.join(SCREENSHOT_DIR, vp.name);
              fs.mkdirSync(shotDir, { recursive: true });
              await page.screenshot({
                path: path.join(shotDir, `${concept}-${vp.name}.png`),
                fullPage: true,
              });
            }
          } catch (error) {
            addIssue("rendered", "critical", "rendered-load-error", concept, `${pageName} ${vp.name}`, String(error.message || error), "Fix page load/runtime.");
          }

          await context.close();
        }
      }
    }
  } finally {
    await browser.close();
    server.kill();
  }
}

function lighthouseBinary() {
  const local = path.join(ROOT, "node_modules", ".bin", process.platform === "win32" ? "lighthouse.cmd" : "lighthouse");
  return fs.existsSync(local) ? local : "lighthouse";
}

function lighthouseTargets() {
  const chosen = RUN_LIGHTHOUSE_MORE
    ? ["01-inspire", "05-elevate", "10-essence", "15-clarity", "20-halo", "25-align", "30-method", "35-atelier", "40-noble", "45-silhouette", "50-sovereign"]
    : ["01-inspire", "10-essence", "20-halo", "30-method", "40-noble", "50-sovereign"];

  return chosen.map((concept) => ({
    concept,
    page: "index.html",
    url: `${BASE_URL}/concepts/${concept}/index.html`,
  }));
}

async function runLighthouse() {
  const server = await startServer();
  const bin = lighthouseBinary();
  const outDir = path.join(REPORT_DIR, "lighthouse");
  fs.mkdirSync(outDir, { recursive: true });

  try {
    for (const target of lighthouseTargets()) {
      const outBase = path.join(outDir, `${target.concept}-index`);
      const result = spawnSync(bin, [
        target.url,
        "--output=json",
        "--output=html",
        `--output-path=${outBase}`,
        "--quiet",
        "--chrome-flags=--headless --no-sandbox",
      ], {
        cwd: ROOT,
        encoding: "utf8",
        timeout: 120000,
      });

      if (result.status !== 0) {
        addIssue("lighthouse", "medium", "lighthouse-run-failed", target.concept, target.page, result.stderr || result.stdout || "Lighthouse failed.", "Check local Chrome/Lighthouse setup.");
        continue;
      }

      const jsonPath = `${outBase}.report.json`;
      if (fs.existsSync(jsonPath)) {
        const data = JSON.parse(read(jsonPath));
        for (const [key, category] of Object.entries(data.categories || {})) {
          const score = Math.round((category.score ?? 0) * 100);
          if (score < 90) {
            addIssue("lighthouse", "medium", "lighthouse-low-score", target.concept, target.page, `${category.title}: ${score}/100.`, "Review Lighthouse report.");
          }
        }
      }
    }
  } finally {
    server.kill();
  }
}

async function runPageSpeed() {
  if (!PSI_BASE) return;

  const targets = ["01-inspire", "10-essence", "20-halo", "30-method", "40-noble", "50-sovereign"];
  for (const concept of targets) {
    const url = `${PSI_BASE.replace(/\/$/, "")}/concepts/${concept}/index.html`;
    const api = `https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url=${encodeURIComponent(url)}&strategy=mobile&category=performance&category=accessibility&category=best-practices&category=seo`;

    try {
      const response = await fetch(api);
      if (!response.ok) {
        addIssue("pagespeed", "medium", "pagespeed-request-failed", concept, url, `PageSpeed failed with HTTP ${response.status}.`, "Check deployed URL or try later.");
        continue;
      }

      const data = await response.json();
      const cats = data.lighthouseResult?.categories || {};
      for (const [key, cat] of Object.entries(cats)) {
        const score = Math.round((cat.score ?? 0) * 100);
        if (score < 90) {
          addIssue("pagespeed", "medium", "pagespeed-low-score", concept, url, `${cat.title}: ${score}/100.`, "Open PageSpeed report and optimize.");
        }
      }
    } catch (error) {
      addIssue("pagespeed", "medium", "pagespeed-error", concept, url, String(error.message || error), "Check internet/deployed URL.");
    }
  }
}

function runStaticAudits() {
  auditInventory();
  auditPartials();
  auditPagesSections();
  auditSeoSchema();
  auditAccessibilityStatic();
  auditLinksAssets();
  auditCssJs();
  auditPerformanceStatic();
  auditUxStatic();
}

function severityCounts(items) {
  const counts = { critical: 0, high: 0, medium: 0, low: 0 };
  for (const item of items) {
    counts[item.severity] = (counts[item.severity] || 0) + 1;
  }
  return counts;
}

function groupCount(items, key) {
  const map = new Map();
  for (const item of items) {
    map.set(item[key], (map.get(item[key]) || 0) + 1);
  }
  return [...map.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
}

function writeReports(backupPath = "") {
  const master = path.join(REPORT_DIR, "MASTER-COMPREHENSIVE-QA.md");
  const json = path.join(REPORT_DIR, "MASTER-COMPREHENSIVE-QA.json");
  const counts = severityCounts(issues);
  const autoFixable = issues.filter((i) => i.autoFixable);
  const manual = issues.filter((i) => !i.autoFixable);

  fs.writeFileSync(json, JSON.stringify({ issues, changes }, null, 2));

  const lines = [];
  lines.push("# Sofiati Comprehensive QA, Rendered, Lighthouse and Refactor Report");
  lines.push("");
  lines.push(`Generated: ${new Date().toISOString()}`);
  lines.push("");
  lines.push(`Safe fixes applied: ${FIX_SAFE ? "yes" : "no"}`);
  lines.push(`Aggressive fixes applied: ${FIX_AGGRESSIVE ? "yes" : "no"}`);
  if (backupPath) lines.push(`Backup: \`${rel(backupPath)}\``);
  lines.push("");
  lines.push(`Total issues: ${issues.length}`);
  lines.push("");
  lines.push(`- Critical: ${counts.critical}`);
  lines.push(`- High: ${counts.high}`);
  lines.push(`- Medium: ${counts.medium}`);
  lines.push(`- Low: ${counts.low}`);
  lines.push(`- Auto-fixable/repeated structural: ${autoFixable.length}`);
  lines.push(`- Manual/design/content/performance judgement: ${manual.length}`);
  lines.push("");
  lines.push("## Files changed by safe fixes");
  lines.push("");
  if (changes.length) {
    for (const item of [...new Set(changes)].sort()) lines.push(`- \`${item}\``);
  } else {
    lines.push("No files changed.");
  }

  lines.push("");
  lines.push("## Issues by aspect");
  lines.push("");
  lines.push("| Aspect | Count |");
  lines.push("| --- | ---: |");
  for (const [aspect, count] of groupCount(issues, "aspect")) lines.push(`| ${aspect} | ${count} |`);

  lines.push("");
  lines.push("## Issues by kind");
  lines.push("");
  lines.push("| Kind | Count |");
  lines.push("| --- | ---: |");
  for (const [kind, count] of groupCount(issues, "kind")) lines.push(`| ${kind} | ${count} |`);

  lines.push("");
  lines.push("## Auto-fixable / structural issues");
  lines.push("");
  lines.push("| Severity | Aspect | Kind | Concept | File | Detail | Fix |");
  lines.push("| --- | --- | --- | --- | --- | --- | --- |");
  for (const item of autoFixable) {
    lines.push(`| ${item.severity} | ${item.aspect} | ${item.kind} | ${item.concept} | \`${item.file}\` | ${item.detail.replaceAll("|", "\\|")} | ${item.fix.replaceAll("|", "\\|")} |`);
  }

  lines.push("");
  lines.push("## Manual design, content, uniqueness and performance-refactor issues");
  lines.push("");
  lines.push("| Severity | Aspect | Kind | Concept | File | Detail | Recommendation |");
  lines.push("| --- | --- | --- | --- | --- | --- | --- |");
  for (const item of manual) {
    lines.push(`| ${item.severity} | ${item.aspect} | ${item.kind} | ${item.concept} | \`${item.file}\` | ${item.detail.replaceAll("|", "\\|")} | ${item.fix.replaceAll("|", "\\|")} |`);
  }

  fs.writeFileSync(master, lines.join("\n"));
  console.log(`Report written: ${rel(master)}`);
  console.log(`JSON written: ${rel(json)}`);
}

async function main() {
  console.log("Sofiati comprehensive QA started.");

  let backupPath = "";

  if (FIX_SAFE) {
    console.log("Applying safe fixes with backup...");
    backupPath = applySafeFixes();
    console.log(`Backup created: ${rel(backupPath)}`);
    console.log(`Changed files: ${new Set(changes).size}`);
  }

  console.log("Running static audits...");
  runStaticAudits();

  if (RUN_RENDERED) {
    console.log("Running rendered Playwright + axe audits...");
    await renderedAudit();
  }

  if (RUN_LIGHTHOUSE) {
    console.log("Running selected Lighthouse audits...");
    await runLighthouse();
  }

  if (PSI_BASE) {
    console.log("Running deployed PageSpeed Insights checks...");
    await runPageSpeed();
  }

  writeReports(backupPath);

  const counts = severityCounts(issues);
  console.log(`Total issues: ${issues.length}`);
  console.log(`Critical: ${counts.critical}, High: ${counts.high}, Medium: ${counts.medium}, Low: ${counts.low}`);
  console.log("Done.");
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
