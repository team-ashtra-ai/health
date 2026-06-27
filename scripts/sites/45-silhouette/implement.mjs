#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  siteId: "45-silhouette",
  siteName: "Silhouette",
  number: "45",
  slug: "silhouette",
  index: 44,
  dnaName: "Silhouette Cutout Theater",
  heroStrategy: "salon-style portrait panel with bronze rule",
  sectionRhythm: "botanical dividers and salon-style quote frames",
  partialStrategy:
    "salonHero, botanicalDivider, softProcess, ctaSalon, footerSalon",
  mobileStrategy: "botanical accents reduce opacity and never block copy",
  motionStrategy: "botanical accent sway disabled for reduced motion",
  avoidNote: "rustic beige sameness, ornamental clutter, badge overload",
  primaryColor: "#403F36",
  accentColor: "#B88352",
  surfaceColor: "#F2EEE3",
  radius: 22,
  rhythmOffset: 4,
  imageRhythm: "journal thumbnail, portrait, service icon, texture",
  footerStrategy: "editorial footer bridge with contact emphasis",
  mobileMenuStrategy: "editorial menu with journal route emphasis",
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only"),
});
