#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  siteId: "29-solace",
  siteName: "Solace",
  number: "29",
  slug: "solace",
  index: 28,
  dnaName: "Solace Gentle Retreat",
  heroStrategy: "magazine cover crop with service route tabs",
  sectionRhythm: "editorial chapter cards and magazine previews",
  partialStrategy:
    "magazineHero, articleFeature, serviceChapter, ctaSpread, footerMagazine",
  mobileStrategy:
    "journal previews become horizontal-scannable but readable cards",
  motionStrategy: "editorial card reveal by section order",
  avoidNote: "blog-template sameness and repeated thumbnail rhythm",
  primaryColor: "#694B43",
  accentColor: "#D1A771",
  surfaceColor: "#FBF5EC",
  radius: 96,
  rhythmOffset: 4,
  imageRhythm: "botanical divider, portrait, route card, footer mark",
  footerStrategy: "minimal legal route footer with botanical stamp",
  mobileMenuStrategy: "minimal menu with strong consultation action",
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only"),
});
