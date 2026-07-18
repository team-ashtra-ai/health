# Performance Baseline Report

Generated: 2026-07-18T12:58:07.215Z

Source: `/run/media/code/Storage/GitHub/ashtra/health`

Chrome: Google Chrome 150.0.7871.46

Lighthouse: 12.8.2

Runs per route/profile: 1

> These are local laboratory measurements. They do not claim deployed PageSpeed or Search Console field performance.

| Route | Profile | Performance median (min–max) | LCP ms | CLS | TBT ms | FCP ms | Transfer KB | Requests |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| index.html | mobile | 74 (74–74) | 21007 | 0.045 | 60 | 1580 | 6607 | 37 |

## Environment and limitations

- Cold-cache Lighthouse navigation with simulated throttling and a clean headless Chrome profile.
- Local responses use gzip for compressible resources and revalidation caching for fair source/build comparison.
- The production domain did not resolve during this audit, so production PSI and CrUX data are not included.
- Analytics IDs remain placeholders; the performance cost of a future published GTM container cannot yet be measured.
