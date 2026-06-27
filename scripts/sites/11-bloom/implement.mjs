#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  "siteId": "11-bloom",
  "siteName": "Bloom",
  "number": "11",
  "slug": "bloom",
  "index": 10,
  "dnaName": "Bloom Layered Botanical",
  "heroStrategy": "asymmetric portrait with small botanical proof mark",
  "sectionRhythm": "alternating portrait, cards, and statement pauses",
  "partialStrategy": "heroPlate, valueRail, serviceDiptych, journalRibbon, footerBridge",
  "mobileStrategy": "portrait stays first, CTAs stack, cards become compact rows",
  "motionStrategy": "small opacity and translate reveals only",
  "avoidNote": "generic split hero, boxed footer columns, heavy card grids",
  "primaryColor": "#485041",
  "accentColor": "#9A6B35",
  "surfaceColor": "#F2EEE3",
  "radius": 0,
  "rhythmOffset": 2,
  "imageRhythm": "portrait, icon, wide image, statement",
  "footerStrategy": "unboxed footer bridge with centered copyright",
  "mobileMenuStrategy": "sheet menu with large calm links"
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only")
});
