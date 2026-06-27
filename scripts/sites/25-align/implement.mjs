#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  "siteId": "25-align",
  "siteName": "Align",
  "number": "25",
  "slug": "align",
  "index": 24,
  "dnaName": "Align Modular Balance",
  "heroStrategy": "salon-style portrait panel with bronze rule",
  "sectionRhythm": "botanical dividers and salon-style quote frames",
  "partialStrategy": "salonHero, botanicalDivider, softProcess, ctaSalon, footerSalon",
  "mobileStrategy": "botanical accents reduce opacity and never block copy",
  "motionStrategy": "botanical accent sway disabled for reduced motion",
  "avoidNote": "rustic beige sameness, ornamental clutter, badge overload",
  "primaryColor": "#403F36",
  "accentColor": "#B88352",
  "surfaceColor": "#F2EEE3",
  "radius": 22,
  "rhythmOffset": 0,
  "imageRhythm": "journal thumbnail, portrait, service icon, texture",
  "footerStrategy": "editorial footer bridge with contact emphasis",
  "mobileMenuStrategy": "editorial menu with journal route emphasis"
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only")
});
