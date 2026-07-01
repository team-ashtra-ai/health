# Sofiati 50 Premium Refactor Report

## Files Changed

- `scripts/rebuild_50_new_websites.py` now owns the 50-way creative matrix, page architecture, hero systems, layout families, card styles, media treatments, tablet/mobile behavior, plan, and registry generation.
- `scripts/generate_public_partial_systems.py` owns approved public chrome: header, mobile menu, footer, EN/PT links, cookie preferences, WhatsApp, accessibility, and back-to-top behavior.
- `css/sofiati-brand-foundation.css`, `js/sofiati-brand-foundation.js`, every `concepts/*/css/concept.css`, every `concepts/*/js/concept.js`, and the five generated partials per concept are the active frontend surface.
- `qa/audit_50_new_websites_compliance.py` validates the current `sf-theme-NN` public partial system.
- `qa/audit_50_new_websites_similarity.py` now evaluates visual profiles instead of stale selector overlap.
- `README.md`, `docs/sofiati-50-premium-refactor-plan.md`, and `docs/sofiati-50-concept-differentiation-registry.md` document the active refactor control plane.
- Obsolete atlas, visual-rescue, architecture-repair, duplicate root partial, and duplicate global CSS/JS files were removed so there is one current build path.

## Concepts Completed

- Concepts rebuilt: 50.
- Pages changed: 1050.
- Public partials regenerated: 250.
- Active concept file contract: 50 concept CSS files, 50 concept JS files, and 250 generated public partials.

## Major Design-System Changes

- Homepage hero sections now use dedicated markup with editorial, clinical, cinematic, concierge, minimal, luminous, botanical, and sculptural variants.
- Each concept has a stored layout family, hero pattern, card style, media treatment, CTA style, footer pattern, and mobile layout strategy.
- Tablet layouts keep multi-column compositions from 721px through 1024px before the phone layout takes over.
- Non-photo visual moments use intentional botanical/clinical CSS art panels rather than gray placeholders.
- The public partial system remains centralized and compatible with the full-site QA selectors.
- Palette generation is constrained to the Sofiati brand identity families: ivory, cream, sage, bronze, champagne, deep green, and ink.
- Cookie consent now supports accept, reject, customize, saved preferences, and localStorage persistence.
- Every generated page now includes one inline JSON-LD block in addition to canonical and social metadata.

## Before And After Design Logic

- Before: generated pages shared a regular section model and relied on color/order changes for differentiation.
- After: the first viewport, section rhythm, media treatment, and responsive behavior are generated from separate creative contracts per numbered concept.

## Commands Run

- `python3 qa/audit_50_new_websites_compliance.py`
- `python3 qa/audit_50_new_websites_similarity.py`
- `python3 scripts/audit_sofiati_full_site_qa.py`
- `python3 scripts/rebuild_50_new_websites.py`
- `python3 -m py_compile scripts/rebuild_50_new_websites.py scripts/generate_public_partial_systems.py scripts/audit_public_partial_systems.py scripts/audit_sofiati_full_site_qa.py qa/audit_50_new_websites_compliance.py qa/audit_50_new_websites_similarity.py qa/write_50_new_websites_final_report.py`
- `python3 scripts/audit_public_partial_systems.py`
- `python3 scripts/audit_public_partial_systems.py --render`
- `node --check scripts/audit_sofiati_render_matrix.mjs`
- `node scripts/audit_sofiati_render_matrix.mjs`
- `python3 qa/write_50_new_websites_final_report.py`

## Errors Found

- Baseline compliance failures: 0 after latest run.
- Baseline/latest similarity failures: 0.
- Public partial rendered failures: 0.
- Full-site static failures: 0.
- Full render matrix failures: 0.
- Cookie persistence failures: 0.

## Errors Fixed

- Stale compliance partial-specific checks were updated for current public partial ownership.
- Stale similarity gating was updated to compare visual profiles, not only repeated generator selectors.
- Rebuild no longer overwrites the approved public partial system with older partial markup.
- Generic home H1 replacement was removed so concept hero differentiation remains visible.
- Homepage hero media was corrected so CSS art overlays the portrait instead of increasing hero height.
- Removed obsolete concept-local `style.css`, `atlas-story.css`, `main.js`, `partials.js`, unused per-concept partials, root partials, and retired global component CSS/JS layers.
- Removed obsolete atlas, visual-rescue, premium visual DNA, and architecture-repair scripts/docs that could reintroduce conflicting frontend layers.
- Foundation JS now exposes helpers only; concept JS owns interactions behind a per-concept runtime guard to prevent duplicate listeners.
- EN/PT controls are real same-page links, active nav state strips query/hash, and mobile menu focus/Escape behavior is handled defensively.

## Errors Still Remaining

None in the final automated gates.

## Remaining Limitations

- Automated checks can confirm structure, overflow, links, assets, widgets, and uniqueness signals; final premium taste still benefits from human review of the generated screenshots.
