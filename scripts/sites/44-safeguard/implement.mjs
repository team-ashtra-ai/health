#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  "siteId": "44-safeguard",
  "siteName": "Safeguard",
  "number": "44",
  "slug": "safeguard",
  "index": 43,
  "dnaName": "Safeguard Trust Frame",
  "heroStrategy": "stacked editorial masthead with floating cutout",
  "sectionRhythm": "gallery cards that break into statement bands",
  "partialStrategy": "galleryHero, imagePause, cardSequence, trustBand, footerGallery",
  "mobileStrategy": "gallery cards stack with one visual anchor per viewport",
  "motionStrategy": "section rule draw-ins and calm focus states",
  "avoidNote": "stock-like image darkness, oversized hero-only layout",
  "primaryColor": "#586D73",
  "accentColor": "#9A6B35",
  "surfaceColor": "#F6F0E5",
  "radius": 14,
  "rhythmOffset": 3,
  "imageRhythm": "botanical divider, portrait, route card, footer mark",
  "footerStrategy": "minimal legal route footer with botanical stamp",
  "mobileMenuStrategy": "minimal menu with strong consultation action"
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only")
});
