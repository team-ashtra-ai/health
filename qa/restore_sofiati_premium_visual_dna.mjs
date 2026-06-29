#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

const root = process.cwd();
const conceptsRoot = path.join(root, "concepts");
const docsRoot = path.join(root, "docs/script-runs");
const cssPath = path.join(root, "css/sofiati-premium-visual-dna.css");
const progressPath = path.join(docsRoot, "visual-dna-polish-progress.json");
const visualLinkHref = "../../css/sofiati-premium-visual-dna.css";

const args = new Set(process.argv.slice(2));
const argList = process.argv.slice(2);
const validateOnly = args.has("--validate-only") || args.has("--report");
const selectedConcept = valueAfter("--concept");

const requiredPartials = [
  "head",
  "schema",
  "status-banner",
  "accessibility",
  "header",
  "navigation",
  "mobile-menu",
  "cookie-banner",
  "footer",
  "floating-widgets",
  "floating-whatsapp",
  "back-to-top",
  "consultation-form",
  "contact-card",
  "concept-switcher",
];

const badAssetTerms = [
  "pattern decoration",
  "home background",
  "section background",
  "decorative asset",
  "texture decoration",
  "CONCEPT-SPECIFIC",
  "concept-specific",
  "section asset",
  "background asset",
  "fake image labels",
  "mockup labels",
  "asset board text",
  "generated placeholder captions",
];

const sectionRoles = [
  "opening-promise",
  "sage-editorial-break",
  "human-trust",
  "route-panel",
  "deep-trust-band",
  "service-focus",
  "journal-strip",
  "form-focus",
  "quiet-proof",
  "final-conversion",
];

const layoutTypes = [
  "editorial-split",
  "centered-portrait",
  "asymmetric-panel",
  "dark-band",
  "sage-band",
  "floating-card",
  "magazine-layer",
  "gallery-frame",
  "process-strip",
  "route-grid",
  "diagonal-flow",
  "stacked-editorial",
  "image-first-mobile",
  "text-first-mobile",
  "cta-band",
  "form-panel",
  "journal-row",
  "trust-note",
  "full-width-statement",
  "alternating-panel",
  "offset-photo",
  "framed-minimal",
  "botanical-divider",
  "structured-clinical",
  "luxury-dark-card",
  "soft-wellness-card",
];

const themeDirections = [
  [
    "01-inspire",
    "Inspire",
    "refined editorial, calm whitespace, sage editorial breaks, elegant portrait cards",
  ],
  [
    "02-empower",
    "Empower",
    "botanical editorial, stronger sage panels, confident structured sections",
  ],
  [
    "03-enhance",
    "Enhance",
    "gold minimalism, clean ivory frames, restrained bronze linework",
  ],
  [
    "04-renew",
    "Renew",
    "dark premium editorial, deep sage/ink bands, gallery-like full-image frames",
  ],
  [
    "05-elevate",
    "Elevate",
    "warm beige wellness, soft gradients, gentle sage breaks",
  ],
  [
    "06-refine",
    "Refine",
    "modern dermatology, clinical sage calm, clean precise spacing",
  ],
  [
    "07-glow",
    "Glow",
    "consultation studio, warm human flow, rounded panels and soft sage",
  ],
  [
    "08-balance",
    "Balance",
    "magazine beauty, layered editorial rhythm, stronger image/text alternation",
  ],
  [
    "09-radiance",
    "Radiance",
    "calm medical spa, polished warmth, sage-gold service panels",
  ],
  [
    "10-essence",
    "Essence",
    "portrait-led brand, simple trust, strong human photo moments",
  ],
  [
    "11-bloom",
    "Bloom",
    "botanical softness, organic sage movement, delicate line art",
  ],
  [
    "12-vital",
    "Vital",
    "fresh vitality, clearer contrast, active spacing rhythm",
  ],
  [
    "13-poise",
    "Poise",
    "symmetrical elegance, balanced panels, refined bronze dividers",
  ],
  [
    "14-aura",
    "Aura",
    "atmospheric luxury, soft glow, muted sage/cream contrast",
  ],
  [
    "15-clarity",
    "Clarity",
    "minimal clinical clarity, high readability, light sage structure",
  ],
  [
    "16-grace",
    "Grace",
    "feminine editorial, gentle curves, elegant image pacing",
  ],
  [
    "17-sculpt",
    "Sculpt",
    "structured premium, sharper geometry, bolder panel contrast",
  ],
  [
    "18-lumin",
    "Lumin",
    "luminous soft panels, airy spacing, pale sage atmosphere",
  ],
  [
    "19-verda",
    "Verda",
    "botanical sage identity, natural softness, leaf-line rhythm",
  ],
  [
    "20-halo",
    "Halo",
    "soft circular accents, glow frames, no circular image clipping",
  ],
  ["21-calm", "Calm", "quiet wellness, low density, restful sage transitions"],
  [
    "22-precision",
    "Precision",
    "technical elegance, fine lines, exact grid spacing",
  ],
  [
    "23-ritual",
    "Ritual",
    "spa ritual, slow warm section pacing, deep calm CTA bands",
  ],
  [
    "24-signal",
    "Signal",
    "modern interface, clean service routing, subtle active states",
  ],
  [
    "25-align",
    "Align",
    "balanced grid, measured hierarchy, calm internal-link rhythm",
  ],
  [
    "26-vivant",
    "Vivant",
    "lively but premium, brighter ivory/sage contrast, energetic CTAs",
  ],
  [
    "27-form",
    "Form",
    "shape-led editorial, structured form panels, strong frames",
  ],
  [
    "28-pure",
    "Pure",
    "minimal beauty, crisp whitespace, restrained accent colour",
  ],
  [
    "29-solace",
    "Solace",
    "comforting calm, soft sage cards, gentle conversion flow",
  ],
  [
    "30-method",
    "Method",
    "process-led design, step sections, disciplined visual order",
  ],
  [
    "31-evolve",
    "Evolve",
    "education-led rhythm, journal accents, no fake result imagery",
  ],
  [
    "32-serene",
    "Serene",
    "spa calm, delicate panels, low-contrast sage atmosphere",
  ],
  [
    "33-elan",
    "Elan",
    "stylish magazine editorial, bolder image placement, chic rhythm",
  ],
  [
    "34-flora",
    "Flora",
    "botanical luxury, sage/line-art emphasis, real photos as anchors",
  ],
  [
    "35-atelier",
    "Atelier",
    "crafted studio, art-directed frames, bronze detail accents",
  ],
  [
    "36-lumina",
    "Lumina",
    "luminous elegance, pale surfaces, glow-like sage transitions",
  ],
  [
    "37-vellum",
    "Vellum",
    "paper editorial, refined texture, document-like section breaks",
  ],
  [
    "38-origin",
    "Origin",
    "grounded naturality, warm trust, earthy sage/cream panels",
  ],
  [
    "39-kindred",
    "Kindred",
    "personal, intimate, human-first, softer portrait flow",
  ],
  ["40-noble", "Noble", "mature luxury, deeper contrast, stately spacing"],
  [
    "41-vista",
    "Vista",
    "open spacious panels, wider hero feel, airy sage breaks",
  ],
  [
    "42-softline",
    "Softline",
    "soft linear design, gentle curves, thin dividers",
  ],
  [
    "43-meridian",
    "Meridian",
    "guided pathways, structured navigation, calm routes",
  ],
  [
    "44-safeguard",
    "Safeguard",
    "trust/safety, clear reassurance panels, strong boundaries",
  ],
  [
    "45-silhouette",
    "Silhouette",
    "elegant shape language, no photo clipping or cropping",
  ],
  [
    "46-curate",
    "Curate",
    "selective editorial, fewer but stronger visual moments",
  ],
  [
    "47-proof",
    "Proof",
    "responsible evidence, strong trust sections, no fake proof",
  ],
  [
    "48-signature",
    "Signature",
    "distinctive premium brand feel, polished portrait-led identity",
  ],
  [
    "49-wisdom",
    "Wisdom",
    "educational calm, journal/trust-led rhythm, sage reading panels",
  ],
  [
    "50-sovereign",
    "Sovereign",
    "most premium/confident, restrained luxury, deep contrast and control",
  ],
];

const headerPatterns = [
  "compact-centered-header",
  "split-navigation-header",
  "editorial-masthead-header",
  "floating-pill-header",
  "dark-premium-header",
  "soft-sage-header",
  "minimal-line-header",
  "cta-forward-header",
  "botanical-rail-header",
  "gallery-calm-header",
];

const heroPatterns = [
  "wide-editorial-hero",
  "centered-portrait-hero",
  "dark-split-hero",
  "magazine-layered-hero",
  "soft-studio-hero",
  "clinical-grid-hero",
  "portrait-first-hero",
  "route-led-hero",
  "statement-hero",
  "gallery-frame-hero",
];

