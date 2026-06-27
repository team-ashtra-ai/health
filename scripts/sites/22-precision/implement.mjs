#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  siteId: "22-precision",
  siteName: "Precision",
  number: "22",
  slug: "precision",
  index: 21,
  dnaName: "Precision Clinical Matrix",
  heroStrategy: "concierge letter opener with compact action rail",
  sectionRhythm: "ledger rows, narrow callouts, and concise routes",
  partialStrategy:
    "conciergeHero, routeLedger, compactCta, supportStrip, footerIndex",
  mobileStrategy:
    "routes collapse into touch-led ledger items with clear spacing",
  motionStrategy: "hover lifts under 4px with reduced-motion fallback",
  avoidNote: "sales funnel pressure, loud colors, duplicated four-card rhythm",
  primaryColor: "#6B5846",
  accentColor: "#A2AEA0",
  surfaceColor: "#F8F7F2",
  radius: 3,
  rhythmOffset: 5,
  imageRhythm: "wide image, portrait, compact icon, journal",
  footerStrategy: "thin-rule footer index with no column boxes",
  mobileMenuStrategy: "ledger menu with service route grouping",
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only"),
});
