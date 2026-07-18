# Franciele Sofiati website

Production repository for the bilingual Franciele Sofiati Biomédica website: a framework-free static publication focused on responsible aesthetic biomedicine, skin health, laser care and consultation-led treatment planning in Londrina, Paraná.

Current maintenance references: [architecture](docs/architecture.md), [content workflow](docs/content-workflow.md), [deployment](docs/deployment.md), and the [2026 cleanup audit](docs/repository-cleanup-audit.md). Detailed `docs/rebuild/` files are historical reference, not the current operating instructions.

- Canonical origin: `https://www.francielesofiati.com`
- Languages: English at `/`; Brazilian Portuguese at `/pt/`
- Public inventory: 19 paired indexable routes, 10 English Journal articles, localized policy pages, and dedicated `404` and post-form confirmation pages
- Runtime: semantic HTML, layered CSS, native JavaScript modules and shared HTML partials
- Discovery: canonical URLs, reciprocal `hreflang`, JSON-LD, Open Graph, `sitemap.xml`, `robots.txt` and a curated `llms.txt`

## Quick start

The shared interface is fetched at runtime, so use HTTP rather than opening files with `file://`.

```bash
python3 -m http.server 4173
```

Open `http://127.0.0.1:4173/`.

## Source-of-truth map

| Concern | Authoritative source | Generated or compiled output |
| --- | --- | --- |
| Standard English page content | `data/content-master.json` | Root English HTML pages |
| Standard English rendering | `scripts/render-english-site.py` | Semantic page bodies, metadata and JSON-LD |
| Final hand-authored pages | `404.html`, `consultation.html`, `contact.html`, `cookies.html` | Published directly; excluded from standard page regeneration |
| Journal publication | `posts/Franciele_Sofiati_Journal_10_Articles_Final.docx` and `scripts/build-journal.py` | `journal.html`, ten `journal/*.html` pages and article imagery |
| Shared interface | `partials/*.html` | Runtime header, navigation, footer, cookie banner and floating controls |
| Portuguese localization | English sources, translation memory and `scripts/generate-portuguese-site.py` | `pt/*.html` and `partials/pt-BR/*.html` |
| Language equivalents | `data/page-pairs.json` | Runtime language switching and sitemap route inventory |
| Interface messages | `data/interface-copy.json` | Localized form, filter and cookie feedback |
| Site identity and canonical origin | `data/seo.json` | SEO validation and generated discovery files |
| Styling | `css/src/` | `css/site.css` |
| Browser behavior | `js/main.js` and its modules | Native module runtime |
| Consent-aware measurement | `js/analytics-config.js`, `js/consent-manager.js`, `js/analytics.js` | Consent-gated GTM data layer and event tracking |
| Search discovery | `scripts/generate-sitemap.py` and `scripts/generate-robots.py` | `sitemap.xml` and `robots.txt` |
| LLM-oriented index | `llms.txt` | Curated public Markdown served at `/llms.txt` |

## Editing rules

Do not hand-edit generated English page bodies. For standard pages, change the content master or renderer and regenerate. For Journal content, update the authoritative article document or Journal renderer. The general English renderer deliberately excludes `journal.html` and the ten article pages.

Portuguese page text may be improved directly when necessary, but shared Portuguese interface wording belongs in the translation glossary, memory or explicit overrides because the generator rewrites `partials/pt-BR/`. Shared design or navigation changes belong in the English partials first.

Never publish private location details, invent clinical claims or convert educational content into individualized advice. Treatment suitability, settings, timing and outcomes must remain consultation-dependent.

Detailed maintenance guidance lives in [docs/rebuild/maintenance-guide.md](docs/rebuild/maintenance-guide.md), and the localization workflow is documented in [docs/PORTUGUESE_GENERATION.md](docs/PORTUGUESE_GENERATION.md).

## Build workflows

### Standard English pages and shared interface

```bash
python3 scripts/render-english-site.py --dry-run
python3 scripts/render-english-site.py --write
python3 scripts/build-shared-chrome.py
```

### Journal

```bash
python3 scripts/build-journal.py --write --assets
python3 scripts/build-journal.py --check
python3 scripts/check-journal.py
```

### Brazilian Portuguese

```bash
# Interactive: incremental generation, complete regeneration or dry run
python3 scripts/generate-portuguese-site.py
python3 scripts/check-portuguese-site.py --strict-warnings
```

Install the optional local translation environment with:

```bash
python3 -m venv .venv-argos
.venv-argos/bin/python -m pip install -r requirements-translation.txt
```

