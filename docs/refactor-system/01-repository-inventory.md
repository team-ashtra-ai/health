# Repository Inventory

Date: 2026-06-26

## Inventory Summary

- Root contains: `.git`, `.gitignore`, `AGENTS.md`, `README.md`, `assets/`, `audit/`, `brand identity/`, `concepts/`, `css/`, `data/`, `docs/`, `final/`, `index.html`, `llms.txt`, `robots.txt`, `scripts/`, `select.html`, `sitemap.xml`.
- Concept folders: 50 folders from `concepts/01-inspire` through `concepts/50-sovereign`.
- Per concept structure: 20 HTML pages, 15 partials, 1 concept CSS file, 2 concept JS files, 67 asset files, 6 planning docs.
- Total concept HTML files found: 1750.
- Total concept asset files found: 3350.
- Root tracked files count observed with `git ls-files`: 5998.

## Root Files

| Path | Purpose | Active / referenced evidence | Safe to edit | Safe to delete | Confidence |
| --- | --- | --- | --- | --- | --- |
| `index.html` | Root Sofiati website atlas linking to all 50 concept homepages. | Contains links to `concepts/*/index.html`; README tells users to open root. | Yes, narrow selector edits only. | No. | High |
| `select.html` | Duplicate or alternate selector atlas page. | Contains the same concept selector link pattern as `index.html`; final screenshot workflow captures selector homepage. | Yes, if selector policy is decided. | Unknown until root selector policy is confirmed. | Medium |
| `sitemap.xml` | Root XML sitemap for public URLs. | Referenced by `robots.txt`; includes root and concept pages. | Yes, with SEO audit. | No. | High |
| `robots.txt` | Search crawler policy and sitemap pointer. | Points to `https://www.sofiati.com/sitemap.xml`. | Yes, with SEO review. | No. | High |
| `README.md` | Human run instructions and repo overview. | Mentions local server and script commands; currently references missing `scripts/generate_concepts.py`. | Yes. | No. | High |
| `llms.txt` | Short machine-readable site guidance. | Contains site topic and no-private-address/no-guarantee warning. | Yes. | No. | Medium |
| `AGENTS.md` | Codex process instructions. | Requires reading ledger, master brief and current task brief first. | Only with explicit workflow approval. | No. | High |
| `.gitignore` | Git ignore policy. | Git control file. | Yes, narrow. | No. | High |
| `css/brand-colours.css` | Root brand color tokens. | Present as source/reference CSS; not directly linked from concept pages observed. | Yes, after checking root or generator use. | Unknown. | Medium |
| `css/brand-typography.css` | Root brand type tokens. | Present as source/reference CSS; not directly linked from concept pages observed. | Yes, after checking root or generator use. | Unknown. | Medium |
| `data/brand.json` | Brand facts, contact, domain, address policy and palette. | Referenced conceptually by docs/scripts; source of legal/contact facts. | Yes, only with approval. | No. | High |
| `data/concepts.json` | 50 concept metadata: mood, layout, header, mobile, footer, motion, source references. | Useful for selector/generated docs and layout matrix. | Yes, with full validation. | No. | High |
| `data/treatments.json` | Treatment categories and claim policy. | Supports content architecture and ethical copy. | Human-reviewed edits only. | No. | High |
| `data/journal.json` | Draft educational article topics. | Supports journal/blog planning. | Human-reviewed edits only. | No. | Medium |
| `data/translation-strings.json` | Generated translation inventory. | Written by `translate_pages.py`; role may be stale because generator source is missing. | Yes, generated-output rules. | Archive/investigate, not delete now. | Medium |
| `data/asset-usage-matrix.*` | Asset usage documentation/output. | Useful for asset verification. | Yes. | Archive candidate only after replacement. | Medium |
| `data/instagram/*` | Instagram research/source files. | README says Instagram material is research and content architecture only unless usage is confirmed. | Human-reviewed edits only. | No. | High |
| `docs/` | Project control docs, agent systems, briefs, ledgers, prompts, audits. | AGENTS requires task ledger/master/current briefs; user has related docs open. | Yes, task-scoped. | No. | High |
| `scripts/` | Audit, screenshot, generation, refactor and repair tooling. | Used by task ledger and audit system; scripts have mixed risk. | Yes, after inspection. | No except cache after approval. | High |
| `audit/` | Audit reports and screenshot evidence. | Current ledgers cite these reports and screenshots. | Yes, reports can be regenerated carefully. | Archive only after replacement. | High |
| `final/` | Final homepage screenshot review outputs and manifests. | README and screenshot scripts reference `final/homepage-screenshots/`. | Yes, generated-output rules. | Archive only after replacement. | High |
| `assets/` | Shared source/reference brand and page imagery. | Root selector uses favicon; concept assets appear copied locally. | Yes, asset-governed only. | No without asset audit. | High |
| `brand identity/` | Original brand identity files with spaces and Portuguese names. | Source/reference assets; not necessarily browser-linked. | Avoid unless organizing archive with approval. | No. | High |