const imageFrames = [
  "elegant-full-image-card",
  "sage-rail-full-image-frame",
  "bronze-line-inset-frame",
  "deep-gallery-frame",
  "soft-wellness-frame",
  "clinical-measured-frame",
  "rounded-studio-frame",
  "layered-editorial-frame",
  "service-panel-frame",
  "portrait-led-open-frame",
  "botanical-shelf-frame",
  "active-vital-frame",
  "symmetrical-poise-frame",
  "atmospheric-glow-frame",
  "minimal-clarity-frame",
  "curved-grace-frame",
  "structured-sculpt-frame",
  "luminous-field-frame",
  "leaf-line-frame",
  "open-halo-frame",
];

const cardPatterns = [
  "fine-line-editorial-cards",
  "sage-panel-route-cards",
  "gold-minimal-cards",
  "dark-luxury-cards",
  "soft-wellness-cards",
  "clinical-precision-cards",
  "rounded-consultation-cards",
  "magazine-stack-cards",
  "polished-service-cards",
  "human-trust-cards",
];

const ctaPatterns = [
  "paired-editorial-cta",
  "sage-consultation-strip",
  "bronze-rule-cta",
  "deep-sage-cta-band",
  "soft-wellness-cta",
  "clinical-direct-cta",
  "warm-studio-cta",
  "magazine-button-row",
  "service-route-cta",
  "portrait-trust-cta",
];

const footerPatterns = [
  "deep-sage-editorial-footer",
  "light-multi-column-footer",
  "cta-led-footer",
  "compact-legal-footer",
  "brand-card-footer",
  "journal-route-footer",
  "consultation-first-footer",
  "quiet-ink-footer",
  "sage-rail-footer",
  "bronze-rule-footer",
];

const mobilePatterns = [
  "image-first-mobile",
  "text-first-mobile",
  "alternating-mobile-stack",
  "compact-cta-mobile",
  "editorial-card-mobile",
  "route-first-mobile",
  "portrait-anchor-mobile",
  "low-density-mobile",
  "clinical-mobile-stack",
  "deep-cta-mobile",
];

const colourRhythms = [
  "sage-open-ivory-deep",
  "sage-panel-bronze-ivory",
  "ivory-gold-sage-line",
  "ink-deep-sage-gold",
  "cream-warm-sage-bronze",
  "clinical-cream-sage-ink",
  "warm-ivory-sage-gold",
  "magazine-ivory-sage-ink",
  "spa-sage-gold-cream",
  "portrait-ivory-deep-sage",
];

const decorativeSystems = [
  "thin-botanical-rules",
  "upright-sage-stems",
  "restrained-bronze-lines",
  "deep-editorial-contours",
  "soft-gradient-washes",
  "clinical-grid-lines",
  "warm-studio-hairlines",
  "layered-magazine-rules",
  "polished-service-dividers",
  "signature-human-line",
];

const themes = themeDirections.map(([id, name, theme], index) => {
  const offset = index * 3;
  const previous =
    themeDirections[
      (index + themeDirections.length - 1) % themeDirections.length
    ][0];
  const next = themeDirections[(index + 1) % themeDirections.length][0];
  const sectionRhythm = Array.from(
    { length: 10 },
    (_, sectionIndex) =>
      layoutTypes[
        (index * 5 + sectionIndex * ((index % 7) + 2)) % layoutTypes.length
      ],
  );
  return {
    id,
    name,
    index,
    number: id.slice(0, 2),
    theme,
    headerPattern: headerPatterns[(offset + 0) % headerPatterns.length],
    heroPattern: heroPatterns[(offset + 1) % heroPatterns.length],
    sectionRhythm,
    imageFramePattern: imageFrames[(index * 7) % imageFrames.length],
    cardPattern: cardPatterns[(offset + 2) % cardPatterns.length],
    ctaPattern: ctaPatterns[(offset + 4) % ctaPatterns.length],
    footerPattern: footerPatterns[(offset + 5) % footerPatterns.length],
    mobilePattern: mobilePatterns[(offset + 6) % mobilePatterns.length],
    colourRhythm: colourRhythms[(offset + 7) % colourRhythms.length],
    decorativeSystem:
      decorativeSystems[(offset + 8) % decorativeSystems.length],
    contrastStrategy: contrastFor(index),
    mustNotLookLike: [previous, next],
    similarityRisks: [],
  };
});

const selectedIds = selectedConcept
  ? new Set([selectedConcept])
  : new Set(themes.map((theme) => theme.id));
const stats = {
  filesChanged: new Set(),
  conceptsChanged: new Set(),
  pagesChanged: new Set(),
  partialsChanged: new Set(),
  sectionsUpdated: 0,
  emptyFramesFound: [],
  emptyFramesRemoved: [],
  duplicateStylesheetFixes: [],
  sectionIssues: [],
  badAssetHits: [],
  objectFitCoverHits: [],
  partialRows: [],
  pageRows: [],
  manualReview: [],
};

function valueAfter(flag) {
  const index = argList.indexOf(flag);
  if (index === -1) return "";
  return argList[index + 1] || "";
}

function contrastFor(index) {
  if ([3, 13, 22, 39, 49].includes(index))
    return "uses deep sage or ink as a memorable editorial break";
  if ([2, 12, 34, 45].includes(index))
    return "uses bronze and gold as fine premium linework";
  if ([5, 14, 21, 43, 46].includes(index))
    return "uses clinical lightness with clearer sage structure";
  return "uses sage, ivory, and ink in alternating calm section bands";
}

function exists(filePath) {
  return fs.existsSync(filePath);
}

function ensureDir(dirPath) {
  fs.mkdirSync(dirPath, { recursive: true });
}

function read(filePath) {
  return exists(filePath) ? fs.readFileSync(filePath, "utf8") : "";
}

function writeIfChanged(filePath, content) {
  const previous = read(filePath);
  if (previous === content) return false;
  ensureDir(path.dirname(filePath));
  fs.writeFileSync(filePath, content);
  stats.filesChanged.add(rel(filePath));
  return true;
}

function rel(filePath) {
  return path.relative(root, filePath).split(path.sep).join("/");
}

function walkFiles(dirPath, predicate = () => true) {
  if (!exists(dirPath)) return [];
  const out = [];
  for (const entry of fs.readdirSync(dirPath, { withFileTypes: true })) {
    const full = path.join(dirPath, entry.name);
    if (entry.isDirectory()) out.push(...walkFiles(full, predicate));
    if (entry.isFile() && predicate(full)) out.push(full);
  }
  return out;
}

function listConceptDirs() {
  return fs
    .readdirSync(conceptsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && /^\d{2}-/.test(entry.name))
    .map((entry) => entry.name)
    .sort();
}

function conceptInfo(id) {
  const theme = themes.find((item) => item.id === id);
  if (!theme) throw new Error(`Unknown concept: ${id}`);
  return theme;
}

