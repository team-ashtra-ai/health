#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const conceptsRoot = path.join(root, "concepts");

const badPhrases = [
  "pattern decoration",
  "home background",
  "section background",
  "texture decoration",
  "decorative asset",
  "CONCEPT-SPECIFIC HERO ASSET FOR HERO PROMISE",
  "CONCEPT-SPECIFIC",
  "hero asset for hero promise",
  "asset for hero promise",
  "decorative asset for",
  "background asset",
  "section asset",
];

function walk(dir) {
  if (!fs.existsSync(dir)) return [];
  const out = [];
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, item.name);
    if (item.isDirectory()) out.push(...walk(full));
    if (item.isFile() && item.name.endsWith(".html")) out.push(full);
  }
  return out;
}

let changed = 0;

for (const file of walk(conceptsRoot)) {
  let html = fs.readFileSync(file, "utf8");
  let next = html;

  for (const phrase of badPhrases) {
    next = next.split(phrase).join("");
    next = next.split(phrase.toUpperCase()).join("");
    next = next.split(phrase.toLowerCase()).join("");
  }

  next = next.replace(/\s{2,}/g, " ").replace(/>\s+</g, ">\n<");

  if (next !== html) {
    fs.writeFileSync(file, next);
    changed++;
  }
}

console.log(`Cleaned visible placeholder asset text in ${changed} files.`);
