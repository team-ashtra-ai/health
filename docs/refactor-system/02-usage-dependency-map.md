# Usage and Dependency Map

Date: 2026-06-26

## Definitely Active

| Path / family | Classification | Evidence | Confidence |
| --- | --- | --- | --- |
| `concepts/*/*.html` | Live static pages | Root selector and sitemap link concept pages; every concept has 20 pages. | High |
| `concepts/*/css/style.css` | Live rendering CSS | Every sampled concept page links `css/style.css`. | High |
| `concepts/*/js/partials.js` | Live rendering JS | Every sampled concept page loads `js/partials.js`; it fetches partials and injects head/schema/mounts. | High |
| `concepts/*/js/main.js` | Live interaction JS | Every sampled concept page loads `js/main.js`; it controls floating widgets/back-to-top. | High |
| `concepts/*/assets/js/sofiati-footer-cookie.js` | Live cookie banner JS | Every sampled page loads it; prior ledger recorded 1000/1000 coverage. | High |
| `concepts/*/partials/*.html` | Live partials | `partials.js` fetches partials by name; pages mount them with `data-partial-mount`. | High |
| `concepts/*/assets/**` | Live local assets | HTML, partials and CSS reference local `assets/...` images, SVGs, icons and JS. | High |
| `index.html` | Public/root selector page | Links to all concept homepages; screenshot flow includes selector homepage. | High |
| `sitemap.xml` | SEO sitemap | Referenced by `robots.txt`. | High |
| `robots.txt` | Public crawler file | Points to root sitemap. | High |
| `docs/sofiati-task-ledger.md`, `docs/sofiati-master-brief.md`, `docs/current-task-brief.md` | Project control docs | Required by `AGENTS.md`. | High |
| `AGENTS.md` | Agent control doc | Contains required workflow instructions. | High |

## Probably Active

| Path / family | Classification | Evidence | Confidence |
| --- | --- | --- | --- |
| `select.html` | Alternate selector | Same link pattern as `index.html`; may be retained for selection workflow. | Medium |
| `README.md` | Maintenance doc | Local run instructions and script list, but script list is partially stale. | High |
| `llms.txt` | Machine-readable guidance | Root policy file; direct consumers unknown. | Medium |
| `data/concepts.json` | Concept metadata source | Contains all concept moods/layout seeds; likely used by missing or historical generation workflows and current planning. | High |
| `data/brand.json` | Brand/contact source | Stores approved contact/address policy; useful for scripts/docs. | High |
| `data/treatments.json` | Content/claim source | Contains treatment themes and claim policy. | High |
| `data/journal.json` | Blog/journal source | Draft outline source for educational content. | Medium |
| `css/brand-colours.css`, `css/brand-typography.css` | Brand token source/reference | Present as root CSS; direct page links not observed. | Medium |
| `assets/` | Shared source/reference assets | Root selector uses favicon; concept assets appear copied locally. | High |
| `brand identity/` | Original brand source files | Source/reference assets; many names are original Portuguese brand files. | High |

## Development-Only

| Path / family | Classification | Evidence | Confidence |
| --- | --- | --- | --- |
| `scripts/audit_static_site.py` | Audit report generator | Writes reports under `audit/reports/`. | High |
| `scripts/audit_internal_links.py` | Audit report generator | Writes `internal-link-validation.md`. | High |
| `scripts/audit_layout_signatures.py` | Audit report generator | Writes layout/design/UX reports. | High |
| `scripts/audit_ethics.py` | Audit report generator | Writes ethics and legal/contact reports. | High |
| `scripts/audit_public_partials.py` | Audit report generator | Writes public partial audit md/json. | High |
| `scripts/audit_rendered_concepts.py` | Rendered audit generator | Starts local server/Chrome and writes rendered responsive diagnostics. | High |
| `scripts/capture_header_footer_screenshots.py` | Screenshot generator | Regenerates `audit/screenshots/`. | High |
| `scripts/capture_homepage_screenshots.py` | Screenshot generator | Regenerates `final/homepage-screenshots/`. | High |
| `scripts/run_screenshot_design_qa.py` | Screenshot generator | Regenerates `audit/screenshots/design-qa/`. | High |
| `scripts/generate_agent_brief_system.py` | Documentation generator | Writes `docs/agent-brief-system/`. | High |
| `audit/reports/**` | Audit evidence | Current ledgers cite these reports. | High |
| `audit/screenshots/**` | Screenshot evidence | Current audits and issue register cite screenshot paths. | High |
| `final/homepage-screenshots/**` | Final screenshot evidence | README/script output and visual review evidence. | High |
| `docs/agent-system/**`, `docs/agent-brief-system/**` | Agent work system | Used by current ledger and future implementation workflow. | High |

