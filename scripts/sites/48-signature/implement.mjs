#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  siteId: "48-signature",
  siteName: "Signature",
  number: "48",
  slug: "signature",
  index: 47,
  dnaName: "Signature Personal Mark",
  heroStrategy: "split balance grid with rounded image bracket",
  sectionRhythm: "balanced two-column sections with offset media",
  partialStrategy:
    "balanceHero, splitStep, routePair, trustSplit, footerBalance",
  mobileStrategy:
    "split layouts become single-flow stories with preserved order",
  motionStrategy: "split panels settle without layout shift",
  avoidNote: "symmetry that makes every page feel identical",
  primaryColor: "#505E54",
  accentColor: "#8F7955",
  surfaceColor: "#F6F4EA",
  radius: 64,
  rhythmOffset: 7,
  imageRhythm: "cutout, service visual, texture, form frame",
  footerStrategy: "signature footer note with open route list",
  mobileMenuStrategy: "portrait-accent menu with short support routes",
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only"),
});
