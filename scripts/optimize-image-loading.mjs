#!/usr/bin/env node
/**
 * One-time HTML image hygiene pass. The first meaningful image on each page is
 * promoted as the LCP candidate; all later images are lazy and decode async.
 * Intrinsic dimensions are retained (or added by the source template) to keep
 * layout stable. Re-run after adding a page or hero image.
 */
import { readdir, readFile, writeFile } from 'node:fs/promises';
const pages = (await readdir('.')).filter((f) => f.endsWith('.html'));
for (const file of pages) {
  let html = await readFile(file, 'utf8');
  const tags = [...html.matchAll(/<img\b[^>]*>/gi)];
  let promoted = false;
  for (const match of tags) {
    const original = match[0];
    let tag = original;
    const meaningful = /\balt\s*=\s*"(?!")([^"].*)"/i.test(tag) && !/aria-hidden\s*=\s*"true"/i.test(tag);
    if (meaningful && !promoted) {
      promoted = true;
      tag = tag.replace(/\sloading\s*=\s*"[^"]*"/i, '').replace(/\sfetchpriority\s*=\s*"[^"]*"/i, '');
      tag = tag.replace(/<img/i, '<img loading="eager" fetchpriority="high"');
    } else if (!/loading\s*=/i.test(tag) && !/aria-hidden\s*=\s*"true"/i.test(tag)) {
      tag = tag.replace(/<img/i, '<img loading="lazy"');
    }
    if (tag !== original) html = html.replace(original, tag);
  }
  await writeFile(file, html);
}
console.log(`Optimised image loading hints in ${pages.length} HTML pages.`);
