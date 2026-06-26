# Script Inventory

Date: 2026-06-26

Initial classifications came from reading script headers, entry points and write paths. During the `04-renew` proof-of-concept on 2026-06-26, the audit scripts below were run, `scripts/translate_pages.py` was repaired, and the translation runtime was applied only to `concepts/04-renew/js/main.js`.

## Source Scripts

| Script | Purpose | Safe to run | Audit-only or modifies files | Inputs | Outputs | Usage command if clear | Risk | Useful for refactor | Obsolete/archive candidate | Keep? |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `scripts/audit_static_site.py` | Generates page inventory, sitemap, planning, section, SEO, schema, alt text and final reports. | Yes, but it writes reports. | Audit-only outputs. | Concept files, docs via `sofiati_complete_system.py`. | `audit/reports/*.md`. | `python3 scripts/audit_static_site.py` | Low-medium. | Yes. | No. | Keep. |
| `scripts/audit_internal_links.py` | Audits required internal links and anchor risks. | Yes, writes report. | Audit-only output. | Concept HTML. | `audit/reports/internal-link-validation.md`. | `python3 scripts/audit_internal_links.py` | Low. | Yes. | No. | Keep. |
| `scripts/audit_layout_signatures.py` | Audits duplicate section-order/layout signatures and UX/design reports. | Yes, writes reports. | Audit-only outputs. | Concept HTML and attributes. | `global-duplicate-layout-audit.md`, `design-differentiation-audit.md`, `ux-storytelling-audit.md`. | `python3 scripts/audit_layout_signatures.py` | Low. | Yes. | No. | Keep. |
| `scripts/audit_ethics.py` | Audits ethical copy, contact and no-full-address rules. | Yes, writes reports. | Audit-only outputs. | Concept files. | `ethical-copy-audit.md`, `legal-accessibility-contact-audit.md`. | `python3 scripts/audit_ethics.py` | Low. | Yes, especially after copy edits. | No. | Keep. |
| `scripts/audit_public_partials.py` | Audits public header/mobile/footer/screenshot evidence. | Yes, writes md/json audit files. | Audit-only outputs. | Header/menu/footer/status/accessibility partials and screenshot manifest. | `audit/header-menu-footer-screenshot-audit.md`, `.json`. | `python3 scripts/audit_public_partials.py` | Low-medium. | Yes. | No. | Keep. |
| `scripts/audit_rendered_concepts.py` | Browser-rendered responsive diagnostics across 50 homepages and 6 viewport widths. | Yes after browser/server readiness; writes reports. | Audit-only outputs. | Local server, Chrome/Chromium, concept pages. | `audit/reports/rendered-responsive-diagnostic.*`. | `python3 scripts/audit_rendered_concepts.py` | Medium. | Yes, critical for responsive refactor. | No. | Keep. |
| `scripts/capture_header_footer_screenshots.py` | Captures combined header/menu/footer screenshots for all concepts. | Yes, but overwrites `audit/screenshots/`. | Regenerates screenshot outputs. | Local server, Chrome/Chromium. | `audit/screenshots/**`, contact sheets, manifest. | `python3 scripts/capture_header_footer_screenshots.py` | Medium-high because it deletes and recreates screenshot output. | Yes after visual edits. | No. | Keep. |
| `scripts/capture_homepage_screenshots.py` | Captures selector and all concept homepage screenshots. | Yes, but overwrites `final/homepage-screenshots/`. | Regenerates screenshot outputs. | Local server, Chrome/Chromium. | `final/homepage-screenshots/**`. | `python3 scripts/capture_homepage_screenshots.py` | Medium-high because it deletes and recreates final screenshot output. | Yes after homepage edits. | No. | Keep. |
| `scripts/run_screenshot_design_qa.py` | Captures home/care/laser/skin/results QA screenshots and contact sheets. | Yes, but overwrites `audit/screenshots/design-qa/`. | Regenerates screenshot outputs. | Local server, Chrome/Chromium, Pillow if available for sheets. | `audit/screenshots/design-qa/**`. | `python3 scripts/run_screenshot_design_qa.py` | Medium-high. | Yes after section/page refactors. | No. | Keep. |
| `scripts/generate_agent_brief_system.py` | Generates concept briefs, issue register, uniqueness matrix and ledgers. | Yes with caution; writes docs. | Modifies generated docs. | Concepts, screenshots, rendered diagnostics. | `docs/agent-brief-system/**`. | `python3 scripts/generate_agent_brief_system.py` | Medium. | Yes after audits, but can overwrite hand notes. | No. | Keep. |
| `scripts/run_agent_audit_pipeline.py` | Runs audits, screenshots and review report. Optional safe label fixes. | Yes only with no source-fix flags; use skips intentionally. | Default writes reports/screenshots; `--fix-safe-labels` modifies source labels. | Audit/screenshot scripts. | `audit/reports/agent-pipeline-review.md`, reports/screenshots. | `python3 scripts/run_agent_audit_pipeline.py --skip-screenshots` for lighter audit. | Medium-high; high with `--fix-safe-labels`. | Yes after batches. | No. | Keep. |
| `scripts/refactor_public_partials.py` | Footer/header public partial variation refactor tool. | Dry run only by default; `--apply` requires approval. | Modifies footer partials/CSS with `--apply`; writes audit. | Concept folders. | Footer partials, CSS, `audit/footer-variation-audit.md`. | Dry run: `python3 scripts/refactor_public_partials.py`; apply only with approval. | High with `--apply`. | Maybe, but concept uniqueness must be manually reviewed. | No. | Keep. |
| `scripts/refactor_sofiati_cookie_notices.py` | Refactors footer cookie bar system. | Dry run only by default; `--apply` requires approval. | Modifies HTML/CSS/JS and writes audit with `--apply`. | Concept folders. | Concept pages/assets/CSS and `audit/footer-cookie-bar-audit.md`. | Dry run: `python3 scripts/refactor_sofiati_cookie_notices.py`; apply only with approval. | High with `--apply`. | Useful only for cookie-specific work. | No. | Keep. |
| `scripts/restore_global_widgets.py` | Restores floating widgets and themed cookie loaders across all concepts. | No for this task; source-modifying broad script. | Modifies all concept `main.js`, HTML, partial labels and cookie JS. | All concept folders. | Concept JS/HTML/partials/assets JS. | Do not run unless explicitly approved. | High. | Historical/proven for widget restoration, not layout refactor. | No. | Keep. |
| `scripts/repair_screenshot_design_qa.py` | Repairs service/result hero systems based on screenshot QA. | No for this task; source-modifying broad script. | Modifies care/laser/skin/results pages and reports/ledger. | All concept service pages. | Concept HTML and audit docs. | Do not run unless explicitly approved. | High. | Historical repair script; inspect before reuse. | Maybe archive later only if replaced. | Keep. |
| `scripts/sofiati_complete_system.py` | Broad durable work system and static-site repair pass. | No for this task; broad source/doc generator. | Modifies docs, planning, sitemaps, HTML, CSS and reports. | Existing concepts and optional master attachment. | Many docs/pages/CSS/reports. | Do not run unless explicitly approved. | Very high. | Reference/audit functions are imported by audit scripts; full main is risky. | No. | Keep. |
| `scripts/translate_pages.py` | Builds the translation inventory and can install an optional EN/PT runtime while keeping English HTML as source of truth. | Yes in default report-only mode; runtime install is safe only with explicit scoped target. | Default writes translation data/reports; `--apply-runtime` modifies selected concept `js/main.js` files only. | Concept HTML/partials and existing translation memory. | `data/translation-strings.json`, `final/translation-report.json`, `final/translation-report.md`, optionally selected concept JS. | Report: `python3 scripts/translate_pages.py`; scoped runtime: `python3 scripts/translate_pages.py --concept 04-renew --apply-runtime`; broad rollout requires approval with `--all-concepts`. | Medium. | Yes for language-switcher rollout. | No. | Keep. |
| `scripts/README.md` | Script documentation. | Safe to edit. | Documentation. | Script list. | Markdown only. | N/A | Low. | Yes, update stale references. | No. | Keep. |

