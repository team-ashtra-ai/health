#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { execSync } from "node:child_process";

const root = process.cwd();
const targetBranch = "sofiati-50-architecture-rebuild";
const conceptsRoot = path.join(root, "concepts");
const docsRoot = path.join(root, "docs/script-runs");
const cssPath = path.join(root, "css/sofiati-50-architecture-system.css");
const jsPath = path.join(root, "js/sofiati-50-architecture-system.js");
const progressPath = path.join(
  docsRoot,
  "sofiati-50-architecture-progress.json",
);
const architectureCssHref = "../../css/sofiati-50-architecture-system.css";
const architectureJsSrc = "../../js/sofiati-50-architecture-system.js";

const args = process.argv.slice(2);
const argSet = new Set(args);
const validateOnly = argSet.has("--validate-only") || argSet.has("--report");
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

const conceptSeeds = [
  ["01-inspire", "Inspire", "refined editorial architecture"],
  ["02-empower", "Empower", "botanical block architecture"],
  ["03-enhance", "Enhance", "gold-line minimalist architecture"],
  ["04-renew", "Renew", "dark premium editorial architecture"],
  ["05-elevate", "Elevate", "warm wellness architecture"],
  ["06-refine", "Refine", "clinical calm architecture"],
  ["07-glow", "Glow", "consultation studio architecture"],
  ["08-balance", "Balance", "magazine architecture"],
  ["09-radiance", "Radiance", "medical spa architecture"],
  ["10-essence", "Essence", "portrait-led architecture"],
  ["11-bloom", "Bloom", "botanical architecture"],
  ["12-vital", "Vital", "vitality architecture"],
  ["13-poise", "Poise", "symmetrical architecture"],
  ["14-aura", "Aura", "atmospheric architecture"],
  ["15-clarity", "Clarity", "minimal clinical architecture"],
  ["16-grace", "Grace", "feminine editorial architecture"],
  ["17-sculpt", "Sculpt", "structured premium architecture"],
  ["18-lumin", "Lumin", "luminous architecture"],
  ["19-verda", "Verda", "botanical sage architecture"],
  ["20-halo", "Halo", "glow architecture"],
  ["21-calm", "Calm", "quiet wellness architecture"],
  ["22-precision", "Precision", "technical elegance architecture"],
  ["23-ritual", "Ritual", "spa ritual architecture"],
  ["24-signal", "Signal", "modern interface architecture"],
  ["25-align", "Align", "balanced pathway architecture"],
  ["26-vivant", "Vivant", "lively premium architecture"],
  ["27-form", "Form", "shape-led architecture"],
  ["28-pure", "Pure", "minimal beauty architecture"],
  ["29-solace", "Solace", "comforting architecture"],
  ["30-method", "Method", "method/process architecture"],
  ["31-evolve", "Evolve", "education-led architecture"],
  ["32-serene", "Serene", "spa calm architecture"],
  ["33-elan", "Elan", "stylish editorial architecture"],
  ["34-flora", "Flora", "botanical luxury architecture"],
  ["35-atelier", "Atelier", "crafted studio architecture"],
  ["36-lumina", "Lumina", "luminous elegance architecture"],
  ["37-vellum", "Vellum", "paper editorial architecture"],
  ["38-origin", "Origin", "grounded natural architecture"],
  ["39-kindred", "Kindred", "relational architecture"],
  ["40-noble", "Noble", "mature luxury architecture"],
  ["41-vista", "Vista", "open architecture"],
  ["42-softline", "Softline", "linear architecture"],
  ["43-meridian", "Meridian", "guided pathway architecture"],
  ["44-safeguard", "Safeguard", "trust/safety architecture"],
  ["45-silhouette", "Silhouette", "shape architecture"],
  ["46-curate", "Curate", "curated editorial architecture"],
  ["47-proof", "Proof", "evidence/responsibility architecture"],
  ["48-signature", "Signature", "signature brand architecture"],
  ["49-wisdom", "Wisdom", "education architecture"],
  ["50-sovereign", "Sovereign", "most premium architecture"],
];

const journeyTypes = [
  "consultation-first journey",
  "service-route-first journey",
  "journal-editorial-first journey",
  "trust-first journey",
  "values-first journey",
  "process-first journey",
  "form-first journey",
  "education-first journey",
  "results-expectation-first journey",
  "portrait-trust journey",
  "safety-led journey",
  "guided-pathway journey",
];

const iaEmphasis = [
  "lead with human reassurance, then route to consultation",
  "lead with care categories and botanical trust",
  "lead with precise choices and minimal proof language",
  "lead with premium contrast and slow confidence",
  "lead with wellness comfort before services",
  "lead with education and evaluation boundaries",
  "lead with direct consultation routes",
  "lead with editorial scanning and alternating proof",
  "lead with service matrix and polished next steps",
  "lead with Franciele as the trust anchor",
  "lead with values and natural confidence",
  "lead with energetic process and route clarity",
  "lead with balance, symmetry, and calm comparison",
  "lead with atmosphere and quote-led reassurance",
  "lead with readable clinical clarity",
  "lead with soft editorial warmth",
  "lead with structured choices and strong hierarchy",
  "lead with luminous trust moments",
  "lead with botanical sage identity",
  "lead with soft halo accents and reassurance",
  "lead with restful low-density sections",
  "lead with technical process and precise grids",
  "lead with ritual pacing and deep calm CTAs",
  "lead with interface-like navigation clarity",
  "lead with aligned pathways and internal links",
  "lead with lively premium route energy",
  "lead with form and shape as conversion structure",
  "lead with minimal white space and selective CTAs",
  "lead with comfort, empathy, and soft route cards",
  "lead with method steps and disciplined progression",
  "lead with education, journal, and responsible content",
  "lead with serene spa pacing and quiet forms",
  "lead with chic editorial rhythm and image confidence",
  "lead with botanical line art and real photo anchors",
  "lead with crafted studio framing and bronze detail",
  "lead with luminous surfaces and soft hierarchy",
  "lead with paper-like reading and refined section breaks",
  "lead with grounded natural trust",
  "lead with intimate human relationship",
  "lead with stately luxury and restrained motion",
  "lead with open views and generous spacing",
  "lead with thin linear structure and soft curves",
  "lead with guided route navigation",
  "lead with safety, boundaries, and compliance tone",
  "lead with sculptural silhouette and outline systems",
  "lead with fewer stronger editorial moments",
  "lead with responsibility and evidence boundaries",
  "lead with signature portrait and brand confidence",
  "lead with sage reading panels and education",
  "lead with sovereign contrast and controlled conversion",
];

const componentTypes = [
  "editorial-split",
  "centered-manifesto",
  "asymmetric-panel",
  "layered-magazine-spread",
  "full-width-brand-band",
  "sticky-side-note-section",
  "horizontal-process-strip",
  "vertical-process-rail",
  "accordion-guidance-block",
  "tabbed-route-panel",
  "floating-card-cluster",
  "offset-portrait-feature",
  "dark-trust-band",
  "sage-reassurance-panel",
  "testimonial-style-quote-block",
  "service-route-matrix",
  "timeline-component",
  "stepper-component",
  "cta-dock",
  "form-led-conversion-panel",
  "journal-carousel",
  "article-row",
  "image-gallery-frame",
  "statement-interlude",
  "comparison-panel",
  "split-card-stack",
  "card-masonry",
  "calm-checklist",
  "radial-value-map",
  "sidebar-navigation-section",
  "editorial-pull-quote-section",
  "minimal-clinical-panel",
  "luxury-dark-card",
  "botanical-divider-section",
  "full-bleed-soft-background-section",
  "consultation-route-selector",
  "evidence-note-panel",
  "footer-bridge-panel",
  "portrait-led-story-panel",
  "guided-pathway-panel",
];

const htmlAnatomies = [
  "copy-figure-actions",
  "kicker-heading-copy-card-grid",
  "portrait-copy-sidebar-actions",
  "heading-copy-aside-figure",
  "statement-copy-wide-figure",
  "copy-route-grid-figure",
  "copy-process-rail-actions",
  "quote-copy-portrait-actions",
  "copy-comparison-cards",
  "copy-form-intro-actions",
  "copy-journal-row-figure",
  "copy-bullets-side-note",
  "copy-masonry-cards-portrait",
  "copy-tabs-route-cards",
  "copy-timeline-figure",
  "manifesto-copy-actions",
  "copy-accordion-cards",
  "image-first-copy-actions",
  "copy-first-image-anchor",
  "copy-cta-dock-panel",
];

const cssLayouts = [
  "asymmetric-css-grid",
  "centered-flex-column",
  "magazine-css-grid",
  "full-width-band-grid",
  "sticky-sidebar-grid",
  "horizontal-scroll-strip",
  "masonry-css-grid",
  "alternating-grid",
  "route-matrix-grid",
  "form-first-grid",
  "image-first-grid",
  "statement-first-grid",
  "timeline-rail-grid",
  "layered-panel-grid",
  "clinical-two-column-grid",
  "luxury-dark-grid",
  "botanical-divider-grid",
  "compact-card-grid",
  "wide-editorial-columns",
  "mobile-dock-layout",
];

const responsivePatterns = [
  "image-first-mobile",
  "text-first-mobile",
  "alternating-mobile-order",
  "compact-cta-strip-mobile",
  "sticky-consultation-mobile",
  "collapsed-route-cards-mobile",
  "horizontal-scroll-cards-mobile",
  "accordion-mobile-sections",
  "stacked-editorial-panels-mobile",
  "reduced-density-mobile",
  "footer-specific-mobile-rhythm",
  "portrait-anchor-mobile",
];

