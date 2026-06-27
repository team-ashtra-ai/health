# Scripts

- `build_selector_pages.py` is retained for old selector experiments; the standalone rebuild now writes `index.html` and `select.html` from `generate_concepts.py`.
- `generate_concepts.py` rebuilds the 50 self-contained English-first Sofiati concepts with flat pages, local CSS, local JS, local partials, copied assets and design notes.
- `translate_pages.py` creates a non-destructive English-source translation inventory in `data/translation-strings.json` and `final/translation-report.*`; it does not rewrite the reviewed concepts.
- `capture_homepage_screenshots.py` captures desktop and mobile first-viewport screenshots for the selector homepage and all 50 standalone concept homepages into `final/homepage-screenshots/`.
- `audit_static_site.py` checks standalone folder structure, local runtime dependencies, page completeness, local links, English-first copy, safety copy, service coverage, disclaimers, uniqueness markers, screenshots and tracked video files.
- `git_update.sh` runs `git add -A`, commits with a dated message and pushes the current branch.
- `git_update_allow_empty.sh` does the same but allows an empty commit.
