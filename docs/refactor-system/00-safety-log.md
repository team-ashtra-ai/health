# Refactor System Safety Log

Date: 2026-06-26

## Current Git State

- Current branch: `main`
- Status summary from `git status --short --branch`: `## main...origin/main [ahead 2, behind 1]`
- Working tree before this documentation pass: no modified/untracked paths were shown by the initial short status output.
- Safety recommendation: create a dedicated branch before implementation, for example `git switch -c refactor-system-poc-2026-06-26`, because `main` is both ahead of and behind `origin/main`.

## Initial Risks

- The branch has diverged from `origin/main`; broad refactors on `main` could make later reconciliation harder.
- There are 50 standalone concept sites with repeated structure but concept-specific styling. A global CSS/partial change can affect all 1000 concept HTML pages.
- The partial loader (`js/partials.js`) and floating-widget runtime (`js/main.js`) are active rendering infrastructure and should not be removed or rewritten casually.
- The screenshot folders are evidence, not disposable clutter. They should be archived only after replacement screenshots exist.
- Some scripts are audit-only, while others rewrite concept pages, partials, CSS, docs, or generated screenshot folders. Unknown scripts must be read before running.
- The root script documentation references source scripts that are not currently present as `.py` files, while their compiled `.pyc` files remain in `scripts/__pycache__`.
- Legal, medical, beauty, treatment, testimonial, result, privacy, cookie and accessibility copy requires human review for anything beyond obvious formatting or approved labels.

## Do Not Delete Without Human Approval

- `concepts/` and all concept HTML, CSS, JS, partials, assets and planning docs.
- `assets/` and `brand identity/`, because they are source/reference brand assets.
- `data/`, especially `brand.json`, `concepts.json`, `treatments.json`, `journal.json`, and Instagram research files.
- `docs/`, including agent systems, master brief, current task brief, task ledger and concept briefs.
- `audit/`, including reports and screenshots, until replacement audit evidence exists.
- `final/`, including homepage screenshots, manifests and any translation reports, until replacement output exists.
- `scripts/`, except generated cache files after approval and verification.
- `sitemap.xml`, `robots.txt`, `index.html`, `select.html`, `README.md`, and `llms.txt`.

## Scripts Requiring Inspection Before Running

- Source-writing or broad-modifying scripts:
  - `scripts/sofiati_complete_system.py`
  - `scripts/restore_global_widgets.py`
  - `scripts/repair_screenshot_design_qa.py`
  - `scripts/refactor_public_partials.py` when run with `--apply`
  - `scripts/refactor_sofiati_cookie_notices.py` when run with `--apply`
  - `scripts/run_agent_audit_pipeline.py` when run with `--fix-safe-labels`
- Output-regenerating scripts:
  - `scripts/capture_homepage_screenshots.py`
  - `scripts/capture_header_footer_screenshots.py`
  - `scripts/run_screenshot_design_qa.py`
  - `scripts/audit_rendered_concepts.py`
  - `scripts/generate_agent_brief_system.py`
- Potentially broken or obsolete script path:
  - `scripts/translate_pages.py`, because it imports missing `generate_concepts.py`.

## Rules For This Batch

- No files are deleted.
- No files are moved.
- No unknown scripts are run.
- No concept implementation files are refactored.
- No global CSS or JS behavior changes are made.
- This batch may add planning documentation and update `docs/sofiati-task-ledger.md` only.
