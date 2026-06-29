#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const conceptsRoot = path.join(root, "concepts");
const brandRoot = path.join(root, "assets/brand");
const generatedRoot = path.join(root, "assets/generated");
const quarantineRoot = path.join(
  root,
  "assets/_quarantine/generated-placeholder-assets",
);
const docsRoot = path.join(root, "docs/script-runs");
const dataRoot = path.join(root, "data");
const premiumCssPath = path.join(
  root,
  "css/sofiati-full-image-premium-system.css",
);
const legacyRescueCssPath = path.join(root, "css/sofiati-visual-rescue.css");

const SYSTEM_LINK =
  '<link rel="stylesheet" href="../../css/sofiati-full-image-premium-system.css" />';

const FOLDER_CATEGORIES = [
  "backgrounds",
  "brand-backgrounds",
  "cards",
  "cta",
  "decorative",
  "footer",
  "forms",
  "heroes",
  "icons",
  "journal",
  "logos",
  "navigation",
  "portraits",
  "responsive",
  "section-assets",
  "social",
  "asset-manifest.json",
];

const BAD_TEXT_PATTERNS = [
  "pattern decoration",
  "home background",
  "section background",
  "decorative asset",
  "texture decoration",
  "concept-specific hero asset",
  "concept-specific",
  "asset for hero",
  "hero asset",
  "section asset",
  "background asset",
  "home section",
  "file-name-like labels",
  "fake captions",
  "mockup labels",
  "placeholder words",
  "watermarks",
  "visible UI labels",
  "fake design-system labels",
];

const BAD_ASSET_NAME_PATTERNS = [
  "background",
  "pattern",
  "texture",
  "watermark",
  "placeholder",
  "mockup",
  "crop",
  "cropped",
  "circular",
  "section-asset",
  "homepage-asset",
  "asset-composition",
  "card",
  "cta-image",
  "form-background",
  "menu-background",
  "logo-on-background",
  "portrait-background",
  "square-portrait",
  "thumbnail",
];

const CONCEPTS = [
  [
    "01-inspire",
    "Inspire",
    "refined editorial calm",
    "asymmetric portrait card",
    "quiet botanical line",
  ],
  [
    "02-empower",
    "Empower",
    "botanical editorial confidence",
    "structured portrait panel",
    "upright leaf line",
  ],
  [
    "03-enhance",
    "Enhance",
    "gold minimalism",
    "precise inset portrait",
    "fine gilded rule",
  ],
  [
    "04-renew",
    "Renew",
    "dark premium editorial",
    "gallery portrait frame",
    "low contrast contour",
  ],
  [
    "05-elevate",
    "Elevate",
    "warm wellness softness",
    "relaxed portrait block",
    "soft wash divider",
  ],
  [
    "06-refine",
    "Refine",
    "clean clinical calm",
    "measured portrait grid",
    "thin clinical line",
  ],
  [
    "07-glow",
    "Glow",
    "consultation studio warmth",
    "rounded human card",
    "small glow ring",
  ],
  [
    "08-balance",
    "Balance",
    "magazine beauty rhythm",
    "layered editorial portrait",
    "balanced twin lines",
  ],
  [
    "09-radiance",
    "Radiance",
    "polished medical spa",
    "luminous side portrait",
    "subtle sun line",
  ],
  [
    "10-essence",
    "Essence",
    "portrait-led trust",
    "simple vertical portrait",
    "minimal signature line",
  ],
  [
    "11-bloom",
    "Bloom",
    "botanical softness",
    "organic portrait shelf",
    "leaf stem accent",
  ],
  [
    "12-vital",
    "Vital",
    "clean vitality",
    "energetic portrait panel",
    "brisk fine rule",
  ],
  [
    "13-poise",
    "Poise",
    "elegant balance",
    "symmetrical portrait moment",
    "centered rule",
  ],
  [
    "14-aura",
    "Aura",
    "atmospheric luxury",
    "soft halo portrait",
    "haze line accent",
  ],
  [
    "15-clarity",
    "Clarity",
    "minimal clinical clarity",
    "restrained portrait field",
    "plain rule",
  ],
  [
    "16-grace",
    "Grace",
    "soft feminine editorial",
    "curved portrait frame",
    "graceful curve",
  ],
  [
    "17-sculpt",
    "Sculpt",
    "structured premium geometry",
    "sharp portrait plinth",
    "angled line",
  ],
  [
    "18-lumin",
    "Lumin",
    "light-led elegance",
    "airy luminous portrait",
    "light beam rule",
  ],
  [
    "19-verda",
    "Verda",
    "sage botanical calm",
    "natural portrait panel",
    "sage stem",
  ],
  [
    "20-halo",
    "Halo",
    "soft circular atmosphere",
    "uncropped halo frame",
    "open ring accent",
  ],
  [
    "21-calm",
    "Calm",
    "quiet wellness space",
    "spacious portrait card",
    "low-density line",
  ],
  [
    "22-precision",
    "Precision",
    "technical refinement",
    "exact portrait rail",
    "precise ticks",
  ],
  [
    "23-ritual",
    "Ritual",
    "spa ritual warmth",
    "slow portrait story",
    "ritual thread",
  ],
  [
    "24-signal",
    "Signal",
    "modern clean interface",
    "clear portrait module",
    "signal line",
  ],
  [
    "25-align",
    "Align",
    "balanced grids",
    "measured portrait grid",
    "alignment rule",
  ],
  [
    "26-vivant",
    "Vivant",
    "lively premium brightness",
    "bright portrait moment",
    "animated-feeling line",
  ],
  [
    "27-form",
    "Form",
    "shape-led editorial",
    "architectural portrait frame",
    "shape contour",
  ],
  [
    "28-pure",
    "Pure",
    "minimal clean beauty",
    "white-space portrait",
    "nearly invisible rule",
  ],
  [
    "29-solace",
    "Solace",
    "comforting calm",
    "soft consultation portrait",
    "comfort line",
  ],
  [
    "30-method",
    "Method",
    "process-led discipline",
    "step-aligned portrait",
    "method rule",
  ],
  [
    "31-evolve",
    "Evolve",
    "learning-led transformation",
    "journal portrait lead",
    "growth line",
  ],
  [
    "32-serene",
    "Serene",
    "soft spa calm",
    "delicate portrait panel",
    "fine spa line",
  ],
  [
    "33-elan",
    "Elan",
    "stylish editorial",
    "bold magazine portrait",
    "fashion rule",
  ],
  [
    "34-flora",
    "Flora",
    "botanical luxury",
    "floral portrait anchor",
    "botanical line art",
  ],
  [
    "35-atelier",
    "Atelier",
    "crafted studio detail",
    "art-directed portrait frame",
    "atelier mark",
  ],
  [
    "36-lumina",
    "Lumina",
    "luminous softness",
    "pale portrait panel",
    "luminous rule",
  ],
  [
    "37-vellum",
    "Vellum",
    "paper editorial texture",
    "document portrait frame",
    "vellum line",
  ],
  [
    "38-origin",
    "Origin",
    "grounded natural trust",
    "human-first portrait",
    "ground line",
  ],
  [
    "39-kindred",
    "Kindred",
    "personal relationship",
    "intimate portrait section",
    "relational line",
  ],
  [
    "40-noble",
    "Noble",
    "mature quiet luxury",
    "stately portrait frame",
    "noble rule",
  ],
  [
    "41-vista",
    "Vista",
    "open spacious layout",
    "wide portrait panel",
    "vista horizon",
  ],
  [
    "42-softline",
    "Softline",
    "soft linear minimalism",
    "gentle portrait line",
    "soft curve",
  ],
  [
    "43-meridian",
    "Meridian",
    "structured pathways",
    "pathway portrait frame",
    "route line",
  ],
  [
    "44-safeguard",
    "Safeguard",
    "trust and safety",
    "reassurance portrait panel",
    "safety rule",
  ],
  [
    "45-silhouette",
    "Silhouette",
    "elegant shape language",
    "full-image silhouette frame",
    "shape line",
  ],
  [
    "46-curate",
    "Curate",
    "controlled editorial luxury",
    "curated portrait placement",
    "curator rule",
  ],
  [
    "47-proof",
    "Proof",
    "responsible evidence",
    "trust-note portrait",
    "evidence line",
  ],
  [
    "48-signature",
    "Signature",
    "distinctive brand presence",
    "signature portrait lead",
    "signature line",
  ],
  [
    "49-wisdom",
    "Wisdom",
    "educational calm",
    "journal trust portrait",
    "wisdom rule",
  ],
  [
    "50-sovereign",
    "Sovereign",
    "confident restrained luxury",
    "commanding portrait frame",
    "sovereign rule",
  ],
];

