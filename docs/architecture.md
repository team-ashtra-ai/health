# Architecture

The site is a static, framework-free publication. Public English pages live at the repository root; Brazilian Portuguese output lives under `pt/`; English Journal articles live under `journal/`.

- `partials/` and `partials/pt-BR/` contain runtime-loaded top bar, header, mobile menu, footer, cookie banner and floating widgets.
- `js/main.js` starts native modules for partial loading, navigation, consent, analytics, forms and page enhancements.
- `css/src/` is the authored stylesheet source. `scripts/build-css.py` concatenates its ordered manifest into the committed public `css/site.css`. Modules are ordered by foundation, layout, component, composition, page, then utility concerns; `pages/home-layout.css` is the single documented final authority for homepage layout.
- `data/` holds English content, navigation, language pair, SEO and translation inputs.
- `assets/` contains only published assets. Paths are public compatibility contracts; do not rename or deduplicate assets without updating every verified consumer.

`scripts/build/build-production.mjs` builds a deployable allowlisted `dist/` artifact. Do not deploy the repository root.

## Generated files

Current English HTML pages are the source of public page content. Edit them directly while preserving their page contracts, metadata, IDs and data attributes. Journal HTML is generated from the tracked Word source. Portuguese HTML and PT partials are generator output: change the translation inputs/overrides rather than making changes that a generation run will overwrite.

CSS source and the committed runtime stylesheet are kept in sync. After changing a source module, run `python3 scripts/build-css.py` and then `python3 scripts/build-css.py --check`.
