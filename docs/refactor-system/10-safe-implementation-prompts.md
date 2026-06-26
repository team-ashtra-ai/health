# Safe Implementation Prompts

Date: 2026-06-26

Use these prompts for future Codex sessions. Each prompt intentionally narrows scope.

## 1. Refactor One Proof-of-Concept Concept

```txt
Work inside /run/media/code/Storage/GitHub/ashtra/health. Follow AGENTS.md. Read docs/sofiati-task-ledger.md, docs/sofiati-master-brief.md, docs/current-task-brief.md, then docs/refactor-system/09-proof-of-concept-plan.md.

Refactor only concepts/04-renew as the first proof-of-concept. Do not edit any other concept except documentation/audit files required to report the work. Inspect existing 04-renew pages, partials, CSS, JS and screenshots first.

Goal: make 04-renew a stronger laser technology dossier concept while preserving ethical copy and all required pages. Scope: header/nav, mobile menu, homepage sections, laser.html, consultation/contact path, footer polish, responsive behavior. Preserve concept uniqueness and do not make it match other concepts.

Do not delete files. Do not run broad refactor scripts. Do not change medical/legal/beauty claims beyond obvious formatting without flagging for human review.

Verification: run targeted static/link/ethics checks if touched areas require them, run rendered/screenshot checks for 04-renew at desktop/mobile, confirm cookie/WhatsApp/back-to-top/form still work, update docs/sofiati-task-ledger.md and relevant refactor docs with results. Include rollback notes and final report.
```

## 2. Review Screenshots After Proof-of-Concept

```txt
Review only the screenshots and audit output from the 04-renew proof-of-concept. Do not edit source files unless I explicitly approve fixes. Compare before/after if available. Check desktop/mobile home, laser, consultation/contact, header, mobile menu, footer, cookie, WhatsApp and back-to-top. Report pass/fail, visual regressions, concept identity strength, responsive issues and exact files likely needing follow-up.
```

## 3. Apply Refactor Pattern To Next 5 Concepts

```txt
After the approved POC passes, refactor only the next approved five concepts. Inspect each concept first and preserve its unique matrix signature from docs/refactor-system/06-50-concept-layout-matrix.md. Do not apply one universal visual template. Keep scope to header/nav, mobile menu, homepage, one service page, consultation/contact path and footer for those five concepts only. Run verification and update ledgers after the batch.
```

## 4. Refactor Headers Only Across All Concepts

```txt
Inspect all concept headers, navigation templates and rendered nav-wrap issues first. Refactor headers only; do not change heroes, footers, service content or assets except where required for header rendering. Preserve unique header signatures per concept. Ensure desktop nav does not wrap at 1024/1366/1440 unless an intentional compact mode is documented. Run rendered diagnostics and screenshot header checks. Update docs/sofiati-task-ledger.md.
```

## 5. Refactor Mobile Menus Only

```txt
Inspect mobile-menu partials, status/language controls and current screenshots first. Refactor mobile menus only. Preserve concept-specific reveal behavior and menu mood. Fix language switcher contrast, close button visibility, overflow and touch target issues. Do not alter desktop headers, footers or page sections except CSS directly needed for mobile menu. Verify at 360, 390 and 768px and update docs/ledgers.
```

## 6. Refactor Footers Only

```txt
Inspect all footer partials, footer CSS and current footer screenshot/audit issues first. Refactor footers only. Preserve required footer link groups, approved contact details, legal links, disclaimer and concept-specific footer identity. Remove accidental boxes/circles/heavy card treatments where flagged. Fix copyright centering. Do not change headers/heroes/page copy. Verify with public partial audit, rendered diagnostics and footer screenshots. Update docs/ledgers.
```

## 7. Refactor Homepage Sections Only

```txt
Inspect homepage structure, design DNA, page-flow maps and screenshots first. Refactor homepage sections only for the approved concept or approved batch. Preserve all required content and ethical copy. Increase section rhythm diversity, image rhythm and CTA clarity without touching headers/footers except if required by layout overlap. Verify screenshots and static audits. Update docs/ledgers.
```

## 8. Refactor Service Pages Only

```txt
Inspect care.html, laser.html, skin.html and results.html for the approved concept or batch. Refactor service pages only. Keep evaluation-first, no-guarantee, no-diagnosis and no-before-after rules intact. Vary section order and image rhythm by concept. Do not change legal/medical claims beyond formatting without flagging for review. Verify static audits, link audits, ethics audit and screenshots.
```

## 9. Refactor Consultation / Contact Flow Only

```txt
Inspect consultation.html, contact.html, consultation-form partial, contact-card partial, form CSS and contact links first. Refactor only the consultation/contact path for the approved concept or batch. Preserve Formspree action, consent/privacy copy, WhatsApp/email/Instagram, and Londrina PR only. Verify form labels, focus states, route links, WhatsApp, privacy note and mobile layout. Update docs/ledgers.
```

## 10. Refactor SEO / Schema Only

```txt
Inspect page metadata, body data attributes, head/schema partials, sitemap.xml, concept sitemap pages and SEO/schema reports first. Refactor SEO/schema only. Do not change visible page design. Preserve no-full-address policy and avoid unsupported claims. Run SEO/schema/static/internal-link audits and update docs/ledgers.
```

## 11. Refactor Accessibility Only

```txt
Inspect accessibility partials, skip links, forms, buttons, language controls, mobile menus, focus states and rendered screenshots first. Refactor accessibility only. Do not change visual identity except where accessibility requires contrast, focus, target size or overlap fixes. Verify keyboard/focus behavior, reduced motion/large text if available, mobile menu dialog behavior and screenshots. Update docs/ledgers.
```

## 12. Archive Unused Files After Approval

```txt
Use docs/refactor-system/03-cleanup-manifest.md and docs/refactor-system/04-archive-plan.md. Do not delete anything. Archive only the specifically approved paths into _archive/refactor-cleanup/YYYY-MM-DD/ with a MANIFEST.md preserving original paths, reasons, verification and rollback. Run git status before and after. Do not archive source assets, concept files, docs or scripts unless explicitly approved.
```

## 13. Delete Approved Files After Verification

```txt
Delete only the exact paths I approve from docs/refactor-system/03-cleanup-manifest.md. Before deleting, run git status and list the paths. Delete no source files. Prefer deleting only generated cache such as scripts/__pycache__ after approval. Verify after deletion with git status and relevant audits. Update docs/sofiati-task-ledger.md with the cleanup record.
```

## 14. Final Full-Site Regression Audit

```txt
Run a final regression after approved refactor batches. Inspect docs first. Run static, internal-link, layout-signature, ethics/contact, public partial, rendered responsive and screenshot workflows as appropriate. Do not apply fixes automatically. Report failures with file paths and screenshots. Confirm cookie, WhatsApp, back-to-top, consultation form, headers, mobile menus, footers, SEO/schema and accessibility. Update docs/sofiati-task-ledger.md and final audit docs.
```