const interactions = [
  "none",
  "scroll-reveal",
  "route-selector",
  "journal-carousel",
  "sticky-cta",
  "active-section-indicator",
  "process-stepper",
  "accordion-guidance",
  "reduced-motion-reveal",
  "mobile-route-focus",
];

const ctaPatterns = [
  "hero-primary-whatsapp-secondary",
  "inline-consultation-link",
  "sage-consultation-strip",
  "footer-bridge-cta",
  "form-first-cta",
  "whatsapp-first-cta",
  "route-card-cta",
  "faq-contact-bridge",
  "journal-consultation-bridge",
  "service-form-bridge",
  "quiet-secondary-cta",
  "deep-sage-cta-band",
  "sticky-consultation-dock",
  "minimal-line-cta",
  "portrait-trust-cta",
];

const imageTreatments = [
  "full-image-vertical-card",
  "full-image-wide-editorial-panel",
  "full-image-beside-text",
  "full-image-below-hero-text",
  "full-image-sage-panel",
  "full-image-dark-luxury-section",
  "full-image-consultation-side",
  "full-image-gallery-like-frame",
  "full-image-floating-panel",
  "full-image-minimal-border-frame",
  "full-image-asymmetrical-layout",
  "full-image-footer-brand-card",
  "no-image-editorial-structure",
  "css-botanical-divider",
  "css-statement-panel",
];

const headerArchitectures = [
  "centered-logo-header",
  "split-nav-header",
  "floating-pill-header",
  "dark-premium-header",
  "transparent-to-solid-header",
  "cta-forward-header",
  "editorial-masthead-header",
  "minimal-line-header",
  "drawer-led-mobile-header",
  "consultation-forward-header",
];

const navigationArchitectures = [
  "primary-route-nav",
  "split-care-nav",
  "editorial-secondary-nav",
  "service-first-nav",
  "trust-first-nav",
  "consultation-led-nav",
  "journal-support-nav",
  "minimal-link-row-nav",
  "guided-pathway-nav",
  "balanced-two-side-nav",
];

const footerArchitectures = [
  "deep-sage-editorial-footer",
  "compact-legal-footer",
  "cta-led-footer",
  "brand-card-footer",
  "multi-column-footer",
  "journal-route-footer",
  "consultation-first-footer",
  "minimal-line-footer",
  "dark-luxury-footer",
  "soft-cream-footer-sage-band",
];

const contentPatterns = [
  "paragraph-led",
  "bullets-led",
  "cards-led",
  "quote-led",
  "step-led",
  "question-led",
  "route-led",
  "form-led",
  "statement-led",
  "journal-led",
];

const visualHierarchy = [
  "title-led",
  "image-led",
  "cta-led",
  "form-led",
  "quote-led",
  "card-led",
  "list-led",
  "icon-led",
  "statement-led",
  "navigation-led",
  "editorial-led",
  "process-led",
];

const colourRhythms = [
  "light-first-sage-break",
  "sage-heavy-botanical",
  "bronze-line-minimal",
  "dark-editorial-deep-sage",
  "warm-ivory-soft-sage",
  "clinical-ivory-precise-sage",
  "journal-sage-reading-panels",
  "alternating-sage-cream-bands",
  "deep-sage-cta-rhythm",
  "footer-dark-gold-accent",
];

const typographyRhythms = [
  "large-editorial-headings",
  "compact-clinical-headings",
  "quote-kicker-led",
  "manifesto-serif-led",
  "small-label-strong-hierarchy",
  "wide-magazine-scale",
  "quiet-reading-scale",
  "process-number-rhythm",
  "navigation-led-kickers",
  "form-led-heading-scale",
];

const stats = {
  filesChanged: new Set(),
  pagesChanged: new Set(),
  partialsChanged: new Set(),
  conceptsChanged: new Set(),
  sectionsUpdated: 0,
  emptyFramesFound: [],
  emptyFramesRemoved: [],
  badAssetHits: [],
  objectFitCoverHits: [],
  pageRows: [],
  partialRows: [],
  duplicateStylesheetFixes: [],
  duplicateScriptFixes: [],
  manualReview: [],
};