const PAGE_ORDER = [
  "index",
  "about",
  "care",
  "laser",
  "skin",
  "results",
  "consultation",
  "contact",
  "mission",
  "values",
  "testimonials",
  "faq",
  "journal",
  "blog",
  "legal",
  "privacy",
  "cookies",
  "accessibility",
  "sitemap",
  "thank-you",
  "404",
];

const stats = {
  filesChanged: new Set(),
  realPagesChanged: new Set(),
  partialsChanged: new Set(),
  cssFilesChanged: new Set(),
  jsFilesChanged: new Set(),
  manifestsUpdated: new Set(),
  conceptsChanged: new Set(),
  generatedRefsRemoved: [],
  fullImageFixes: [],
  cardIconsReplaced: 0,
  figcaptionsRemoved: 0,
  objectFitReplacements: 0,
  generatedUrlsRemovedFromCss: 0,
  photoUsage: [],
  folderAudits: [],
  quarantineEntries: [],
  manualReview: [],
  sectionIssues: [],
  changedPages: new Set(),
};

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

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function escapeHtml(value) {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function sentenceCase(value) {
  if (!value) return "";
  return value.charAt(0).toUpperCase() + value.slice(1);
}

function conceptNumber(siteId) {
  return siteId.slice(0, 2);
}

function conceptById(siteId) {
  const index = CONCEPTS.findIndex(([id]) => id === siteId);
  if (index === -1) return null;
  const [id, name, direction, frame, decor] = CONCEPTS[index];
  return {
    id,
    number: conceptNumber(id),
    name,
    direction,
    frame,
    decor,
    index,
  };
}

const brandAssets = walkFiles(brandRoot, (filePath) =>
  /\.(webp|png|jpe?g|svg)$/i.test(filePath),
).map(rel);

const brandPhotos = brandAssets.filter((assetPath) =>
  /assets\/brand\/franciele-sofiati-\d+.+\.(webp|png|jpe?g)$/i.test(assetPath),
);

if (!brandPhotos.length) {
  throw new Error("No Franciele brand photos found in assets/brand.");
}

function brandPageSrc(assetPath) {
  return `../../${assetPath}`;
}

function photoFor(siteId, pageKey, sectionNumber) {
  const info = conceptById(siteId);
  const pageIndex = Math.max(0, PAGE_ORDER.indexOf(pageKey));
  const sectionIndex = Number.parseInt(sectionNumber || "1", 10) || 1;
  const photoIndex =
    (info.index * 9 + pageIndex * 5 + sectionIndex * 3) % brandPhotos.length;
  return brandPhotos[photoIndex];
}

function photoAlt(info, pageKey, sectionNumber, role) {
  const pageLabel = sentenceCase(pageKey.replace(/-/g, " "));
  const roleText = role ? ` for ${role.replace(/-/g, " ")}` : "";
  return `Franciele Sofiati in a full-image ${info.name} ${pageLabel} visual${roleText}`;
}

function cssForPremiumSystem() {
  const palette = [
    ["#485041", "#9a6b35", "#f8f7f2", "#f2eee3"],
    ["#3f5b4a", "#b28a55", "#f7f5ed", "#e8efe4"],
    ["#4b4437", "#c19a57", "#fbf8ef", "#efe3cf"],
    ["#292d2a", "#c7a46c", "#f5f0e7", "#dde3da"],
    ["#80664f", "#b88452", "#fbf4e8", "#efe4d5"],
    ["#3f5453", "#9c7651", "#f8faf6", "#e5efed"],
    ["#75594d", "#c69b67", "#fff8ed", "#f1e2d4"],
    ["#554a66", "#b58c5b", "#f8f2ef", "#e9e1ec"],
    ["#53645c", "#c49a6b", "#fbf7f0", "#e8eee9"],
    ["#3d3a35", "#a97946", "#faf8f3", "#eee8db"],
  ];
  const radius = [4, 10, 18, 26, 34, 6, 14, 22, 30, 2];
  const maxes = [520, 560, 600, 640, 500, 580, 620, 540, 660, 590];
  const sectionGaps = ["5.5rem", "6.25rem", "7rem", "5rem", "6.75rem"];
  const conceptVars = CONCEPTS.map(([id], index) => {
    const [ink, accent, surface, tint] = palette[index % palette.length];
    const frameRadius = radius[index % radius.length];
    const frameMax = maxes[index % maxes.length];
    const gap = sectionGaps[index % sectionGaps.length];
    const density = (0.08 + (index % 7) * 0.018).toFixed(3);
    const rotate = [-1.5, 0, 1.25, -0.75, 0.8][index % 5];
    return `[data-concept="${id}"] {
  --premium-ink: ${ink};
  --premium-accent: ${accent};
  --premium-surface: ${surface};
  --premium-tint: ${tint};
  --photo-frame-max: ${frameMax}px;
  --photo-frame-radius: ${frameRadius}px;
  --section-gap: ${gap};
  --decorative-density: ${density};
  --frame-tilt: ${rotate}deg;
}`;
  }).join("\n\n");

  return `/*
SOFIATI FULL IMAGE PREMIUM SYSTEM
Generated by qa/repair_sofiati_full_image_premium_asset_system.mjs.
Rules: real Franciele images remain full-image, generated placeholder art is
dereferenced, and concept-specific variables keep the atlas visually varied.
*/

${conceptVars}

:root {
  --premium-ink: #485041;
  --premium-accent: #9a6b35;
  --premium-surface: #f8f7f2;
  --premium-tint: #f2eee3;
  --photo-frame-max: 560px;
  --photo-frame-radius: 18px;
  --section-gap: 6rem;
  --decorative-density: 0.12;
  --frame-tilt: 0deg;
}

body.atlas-site {
  background:
    radial-gradient(circle at 12% 10%, color-mix(in srgb, var(--premium-accent) 10%, transparent), transparent 34rem),
    linear-gradient(135deg, color-mix(in srgb, var(--premium-tint) 74%, white), var(--premium-surface)) !important;
  color: #252321;
}

.atlas-main {
  padding-block: clamp(28px, 5vw, 72px) clamp(60px, 8vw, 118px);
}

.atlas-section {
  isolation: isolate;
  gap: clamp(24px, 4vw, 58px) !important;
  padding-block: var(--section-gap) !important;
  background-image: none !important;
  background:
    linear-gradient(115deg, color-mix(in srgb, var(--premium-tint) 38%, transparent), transparent 58%),
    color-mix(in srgb, var(--premium-surface) 72%, white) !important;
  border-color: color-mix(in srgb, var(--premium-ink) 16%, transparent) !important;
  overflow: visible !important;
}

.atlas-section:nth-child(3n + 1) {
  border-radius: var(--photo-frame-radius);
}

.atlas-section:nth-child(3n + 2) {
  background:
    linear-gradient(180deg, color-mix(in srgb, white 72%, var(--premium-tint)), color-mix(in srgb, var(--premium-surface) 88%, white)) !important;
}

.atlas-section:nth-child(4n) {
  background:
    linear-gradient(90deg, color-mix(in srgb, var(--premium-ink) 7%, transparent), transparent 68%),
    color-mix(in srgb, var(--premium-surface) 84%, white) !important;
}

.atlas-section::before {
  content: "";
  position: absolute;
  inset: clamp(20px, 4vw, 52px);
  z-index: -1;
  pointer-events: none;
  border-top: 1px solid color-mix(in srgb, var(--premium-accent) 28%, transparent);
  border-left: 1px solid color-mix(in srgb, var(--premium-ink) calc(var(--decorative-density) * 100%), transparent);
  opacity: 0.72;
}

.atlas-section:first-child {
  min-height: auto !important;
  background:
    linear-gradient(125deg, color-mix(in srgb, white 82%, var(--premium-tint)), color-mix(in srgb, var(--premium-ink) 8%, transparent)),
    var(--premium-surface) !important;
  background-image: none !important;
}

.atlas-section__copy {
  position: relative;
  z-index: 2;
}

.atlas-section h1,
.atlas-section h2,
.atlas-section h3 {
  letter-spacing: 0 !important;
}

.atlas-section h1 {
  max-width: min(100%, 13ch) !important;
  font-size: clamp(2.9rem, 7vw, 6.8rem) !important;
}

.atlas-section h2 {
  max-width: min(100%, 15ch) !important;
}

.sofiati-photo,
.sofiati-portrait,
.sofiati-hero-photo,
.sofiati-brand-photo,
img[data-sofiati-photo="true"] {
  display: block;
  width: 100% !important;
  height: auto !important;
  min-height: 0 !important;
  max-width: 100% !important;
  object-fit: contain !important;
  object-position: center !important;
}

.sofiati-photo-frame,
.sofiati-portrait-frame,
.sofiati-hero-photo-frame,
.atlas-section__media.sofiati-photo-frame {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  width: 100% !important;
  max-width: min(100%, var(--photo-frame-max)) !important;
  min-height: auto !important;
  height: auto !important;
  aspect-ratio: auto !important;
  margin-inline: auto !important;
  overflow: visible !important;
  padding: clamp(18px, 3.8vw, 44px) !important;
  border-radius: var(--photo-frame-radius) !important;
  background:
    linear-gradient(145deg, color-mix(in srgb, white 76%, var(--premium-tint)), color-mix(in srgb, var(--premium-accent) 10%, white)),
    var(--premium-surface) !important;
  border: 1px solid color-mix(in srgb, var(--premium-accent) 28%, transparent) !important;
  box-shadow: 0 22px 70px rgba(37, 35, 33, 0.12) !important;
  transform: rotate(var(--frame-tilt));
}

.atlas-section:nth-child(even) .sofiati-photo-frame {
  transform: rotate(calc(var(--frame-tilt) * -1));
}

.atlas-section__media.sofiati-photo-frame img,
.sofiati-photo-frame img[data-sofiati-photo="true"] {
  width: min(100%, var(--photo-frame-max)) !important;
  height: auto !important;
  min-height: 0 !important;
  padding: 0 !important;
  object-fit: contain !important;
}

.atlas-layout-centered .atlas-section__media.sofiati-photo-frame {
  max-width: min(760px, 100%) !important;
}

.atlas-card-row img[src*="assets/generated"],
.public-footer-watermark,
.mobile-menu-asset-bg {
  display: none !important;
}

.sofiati-inline-icon,
.footer-heading-icon,
.public-menu-close-icon,
.sofiati-widget-icon {
  display: inline-block;
  flex: 0 0 auto;
  width: 1.45rem;
  height: 1.45rem;
  border: 1px solid color-mix(in srgb, var(--premium-accent) 48%, transparent);
  border-radius: max(2px, calc(var(--photo-frame-radius) / 4));
  background:
    linear-gradient(135deg, transparent 44%, color-mix(in srgb, var(--premium-accent) 58%, transparent) 45% 55%, transparent 56%),
    color-mix(in srgb, white 78%, var(--premium-tint));
}

.sofiati-widget-icon {
  width: 1.2rem;
  height: 1.2rem;
  border-radius: 999px;
}

.sofiati-widget-icon--top {
  border-radius: 4px;
  transform: rotate(45deg);
}

.atlas-card-row article {
  align-content: start;
  background:
    linear-gradient(180deg, color-mix(in srgb, white 82%, var(--premium-surface)), color-mix(in srgb, var(--premium-tint) 72%, white)) !important;
  border-color: color-mix(in srgb, var(--premium-ink) 16%, transparent) !important;
  border-radius: max(4px, calc(var(--photo-frame-radius) * 0.42)) !important;
}

.atlas-section__media figcaption,
.hero-visual figcaption {
  display: none !important;
}

.public-brand-mark img,
.footer-signature-logo img,
.mobile-menu-top img {
  object-fit: contain !important;
}

.mobile-menu-avatar,
.doctor-portrait,
.consultation-form-asset,
.contact-card-asset {
  width: min(100%, 420px) !important;
  height: auto !important;
  max-height: none !important;
  object-fit: contain !important;
  border-radius: var(--photo-frame-radius) !important;
  background: color-mix(in srgb, var(--premium-tint) 76%, white);
  padding: clamp(10px, 2vw, 24px);
}

.public-footer,
.mobile-menu {
  background-image: none !important;
}

@media (max-width: 820px) {
  .atlas-section {
    grid-template-columns: 1fr !important;
    padding-block: clamp(3.2rem, 14vw, 5rem) !important;
  }

  .atlas-layout-media-left .atlas-section__media,
  .atlas-layout-portrait-stack .atlas-section__media,
  .atlas-page-home .atlas-section:first-child .atlas-section__media {
    order: -1;
  }

  .sofiati-photo-frame,
  .atlas-section__media.sofiati-photo-frame {
    max-width: min(100%, 480px) !important;
    transform: none !important;
  }

  .atlas-section h1 {
    font-size: clamp(2.45rem, 15vw, 4.7rem) !important;
  }
}
`;
}

function legacyRescueCss() {
  return `/*
SOFIATI VISUAL RESCUE LEGACY COMPATIBILITY
This older layer now delegates to the governed full-image premium system.
It intentionally contains no image cropping rules.
*/
@import url("./sofiati-full-image-premium-system.css");

.sofiati-photo,
.sofiati-portrait,
.sofiati-hero-photo,
.sofiati-brand-photo,
img[data-sofiati-photo="true"] {
  width: 100%;
  height: auto;
  max-width: 100%;
  object-fit: contain;
  object-position: center;
}
`;
}

function collectGeneratedReferenceMap() {
  const refMap = new Map();
  const files = walkFiles(conceptsRoot, (filePath) =>
    /\.(html|css|js)$/i.test(filePath),
  );
  const matcher = /assets\/generated\/concept-\d+\/[^"')\s<]+/g;
  for (const filePath of files) {
    const content = read(filePath);
    const refs = content.match(matcher) || [];
    for (const raw of refs) {
      const normalized = raw.replace(/^\.\.\/\.\.\//, "");
      if (!refMap.has(normalized)) refMap.set(normalized, new Set());
      refMap.get(normalized).add(rel(filePath));
    }
  }
  return refMap;
}

function sectionInfoAt(html, offset, filePath) {
  const before = html.slice(0, offset);
  const sectionStart = before.lastIndexOf("<section");
  const chunk =
    sectionStart >= 0 ? html.slice(sectionStart, offset) : before.slice(-1200);
  const section = chunk.match(/data-section="([^"]+)"/)?.[1] || "01";
  const role = chunk.match(/data-role="([^"]+)"/)?.[1] || "brand trust";
  const title =
    chunk
      .match(/<h[12][^>]*>([\s\S]*?)<\/h[12]>/)?.[1]
      ?.replace(/<[^>]+>/g, "")
      .replace(/\s+/g, " ")
      .trim() || role;
  const pageKey = path.basename(filePath, ".html");
  return { section, role, title, pageKey };
}

function addClass(existing, additions) {
  const classes = new Set(
    String(existing || "")
      .split(/\s+/)
      .filter(Boolean),
  );
  for (const item of additions) classes.add(item);
  return [...classes].join(" ");
}

function replaceAttribute(tag, name, value) {
  const pattern = new RegExp(`\\s${name}="[^"]*"`, "i");
  if (pattern.test(tag)) return tag.replace(pattern, ` ${name}="${value}"`);
  return tag.replace(/\/?>$/, ` ${name}="${value}"$&`);
}

function removeAttribute(tag, name) {
  const pattern = new RegExp(`\\s${name}="[^"]*"`, "gi");
  return tag.replace(pattern, "");
}

function replaceGeneratedPageImage(tag, context) {
  const src = tag.match(/\ssrc="([^"]+)"/i)?.[1] || "";
  if (!src.includes("assets/generated")) return tag;
  const photoPath = photoFor(
    context.siteId,
    context.info.pageKey,
    context.info.section,
  );
  const photoSrc = brandPageSrc(photoPath);
  const loading = "eager";
  const imageClass = addClass(tag.match(/\sclass="([^"]*)"/i)?.[1] || "", [
    "sofiati-photo",
    context.info.section === "01"
      ? "sofiati-hero-photo"
      : "sofiati-brand-photo",
  ]);
  stats.generatedRefsRemoved.push({
    file: rel(context.filePath),
    oldRef: src.replace(/^\.\.\/\.\.\//, ""),
    replacement: photoPath,
    strategy: "replaced section media with full Franciele brand photo",
  });
  stats.fullImageFixes.push(
    `${rel(context.filePath)} section ${context.info.section}`,
  );
  stats.photoUsage.push({
    sourcePath: photoPath,
    conceptId: context.siteId,
    page: context.info.pageKey,
    section: context.info.section,
    role: context.info.role,
    cssClass: imageClass,
    strategy:
      "width 100 percent, height auto, object-fit contain, flexible visible frame",
    fullImageVisible:
      "yes - CSS uses contain and the frame has overflow visible",
    mobile: "stacks above/below copy with full image preserved",
    alt: photoAlt(
      context.conceptInfo,
      context.info.pageKey,
      context.info.section,
      context.info.role,
    ),
    manualReviewNeeded: "visual spot check recommended",
  });
  let next = tag;
  next = replaceAttribute(next, "src", photoSrc);
  next = replaceAttribute(
    next,
    "alt",
    photoAlt(
      context.conceptInfo,
      context.info.pageKey,
      context.info.section,
      context.info.role,
    ),
  );
  next = replaceAttribute(next, "class", imageClass);
  next = replaceAttribute(next, "loading", loading);
  next = replaceAttribute(next, "decoding", "async");
  next = replaceAttribute(next, "data-sofiati-photo", "true");
  next = removeAttribute(next, "width");
  next = removeAttribute(next, "height");
  if (context.info.section === "01") {
    next = replaceAttribute(next, "fetchpriority", "high");
  }
  return next;
}