## Archive Candidates

| Path / family | Reason | Evidence | Confidence |
| --- | --- | --- | --- |
| Older screenshot folders after regeneration | Useful historical QA evidence but bulky and generated. | Screenshot scripts can regenerate outputs but overwrite folders. | Medium |
| Superseded audit reports after a new full audit | Useful trail but may be stale after refactor. | Audit scripts write reports under stable filenames. | Medium |
| `data/translation-strings.json` and future translation reports | Generated inventory; not live rendering source. | `translate_pages.py` writes these files, but script currently imports missing source. | Medium |
| Old generated `docs/agent-brief-system/**` after a new generation | Generated from current evidence. | `generate_agent_brief_system.py` can refresh them. | Medium |
| `select.html` if root selector policy keeps only `index.html` | Possible duplicate selector. | Same selector structure as `index.html`; needs policy decision. | Low |

## Delete Candidates

| Path / family | Reason | Evidence | Confidence |
| --- | --- | --- | --- |
| `scripts/__pycache__/` | Python generated bytecode cache. | Contains `.pyc` files; can be regenerated by Python. | High |
| `scripts/__pycache__/*.pyc` for missing sources | Generated cache for absent source scripts. | `build_selector_pages.py`, `build_sofiati_asset_system.py`, `generate_concepts.py` are missing as `.py` but present as `.pyc`. | High |

## Unknown

| Path / family | Why unknown | Evidence | Confidence |
| --- | --- | --- | --- |
| Missing source generator history | README references `scripts/generate_concepts.py`, but source is absent. | `.pyc` exists; docs mention it. | High unknown |
| `scripts/translate_pages.py` | It imports missing `generate_concepts.py`; role may be stale or broken. | Source import line references missing module. | Medium |
| Root `css/` token files | Could be source/reference only or used by absent generation. | No direct concept page link observed. | Medium |
| `data/inspiration-sites.json` | Planning/reference role; direct consumers not confirmed. | Similar data family to concept inspiration references. | Medium |
| Some root data audit markdown files | Useful historical audits, not live rendering. | No direct live references observed. | Medium |

## Dependency Chains

- Page rendering chain: `concepts/{concept}/{page}.html` -> `css/style.css` -> local `assets/**`; page loads `js/partials.js`, `js/main.js`, `assets/js/sofiati-footer-cookie.js`.
- Partial chain: page `data-partial-mount` -> `js/partials.js` -> `partials/{name}.html` -> local assets and navigation templates.
- Navigation chain: `partials/header.html` slots -> `partials/navigation.html` templates -> `js/partials.js` current page highlighting.
- Mobile chain: `partials/mobile-menu.html` -> `data-menu-toggle`, `data-menu-close`, `#mobile-menu`, `data-lang-switch` -> concept CSS/JS behavior.
- Floating widget chain: `partials/floating-widgets.html` -> `partials/floating-whatsapp.html` and `partials/back-to-top.html` -> `js/main.js` normalization and scroll behavior -> icon assets.
- Cookie chain: `partials/cookie-banner.html` and page script tag -> `assets/js/sofiati-footer-cookie.js` -> concept CSS.
- Audit chain: source files -> audit scripts -> `audit/reports/**` and screenshot folders -> agent issue docs and task ledgers.
