# Proof-of-Concept Refactor Plan

Date: 2026-06-26

Do not implement this plan until explicitly instructed.

## POC Concepts

### 1. Low-Risk Concept: `04-renew`

- Why chosen: current uniqueness matrix marks it `strong` with no active issue recorded, and its laser technology dossier direction is concrete enough to refactor without repairing major breakage first.
- What will be refactored: header/nav rhythm, mobile menu polish, homepage first half, one service page (`laser.html`), consultation/contact path, footer polish.
- Files likely affected: `concepts/04-renew/index.html`, `laser.html`, `consultation.html`, `contact.html`, `css/style.css`, `partials/header.html`, `partials/navigation.html`, `partials/mobile-menu.html`, `partials/footer.html`, `partials/consultation-form.html`, `partials/contact-card.html`.
- Risks: accidentally making the dossier too generic; overstandardizing from the first POC; disturbing a currently strong concept.
- Screenshot requirements: home desktop/mobile, laser desktop/mobile, consultation/contact desktop/mobile, header/footer/menu screenshots, rendered widths 360/390/768/1024/1366/1440.
- Rollback method: use git diff for only `concepts/04-renew/**` and revert those files if screenshots fail.
- Success criteria: stronger dossier identity, no nav wrapping, readable menu, intact forms/widgets/cookie bar, no ethical copy regression, visually distinct from 14/24/34/44.

### 2. Medium-Risk Concept: `03-enhance`

- Why chosen: known language switcher and footer decoration issues, but scope is bounded and useful for testing menu/footer fixes.
- What will be refactored: mobile menu contrast/top-row spacing, footer unboxing, header polish, homepage hero and one service page (`care.html` or `laser.html`).
- Files likely affected: `concepts/03-enhance/index.html`, `care.html` or `laser.html`, `consultation.html`, `contact.html`, `css/style.css`, `partials/header.html`, `partials/mobile-menu.html`, `partials/footer.html`.
- Risks: clinical drawer can become too dark/heavy; footer fix could erase Enhance's clinical magazine identity.
- Screenshot requirements: menu open at 360/390/768, footer at desktop/mobile, home and service page before/after.
- Rollback method: git diff scoped to `concepts/03-enhance/**`.
- Success criteria: EN/PT readable, footer premium without heavy boxes/circles, no copyright offset regression, distinct from 13/23/43.

### 3. High-Risk Concept: `46-curate`

- Why chosen: high-risk matrix status and rendered diagnostics show desktop nav wrapping at 1024, 1366 and 1440, making it a good stress test for responsive header repair.
- What will be refactored: curated tab header, desktop nav compression without hiding essential navigation, treatment-category mobile menu, footer centering, homepage and one service page.
- Files likely affected: `concepts/46-curate/index.html`, `care.html` or `laser.html`, `consultation.html`, `contact.html`, `css/style.css`, `partials/header.html`, `partials/navigation.html`, `partials/mobile-menu.html`, `partials/footer.html`.
- Risks: solving nav wrapping with a generic header; making it too similar to 06/16/26/36; breaking responsive menu behavior.
- Screenshot requirements: all standard desktop widths, mobile menu open, footer, contact/consultation path.
- Rollback method: git diff scoped to `concepts/46-curate/**`.
- Success criteria: nav one row or intentionally compact at all desktop widths, curated tab identity intact, no widget/form/cookie regression.

## Systems The POC Must Test

- Header/nav.
- Mobile menu.
- Language switcher.
- CTA hierarchy.
- Footer and copyright alignment.
- Homepage sections.
- One service page.
- One consultation/contact path.
- Responsive behavior at 360, 390, 768, 1024, 1366 and 1440px.
- Screenshot capture.
- Static audit and rendered audit verification.

## POC Implementation Guardrails

- Implement only one POC concept at a time.
- Start with `04-renew` unless the human explicitly chooses another concept.
- Do not edit all 50 concepts.
- Do not run source-modifying scripts.
- Do not delete or archive anything.
- Preserve approved claims and legal/privacy wording.
- Update this plan, the task ledger and relevant audit notes after each POC.

## POC 1 Result: `04-renew` - Completed 2026-06-26

- Status: implemented on branch `refactor-system-poc-2026-06-26`.
- Scope kept: only `concepts/04-renew` source files were refactored, plus shared audit/translation scripts and generated documentation/audit outputs.
- Files changed in the concept: `index.html`, `laser.html`, `consultation.html`, `contact.html`, `care.html`, `skin.html`, `results.html`, `css/style.css`, `js/main.js`, `partials/header.html`, `partials/mobile-menu.html`.
- Identity outcome: Renew now reads more clearly as a laser technology dossier with a dossier-style header, gridded dossier index, structured laser panels, evaluation-led consultation/contact path and calmer footer/mobile treatment.
- Technical outcome: `04-renew/js/main.js` now includes local mobile-menu behavior and the optional EN/PT runtime. English remains source copy; Portuguese switching uses exact mappings from `data/translation-strings.json`.
- Audit outcome: static site, internal links, layout signatures, ethics/contact and public partial audits pass after the POC.
- Rendered outcome: `audit/reports/04-renew-poc-rendered-smoke.md` is PASS for desktop/mobile home and laser screenshots, cookie/WhatsApp/back-to-top/form/menu/language checks and no horizontal overflow.
- Screenshot evidence:
  - `audit/screenshots/poc-04-renew/04-renew-home-desktop.png`
  - `audit/screenshots/poc-04-renew/04-renew-home-mobile.png`
  - `audit/screenshots/poc-04-renew/04-renew-laser-desktop.png`
  - `audit/screenshots/poc-04-renew/04-renew-laser-mobile.png`
- Issue found and fixed during visual review: the doctor credential card overlapped the desktop hero headline. A `04-renew` CSS override moved it onto the visual panel and the rerun confirmed `heroOverlap: false`.
- Additional target-concept cleanup: removed duplicate `data-visual-qa-repair` attributes from `care.html`, `skin.html` and `results.html`.
- Known follow-up: the translation report intentionally lists the other 49 concepts as pending runtime rollout because this POC did not modify other concept folders.
- Rollback method: revert the POC commit, or revert the `04-renew` files above plus `scripts/translate_pages.py`, the ethics-audit helper change in `scripts/sofiati_complete_system.py`, translation report/data outputs and the POC rendered-smoke outputs.
- Next recommended implementation: do not apply to all 50 yet. Review the four POC screenshots, approve the direction, then either polish `04-renew` one more pass or proceed to the next POC concept, `03-enhance`.