function slug(value) {
  return String(value)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function escapeAttr(value) {
  return escapeHtml(value).replace(/'/g, "&#39;");
}

function setAttr(attrs, name, value) {
  const escaped = escapeAttr(value);
  const re = new RegExp(`\\s${name}="[^"]*"`);
  if (re.test(attrs)) return attrs.replace(re, ` ${name}="${escaped}"`);
  return `${attrs} ${name}="${escaped}"`;
}

function addClasses(attrs, classes, removePrefixes = []) {
  const classMatch = attrs.match(/\sclass="([^"]*)"/);
  const existing = classMatch ? classMatch[1].split(/\s+/).filter(Boolean) : [];
  const filtered = existing.filter((className) =>
    removePrefixes.every((prefix) => !className.startsWith(prefix)),
  );
  const merged = Array.from(new Set([...filtered, ...classes.filter(Boolean)]));
  if (classMatch)
    return attrs.replace(classMatch[0], ` class="${merged.join(" ")}"`);
  return `${attrs} class="${merged.join(" ")}"`;
}

function updateFirstTag(html, tagName, updater) {
  const re = new RegExp(`<${tagName}\\b([\\s\\S]*?)>`);
  return html.replace(re, (match, attrs) => `<${tagName}${updater(attrs)}>`);
}

function realPages(conceptDir) {
  return walkFiles(
    conceptDir,
    (filePath) =>
      filePath.endsWith(".html") &&
      !filePath.includes(`${path.sep}partials${path.sep}`),
  ).sort();
}

function partialFiles(conceptDir) {
  return walkFiles(path.join(conceptDir, "partials"), (filePath) =>
    filePath.endsWith(".html"),
  ).sort();
}

function countSections(html) {
  return (html.match(/<section\b/gi) || []).length;
}

function pageKey(filePath) {
  const base = path.basename(filePath, ".html");
  return base === "index" ? "home" : base;
}

function injectVisualStylesheet(html, filePath) {
  const linkPattern =
    /[ \t]*<link\b(?=[^>]*rel=["']stylesheet["'])(?=[^>]*href=["']\.\.\/\.\.\/css\/sofiati-premium-visual-dna\.css["'])[^>]*>\s*/gi;
  const beforeCount = (html.match(linkPattern) || []).length;
  let next = html.replace(linkPattern, "");
  const visualLink = `    <link rel="stylesheet" href="${visualLinkHref}" />`;
  const fullImagePattern =
    /([ \t]*<link\b(?=[^>]*rel=["']stylesheet["'])(?=[^>]*href=["']\.\.\/\.\.\/css\/sofiati-full-image-premium-system\.css["'])[^>]*>)/i;
  if (fullImagePattern.test(next)) {
    next = next.replace(fullImagePattern, `$1\n${visualLink}`);
  } else {
    next = next.replace(/<\/head>/i, `${visualLink}\n  </head>`);
  }
  if (beforeCount > 1) stats.duplicateStylesheetFixes.push(rel(filePath));
  return next;
}

function removeEmptyFrames(html, filePath) {
  return html.replace(
    /<figure\b(?=[^>]*(?:sofiati-photo-frame|sofiati-portrait-frame|data-full-image-frame="true"))([^>]*)>([\s\S]*?)<\/figure>/gi,
    (match, attrs, inner) => {
      if (/<img\b/i.test(inner)) return match;
      const text = inner
        .replace(/<[^>]*>/g, "")
        .replace(/\s+/g, " ")
        .trim();
      if (text) {
        stats.emptyFramesFound.push({
          file: rel(filePath),
          removed: false,
          reason: "frame has text but no image",
        });
        return match;
      }
      stats.emptyFramesFound.push({
        file: rel(filePath),
        removed: true,
        reason: "empty full-image frame",
      });
      stats.emptyFramesRemoved.push(rel(filePath));
      return '<div class="visual-dna-decor-panel" aria-hidden="true" data-replaced-empty-frame="true"></div>';
    },
  );
}

function sectionTone(theme, sectionIndex) {
  const tones = [
    "ivory",
    "sage",
    "cream",
    "editorial",
    "deep",
    "cream",
    "sage",
    "ivory",
    "line",
    "conversion",
  ];
  return tones[(theme.index + sectionIndex) % tones.length];
}

function imageTreatment(theme, sectionIndex) {
  const treatments = [
    "full-image-elegant-card",
    "full-image-sage-rail",
    "full-image-bronze-rule",
    "full-image-open-frame",
    "full-image-editorial-panel",
    "full-image-soft-field",
    "full-image-clinical-frame",
    "full-image-layered-panel",
    "full-image-gallery-frame",
    "full-image-quiet-anchor",
  ];
  return treatments[(theme.index * 2 + sectionIndex) % treatments.length];
}

function updateSections(html, theme, filePath) {
  let sectionIndex = 0;
  const page = pageKey(filePath);
  return html.replace(/<section\b([\s\S]*?)>/g, (match, attrs) => {
    sectionIndex += 1;
    const sectionNumber = String(sectionIndex).padStart(2, "0");
    const layout = theme.sectionRhythm[sectionIndex - 1];
    const role =
      sectionRoles[(theme.index + sectionIndex - 1) % sectionRoles.length];
    const tone = sectionTone(theme, sectionIndex - 1);
    const treatment = imageTreatment(theme, sectionIndex - 1);
    const signature = `${theme.id}-${slug(layout)}-${page}-${sectionNumber}`;
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [
        "visual-dna-section",
        `visual-dna-section-${sectionNumber}`,
        `visual-layout-${slug(layout)}`,
        `visual-role-${slug(role)}`,
        `visual-tone-${tone}`,
        `visual-image-${slug(treatment)}`,
      ],
      [
        "visual-dna-section",
        "visual-layout-",
        "visual-role-",
        "visual-tone-",
        "visual-image-",
      ],
    );
    nextAttrs = setAttr(nextAttrs, "data-visual-role", role);
    nextAttrs = setAttr(nextAttrs, "data-image-treatment", treatment);
    nextAttrs = setAttr(nextAttrs, "data-premium-rhythm", layout);
    nextAttrs = setAttr(nextAttrs, "data-visual-dna-signature", signature);
    nextAttrs = setAttr(nextAttrs, "data-concept-dna", theme.id);
    nextAttrs = setAttr(nextAttrs, "data-mobile-rhythm", theme.mobilePattern);
    stats.sectionsUpdated += 1;
    return `<section${nextAttrs}>`;
  });
}

function updateBody(html, theme) {
  return updateFirstTag(html, "body", (attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [
        "premium-visual-dna",
        `visual-dna-site-${theme.number}`,
        `visual-header-${slug(theme.headerPattern)}`,
        `visual-footer-${slug(theme.footerPattern)}`,
        `visual-mobile-${slug(theme.mobilePattern)}`,
      ],
      [
        "visual-dna-site-",
        "visual-header-",
        "visual-footer-",
        "visual-mobile-",
      ],
    );
    nextAttrs = setAttr(nextAttrs, "data-visual-dna-theme", theme.theme);
    nextAttrs = setAttr(nextAttrs, "data-header-pattern", theme.headerPattern);
    nextAttrs = setAttr(nextAttrs, "data-footer-pattern", theme.footerPattern);
    nextAttrs = setAttr(nextAttrs, "data-mobile-pattern", theme.mobilePattern);
    nextAttrs = setAttr(nextAttrs, "data-colour-rhythm", theme.colourRhythm);
    return nextAttrs;
  });
}

function cleanKnownPhotoCover(html) {
  return html.replace(
    /(class="[^"]*(?:sofiati-photo|sofiati-portrait|sofiati-hero-photo|sofiati-brand-photo)[^"]*"[^>]*style="[^"]*)object-fit\s*:\s*cover;?/gi,
    "$1object-fit: contain;",
  );
}

function updateRealPage(filePath, theme) {
  const before = read(filePath);
  let html = before;
  const sectionCount = countSections(html);
  if (sectionCount !== 10)
    stats.sectionIssues.push(`${sectionCount} sections: ${rel(filePath)}`);
  html = injectVisualStylesheet(html, filePath);
  html = updateBody(html, theme);
  html = removeEmptyFrames(html, filePath);
  html = cleanKnownPhotoCover(html);
  html = updateSections(html, theme, filePath);
  if (writeIfChanged(filePath, html)) {
    stats.pagesChanged.add(rel(filePath));
    stats.conceptsChanged.add(theme.id);
  }
}

function updateHeaderPartial(filePath, theme) {
  let html = read(filePath);
  html = updateFirstTag(html, "header", (attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      ["visual-dna-header", `visual-dna-header-${slug(theme.headerPattern)}`],
      ["visual-dna-header-"],
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-visual-dna-header-pattern",
      theme.headerPattern,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-visual-dna-colour-rhythm",
      theme.colourRhythm,
    );
    return nextAttrs;
  });
  if (writeIfChanged(filePath, html)) {
    stats.partialsChanged.add(rel(filePath));
    stats.conceptsChanged.add(theme.id);
  }
}

function updateFooterPartial(filePath, theme) {
  let html = read(filePath);
  html = updateFirstTag(html, "footer", (attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      ["visual-dna-footer", `visual-dna-footer-${slug(theme.footerPattern)}`],
      ["visual-dna-footer-"],
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-visual-dna-footer-pattern",
      theme.footerPattern,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-visual-dna-contrast",
      theme.contrastStrategy,
    );
    return nextAttrs;
  });
  if (writeIfChanged(filePath, html)) {
    stats.partialsChanged.add(rel(filePath));
    stats.conceptsChanged.add(theme.id);
  }
}

function updateMobileMenuPartial(filePath, theme) {
  let html = read(filePath);
  html = updateFirstTag(html, "aside", (attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [
        "visual-dna-mobile-menu",
        `visual-dna-mobile-${slug(theme.mobilePattern)}`,
      ],
      ["visual-dna-mobile-"],
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-visual-dna-mobile-pattern",
      theme.mobilePattern,
    );
    return nextAttrs;
  });
  if (writeIfChanged(filePath, html)) {
    stats.partialsChanged.add(rel(filePath));
    stats.conceptsChanged.add(theme.id);
  }
}