## Concept Folder Baseline

Each concept folder contains:

- Pages: `index.html`, `about.html`, `care.html`, `laser.html`, `skin.html`, `results.html`, `journal.html`, `blog.html`, `consultation.html`, `contact.html`, `faq.html`, `testimonials.html`, `mission.html`, `values.html`, `privacy.html`, `cookies.html`, `accessibility.html`, `legal.html`, `sitemap.html`, `404.html`.
- Partials: `header.html`, `navigation.html`, `mobile-menu.html`, `footer.html`, `head.html`, `schema.html`, `consultation-form.html`, `contact-card.html`, `cookie-banner.html`, `floating-whatsapp.html`, `floating-widgets.html`, `back-to-top.html`, `accessibility.html`, `concept-switcher.html`, `status-banner.html`.
- CSS: `css/style.css`.
- JS: `js/partials.js`, `js/main.js`.
- Cookie JS: `assets/js/sofiati-footer-cookie.js`.
- Planning docs: `design-dna.md`, `page-flow-map.md`, `internal-link-map.md`, `asset-plan.md`, `asset-notes.md`, `design-notes.md`.
- Asset subfolders: `animations`, `backgrounds`, `botanical`, `brand`, `forms`, `generated`, `icons`, `images`, `journal`, `js`, `portrait`, `service`, `textures`.
- Legal pages present in every concept: `legal.html`, `privacy.html`, `cookies.html`, `accessibility.html`.
- Sitemap page present in every concept: `sitemap.html`.

## Concept Folder Inventory

