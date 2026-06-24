# Sofiati Premium English-First Website Concept System

Static website presentation for `www.sofiati.com`, built for Franciele Sofiati, Advanced Aesthetic Biomedicine, CRBM 6277, Londrina, PR.

## Purpose

This repository replaces the previous 50-industry portfolio with 50 premium Sofiati website concepts. Every concept is English-first, mobile-first, ethical, and based on the supplied Sofiati Brand Identity folder.

## Run Locally

```bash
python3 -m http.server 8000
```

Open `http://localhost:8000/` or `http://localhost:8000/select.html`.

## Rules

- English first only. No Portuguese pages or translation script are included yet.
- Use `Londrina, PR` only. Do not publish a full address or Google Maps embed.
- Do not invent testimonials, before-and-after claims, results, guarantees, cures or risk-free language.
- All treatment copy is educational until reviewed and approved by Franciele Sofiati.
- Instagram material is used for research and content architecture only unless client-owned usage is confirmed.

## Structure

```txt
/assets/          Optimized local logos, brand images, icons, Instagram placeholders
/css/             Tokens, base styles, components, utilities, concept-specific CSS
/js/              Partial loading, navigation, accessibility, cookies, forms, motion
/partials/        Header, footer, mobile menu, concept switcher
/data/            Brand, concepts, treatments, FAQ, journal, inspiration and Instagram research
/concepts/01-50/  Numbered concept sites with all required pages
```

## Concept System

Concepts are numbered `01` through `50` and named with original strategy names such as Inspire, Empower, Enhance, Renew and Elevate. Names are not copied from reference websites. Each concept includes Home, About, Mission, Values, Care, Laser, Skin, Results, Testimonials, Journal, Blog, FAQ, Contact, Consultation, Legal, Privacy, Cookies, Accessibility and 404.

## Brand Identity

The source folder is `brand identity/`. Extracted anchors: sage `#A2AE9F`, deep sage `#798A80`, soft sand `#F3EFE5`, gold endpoints `#734011` and `#FDE3B0`. The identity references Bellarina for the signature and Mansory for the wordmark; the site preserves official logo artwork and uses refined local serif/sans fallbacks for live text.

## Partials

Each page loads `/partials/header.html`, `/partials/footer.html`, `/partials/mobile-menu.html` and `/partials/concept-switcher.html` through `/js/partials.js`. Use a local HTTP server so partial loading works consistently; pages include fallback header/footer markup if a fetch fails.

## Editing A Concept

1. Edit concept metadata in `/data/concepts.json`.
2. Edit concept CSS in `/css/concepts/NN.css`.
3. Edit the static page folder under `/concepts/NN/page/index.html`.
4. Preserve relative links and partial placeholders.

## Assets

Optimized assets live under SEO-friendly paths such as `/assets/brand/sofiati-logo-primary-sage.png` and `/assets/images/home/sofiati-home-hero-botanical-clinical-luxury.webp`. Use WebP for photographs, PNG for transparent logos and SVG for simple vector marks.

## Instagram Research

Research files live in `/data/instagram/`. Full scraping was not performed; the repository includes a manual import path for approved post URLs, captions and assets. Do not bypass login restrictions or reuse patient/caption/media content without approval.

## Contact Details

- WhatsApp: `(43) 9 9104-3536`
- Email: `sofiatimendonca@gmail.com`
- Instagram: `@fransofiati_biomedica`
- Location: `Londrina, PR`
- CRBM: `6277`

## Production Checklist

- Review all medical, legal and treatment copy with the client.
- Replace testimonial placeholders only with written approval.
- Confirm active services, equipment names and regulatory scope.
- Add real analytics IDs only after consent policy approval.
- Run link, console, keyboard, responsive and Lighthouse checks.
- Confirm every page keeps the no-full-address rule.

## Deployment

The project is plain static HTML/CSS/JS and can deploy to any static host. Canonical URLs currently point to `https://www.sofiati.com`.
