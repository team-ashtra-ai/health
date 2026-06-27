#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import {
  flattenGeneratedAssetRefs,
  generatedAssetRefs,
  siteProfile,
} from "./lib/sofiati-atlas-core.mjs";

const root = process.cwd();
const generatedRoot = path.join(root, "assets", "generated");
const brandDir = path.join(root, "assets", "brand");
const photosDir = path.join(root, "assets", "photos");
const conceptRoot = path.join(root, "concepts");

const sourceUsage = {
  migratedBrandSources: [],
  photoSources: new Set(),
  transparentBrandSources: new Set(),
};

const directions = [
  "soft-clinical-luxury",
  "botanical-editorial",
  "gold-minimalism",
  "dark-premium-editorial",
  "warm-beige-wellness",
  "modern-dermatology",
  "consultation-studio",
  "magazine-beauty",
  "calm-medical-spa",
  "portrait-led-brand",
];

const gravities = [
  "Center",
  "North",
  "South",
  "East",
  "West",
  "NorthEast",
  "NorthWest",
  "SouthEast",
  "SouthWest",
];

const palettes = [
  ["#485041", "#CDAA78", "#F8F7F2", "#252321"],
  ["#6B5846", "#A2AEA0", "#F2EEE3", "#2E2A24"],
  ["#5F6E61", "#D1A771", "#FFF9ED", "#28302A"],
  ["#2E332B", "#B88352", "#F6F0E5", "#151613"],
  ["#735C62", "#CDAA78", "#F7EFE8", "#31282B"],
  ["#4D5A63", "#A2AEA0", "#F8F7F2", "#1F272B"],
  ["#694B43", "#C9A56A", "#FBF5EC", "#2D211D"],
  ["#403F36", "#B7A06D", "#F2EEE3", "#252321"],
  ["#586D73", "#9A6B35", "#F6F4EA", "#20282B"],
  ["#505E54", "#8F7955", "#F8F7F2", "#222720"],
];