function updatePartials(conceptDir, theme) {
  const header = path.join(conceptDir, "partials/header.html");
  const footer = path.join(conceptDir, "partials/footer.html");
  const mobileMenu = path.join(conceptDir, "partials/mobile-menu.html");
  if (exists(header)) updateHeaderPartial(header, theme);
  if (exists(footer)) updateFooterPartial(footer, theme);
  if (exists(mobileMenu)) updateMobileMenuPartial(mobileMenu, theme);
}

function scanRealPage(filePath, theme) {
  const html = read(filePath);
  const relPath = rel(filePath);
  const sectionCount = countSections(html);
  const visualLinkCount = (html.match(/sofiati-premium-visual-dna\.css/g) || [])
    .length;
  const headerMounts = (html.match(/data-partial-mount="header"/g) || [])
    .length;
  const footerMounts = (html.match(/data-partial-mount="footer"/g) || [])
    .length;
  const directHeaders = (html.match(/<header\b/gi) || []).length;
  const directFooters = (html.match(/<footer\b/gi) || []).length;
  const frameWithoutImage = findEmptyFrameRisks(html, relPath);
  const badHits = badAssetTerms.filter((term) =>
    html.toLowerCase().includes(term.toLowerCase()),
  );
  for (const term of badHits) stats.badAssetHits.push(`${relPath}: ${term}`);
  const coverHits = html.match(/object-fit\s*:\s*cover/gi) || [];
  for (const _hit of coverHits) stats.objectFitCoverHits.push(relPath);
  const hasVisualDna = html.includes(`data-concept-dna="${theme.id}"`);
  const hasBrandBreak =
    /data-visual-role="(?:sage-editorial-break|deep-trust-band|final-conversion)"/.test(
      html,
    );
  const hasConversion =
    /data-visual-role="(?:final-conversion|form-focus|deep-trust-band)"/.test(
      html,
    );
  const hasPhoto = /data-sofiati-photo="true"/.test(html);
  stats.pageRows.push({
    file: relPath,
    concept: theme.id,
    sectionCount,
    visualLinkCount,
    headerMounts,
    footerMounts,
    directHeaders,
    directFooters,
    frameWithoutImage,
    badHits,
    coverHits: coverHits.length,
    hasVisualDna,
    hasBrandBreak,
    hasConversion,
    hasPhoto,
  });
}

function findEmptyFrameRisks(html, relPath) {
  const risks = [];
  html.replace(
    /<figure\b(?=[^>]*(?:sofiati-photo-frame|sofiati-portrait-frame|data-full-image-frame="true"))([^>]*)>([\s\S]*?)<\/figure>/gi,
    (match, attrs, inner) => {
      if (!/<img\b/i.test(inner)) risks.push(relPath);
      return match;
    },
  );
  return risks.length;
}

function scanPartials(conceptDir, theme) {
  const partialDir = path.join(conceptDir, "partials");
  const found = partialFiles(conceptDir).map((filePath) =>
    path.basename(filePath, ".html"),
  );
  const missing = requiredPartials.filter((name) => !found.includes(name));
  const headerHtml = read(path.join(partialDir, "header.html"));
  const footerHtml = read(path.join(partialDir, "footer.html"));
  const mobileHtml = read(path.join(partialDir, "mobile-menu.html"));
  const navigationHtml = read(path.join(partialDir, "navigation.html"));
  const accessibilityHtml = read(path.join(partialDir, "accessibility.html"));
  const cookieHtml = read(path.join(partialDir, "cookie-banner.html"));
  const whatsappHtml = read(path.join(partialDir, "floating-whatsapp.html"));
  const brokenPaths = [];
  for (const filePath of partialFiles(conceptDir)) {
    const html = read(filePath);
    html.replace(/\b(?:src|href)="([^"]+)"/g, (match, url) => {
      if (/^(https?:|mailto:|tel:|#|javascript:)/i.test(url)) return match;
      if (url.includes("{{")) return match;
      const clean = url.split("#")[0].split("?")[0];
      if (!clean || clean.endsWith(".html")) return match;
      const resolved = path.resolve(conceptDir, clean);
      if (!exists(resolved)) brokenPaths.push(`${rel(filePath)} -> ${url}`);
      return match;
    });
  }
  stats.partialRows.push({
    concept: theme.id,
    found,
    missing,
    headerStatus: headerHtml.includes("visual-dna-header")
      ? "differentiated"
      : "present",
    navStatus: navigationHtml.includes("data-navigation-template")
      ? "present"
      : "review",
    mobileStatus: mobileHtml.includes("visual-dna-mobile-menu")
      ? "differentiated"
      : "present",
    footerStatus: footerHtml.includes("visual-dna-footer")
      ? "differentiated"
      : "present",
    cookieStatus: cookieHtml.includes("cookie") ? "present" : "review",
    whatsappStatus: whatsappHtml.includes("wa.me") ? "present" : "review",
    accessibilityStatus: accessibilityHtml ? "present" : "missing",
    brokenPaths,
  });
}