The first Argos Translate model installation requires network access. Later English-to-Portuguese runs are local. Each generation refreshes Portuguese partials, synchronizes page placeholders and validates language, structure, links, metadata and localized components.

### CSS

```bash
python3 scripts/build-css.py
python3 scripts/build-css.py --check
```

`python3 scripts/check-css-architecture.py --strict-unused` is the deeper CSS
debt audit. It intentionally reports the remaining legacy selector, token and
override violations and is not part of the passing release gate until that
separate cleanup is complete.

### Search and LLM discovery files

Always regenerate these files after adding, removing, renaming or substantially changing a public page:

```bash
python3 scripts/generate-robots.py
python3 scripts/generate-sitemap.py
python3 scripts/check-seo-files.py
```

The sitemap generator reads the canonical domain from `data/seo.json`, derives routes from `data/page-pairs.json`, excludes `noindex` pages, validates each canonical URL, preserves true language equivalence and emits accurate page-level `lastmod` dates. Journal articles remain English-only until one-to-one Portuguese translations exist.

`robots.txt` keeps all public pages and required render assets crawlable while discouraging crawling of repository source and QA paths. It is not access control. A deployment must exclude internal files rather than relying on crawler compliance.

`llms.txt` follows the community proposal's Markdown structure: one site H1, a concise summary, interpretation safeguards, curated canonical links and an `Optional` section. It complements rather than replaces the XML sitemap or robots policy.

### Analytics hooks

HTML and Portuguese regeneration can replace page-level tracking attributes.
Reinstall the consent-aware script block and explicit interaction hooks afterward:

```bash
python3 scripts/install-analytics.py
python3 scripts/check-analytics-implementation.py
```

The installer is idempotent. GA4 is delivered through GTM only, and GTM remains
inactive until analytics consent is granted. Account setup and placeholder
replacement are documented in
`GOOGLE-ANALYTICS-GTM-SEARCH-CONSOLE-SETUP.md`.

## Release validation

Run the fast deterministic release gate before every deployment:

```bash
python3 scripts/build-css.py --check
python3 scripts/render-english-site.py --dry-run
python3 scripts/build-journal.py --check
python3 scripts/build-shared-chrome.py --check
python3 scripts/check-journal.py
python3 scripts/check-portuguese-site.py --strict-warnings
python3 scripts/check-english-site.py
python3 scripts/check-local-assets.py
python3 scripts/check-seo-files.py
python3 scripts/install-analytics.py
python3 scripts/check-analytics-implementation.py
git diff --check
```

For interaction and layout QA:

```bash
node scripts/audit-interactions.cjs
python3 scripts/audit-responsive-layout.py
python3 scripts/capture_sitewide_responsive_screenshots.py
python3 scripts/screenshot_manager.py
```

`screenshot_manager.py` can target selected languages, routes, viewports, sections, selectors, IDs, hero regions, main content, final calls to action or footers. It stores each run under `screenshots/interactive/` with a machine-readable manifest.

## SEO architecture

- Every indexable HTML document declares one canonical URL, crawl directives, unique title and description, social metadata and structured data.
- English and Portuguese equivalents declare reciprocal `hreflang` values plus an English `x-default`.
- `404.html`, `thank-you.html` and their Portuguese equivalents use `noindex` and are deliberately absent from the sitemap.
- The root sitemap contains only absolute canonical HTTPS URLs. Google-ignored `priority` and `changefreq` fields are intentionally omitted.
- Sitemap `lastmod` dates come from the latest Git change for clean pages and the file modification date for uncommitted page changes.
- The current canonical host is `www.francielesofiati.com`. The apex host, HTTP variants and the eventual `*.pages.dev` production URL should permanently redirect to that host.
- If the final purchased domain differs, update the canonical origin everywhere before launch, regenerate all HTML and discovery files, and rerun the full release gate.

## Deployment boundary

Do **not** publish the repository root as the Cloudflare Pages output directory. It contains authoring documents, translation data, screenshots, references, backups, tests and QA reports that are not part of the public website.

A production artifact should allowlist only the runtime publication:

- Public root HTML pages, `pt/` and `journal/`
- `assets/`, the compiled `css/site.css`, runtime `js/`, `partials/` and browser-required `data/` files
- `favicon.ico`, `site.webmanifest`, `robots.txt`, `sitemap.xml` and `llms.txt`
- Cloudflare deployment controls such as `_headers` and `_redirects` once authored

Exclude source modules, authoring documents, translation caches, backups, screenshots, references, tests and reports. Build that clean artifact before connecting the custom domain.
