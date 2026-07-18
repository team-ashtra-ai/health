# Scripts guide

Run every command from the repository root. The scripts below are grouped by
purpose; anything not listed is an internal helper imported by one of these
commands and should not be run directly.

## Your normal publishing workflow

1. Export and edit English copy when needed:

   ```bash
   python3 scripts/export-editable-english-content.py
   python3 scripts/apply-editable-english-content.py --apply
   ```

2. Refresh the shared interface and Portuguese pages:

   ```bash
   python3 scripts/build-shared-chrome.py
   python3 scripts/generate-portuguese-site.py
   ```

3. Run the safe weekly SEO maintenance routine after page or SEO changes:

   ```bash
   python3 scripts/weekly-seo-maintenance.py
   ```

   It refreshes `robots.txt` and `sitemap.xml` (including each changed page's
   `lastmod` date), then audits metadata, canonical URLs, schema, and alt text.
   It reports issues but never invents or rewrites marketing copy.

   To apply the currently reviewed Portuguese metadata corrections reported by
   that audit, preview first and then apply them:

   ```bash
   python3 scripts/apply-seo-metadata-fixes.py
   python3 scripts/apply-seo-metadata-fixes.py --apply
   ```

4. Check a specific layout visually when needed:

   ```bash
   python3 scripts/screenshot_manager.py
   ```

5. Validate, build and save a checkpoint:

   ```bash
   npm run validate
   npm run build
   python3 scripts/git-save.py
   ```

   Add `--push` to `git-save.py` only when you want to push the new commit.

## Content and localization

| Script | Use it when |
| --- | --- |
| `export-editable-english-content.py` | You need a fresh Word document for editing English content. |
| `apply-editable-english-content.py` | You are ready to preview or apply edits from that Word document. |
| `build-journal.py` | The authoritative Journal Word document has changed. Use `--write --assets`. |
| `check-journal.py` | You changed Journal source or generated Journal pages. |
| `generate-portuguese-site.py` | English source content changed and Portuguese output needs refreshing. |
| `check-portuguese-site.py` | You need strict English/PT-BR parity verification. |
| `build-shared-chrome.py` | Shared partial placeholders need refreshing or checking. |

## Site generation and validation

| Script | Use it when |
| --- | --- |
| `build-css.py` | You changed CSS source. Run it, then rerun it with `--check`. |
| `build-production.mjs` | `npm run build` uses it to create the disposable deployable `dist/` output. |
| `serve-production.mjs` | `npm run serve` uses it to preview a production build. |
| `generate-robots.py` / `generate-sitemap.py` | Public routes, canonical URLs or SEO data changed. |
| `check-seo-files.py` | You need to confirm `robots.txt`, `sitemap.xml` and `llms.txt` are fresh. |
| `check-local-assets.py` | You changed HTML, CSS, partials or asset paths. |
| `check-seo-implementation.py` | You need the full SEO implementation report. |
| `weekly-seo-maintenance.py` | Your one-command weekly SEO refresh and audit; it does not edit page content. |
| `apply-seo-metadata-fixes.py` | Applies reviewed Portuguese metadata fixes to page, Open Graph, Twitter and translation-memory values. |
| `check-analytics-implementation.py` | You changed consent, analytics, forms or tracking attributes. |
| `install-analytics.py` | Generated or translated pages need the standard analytics block reinstalled. |

## Optional engineering checks

These are not needed for routine content edits. Node (`.mjs`) tools now live in
`scripts/build/` (production build and preview) and `scripts/performance/`
(asset, image, Lighthouse, PageSpeed, trace, budget and visual checks). Python
scripts in the root are the site's source generation and validation tools.

Their npm aliases are listed in `package.json` under `scripts`.