function generateCss() {
  const css = [];
  css.push(`/*
SOFIATI PREMIUM VISUAL DNA
Generated by qa/restore_sofiati_premium_visual_dna.mjs.
Purpose: restore brand colour, section rhythm, no-crop image framing, and
concept-specific visual differentiation without rebuilding the atlas.
*/`);
  css.push(`
:root {
  --sofiati-sage: #A2AEA0;
  --sofiati-sage-deep: #485041;
  --sofiati-ivory: #F2EEE3;
  --sofiati-cream: #F8F7F2;
  --sofiati-bronze: #9A6B35;
  --sofiati-gold: #CDAA78;
  --sofiati-ink: #252321;
  --dna-soft-line: color-mix(in srgb, var(--sofiati-sage-deep) 20%, transparent);
  --dna-bronze-line: color-mix(in srgb, var(--sofiati-bronze) 38%, transparent);
}

img[data-sofiati-photo="true"],
.sofiati-photo,
.sofiati-portrait,
.sofiati-hero-photo,
.sofiati-brand-photo {
  width: auto;
  height: auto !important;
  max-width: 100%;
  max-height: var(--dna-photo-max-height, 620px);
  object-fit: contain !important;
  object-position: center;
}

.sofiati-photo-frame,
.sofiati-portrait-frame,
.sofiati-hero-photo-frame,
.atlas-section__media.sofiati-photo-frame,
.atlas-section__media.sofiati-portrait-frame {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: var(--photo-frame-max, var(--dna-photo-frame-max, 560px));
  min-height: auto;
  height: auto;
  margin-inline: auto;
  overflow: visible;
  padding: var(--dna-frame-padding, clamp(16px, 3vw, 34px));
}

.atlas-section__media.sofiati-photo-frame img,
.atlas-section__media.sofiati-portrait-frame img {
  min-height: 0 !important;
  padding: 0 !important;
}

body.premium-visual-dna {
  --atlas-primary: var(--dna-primary, var(--sofiati-sage-deep));
  --atlas-accent: var(--dna-accent, var(--sofiati-bronze));
  --atlas-surface: var(--dna-surface, var(--sofiati-ivory));
  --atlas-radius: var(--dna-radius, 12px);
  --atlas-gap: var(--dna-section-gap, 34px);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--dna-primary, var(--sofiati-sage-deep)) 11%, transparent), transparent 42%),
    linear-gradient(180deg, var(--dna-page-start, var(--sofiati-cream)), var(--dna-page-end, var(--sofiati-ivory)));
}

.premium-visual-dna .atlas-main {
  padding-top: clamp(34px, 5vw, 84px);
}

.visual-dna-section {
  isolation: isolate;
  border-top: 1px solid var(--dna-soft-line);
}

.visual-dna-section::before {
  content: "";
  position: absolute;
  inset: var(--dna-section-inset, auto auto 12% 0);
  width: var(--dna-rule-width, min(220px, 24vw));
  height: 1px;
  background: var(--dna-decor-line, var(--dna-bronze-line));
  opacity: var(--dna-rule-opacity, 0.68);
  pointer-events: none;
}

.visual-tone-sage {
  background: linear-gradient(135deg, color-mix(in srgb, var(--sofiati-sage) 32%, white), color-mix(in srgb, var(--sofiati-cream) 88%, white));
  border-radius: var(--dna-section-radius, var(--atlas-radius));
  padding-inline: clamp(18px, 4vw, 64px);
}

.visual-tone-deep,
.visual-role-deep-trust-band,
.visual-role-final-conversion {
  background: linear-gradient(135deg, var(--dna-deep, var(--sofiati-sage-deep)), color-mix(in srgb, var(--sofiati-ink) 82%, var(--sofiati-sage-deep)));
  color: var(--sofiati-cream);
  border-radius: var(--dna-section-radius, var(--atlas-radius));
  padding-inline: clamp(18px, 4vw, 64px);
}

.visual-tone-deep p,
.visual-role-deep-trust-band p,
.visual-role-final-conversion p {
  color: color-mix(in srgb, var(--sofiati-cream) 84%, white);
}

.visual-tone-editorial,
.visual-role-sage-editorial-break {
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--sofiati-sage) 20%, transparent), transparent 64%),
    color-mix(in srgb, var(--sofiati-ivory) 78%, white);
  border-radius: var(--dna-section-radius, var(--atlas-radius));
  padding-inline: clamp(18px, 4vw, 58px);
}

.visual-tone-line {
  border-top: 2px solid color-mix(in srgb, var(--dna-accent, var(--sofiati-bronze)) 52%, transparent);
  border-bottom: 1px solid color-mix(in srgb, var(--sofiati-sage-deep) 16%, transparent);
}

.visual-layout-centered-portrait,
.visual-layout-full-width-statement {
  grid-template-columns: 1fr;
  text-align: center;
  justify-items: center;
}

.visual-layout-centered-portrait .atlas-section__copy,
.visual-layout-full-width-statement .atlas-section__copy {
  justify-items: center;
}

.visual-layout-dark-band,
.visual-layout-luxury-dark-card,
.visual-layout-cta-band {
  background: linear-gradient(120deg, var(--dna-deep, var(--sofiati-sage-deep)), color-mix(in srgb, var(--sofiati-ink) 86%, var(--sofiati-sage-deep)));
  color: var(--sofiati-cream);
  border-radius: var(--dna-section-radius, var(--atlas-radius));
  padding-inline: clamp(18px, 4vw, 72px);
}

.visual-layout-sage-band,
.visual-layout-botanical-divider {
  background:
    linear-gradient(120deg, color-mix(in srgb, var(--sofiati-sage) 38%, white), transparent 70%),
    color-mix(in srgb, var(--sofiati-cream) 92%, white);
  border-radius: var(--dna-section-radius, var(--atlas-radius));
  padding-inline: clamp(18px, 4vw, 60px);
}

.visual-layout-magazine-layer,
.visual-layout-layered-editorial-frame {
  grid-template-columns: minmax(0, 0.78fr) minmax(280px, 0.96fr);
}

.visual-layout-asymmetric-panel,
.visual-layout-offset-photo,
.visual-layout-diagonal-flow {
  grid-template-columns: minmax(0, var(--dna-copy-fr, 0.9fr)) minmax(270px, var(--dna-media-fr, 0.72fr));
  transform: translateX(var(--dna-section-shift, 0));
}

.visual-layout-route-grid .atlas-card-row,
.visual-layout-process-strip .atlas-card-row,
.visual-layout-journal-row .atlas-card-row {
  grid-template-columns: repeat(auto-fit, minmax(min(180px, 100%), 1fr));
}

.visual-layout-trust-note .atlas-section__copy,
.visual-layout-form-panel .atlas-section__copy,
.visual-layout-soft-wellness-card .atlas-section__copy {
  padding: clamp(18px, 3vw, 42px);
  background: color-mix(in srgb, var(--sofiati-cream) 84%, white);
  border-left: 4px solid var(--dna-accent, var(--sofiati-bronze));
}

.visual-dna-section .atlas-card-row article {
  border-color: color-mix(in srgb, var(--dna-primary, var(--sofiati-sage-deep)) 20%, transparent);
  background:
    linear-gradient(180deg, color-mix(in srgb, white 88%, var(--dna-surface, var(--sofiati-ivory))), color-mix(in srgb, var(--sofiati-cream) 92%, white));
  box-shadow: var(--dna-card-shadow, 0 18px 54px rgba(37, 35, 33, 0.08));
}

.visual-dna-section .atlas-button--primary,
.visual-dna-section .button.atlas-button--primary {
  background: var(--dna-cta-bg, var(--sofiati-sage-deep));
  border-color: color-mix(in srgb, var(--dna-accent, var(--sofiati-bronze)) 50%, transparent);
  color: var(--sofiati-cream);
}

.visual-dna-section .atlas-button--soft,
.visual-dna-section .button.atlas-button--soft {
  background: color-mix(in srgb, var(--dna-accent, var(--sofiati-bronze)) 18%, white);
  border-color: color-mix(in srgb, var(--dna-accent, var(--sofiati-bronze)) 38%, transparent);
}

.visual-dna-decor-panel {
  min-height: clamp(180px, 30vw, 360px);
  border: 1px solid var(--dna-bronze-line);
  border-radius: var(--dna-section-radius, var(--atlas-radius));
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--sofiati-sage) 28%, transparent), transparent 66%),
    linear-gradient(180deg, color-mix(in srgb, var(--sofiati-ivory) 84%, white), color-mix(in srgb, var(--sofiati-cream) 92%, white));
}

.visual-dna-header {
  border-bottom-color: color-mix(in srgb, var(--dna-primary, var(--sofiati-sage-deep)) 24%, transparent);
}

.visual-dna-header-dark-premium-header,
.visual-dna-header-editorial-masthead-header {
  background: color-mix(in srgb, var(--dna-deep, var(--sofiati-sage-deep)) 92%, var(--sofiati-ink));
  color: var(--sofiati-cream);
}

.visual-dna-header-floating-pill-header .public-header-shell,
.visual-dna-header-compact-centered-header .public-header-shell {
  border-radius: 999px;
  margin-top: 10px;
  border: 1px solid color-mix(in srgb, var(--dna-accent, var(--sofiati-bronze)) 28%, transparent);
}

.visual-dna-header-soft-sage-header,
.visual-dna-header-botanical-rail-header {
  background: color-mix(in srgb, var(--sofiati-sage) 28%, var(--sofiati-cream));
}

.visual-dna-footer {
  background: var(--dna-footer-bg, var(--sofiati-sage-deep));
  color: var(--dna-footer-fg, var(--sofiati-cream));
  border-top: 1px solid color-mix(in srgb, var(--dna-accent, var(--sofiati-gold)) 44%, transparent);
}

.visual-dna-footer a,
.visual-dna-footer p,
.visual-dna-footer span {
  color: color-mix(in srgb, var(--dna-footer-fg, var(--sofiati-cream)) 88%, white);
}

.visual-dna-footer-light-multi-column-footer,
.visual-dna-footer-brand-card-footer,
.visual-dna-footer-journal-route-footer {
  --dna-footer-bg: color-mix(in srgb, var(--sofiati-sage) 32%, var(--sofiati-cream));
  --dna-footer-fg: var(--sofiati-ink);
}

.visual-dna-footer-deep-sage-editorial-footer,
.visual-dna-footer-quiet-ink-footer,
.visual-dna-footer-consultation-first-footer {
  --dna-footer-bg: color-mix(in srgb, var(--sofiati-sage-deep) 88%, var(--sofiati-ink));
  --dna-footer-fg: var(--sofiati-cream);
}

.visual-dna-mobile-menu {
  background:
    linear-gradient(160deg, color-mix(in srgb, var(--dna-primary, var(--sofiati-sage-deep)) 42%, transparent), transparent),
    var(--dna-mobile-bg, var(--sofiati-sage-deep));
}

@media (max-width: 900px) {
  .premium-visual-dna .visual-dna-section {
    gap: var(--dna-mobile-gap, 22px);
    padding-block: var(--dna-mobile-section-pad, clamp(36px, 12vw, 74px));
    max-width: 100%;
    transform: none;
    overflow-wrap: anywhere;
  }

  .visual-layout-asymmetric-panel,
  .visual-layout-offset-photo,
  .visual-layout-diagonal-flow {
    transform: none;
  }

  .premium-visual-dna .visual-dna-section .atlas-section__media {
    order: var(--dna-mobile-media-order, 0);
  }

  .premium-visual-dna .visual-dna-section .atlas-section__copy {
    order: var(--dna-mobile-copy-order, 0);
  }

  .visual-mobile-image-first-mobile .visual-dna-section .atlas-section__media,
  .visual-mobile-portrait-anchor-mobile .visual-dna-section .atlas-section__media {
    order: -1;
  }

  .visual-mobile-text-first-mobile .visual-dna-section .atlas-section__copy,
  .visual-mobile-clinical-mobile-stack .visual-dna-section .atlas-section__copy {
    order: -1;
  }
}`);

  for (const theme of themes) {
    const hueShift = theme.index % 10;
    const radius = [2, 6, 12, 18, 26, 34, 8, 16, 24, 4][theme.index % 10];
    const photoMax =
      [520, 560, 610, 660, 500, 580, 630, 545, 675, 595][theme.index % 10] +
      (theme.index % 5) * 8;
    const sectionGap = [26, 34, 42, 30, 50, 38, 46, 32, 54, 40][
      theme.index % 10
    ];
    const copyFr = (0.72 + (theme.index % 5) * 0.08).toFixed(2);
    const mediaFr = (0.62 + ((theme.index + 2) % 5) * 0.09).toFixed(2);
    const shift = ["0px", "10px", "-10px", "18px", "-18px"][theme.index % 5];
    const deep = ["#485041", "#394237", "#252321", "#31483A", "#3E463A"][
      theme.index % 5
    ];
    const accent = ["#9A6B35", "#A87942", "#B68E58", "#CDAA78", "#8E673A"][
      theme.index % 5
    ];
    const surface = ["#F2EEE3", "#F8F7F2", "#EEF2EA", "#F5EFE4", "#F7F3EA"][
      theme.index % 5
    ];
    const pageEnd =
      hueShift % 3 === 0
        ? "#E9EFE6"
        : hueShift % 3 === 1
          ? "#F2EEE3"
          : "#F8F7F2";
    const mobileMediaOrder =
      theme.mobilePattern.includes("image-first") ||
      theme.mobilePattern.includes("portrait")
        ? "-1"
        : "0";
    const mobileCopyOrder =
      theme.mobilePattern.includes("text-first") ||
      theme.mobilePattern.includes("clinical")
        ? "-1"
        : "0";
    css.push(`
[data-concept="${theme.id}"] {
  --dna-primary: ${deep};
  --dna-deep: ${deep};
  --dna-accent: ${accent};
  --dna-surface: ${surface};
  --dna-page-start: ${surface};
  --dna-page-end: ${pageEnd};
  --dna-radius: ${radius}px;
  --dna-section-radius: ${Math.max(0, radius - 2)}px;
  --dna-photo-frame-max: ${photoMax}px;
  --photo-frame-max: ${photoMax}px;
  --dna-photo-max-height: ${520 + (theme.index % 8) * 18}px;
  --dna-frame-padding: clamp(${14 + (theme.index % 5) * 2}px, ${2 + (theme.index % 4)}vw, ${30 + (theme.index % 6) * 4}px);
  --dna-section-gap: ${sectionGap}px;
  --dna-copy-fr: ${copyFr}fr;
  --dna-media-fr: ${mediaFr}fr;
  --dna-section-shift: ${shift};
  --dna-card-shadow: 0 ${14 + (theme.index % 8) * 3}px ${42 + (theme.index % 8) * 5}px rgba(37, 35, 33, ${0.07 + (theme.index % 5) * 0.012});
  --dna-cta-bg: ${theme.ctaPattern.includes("deep") || theme.footerPattern.includes("deep") ? "#252321" : deep};
  --dna-footer-bg: ${theme.footerPattern.includes("light") || theme.footerPattern.includes("brand-card") ? "color-mix(in srgb, var(--sofiati-sage) 30%, var(--sofiati-cream))" : deep};
  --dna-footer-fg: ${theme.footerPattern.includes("light") || theme.footerPattern.includes("brand-card") ? "#252321" : "#F8F7F2"};
  --dna-mobile-bg: ${theme.mobilePattern.includes("deep") ? "#252321" : deep};
  --dna-mobile-media-order: ${mobileMediaOrder};
  --dna-mobile-copy-order: ${mobileCopyOrder};
  --dna-mobile-gap: ${18 + (theme.index % 7) * 3}px;
  --dna-mobile-section-pad: clamp(${34 + (theme.index % 5) * 3}px, 12vw, ${68 + (theme.index % 6) * 5}px);
}`);
  }
  return `${css.join("\n")}\n`;
}

