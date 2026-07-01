# Sofiati Static Website

Static handwritten website for Franciele Sofiati, based on the selected Inspire direction.

The site is plain HTML, CSS, and JavaScript. There is no build step and no concept generator. Edit the root HTML pages, shared partials, `css/sofiati-brand-foundation.css`, and `js/sofiati-brand-foundation.js` directly.

## Run Locally

```bash
python3 -m http.server 8000
```

Open:

```txt
http://localhost:8000/
```

## Structure

```txt
/
  index.html
  about.html
  care.html
  consultation.html
  contact.html
  ...
/assets/brand/      Logo and brand assets
/assets/photos/     Site photography
/css/               Shared site styles
/js/                Shared site JavaScript
/partials/          Header, footer, mobile menu, cookies, floating widgets
/scripts/           Small local helper scripts
```

## Helper Scripts

Stage all changes, commit with an automatic date/time message, and push:

```bash
python3 scripts/git_add_commit_push.py
```

Create and push an empty timestamped commit:

```bash
python3 scripts/git_empty_commit.py
```

Capture full-page homepage screenshots for mobile, tablet, and desktop:

```bash
python3 scripts/capture_homepage_full_screenshots.py
```

Screenshots are saved to:

```txt
screenshots/homepage/YYYY-mm-dd_HH-MM-SS/
```

The screenshot script uses Node Playwright from `package.json`. If dependencies are missing, run:

```bash
npm install
```

## Content Rules

- Keep the website English-first unless a page is intentionally translated.
- Use `Londrina, PR` only for location references.
- Do not publish private address details or map embeds without approval.
- Do not invent testimonials, guarantees, cures, risk-free claims, or before-and-after results.
- Keep treatment language educational and expectation-led until reviewed by Franciele Sofiati.
