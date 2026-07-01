# Deployment

This project is a static site. Deploy the repository root to the hosting provider.

Recommended pre-deploy checks:

```bash
npm install
python3 scripts/generate-sitemap.py
python3 scripts/generate-robots.py
python3 scripts/validate-links.py
python3 scripts/check-seo.py
npm run screenshots
```

Production domain:

```txt
https://www.sofiati.com
```

Make sure the host serves `index.html`, `robots.txt`, `sitemap.xml`, `site.webmanifest`, `favicon.ico`, and the `assets/`, `css/`, `js/`, and `partials/` folders.