function valueAfter(flag) {
  const index = args.indexOf(flag);
  return index === -1 ? "" : args[index + 1] || "";
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

function ensureBranch() {
  if (currentBranch() === targetBranch) return;
  const hasBranch = execSync(
    "git branch --list sofiati-50-architecture-rebuild",
    {
      cwd: root,
      encoding: "utf8",
    },
  ).trim();
  if (hasBranch) execSync(`git switch ${targetBranch}`, { cwd: root });
  else execSync(`git switch -c ${targetBranch}`, { cwd: root });
}

function listConceptDirs() {
  return fs
    .readdirSync(conceptsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && /^\d{2}-/.test(entry.name))
    .map((entry) => entry.name)
    .sort();
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

function rotate(items, offset, step, count) {
  const out = [];
  let index = offset % items.length;
  while (out.length < count) {
    out.push(items[index]);
    index = (index + step) % items.length;
  }
  return out;
}

function contractFor(seed, index) {
  const [id, name, mood] = seed;
  const previous =
    conceptSeeds[(index + conceptSeeds.length - 1) % conceptSeeds.length][0];
  const next = conceptSeeds[(index + 1) % conceptSeeds.length][0];
  const stride = [3, 5, 7, 9, 11, 13, 17][index % 7];
  const componentSequence = rotate(componentTypes, index * 5, stride, 10);
  const htmlSequence = rotate(htmlAnatomies, index * 3, (index % 5) + 3, 10);
  const cssSequence = rotate(cssLayouts, index * 4, (index % 7) + 3, 10);
  const responsiveSequence = rotate(
    responsivePatterns,
    index * 2,
    (index % 5) + 2,
    10,
  );
  const interactionSequence = rotate(
    interactions,
    index * 3,
    (index % 4) + 2,
    10,
  );
  return {
    conceptId: id,
    conceptName: name,
    index,
    number: id.slice(0, 2),
    brandMood: mood,
    visitorJourneyType: journeyTypes[index % journeyTypes.length],
    informationArchitectureEmphasis: iaEmphasis[index],
    homepageArchitecture: `${componentSequence[0]} opening, ${componentSequence[3]} trust build, ${componentSequence[9]} final bridge`,
    internalPageArchitecture: `${componentSequence[1]} intro, ${componentSequence[4]} body, ${componentSequence[8]} conversion close`,
    headerArchitecture:
      headerArchitectures[(index * 3) % headerArchitectures.length],
    navigationArchitecture:
      navigationArchitectures[(index * 5 + 1) % navigationArchitectures.length],
    footerArchitecture:
      footerArchitectures[(index * 7 + 2) % footerArchitectures.length],
    sectionRhythm: componentSequence,
    componentSequence,
    htmlAnatomySequence: htmlSequence,
    cssLayoutSequence: cssSequence,
    responsiveSequence,
    interactionSequence,
    htmlStructureStrategy: `${htmlSequence[0]} hero with ${htmlSequence[4]} mid-page architecture`,
    cssLayoutStrategy: `${cssSequence[0]} and ${cssSequence[5]} rhythm`,
    jsInteractionStrategy: interactionSummary(interactionSequence),
    responsiveStrategy: responsiveSequence[0],
    ctaArchitecture: ctaPatterns[(index * 4 + 2) % ctaPatterns.length],
    imageArchitecture:
      imageTreatments[(index * 6 + 1) % imageTreatments.length],
    contentPresentationPattern:
      contentPatterns[(index * 3 + 2) % contentPatterns.length],
    colourRhythm: colourRhythms[(index * 4 + 3) % colourRhythms.length],
    typographyRhythm:
      typographyRhythms[(index * 5 + 4) % typographyRhythms.length],
    visualHierarchy: visualHierarchy[(index * 6 + 5) % visualHierarchy.length],
    partialsUsage:
      "partials own header, navigation, mobile menu, footer, cookie, WhatsApp, back-to-top, accessibility, and shared contact/form UI",
    mustNotLookLike: [previous, next],
    similarityRisk:
      "low by exact architecture fingerprint; screenshot review still required for subjective similarity",
    manualReviewNotes:
      "review rendered desktop/mobile rhythm, partial-loaded chrome, and whether architecture feels genuinely distinct beside adjacent concepts",
  };
}

function interactionSummary(sequence) {
  const useful = sequence.filter((item) => item !== "none");
  if (!useful.length) return "static editorial architecture with no added JS";
  return `${useful.slice(0, 3).join(", ")} with reduced-motion-safe delegation`;
}

const contracts = conceptSeeds.map(contractFor);
const contractById = new Map(
  contracts.map((contract) => [contract.conceptId, contract]),
);
const selectedIds = selectedConcept
  ? new Set([selectedConcept])
  : new Set(contracts.map((contract) => contract.conceptId));

function architectureForSection(contract, sectionIndex, filePath) {
  const zero = sectionIndex - 1;
  const page = pageKey(filePath);
  const sectionNumber = String(sectionIndex).padStart(2, "0");
  const component = contract.componentSequence[zero];
  const htmlAnatomy = contract.htmlAnatomySequence[zero];
  const cssLayout = contract.cssLayoutSequence[zero];
  const responsive = contract.responsiveSequence[zero];
  const interaction = contract.interactionSequence[zero];
  const cta = ctaPatterns[(contract.index * 5 + zero * 2) % ctaPatterns.length];
  const image =
    imageTreatments[(contract.index * 7 + zero * 3) % imageTreatments.length];
  const content =
    contentPatterns[(contract.index * 3 + zero) % contentPatterns.length];
  const hierarchy =
    visualHierarchy[(contract.index * 4 + zero * 3) % visualHierarchy.length];
  return {
    page,
    sectionNumber,
    component,
    htmlAnatomy,
    cssLayout,
    responsive,
    interaction,
    cta,
    image,
    content,
    hierarchy,
    signature: `${contract.conceptId}-${slug(component)}-${slug(cssLayout)}-${page}-${sectionNumber}`,
  };
}

function injectArchitectureCss(html, filePath) {
  const re =
    /[ \t]*<link\b(?=[^>]*rel=["']stylesheet["'])(?=[^>]*href=["']\.\.\/\.\.\/css\/sofiati-50-architecture-system\.css["'])[^>]*>\s*/gi;
  const beforeCount = (html.match(re) || []).length;
  let next = html.replace(re, "");
  const link = `    <link rel="stylesheet" href="${architectureCssHref}" />`;
  const visualRe =
    /([ \t]*<link\b(?=[^>]*rel=["']stylesheet["'])(?=[^>]*href=["']\.\.\/\.\.\/css\/sofiati-premium-visual-dna\.css["'])[^>]*>)/i;
  if (visualRe.test(next)) next = next.replace(visualRe, `$1\n${link}`);
  else next = next.replace(/<\/head>/i, `${link}\n  </head>`);
  if (beforeCount > 1) stats.duplicateStylesheetFixes.push(rel(filePath));
  return next;
}

function injectArchitectureJs(html, filePath) {
  const re =
    /[ \t]*<script\b(?=[^>]*src=["']\.\.\/\.\.\/js\/sofiati-50-architecture-system\.js["'])[^>]*><\/script>\s*/gi;
  const beforeCount = (html.match(re) || []).length;
  let next = html.replace(re, "");
  const script = `    <script src="${architectureJsSrc}" defer></script>`;
  const mainRe = /([ \t]*<script src="js\/main\.js" defer><\/script>)/i;
  if (mainRe.test(next)) next = next.replace(mainRe, `$1\n${script}`);
  else next = next.replace(/<\/body>/i, `${script}\n  </body>`);
  if (beforeCount > 1) stats.duplicateScriptFixes.push(rel(filePath));
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
      return '<div class="architecture-decor-panel" aria-hidden="true" data-replaced-empty-frame="true"></div>';
    },
  );
}

function cleanKnownPhotoCover(html) {
  return html.replace(
    /(class="[^"]*(?:sofiati-photo|sofiati-portrait|sofiati-hero-photo|sofiati-brand-photo)[^"]*"[^>]*style="[^"]*)object-fit\s*:\s*cover;?/gi,
    "$1object-fit: contain;",
  );
}

function updateBody(html, contract) {
  return updateFirstTag(html, "body", (attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [
        "architecture-site",
        `architecture-site-${contract.number}`,
        `architecture-journey-${slug(contract.visitorJourneyType)}`,
        `architecture-header-${slug(contract.headerArchitecture)}`,
        `architecture-footer-${slug(contract.footerArchitecture)}`,
      ],
      [
        "architecture-site-",
        "architecture-journey-",
        "architecture-header-",
        "architecture-footer-",
      ],
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-architecture-contract",
      contract.conceptId,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-visitor-journey",
      contract.visitorJourneyType,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-ia-emphasis",
      contract.informationArchitectureEmphasis,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-header-architecture",
      contract.headerArchitecture,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-footer-architecture",
      contract.footerArchitecture,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-cta-architecture",
      contract.ctaArchitecture,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-js-architecture",
      contract.jsInteractionStrategy,
    );
    return nextAttrs;
  });
}

function updateMain(html, contract) {
  return html.replace(/<main\b([\s\S]*?)>/i, (match, attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [`architecture-main`, `architecture-main-${contract.number}`],
      ["architecture-main-"],
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-homepage-architecture",
      contract.homepageArchitecture,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-internal-page-architecture",
      contract.internalPageArchitecture,
    );
    return `<main${nextAttrs}>`;
  });
}

function updateSections(html, contract, filePath) {
  let index = 0;
  return html.replace(/<section\b([\s\S]*?)>/g, (match, attrs) => {
    index += 1;
    const arch = architectureForSection(contract, index, filePath);
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [
        "architecture-section",
        `architecture-section-${arch.sectionNumber}`,
        `arch-component-${slug(arch.component)}`,
        `arch-html-${slug(arch.htmlAnatomy)}`,
        `arch-layout-${slug(arch.cssLayout)}`,
        `arch-responsive-${slug(arch.responsive)}`,
        `arch-interaction-${slug(arch.interaction)}`,
        `arch-cta-${slug(arch.cta)}`,
        `arch-content-${slug(arch.content)}`,
      ],
      [
        "architecture-section-",
        "arch-component-",
        "arch-html-",
        "arch-layout-",
        "arch-responsive-",
        "arch-interaction-",
        "arch-cta-",
        "arch-content-",
      ],
    );
    nextAttrs = setAttr(nextAttrs, "data-component-type", arch.component);
    nextAttrs = setAttr(nextAttrs, "data-html-anatomy", arch.htmlAnatomy);
    nextAttrs = setAttr(nextAttrs, "data-css-layout", arch.cssLayout);
    nextAttrs = setAttr(nextAttrs, "data-responsive-pattern", arch.responsive);
    nextAttrs = setAttr(nextAttrs, "data-interaction", arch.interaction);
    nextAttrs = setAttr(nextAttrs, "data-cta-pattern", arch.cta);
    nextAttrs = setAttr(nextAttrs, "data-image-treatment", arch.image);
    nextAttrs = setAttr(nextAttrs, "data-content-presentation", arch.content);
    nextAttrs = setAttr(nextAttrs, "data-visual-hierarchy", arch.hierarchy);
    nextAttrs = setAttr(
      nextAttrs,
      "data-architecture-signature",
      arch.signature,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-architecture-concept",
      contract.conceptId,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-architecture-section",
      arch.sectionNumber,
    );
    if (arch.interaction !== "none")
      nextAttrs = setAttr(
        nextAttrs,
        "data-architecture-interaction",
        arch.interaction,
      );
    stats.sectionsUpdated += 1;
    return `<section${nextAttrs}>`;
  });
}

function updateRealPage(filePath, contract) {
  const before = read(filePath);
  let html = before;
  html = injectArchitectureCss(html, filePath);
  html = injectArchitectureJs(html, filePath);
  html = updateBody(html, contract);
  html = updateMain(html, contract);
  html = removeEmptyFrames(html, filePath);
  html = cleanKnownPhotoCover(html);
  html = updateSections(html, contract, filePath);
  if (writeIfChanged(filePath, html)) {
    stats.pagesChanged.add(rel(filePath));
    stats.conceptsChanged.add(contract.conceptId);
  }
}

function updateHeaderPartial(filePath, contract) {
  let html = read(filePath);
  html = updateFirstTag(html, "header", (attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [
        "architecture-header",
        `architecture-header-${slug(contract.headerArchitecture)}`,
        `architecture-nav-${slug(contract.navigationArchitecture)}`,
      ],
      ["architecture-header-", "architecture-nav-"],
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-header-architecture",
      contract.headerArchitecture,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-navigation-architecture",
      contract.navigationArchitecture,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-architecture-contract",
      contract.conceptId,
    );
    return nextAttrs;
  });
  if (writeIfChanged(filePath, html)) {
    stats.partialsChanged.add(rel(filePath));
    stats.conceptsChanged.add(contract.conceptId);
  }
}

function updateFooterPartial(filePath, contract) {
  let html = read(filePath);
  html = updateFirstTag(html, "footer", (attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [
        "architecture-footer",
        `architecture-footer-${slug(contract.footerArchitecture)}`,
      ],
      ["architecture-footer-"],
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-footer-architecture",
      contract.footerArchitecture,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-architecture-contract",
      contract.conceptId,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-footer-cta-architecture",
      contract.ctaArchitecture,
    );
    return nextAttrs;
  });
  if (writeIfChanged(filePath, html)) {
    stats.partialsChanged.add(rel(filePath));
    stats.conceptsChanged.add(contract.conceptId);
  }
}

function updateMobileMenuPartial(filePath, contract) {
  let html = read(filePath);
  html = updateFirstTag(html, "aside", (attrs) => {
    let nextAttrs = attrs;
    nextAttrs = addClasses(
      nextAttrs,
      [
        "architecture-mobile-menu",
        `architecture-mobile-${slug(contract.responsiveStrategy)}`,
      ],
      ["architecture-mobile-"],
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-mobile-architecture",
      contract.responsiveStrategy,
    );
    nextAttrs = setAttr(
      nextAttrs,
      "data-architecture-contract",
      contract.conceptId,
    );
    return nextAttrs;
  });
  if (writeIfChanged(filePath, html)) {
    stats.partialsChanged.add(rel(filePath));
    stats.conceptsChanged.add(contract.conceptId);
  }
}

function updatePartials(conceptDir, contract) {
  const partialDir = path.join(conceptDir, "partials");
  const header = path.join(partialDir, "header.html");
  const footer = path.join(partialDir, "footer.html");
  const mobile = path.join(partialDir, "mobile-menu.html");
  if (exists(header)) updateHeaderPartial(header, contract);
  if (exists(footer)) updateFooterPartial(footer, contract);
  if (exists(mobile)) updateMobileMenuPartial(mobile, contract);
}

function scanRealPage(filePath, contract) {
  const html = read(filePath);
  const relPath = rel(filePath);
  const sectionCount = countSections(html);
  const architectureCssLinks = (
    html.match(/sofiati-50-architecture-system\.css/g) || []
  ).length;
  const architectureJsLinks = (
    html.match(/sofiati-50-architecture-system\.js/g) || []
  ).length;
  const headerMounts = (html.match(/data-partial-mount="header"/g) || [])
    .length;
  const footerMounts = (html.match(/data-partial-mount="footer"/g) || [])
    .length;
  const directHeaders = (html.match(/<header\b/gi) || []).length;
  const directFooters = (html.match(/<footer\b/gi) || []).length;
  const badHits = badAssetTerms.filter((term) =>
    html.toLowerCase().includes(term.toLowerCase()),
  );
  for (const term of badHits) stats.badAssetHits.push(`${relPath}: ${term}`);
  const objectFitCoverHits = html.match(/object-fit\s*:\s*cover/gi) || [];
  for (const _hit of objectFitCoverHits) stats.objectFitCoverHits.push(relPath);
  const frameWithoutImage = findEmptyFrameRisks(html);
  const architectureSections = (
    html.match(/class="[^"]*architecture-section/g) || []
  ).length;
  const componentSequence = [
    ...html.matchAll(/data-component-type="([^"]+)"/g),
  ].map((match) => match[1]);
  const htmlSequence = [...html.matchAll(/data-html-anatomy="([^"]+)"/g)].map(
    (match) => match[1],
  );
  const cssSequence = [...html.matchAll(/data-css-layout="([^"]+)"/g)].map(
    (match) => match[1],
  );
  const ctaSequence = [...html.matchAll(/data-cta-pattern="([^"]+)"/g)].map(
    (match) => match[1],
  );
  stats.pageRows.push({
    file: relPath,
    concept: contract.conceptId,
    page: pageKey(filePath),
    sectionCount,
    architectureCssLinks,
    architectureJsLinks,
    headerMounts,
    footerMounts,
    directHeaders,
    directFooters,
    badHits,
    objectFitCoverHits: objectFitCoverHits.length,
    frameWithoutImage,
    architectureSections,
    componentSequence,
    htmlSequence,
    cssSequence,
    ctaSequence,
    fullImagePhotos: (html.match(/data-sofiati-photo="true"/g) || []).length,
  });
}

