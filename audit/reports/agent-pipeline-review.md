# Agent Audit Pipeline Review

Status: FAIL
Generated: 2026-06-26T17:16:19

## Scope
- Runs static audits, public-partial checks and screenshot capture scripts.
- Writes this review report for the next agent pass.
- Applies only deterministic public-label fixes when `--fix-safe-labels` is used.
- Does not auto-edit visual CSS/header/footer layout issues because concept uniqueness requires rendered review.

## Fix Mode
- `--fix-safe-labels`: off
- `--dry-run-fixes`: off
- Safe-fix files changed or proposed: 0

## Command Results

| Step | Result | Command |
| --- | --- | --- |
| Static site audit | PASS | `/usr/bin/python3 scripts/audit_static_site.py` |
| Internal link audit | PASS | `/usr/bin/python3 scripts/audit_internal_links.py` |
| Layout signature audit | PASS | `/usr/bin/python3 scripts/audit_layout_signatures.py` |
| Ethics/contact audit | FAIL 2 | `/usr/bin/python3 scripts/audit_ethics.py` |
| Header/footer/mobile-menu screenshots | PASS | `/usr/bin/python3 scripts/capture_header_footer_screenshots.py` |
| Design QA screenshots | PASS | `/usr/bin/python3 scripts/run_screenshot_design_qa.py` |
| Homepage screenshots | PASS | `/usr/bin/python3 scripts/capture_homepage_screenshots.py` |
| Public partial audit | PASS | `/usr/bin/python3 scripts/audit_public_partials.py` |

## Screenshot Manifests

| Set | Status | Count | Expected |
| --- | --- | --- | --- |
| Header/footer screenshots | present | 100 | 100 |
| Design QA screenshots | present | 500 | 500 |
| Homepage screenshots | present | 102 | 102 |

## Automated Issue Scan
- Footer Brand-label hits: 0
- Sitemap Brand-label hits: 0

## Human/Agent Review Queue
1. Open the contact sheets in `audit/screenshots/` and `audit/screenshots/design-qa/`.
2. Use `docs/agent-system/19-known-errors-and-regressions.md` for exact concept priorities.
3. Use `docs/agent-system/prompts/prompt-02-fix-header-nav.md` for header/nav fixes.
4. Use `docs/agent-system/prompts/prompt-03-fix-footer.md` for footer fixes.
5. Use `docs/agent-system/prompts/prompt-04-fix-language-switcher.md` for Concepts 3 and 28.
6. After implementation, rerun this script and update `docs/agent-system/20-implementation-task-ledger.md` plus `docs/sofiati-task-ledger.md`.

## Exit Guidance
- PASS means automated checks found no remaining known machine-detectable issue.
- FAIL means at least one audit command failed, a screenshot manifest is missing/incomplete, or Brand-label hits remain.
