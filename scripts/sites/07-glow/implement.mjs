#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  "siteId": "07-glow",
  "siteName": "Glow",
  "number": "07",
  "slug": "glow",
  "index": 6,
  "dnaName": "Glow Soft Light Story",
  "heroStrategy": "lightbox portrait glow with low-pressure CTAs",
  "sectionRhythm": "soft glow blocks with generous negative space",
  "partialStrategy": "glowHero, lightboxCard, educationArc, contactGlow, footerHalo",
  "mobileStrategy": "lightbox media moves below copy and keeps buttons visible",
  "motionStrategy": "lightbox glow transition under 300ms",
  "avoidNote": "purple-blue gradients, dramatic promises, blurred backgrounds",
  "primaryColor": "#735C62",
  "accentColor": "#CDAA78",
  "surfaceColor": "#F7EFE8",
  "radius": 48,
  "rhythmOffset": 6,
  "imageRhythm": "wide image, portrait, compact icon, journal",
  "footerStrategy": "thin-rule footer index with no column boxes",
  "mobileMenuStrategy": "ledger menu with service route grouping"
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only")
});