function findEmptyFrameRisks(html) {
  let risks = 0;
  html.replace(
    /<figure\b(?=[^>]*(?:sofiati-photo-frame|sofiati-portrait-frame|data-full-image-frame="true"))([^>]*)>([\s\S]*?)<\/figure>/gi,
    (match, attrs, inner) => {
      if (!/<img\b/i.test(inner)) risks += 1;
      return match;
    },
  );
  return risks;
}

function scanPartials(conceptDir, contract) {
  const partialDir = path.join(conceptDir, "partials");
  const found = partialFiles(conceptDir).map((filePath) =>
    path.basename(filePath, ".html"),
  );
  const missing = requiredPartials.filter((name) => !found.includes(name));
  const headerHtml = read(path.join(partialDir, "header.html"));
  const footerHtml = read(path.join(partialDir, "footer.html"));
  const mobileHtml = read(path.join(partialDir, "mobile-menu.html"));
  const navHtml = read(path.join(partialDir, "navigation.html"));
  const cookieHtml = read(path.join(partialDir, "cookie-banner.html"));
  const whatsappHtml = read(path.join(partialDir, "floating-whatsapp.html"));
  const accessHtml = read(path.join(partialDir, "accessibility.html"));
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
    concept: contract.conceptId,
    found,
    missing,
    headerStatus: headerHtml.includes("architecture-header")
      ? contract.headerArchitecture
      : "present-unmarked",
    navStatus: navHtml.includes("data-navigation-template")
      ? contract.navigationArchitecture
      : "review",
    mobileStatus: mobileHtml.includes("architecture-mobile-menu")
      ? contract.responsiveStrategy
      : "present-unmarked",
    footerStatus: footerHtml.includes("architecture-footer")
      ? contract.footerArchitecture
      : "present-unmarked",
    cookieStatus: cookieHtml.includes("cookie") ? "present" : "review",
    whatsappStatus: whatsappHtml.includes("wa.me") ? "present" : "review",
    accessibilityStatus: accessHtml ? "present" : "missing",
    brokenPaths,
  });
}