| Concept | Path | Pages | Partials | CSS | JS | Assets | Docs | Screenshot evidence | Obvious inconsistencies / notes |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | --- | --- |
| 01 Inspire | `concepts/01-inspire` | 20 | 15 | 1 | 2 | 67 | 6 | `audit/screenshots/*/01-inspire-*`, `final/homepage-screenshots/*/concept-01-inspire-*` | High risk: desktop nav wraps at 1024 and footer copyright offset. |
| 02 Empower | `concepts/02-empower` | 20 | 15 | 1 | 2 | 67 | 6 | `02-empower` screenshots | Needs review: footer copyright offset. |
| 03 Enhance | `concepts/03-enhance` | 20 | 15 | 1 | 2 | 67 | 6 | `03-enhance` screenshots | High risk: language contrast/squeeze, footer decoration, copyright offset. |
| 04 Renew | `concepts/04-renew` | 20 | 15 | 1 | 2 | 67 | 6 | `04-renew` screenshots | Strong in current matrix; no active issue recorded. |
| 05 Elevate | `concepts/05-elevate` | 20 | 15 | 1 | 2 | 67 | 6 | `05-elevate` screenshots | High risk: header styling, footer decoration, copyright offset. |
| 06 Refine | `concepts/06-refine` | 20 | 15 | 1 | 2 | 67 | 6 | `06-refine` screenshots | High risk: nav wrapping and footer copyright offset. |
| 07 Glow | `concepts/07-glow` | 20 | 15 | 1 | 2 | 67 | 6 | `07-glow` screenshots | High risk: nav wrapping and footer copyright offset. |
| 08 Balance | `concepts/08-balance` | 20 | 15 | 1 | 2 | 67 | 6 | `08-balance` screenshots | Strong in current matrix; no active issue recorded. |
| 09 Radiance | `concepts/09-radiance` | 20 | 15 | 1 | 2 | 67 | 6 | `09-radiance` screenshots | Needs review: footer copyright offset. |
| 10 Essence | `concepts/10-essence` | 20 | 15 | 1 | 2 | 67 | 6 | `10-essence` screenshots | High risk: desktop header CTA missing, footer copyright offset. |
| 11 Bloom | `concepts/11-bloom` | 20 | 15 | 1 | 2 | 67 | 6 | `11-bloom` screenshots | High risk: decoration issue and rendered issue. |
| 12 Vital | `concepts/12-vital` | 20 | 15 | 1 | 2 | 67 | 6 | `12-vital` screenshots | Needs review: footer copyright offset. |
| 13 Poise | `concepts/13-poise` | 20 | 15 | 1 | 2 | 67 | 6 | `13-poise` screenshots | High risk: footer issue and rendered issue. |
| 14 Aura | `concepts/14-aura` | 20 | 15 | 1 | 2 | 67 | 6 | `14-aura` screenshots | Strong in current matrix; no active issue recorded. |
| 15 Clarity | `concepts/15-clarity` | 20 | 15 | 1 | 2 | 67 | 6 | `15-clarity` screenshots | High risk: footer issue and rendered issue. |
| 16 Grace | `concepts/16-grace` | 20 | 15 | 1 | 2 | 67 | 6 | `16-grace` screenshots | High risk: desktop nav wrap. |
| 17 Sculpt | `concepts/17-sculpt` | 20 | 15 | 1 | 2 | 67 | 6 | `17-sculpt` screenshots | Needs review: mobile/rendered issue and footer offset. |
| 18 Lumin | `concepts/18-lumin` | 20 | 15 | 1 | 2 | 67 | 6 | `18-lumin` screenshots | High risk: footer issue and rendered issue. |
| 19 Verda | `concepts/19-verda` | 20 | 15 | 1 | 2 | 67 | 6 | `19-verda` screenshots | Needs review: footer copyright offset. |
| 20 Halo | `concepts/20-halo` | 20 | 15 | 1 | 2 | 67 | 6 | `20-halo` screenshots | Strong in current matrix; no active issue recorded. |
| 21 Calm | `concepts/21-calm` | 20 | 15 | 1 | 2 | 67 | 6 | `21-calm` screenshots | Needs review: footer copyright offset. |
| 22 Precision | `concepts/22-precision` | 20 | 15 | 1 | 2 | 67 | 6 | `22-precision` screenshots | High risk: desktop nav wrap and footer offset. |
| 23 Ritual | `concepts/23-ritual` | 20 | 15 | 1 | 2 | 67 | 6 | `23-ritual` screenshots | Needs review: footer copyright offset. |
| 24 Signal | `concepts/24-signal` | 20 | 15 | 1 | 2 | 67 | 6 | `24-signal` screenshots | Needs review: footer copyright offset. |
| 25 Align | `concepts/25-align` | 20 | 15 | 1 | 2 | 67 | 6 | `25-align` screenshots | Needs review: footer copyright offset. |
| 26 Vivant | `concepts/26-vivant` | 20 | 15 | 1 | 2 | 67 | 6 | `26-vivant` screenshots | Needs review: footer copyright offset. |
| 27 Form | `concepts/27-form` | 20 | 15 | 1 | 2 | 67 | 6 | `27-form` screenshots | High risk: logo/rendered issue and footer offset. |
| 28 Pure | `concepts/28-pure` | 20 | 15 | 1 | 2 | 67 | 6 | `28-pure` screenshots | High risk: language/footer issues and desktop nav wrap. |
| 29 Solace | `concepts/29-solace` | 20 | 15 | 1 | 2 | 67 | 6 | `29-solace` screenshots | Needs review: footer copyright offset. |
| 30 Method | `concepts/30-method` | 20 | 15 | 1 | 2 | 67 | 6 | `30-method` screenshots | High risk: nav wrap at 1024/1366/1440 and footer offset. |
| 31 Evolve | `concepts/31-evolve` | 20 | 15 | 1 | 2 | 67 | 6 | `31-evolve` screenshots | High risk: nav wrapping and footer offset. |
| 32 Serene | `concepts/32-serene` | 20 | 15 | 1 | 2 | 67 | 6 | `32-serene` screenshots | Strong in current matrix; no active issue recorded. |
| 33 Elan | `concepts/33-elan` | 20 | 15 | 1 | 2 | 67 | 6 | `33-elan` screenshots | Needs review: footer copyright offset. |
| 34 Flora | `concepts/34-flora` | 20 | 15 | 1 | 2 | 67 | 6 | `34-flora` screenshots | Needs review: footer copyright offset. |
| 35 Atelier | `concepts/35-atelier` | 20 | 15 | 1 | 2 | 67 | 6 | `35-atelier` screenshots | Needs review: small footer copyright delta at 1024. |
| 36 Lumina | `concepts/36-lumina` | 20 | 15 | 1 | 2 | 67 | 6 | `36-lumina` screenshots | Needs review: footer copyright offset. |
| 37 Vellum | `concepts/37-vellum` | 20 | 15 | 1 | 2 | 67 | 6 | `37-vellum` screenshots | Needs review: footer copyright offset. |
| 38 Origin | `concepts/38-origin` | 20 | 15 | 1 | 2 | 67 | 6 | `38-origin` screenshots | Needs review: footer copyright offset. |
| 39 Kindred | `concepts/39-kindred` | 20 | 15 | 1 | 2 | 67 | 6 | `39-kindred` screenshots | Needs review: footer copyright offset. |
| 40 Noble | `concepts/40-noble` | 20 | 15 | 1 | 2 | 67 | 6 | `40-noble` screenshots | Strong in current matrix; no active issue recorded. |
| 41 Vista | `concepts/41-vista` | 20 | 15 | 1 | 2 | 67 | 6 | `41-vista` screenshots | Needs review: footer copyright offset. |
| 42 Softline | `concepts/42-softline` | 20 | 15 | 1 | 2 | 67 | 6 | `42-softline` screenshots | Strong in current matrix; no active issue recorded. |
| 43 Meridian | `concepts/43-meridian` | 20 | 15 | 1 | 2 | 67 | 6 | `43-meridian` screenshots | Needs review: footer copyright offset. |
| 44 Safeguard | `concepts/44-safeguard` | 20 | 15 | 1 | 2 | 67 | 6 | `44-safeguard` screenshots | Needs review: footer copyright offset. |
| 45 Silhouette | `concepts/45-silhouette` | 20 | 15 | 1 | 2 | 67 | 6 | `45-silhouette` screenshots | Needs review: footer copyright offset. |
| 46 Curate | `concepts/46-curate` | 20 | 15 | 1 | 2 | 67 | 6 | `46-curate` screenshots | High risk: nav wrap at 1024/1366/1440 and footer offset. |
| 47 Proof | `concepts/47-proof` | 20 | 15 | 1 | 2 | 67 | 6 | `47-proof` screenshots | Needs review: footer copyright offset. |
| 48 Signature | `concepts/48-signature` | 20 | 15 | 1 | 2 | 67 | 6 | `48-signature` screenshots | Strong in current matrix; no active issue recorded. |
| 49 Wisdom | `concepts/49-wisdom` | 20 | 15 | 1 | 2 | 67 | 6 | `49-wisdom` screenshots | Needs review: footer copyright offset. |
| 50 Sovereign | `concepts/50-sovereign` | 20 | 15 | 1 | 2 | 67 | 6 | `50-sovereign` screenshots | Strong in current matrix; no active issue recorded. |

