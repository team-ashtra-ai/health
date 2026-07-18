#!/usr/bin/env node

import { mkdir, writeFile } from 'node:fs/promises';
import { resolve } from 'node:path';
import { createAssetInventory } from './asset-inventory.mjs';

function csvCell(value) {
  const text = Array.isArray(value) ? value.join(' | ') : String(value ?? '');
  return `"${text.replaceAll('"', '""')}"`;
}

async function main() {
  await mkdir(resolve('performance-reports'), { recursive: true });
  const inventory = await createAssetInventory();
  const headers = [
    'source_file',
    'format',
    'dimensions',
    'file_size_bytes',
    'transparency',
    'pages_used',
    'display_dimensions',
    'fold_context',
    'decorative_or_meaningful',
    'loading',
    'candidate_output_formats',
    'responsive_variants_required',
    'referenced'
  ];
  const rows = inventory.images.map((image) => [
    image.source,
    image.format,
    image.width && image.height ? `${image.width}x${image.height}` : '',
    image.bytes,
    image.transparency,
    image.pagesUsed,
    image.displayDimensions,
    image.foldContext,
    image.purpose,
    image.loading,
    image.candidateFormats,
    image.responsiveWidths,
    image.referenced
  ]);
  const csv = [
    headers.map(csvCell).join(','),
    ...rows.map((row) => row.map(csvCell).join(','))
  ].join('\n');
  await writeFile(resolve('reports/performance/image-audit.csv'), `${csv}\n`);
  await writeFile(
    resolve('performance-reports/asset-inventory.json'),
    `${JSON.stringify(inventory, null, 2)}\n`
  );
  process.stdout.write(
    `Wrote reports/performance/image-audit.csv for ${inventory.imageCount} images; `
    + `${inventory.referencedImageCount} are referenced by current HTML or CSS.\n`
  );
}

main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