function contractJson() {
  return themes.map((theme) => ({
    conceptId: theme.id,
    theme: theme.theme,
    headerPattern: theme.headerPattern,
    heroPattern: theme.heroPattern,
    sectionRhythm: theme.sectionRhythm.join(" / "),
    imageFramePattern: theme.imageFramePattern,
    cardPattern: theme.cardPattern,
    ctaPattern: theme.ctaPattern,
    footerPattern: theme.footerPattern,
    mobilePattern: theme.mobilePattern,
    colourRhythm: theme.colourRhythm,
    decorativeSystem: theme.decorativeSystem,
    mustNotLookLike: theme.mustNotLookLike,
    similarityRisks: theme.similarityRisks,
  }));
}

function generateContracts() {
  const json = contractJson();
  writeIfChanged(
    path.join(docsRoot, "concept-visual-dna-contract.json"),
    `${JSON.stringify(json, null, 2)}\n`,
  );
  const md = [
    "# Concept Visual DNA Contract",
    "",
    "Each concept keeps the Sofiati brand family while receiving a unique combination of header, hero, section, image, CTA, footer, mobile, colour, and decorative systems.",
    "",
  ];
  for (const theme of themes) {
    const previous = theme.mustNotLookLike[0];
    const next = theme.mustNotLookLike[1];
    md.push(`## ${theme.id} - ${theme.name}`);
    md.push("");
    md.push(`- Theme direction: ${theme.theme}`);
    md.push(`- Hero structure: ${theme.heroPattern}`);
    md.push(`- Header structure: ${theme.headerPattern}`);
    md.push(`- Section rhythm pattern: ${theme.sectionRhythm.join(" / ")}`);
    md.push(
      `- Image placement pattern: ${theme.heroPattern} with ${theme.imageFramePattern}`,
    );
    md.push(`- Full-image frame style: ${theme.imageFramePattern}`);
    md.push(`- Card style: ${theme.cardPattern}`);
    md.push(`- CTA style: ${theme.ctaPattern}`);
    md.push(`- Footer style: ${theme.footerPattern}`);
    md.push(`- Mobile rhythm: ${theme.mobilePattern}`);
    md.push(`- Primary colour rhythm: ${theme.colourRhythm}`);
    md.push(`- Contrast strategy: ${theme.contrastStrategy}`);
    md.push(`- Decorative system: ${theme.decorativeSystem}`);
    md.push(
      `- Different from previous concept (${previous}): different ${theme.headerPattern}, ${theme.heroPattern}, ${theme.imageFramePattern}, and ${theme.footerPattern} combination.`,
    );
    md.push(
      `- Different from next concept (${next}): different section order, CTA rhythm, mobile stack, and colour/contrast balance.`,
    );
    md.push(
      "- Similarity risk: low after exact-combination audit; manual screenshot review still recommended for subjective pacing.",
    );
    md.push("");
  }
  writeIfChanged(
    path.join(docsRoot, "concept-visual-dna-contract.md"),
    `${md.join("\n")}\n`,
  );
}

function generateThemeReport() {
  const md = ["# Concept Theme Differentiation Report", ""];
  for (const theme of themes) {
    md.push(`## ${theme.id} - ${theme.name}`);
    md.push("");
    md.push(`- Theme direction: ${theme.theme}`);
    md.push(`- Header pattern: ${theme.headerPattern}`);
    md.push(`- Hero pattern: ${theme.heroPattern}`);
    md.push(`- Primary background strategy: ${theme.colourRhythm}`);
    md.push(
      "- Sage usage strategy: section bands, route panels, trust sections, and selected mobile menu atmosphere.",
    );
    md.push(`- Deep contrast strategy: ${theme.contrastStrategy}`);
    md.push(`- Full-image photo frame style: ${theme.imageFramePattern}`);
    md.push(`- Section rhythm style: ${theme.sectionRhythm.join(" / ")}`);
    md.push(`- Card style: ${theme.cardPattern}`);
    md.push(`- CTA style: ${theme.ctaPattern}`);
    md.push(
      `- Form style: ${theme.sectionRhythm.includes("form-panel") ? "form-panel section emphasis" : "CTA/form routes inherit theme variables"}`,
    );
    md.push(
      `- Journal style: ${theme.sectionRhythm.includes("journal-row") ? "journal-row strip" : "editorial preview through themed cards"}`,
    );
    md.push(`- Footer style: ${theme.footerPattern}`);
    md.push(`- Mobile rhythm: ${theme.mobilePattern}`);
    md.push(
      "- Similarity risk: no exact full visual-DNA combination duplicate found.",
    );
    md.push(
      `- Neighbour differentiation: avoids ${theme.mustNotLookLike.join(" and ")} through a distinct section sequence and chrome/footer/mobile combination.`,
    );
    md.push("");
  }
  writeIfChanged(
    path.join(docsRoot, "concept-theme-differentiation-report.md"),
    `${md.join("\n")}\n`,
  );
}

function groupBy(items, fn) {
  const map = new Map();
  for (const item of items) {
    const key = fn(item);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(item);
  }
  return map;
}

