# New Layout Strategy

Date: 2026-06-26

## Global Refactor Goals

- Make the repo easier to maintain without flattening the 50 concepts into one template.
- Preserve the existing standalone concept model: each concept can render independently with local HTML, CSS, JS, partials and assets.
- Standardize technical skeletons where they reduce risk: mount names, accessibility attributes, navigation semantics, schema generation, form states, floating widget hooks and cookie hooks.
- Keep visual expression concept-specific: header composition, hero geometry, section order, card treatment, CTA rhythm, footer layout, motion and image sequencing.
- Reduce clutter by archiving generated evidence only after replacement evidence exists.
- Improve headers so desktop navigation is visible, single-row where intended, and does not wrap or crowd the brand mark.
- Improve mobile menus so controls, language switchers and primary routes are readable, reachable and concept-appropriate.
- Improve footers by removing accidental boxes/circles while preserving the concept's own editorial, clinical, botanical, luxury, or minimal identity.
- Make consultation CTAs clearer without pressuring visitors or implying suitability without evaluation.
- Improve responsive behavior at 360, 390, 768, 1024, 1366 and 1440px.
- Preserve ethical, legal, accessibility and SEO rules from the master brief.
- Use screenshot review as a quality gate, not just static source checks.

## Technical Standardization Targets

- Keep `data-partial-mount` names stable.
- Keep `partials.js` behavior concept-local but structurally consistent.
- Keep required partial types in every concept.
- Keep body `data-page`, `data-page-title`, `data-page-description`, `data-canonical` and `data-concept` consistent.
- Keep form markup accessible and privacy-aware.
- Keep cookie/floating-widget hooks stable: `[data-cookie-banner]`, `[data-sofiati-cookie-loader]`, `[data-floating-tools]`, `.floating-whatsapp`, `[data-back-to-top]`.
- Keep navigation templates semantic with real links, not hidden desktop-only tricks.
- Keep schema/head structure auditable.

## Concept Uniqueness Rules

Each concept must differ meaningfully in:

- Header layout: examples include split editorial, stacked magazine, rail, command bar, capsule, centered monogram, transparent overlay, quiet legal ledger, and concierge strip.
- Navigation rhythm: examples include split left/right, priority routes, secondary care rail, compact command nav, chapter index, and contextual service nav.
- Mobile menu behavior: examples include full-screen editorial, left drawer, bottom sheet, two-column grid, paper panel, radial reveal, story panel, and secure clean drawer.
- Hero structure: examples include portrait-led, image-first, dossier, split copy, full-bleed editorial, typographic index, product-like service cards, and consultation desk still life.
- Section order: do not reuse the same page order across same-family concepts.
- Image rhythm: alternate portrait, service still life, botanical macro, clinical document, visual pause, and icon-led moments.
- Card style: use concept-specific density, borders, dividers, notes, ledger rows, tabs, labels, drawers, strips, and frames.
- CTA treatment: vary from quiet text links to appointment strip, ledger stamp, concierge button, pinned mobile CTA, consultation card, or footer gateway.
- Footer structure: vary from business card, legal ledger, editorial index, route map, monogram field, compact legal strip, or contact desk.
- Animation style: prefer subtle motion tied to concept identity, with reduced-motion support.
- Typography rhythm: vary scale contrast, line length, heading cadence and label density.
- Spacing rhythm: vary compact, generous, chaptered, editorial, clinical, modular and ceremony-like spacing.
- Decorative assets: use sparingly and conceptually; never add decoration just to fill space.
- Desktop/mobile adaptation: mobile must be designed, not an accidental collapse of desktop.

## Forbidden Refactor Patterns

Do not:

- Make all concepts use the same header.
- Make all concepts use the same hero.
- Make all concepts use the same footer.
- Make all concepts use identical CTAs.
- Use the same card grid everywhere.
- Hide essential desktop navigation without a concept-specific reason and an alternate accessible route.
- Create nav wrapping at desktop widths.
- Overuse boxes, circles, floating cards, badges, or decorative containers.
- Create two-color block menus unless the concept specifically calls for that behavior.
- Make mobile and desktop behave accidentally the same.
- Remove premium visual personality.
- Replace all layouts with generic templates.
- Reword medical/beauty/legal claims beyond obvious formatting without human review.
- Introduce fake testimonials, before/after implications, guaranteed results, no-risk language, or private address details.

## Refactor Model

Use a three-layer model:

1. Stable technical skeleton:
   partial mounts, accessible landmarks, page metadata, schema, form semantics, cookie/floating hooks, script loading and audit attributes.
2. Concept-specific component recipe:
   header, navigation, mobile menu, hero, footer, CTA and interaction recipe per concept.
3. Page-type storytelling variation:
   each page type keeps required content but changes section order, visual emphasis and CTA timing by concept.

## Recommended Refactor Order

1. Proof-of-concept on 3 concepts.
2. Screenshot and audit review.
3. Stabilize partial skeletons only where the POC proves repeated technical issues.
4. Apply concept-by-concept batches of 5 concepts.
5. Run rendered diagnostics and screenshot review after every batch.
6. Archive superseded generated evidence after replacement evidence exists.
7. Delete only approved generated junk after verification.

## Quality Gates

- Static audits pass.
- Rendered responsive diagnostics pass for edited concepts at 360, 390, 768, 1024, 1366 and 1440px.
- Header/nav does not wrap unintentionally.
- Mobile menu is readable and operable.
- Footer is visually polished and copyright alignment is acceptable.
- Consultation/contact path is visible and ethical.
- Cookie, WhatsApp and back-to-top still work.
- Screenshots confirm concepts remain distinct.
