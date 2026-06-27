#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  siteId: "40-noble",
  siteName: "Noble",
  number: "40",
  slug: "noble",
  index: 39,
  dnaName: "Noble Classic Register",
  heroStrategy: "minimal promise block with tactile texture",
  sectionRhythm: "quiet text-first sections with restrained media",
  partialStrategy:
    "minimalHero, quietStatement, measuredCards, finalNote, footerMinimal",
  mobileStrategy:
    "minimal pages remove decorative weight and keep final CTA visible",
  motionStrategy: "minimal focus ring and button state motion",
  avoidNote: "empty minimalism that removes guidance",
  primaryColor: "#3F4A45",
  accentColor: "#B7A06D",
  surfaceColor: "#F8F7F2",
  radius: 999,
  rhythmOffset: 7,
  imageRhythm: "journal thumbnail, portrait, service icon, texture",
  footerStrategy: "editorial footer bridge with contact emphasis",
  mobileMenuStrategy: "editorial menu with journal route emphasis",
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only"),
});
