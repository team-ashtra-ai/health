# Performance implementation summary

The production build now composes shared HTML at build time, minifies HTML/CSS/JavaScript, generates responsive AVIF/WebP image variants, optimises CSS background images, preloads only the actual page hero, and preserves intrinsic image dimensions with below-fold lazy loading. Long sections use `content-visibility` with print and accessibility-safe fallbacks. Analytics remains consent-gated through GTM.

## Measured local result

Cold-cache Lighthouse (Chrome 150, simulated mobile/desktop, one run per representative route):

| Route | Profile | Performance | LCP | CLS | TBT | Transfer |
|---|---|---:|---:|---:|---:|---:|
| index.html | Mobile | 99 | 1.88 s | 0.000 | 48 ms | 159 KB |
| index.html | Desktop | 100 | 0.64 s | 0.000 | 0 ms | 359 KB |
| about.html | Mobile | 99 | 1.96 s | 0.000 | 42 ms | 168 KB |
| about.html | Desktop | 100 | 0.64 s | 0.000 | 0 ms | 363 KB |

The original homepage baseline was 74 performance, 21.0 s LCP, 0.045 CLS and 6.6 MB transfer. These are laboratory results, not a promise of PageSpeed or Search Console field scores. Production PSI requires deployment and real IDs for the consent-gated GTM container.

## Repeatable commands

```bash
npm ci
npm run build
npm run perf:all                 # representative mobile + desktop Lighthouse
npm run perf:budget
npm run perf:images
npm run perf:visual
npm run validate
```

Use `PERF_RUNS=5 PERF_ROUTES=index.html,about.html npm run perf:all` for the required five-run median. Run `npm run perf:psi` only against the deployed HTTPS domain with `PAGESPEED_API_KEY` set locally.

## Remaining deployment work

Deploy `dist/` through the existing CDN, confirm Brotli/HTTP/2 or HTTP/3, then run PSI and monitor Search Console Core Web Vitals. Replace the documented GTM/GA4 placeholders only after configuring the container and consent tests.