function titleCase(value) {
  return value
    .split("-")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function listFiles(dir, pattern) {
  if (!fs.existsSync(dir)) return [];
  return fs
    .readdirSync(dir)
    .filter((name) => pattern.test(name))
    .map((name) => path.join(dir, name))
    .sort();
}

function ensureDir(filePath) {
  fs.mkdirSync(path.dirname(filePath), { recursive: true });
}

function writeFileIfChanged(filePath, content) {
  ensureDir(filePath);
  if (fs.existsSync(filePath) && fs.readFileSync(filePath, "utf8") === content)
    return false;
  fs.writeFileSync(filePath, content);
  return true;
}

function copyIfMissing(source, dest) {
  if (!fs.existsSync(source)) return;
  fs.mkdirSync(path.dirname(dest), { recursive: true });
  if (!fs.existsSync(dest)) {
    fs.copyFileSync(source, dest);
    sourceUsage.migratedBrandSources.push(path.relative(root, dest));
  }
}

function migrateBrandSources() {
  fs.mkdirSync(brandDir, { recursive: true });
  const conceptBrand = path.join(
    root,
    "concepts",
    "01-inspire",
    "assets",
    "brand",
  );
  [
    "sofiati-logo-primary-bronze.png",
    "sofiati-logo-primary-white.png",
    "sofiati-logo-primary-sage.png",
    "sofiati-monogram-bronze.png",
    "sofiati-monogram-white.png",
    "sofiati-monogram-sage.png",
    "sofiati-signature-white.png",
    "sofiati-signature-sage.png",
    "sofiati-botanical-line-mark.svg",
    "sofiati-favicon.svg",
    "footer-signature-watermark.png",
    "assinatura-1.jpg",
  ].forEach((name) =>
    copyIfMissing(path.join(conceptBrand, name), path.join(brandDir, name)),
  );
}

function conceptSites() {
  return fs
    .readdirSync(conceptRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && /^\d{2}-/.test(entry.name))
    .map((entry, index) => ({
      siteId: entry.name,
      siteName: titleCase(entry.name.slice(3)),
      number: entry.name.slice(0, 2),
      slug: entry.name.slice(3),
      index,
    }))
    .sort((a, b) => a.siteId.localeCompare(b.siteId));
}

function xml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function relHref(fromFile, toFile) {
  return path
    .relative(path.dirname(fromFile), toFile)
    .replaceAll(path.sep, "/");
}

function generatedFilePath(ref) {
  return path.join(root, ref);
}

function palette(profile) {
  return palettes[profile.index % palettes.length];
}

function writeSvg(ref, content) {
  writeFileIfChanged(generatedFilePath(ref), content);
}

function runMagick(args) {
  execFileSync("magick", args, { stdio: "pipe" });
}

function makePhotoCrop(source, ref, width, height, profile, offset = 0) {
  const out = generatedFilePath(ref);
  ensureDir(out);
  const gravity = gravities[(profile.index + offset) % gravities.length];
  const brightness = 94 + ((profile.index + offset) % 9);
  const saturation = 82 + ((profile.index + offset * 3) % 18);
  runMagick([
    source,
    "-auto-orient",
    "-resize",
    `${width}x${height}^`,
    "-gravity",
    gravity,
    "-extent",
    `${width}x${height}`,
    "-modulate",
    `${brightness},${saturation},100`,
    "-strip",
    "-quality",
    "72",
    out,
  ]);
  sourceUsage.photoSources.add(path.relative(root, source));
}

function makePortraitComposite(source, ref, width, height, profile, offset = 0) {
  const out = generatedFilePath(ref);
  ensureDir(out);
  const [primary, accent, surface] = palette(profile);
  const gravity = offset % 2 === 0 ? "South" : "Center";
  const imageWidth = Math.round(width * (offset % 3 === 0 ? 0.76 : 0.66));
  runMagick([
    "-size",
    `${width}x${height}`,
    `xc:${surface}`,
    "(",
    "-size",
    `${width}x${height}`,
    `gradient:${surface}-${primary}`,
    "-alpha",
    "set",
    "-channel",
    "a",
    "-evaluate",
    "set",
    `${18 + (profile.index % 12)}%`,
    "+channel",
    ")",
    "-composite",
    source,
    "-resize",
    `${imageWidth}x${Math.round(height * 0.92)}>`,
    "-gravity",
    gravity,
    "-composite",
    "-bordercolor",
    accent,
    "-border",
    offset % 2 === 0 ? "10" : "0",
    "-strip",
    "-quality",
    "74",
    out,
  ]);
  sourceUsage.transparentBrandSources.add(path.relative(root, source));
}

function makeLogoComposite(source, ref, width, height, profile) {
  const out = generatedFilePath(ref);
  ensureDir(out);
  const [primary, accent, surface] = palette(profile);
  runMagick([
    "-size",
    `${width}x${height}`,
    `gradient:${surface}-${primary}`,
    source,
    "-resize",
    `${Math.round(width * 0.58)}x${Math.round(height * 0.34)}>`,
    "-gravity",
    "Center",
    "-composite",
    "-fill",
    "none",
    "-stroke",
    accent,
    "-strokewidth",
    "12",
    "-draw",
    `rectangle 24,24 ${width - 24},${height - 24}`,
    "-strip",
    "-quality",
    "76",
    out,
  ]);
  sourceUsage.transparentBrandSources.add(path.relative(root, source));
}

function countFiles(dir) {
  if (!fs.existsSync(dir)) return 0;
  return fs.readdirSync(dir, { withFileTypes: true }).reduce((total, entry) => {
    const full = path.join(dir, entry.name);
    return total + (entry.isDirectory() ? countFiles(full) : 1);
  }, 0);
}

function makePngFromSvg(sourceRef, targetRef, size) {
  const source = generatedFilePath(sourceRef);
  const target = generatedFilePath(targetRef);
  ensureDir(target);
  runMagick([source, "-resize", `${size}x${size}`, "-background", "none", target]);
}

function makeIcoFromSvg(sourceRef, targetRef) {
  const source = generatedFilePath(sourceRef);
  const target = generatedFilePath(targetRef);
  ensureDir(target);
  runMagick([source, "-resize", "64x64", "-background", "none", target]);
}

function logoSvg(ref, profile, sourceName, variant) {
  const out = generatedFilePath(ref);
  const source = path.join(brandDir, sourceName);
  const href = fs.existsSync(source) ? relHref(out, source) : "";
  const [primary, accent, surface, ink] = palette(profile);
  const direction = directions[profile.index % directions.length];
  const isDark = variant.includes("dark") || variant.includes("footer");
  const bg = isDark ? ink : surface;
  const fg = isDark ? surface : primary;
  const radius = [0, 12, 32, 72, 140][profile.index % 5];
  const image = href
    ? `<image href="${xml(href)}" x="130" y="96" width="700" height="170" preserveAspectRatio="xMidYMid meet"/>`
    : `<text x="480" y="190" text-anchor="middle" font-family="Georgia, serif" font-size="88" fill="${fg}">Sofiati</text>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="960" height="420" viewBox="0 0 960 420" role="img" aria-label="Sofiati ${xml(profile.siteName)} ${xml(variant)} logo treatment">
  <rect width="960" height="420" rx="${radius}" fill="${bg}"/>
  <rect x="28" y="28" width="904" height="364" rx="${Math.max(0, radius - 8)}" fill="none" stroke="${accent}" stroke-width="${profile.index % 2 ? 2 : 4}" opacity=".82"/>
  <path d="M92 316 C188 260 280 354 390 296 C486 246 560 288 650 244 C730 204 784 210 870 166" fill="none" stroke="${accent}" stroke-width="2" opacity=".45"/>
  ${image}
  <text x="480" y="314" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="21" letter-spacing="4" fill="${fg}" opacity=".82">${xml(profile.siteName.toUpperCase())} / ${xml(direction.toUpperCase())}</text>
</svg>
`;
}

function simpleAssetSvg(profile, label, role, options = {}) {
  const [primary, accent, surface, ink] = palette(profile);
  const w = options.width || 960;
  const h = options.height || 640;
  const radius = options.radius ?? [0, 18, 44, 88][profile.index % 4];
  const reverse = options.dark || false;
  const bg = reverse ? ink : options.bg || surface;
  const fg = reverse ? surface : primary;
  const line = options.accent || accent;
  const patternId = `p${profile.number}${label.replace(/[^a-z0-9]/gi, "")}`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}" viewBox="0 0 ${w} ${h}" role="img" aria-label="${xml(label)} for ${xml(profile.siteName)}">
  <defs>
    <pattern id="${patternId}" width="${32 + (profile.index % 5) * 6}" height="${32 + (profile.index % 5) * 6}" patternUnits="userSpaceOnUse">
      <path d="M4 22 C16 4 22 30 34 8" fill="none" stroke="${line}" stroke-width="1" opacity=".22"/>
    </pattern>
  </defs>
  <rect width="${w}" height="${h}" rx="${radius}" fill="${bg}"/>
  <rect width="${w}" height="${h}" fill="url(#${patternId})" opacity=".72"/>
  <rect x="34" y="34" width="${w - 68}" height="${h - 68}" rx="${Math.max(0, radius - 14)}" fill="none" stroke="${line}" stroke-width="${profile.index % 3 === 0 ? 4 : 2}" opacity=".74"/>
  <circle cx="${Math.round(w * (0.22 + (profile.index % 4) * 0.08))}" cy="${Math.round(h * 0.34)}" r="${70 + (profile.index % 7) * 8}" fill="${line}" opacity=".16"/>
  <path d="M${Math.round(w * 0.18)} ${Math.round(h * 0.72)} C${Math.round(w * 0.34)} ${Math.round(h * 0.54)} ${Math.round(w * 0.48)} ${Math.round(h * 0.88)} ${Math.round(w * 0.64)} ${Math.round(h * 0.62)} S${Math.round(w * 0.82)} ${Math.round(h * 0.52)} ${Math.round(w * 0.9)} ${Math.round(h * 0.36)}" fill="none" stroke="${line}" stroke-width="4" stroke-linecap="round" opacity=".62"/>
  <text x="${Math.round(w * 0.12)}" y="${Math.round(h * 0.24)}" font-family="Inter, Arial, sans-serif" font-size="22" letter-spacing="5" fill="${fg}" opacity=".72">${xml(profile.number)} / ${xml(role.toUpperCase())}</text>
  <text x="${Math.round(w * 0.12)}" y="${Math.round(h * 0.38)}" font-family="Georgia, serif" font-size="${Math.round(h * 0.1)}" fill="${fg}">${xml(label)}</text>
  <text x="${Math.round(w * 0.12)}" y="${Math.round(h * 0.5)}" font-family="Inter, Arial, sans-serif" font-size="24" fill="${fg}" opacity=".74">${xml(profile.siteName)} / ${xml(directions[profile.index % directions.length])}</text>
</svg>
`;
}

function iconSvg(profile, label, symbol = "circle") {
  const [primary, accent, surface, ink] = palette(profile);
  const dark = profile.index % 5 === 3;
  const bg = dark ? ink : surface;
  const fg = dark ? surface : primary;
  const y = symbol === "laser" ? 270 : 250;
  const symbolMarkup =
    symbol === "laser"
      ? `<path d="M150 300 H810 M430 210 L530 300 L430 390" fill="none" stroke="${accent}" stroke-width="28" stroke-linecap="round" stroke-linejoin="round"/>`
      : symbol === "skin"
        ? `<path d="M306 330 C306 210 412 132 498 132 C604 132 678 222 654 332 C632 436 554 492 468 486 C378 480 306 418 306 330Z" fill="none" stroke="${accent}" stroke-width="24"/><circle cx="474" cy="300" r="44" fill="${accent}" opacity=".22"/>`
        : symbol === "consultation"
          ? `<rect x="246" y="168" width="468" height="300" rx="42" fill="none" stroke="${accent}" stroke-width="22"/><path d="M330 270 H630 M330 342 H560" stroke="${accent}" stroke-width="20" stroke-linecap="round"/>`
          : `<circle cx="480" cy="310" r="150" fill="none" stroke="${accent}" stroke-width="24"/><path d="M410 330 C460 250 506 380 560 288" fill="none" stroke="${accent}" stroke-width="22" stroke-linecap="round"/>`;
  return `<svg xmlns="http://www.w3.org/2000/svg" width="960" height="640" viewBox="0 0 960 640" role="img" aria-label="${xml(label)} icon set for ${xml(profile.siteName)}">
  <rect width="960" height="640" rx="${profile.radius}" fill="${bg}"/>
  <rect x="40" y="40" width="880" height="560" rx="${Math.max(0, profile.radius - 6)}" fill="none" stroke="${accent}" stroke-width="2" opacity=".5"/>
  ${symbolMarkup}
  <text x="480" y="${y + 220}" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="24" letter-spacing="5" fill="${fg}" opacity=".82">${xml(label.toUpperCase())}</text>
</svg>
`;
}

function writeLogoAssets(profile, refs, brandSources) {
  const darkLogo = brandSources.logoSage || brandSources.logoBronze || brandSources.logoWhite;
  const lightLogo = brandSources.logoWhite || brandSources.logoSage || brandSources.logoBronze;
  writeSvg(
    refs.logos.lockup,
    logoSvg(refs.logos.lockup, profile, path.basename(darkLogo), "lockup"),
  );
  writeSvg(
    refs.logos.badge,
    logoSvg(refs.logos.badge, profile, path.basename(darkLogo), "badge"),
  );
  writeSvg(
    refs.logos.mark,
    logoSvg(refs.logos.mark, profile, path.basename(brandSources.monogram || darkLogo), "mark"),
  );
  writeSvg(
    refs.logos.seal,
    logoSvg(refs.logos.seal, profile, path.basename(brandSources.favicon || darkLogo), "seal"),
  );
  writeSvg(
    refs.logos.header,
    logoSvg(refs.logos.header, profile, path.basename(darkLogo), "header"),
  );
  writeSvg(
    refs.logos.footer,
    logoSvg(refs.logos.footer, profile, path.basename(lightLogo), "footer-dark"),
  );
  writeSvg(
    refs.logos.mobile,
    logoSvg(refs.logos.mobile, profile, path.basename(lightLogo), "mobile-dark"),
  );
  writeSvg(
    refs.logos.social,
    logoSvg(refs.logos.social, profile, path.basename(darkLogo), "social"),
  );
  writeSvg(
    refs.logos.watermark,
    simpleAssetSvg(profile, "Sofiati watermark", "logo watermark", {
      width: 720,
      height: 720,
      dark: profile.index % 4 === 0,
    }),
  );
  writeSvg(
    refs.logos.favicon,
    `<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128" role="img" aria-label="Sofiati ${xml(profile.siteName)} favicon">
  <rect width="128" height="128" rx="${[0, 18, 32, 64][profile.index % 4]}" fill="${palette(profile)[0]}"/>
  <path d="M30 86 C48 40 72 96 98 36" fill="none" stroke="${palette(profile)[1]}" stroke-width="7" stroke-linecap="round"/>
  <text x="64" y="76" text-anchor="middle" font-family="Georgia, serif" font-size="48" fill="${palette(profile)[2]}">S</text>
</svg>
`,
  );
  makeLogoComposite(darkLogo, refs.logos.background, 1200, 720, profile);
  makeIcoFromSvg(refs.logos.favicon, refs.logos.faviconIco);
}

function writeSvgGroups(profile, refs) {
  Object.entries(refs.brandBackgrounds).forEach(([key, ref], index) => {
    writeSvg(
      ref,
      simpleAssetSvg(profile, `Brand ${key}`, "brand background", {
        dark: key === "dark",
        bg:
          key === "gold"
            ? palette(profile)[1]
            : key === "botanicalGreen"
              ? palette(profile)[0]
              : undefined,
        radius: [0, 24, 80, 160][(profile.index + index) % 4],
      }),
    );
  });

  Object.entries(refs.icons).forEach(([key, ref]) => {
    writeSvg(
      ref,
      iconSvg(
        profile,
        `${profile.siteName} ${key.replace(/([A-Z])/g, " $1")}`,
        key.includes("laser")
          ? "laser"
          : key.includes("skin")
            ? "skin"
            : key.includes("consult")
              ? "consultation"
              : "circle",
      ),
    );
  });

  Object.entries(refs.backgrounds).forEach(([key, ref], index) => {
    writeSvg(
      ref,
      simpleAssetSvg(profile, `${key} background`, "section background", {
        dark: key === "footer" || (profile.index + index) % 7 === 0,
        radius: [0, 18, 48, 120][(profile.index + index) % 4],
      }),
    );
  });

  Object.entries(refs.cards).forEach(([key, ref], index) => {
    writeSvg(
      ref,
      simpleAssetSvg(profile, `${key} card`, "card asset", {
        width: 760,
        height: 520,
        dark: (profile.index + index) % 6 === 0,
        radius: [0, 8, 22, 44, 88][(profile.index + index) % 5],
      }),
    );
  });

  Object.entries(refs.cta)
    .filter(([, ref]) => ref.endsWith(".svg"))
    .forEach(([key, ref], index) => {
      writeSvg(
        ref,
        simpleAssetSvg(profile, `${key} CTA`, "cta asset", {
          dark: key.includes("seal") || (profile.index + index) % 4 === 0,
          radius: [0, 24, 72, 140][(profile.index + index) % 4],
        }),
      );
    });

  Object.entries(refs.decorative).forEach(([key, ref], index) => {
    writeSvg(
      ref,
      simpleAssetSvg(profile, `${key} decoration`, "decorative asset", {
        width: key.includes("divider") ? 1200 : 720,
        height: key.includes("divider") ? 160 : 720,
        dark: key.includes("watermark") && profile.index % 2 === 0,
        radius: key.includes("divider") ? 0 : [0, 60, 160][index % 3],
      }),
    );
  });

  Object.entries(refs.navigation).forEach(([key, ref], index) => {
    writeSvg(
      ref,
      simpleAssetSvg(profile, `${key} navigation`, "navigation asset", {
        width: key.includes("Background") ? 1200 : 720,
        height: key.includes("Background") ? 1500 : 520,
        dark: (profile.index + index) % 3 === 0,
        radius: [0, 28, 96][(profile.index + index) % 3],
      }),
    );
  });

  Object.entries(refs.footer).forEach(([key, ref], index) => {
    writeSvg(
      ref,
      simpleAssetSvg(profile, `${key} footer`, "footer asset", {
        width: key === "background" ? 1400 : 780,
        height: key === "background" ? 760 : 520,
        dark: true,
        radius: [0, 20, 80][(profile.index + index) % 3],
      }),
    );
  });

  Object.entries(refs.forms)
    .filter(([, ref]) => ref.endsWith(".svg"))
    .forEach(([key, ref], index) => {
      writeSvg(
        ref,
        simpleAssetSvg(profile, `${key} form`, "form asset", {
          width: 900,
          height: 720,
          dark: (profile.index + index) % 5 === 0,
          radius: [0, 18, 44, 90][(profile.index + index) % 4],
        }),
      );
    });

  Object.entries(refs.journal)
    .filter(([, ref]) => ref.endsWith(".svg"))
    .forEach(([key, ref], index) => {
      writeSvg(
        ref,
        simpleAssetSvg(profile, `${key} journal`, "journal asset", {
          width: 900,
          height: 620,
          dark: (profile.index + index) % 4 === 1,
          radius: [0, 12, 48][(profile.index + index) % 3],
        }),
      );
    });

  Object.entries(refs.social)
    .filter(([, ref]) => ref.endsWith(".svg"))
    .forEach(([key, ref]) => {
      writeSvg(ref, simpleAssetSvg(profile, `${key} social`, "social asset"));
    });

  Object.entries(refs.sectionAssets).forEach(([key, ref], index) => {
    writeSvg(
      ref,
      simpleAssetSvg(profile, `${key} section`, "section asset", {
        dark: (profile.index + index) % 8 === 0,
        radius: [0, 32, 72][(profile.index + index) % 3],
      }),
    );
  });
}

function writePortraitSvg(profile, ref, source) {
  const out = generatedFilePath(ref);
  const href = relHref(out, source);
  const [primary, accent, surface] = palette(profile);
  writeSvg(
    ref,
    `<svg xmlns="http://www.w3.org/2000/svg" width="900" height="900" viewBox="0 0 900 900" role="img" aria-label="Circular Franciele portrait for ${xml(profile.siteName)}">
  <defs>
    <clipPath id="portraitCircle"><circle cx="450" cy="430" r="318"/></clipPath>
  </defs>
  <rect width="900" height="900" fill="${surface}"/>
  <circle cx="450" cy="430" r="362" fill="${primary}" opacity=".16"/>
  <circle cx="450" cy="430" r="330" fill="none" stroke="${accent}" stroke-width="18"/>
  <image href="${xml(href)}" x="142" y="74" width="616" height="820" preserveAspectRatio="xMidYMax meet" clip-path="url(#portraitCircle)"/>
  <text x="450" y="820" text-anchor="middle" font-family="Inter, Arial, sans-serif" font-size="24" letter-spacing="5" fill="${primary}">${xml(profile.siteName.toUpperCase())}</text>
</svg>
`,
  );
}

function buildConceptAssets(profile, sources, brandSources) {
  const refs = generatedAssetRefs(profile, "");
  const photo = sources.photos[profile.index % sources.photos.length];
  const photoAlt = sources.photos[(profile.index + 11) % sources.photos.length];
  const portrait = sources.transparent[profile.index % sources.transparent.length];
  const portraitAlt = sources.transparent[(profile.index + 6) % sources.transparent.length];

  writeLogoAssets(profile, refs, brandSources);
  writeSvgGroups(profile, refs);
  writePortraitSvg(profile, refs.portraits.circle, portrait);

  makePhotoCrop(photo, refs.heroes.desktop, 1400, 980, profile, 0);
  makePhotoCrop(photoAlt, refs.heroes.background, 1800, 1100, profile, 1);
  makePortraitComposite(portrait, refs.heroes.portrait, 1040, 1320, profile, 2);
  makePortraitComposite(portraitAlt, refs.heroes.mobile, 900, 1300, profile, 3);
  makePortraitComposite(portrait, refs.portraits.crop, 900, 1100, profile, 4);
  makePortraitComposite(portraitAlt, refs.portraits.editorial, 1100, 1400, profile, 5);
  makePortraitComposite(portrait, refs.portraits.vertical, 880, 1300, profile, 6);
  makePortraitComposite(portraitAlt, refs.portraits.square, 980, 980, profile, 7);
  makePortraitComposite(portrait, refs.portraits.card, 1080, 1180, profile, 8);
  makePortraitComposite(portraitAlt, refs.portraits.background, 1400, 900, profile, 9);

  makePhotoCrop(photoAlt, refs.cta.finalBackground, 1400, 720, profile, 10);
  makePhotoCrop(photo, refs.cta.imagePanel, 980, 1180, profile, 11);
  makePhotoCrop(photoAlt, refs.forms.background, 1200, 850, profile, 12);
  makePhotoCrop(photo, refs.forms.sideImage, 860, 1180, profile, 13);
  makePhotoCrop(photoAlt, refs.forms.headerImage, 1200, 520, profile, 14);
  makePhotoCrop(photo, refs.journal.blogHero, 1400, 760, profile, 15);
  makePhotoCrop(photoAlt, refs.journal.blogCard, 840, 640, profile, 16);
  makePhotoCrop(photo, refs.journal.featuredArticle, 1200, 860, profile, 17);
  makePhotoCrop(photoAlt, refs.journal.articleHeader, 1400, 680, profile, 18);
  makePhotoCrop(photo, refs.social.openGraph, 1200, 630, profile, 19);
  makePhotoCrop(photoAlt, refs.social.whatsappPreview, 1200, 630, profile, 20);
  makePhotoCrop(photo, refs.social.share, 1200, 630, profile, 21);
  makePhotoCrop(photoAlt, refs.social.servicePreview, 1200, 630, profile, 22);
  makePhotoCrop(photo, refs.social.consultationPreview, 1200, 630, profile, 23);
  makePhotoCrop(photo, refs.responsive.desktop, 1280, 820, profile, 24);
  makePhotoCrop(photoAlt, refs.responsive.tablet, 900, 900, profile, 25);
  makePhotoCrop(photo, refs.responsive.mobile, 720, 1080, profile, 26);
  makePhotoCrop(photoAlt, refs.responsive.square, 900, 900, profile, 27);
  makePhotoCrop(photo, refs.responsive.vertical, 760, 1100, profile, 28);
  makePhotoCrop(photoAlt, refs.responsive.wide, 1400, 620, profile, 29);
  makePhotoCrop(photo, refs.responsive.thumbnail, 420, 320, profile, 30);
  makePhotoCrop(photoAlt, refs.responsive.lqip, 64, 48, profile, 31);
  makePhotoCrop(photo, refs.responsive.compressed, 960, 640, profile, 32);

  makePngFromSvg(refs.logos.favicon, refs.social.appleTouch, 180);
  makePngFromSvg(refs.logos.favicon, refs.social.androidIcon, 192);

  const manifest = {
    siteId: profile.siteId,
    siteName: profile.siteName,
    conceptNumber: profile.number,
    visualDirection: directions[profile.index % directions.length],
    sourcePhotos: [path.relative(root, photo), path.relative(root, photoAlt)],
    transparentBrandSources: [
      path.relative(root, portrait),
      path.relative(root, portraitAlt),
    ],
    sourceBrandFolder: "assets/brand",
    generatedAssets: flattenGeneratedAssetRefs(refs),
    notes: [
      "All generated media is derived from local assets/photos and assets/brand.",
      "assets/brand-photos is absent on this branch; transparent portrait sources in assets/brand are used instead.",
      "Concept-local assets are replaced by assets/generated/concept-XX paths.",
    ],
  };
  writeFileIfChanged(
    path.join(root, "assets", "generated", `concept-${profile.number}`, "asset-manifest.json"),
    JSON.stringify(manifest, null, 2) + "\n",
  );
  return manifest;
}

function navLinks() {
  return [
    ["index.html", "Home"],
    ["about.html", "About"],
    ["care.html", "Care"],
    ["laser.html", "Laser"],
    ["skin.html", "Skin"],
    ["results.html", "Results"],
    ["consultation.html", "Consultation"],
    ["contact.html", "Contact"],
  ];
}

function headerPartial(profile, refs) {
  const mode = [
    "split",
    "centered",
    "compact",
    "editorial",
    "minimal",
    "studio",
  ][profile.index % 6];
  const secondary = profile.index % 3 === 0 ? "secondary-care" : "secondary-path";
  return `<header class="site-header public-header public-header-${profile.number} public-header-layout-${mode} atlas-public-header-${profile.number}" data-public-header="${mode}" data-layout-signature="${profile.siteId}-header-${directions[profile.index % directions.length]}">
  <div class="public-header-shell">
    <div class="public-nav-zone public-nav-left" data-navigation-slot="${profile.index % 2 === 0 ? "split-left" : "compact"}"></div>
    <a class="brand-mark public-brand-mark" href="index.html" aria-label="Sofiati home">
      <img src="${refs.logos.header}" alt="Sofiati ${profile.siteName} logo treatment">
    </a>
    <div class="public-nav-zone public-nav-right" data-navigation-slot="${profile.index % 2 === 0 ? "split-right" : "primary"}"></div>
    <div class="public-header-tools">
      <a class="header-consultation" href="consultation.html">Consultation</a>
      <button class="menu-button public-menu-button" type="button" data-menu-toggle aria-controls="mobile-menu" aria-expanded="false" aria-label="Open menu">Menu</button>
    </div>
  </div>
  <div class="public-secondary-bar public-secondary-${profile.number}" data-public-secondary="${secondary}">
    <div data-navigation-slot="${secondary}"></div>
  </div>
</header>
`;
}

function mobileMenuPartial(profile, refs) {
  return `<aside class="mobile-menu public-mobile-menu public-menu-${profile.number} public-menu-layout-${directions[profile.index % directions.length]}" id="mobile-menu" data-public-menu="${directions[profile.index % directions.length]}" aria-hidden="true" aria-modal="true" role="dialog" aria-label="Site menu" tabindex="-1" data-layout-signature="${profile.siteId}-mobile-menu-${directions[profile.index % directions.length]}">
  <img class="mobile-menu-asset-bg public-menu-bg" src="${refs.navigation.mobileMenuBackground}" alt="" aria-hidden="true">
  <div class="mobile-menu-top public-mobile-menu-top">
    <a class="brand-mark public-brand-mark" href="index.html" aria-label="Sofiati home">
      <img src="${refs.logos.mobile}" alt="Sofiati ${profile.siteName} mobile logo">
    </a>
    <button class="public-menu-close" type="button" data-menu-close aria-label="Close menu">
      <img src="${refs.navigation.closeIcon}" alt="" aria-hidden="true">
    </button>
  </div>
  <img class="mobile-menu-avatar doctor-portrait doctor-portrait--menu" src="${refs.portraits.square}" alt="Franciele Sofiati portrait for ${profile.siteName}" decoding="async" loading="lazy" width="980" height="980">
  <nav class="mobile-menu-primary public-mobile-primary" aria-label="Mobile primary navigation">
    ${navLinks().map(([href, label]) => `<a href="${href}" class="mobile-menu-link">${label}</a>`).join("\n    ")}
  </nav>
  <a class="mobile-consult public-mobile-cta" href="consultation.html">Consultation</a>
</aside>
`;
}

function footerPartial(profile, refs) {
  return `<footer class="site-footer public-footer public-footer-${profile.number} public-footer-recipe-${profile.slug}" data-footer-recipe="${directions[profile.index % directions.length]}" data-layout-signature="${profile.siteId}-footer-${directions[profile.index % directions.length]}">
  <img class="public-footer-watermark" src="${refs.footer.watermark}" alt="" aria-hidden="true">
  <div class="public-footer-shell">
    <section class="footer-brand-panel" aria-label="About" data-section-id="${profile.siteId}-footer-brand" data-layout-signature="${profile.siteId}-footer-brand-panel-${directions[profile.index % directions.length]}">
      <a class="footer-signature-logo" href="index.html" aria-label="Sofiati home">
        <img src="${refs.logos.footer}" alt="Franciele Sofiati footer logo">
      </a>
      <h3><span class="footer-heading-icon" aria-hidden="true"></span>About</h3>
      <h2>Franciele Sofiati</h2>
      <p class="footer-role">Advanced Aesthetic Biomedicine</p>
      <p class="footer-credential">CRBM 6277</p>
      <p class="footer-description">Laser and skin care guided by professional evaluation in Londrina, PR.</p>
      <a class="footer-cta" href="consultation.html">Consultation</a>
    </section>
    <nav class="footer-link-group footer-main-links" aria-label="Main Pages">
      <h3><span class="footer-heading-icon" aria-hidden="true"></span>Main Pages</h3>
      ${navLinks().map(([href, label]) => `<a href="${href}">${label}</a>`).join("\n      ")}
    </nav>
    <nav class="footer-link-group footer-trust-links" aria-label="About">
      <h3><span class="footer-heading-icon" aria-hidden="true"></span>About</h3>
      <a href="mission.html">Mission</a>
      <a href="values.html">Values</a>
      <a href="testimonials.html">Testimonials</a>
      <a href="faq.html">FAQ</a>
      <a href="journal.html">Journal</a>
      <a href="blog.html">Blog</a>
    </nav>
    <nav class="footer-link-group footer-legal-links" aria-label="Legal">
      <h3><span class="footer-heading-icon" aria-hidden="true"></span>Legal</h3>
      <a href="legal.html">Legal</a>
      <a href="privacy.html">Privacy</a>
      <a href="cookies.html">Cookies</a>
      <a href="accessibility.html">Accessibility</a>
      <a href="sitemap.html">Sitemap</a>
    </nav>
    <div class="footer-contact" aria-label="Contact">
      <h3><span class="footer-heading-icon" aria-hidden="true"></span>Contact</h3>
      <a href="https://wa.me/5543991043536" rel="noopener" target="_blank">WhatsApp: (43) 9 9104-3536</a>
      <a href="mailto:sofiatimendonca@gmail.com">sofiatimendonca@gmail.com</a>
      <a href="https://www.instagram.com/fransofiati_biomedica/" rel="noopener" target="_blank">@fransofiati_biomedica</a>
      <span>Londrina, PR</span>
    </div>
    <div class="footer-bottom-row">
      <p>Information on this website is educational and does not replace an individual professional evaluation.</p>
      <p>2026 Franciele Sofiati. All rights reserved.</p>
    </div>
  </div>
</footer>
`;
}

function patchConceptRuntime(profile) {
  const refs = generatedAssetRefs(profile, "../../");
  const cssRefs = generatedAssetRefs(profile, "../../../");
  const dir = path.join(root, "concepts", profile.siteId);
  writeFileIfChanged(path.join(dir, "partials", "header.html"), headerPartial(profile, refs));
  writeFileIfChanged(
    path.join(dir, "partials", "mobile-menu.html"),
    mobileMenuPartial(profile, refs),
  );
  writeFileIfChanged(path.join(dir, "partials", "footer.html"), footerPartial(profile, refs));
  writeFileIfChanged(
    path.join(dir, "partials", "floating-whatsapp.html"),
    `<a class="floating-whatsapp floating-whatsapp-${profile.number}" href="https://wa.me/5543991043536" target="_blank" rel="noopener" aria-label="Open WhatsApp contact with Franciele Sofiati"><img src="${refs.icons.whatsapp}" alt="" aria-hidden="true"><b>Message Franciele on WhatsApp</b></a>\n`,
  );
  writeFileIfChanged(
    path.join(dir, "partials", "back-to-top.html"),
    `<button class="back-to-top back-to-top-${profile.number}" type="button" data-back-to-top aria-label="Return to the top of the page" aria-hidden="true" tabindex="-1"><img src="${refs.icons.backToTop}" alt="" aria-hidden="true"></button>\n`,
  );
  writeFileIfChanged(
    path.join(dir, "partials", "consultation-form.html"),
    `<section class="consultation-form-shell consultation-form-shell-${profile.number}" data-form-route="consultation" data-layout-signature="${profile.siteId}-consultation-form-${directions[profile.index % directions.length]}"><img src="${refs.forms.consultationForm}" alt="" aria-hidden="true"><form><label>Name<input name="name" autocomplete="name"></label><label>Message<textarea name="message"></textarea></label><button type="submit">Request evaluation</button></form></section>\n`,
  );
  writeFileIfChanged(
    path.join(dir, "partials", "contact-card.html"),
    `<aside class="contact-card contact-card-${profile.number}" data-layout-signature="${profile.siteId}-contact-panel-${directions[profile.index % directions.length]}"><img src="${refs.forms.contactPanel}" alt="" aria-hidden="true"><p>Contact Franciele Sofiati for evaluation-first aesthetic guidance.</p><a href="https://wa.me/5543991043536" rel="noopener" target="_blank">WhatsApp</a><img class="contact-card-accent" src="${refs.decorative.botanical}" alt="" aria-hidden="true"></aside>\n`,
  );
  writeFileIfChanged(
    path.join(dir, "partials", "head.html"),
    `<title>{{TITLE}}</title>
<meta name="description" content="{{DESCRIPTION}}">
<link rel="canonical" href="{{CANONICAL}}">
<meta property="og:title" content="{{TITLE}}">
<meta property="og:description" content="{{DESCRIPTION}}">
<meta property="og:image" content="${refs.social.openGraph}">
<meta name="theme-color" content="${palette(profile)[0]}">
<link rel="icon" href="${refs.logos.favicon}" type="image/svg+xml">
<link rel="apple-touch-icon" href="${refs.social.appleTouch}">
`,
  );

  const cssFile = path.join(dir, "css", "style.css");
  if (fs.existsSync(cssFile)) {
    let css = fs.readFileSync(cssFile, "utf8");
    const replacements = new Map([
      ["../assets/brand/sofiati-monogram-white.png", cssRefs.logos.watermark],
      ["../assets/brand/sofiati-monogram-bronze.png", cssRefs.logos.watermark],
      ["../assets/backgrounds/botanical-background.svg", cssRefs.backgrounds.home],
      ["../assets/botanical/gold-leaf-divider.svg", cssRefs.decorative.goldDivider],
      ["../assets/textures/soft-skin-texture.svg", cssRefs.decorative.texture],
      ["../assets/forms/consultation-form-frame.svg", cssRefs.forms.consultationForm],
      ["../assets/generated/homepage-asset-composition.svg", cssRefs.sectionAssets.generated],
      ["../assets/journal/journal-thumbnail-1.svg", cssRefs.journal.blogCard],
      ["../assets/journal/journal-thumbnail-2.svg", cssRefs.journal.featuredArticle],
      ["../assets/journal/journal-thumbnail-3.svg", cssRefs.journal.articleHeader],
      ["../assets/service/care-service-visual.svg", cssRefs.icons.care],
      ["../assets/service/laser-service-visual.svg", cssRefs.icons.laser],
      ["../assets/service/skin-service-visual.svg", cssRefs.icons.skin],
      ["../assets/service/results-service-visual.svg", cssRefs.cards.result],
      ["../assets/textures/clinical-paper-texture.svg", cssRefs.brandBackgrounds.textured],
      ["../assets/backgrounds/mobile-menu-background.svg", cssRefs.navigation.mobileMenuBackground],
      ["../assets/brand/footer-signature-watermark.png", cssRefs.footer.watermark],
    ]);
    for (const [from, to] of replacements) css = css.replaceAll(from, to);
    css += `
/* Generated asset bridge for ${profile.siteId}. */
.public-footer-${profile.number} {
  background-image: url("${cssRefs.footer.background}");
  background-size: cover;
  background-position: center;
}
.public-footer-${profile.number} .public-footer-watermark {
  position: absolute;
  inset: auto 5% 10% auto;
  width: min(260px, 34vw);
  opacity: .16;
  pointer-events: none;
}
.public-header-${profile.number} .public-brand-mark img,
.public-menu-${profile.number} .public-brand-mark img,
.public-footer-${profile.number} .footer-signature-logo img {
  max-width: min(220px, 50vw);
  height: auto;
}
`;
    writeFileIfChanged(cssFile, css);
  }

  const mainFile = path.join(dir, "js", "main.js");
  if (fs.existsSync(mainFile)) {
    let js = fs.readFileSync(mainFile, "utf8");
    js = js
      .replaceAll("assets/icons/whatsapp.svg", refs.icons.whatsapp)
      .replaceAll("assets/icons/back-to-top.svg", refs.icons.backToTop);
    writeFileIfChanged(mainFile, js);
  }
}

function removeConceptAssets() {
  const removed = [];
  for (const site of conceptSites()) {
    const assetDir = path.join(root, "concepts", site.siteId, "assets");
    if (fs.existsSync(assetDir)) {
      fs.rmSync(assetDir, { recursive: true, force: true });
      removed.push(path.relative(root, assetDir));
    }
  }
  return removed;
}

function main() {
  migrateBrandSources();
  if (fs.existsSync(generatedRoot))
    fs.rmSync(generatedRoot, { recursive: true, force: true });
  fs.mkdirSync(generatedRoot, { recursive: true });

  const photos = listFiles(photosDir, /\.(jpe?g|png|webp)$/i);
  const transparent = listFiles(brandDir, /transparent\.webp$/i);
  if (!photos.length) throw new Error("No source files found in assets/photos.");
  if (!transparent.length)
    throw new Error("No transparent source files found in assets/brand.");

  const brandSources = {
    logoSage: path.join(brandDir, "sofiati-logo-primary-sage.png"),
    logoBronze: path.join(brandDir, "sofiati-logo-primary-bronze.png"),
    logoWhite: path.join(brandDir, "sofiati-logo-primary-white.png"),
    monogram: path.join(brandDir, "sofiati-monogram-sage.png"),
    favicon: path.join(brandDir, "sofiati-favicon.svg"),
  };
  Object.entries(brandSources).forEach(([key, value]) => {
    if (!fs.existsSync(value)) {
      brandSources[key] = transparent[0];
    }
  });

  const manifests = [];
  for (const site of conceptSites()) {
    const profile = siteProfile(site);
    manifests.push(buildConceptAssets(profile, { photos, transparent }, brandSources));
    patchConceptRuntime(profile);
    process.stdout.write(`generated ${profile.siteId}\n`);
  }

  const removed = removeConceptAssets();
  const globalManifest = {
    generatedAt: new Date().toISOString(),
    totalConcepts: manifests.length,
    generatedRoot: "assets/generated",
    sourceFoldersUsed: ["assets/photos", "assets/brand"],
    absentSourceFolders: ["assets/brand-photos"],
    migratedBrandSources: sourceUsage.migratedBrandSources,
    photoSourcesUsed: [...sourceUsage.photoSources].sort(),
    transparentBrandSourcesUsed: [...sourceUsage.transparentBrandSources].sort(),
    conceptAssetFoldersRemoved: removed,
    totalGeneratedFiles: countFiles(generatedRoot),
    concepts: manifests.map((item) => ({
      siteId: item.siteId,
      visualDirection: item.visualDirection,
      sourcePhotos: item.sourcePhotos,
      transparentBrandSources: item.transparentBrandSources,
      generatedAssetCount: item.generatedAssets.length,
    })),
  };
  writeFileIfChanged(
    path.join(generatedRoot, "sofiati-generated-assets-manifest.json"),
    JSON.stringify(globalManifest, null, 2) + "\n",
  );
  console.log(
    `Generated ${globalManifest.totalGeneratedFiles} files and removed ${removed.length} concept asset folders.`,
  );
}

main();