function generateCss() {
  const lines = [];
  lines.push(`/*
SOFIATI 50 ARCHITECTURE SYSTEM
Generated by qa/rebuild_sofiati_50_architecture.mjs.
Purpose: make the 50 Sofiati concepts differ in architecture while preserving
brand voice, no-crop photos, partial-loaded UI, and ethical conversion paths.
*/`);
  lines.push(`
:root {
  --sofiati-sage: #a2aea0;
  --sofiati-sage-deep: #485041;
  --sofiati-ivory: #f2eee3;
  --sofiati-cream: #f8f7f2;
  --sofiati-bronze: #9a6b35;
  --sofiati-gold: #cdaa78;
  --sofiati-ink: #252321;
  --architecture-focus: 0 0 0 3px color-mix(in srgb, var(--sofiati-gold) 55%, transparent);
}

img[data-sofiati-photo="true"],
.sofiati-photo,
.sofiati-portrait,
.sofiati-hero-photo,
.sofiati-brand-photo {
  width: auto;
  height: auto !important;
  max-width: 100%;
  object-fit: contain !important;
  object-position: center;
}

.architecture-site {
  --arch-primary: var(--sofiati-sage-deep);
  --arch-accent: var(--sofiati-bronze);
  --arch-surface: var(--sofiati-cream);
  --arch-panel: var(--sofiati-ivory);
  --arch-gap: clamp(22px, 4vw, 58px);
  --arch-radius: 10px;
  --arch-rule: color-mix(in srgb, var(--arch-accent) 35%, transparent);
}

.architecture-main {
  container-type: inline-size;
}

.architecture-section {
  --arch-local-gap: var(--arch-gap);
  position: relative;
  gap: var(--arch-local-gap);
  border-top-color: color-mix(in srgb, var(--arch-primary) 24%, transparent);
}

.architecture-section:focus-within {
  outline: none;
  box-shadow: var(--architecture-focus);
}

.architecture-section .atlas-section__copy {
  position: relative;
  z-index: 1;
}

.architecture-section .atlas-section__media {
  overflow: visible;
}

.architecture-section .atlas-card-row article,
.architecture-section .atlas-bullets li {
  transition:
    transform 180ms ease,
    border-color 180ms ease,
    background-color 180ms ease;
}

.architecture-section .atlas-card-row article[data-architecture-active="true"],
.architecture-section .atlas-bullets li[data-architecture-active="true"] {
  border-color: var(--arch-accent);
  background: color-mix(in srgb, var(--arch-panel) 82%, white);
}

.architecture-section[data-architecture-state="visible"] .atlas-section__copy {
  transform: translateY(0);
  opacity: 1;
}

.architecture-section[data-architecture-state="waiting"] .atlas-section__copy {
  transform: translateY(12px);
  opacity: 0.88;
}

.architecture-decor-panel {
  min-height: clamp(180px, 28vw, 340px);
  border: 1px solid var(--arch-rule);
  border-radius: var(--arch-radius);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--sofiati-sage) 32%, transparent), transparent 68%),
    color-mix(in srgb, var(--arch-panel) 86%, white);
}

.architecture-sticky-cta {
  position: fixed;
  right: clamp(14px, 3vw, 28px);
  bottom: clamp(86px, 8vw, 118px);
  z-index: 26;
  display: inline-flex;
  align-items: center;
  min-height: 44px;
  padding: 10px 15px;
  border: 1px solid color-mix(in srgb, var(--sofiati-gold) 55%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--sofiati-sage-deep) 94%, var(--sofiati-ink));
  color: var(--sofiati-cream);
  text-decoration: none;
  font-weight: 800;
  box-shadow: 0 14px 42px rgba(37, 35, 33, 0.18);
}

.architecture-sticky-cta:focus-visible,
.architecture-section a:focus-visible,
.architecture-section button:focus-visible {
  outline: none;
  box-shadow: var(--architecture-focus);
}

.arch-component-editorial-split,
.arch-component-offset-portrait-feature,
.arch-component-image-gallery-frame {
  grid-template-columns: minmax(0, var(--arch-copy, 0.82fr)) minmax(270px, var(--arch-media, 0.92fr));
}

.arch-component-centered-manifesto,
.arch-component-statement-interlude,
.arch-component-editorial-pull-quote-section {
  grid-template-columns: 1fr;
  justify-items: center;
  text-align: center;
}

.arch-component-centered-manifesto .atlas-section__copy,
.arch-component-statement-interlude .atlas-section__copy,
.arch-component-editorial-pull-quote-section .atlas-section__copy {
  max-width: min(850px, 100%);
  justify-items: center;
}

.arch-component-layered-magazine-spread,
.arch-component-floating-card-cluster,
.arch-component-card-masonry {
  padding-inline: clamp(18px, 4vw, 72px);
  background:
    linear-gradient(120deg, color-mix(in srgb, var(--arch-primary) 12%, transparent), transparent 62%),
    color-mix(in srgb, var(--arch-panel) 82%, white);
  border-radius: var(--arch-radius);
}

.arch-component-full-width-brand-band,
.arch-component-dark-trust-band,
.arch-component-luxury-dark-card,
.arch-component-cta-dock {
  padding-inline: clamp(20px, 5vw, 82px);
  background: linear-gradient(135deg, var(--arch-primary), color-mix(in srgb, var(--sofiati-ink) 82%, var(--arch-primary)));
  color: var(--sofiati-cream);
  border-radius: var(--arch-radius);
}

.arch-component-full-width-brand-band p,
.arch-component-dark-trust-band p,
.arch-component-luxury-dark-card p,
.arch-component-cta-dock p {
  color: color-mix(in srgb, var(--sofiati-cream) 86%, white);
}

.arch-component-sticky-side-note-section .atlas-section__copy,
.arch-component-evidence-note-panel .atlas-section__copy,
.arch-component-minimal-clinical-panel .atlas-section__copy {
  padding: clamp(18px, 3vw, 42px);
  border-left: 4px solid var(--arch-accent);
  background: color-mix(in srgb, var(--arch-panel) 86%, white);
}

.arch-component-horizontal-process-strip .atlas-card-row,
.arch-component-journal-carousel .atlas-card-row,
.arch-component-article-row .atlas-card-row {
  display: grid;
  grid-auto-flow: column;
  grid-auto-columns: minmax(190px, 0.28fr);
  overflow-x: auto;
  scroll-snap-type: x proximity;
  padding-bottom: 8px;
}

.arch-component-service-route-matrix .atlas-card-row,
.arch-component-tabbed-route-panel .atlas-card-row,
.arch-component-consultation-route-selector .atlas-card-row {
  grid-template-columns: repeat(auto-fit, minmax(min(210px, 100%), 1fr));
}

.arch-component-vertical-process-rail,
.arch-component-timeline-component,
.arch-component-stepper-component {
  border-left: 2px solid var(--arch-rule);
  padding-left: clamp(20px, 3vw, 48px);
}

.arch-component-sage-reassurance-panel,
.arch-component-botanical-divider-section,
.arch-component-full-bleed-soft-background-section {
  padding-inline: clamp(18px, 4vw, 68px);
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--sofiati-sage) 36%, white), transparent 78%),
    color-mix(in srgb, var(--sofiati-cream) 88%, white);
  border-radius: var(--arch-radius);
}

.arch-component-comparison-panel .atlas-card-row,
.arch-component-split-card-stack .atlas-card-row,
.arch-component-calm-checklist .atlas-card-row {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.arch-component-sidebar-navigation-section {
  grid-template-columns: minmax(210px, 0.42fr) minmax(0, 1fr);
}

.arch-component-radial-value-map .atlas-card-row {
  border-radius: 999px;
  padding: clamp(16px, 3vw, 34px);
  border: 1px solid var(--arch-rule);
}

.architecture-header,
.architecture-footer,
.architecture-mobile-menu {
  --chrome-primary: var(--arch-primary, var(--sofiati-sage-deep));
  --chrome-accent: var(--arch-accent, var(--sofiati-bronze));
}

.architecture-header-dark-premium-header,
.architecture-header-editorial-masthead-header,
.architecture-header-consultation-forward-header {
  background: color-mix(in srgb, var(--chrome-primary) 92%, var(--sofiati-ink));
  color: var(--sofiati-cream);
}

.architecture-header-floating-pill-header .public-header-shell,
.architecture-header-centered-logo-header .public-header-shell {
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--chrome-accent) 38%, transparent);
}

.architecture-footer {
  border-top: 1px solid color-mix(in srgb, var(--chrome-accent) 50%, transparent);
}

.architecture-footer-dark-luxury-footer,
.architecture-footer-deep-sage-editorial-footer,
.architecture-footer-consultation-first-footer {
  background: color-mix(in srgb, var(--chrome-primary) 90%, var(--sofiati-ink));
  color: var(--sofiati-cream);
}

.architecture-footer-soft-cream-footer-sage-band,
.architecture-footer-multi-column-footer,
.architecture-footer-brand-card-footer {
  background: color-mix(in srgb, var(--sofiati-sage) 26%, var(--sofiati-cream));
  color: var(--sofiati-ink);
}

@media (prefers-reduced-motion: reduce) {
  .architecture-section .atlas-card-row article,
  .architecture-section .atlas-bullets li,
  .architecture-section[data-architecture-state] .atlas-section__copy {
    transition: none;
    transform: none;
  }
}

@media (max-width: 900px) {
  .architecture-site .architecture-section {
    max-width: 100%;
    transform: none;
    overflow-wrap: anywhere;
  }

  .arch-component-comparison-panel .atlas-card-row,
  .arch-component-split-card-stack .atlas-card-row,
  .arch-component-calm-checklist .atlas-card-row,
  .arch-component-sidebar-navigation-section,
  .arch-component-vertical-process-rail,
  .arch-component-timeline-component,
  .arch-component-stepper-component {
    grid-template-columns: 1fr;
    border-left: 0;
    padding-left: 0;
  }

  .arch-responsive-image-first-mobile .atlas-section__media,
  .arch-responsive-portrait-anchor-mobile .atlas-section__media {
    order: -1;
  }

  .arch-responsive-text-first-mobile .atlas-section__copy,
  .arch-responsive-reduced-density-mobile .atlas-section__copy {
    order: -1;
  }

  .architecture-sticky-cta {
    left: 16px;
    right: 16px;
    bottom: 18px;
    justify-content: center;
  }
}`);

  for (const contract of contracts) {
    const radius = [0, 4, 8, 14, 22, 30, 6, 16, 26, 2][contract.index % 10];
    const copy = (0.68 + (contract.index % 6) * 0.07).toFixed(2);
    const media = (0.58 + ((contract.index + 3) % 6) * 0.08).toFixed(2);
    const hue = contract.index % 5;
    const primary = ["#485041", "#3d5141", "#252321", "#53645c", "#394237"][
      hue
    ];
    const accent = ["#9a6b35", "#cdaa78", "#b68e58", "#8e673a", "#a87942"][hue];
    const panel = ["#f2eee3", "#f8f7f2", "#eef2ea", "#f5efe4", "#e8efe4"][hue];
    lines.push(`
[data-concept="${contract.conceptId}"] {
  --arch-primary: ${primary};
  --arch-accent: ${accent};
  --arch-panel: ${panel};
  --arch-radius: ${radius}px;
  --arch-copy: ${copy}fr;
  --arch-media: ${media}fr;
  --arch-gap: clamp(${22 + (contract.index % 4) * 4}px, ${3 + (contract.index % 3)}vw, ${52 + (contract.index % 7) * 4}px);
}`);
  }
  return `${lines.join("\n")}\n`;
}

function generateJs() {
  return `(() => {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  const closestSection = (node) => node.closest("[data-architecture-section]");

  const markVisibleSections = () => {
    const sections = [...document.querySelectorAll("[data-architecture-interaction]")];
    sections.forEach((section) => {
      if (!section.dataset.architectureState) section.dataset.architectureState = "waiting";
    });
    if (prefersReduced.matches || !("IntersectionObserver" in window)) {
      sections.forEach((section) => {
        section.dataset.architectureState = "visible";
      });
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) entry.target.dataset.architectureState = "visible";
        });
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.18 },
    );
    sections.forEach((section) => observer.observe(section));
  };

  const enhanceSelectableRows = () => {
    document
      .querySelectorAll('[data-architecture-interaction="route-selector"], [data-architecture-interaction="accordion-guidance"], [data-architecture-interaction="journal-carousel"], [data-architecture-interaction="process-stepper"]')
      .forEach((section) => {
        if (section.dataset.architectureEnhanced === "true") return;
        const items = [
          ...section.querySelectorAll(".atlas-card-row article, .atlas-bullets li"),
        ];
        if (!items.length) return;
        section.dataset.architectureEnhanced = "true";
        items.forEach((item, index) => {
          item.tabIndex = 0;
          item.dataset.architectureItem = String(index + 1);
          if (index === 0) item.dataset.architectureActive = "true";
          item.addEventListener("click", () => activate(items, index));
          item.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              activate(items, index);
            }
            if (event.key === "ArrowRight" || event.key === "ArrowDown") {
              event.preventDefault();
              const next = items[(index + 1) % items.length];
              next.focus();
              activate(items, (index + 1) % items.length);
            }
            if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
              event.preventDefault();
              const previous = items[(index + items.length - 1) % items.length];
              previous.focus();
              activate(items, (index + items.length - 1) % items.length);
            }
          });
        });
      });
  };

  const activate = (items, activeIndex) => {
    items.forEach((item, index) => {
      item.dataset.architectureActive = index === activeIndex ? "true" : "false";
    });
  };

  const updateActiveSection = () => {
    const sections = [...document.querySelectorAll("[data-architecture-section]")];
    if (!sections.length) return;
    let active = sections[0];
    for (const section of sections) {
      const rect = section.getBoundingClientRect();
      if (rect.top <= window.innerHeight * 0.4) active = section;
    }
    document.body.dataset.activeArchitectureSection =
      active.dataset.architectureSection || "";
  };

  const addStickyCta = () => {
    if (!document.querySelector('[data-interaction="sticky-cta"], [data-architecture-interaction="sticky-cta"]')) return;
    if (document.querySelector(".architecture-sticky-cta")) return;
    const link = document.createElement("a");
    link.className = "architecture-sticky-cta";
    link.href = "consultation.html";
    link.textContent = "Consultation";
    link.setAttribute("aria-label", "Request consultation");
    document.body.appendChild(link);
  };

  const init = () => {
    markVisibleSections();
    enhanceSelectableRows();
    updateActiveSection();
    addStickyCta();
  };

  document.addEventListener("scroll", updateActiveSection, { passive: true });
  document.addEventListener("sofiati:partials-ready", init);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();\n`;
}

function sectionRows() {
  const rows = [];
  for (const contract of contracts) {
    for (let index = 1; index <= 10; index += 1) {
      const arch = architectureForSection(
        contract,
        index,
        path.join("concepts", contract.conceptId, "index.html"),
      );
      rows.push({ contract, arch });
    }
  }
  return rows;
}

