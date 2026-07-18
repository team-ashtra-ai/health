# Deployment

Preview the source site over HTTP:

```bash
python3 -m http.server 4173
```

Build the production artifact with:

```bash
npm run build
npm run serve
```

Deploy only `dist/`, never the repository root. The builder excludes development caches, reports, screenshots, historical references and source-only artifacts. Cloudflare Pages and GitHub deployment configuration are not present in this checkout, so this cleanup does not create or replace them.

Before deployment, run the deterministic checks that currently pass:

```bash
python3 scripts/check-local-assets.py
python3 scripts/check-portuguese-site.py --strict-warnings
python3 scripts/check-seo-files.py
python3 scripts/build-shared-chrome.py --check
```

Also review the known baseline failures recorded in the cleanup report before treating a deployment as fully validated.
