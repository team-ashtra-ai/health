# Performance regression guide

## Routine commands

Install and create a clean production build:

```bash
npm ci
npm run build
```

Run the final five-run Lighthouse matrix:

```bash
npm run perf:all
npm run perf:budget
```

Run one profile or a selected route while developing:

```bash
PERF_ROUTES=index.html,treatments.html PERF_RUNS=3 npm run perf:mobile
PERF_ROUTES=contact.html PERF_RUNS=3 npm run perf:desktop
```

Capture Chrome DevTools-compatible traces, network data and CSS/JavaScript coverage:

```bash
node scripts/performance-trace.mjs --source dist --label final
```

Recreate the image inventory:

```bash
npm run perf:images
```

Compare source and production screenshots at the maintained viewport matrix:

```bash
npm run perf:visual
```

Run functional, responsive, SEO and analytics checks:

```bash
npm run validate
NODE_PATH=node_modules python3 scripts/audit-responsive-layout.py
```

## Budgets and review rules

`performance-budget.json` contains laboratory and page-type resource budgets. The strict internal medians are engineering targets. CI uses slightly more tolerant hard failures so normal Lighthouse variance does not fail a healthy change.

A pull request must not introduce:

- a mobile Lighthouse run below 90;
- a multi-megabyte hero image;
- an unreserved content image;
- an eagerly loaded below-the-fold image without a documented reason;
- a duplicate font or analytics installation;
- a page-specific script loaded globally without need;
- an application long task over 200 ms;
- a stable-name asset with a one-year immutable cache header;
- a broken consent, language, form, SEO or accessibility flow.

When a budget cannot be met, record the exact resource, its compressed bytes, why it is necessary and the approved new ceiling. Do not silently loosen a global threshold.

## Adding images

1. Keep the high-quality source in `assets/`.
2. Use an accurate `width`, `height`, `alt` and loading policy in source HTML.
3. Do not manually add generated files to `assets/generated`; the build owns them.
4. Run `npm run build` and inspect the generated AVIF/WebP `srcset`.
5. Confirm the image remains sharp at 320, 390, 768, 1440 and 1920 px viewports.
6. Run `npm run perf:images` and the visual comparison.

The single above-the-fold hero scene is preloaded. Do not preload card, journal, footer or quotation images.

## Adding JavaScript

- Prefer an existing delegated listener over one listener per card.
- Keep interaction handlers short and render visual feedback before secondary work.
- Do not add polling while a page is hidden.
- Use observers for visibility and `requestIdleCallback` only for genuinely optional work.
- Preserve the consent gate: GTM loads only after analytics consent in basic mode.
- Never add a direct GA4 `gtag.js` installation.
- Re-run the trace script and inspect long tasks and unused coverage across more than one template.

## Adding CSS

- Edit readable files under `css/src/`, then rebuild `css/site.css` using the existing CSS assembly process before the production build.
- Do not add `@import`.
- Avoid full-screen blur or backdrop filters on moving elements.
- Prefer transforms and opacity for animation.
- Preserve reduced-motion behaviour.
- Test anchor navigation, print layout and browser search when applying `content-visibility`.

## Analysing a regression

1. Confirm it reproduces across at least three clean runs.
2. Compare the median, minimum and variance.
3. Identify the LCP element and split LCP into response, load delay, load duration and render delay.
4. Inspect the network initiator and priority for the resource.
5. Open the stored trace in the current Chrome DevTools Performance panel.
6. Review Insights, Network, Coverage and Rendering diagnostics.
7. For an interaction regression, separate input delay, handler time and presentation delay.
8. Check accepted-analytics and denied-analytics states.
9. Correct the cause, then repeat the same test matrix.

## Lighthouse CI

The GitHub Actions workflow builds once, runs five mobile and five desktop Lighthouse CI collections, and uploads the reports. The filesystem reports are build artifacts; no Lighthouse server token is required.

Local equivalents:

```bash
npx lhci autorun --config=lighthouserc.mobile.cjs
npx lhci autorun --config=lighthouserc.desktop.cjs
```

## Production field monitoring

Laboratory results are safeguards, not field-data claims. After deployment:

- use PageSpeed Insights for lab and available CrUX data;
- use Search Console for grouped 75th-percentile field status;
- use the existing consent-aware `field_performance` event for directional real-user diagnostics;
- re-test after publishing or materially changing the real GTM container.
