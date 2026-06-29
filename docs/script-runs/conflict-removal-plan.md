# Conflict Removal Plan

1. Replace active concept pages with clean HTML that links only `../../css/sofiati-brand-foundation.css` and `css/concept.css`.
2. Replace active scripts with `../../js/sofiati-brand-foundation.js` and `js/concept.js`.
3. Remove active Atlas, Visual DNA, architecture, and conflict-repair classes from rebuilt pages.
4. Use concept-local partials for header, mobile menu, footer, cookie banner, and floating widgets.
5. Keep old global rescue files only as deprecated historical files; do not load them from rebuilt pages.
6. Validate with `qa/audit_50_new_websites_compliance.py` and `qa/audit_50_new_websites_similarity.py`.
