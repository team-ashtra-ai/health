# Repository cleanup report

Date: 2026-07-18. Branch: `chore/repository-cleanup`.

## Outcome

The cleanup preserves all public HTML, PT-BR output, partials, production assets, data, CSS, JavaScript, analytics and deployment build behavior. It removes only proven non-runtime material and two unreferenced, dangerous auto-push helpers. No page content, URLs, markup, CSS cascade, JavaScript behavior, analytics configuration or public asset path was changed.

| File or component | Previous problem | Action taken | Evidence | Testing performed | Final status |
| --- | --- | --- | --- | --- | --- |
| `validation-artifacts/` | 240 MB of historic before/after screenshots in repository | Deleted; ignored for future local output | No runtime/code reference; builder excludes directory | Local asset, PT, SEO and partial checks | Removed |
| `references/` | 133 MB of design-reference exports mixed with site source | Deleted; ignored for future local output | No runtime/code reference; builder excludes directory | Local asset, PT, SEO and partial checks | Removed |
| Dated `screenshots/interactive/` | Historic local captures tracked as source | Deleted; interactive output ignored | No runtime/code reference | Local asset, PT, SEO and partial checks | Removed |
| Git auto-push helpers | Unreferenced scripts could stage/push all work or create empty remote commits | Deleted | No package, docs, CI or script reference; not part of deployment | Reference search and clean Git state | Removed |
| Production byte-duplicate assets | Multiple paths share file content | Retained | Distinct published paths and generated/CSS consumers; checksum alone is not proof | Local asset checker | Retained safely |
| CSS conflicts and `!important` debt | Existing architecture check reports errors/warnings | Not changed | Committed CSS is stale; visual baseline incomplete | Recorded baseline architecture audit | Deferred safely |
| Interaction audit | Runner imports unavailable `playwright` although lockfile has `playwright-core` | Not changed | Reproducible module-resolution failure | Baseline command run | Unresolved |

## Counts and size

| Measure | Before | After | Change |
| --- | ---: | ---: | ---: |
| Tracked files | 2,042 | 1,876 before documentation additions; 1,880 after deliverables | reduced historical file count |
| Tracked checkout size | 1.1 GB | 719 MB before documentation additions | about 381 MB removed |

The size excludes ignored local `node_modules`, virtual environments, caches and `dist/`; those made the working directory appear as 35 GB at baseline and are not repository content.

## Consolidated documentation

`README.md` remains the root maintenance entry point. `docs/architecture.md`, `docs/content-workflow.md` and `docs/deployment.md` are the concise current references. Existing detailed design/rebuild reports are retained as historical reference because their purpose cannot be conclusively discarded; they are not the current operating instructions.

## Testing

Passed after deletion:

- `python3 scripts/check-local-assets.py`
- `python3 scripts/check-portuguese-site.py --strict-warnings`
- `python3 scripts/check-seo-files.py`
- `python3 scripts/build-shared-chrome.py --check`
- `git diff --check`
- `npm run build`
- A local Chrome runtime sweep of all 52 public HTML routes at 390 px and 1440 px (104 passes): no 4xx requests, page errors, broken images, duplicate IDs, missing main landmarks or missing H1s
- A 390 px homepage smoke check confirming the cookie banner and mobile-menu partials load and that English/PT language links resolve to `index.html` and `pt/index.html`

Baseline failures, not caused or hidden by this cleanup:

- CSS compiled output stale.
- English content checker mismatches in `mission.html` and `values.html`.
- Journal generated HTML stale.
- CSS architecture checker reports existing debt.
- Browser interaction runner cannot load `playwright` from current dependencies.

The direct runtime sweep verifies loading and structural invariants, but it does not replace the blocked automated click/focus/consent suite. Cookie acceptance, consent-gated analytics events and mobile-menu focus trapping therefore remain explicitly unverified in this cleanup.

## Future maintenance

1. Keep public paths stable; make content changes through English sources and regenerate PT output.
2. Run the passing release checks above after each scoped change.
3. Repair the Playwright dependency mismatch, then establish complete before/after visual captures before any CSS cascade refactor.
4. Reconcile generated CSS, Journal output and English source checks in dedicated reviewed changes, never as incidental cleanup.
5. Write local audits and screenshots into ignored directories, not `assets/` or public paths.
