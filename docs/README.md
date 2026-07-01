# Sofiati Static Site

This is the static HTML, CSS, and JavaScript website for Franciele Sofiati Biomédica. It is a handwritten site with reusable partials and no required build step.

## Folder Structure

- Root HTML files are the public pages.
- `partials/` contains shared header, mobile menu, footer, cookie banner, and floating widgets.
- `assets/` contains brand files, portraits, photos, icons, social images, favicons, backgrounds, downloads, and videos.
- `css/` contains the prepared modular CSS stack. The current visual system is preserved mainly in `pages.css` and `sofiati-brand-foundation.css`.
- `js/` contains small behavior modules loaded by every page.
- `data/` stores structured editing references for navigation, SEO, services, FAQ, and testimonials.
- `scripts/` contains local maintenance helpers.

## Partials

Every page includes these placeholders:

```html
<div data-sofiati-partial="header"></div>
<div data-sofiati-partial="mobile-menu"></div>
<div data-sofiati-partial="footer"></div>
<div data-sofiati-partial="cookie-banner"></div>
<div data-sofiati-partial="floating-widgets"></div>
```

`js/partial-loader.js` fetches files from `partials/` and dispatches `sofiati:partials-loaded` after insertion.

## Add A Page

Copy an existing root page, update the title, meta description, canonical URL, OpenGraph metadata, JSON-LD URL, body `data-page`, and H1. Add the page to navigation if needed, then run:

```bash
python3 scripts/generate-sitemap.py
python3 scripts/check-seo.py
python3 scripts/validate-links.py
```

## Add An Image

Place the image in the most specific asset folder:

- `assets/brand/` for logos and marks
- `assets/portraits/` for Franciele portrait cutouts
- `assets/photos/` for source photography
- `assets/social/` for share images
- `assets/favicons/` for icons used by browsers and manifests

Then reference it with a root-level relative path such as `assets/portraits/example.webp`.

## Update Navigation

Edit `partials/header.html`, `partials/mobile-menu.html`, and `partials/footer.html`. Keep `data-main-nav` and footer indexes consistent. `data/navigation.json` is a planning reference for future automation.

## Regenerate Files

```bash
python3 scripts/generate-sitemap.py
python3 scripts/generate-robots.py
```

## Checks

```bash
python3 scripts/validate-links.py
python3 scripts/check-seo.py
npm run screenshots
```

## Deployment

Deploy the repository root as a static site. No compiled output directory is required.