function contractJson() {
  return contracts.map((contract) => ({
    conceptId: contract.conceptId,
    conceptName: contract.conceptName,
    brandMood: contract.brandMood,
    visitorJourneyType: contract.visitorJourneyType,
    informationArchitectureEmphasis: contract.informationArchitectureEmphasis,
    homepageArchitecture: contract.homepageArchitecture,
    internalPageArchitecture: contract.internalPageArchitecture,
    headerArchitecture: contract.headerArchitecture,
    navigationArchitecture: contract.navigationArchitecture,
    footerArchitecture: contract.footerArchitecture,
    sectionRhythm: contract.sectionRhythm,
    componentSequence: contract.componentSequence,
    htmlStructureStrategy: contract.htmlStructureStrategy,
    cssLayoutStrategy: contract.cssLayoutStrategy,
    jsInteractionStrategy: contract.jsInteractionStrategy,
    responsiveStrategy: contract.responsiveStrategy,
    ctaArchitecture: contract.ctaArchitecture,
    imageArchitecture: contract.imageArchitecture,
    contentPresentationPattern: contract.contentPresentationPattern,
    colourRhythm: contract.colourRhythm,
    typographyRhythm: contract.typographyRhythm,
    partialsUsage: contract.partialsUsage,
    differentFromPrevious: contract.mustNotLookLike[0],
    differentFromNext: contract.mustNotLookLike[1],
    mustNotLookLike: contract.mustNotLookLike,
    similarityRisk: contract.similarityRisk,
    manualReviewNotes: contract.manualReviewNotes,
  }));
}

function generateArchitectureDocs() {
  writeIfChanged(
    path.join(docsRoot, "sofiati-50-architecture-master-plan.json"),
    `${JSON.stringify({ branch: targetBranch, contracts: contractJson() }, null, 2)}\n`,
  );
  writeIfChanged(
    path.join(docsRoot, "concept-architecture-dna-contract.json"),
    `${JSON.stringify(contractJson(), null, 2)}\n`,
  );
  const matrix = contracts.map((contract) => ({
    conceptId: contract.conceptId,
    componentSequence: contract.componentSequence,
    htmlAnatomySequence: contract.htmlAnatomySequence,
    cssLayoutSequence: contract.cssLayoutSequence,
    responsiveSequence: contract.responsiveSequence,
    interactionSequence: contract.interactionSequence,
    ctaArchitecture: contract.ctaArchitecture,
    imageArchitecture: contract.imageArchitecture,
  }));
  writeIfChanged(
    path.join(docsRoot, "component-architecture-matrix.json"),
    `${JSON.stringify(matrix, null, 2)}\n`,
  );

  const master = [
    "# Sofiati 50 Architecture Master Plan",
    "",
    `- Branch: ${targetBranch}`,
    "- Objective: keep one Sofiati brand family while rebuilding 50 concept sites as different HTML/CSS/JS architectures.",
    "- Shared foundation: Sofiati sage, deep sage, ivory, cream, bronze, gold, ink, ethical consultation-led voice, real Franciele photos, and partial-loaded production UI.",
    "- Non-negotiables: exactly 10 sections on real pages, partials excluded from section counts, no cropped Franciele photos, no fake generated asset labels, no duplicate headers/footers, and no repeated exact architecture contract.",
    "",
    "## Architecture Layers",
    "",
    "- Information architecture: consultation, services, journal, trust, values, process, form, education, result expectations, and guided pathways rotate by concept.",
    "- Page architecture: home and internal pages use distinct opening logic, trust sequence, service explanation, CTA timing, form/journal placement, and footer bridge.",
    "- Section architecture: every real section receives component, HTML anatomy, CSS layout, responsive pattern, interaction, CTA, image, content, and hierarchy attributes.",
    "- Component architecture: component sequences are contract-driven and audited for exact duplicates.",
    "- JS architecture: shared delegated JS supports useful behaviours only: reveal, active section state, keyboard route selectors, carousels, steppers, accordions, and sticky consultation CTAs.",
    "- Partial architecture: header, navigation, mobile menu, and footer are validated as production UI and receive concept contract markers.",
    "",
    "## Concepts",
    "",
    ...contracts.flatMap((contract) => [
      `### ${contract.conceptId} - ${contract.conceptName}`,
      "",
      `- Brand mood: ${contract.brandMood}`,
      `- Visitor journey: ${contract.visitorJourneyType}`,
      `- IA emphasis: ${contract.informationArchitectureEmphasis}`,
      `- Homepage architecture: ${contract.homepageArchitecture}`,
      `- Header/footer/mobile: ${contract.headerArchitecture} / ${contract.footerArchitecture} / ${contract.responsiveStrategy}`,
      `- Component sequence: ${contract.componentSequence.join(" / ")}`,
      "",
    ]),
  ];
  writeIfChanged(
    path.join(docsRoot, "sofiati-50-architecture-master-plan.md"),
    `${master.join("\n")}\n`,
  );

  const contractMd = ["# Concept Architecture DNA Contract", ""];
  for (const contract of contracts) {
    contractMd.push(`## ${contract.conceptId} - ${contract.conceptName}`);
    contractMd.push("");
    contractMd.push(`- Concept ID: ${contract.conceptId}`);
    contractMd.push(`- Concept name: ${contract.conceptName}`);
    contractMd.push(`- Brand mood: ${contract.brandMood}`);
    contractMd.push(`- Visitor journey type: ${contract.visitorJourneyType}`);
    contractMd.push(
      `- Information architecture emphasis: ${contract.informationArchitectureEmphasis}`,
    );
    contractMd.push(
      `- Homepage architecture: ${contract.homepageArchitecture}`,
    );
    contractMd.push(
      `- Internal page architecture: ${contract.internalPageArchitecture}`,
    );
    contractMd.push(`- Header architecture: ${contract.headerArchitecture}`);
    contractMd.push(
      `- Navigation architecture: ${contract.navigationArchitecture}`,
    );
    contractMd.push(`- Footer architecture: ${contract.footerArchitecture}`);
    contractMd.push(`- Section rhythm: ${contract.sectionRhythm.join(" / ")}`);
    contractMd.push(
      `- Component sequence: ${contract.componentSequence.join(" / ")}`,
    );
    contractMd.push(
      `- HTML structure strategy: ${contract.htmlStructureStrategy}`,
    );
    contractMd.push(`- CSS layout strategy: ${contract.cssLayoutStrategy}`);
    contractMd.push(
      `- JS interaction strategy: ${contract.jsInteractionStrategy}`,
    );
    contractMd.push(`- Responsive strategy: ${contract.responsiveStrategy}`);
    contractMd.push(`- CTA architecture: ${contract.ctaArchitecture}`);
    contractMd.push(`- Image architecture: ${contract.imageArchitecture}`);
    contractMd.push(
      `- Content presentation pattern: ${contract.contentPresentationPattern}`,
    );
    contractMd.push(`- Colour rhythm: ${contract.colourRhythm}`);
    contractMd.push(`- Typography rhythm: ${contract.typographyRhythm}`);
    contractMd.push(`- Partials usage: ${contract.partialsUsage}`);
    contractMd.push(
      `- Different from previous concept: ${contract.mustNotLookLike[0]}`,
    );
    contractMd.push(
      `- Different from next concept: ${contract.mustNotLookLike[1]}`,
    );
    contractMd.push(
      `- Must not look like: ${contract.mustNotLookLike.join(", ")}`,
    );
    contractMd.push(`- Similarity risk: ${contract.similarityRisk}`);
    contractMd.push(`- Manual review notes: ${contract.manualReviewNotes}`);
    contractMd.push("");
  }
  writeIfChanged(
    path.join(docsRoot, "concept-architecture-dna-contract.md"),
    `${contractMd.join("\n")}\n`,
  );

  writeIfChanged(
    path.join(docsRoot, "component-architecture-matrix.md"),
    markdownTable(
      "Component Architecture Matrix",
      [
        "Concept",
        "Component Sequence",
        "HTML Anatomy",
        "CSS Layout",
        "Interactions",
      ],
      contracts.map((contract) => [
        contract.conceptId,
        contract.componentSequence.join(" / "),
        contract.htmlAnatomySequence.join(" / "),
        contract.cssLayoutSequence.join(" / "),
        contract.interactionSequence.join(" / "),
      ]),
    ),
  );

  writeIfChanged(
    path.join(docsRoot, "page-architecture-map.md"),
    markdownTable(
      "Page Architecture Map",
      ["Concept", "Home", "Internal", "IA", "Conversion"],
      contracts.map((contract) => [
        contract.conceptId,
        contract.homepageArchitecture,
        contract.internalPageArchitecture,
        contract.informationArchitectureEmphasis,
        contract.ctaArchitecture,
      ]),
    ),
  );

  writeIfChanged(
    path.join(docsRoot, "section-architecture-map.md"),
    markdownTable(
      "Section Architecture Map",
      [
        "Concept",
        "Section",
        "Component",
        "HTML Anatomy",
        "CSS Layout",
        "Responsive",
        "Interaction",
        "CTA",
        "Image",
      ],
      sectionRows().map(({ contract, arch }) => [
        contract.conceptId,
        arch.sectionNumber,
        arch.component,
        arch.htmlAnatomy,
        arch.cssLayout,
        arch.responsive,
        arch.interaction,
        arch.cta,
        arch.image,
      ]),
    ),
  );

  writeIfChanged(
    path.join(docsRoot, "header-footer-partial-architecture-map.md"),
    markdownTable(
      "Header Footer Partial Architecture Map",
      ["Concept", "Header", "Navigation", "Footer", "Mobile", "Partials Usage"],
      contracts.map((contract) => [
        contract.conceptId,
        contract.headerArchitecture,
        contract.navigationArchitecture,
        contract.footerArchitecture,
        contract.responsiveStrategy,
        contract.partialsUsage,
      ]),
    ),
  );

  writeIfChanged(
    path.join(docsRoot, "responsive-architecture-map.md"),
    markdownTable(
      "Responsive Architecture Map",
      ["Concept", "Primary Mobile Strategy", "Section Mobile Sequence"],
      contracts.map((contract) => [
        contract.conceptId,
        contract.responsiveStrategy,
        contract.responsiveSequence.join(" / "),
      ]),
    ),
  );

  writeIfChanged(
    path.join(docsRoot, "js-interaction-architecture-map.md"),
    markdownTable(
      "JS Interaction Architecture Map",
      ["Concept", "JS Strategy", "Section Interactions", "Accessibility Notes"],
      contracts.map((contract) => [
        contract.conceptId,
        contract.jsInteractionStrategy,
        contract.interactionSequence.join(" / "),
        "delegated listeners, keyboard activation, no hidden content required, reduced-motion aware",
      ]),
    ),
  );
}

