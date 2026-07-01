# Sofiati 50 Premium Refactor Plan

## Current Architecture Summary

- Concept folders found: 50.
- Real concept HTML pages found: 1050.
- Concept partial files found: 250.
- Concept-local CSS files found: 50.
- Concept-local JS files found: 50.
- Active pages load `../../css/sofiati-brand-foundation.css`, `css/concept.css`, `../../js/sofiati-brand-foundation.js`, and `js/concept.js`.
- The approved public partial system owns header, language switcher, mobile menu, footer, cookie banner, WhatsApp, accessibility, and back-to-top controls.
- The page generator owns the 21 HTML pages per concept and the concept-specific layout CSS before the public partial CSS block is appended.
- The active file contract is intentionally narrow: each concept keeps only `css/concept.css`, `js/concept.js`, and five public partials: `header.html`, `mobile-menu.html`, `footer.html`, `cookie-banner.html`, and `floating-widgets.html`.
- Shared global styling and scripting are limited to `css/sofiati-brand-foundation.css` and `js/sofiati-brand-foundation.js`.

## All 50 Concepts

- `01-inspire`: public folder retained; creative label Inspire; mood high-end editorial, botanical, quiet confidence; hero editorial-spread; layout editorial-asymmetric; cards fine-line; media portrait-atelier.
- `02-empower`: public folder retained; creative label Empower; mood precise, structured, confident, medical luxury; hero clinical-dashboard; layout clinical-grid; cards clinical-module; media clinical-crop.
- `03-enhance`: public folder retained; creative label Enhance; mood gentle, feminine, progress oriented; hero soft-layers; layout soft-journey; cards offset-soft; media soft-vellum.
- `04-renew`: public folder retained; creative label Renew; mood dramatic, restorative, cinematic; hero dark-cinematic; layout cinematic-immersive; cards cinematic-slate; media shadow-botanical.
- `05-elevate`: public folder retained; creative label Elevate; mood polished, private, high end; hero concierge-card; layout concierge-suite; cards concierge-ticket; media concierge-frame.
- `06-refine`: public folder retained; creative label Refine; mood intelligent, restrained, calm; hero quiet-minimal; layout minimal-clinical; cards minimal-rule; media quiet-negative.
- `07-glow`: public folder retained; creative label Glow; mood luminous, soft, beauty forward; hero radiance-glow; layout luminous-studio; cards luminous-card; media skin-light.
- `08-balance`: public folder retained; creative label Balance; mood grounded, natural, wellness clinical; hero balanced-split; layout balanced-pathway; cards calm-path; media balanced-window.
- `09-radiance`: public folder retained; creative label Radiance; mood confident, luminous, proof oriented; hero proof-route; layout route-led; cards proof-ledger; media contrast-proof.
- `10-essence`: public folder retained; creative label Essence; mood intimate, organic, refined; hero organic-paper; layout organic-editorial; cards paper-note; media organic-paper.
- `11-bloom`: public folder retained; creative label Aura; mood airy, luminous, delicate; hero aura-field; layout ethereal-panels; cards floating-pane; media mist-layer.
- `12-vital`: public folder retained; creative label Verda; mood botanical, fresh, grounded; hero garden-panel; layout botanical-garden; cards botanical-tile; media leaf-annotation.
- `13-poise`: public folder retained; creative label Luma; mood light, precise, modern; hero light-lab; layout light-science; cards light-cell; media lab-light.
- `14-aura`: public folder retained; creative label Seren; mood calm, private, soft spoken; hero private-note; layout private-serene; cards private-panel; media private-room.
- `15-clarity`: public folder retained; creative label Vitta; mood fresh, health forward, energetic but premium; hero vitality-board; layout vitality-pillars; cards health-pillar; media fresh-motion.
- `16-grace`: public folder retained; creative label Bloom; mood soft botanical growth; hero bloom-frame; layout botanical-bloom; cards petal-card; media bloom-outline.
- `17-sculpt`: public folder retained; creative label Poise; mood composed, poised, premium; hero portrait-confidence; layout poised-portrait; cards confidence-frame; media poised-portrait.
- `18-lumin`: public folder retained; creative label Clare; mood clean, transparent, direct; hero clarity-brief; layout clarity-led; cards clarity-row; media clean-cut.
- `19-verda`: public folder retained; creative label Natura; mood natural, subtle, trustworthy; hero natural-texture; layout natural-philosophy; cards natural-slip; media natural-fiber.
- `20-halo`: public folder retained; creative label Forma; mood structured, sculptural, precise; hero sculptural-form; layout sculptural-grid; cards sculpted-plate; media sculptural-plinth.
- `21-calm`: public folder retained; creative label Amara; mood warm, personal, inviting; hero editorial-spread; layout editorial-asymmetric; cards fine-line; media portrait-atelier.
- `22-precision`: public folder retained; creative label Celeste; mood airy, refined, spa editorial; hero clinical-dashboard; layout clinical-grid; cards clinical-module; media clinical-crop.
- `23-ritual`: public folder retained; creative label Olive; mood mature, grounded, premium; hero soft-layers; layout soft-journey; cards offset-soft; media soft-vellum.
- `24-signal`: public folder retained; creative label Rosea; mood warm, feminine, soft clinical; hero dark-cinematic; layout cinematic-immersive; cards cinematic-slate; media shadow-botanical.
- `25-align`: public folder retained; creative label Silka; mood silky, smooth, minimal; hero concierge-card; layout concierge-suite; cards concierge-ticket; media concierge-frame.
- `26-vivant`: public folder retained; creative label Alba; mood fresh, bright, optimistic; hero quiet-minimal; layout minimal-clinical; cards minimal-rule; media quiet-negative.
- `27-form`: public folder retained; creative label Noemi; mood boutique, personal, intimate; hero radiance-glow; layout luminous-studio; cards luminous-card; media skin-light.
- `28-pure`: public folder retained; creative label Flora; mood educational, botanical, calm; hero balanced-split; layout balanced-pathway; cards calm-path; media balanced-window.
- `29-solace`: public folder retained; creative label Siena; mood warm, earthy, premium; hero proof-route; layout route-led; cards proof-ledger; media contrast-proof.
- `30-method`: public folder retained; creative label Elan; mood modern, energetic, confident; hero organic-paper; layout organic-editorial; cards paper-note; media organic-paper.
- `31-evolve`: public folder retained; creative label Mira; mood reflective, elegant, confidence led; hero aura-field; layout ethereal-panels; cards floating-pane; media mist-layer.
- `32-serene`: public folder retained; creative label Solea; mood sunlit, warm, radiant; hero garden-panel; layout botanical-garden; cards botanical-tile; media leaf-annotation.
- `33-elan`: public folder retained; creative label Aria; mood light, breathable, sophisticated; hero light-lab; layout light-science; cards light-cell; media lab-light.
- `34-flora`: public folder retained; creative label Vale; mood earthy, calm, reassuring; hero private-note; layout private-serene; cards private-panel; media private-room.
- `35-atelier`: public folder retained; creative label Nobile; mood formal, luxurious, high end; hero vitality-board; layout vitality-pillars; cards health-pillar; media fresh-motion.
- `36-lumina`: public folder retained; creative label Brisa; mood soft, fresh, gentle; hero bloom-frame; layout botanical-bloom; cards petal-card; media bloom-outline.
- `37-vellum`: public folder retained; creative label Linha; mood precise, artistic, line based; hero portrait-confidence; layout poised-portrait; cards confidence-frame; media poised-portrait.
- `38-origin`: public folder retained; creative label Dama; mood feminine authority, refined; hero clarity-brief; layout clarity-led; cards clarity-row; media clean-cut.
- `39-kindred`: public folder retained; creative label Terra; mood organic, biological, grounded; hero natural-texture; layout natural-philosophy; cards natural-slip; media natural-fiber.
- `40-noble`: public folder retained; creative label Prisma; mood modern, clear, multi service; hero sculptural-form; layout sculptural-grid; cards sculpted-plate; media sculptural-plinth.
- `41-vista`: public folder retained; creative label Calma; mood peaceful, slow, reassuring; hero editorial-spread; layout editorial-asymmetric; cards fine-line; media portrait-atelier.
- `42-softline`: public folder retained; creative label Vellum; mood paper, editorial, tactile; hero clinical-dashboard; layout clinical-grid; cards clinical-module; media clinical-crop.
- `43-meridian`: public folder retained; creative label Opal; mood luminous, delicate, refined; hero soft-layers; layout soft-journey; cards offset-soft; media soft-vellum.
- `44-safeguard`: public folder retained; creative label Jardim; mood lush but controlled botanical; hero dark-cinematic; layout cinematic-immersive; cards cinematic-slate; media shadow-botanical.
- `45-silhouette`: public folder retained; creative label Lisse; mood smooth, clean, refined; hero concierge-card; layout concierge-suite; cards concierge-ticket; media concierge-frame.
- `46-curate`: public folder retained; creative label Magna; mood high authority, premium, confident; hero quiet-minimal; layout minimal-clinical; cards minimal-rule; media quiet-negative.
- `47-proof`: public folder retained; creative label Senda; mood guided, structured, reassuring; hero radiance-glow; layout luminous-studio; cards luminous-card; media skin-light.
- `48-signature`: public folder retained; creative label Isla; mood private, gentle, retreat like; hero balanced-split; layout balanced-pathway; cards calm-path; media balanced-window.
- `49-wisdom`: public folder retained; creative label Oro; mood refined gold luxury; hero proof-route; layout route-led; cards proof-ledger; media contrast-proof.
- `50-sovereign`: public folder retained; creative label Maison; mood private maison and atelier clinic; hero organic-paper; layout organic-editorial; cards paper-note; media organic-paper.