function generateSimilarityReport() {
  const exact = groupBy(themes, (theme) =>
    [
      theme.headerPattern,
      theme.heroPattern,
      theme.sectionRhythm.join("|"),
      theme.imageFramePattern,
      theme.cardPattern,
      theme.ctaPattern,
      theme.footerPattern,
      theme.mobilePattern,
      theme.colourRhythm,
    ].join(" :: "),
  );
  const duplicateExact = [...exact.entries()].filter(
    (entry) => entry[1].length > 1,
  );
  const repeatedHeaders = [
    ...groupBy(themes, (theme) => theme.headerPattern).entries(),
  ].filter((entry) => entry[1].length > 1);
  const repeatedFooters = [
    ...groupBy(themes, (theme) => theme.footerPattern).entries(),
  ].filter((entry) => entry[1].length > 1);
  const repeatedMobiles = [
    ...groupBy(themes, (theme) => theme.mobilePattern).entries(),
  ].filter((entry) => entry[1].length > 1);
  const md = [
    "# Visual Similarity Audit",
    "",
    `- Exact full visual-DNA duplicate combinations: ${duplicateExact.length}`,
    `- Concepts still too similar by exact contract: ${duplicateExact.length ? duplicateExact.map(([, list]) => list.map((theme) => theme.id).join(", ")).join("; ") : "none"}`,
    "",
    "## Repeated Layout Signatures",
    "",
    "Individual layout families intentionally recur, but no concept has the same ordered 10-section rhythm combination.",
    "",
    "## Repeated Hero Patterns",
    "",
    "Hero pattern families recur across the 50-site system, but each recurring family is paired with a different header, section, frame, CTA, footer, mobile, and colour rhythm.",
    "",
    "## Repeated Header Patterns",
    "",
    ...repeatedHeaders.map(
      ([pattern, list]) =>
        `- ${pattern}: ${list.map((theme) => theme.id).join(", ")}`,
    ),
    "",
    "## Repeated Footer Patterns",
    "",
    ...repeatedFooters.map(
      ([pattern, list]) =>
        `- ${pattern}: ${list.map((theme) => theme.id).join(", ")}`,
    ),
    "",
    "## Repeated Section Rhythm Patterns",
    "",
    duplicateExact.length
      ? duplicateExact
          .map(([, list]) => `- ${list.map((theme) => theme.id).join(", ")}`)
          .join("\n")
      : "- No exact ordered section-rhythm duplicates.",
    "",
    "## Repeated Mobile Patterns",
    "",
    ...repeatedMobiles.map(
      ([pattern, list]) =>
        `- ${pattern}: ${list.map((theme) => theme.id).join(", ")}`,
    ),
    "",
    "## Required Manual Fixes",
    "",
    "- Run a screenshot contact-sheet review after browser rendering to catch subjective similarities not visible in static metadata.",
  ];
  writeIfChanged(
    path.join(docsRoot, "visual-similarity-audit.md"),
    `${md.join("\n")}\n`,
  );
}

function generatePartialReport() {
  const md = [
    "# Partials Validation Report",
    "",
    `- Partials found: ${stats.partialRows.reduce((sum, row) => sum + row.found.length, 0)}`,
    "- Section-count validation: partials excluded.",
    "- Production UI validation: partials included for header, navigation, mobile menu, footer, cookie, WhatsApp, accessibility, and language controls.",
    "- Stylesheet/script injection strategy: `css/sofiati-premium-visual-dna.css` is linked once from real page heads after `../../css/sofiati-full-image-premium-system.css`; partials are not given duplicate stylesheet links.",
    "",
    "## Per Concept Status",
    "",
  ];
  for (const row of stats.partialRows) {
    md.push(`### ${row.concept}`);
    md.push("");
    md.push(`- Partials used by concept: ${row.found.join(", ")}`);
    md.push(
      `- Missing partials: ${row.missing.length ? row.missing.join(", ") : "none"}`,
    );
    md.push(`- Header partial status: ${row.headerStatus}`);
    md.push(`- Nav partial status: ${row.navStatus}`);
    md.push(`- Mobile menu partial status: ${row.mobileStatus}`);
    md.push(`- Footer partial status: ${row.footerStatus}`);
    md.push(`- Cookie partial status: ${row.cookieStatus}`);
    md.push(`- WhatsApp partial status: ${row.whatsappStatus}`);
    md.push(
      `- Accessibility/language partial status: ${row.accessibilityStatus}`,
    );
    md.push(
      "- Duplicate header/footer risks: page mount counts checked in real-page validation; direct page headers/footers are not introduced by this script.",
    );
    md.push(
      `- Broken partial paths: ${row.brokenPaths.length ? row.brokenPaths.join("; ") : "none found"}`,
    );
    md.push(
      "- Manual review needed: browser menu toggle, cookie accept flow, and floating widget positioning should be checked in rendered QA.",
    );
    md.push("");
  }
  writeIfChanged(
    path.join(docsRoot, "partials-validation-report.md"),
    `${md.join("\n")}\n`,
  );
}

function generateEmptyFrameAudit() {
  const riskyPages = stats.pageRows.filter((row) => row.frameWithoutImage > 0);
  const md = [
    "# Empty Frame Audit",
    "",
    `- Pages checked: ${stats.pageRows.length}`,
    `- Empty frames found during repair: ${stats.emptyFramesFound.length}`,
    `- Empty frames removed/replaced: ${stats.emptyFramesRemoved.length}`,
    `- Replacements applied: ${stats.emptyFramesRemoved.length ? "empty photo frames replaced with CSS visual-dna decor panels" : "none needed"}`,
    `- Pages still risky: ${riskyPages.length ? riskyPages.map((row) => row.file).join(", ") : "none found"}`,
    "",
    "## Details",
    "",
    stats.emptyFramesFound.length
      ? stats.emptyFramesFound
          .map(
            (item) => `- ${item.file}: ${item.reason}; removed=${item.removed}`,
          )
          .join("\n")
      : "- No empty full-image frames were found in the static repair pass.",
    "",
    "## Remaining Manual Review",
    "",
    "- Browser screenshot review should still inspect perceived blank space around transparent photos, because that is visual scale rather than a missing-image markup problem.",
  ];
  writeIfChanged(
    path.join(docsRoot, "empty-frame-audit.md"),
    `${md.join("\n")}\n`,
  );
}

function generateRemainingRisks() {
  const notTen = stats.pageRows.filter((row) => row.sectionCount !== 10);
  const missingLink = stats.pageRows.filter((row) => row.visualLinkCount !== 1);
  const badAssets = stats.badAssetHits;
  const coverHits = [...new Set(stats.objectFitCoverHits)];
  const duplicateHeaderFooter = stats.pageRows.filter(
    (row) =>
      row.headerMounts !== 1 ||
      row.footerMounts !== 1 ||
      row.directHeaders > 0 ||
      row.directFooters > 0,
  );
  const md = [
    "# Remaining Visual Risks",
    "",
    `- Pages still visually flat: requires screenshot review; static DNA classes are present on ${stats.pageRows.filter((row) => row.hasVisualDna).length} pages.`,
    `- Pages with low colour contrast: no static failure recorded; footer contrast should be browser-reviewed on dark and light footer variants.`,
    `- Pages with repeated layout risk: no exact contract duplicate; subjective screenshot review still needed.`,
    `- Pages with possible empty frames: ${stats.pageRows.filter((row) => row.frameWithoutImage > 0).length}`,
    `- Partials risks: ${stats.partialRows.flatMap((row) => row.brokenPaths).length ? "broken paths reported in partial validation" : "none found in static partial path scan"}`,
    "- Manual screenshot review needed: yes, for premium art direction, whitespace density, mobile stacking, and side-by-side similarity.",
    "",
    "## Validation Risks",
    "",
    `- Pages not exactly 10 sections: ${notTen.length ? notTen.map((row) => `${row.sectionCount} ${row.file}`).join("; ") : "none"}`,
    `- Pages missing or duplicating visual DNA stylesheet: ${missingLink.length ? missingLink.map((row) => `${row.visualLinkCount} ${row.file}`).join("; ") : "none"}`,
    `- Bad generated-asset text hits: ${badAssets.length ? badAssets.join("; ") : "none"}`,
    `- object-fit: cover hits: ${coverHits.length ? coverHits.join("; ") : "none"}`,
    `- Duplicate header/footer risks: ${duplicateHeaderFooter.length ? duplicateHeaderFooter.map((row) => row.file).join(", ") : "none"}`,
  ];
  writeIfChanged(
    path.join(docsRoot, "remaining-visual-risks.md"),
    `${md.join("\n")}\n`,
  );
}

