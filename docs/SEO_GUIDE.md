# SEO Guide

Every public HTML page should include:

- One unique `<title>`.
- One unique meta description.
- One canonical URL.
- OpenGraph title, description, image, type, and URL.
- Twitter card metadata.
- JSON-LD with `image`, `logo`, `url`, and `mainEntityOfPage`.
- Exactly one H1.

Run:

```bash
python3 scripts/check-seo.py
python3 scripts/generate-sitemap.py
```

`sitemap.xml` should include public pages only and should not include `404.html`.