## Repeated Template Problems Found

- Homepage sections shared one dominant grid rhythm even when palette and labels changed.
- Hero areas used the same section model as normal content, which weakened the first viewport.
- Tablet behavior collapsed too early and did not keep composed two-column layouts.
- Similarity checks were stale and measured repeated generated selectors instead of visual decisions.
- The older rebuild script could overwrite the current public partial system with incompatible `cXX-*` partials.

## Design-System Problems Found

- Composition, card style, media treatment, hero type, and mobile strategy were not stored in one durable registry.
- Section archetypes existed as names but did not create enough rendered layout difference.
- The shared chrome was strong, but page architecture did not yet carry the same level of differentiation.
- Multiple obsolete brand and architecture CSS files existed beside the active foundation file, making the visual system look conflict-prone even when pages no longer referenced those files.
- Legacy colour families could still be generated from descriptive palette words, so the palette contract was tightened to the Sofiati brand colours: ivory, cream, sage, bronze, champagne, deep green, and ink.

## Partial And Runtime Problems Found

- Concept folders still contained unused `css/style.css`, `css/atlas-story.css`, `js/main.js`, and `js/partials.js` files after the active pages had moved to `concept.css` and `concept.js`.
- Concept partial folders still contained unused fragments for older accessibility, schema, navigation, form, status, contact, WhatsApp, and back-to-top systems.
- Root-level public partials and global component scripts represented older architecture and were no longer referenced by generated pages.
- The foundation script and concept script both contained interaction responsibilities, which made duplicate listeners easier to reintroduce.
- Cookie consent only supported a simple accept flow; the new contract requires accept, reject, customize, saved preferences, and localStorage persistence.
- Language controls needed real EN/PT links that point to equivalent same-page URLs instead of inert buttons.