## Shared Systems

### Partial Loading System

- Active files: each concept's `js/partials.js` and `partials/*.html`.
- Evidence: every sampled page mounts `status-banner`, `accessibility`, `header`, `mobile-menu`, `footer`, `floating-widgets`, `consultation-form` and `contact-card`; `partials.js` fetches partials and dispatches `sofiati:partials-ready`.
- Risk: changing mount names or partial filenames breaks all pages in that concept.

### Header, Navigation and Mobile Menu

- Active files: `partials/header.html`, `partials/navigation.html`, `partials/mobile-menu.html`, `css/style.css`, `js/main.js`.
- Evidence: `header.html` uses `data-navigation-slot`; `navigation.html` provides templates; mobile menu uses `#mobile-menu`, `data-menu-toggle`, `data-menu-close`, and language switcher buttons.
- Known risk: rendered diagnostics report nav wrapping and missing header CTA in several concepts.

### Footer

- Active files: `partials/footer.html`, `css/style.css`.
- Evidence: public footer partials contain main, trust, legal and contact link groups; audit docs cite footer label and copyright alignment checks.
- Known risk: footer boxes/circles and copyright offset are tracked issues.

### Cookie / Banner System

- Active files: `partials/cookie-banner.html`, `assets/js/sofiati-footer-cookie.js`, page script tags with `data-sofiati-cookie-loader`, `css/style.css`.
- Evidence: concept pages include `assets/js/sofiati-footer-cookie.js`; prior ledgers record 1000/1000 coverage.
- Risk: old/floating cookie variants should not be reintroduced.

