# Sofiati Standalone Website Concepts

Static presentation for `www.sofiati.com`, built for Franciele Sofiati, Advanced Aesthetic Biomedicine, CRBM 6277, Londrina, PR.

## Purpose

This repository contains 50 self-contained Sofiati website concepts. Each concept is an English-first standalone static website with its own flat HTML pages, local CSS, local JavaScript, local partials, copied assets and design notes.

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
python3 scripts/generate_concepts.py
python3 scripts/translate_pages.py
python3 scripts/audit_static_site.py
python3 scripts/capture_homepage_screenshots.py
python3 scripts/capture_homepage_full_screenshots.py
python3 scripts/capture_concept_focus_screenshots.py
python3 scripts/git_add_commit_push.py
python3 scripts/git_empty_commit.py
```

- `generate_concepts.py` rebuilds the 50 standalone concepts.
- `translate_pages.py` creates a non-destructive English-source translation inventory.
- `audit_static_site.py` checks standalone structure, local links, ethical copy, service coverage, disclaimers, uniqueness markers, screenshots and tracked video files.
- `capture_homepage_screenshots.py` captures desktop and mobile homepages into `final/homepage-screenshots/`.
- `capture_homepage_full_screenshots.py` captures full-page homepage screenshots for all 50 concepts.
- `capture_concept_focus_screenshots.py` captures full-page and focused header/footer/hero/widget screenshots for all 50 concepts.
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

Every concept contains `index.html`, all required page files, `css/style.css`, `js/main.js`, `partials/`, `assets/` and `design-notes.md`.
