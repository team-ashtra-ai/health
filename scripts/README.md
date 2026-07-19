# Scripts guide

Run commands from the repository root. Prefer the npm aliases below; they group the correct underlying tools and make the release workflow portable.

## Daily commands

| Command | Purpose |
| --- | --- |
| `npm run check:assets` | Verify local HTML, CSS and partial asset references. |
| `npm run check:pt` | Verify English/PT-BR route, language, metadata and structural parity. |
| `npm run check:seo` | Verify discovery files and audit on-page SEO implementation. |
| `npm run check:analytics` | Verify consent-aware analytics and form hooks. |
| `npm run validate` | Run all deterministic source checks. |
| `npm run build` | Recreate the deployable `dist/` output. |
| `npm run release:check` | Validate, then build. Use before each deployment. |
| `npm run serve` | Serve the built `dist/` output locally. |
| `npm run seo:refresh` | Regenerate `robots.txt`/`sitemap.xml` and write the SEO maintenance report. |
| `npm run maintain:performance` | Run the weekly mobile performance sample and write recommendations. |

## Content and localization

```bash
python3 scripts/export-editable-bilingual-content.py
python3 scripts/apply-editable-bilingual-content.py --apply
python3 scripts/generate-portuguese-site.py
npm run check:pt
```

The export/apply pair creates one bilingual Word document with English and Brazilian Portuguese text in side-by-side editable columns. Review its preview before applying changes. Portuguese edits are written directly to the corresponding published PT-BR source; run the PT-BR generator afterwards so it records page-level Portuguese edits as manual overrides. Shared partials are regenerated from translation memory, so maintain recurring shared-interface wording in `data/translation/`.

## Search and analytics

Run `npm run seo:refresh` after changing public routes, indexability, canonical URLs or the canonical domain. It regenerates only discovery files and reports editorial issues; it does not invent marketing copy.

After generated HTML or PT-BR output changes, run:

```bash
python3 scripts/install-analytics.py
npm run check:analytics
```

The installer is idempotent and keeps analytics consent-gated.

## Performance

```bash
npm run perf:images
npm run perf:all
npm run perf:budget
npm run perf:ci
```

Use `npm run maintain:performance -- --full` before major releases. It removes its disposable `dist/` output when complete. Review generated `reports/` and `performance-reports/` before committing them.

`python3 scripts/weekly-performance-maintenance.py --safe-fixes` previews the only automated markup remediation. Add `--apply-safe-fixes` only after review; it is limited to missing intrinsic dimensions on local raster images.

## Direct tools

`generate-robots.py`, `generate-sitemap.py`, `check-seo-files.py`, `check-local-assets.py`, `check-seo-implementation.py`, `check-analytics-implementation.py`, `install-analytics.py` and `screenshot_manager.py` can be used directly when a focused check is more useful than the grouped npm command. Their names describe their scope; use `--help` for options.