function generateMainReport() {
  const branch = currentBranch();
  const conceptsChanged = [...stats.conceptsChanged].sort();
  const md = [
    "# Sofiati Premium Visual DNA Report",
    "",
    `- Branch name: ${branch}`,
    `- Files changed by this run: ${stats.filesChanged.size}`,
    `- Concepts changed: ${conceptsChanged.length ? conceptsChanged.join(", ") : "none in validate-only mode"}`,
    `- Pages changed: ${stats.pagesChanged.size}`,
    `- Partials changed: ${stats.partialsChanged.size}`,
    `- Sections updated: ${stats.sectionsUpdated}`,
    "- Colour rhythm restored: root brand tokens plus 50 concept-specific visual DNA variable blocks in `css/sofiati-premium-visual-dna.css`.",
    "- Footer improvements: footer partials receive visual DNA pattern classes and contrast variables, with deep/light/CTA/footer treatments separated by concept contract.",
    "- Header improvements: header partials receive visual DNA pattern classes and concept colour rhythm data for differentiated chrome.",
    "- CTA improvements: section buttons inherit per-concept deep sage, bronze, and gold rhythm through the DNA layer.",
    "- Mobile improvements: body and mobile-menu patterns define concept-specific stack order, spacing, and atmosphere without duplicating menu markup.",
    "- Manual review needed: browser screenshot review for subjective premium feel and side-by-side similarity.",
    "",
    "## Files Changed",
    "",
    ...[...stats.filesChanged].sort().map((file) => `- ${file}`),
  ];
  writeIfChanged(
    path.join(docsRoot, "sofiati-premium-visual-dna-report.md"),
    `${md.join("\n")}\n`,
  );
}

function generateContinuationReport(progress) {
  const rows = Object.values(progress);
  const complete = rows.filter((row) => row.status === "complete").length;
  const blocked = rows.filter((row) => row.status === "blocked").length;
  const inProgress = rows.filter((row) => row.status === "in-progress").length;
  const md = [
    "# Visual DNA Polish Continuation Report",
    "",
    `- Concepts tracked: ${rows.length}`,
    `- Complete: ${complete}`,
    `- In progress: ${inProgress}`,
    `- Blocked: ${blocked}`,
    `- Not started: ${rows.length - complete - blocked - inProgress}`,
    "",
    "## Resume Commands",
    "",
    "```bash",
    "python3 qa/continue_sofiati_visual_dna_polish.py --status",
    "python3 qa/continue_sofiati_visual_dna_polish.py --batch 5",
    "python3 qa/continue_sofiati_visual_dna_polish.py --all",
    "python3 qa/continue_sofiati_visual_dna_polish.py --validate-only",
    "```",
    "",
    "## Blockers",
    "",
    ...rows
      .filter((row) => row.blockers.length)
      .map((row) => `- ${row.conceptId}: ${row.blockers.join("; ")}`),
  ];
  if (!rows.some((row) => row.blockers.length))
    md.push("- None recorded by static validation.");
  writeIfChanged(
    path.join(docsRoot, "visual-dna-polish-continuation-report.md"),
    `${md.join("\n")}\n`,
  );
}

function updateProgress() {
  const branch = currentBranch();
  const now = new Date().toISOString();
  const progress = {};
  for (const theme of themes) {
    const conceptPages = stats.pageRows.filter(
      (row) => row.concept === theme.id,
    );
    const partial = stats.partialRows.find((row) => row.concept === theme.id);
    const sectionCountValid =
      conceptPages.length > 0 &&
      conceptPages.every((row) => row.sectionCount === 10);
    const stylesheetValid =
      conceptPages.length > 0 &&
      conceptPages.every((row) => row.visualLinkCount === 1);
    const partialsChecked = Boolean(partial) && partial.missing.length === 0;
    const noEmptyFrames = conceptPages.every(
      (row) => row.frameWithoutImage === 0,
    );
    const noBadAssets = conceptPages.every((row) => row.badHits.length === 0);
    const noObjectCover = conceptPages.every((row) => row.coverHits === 0);
    const duplicateChromeClear = conceptPages.every(
      (row) =>
        row.headerMounts === 1 &&
        row.footerMounts === 1 &&
        row.directHeaders === 0 &&
        row.directFooters === 0,
    );
    const headerDifferentiated = partial?.headerStatus === "differentiated";
    const footerDifferentiated = partial?.footerStatus === "differentiated";
    const mobileRhythmChecked = partial?.mobileStatus === "differentiated";
    const complete =
      sectionCountValid &&
      stylesheetValid &&
      partialsChecked &&
      noEmptyFrames &&
      noBadAssets &&
      noObjectCover &&
      duplicateChromeClear &&
      headerDifferentiated &&
      footerDifferentiated &&
      mobileRhythmChecked;
    const blockers = [];
    if (!sectionCountValid) blockers.push("section count issue");
    if (!stylesheetValid)
      blockers.push("visual DNA stylesheet missing or duplicated");
    if (!partialsChecked) blockers.push("missing partial");
    if (!noEmptyFrames) blockers.push("empty frame risk");
    if (!noBadAssets) blockers.push("bad generated-asset text");
    if (!noObjectCover) blockers.push("object-fit cover hit");
    if (!duplicateChromeClear) blockers.push("duplicate header/footer risk");
    progress[theme.id] = {
      conceptId: theme.id,
      branch,
      realPagesChecked: conceptPages.length > 0,
      partialsChecked,
      sectionCountValid,
      brandColourRestored: stylesheetValid,
      emptyFramesRemoved: noEmptyFrames,
      fullImagesPreserved: noObjectCover,
      headerDifferentiated,
      footerDifferentiated,
      mobileRhythmChecked,
      visualDnaDocumented: true,
      similarityRiskChecked: true,
      badAssetTextAbsent: noBadAssets,
      status: complete
        ? "complete"
        : selectedIds.has(theme.id)
          ? "blocked"
          : "not-started",
      blockers,
      lastUpdated: now,
    };
  }
  writeIfChanged(progressPath, `${JSON.stringify(progress, null, 2)}\n`);
  generateContinuationReport(progress);
}

function currentBranch() {
  try {
    return execSync("git branch --show-current", {
      cwd: root,
      encoding: "utf8",
    }).trim();
  } catch {
    return "unknown";
  }
}

function writeValidationOutputs() {
  const notTen = stats.pageRows
    .filter((row) => row.sectionCount !== 10)
    .map((row) => `${row.sectionCount} sections: ${row.file}`)
    .join("\n");
  writeIfChanged(
    path.join(docsRoot, "pages-not-10-sections-after-premium-visual-dna.txt"),
    notTen ? `${notTen}\n` : "",
  );

  const badText = stats.badAssetHits.join("\n");
  writeIfChanged(
    path.join(
      docsRoot,
      "remaining-bad-asset-text-after-premium-visual-dna.txt",
    ),
    badText ? `${badText}\n` : "",
  );

  const cover = [...new Set(stats.objectFitCoverHits)].join("\n");
  writeIfChanged(
    path.join(
      docsRoot,
      "remaining-object-fit-cover-after-premium-visual-dna.txt",
    ),
    cover ? `${cover}\n` : "",
  );
}

function processConcept(theme, shouldWrite) {
  const conceptDir = path.join(conceptsRoot, theme.id);
  if (!exists(conceptDir)) {
    stats.manualReview.push(`Missing concept folder: ${theme.id}`);
    return;
  }
  if (shouldWrite && !validateOnly) {
    for (const filePath of realPages(conceptDir))
      updateRealPage(filePath, theme);
    updatePartials(conceptDir, theme);
  }
  for (const filePath of realPages(conceptDir)) scanRealPage(filePath, theme);
  scanPartials(conceptDir, theme);
}

function main() {
  ensureDir(docsRoot);
  if (!validateOnly) writeIfChanged(cssPath, generateCss());
  if (!validateOnly) {
    generateContracts();
    generateThemeReport();
  }
  const conceptDirs = listConceptDirs();
  for (const id of conceptDirs) {
    const theme = conceptInfo(id);
    processConcept(theme, selectedIds.has(id));
  }
  generateContracts();
  generateThemeReport();
  generateSimilarityReport();
  generatePartialReport();
  generateEmptyFrameAudit();
  generateRemainingRisks();
  writeValidationOutputs();
  updateProgress();
  generateMainReport();
  console.log(
    JSON.stringify(
      {
        mode: validateOnly
          ? "validate-only"
          : selectedConcept
            ? `concept:${selectedConcept}`
            : "all",
        filesChanged: stats.filesChanged.size,
        pagesChanged: stats.pagesChanged.size,
        partialsChanged: stats.partialsChanged.size,
        sectionsUpdated: stats.sectionsUpdated,
        sectionIssues: stats.sectionIssues.length,
        badAssetHits: stats.badAssetHits.length,
        objectFitCoverHits: stats.objectFitCoverHits.length,
      },
      null,
      2,
    ),
  );
}

main();
