#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = {
  "siteId": "43-meridian",
  "siteName": "Meridian",
  "number": "43",
  "slug": "meridian",
  "index": 42,
  "dnaName": "Meridian Measured Journey",
  "heroStrategy": "soft full-bleed photo crop with quiet text margin",
  "sectionRhythm": "large image beats followed by airy text panels",
  "partialStrategy": "studioHero, portraitNote, serviceCards, formFrame, footerSignature",
  "mobileStrategy": "images crop to calm center points and text stays short",
  "motionStrategy": "soft image fade with no parallax requirement",
  "avoidNote": "text-heavy essays, fake proof, clinical coldness",
  "primaryColor": "#5F6E61",
  "accentColor": "#CDAA78",
  "surfaceColor": "#FFF9ED",
  "radius": 8,
  "rhythmOffset": 2,
  "imageRhythm": "cutout, service visual, texture, form frame",
  "footerStrategy": "signature footer note with open route list",
  "mobileMenuStrategy": "portrait-accent menu with short support routes"
};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only")
});