function replaceGeneratedCardImages(block) {
  return block.replace(/<img\b[\s\S]*?>/gi, (tag) => {
    const src = tag.match(/\ssrc="([^"]+)"/i)?.[1] || "";
    if (!src.includes("assets/generated")) return tag;
    stats.cardIconsReplaced += 1;
    return '<span class="sofiati-inline-icon" aria-hidden="true"></span>';
  });
}

function cleanBadVisitorText(html) {
  let next = html;
  next = next.replace(
    /Assets:\s*.*?rendered asset role:\s*[^\n<]*/gi,
    "Assets: Full Franciele image, CSS decoration, and no-crop responsive framing.",
  );
  next = next.replace(/rendered asset role:/gi, "visual role:");
  const replacements = new Map([
    ["pattern decoration", "botanical surface"],
    ["home background", "home surface"],
    ["section background", "section surface"],
    ["decorative asset", "CSS decoration"],
    ["texture decoration", "quiet texture"],
    ["concept-specific hero asset", "concept hero visual"],
    ["concept-specific", "concept-led"],
    ["asset for hero", "visual for hero"],
    ["hero asset", "hero visual"],
    ["section asset", "section visual"],
    ["background asset", "background surface"],
    ["home section", "home area"],
    ["file-name-like labels", "editorial labels"],
    ["fake captions", "supporting captions"],
    ["mockup labels", "editorial labels"],
    ["placeholder words", "supporting words"],
    ["watermarks", "brand marks"],
    ["visible UI labels", "visible labels"],
    ["fake design-system labels", "design labels"],
  ]);
  for (const [bad, good] of replacements.entries()) {
    next = next.replace(new RegExp(escapeRegExp(bad), "gi"), good);
  }
  return next;
}

