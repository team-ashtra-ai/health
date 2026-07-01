# Sofiati Standalone Website Concepts

Static presentation for `www.sofiati.com`, built for Franciele Sofiati, Advanced Aesthetic Biomedicine, CRBM 6277, Londrina, PR.

## Purpose

This repository contains 50 self-contained Sofiati website concepts. Each concept is an English-first standalone static website with its own flat HTML pages, one concept stylesheet, one concept script, generated public partials, copied assets and design notes.

## Run Locally

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/` or open any concept directly, for example:

```txt
http://localhost:8000/concepts/01-inspire/index.html
```

## Scripts

```bash
python3 scripts/rebuild_50_new_websites.py
python3 qa/audit_50_new_websites_compliance.py
python3 qa/audit_50_new_websites_similarity.py
python3 scripts/audit_public_partial_systems.py
python3 scripts/audit_sofiati_full_site_qa.py
python3 scripts/audit_public_partial_systems.py --render
python3 scripts/audit_sofiati_full_site_qa.py --render
python3 scripts/capture_homepage_full_screenshots.py
python3 scripts/capture_header_hero_footer_widgets.py --mode both --port 8001
python3 scripts/git_add_commit_push.py
python3 scripts/git_empty_commit.py
```

- `rebuild_50_new_websites.py` rebuilds all 50 concepts, 1050 pages, active page CSS/JS, schema, documentation, and generated public partials.
- `audit_50_new_websites_compliance.py` checks the current 50-site architecture, stale CSS/JS references, local links, copy constraints, and required partials.
- `audit_50_new_websites_similarity.py` checks concept differentiation signals.
- `audit_public_partial_systems.py` checks header, mobile menu, footer, language, cookie and floating-widget structure; `--render` runs browser checks across desktop, tablet, and mobile widths.
- `audit_sofiati_full_site_qa.py` checks every public page; `--render` runs the all-page browser matrix.
- `capture_homepage_full_screenshots.py` and `capture_header_hero_footer_widgets.py` create visual review evidence.
- `git_add_commit_push.py` stages all changes, commits them with a timestamped message, and pushes to the current remote.
- `git_empty_commit.py` creates and pushes an empty timestamped commit.

## Rules

- Keep all reviewed pages English-first.
- Use `Londrina, PR` only and do not publish private location details or map embeds.
- Do not invent testimonials, before-and-after claims, results, guarantees, cures or risk-free language.
- All treatment copy is educational until reviewed and approved by Franciele Sofiati.
- Instagram material is used for research and content architecture only unless client-owned usage is confirmed.

## Structure

```txt
/assets/                 Shared source/reference assets
/concepts/01-inspire/    Standalone concept website
/concepts/02-empower/    Standalone concept website
...
/concepts/50-sovereign/  Standalone concept website
/final/                  Audit, translation and screenshot review outputs
/scripts/                Build, translation, audit, screenshot and git helpers
```

Every concept contains `index.html`, all required page files, `css/concept.css`, `js/concept.js`, generated public partials, `assets/` and `design-notes.md`.

Current generated concepts use this active public architecture:

- `css/concept.css` for concept-specific layout, page rhythm and the appended public partial styles.
- `js/concept.js` for the concept runtime: mobile menu, active navigation, language links, cookie preferences, WhatsApp and back-to-top behavior.
- `partials/header.html`, `partials/mobile-menu.html`, `partials/footer.html`, `partials/cookie-banner.html` and `partials/floating-widgets.html`.
- Shared foundation files are limited to `css/sofiati-brand-foundation.css` and `js/sofiati-brand-foundation.js`.

Older `css/style.css`, `css/atlas-story.css`, `js/main.js`, `js/partials.js`, root partials, and standalone global component CSS/JS files are no longer active extension points.