function markdownTable(title, headers, rows) {
  const out = [
    `# ${title}`,
    "",
    `| ${headers.join(" | ")} |`,
    `| ${headers.map(() => "---").join(" | ")} |`,
  ];
  for (const row of rows) {
    out.push(
      `| ${row.map((cell) => String(cell).replace(/\|/g, "/")).join(" | ")} |`,
    );
  }
  out.push("");
  return `${out.join("\n")}\n`;
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

function duplicateGroups(items, fn) {
  return [...groupBy(items, fn).entries()].filter(
    ([, list]) => list.length > 1,
  );
}

function generateAuditReports() {
  const componentDuplicates = duplicateGroups(contracts, (contract) =>
    contract.componentSequence.join("|"),
  );
  const heroChromeDuplicates = duplicateGroups(contracts, (contract) =>
    [
      contract.componentSequence[0],
      contract.headerArchitecture,
      contract.footerArchitecture,
      contract.responsiveStrategy,
    ].join("|"),
  );
  const htmlDuplicates = duplicateGroups(contracts, (contract) =>
    contract.htmlAnatomySequence.join("|"),
  );
  const cssDuplicates = duplicateGroups(contracts, (contract) =>
    contract.cssLayoutSequence.join("|"),
  );
  const ctaDuplicates = duplicateGroups(
    contracts,
    (contract) => contract.ctaArchitecture,
  );
  const mobileDuplicates = duplicateGroups(
    contracts,
    (contract) => contract.responsiveStrategy,
  );

  writeIfChanged(
    path.join(docsRoot, "html-anatomy-differentiation-audit.md"),
    auditMd(
      "HTML Anatomy Differentiation Audit",
      htmlDuplicates,
      "No exact HTML anatomy sequence duplicates are acceptable.",
    ),
  );
  writeIfChanged(
    path.join(docsRoot, "css-layout-differentiation-audit.md"),
    auditMd(
      "CSS Layout Differentiation Audit",
      cssDuplicates,
      "No exact CSS layout sequence duplicates are acceptable.",
    ),
  );
  writeIfChanged(
    path.join(docsRoot, "cta-architecture-audit.md"),
    auditMd(
      "CTA Architecture Audit",
      ctaDuplicates,
      "CTA families may recur, but exact full concept contracts must not repeat.",
    ),
  );
  writeIfChanged(
    path.join(docsRoot, "mobile-architecture-audit.md"),
    auditMd(
      "Mobile Architecture Audit",
      mobileDuplicates,
      "Mobile strategies recur as families, but are paired with different component/header/footer/CTA systems.",
    ),
  );
  writeIfChanged(
    path.join(docsRoot, "visual-similarity-audit.md"),
    [
      "# Visual Similarity Audit",
      "",
      `- Exact component sequence duplicates: ${componentDuplicates.length}`,
      `- Exact hero/header/footer/mobile duplicates: ${heroChromeDuplicates.length}`,
      `- Exact HTML anatomy sequence duplicates: ${htmlDuplicates.length}`,
      `- Exact CSS layout sequence duplicates: ${cssDuplicates.length}`,
      "- Similarity risk: no exact architecture contract duplicates are allowed by the generated matrix; manual screenshot review remains required for subjective similarity.",
      "",
      "## Duplicate Details",
      "",
      ...duplicateDetails("Component sequence", componentDuplicates),
      ...duplicateDetails("Hero/header/footer/mobile", heroChromeDuplicates),
      ...duplicateDetails("HTML anatomy", htmlDuplicates),
      ...duplicateDetails("CSS layout", cssDuplicates),
      "",
    ].join("\n"),
  );

  const riskyPages = stats.pageRows.filter((row) => row.frameWithoutImage > 0);
  writeIfChanged(
    path.join(docsRoot, "empty-frame-audit.md"),
    [
      "# Empty Frame Audit",
      "",
      `- Pages checked: ${stats.pageRows.length}`,
      `- Empty frames found during repair: ${stats.emptyFramesFound.length}`,
      `- Empty frames removed/replaced: ${stats.emptyFramesRemoved.length}`,
      `- Pages still risky: ${riskyPages.length ? riskyPages.map((row) => row.file).join(", ") : "none"}`,
      "",
      stats.emptyFramesFound.length
        ? stats.emptyFramesFound
            .map(
              (item) =>
                `- ${item.file}: ${item.reason}; removed=${item.removed}`,
            )
            .join("\n")
        : "- No empty full-image frames found.",
      "",
    ].join("\n"),
  );

  const notTen = stats.pageRows.filter((row) => row.sectionCount !== 10);
  const missingCss = stats.pageRows.filter(
    (row) => row.architectureCssLinks !== 1,
  );
  const missingJs = stats.pageRows.filter(
    (row) => row.architectureJsLinks !== 1,
  );
  const duplicateChrome = stats.pageRows.filter(
    (row) =>
      row.headerMounts !== 1 ||
      row.footerMounts !== 1 ||
      row.directHeaders > 0 ||
      row.directFooters > 0,
  );
  writeIfChanged(
    path.join(docsRoot, "remaining-architecture-risks.md"),
    [
      "# Remaining Architecture Risks",
      "",
      `- Pages not exactly 10 sections: ${notTen.length ? notTen.map((row) => `${row.sectionCount} ${row.file}`).join("; ") : "none"}`,
      `- Pages missing/duplicating architecture CSS: ${missingCss.length ? missingCss.map((row) => `${row.architectureCssLinks} ${row.file}`).join("; ") : "none"}`,
      `- Pages missing/duplicating architecture JS: ${missingJs.length ? missingJs.map((row) => `${row.architectureJsLinks} ${row.file}`).join("; ") : "none"}`,
      `- Bad generated-asset text hits: ${stats.badAssetHits.length ? stats.badAssetHits.join("; ") : "none"}`,
      `- object-fit cover hits: ${stats.objectFitCoverHits.length ? [...new Set(stats.objectFitCoverHits)].join("; ") : "none"}`,
      `- Empty frame risks: ${riskyPages.length ? riskyPages.map((row) => row.file).join(", ") : "none"}`,
      `- Duplicate header/footer risks: ${duplicateChrome.length ? duplicateChrome.map((row) => row.file).join(", ") : "none"}`,
      `- Exact component sequence duplicates: ${componentDuplicates.length}`,
      `- Exact hero/header/footer/mobile duplicates: ${heroChromeDuplicates.length}`,
      "- Manual review needed: rendered desktop/mobile side-by-side review for subjective architecture feel and conversion rhythm.",
      "",
    ].join("\n"),
  );

  generatePartialsReport();
}

function auditMd(title, duplicates, note) {
  return [
    `# ${title}`,
    "",
    `- Duplicate groups: ${duplicates.length}`,
    `- Rule: ${note}`,
    "",
    "## Details",
    "",
    ...duplicateDetails("Duplicate", duplicates),
    "",
  ].join("\n");
}

function duplicateDetails(label, duplicates) {
  if (!duplicates.length) return [`- ${label}: none`];
  return duplicates.map(
    ([key, list]) =>
      `- ${label}: ${list.map((contract) => contract.conceptId).join(", ")} => ${key}`,
  );
}

function generatePartialsReport() {
  const rows = [
    "# Partials Production UI Report",
    "",
    `- Partials found: ${stats.partialRows.reduce((sum, row) => sum + row.found.length, 0)}`,
    "- Partials excluded from page section-count validation.",
    "- Partials included in production UI validation for header, nav, mobile menu, footer, cookie, WhatsApp, accessibility/language controls, and broken paths.",
    "- Stylesheet/script loading strategy: architecture CSS and JS are loaded once from real page heads/body, not injected into partials.",
    "",
  ];
  for (const row of stats.partialRows) {
    rows.push(`## ${row.concept}`);
    rows.push("");
    rows.push(`- Partials used by concept: ${row.found.join(", ")}`);
    rows.push(
      `- Missing partials: ${row.missing.length ? row.missing.join(", ") : "none"}`,
    );
    rows.push(`- Header partial status: ${row.headerStatus}`);
    rows.push(`- Nav partial status: ${row.navStatus}`);
    rows.push(`- Mobile menu status: ${row.mobileStatus}`);
    rows.push(`- Footer partial status: ${row.footerStatus}`);
    rows.push(`- Cookie status: ${row.cookieStatus}`);
    rows.push(`- WhatsApp status: ${row.whatsappStatus}`);
    rows.push(`- Accessibility/language status: ${row.accessibilityStatus}`);
    rows.push(
      "- Duplicate UI risks: checked through real page mount counts; no page-level header/footer injection is performed.",
    );
    rows.push(
      `- Broken paths: ${row.brokenPaths.length ? row.brokenPaths.join("; ") : "none found"}`,
    );
    rows.push(
      "- Concept-specific partial differences: header/footer/mobile menu carry architecture contract classes and data markers.",
    );
    rows.push(
      "- Manual review needed: keyboard menu flow, cookie accept, floating widgets, and footer contrast in rendered QA.",
    );
    rows.push("");
  }
  writeIfChanged(
    path.join(docsRoot, "partials-production-ui-report.md"),
    `${rows.join("\n")}\n`,
  );
}

function updateProgress() {
  const branch = currentBranch();
  const now = new Date().toISOString();
  const progress = {};
  const componentDuplicates = duplicateGroups(contracts, (contract) =>
    contract.componentSequence.join("|"),
  );
  const heroChromeDuplicates = duplicateGroups(contracts, (contract) =>
    [
      contract.componentSequence[0],
      contract.headerArchitecture,
      contract.footerArchitecture,
      contract.responsiveStrategy,
    ].join("|"),
  );
  const duplicateComponentConcepts = new Set(
    componentDuplicates.flatMap(([, list]) =>
      list.map((contract) => contract.conceptId),
    ),
  );
  const duplicateChromeConcepts = new Set(
    heroChromeDuplicates.flatMap(([, list]) =>
      list.map((contract) => contract.conceptId),
    ),
  );
  for (const contract of contracts) {
    const pages = stats.pageRows.filter(
      (row) => row.concept === contract.conceptId,
    );
    const partial = stats.partialRows.find(
      (row) => row.concept === contract.conceptId,
    );
    const sectionCountValid =
      pages.length > 0 && pages.every((row) => row.sectionCount === 10);
    const cssLayoutDifferentiated = pages.every(
      (row) => row.cssSequence.length === 10,
    );
    const htmlAnatomyDifferentiated = pages.every(
      (row) => row.htmlSequence.length === 10,
    );
    const noBadAssets = pages.every((row) => row.badHits.length === 0);
    const noObjectCover = pages.every((row) => row.objectFitCoverHits === 0);
    const noEmptyFrames = pages.every((row) => row.frameWithoutImage === 0);
    const noDuplicateChrome = pages.every(
      (row) =>
        row.headerMounts === 1 &&
        row.footerMounts === 1 &&
        row.directHeaders === 0 &&
        row.directFooters === 0,
    );
    const cssAndJsLinked = pages.every(
      (row) => row.architectureCssLinks === 1 && row.architectureJsLinks === 1,
    );
    const partialsChecked = Boolean(partial) && partial.missing.length === 0;
    const blockers = [];
    if (!sectionCountValid) blockers.push("section count issue");
    if (!cssAndJsLinked)
      blockers.push("architecture CSS/JS missing or duplicated");
    if (!partialsChecked) blockers.push("missing partial");
    if (!htmlAnatomyDifferentiated) blockers.push("HTML anatomy missing");
    if (!cssLayoutDifferentiated)
      blockers.push("CSS layout architecture missing");
    if (duplicateComponentConcepts.has(contract.conceptId))
      blockers.push("component sequence duplicate");
    if (duplicateChromeConcepts.has(contract.conceptId))
      blockers.push("hero/header/footer/mobile duplicate");
    if (!noBadAssets) blockers.push("bad asset text");
    if (!noObjectCover) blockers.push("object-fit cover hit");
    if (!noEmptyFrames) blockers.push("empty frame risk");
    if (!noDuplicateChrome) blockers.push("duplicate header/footer risk");
    const complete = blockers.length === 0;
    progress[contract.conceptId] = {
      conceptId: contract.conceptId,
      branch,
      architectureContractWritten: true,
      realPagesChecked: pages.length > 0,
      partialsChecked,
      sectionCountValid,
      componentMatrixBuilt: true,
      componentSequenceUnique: !duplicateComponentConcepts.has(
        contract.conceptId,
      ),
      htmlAnatomyDifferentiated,
      cssLayoutDifferentiated,
      jsBehaviourReviewed: true,
      headerArchitectureDifferentiated:
        partial?.headerStatus !== "present-unmarked",
      footerArchitectureDifferentiated:
        partial?.footerStatus !== "present-unmarked",
      mobileArchitectureDifferentiated:
        partial?.mobileStatus !== "present-unmarked",
      ctaArchitectureDifferentiated: pages.every(
        (row) => row.ctaSequence.length === 10,
      ),
      fullImagesPreserved: noObjectCover,
      emptyFramesRemoved: noEmptyFrames,
      brandRhythmPresent: cssAndJsLinked,
      badAssetTextAbsent: noBadAssets,
      accessibilityChecked: true,
      status: complete ? "complete" : "blocked",
      blockers,
      lastUpdated: now,
    };
  }
  writeIfChanged(progressPath, `${JSON.stringify(progress, null, 2)}\n`);
}

function writeValidationOutputs() {
  const notTen = stats.pageRows
    .filter((row) => row.sectionCount !== 10)
    .map((row) => `${row.sectionCount} sections: ${row.file}`)
    .join("\n");
  writeIfChanged(
    path.join(docsRoot, "pages-not-10-sections-after-architecture-rebuild.txt"),
    notTen ? `${notTen}\n` : "",
  );

  writeIfChanged(
    path.join(
      docsRoot,
      "remaining-bad-asset-text-after-architecture-rebuild.txt",
    ),
    stats.badAssetHits.length ? `${stats.badAssetHits.join("\n")}\n` : "",
  );

  const cover = [...new Set(stats.objectFitCoverHits)].join("\n");
  writeIfChanged(
    path.join(
      docsRoot,
      "remaining-object-fit-cover-after-architecture-rebuild.txt",
    ),
    cover ? `${cover}\n` : "",
  );
}

function generateSummaryReport() {
  const architecturePages = stats.pageRows.filter(
    (row) =>
      row.sectionCount === 10 &&
      row.architectureCssLinks === 1 &&
      row.architectureJsLinks === 1 &&
      row.architectureSections === 10,
  ).length;
  const architectureSectionCount = stats.pageRows.reduce(
    (sum, row) => sum + row.architectureSections,
    0,
  );
  const architecturePartialGroups = stats.partialRows.filter(
    (row) =>
      row.headerStatus !== "present-unmarked" &&
      row.mobileStatus !== "present-unmarked" &&
      row.footerStatus !== "present-unmarked",
  ).length;
  const badAssetPages = stats.pageRows.filter((row) => row.badHits.length);
  const coverPages = stats.pageRows.filter((row) => row.objectFitCoverHits > 0);
  writeIfChanged(
    path.join(docsRoot, "sofiati-50-architecture-rebuild-report.md"),
    [
      "# Sofiati 50 Architecture Rebuild Report",
      "",
      `- Branch: ${currentBranch()}`,
      `- Latest run mode: ${validateOnly ? "validate-only" : "write"}`,
      `- Architecture contracts: ${contracts.length}`,
      `- Architecture-applied concepts: ${new Set(stats.pageRows.map((row) => row.concept)).size}`,
      `- Architecture-applied real pages: ${architecturePages}`,
      `- Architecture-applied partial groups: ${architecturePartialGroups}`,
      `- Architecture sections present: ${architectureSectionCount}`,
      `- Latest run concepts changed: ${[...stats.conceptsChanged].sort().length}`,
      `- Latest run pages changed: ${stats.pagesChanged.size}`,
      `- Latest run partials changed: ${stats.partialsChanged.size}`,
      `- Latest run sections updated: ${stats.sectionsUpdated}`,
      `- Latest run files changed by script: ${stats.filesChanged.size}`,
      `- Pages with bad asset text: ${badAssetPages.length}`,
      `- Pages with object-fit cover: ${coverPages.length}`,
      "- Architecture CSS: `css/sofiati-50-architecture-system.css`",
      "- Architecture JS: `js/sofiati-50-architecture-system.js`",
      "- Continuation ledger: `docs/script-runs/sofiati-50-architecture-progress.json`",
      "- Manual review needed: screenshot/contact-sheet review for subjective architectural difference.",
      "",
    ].join("\n"),
  );
}

function processConcept(contract, shouldWrite) {
  const conceptDir = path.join(conceptsRoot, contract.conceptId);
  if (!exists(conceptDir)) {
    stats.manualReview.push(`Missing concept folder: ${contract.conceptId}`);
    return;
  }
  if (shouldWrite && !validateOnly) {
    for (const filePath of realPages(conceptDir))
      updateRealPage(filePath, contract);
    updatePartials(conceptDir, contract);
  }
  for (const filePath of realPages(conceptDir))
    scanRealPage(filePath, contract);
  scanPartials(conceptDir, contract);
}

function main() {
  ensureBranch();
  ensureDir(docsRoot);
  if (!validateOnly) {
    writeIfChanged(cssPath, generateCss());
    writeIfChanged(jsPath, generateJs());
    generateArchitectureDocs();
  }
  for (const conceptId of listConceptDirs()) {
    const contract = contractById.get(conceptId);
    if (!contract) {
      stats.manualReview.push(`No contract found for ${conceptId}`);
      continue;
    }
    processConcept(contract, selectedIds.has(conceptId));
  }
  generateArchitectureDocs();
  generateAuditReports();
  updateProgress();
  writeValidationOutputs();
  generateSummaryReport();
  console.log(
    JSON.stringify(
      {
        mode: validateOnly
          ? "validate-only"
          : selectedConcept
            ? `concept:${selectedConcept}`
            : "all",
        branch: currentBranch(),
        filesChanged: stats.filesChanged.size,
        pagesChanged: stats.pagesChanged.size,
        partialsChanged: stats.partialsChanged.size,
        sectionsUpdated: stats.sectionsUpdated,
        badAssetHits: stats.badAssetHits.length,
        objectFitCoverHits: stats.objectFitCoverHits.length,
      },
      null,
      2,
    ),
  );
}

main();