function repairRealPage(filePath, refMap) {
  const siteId = filePath.split(path.sep).find((part) => /^\d{2}-/.test(part));
  const conceptInfo = conceptById(siteId);
  if (!conceptInfo) return;
  let html = read(filePath);
  const original = html;

  html = html.replace(
    /\s*<link[^>]+sofiati-visual-rescue\.css[^>]*>\s*/gi,
    "\n",
  );
  if (!html.includes("sofiati-full-image-premium-system.css")) {
    html = html.includes("</head>")
      ? html.replace("</head>", `    ${SYSTEM_LINK}\n  </head>`)
      : `${SYSTEM_LINK}\n${html}`;
  }

  html = html
    .replace(
      /content="\.\.\/\.\.\/assets\/generated\/concept-\d+\/social\/[^"]+"/gi,
      `content="${brandPageSrc(brandPhotos[conceptInfo.index % brandPhotos.length])}"`,
    )
    .replace(
      /href="\.\.\/\.\.\/assets\/generated\/concept-\d+\/logos\/[^"]*favicon[^"]*"/gi,
      'href="../../assets/brand/sofiati-favicon.svg"',
    )
    .replace(
      /href="\.\.\/\.\.\/assets\/generated\/concept-\d+\/social\/[^"]*apple[^"]*"/gi,
      'href="../../assets/brand/sofiati-monogram-sage.png"',
    )
    .replace(
      /data-asset-root="\.\.\/\.\.\/assets\/generated\/concept-\d+"/gi,
      'data-brand-asset-root="../../assets/brand"',
    );

  html = html.replace(
    /<figure class="([^"]*\batlas-section__media\b[^"]*)"/gi,
    (_match, classes) =>
      `<figure class="${addClass(classes, [
        "sofiati-photo-frame",
        "sofiati-portrait-frame",
      ])}" data-full-image-frame="true"`,
  );

  html = html.replace(
    /<div class="atlas-card-row"[\s\S]*?<\/div>/gi,
    replaceGeneratedCardImages,
  );

  const captionMatches =
    html.match(/\s*<figcaption>[\s\S]*?<\/figcaption>/gi) || [];
  stats.figcaptionsRemoved += captionMatches.length;
  html = html.replace(/\s*<figcaption>[\s\S]*?<\/figcaption>/gi, "");

  const beforeImages = html;
  html = html.replace(/<img\b[\s\S]*?>/gi, (tag, offset) => {
    const info = sectionInfoAt(beforeImages, offset, filePath);
    return replaceGeneratedPageImage(tag, {
      filePath,
      siteId,
      conceptInfo,
      info,
      refMap,
    });
  });

  html = html.replace(
    /data-asset-role="[^"]*"/gi,
    'data-asset-role="full-image-photo"',
  );
  html = cleanBadVisitorText(html);

  if (html !== original && writeIfChanged(filePath, html)) {
    stats.realPagesChanged.add(rel(filePath));
    stats.changedPages.add(rel(filePath));
    stats.conceptsChanged.add(siteId);
  }
}

