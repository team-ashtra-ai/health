# Performance Final Report

Generated: 2026-07-18T13:20:09.464Z

Source: `/run/media/code/Storage/GitHub/ashtra/health/dist`

Chrome: Google Chrome 150.0.7871.46

Lighthouse: 12.8.2

Runs per route/profile: 1

> These are local laboratory measurements. They do not claim deployed PageSpeed or Search Console field performance.

| Route | Profile | Performance median (min–max) | LCP ms | CLS | TBT ms | FCP ms | Transfer KB | Requests |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| index.html | mobile | 99 (99–99) | 1879 | 0.000 | 48 | 1204 | 159 | 13 |
| index.html | desktop | 100 (100–100) | 642 | 0.000 | 0 | 282 | 359 | 15 |
| about.html | mobile | 99 (99–99) | 1955 | 0.000 | 42 | 1203 | 168 | 13 |
| about.html | desktop | 100 (100–100) | 643 | 0.000 | 0 | 282 | 363 | 15 |

## Environment and limitations

- Cold-cache Lighthouse navigation with simulated throttling and a clean headless Chrome profile.
- Local responses use gzip for compressible resources and revalidation caching for fair source/build comparison.
- The production domain did not resolve during this audit, so production PSI and CrUX data are not included.
- Analytics IDs remain placeholders; the performance cost of a future published GTM container cannot yet be measured.
