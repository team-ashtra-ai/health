#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  "siteId": "46-curate",
  "siteName": "Curate",
  "number": "46",
  "slug": "curate",
  "index": 45,
  "dnaName": "Curate Gallery System",
  "heroStrategy": "clinical index hero with trust note and image strip",
  "sectionRhythm": "matrix panels with measured service notes",
  "partialStrategy": "clinicalHero, evidencePanel, routeMatrix, faqBridge, footerLedger",
  "mobileStrategy": "matrix panels become numbered blocks with large touch targets",
  "motionStrategy": "ledger row highlight with no flashing",
  "avoidNote": "spreadsheet feeling, unsupported equipment claims",
  "primaryColor": "#4D5A63",
  "accentColor": "#A2AEA0",
  "surfaceColor": "#F8F7F2",
  "radius": 34,
  "rhythmOffset": 5,
  "imageRhythm": "portrait, icon, wide image, statement",
  "footerStrategy": "unboxed footer bridge with centered copyright",
  "mobileMenuStrategy": "sheet menu with large calm links"
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only")
});