### WhatsApp / Floating Widgets

- Active files: `partials/floating-widgets.html`, `partials/floating-whatsapp.html`, `partials/back-to-top.html`, `js/main.js`, `css/style.css`, `assets/icons/whatsapp.svg`, `assets/icons/back-to-top.svg`.
- Evidence: `main.js` ensures `[data-floating-tools]`, `.floating-whatsapp` and `[data-back-to-top]`.
- Risk: back-to-top visibility depends on scroll threshold and transition timing.

### Consultation Forms and Contact Cards

- Active files: `partials/consultation-form.html`, `partials/contact-card.html`, `css/style.css`, form and portrait assets.
- Evidence: page sections mount these partials; form action uses Formspree; contact cards include WhatsApp/email/Instagram routes.
- Risk: human review needed for consent/privacy wording and any claims.

### Head and Schema

- Active files: `partials/head.html`, `partials/schema.html`, `js/partials.js`, page body `data-page-*` metadata.
- Evidence: `partials.js` builds dynamic metadata and JSON-LD from body data, while static pages also include initial metadata.
- Risk: duplicate or conflicting metadata requires SEO/schema audit after edits.

### CSS Architecture

- Active files: each `concepts/*/css/style.css`.
- Evidence: every concept page links local `css/style.css`; styles include base components, concept-numbered selectors, responsive rules, header/menu/footer variants and floating widget CSS.
- Risk: CSS appears large and generated/mechanical in places; global class names inside per-concept CSS can create accidental sameness.

### JS Architecture

- Active files: each concept's `js/partials.js`, `js/main.js`, and `assets/js/sofiati-footer-cookie.js`.
- Evidence: pages load all three; `main.js` handles floating widgets; `partials.js` handles mounts and schema; cookie JS handles footer cookie bar.
- Risk: no bundler exists; each concept owns local copies, so a fix must be applied intentionally per concept or through inspected scripts.

### Screenshot and Audit Scripts

- Active files: `scripts/audit_*.py`, `scripts/capture_*.py`, `scripts/run_*audit*.py`, `scripts/run_screenshot_design_qa.py`.
- Evidence: ledger and audit reports reference these outputs; screenshots exist in `audit/` and `final/`.
- Risk: screenshot scripts delete and regenerate output folders.

### Data-Driven Generation Files

- Active/reference files: `data/*.json`, `scripts/sofiati_complete_system.py`, missing generator references in README/scripts README.
- Evidence: `data/concepts.json` has all 50 concept directions; README references `scripts/generate_concepts.py`, but source is missing.
- Risk: do not rebuild concepts from stale/missing generators.
