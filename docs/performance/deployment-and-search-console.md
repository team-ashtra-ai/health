# Performance deployment and Search Console workflow

## What is deployable

The readable HTML, CSS, JavaScript and original images in the repository root are the source. Run the production build and deploy only `dist/`. Do not edit generated `dist/` files directly.

```bash
npm ci
npm run build
```

The build:

- composes shared navigation, footer and consent partials into every HTML page;
- bundles and minifies first-party JavaScript;
- combines the consent-aware measurement files without adding direct GA4;
- minifies CSS and HTML;
- creates responsive AVIF and WebP image variants;
- preloads only the route-specific hero image;
- applies content hashes to production CSS, JavaScript and generated images;
- creates Cloudflare Pages-compatible cache headers in `dist/_headers`.

## Deploying

1. Set the hosting build command to `npm ci && npm run build`.
2. Set the publish directory to `dist`.
3. Keep the production hostname as `www.francielesofiati.com`; canonicals, sitemap and robots use that hostname.
4. Deploy to a preview URL first.
5. Confirm the preview serves `dist/.performance-build.json`, then check representative pages and the form flow.
6. Promote the same build output to production. Do not rebuild between preview approval and production when the platform can promote an immutable deployment.
7. Purge only changed HTML, manifest, sitemap and robots entries if a manual Cloudflare purge is needed. Hashed assets do not need purging.
8. Confirm response compression is Brotli or gzip and that HTTP/2 or HTTP/3 is active at the CDN.
9. Confirm HTML returns `Cache-Control: public, max-age=0, must-revalidate`; hashed files under `/assets/build/` and `/assets/generated/` should return one-year immutable caching.
10. Confirm `thank-you.html` and `pt/thank-you.html` return `private, no-store` and retain their `noindex` tags.

Do not add an immutable cache rule to every `/assets/*` file unless all those filenames become content-addressed. The generated rules deliberately reserve immutable caching for hashed output.

## Post-deployment PageSpeed checks

Run the repository PSI client only after the production hostname resolves publicly:

```bash
cp .env.example .env
export PAGESPEED_API_KEY="your-key-if-used"
npm run perf:psi
```

The API key is optional but helps with quota. Never commit it. To limit a verification pass:

```bash
node scripts/performance/psi-audit.mjs --paths /,/treatments.html,/contact.html
node scripts/performance/psi-audit.mjs --strategy mobile --limit 10
```

The report distinguishes URL-level CrUX, origin-level CrUX and unavailable field data. A low-traffic URL with no URL-level CrUX record is expected and is not a technical error.

For each representative production URL:

1. Test mobile and desktop separately.
2. Run more than once; do not act on a single outlier.
3. Compare the LCP element and LCP subparts, not only the score.
4. Test once before optional analytics consent and once after accepting analytics.
5. If a real GTM container is now live, inspect its network and main-thread cost because placeholder-only local tests cannot predict the contents of a future container.

## Search Console Core Web Vitals

1. Deploy the optimised production build.
2. Confirm the canonical production files are live.
3. Open Search Console and select the Domain property for `francielesofiati.com`.
4. Open **Experience → Core Web Vitals**.
5. Review mobile URL groups.
6. Review desktop URL groups.
7. Open each **Poor** or **Needs improvement** issue.
8. Note the representative URLs Google assigns to the group.
9. Match those URLs to the relevant site template: home, editorial, service, conversion, trust, journal index, article, policy or confirmation.
10. Test the representative URL in PageSpeed Insights and compare it with the local final report.
11. Correct template-level problems and redeploy.
12. Start **Validate fix** only after the corrected response is confirmed live.
13. Monitor the validation period; do not repeatedly restart it for normal daily variation.
14. Continue reviewing consent-aware `field_performance` events in GA4 after the real GTM container is configured.

Search Console reports grouped, rolling real-user field data. It may not list low-traffic pages individually, and a successful deployment does not immediately change the report. Do not claim that the Core Web Vitals report has passed until sufficient field data confirms it.

## Cache verification

Use a production response, not localhost:

```bash
curl -I https://www.francielesofiati.com/
curl -I https://www.francielesofiati.com/assets/build/REPLACE_WITH_LIVE_HASH.css
curl -I https://www.francielesofiati.com/thank-you.html
```

Look for:

- one necessary redirect at most before the canonical `https://www` URL;
- `Content-Encoding: br` or `gzip` for HTML, CSS and JavaScript;
- CDN cache headers consistent with `dist/_headers`;
- no mixed-content resources;
- correct content types for AVIF, WebP, CSS, modules and the manifest.

## Rollback

Rollback should promote the preceding immutable deployment. Avoid broad manual file replacement because HTML and content-hashed asset references must remain from the same build.