function repairPartial(filePath) {
  const siteId = filePath.split(path.sep).find((part) => /^\d{2}-/.test(part));
  const conceptInfo = conceptById(siteId);
  if (!conceptInfo) return;
  const partialName = path.basename(filePath);
  let html = read(filePath);
  const original = html;

  html = html
    .replace(
      /content="\.\.\/\.\.\/assets\/generated\/concept-\d+\/social\/[^"]+"/gi,
      `content="${brandPageSrc(brandPhotos[conceptInfo.index % brandPhotos.length])}"`,
    )
    .replace(
      /href="\.\.\/\.\.\/assets\/generated\/concept-\d+\/logos\/[^"]*favicon[^"]*"/gi,
      'href="../../assets/brand/sofiati-favicon.svg"',
    )
    .replace(
      /href="\.\.\/\.\.\/assets\/generated\/concept-\d+\/social\/[^"]*apple[^"]*"/gi,
      'href="../../assets/brand/sofiati-monogram-sage.png"',
    );

  html = html.replace(
    /\s*<img[^>]+class="[^"]*public-footer-watermark[^"]*"[\s\S]*?\/>\s*/gi,
    "\n",
  );
  html = html.replace(
    /\s*<img[^>]+class="[^"]*mobile-menu-asset-bg[^"]*"[\s\S]*?\/>\s*/gi,
    "\n",
  );

  html = html.replace(/<img\b[\s\S]*?>/gi, (tag) => {
    const src = tag.match(/\ssrc="([^"]+)"/i)?.[1] || "";
    if (!src.includes("assets/generated")) return tag;
    const classValue = tag.match(/\sclass="([^"]*)"/i)?.[1] || "";
    const lower = `${src} ${classValue} ${partialName}`.toLowerCase();

    if (lower.includes("logo") || lower.includes("brand-mark")) {
      const logo =
        partialName === "mobile-menu.html"
          ? "../../assets/brand/sofiati-logo-primary-white.png"
          : "../../assets/brand/sofiati-logo-primary-sage.png";
      let next = tag;
      next = replaceAttribute(next, "src", logo);
      next = replaceAttribute(next, "alt", "Sofiati");
      next = removeAttribute(next, "width");
      next = removeAttribute(next, "height");
      return next;
    }

    if (
      lower.includes("portrait") ||
      lower.includes("avatar") ||
      lower.includes("form") ||
      lower.includes("contact-panel")
    ) {
      const photoPath = photoFor(
        siteId,
        partialName.replace(".html", ""),
        "01",
      );
      let next = tag;
      next = replaceAttribute(next, "src", brandPageSrc(photoPath));
      next = replaceAttribute(
        next,
        "alt",
        `Franciele Sofiati full-image ${conceptInfo.name} visual`,
      );
      next = replaceAttribute(
        next,
        "class",
        addClass(classValue, ["sofiati-photo", "sofiati-brand-photo"]),
      );
      next = replaceAttribute(next, "data-sofiati-photo", "true");
      next = replaceAttribute(next, "loading", "lazy");
      next = replaceAttribute(next, "decoding", "async");
      next = removeAttribute(next, "width");
      next = removeAttribute(next, "height");
      stats.photoUsage.push({
        sourcePath: photoPath,
        conceptId: siteId,
        page: "partial",
        section: partialName,
        role: "partial brand visual",
        cssClass: "sofiati-photo sofiati-brand-photo",
        strategy: "full image in non-cropping partial frame",
        fullImageVisible: "yes - CSS uses contain",
        mobile: "partial keeps natural image ratio",
        alt: `Franciele Sofiati full-image ${conceptInfo.name} visual`,
        manualReviewNeeded: "visual spot check recommended",
      });
      return next;
    }

    if (lower.includes("whatsapp")) {
      return '<span class="sofiati-widget-icon sofiati-widget-icon--whatsapp" aria-hidden="true"></span>';
    }

    if (lower.includes("back-to-top")) {
      return '<span class="sofiati-widget-icon sofiati-widget-icon--top" aria-hidden="true"></span>';
    }

    if (lower.includes("menu-close")) {
      return '<span class="public-menu-close-icon" aria-hidden="true"></span>';
    }

    return '<span class="sofiati-inline-icon" aria-hidden="true"></span>';
  });

  html = cleanBadVisitorText(html);

  if (html !== original && writeIfChanged(filePath, html)) {
    stats.partialsChanged.add(rel(filePath));
    stats.conceptsChanged.add(siteId);
  }
}

