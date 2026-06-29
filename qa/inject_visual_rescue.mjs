#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const conceptsRoot = path.join(root, "concepts");
const link =
  '<link rel="stylesheet" href="../../css/sofiati-visual-rescue.css">';

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
  if (file.includes(`${path.sep}partials${path.sep}`)) continue;

  let html = fs.readFileSync(file, "utf8");

  if (html.includes("sofiati-visual-rescue.css")) continue;

  if (html.includes("</head>")) {
    html = html.replace("</head>", `  ${link}\n</head>`);
  } else {
    html = `${link}\n${html}`;
  }

  fs.writeFileSync(file, html);
  changed++;
}

console.log(`Injected visual rescue CSS into ${changed} pages.`);
