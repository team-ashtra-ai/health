#!/usr/bin/env node
/* Convert oversized transparent quotation portraits to WebP and update references. */
import { readdir, readFile, writeFile } from 'node:fs/promises';
import path from 'node:path';
import sharp from 'sharp';
const dir = 'assets/quotations';
const files = (await readdir(dir)).filter((f) => /\.png$/i.test(f));
for (const file of files) {
  const src = path.join(dir, file);
  const out = src.replace(/\.png$/i, '.webp');
  await sharp(src).webp({ quality: 82, alphaQuality: 90, effort: 5 }).toFile(out);
  const oldRef = `assets/quotations/${file}`;
  const newRef = `assets/quotations/${path.basename(out)}`;
  const roots = ['.'];
  for (const root of roots) {
    const entries = (await readdir(root)).filter((f) => f.endsWith('.html') || f.endsWith('.css'));
    for (const entry of entries) {
      const p = path.join(root, entry);
      const html = await readFile(p, 'utf8');
      if (html.includes(oldRef)) await writeFile(p, html.split(oldRef).join(newRef));
    }
  }
}
console.log(`Converted ${files.length} quotation PNG assets to WebP.`);