## Missing Source Scripts Mentioned By Docs

| Missing path | Evidence | Risk | Recommended action |
| --- | --- | --- | --- |
| `scripts/generate_concepts.py` | Referenced by `README.md`, `scripts/README.md`, `docs/agent-system/21-how-to-use-audit-docs-and-fix-workflow.md`; `.pyc` exists. `translate_pages.py` no longer imports it after the 2026-06-26 POC repair. | High if someone tries to rebuild concepts from README. | Investigate git history or restore/update docs; do not fake a replacement. |
| `scripts/build_selector_pages.py` | Mentioned by `scripts/README.md`; `.pyc` exists. | Low-medium. | Investigate whether selector generation is still needed. |
| `scripts/build_sofiati_asset_system.py` | `.pyc` exists but source absent. | Medium. | Investigate historical asset generation before deleting cache. |

## Generated Cache Files

| Path | Category | Safe to run/delete? | Notes |
| --- | --- | --- | --- |
| `scripts/__pycache__/` | Generated Python bytecode cache folder. | Do not run; delete only after approval. | Best delete candidate after approval. |
| `scripts/__pycache__/*.pyc` | Generated bytecode files. | Delete only after approval. | Some correspond to missing source and may be useful only as historical clues. |

## Safe Commands After Inspection

These are safe because they are audit/report-only or read-only, but they still write audit reports:

```bash
python3 scripts/audit_static_site.py
python3 scripts/audit_internal_links.py
python3 scripts/audit_layout_signatures.py
python3 scripts/audit_ethics.py
python3 scripts/audit_public_partials.py
python3 scripts/translate_pages.py
python3 scripts/translate_pages.py --concept 04-renew --apply-runtime
```

Use screenshot scripts only when you intend to replace screenshot output folders.

## Commands Not To Run Without Explicit Approval

```bash
python3 scripts/sofiati_complete_system.py
python3 scripts/restore_global_widgets.py
python3 scripts/repair_screenshot_design_qa.py
python3 scripts/refactor_public_partials.py --apply
python3 scripts/refactor_sofiati_cookie_notices.py --apply
python3 scripts/run_agent_audit_pipeline.py --fix-safe-labels
python3 scripts/translate_pages.py --all-concepts --apply-runtime
```