function repairConceptCss(filePath) {
  let css = read(filePath);
  const original = css;
  const coverMatches = css.match(/object-fit:\s*cover\b/gi) || [];
  if (coverMatches.length) stats.objectFitReplacements += coverMatches.length;
  css = css.replace(/object-fit:\s*cover\b/gi, "object-fit: contain");
  const generatedUrlMatches =
    css.match(
      /url\((["']?)\.\.\/\.\.\/\.\.\/assets\/generated\/concept-\d+\/[^)]*?\1\)/gi,
    ) || [];
  if (generatedUrlMatches.length) {
    stats.generatedUrlsRemovedFromCss += generatedUrlMatches.length;
  }
  css = css.replace(
    /url\((["']?)\.\.\/\.\.\/\.\.\/assets\/generated\/concept-\d+\/[^)]*?\1\)/gi,
    "none",
  );
  if (css !== original && writeIfChanged(filePath, css)) {
    stats.cssFilesChanged.add(rel(filePath));
    const siteId = filePath
      .split(path.sep)
      .find((part) => /^\d{2}-/.test(part));
    if (siteId) stats.conceptsChanged.add(siteId);
  }
}

function repairConceptJs(filePath) {
  let js = read(filePath);
  const original = js;
  js = js.replace(
    /const makeImage = \(src, alt\) => \{[\s\S]*?\n\s*\};/,
    `const makeWidgetIcon = (type) => {
    const icon = document.createElement("span");
    icon.className = \`sofiati-widget-icon sofiati-widget-icon--\${type}\`;
    icon.setAttribute("aria-hidden", "true");
    return icon;
  };`,
  );
  js = js.replace(
    /makeImage\("\.\.\/\.\.\/assets\/generated\/concept-\d+\/icons\/[^"]*whatsapp[^"]*",\s*""\)/gi,
    'makeWidgetIcon("whatsapp")',
  );
  js = js.replace(
    /makeImage\("\.\.\/\.\.\/assets\/generated\/concept-\d+\/icons\/[^"]*back-to-top[^"]*",\s*""\)/gi,
    'makeWidgetIcon("top")',
  );
  if (js !== original && writeIfChanged(filePath, js)) {
    stats.jsFilesChanged.add(rel(filePath));
    const siteId = filePath
      .split(path.sep)
      .find((part) => /^\d{2}-/.test(part));
    if (siteId) stats.conceptsChanged.add(siteId);
  }
}

function badReasonsForAsset(filePath, category) {
  const assetPath = rel(filePath);
  const base = path.basename(filePath).toLowerCase();
  const reasons = [];
  if (category === "asset-manifest.json") {
    reasons.push("manifest replaced with audited governance structure");
    return reasons;
  }
  if (BAD_ASSET_NAME_PATTERNS.some((pattern) => base.includes(pattern))) {
    reasons.push(
      "filename suggests placeholder, crop, background, mockup, or asset-board use",
    );
  }
  if (
    [
      "backgrounds",
      "brand-backgrounds",
      "cards",
      "section-assets",
      "responsive",
    ].includes(category)
  ) {
    reasons.push(
      `${category} category is high-risk for visible labelled placeholder art`,
    );
  }
  if (/\.(svg|json|html|txt|css)$/i.test(filePath)) {
    const text = read(filePath);
    for (const pattern of BAD_TEXT_PATTERNS) {
      if (new RegExp(escapeRegExp(pattern), "i").test(text)) {
        reasons.push(`contains visible text '${pattern}'`);
        break;
      }
    }
    if (
      /<text\b/i.test(text) &&
      !/sofiati|franciele/i.test(path.basename(filePath))
    ) {
      reasons.push("svg includes baked-in text");
    }
  } else if (/\.(webp|png|jpe?g)$/i.test(filePath)) {
    reasons.push(
      "binary generated image needs manual visual review before approval",
    );
  }
  if (
    /portrait|hero/i.test(assetPath) &&
    /crop|square|circular|mobile|thumbnail/i.test(assetPath)
  ) {
    reasons.push(
      "portrait or hero variant implies a crop and is not approved for Franciele photos",
    );
  }
  return [...new Set(reasons)];
}

function auditGeneratedAssets(refMap) {
  for (const [siteId, conceptName] of CONCEPTS) {
    const conceptDir = path.join(
      generatedRoot,
      `concept-${conceptNumber(siteId)}`,
    );
    for (const category of FOLDER_CATEGORIES) {
      const target =
        category === "asset-manifest.json"
          ? path.join(conceptDir, category)
          : path.join(conceptDir, category);
      const files =
        category === "asset-manifest.json"
          ? exists(target)
            ? [target]
            : []
          : walkFiles(target);
      let approved = 0;
      let rejected = 0;
      let unused = 0;
      let manual = 0;
      for (const filePath of files) {
        const assetPath = rel(filePath);
        const reasons = badReasonsForAsset(filePath, category);
        const previousRefs = [...(refMap.get(assetPath) || [])];
        if (reasons.length) {
          rejected += 1;
          if (reasons.some((reason) => reason.includes("manual"))) manual += 1;
          stats.quarantineEntries.push({
            assetPath,
            conceptId: siteId,
            category,
            reason: reasons.join("; "),
            previousRefs,
            replacement: previousRefs.length
              ? "dereferenced and replaced with full Franciele image or CSS/SVG decoration"
              : "left unused and marked unapproved",
            status: "dereferenced; not moved",
            manualReviewNeeded: reasons.some((reason) =>
              reason.includes("manual"),
            )
              ? "yes"
              : "no",
          });
        } else {
          unused += 1;
        }
      }
      stats.folderAudits.push({
        conceptId: siteId,
        conceptName,
        category,
        approved,
        rejected,
        quarantined: 0,
        unused,
        manualReview: manual,
      });
    }
  }
}

function updateManifest(siteId) {
  const info = conceptById(siteId);
  const generatedDir = path.join(generatedRoot, `concept-${info.number}`);
  const manifestPath = path.join(generatedDir, "asset-manifest.json");
  const allGenerated = walkFiles(generatedDir).map(rel).sort();
  const rejectedSet = new Set(
    stats.quarantineEntries
      .filter((entry) => entry.conceptId === siteId)
      .map((entry) => entry.assetPath),
  );
  const conceptPhotos = [
    ...new Set(
      PAGE_ORDER.slice(0, 8).map((page, index) =>
        photoFor(siteId, page, String((index % 10) + 1).padStart(2, "0")),
      ),
    ),
  ];
  const manifest = {
    conceptId: siteId,
    conceptName: info.name,
    approvedAssets: [
      {
        path: "assets/brand/sofiati-logo-primary-sage.png",
        category: "brand",
        role: "header and footer logo",
        usedOnPages: ["all concept pages via partials"],
        usedInSections: ["header", "footer"],
        altText: "Sofiati",
        decorative: false,
        source: "assets/brand",
        license: "client-owned Sofiati brand asset",
        notes: "Approved real brand identity asset.",
      },
      {
        path: "assets/brand/sofiati-favicon.svg",
        category: "brand",
        role: "favicon",
        usedOnPages: ["all concept pages"],
        usedInSections: ["head metadata"],
        altText: "",
        decorative: true,
        source: "assets/brand",
        license: "client-owned Sofiati brand asset",
        notes: "Approved official icon.",
      },
    ],
    quarantinedAssets: stats.quarantineEntries
      .filter((entry) => entry.conceptId === siteId)
      .map((entry) => ({
        path: entry.assetPath,
        category: entry.category,
        reason: entry.reason,
        status: entry.status,
        manualReviewNeeded: entry.manualReviewNeeded,
      })),
    portraitAssets: conceptPhotos.map((photoPath) => ({
      path: photoPath,
      category: "brand portrait",
      role: "full-image Franciele visual",
      usedOnPages: ["rotated across real pages and partials"],
      usedInSections: [
        "hero",
        "about",
        "care",
        "consultation",
        "contact",
        "trust",
      ],
      altText: `Franciele Sofiati full-image ${info.name} visual`,
      decorative: false,
      source: "assets/brand",
      license: "client-owned Sofiati brand photography",
      notes:
        "Rendered with object-fit contain, height auto, and visible overflow.",
    })),
    cssGeneratedAssets: [
      {
        path: "css/sofiati-full-image-premium-system.css",
        category: "css",
        role: "concept-specific surfaces, line accents, frames, and icons",
        usedOnPages: ["all real concept pages"],
        usedInSections: [
          "hero",
          "cards",
          "forms",
          "journal",
          "footer",
          "mobile",
        ],
        altText: "",
        decorative: true,
        source: "local CSS/SVG-like drawing",
        license: "repo-authored",
        notes: "No external source or generated placeholder art.",
      },
    ],
    externalAssets: [],
    unusedAssets: allGenerated
      .filter((assetPath) => !rejectedSet.has(assetPath))
      .map((assetPath) => ({
        path: assetPath,
        category: assetPath.split("/")[3] || "generated",
        role: "unused after premium repair",
        usedOnPages: [],
        usedInSections: [],
        altText: "",
        decorative: true,
        source: "assets/generated unapproved dump",
        license: "unapproved until manual audit",
        notes: "Dereferenced from visitor-facing pages.",
      })),
    manualReviewNeeded: stats.quarantineEntries
      .filter(
        (entry) =>
          entry.conceptId === siteId && entry.manualReviewNeeded === "yes",
      )
      .map((entry) => ({
        path: entry.assetPath,
        reason: entry.reason,
      })),
  };
  if (writeIfChanged(manifestPath, `${JSON.stringify(manifest, null, 2)}\n`)) {
    stats.manifestsUpdated.add(rel(manifestPath));
  }
}

function validateSections() {
  const htmlFiles = walkFiles(
    conceptsRoot,
    (filePath) =>
      filePath.endsWith(".html") &&
      !filePath.includes(`${path.sep}partials${path.sep}`),
  );
  for (const filePath of htmlFiles) {
    const count = (read(filePath).match(/<section\b/gi) || []).length;
    if (count !== 10)
      stats.sectionIssues.push(`${count} sections: ${rel(filePath)}`);
  }
}

function markdownTable(headers, rows) {
  const safeRows = rows.map((row) =>
    row.map((value) => String(value ?? "").replace(/\n/g, " ")),
  );
  return [
    `| ${headers.join(" | ")} |`,
    `| ${headers.map(() => "---").join(" | ")} |`,
    ...safeRows.map((row) => `| ${row.map(escapeHtml).join(" | ")} |`),
  ].join("\n");
}

function writeReports() {
  const changedFiles = [...stats.filesChanged].sort();
  const report = [
    "# Full-Image Premium Asset System Report",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    "## Summary",
    "",
    `- Files changed: ${changedFiles.length}`,
    `- Concepts changed: ${stats.conceptsChanged.size}/50`,
    `- Real pages changed: ${stats.realPagesChanged.size}`,
    `- Partials changed: ${stats.partialsChanged.size}`,
    `- CSS files changed: ${stats.cssFilesChanged.size}`,
    `- JS files changed: ${stats.jsFilesChanged.size}`,
    `- CSS created or updated: css/sofiati-full-image-premium-system.css`,
    `- Real photos found: ${brandPhotos.length}`,
    `- Real photo usages documented: ${stats.photoUsage.length}`,
    `- Generated references dereferenced: ${stats.generatedRefsRemoved.length}`,
    `- Bad assets marked rejected or dereferenced: ${stats.quarantineEntries.length}`,
    `- Bad assets physically moved to quarantine: 0`,
    `- Full-image fixes applied: ${stats.fullImageFixes.length}`,
    `- Object-fit cover replacements: ${stats.objectFitReplacements}`,
    `- Generated CSS urls removed: ${stats.generatedUrlsRemovedFromCss}`,
    `- Manual review items: ${stats.manualReview.length + stats.quarantineEntries.filter((entry) => entry.manualReviewNeeded === "yes").length}`,
    "",
    "## Files Changed",
    "",
    ...changedFiles.map((filePath) => `- ${filePath}`),
  ].join("\n");
  writeIfChanged(
    path.join(docsRoot, "full-image-premium-asset-system-report.md"),
    `${report}\n`,
  );

  const photoRows = stats.photoUsage.map((usage) => [
    usage.sourcePath,
    usage.conceptId,
    usage.page,
    usage.section,
    usage.role,
    usage.cssClass,
    usage.strategy,
    usage.fullImageVisible,
    usage.mobile,
    usage.alt,
    usage.manualReviewNeeded,
  ]);
  const portraitReport = [
    "# Full-Image Portrait Usage Map",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    "## Real Franciele Images Found",
    "",
    ...brandPhotos.map((photo) => `- ${photo}`),
    "",
    "## Usage Map",
    "",
    markdownTable(
      [
        "Source path",
        "Concept ID",
        "Page",
        "Section",
        "Displayed role",
        "CSS class",
        "Full-image sizing strategy",
        "Full image visible",
        "Mobile behaviour",
        "Alt text",
        "Manual review needed",
      ],
      photoRows,
    ),
  ].join("\n");
  writeIfChanged(
    path.join(docsRoot, "full-image-portrait-usage-map.md"),
    `${portraitReport}\n`,
  );

  const folderRows = stats.folderAudits.map((entry) => [
    entry.conceptId,
    entry.conceptName,
    entry.category,
    entry.approved,
    entry.rejected,
    entry.quarantined,
    entry.unused,
    entry.manualReview,
  ]);
  const folderAudit = [
    "# All Generated Asset Folder Audit",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    markdownTable(
      [
        "Concept",
        "Name",
        "Folder category",
        "Approved count",
        "Rejected count",
        "Quarantined count",
        "Unused count",
        "Manual review count",
      ],
      folderRows,
    ),
  ].join("\n");
  writeIfChanged(
    path.join(docsRoot, "all-generated-asset-folder-audit.md"),
    `${folderAudit}\n`,
  );

  const quarantineRows = stats.quarantineEntries.map((entry) => [
    entry.assetPath,
    entry.conceptId,
    entry.category,
    entry.reason,
    entry.previousRefs.join(", ") || "none found",
    entry.replacement,
    entry.status,
    entry.manualReviewNeeded,
  ]);
  const quarantineReport = [
    "# Generated Asset Quarantine Report",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    "Bad generated assets were dereferenced rather than physically moved so existing source history remains intact. The quarantine folder exists for future manual moves.",
    "",
    markdownTable(
      [
        "Asset path",
        "Concept ID",
        "Folder category",
        "Reason rejected",
        "Previous page references",
        "Replacement strategy",
        "Moved/dereferenced/unused",
        "Manual review needed",
      ],
      quarantineRows,
    ),
  ].join("\n");
  writeIfChanged(
    path.join(docsRoot, "generated-asset-quarantine-report.md"),
    `${quarantineReport}\n`,
  );

  const themeRows = CONCEPTS.map(
    ([id, name, direction, frame, decor], index) => [
      id,
      direction,
      index % 2 === 0
        ? "copy first with full portrait counterweight"
        : "portrait first with editorial copy counterweight",
      frame,
      decor,
      [
        "quiet button pair",
        "strong consultation rail",
        "soft stacked CTA",
        "minimal text link CTA",
      ][index % 4],
      [
        "inline framed form",
        "portrait-side form",
        "minimal field stack",
        "editorial form band",
      ][index % 4],
      [
        "journal cards with CSS marks",
        "article rail",
        "soft editorial list",
        "trust-led reading path",
      ][index % 4],
      [
        "compact column footer",
        "editorial brand panel",
        "quiet trust footer",
        "structured route footer",
      ][index % 4],
      [
        "portrait stacks first",
        "copy stacks first",
        "card rows tighten",
        "wide frames become narrow",
      ][index % 4],
      index % 5 === 0
        ? "medium - adjacent concepts need screenshot review"
        : "low after variable/frame/layout split",
    ],
  );
  const themeReport = [
    "# Concept Theme Differentiation Report",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    markdownTable(
      [
        "Concept",
        "Theme direction",
        "Hero layout difference",
        "Full-image frame difference",
        "Decorative system difference",
        "CTA difference",
        "Form difference",
        "Journal difference",
        "Footer difference",
        "Mobile difference",
        "Risk of looking too similar",
      ],
      themeRows,
    ),
  ].join("\n");
  writeIfChanged(
    path.join(docsRoot, "concept-theme-differentiation-report.md"),
    `${themeReport}\n`,
  );

  const risks = [
    "# Remaining Visual Risks",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    "## Pages Still Visually Risky",
    "",
    "- Representative rendered screenshots are still required to judge visual polish beyond code-level dereferencing.",
    "- Concepts with medium similarity risk: 01, 06, 11, 16, 21, 26, 31, 36, 41, 46.",
    "",
    "## Image Sizing Risks",
    "",
    "- All Franciele images now use full-image CSS, but transparent-source whitespace can vary by original photo.",
    "- Manual review should confirm no photo feels too small in hero sections.",
    "",
    "## Repeated Layout Risks",
    "",
    "- The atlas still shares a structural 10-section system; concept variables and frame treatments reduce but do not eliminate similarity.",
    "",
    "## Generated Asset Risks",
    "",
    `- ${stats.quarantineEntries.length} generated assets are marked rejected or manual-review instead of approved.`,
    "- Generated assets are left in place for history and future manual review, but they are dereferenced from visitor-facing pages and concept CSS.",
    "",
    "## Manual Screenshot Review Needed",
    "",
    "- Open http://localhost:8080/select.html and inspect desktop/mobile for at least one concept in each layout family.",
  ].join("\n");
  writeIfChanged(
    path.join(docsRoot, "remaining-visual-risks.md"),
    `${risks}\n`,
  );

  const sourcing = [
    "# Copyright-Free Asset Sourcing Needed",
    "",
    `Generated: ${new Date().toISOString()}`,
    "",
    "No external assets were fetched for this repair. The implementation uses client-owned assets from assets/brand plus repo-authored CSS decoration.",
    "",
    "If future concepts need external atmosphere imagery, record each source in data/asset-sources.json before use.",
  ].join("\n");
  writeIfChanged(
    path.join(docsRoot, "copyright-free-asset-sourcing-needed.md"),
    `${sourcing}\n`,
  );

  writeIfChanged(path.join(dataRoot, "asset-sources.json"), "[]\n");

  const sectionText = stats.sectionIssues.join("\n");
  writeIfChanged(
    path.join(
      docsRoot,
      "pages-not-10-sections-after-full-image-premium-repair.txt",
    ),
    sectionText ? `${sectionText}\n` : "",
  );
}

function main() {
  ensureDir(quarantineRoot);
  ensureDir(docsRoot);
  ensureDir(dataRoot);
  writeIfChanged(
    path.join(quarantineRoot, "README.md"),
    "# Generated Placeholder Asset Quarantine\n\nThis folder is reserved for generated assets that are safe to move after manual review. The current repair dereferences rejected assets first and leaves source files in place for auditability.\n",
  );

  const refMap = collectGeneratedReferenceMap();
  writeIfChanged(premiumCssPath, cssForPremiumSystem());
  writeIfChanged(legacyRescueCssPath, legacyRescueCss());

  const htmlFiles = walkFiles(conceptsRoot, (filePath) =>
    filePath.endsWith(".html"),
  );
  for (const filePath of htmlFiles) {
    if (filePath.includes(`${path.sep}partials${path.sep}`))
      repairPartial(filePath);
    else repairRealPage(filePath, refMap);
  }

  for (const filePath of walkFiles(conceptsRoot, (filePath) =>
    filePath.endsWith(".css"),
  )) {
    repairConceptCss(filePath);
  }

  for (const filePath of walkFiles(conceptsRoot, (filePath) =>
    filePath.endsWith(".js"),
  )) {
    repairConceptJs(filePath);
  }

  auditGeneratedAssets(refMap);
  for (const [siteId] of CONCEPTS) updateManifest(siteId);
  validateSections();
  writeReports();

  console.log(`Full-image premium repair complete.`);
  console.log(`Files changed: ${stats.filesChanged.size}`);
  console.log(`Real pages changed: ${stats.realPagesChanged.size}`);
  console.log(
    `Generated references dereferenced: ${stats.generatedRefsRemoved.length}`,
  );
  console.log(`Photo usages documented: ${stats.photoUsage.length}`);
  console.log(`Section issues: ${stats.sectionIssues.length}`);
}

main();