## Responsive Problems Found

- Desktop used grid columns, but many sections still behaved like repeated stacked panels.
- Tablet needed a true 721px-1024px layout state instead of immediate phone stacking.
- Mobile needed stronger hero-first scanning and less repeated card rhythm.

## Asset And Placeholder Problems Found

- Approved transparent Sofiati portraits are available under `assets/brand/` and should remain the primary human media.
- Non-photo visual moments need intentional CSS art panels rather than gray or empty-looking boxes.
- No fabricated proof, results, testimonials, prices, awards, or medical promises should be introduced.

## Differentiation Plan

- Preserve the existing `concepts/NN-slug` routes and map the attached 50-way creative matrix onto those numbered folders.
- Generate hero-specific markup for homepage openings instead of reusing regular section scaffolds.
- Add layout family, hero pattern, card style, media treatment, mobile strategy, and uniqueness notes to each concept contract.
- Keep public partial generation centralized in `scripts/generate_public_partial_systems.py`.
- Update similarity/compliance audits so they verify the current architecture instead of stale assumptions.

## Implementation Checklist

- [x] Audit repository structure and baseline checks.
- [x] Create this refactor plan.
- [x] Create the differentiation registry.
- [x] Refactor generator inputs around a 50-concept creative matrix.
- [x] Preserve public partial ownership.
- [x] Rebuild all 50 concepts.
- [x] Run compliance, similarity, full-site static QA, public partial rendered QA, and full render matrix QA.
- [x] Complete full-site rendered QA and write final report.
