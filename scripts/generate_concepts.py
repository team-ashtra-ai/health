#!/usr/bin/env python3
"""Rebuild the Sofiati portfolio as 50 portable standalone static sites.

Each concept receives its own flat HTML pages, local CSS, local JavaScript,
partials, copied assets and design notes. No concept page depends on root
runtime CSS, JS, partials or assets.
"""

from __future__ import annotations

import json
import math
import shutil
from dataclasses import dataclass
from html import escape
from pathlib import Path
from textwrap import dedent


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
ROOT_ASSETS = ROOT / "assets"

BRAND = {
    "name": "Franciele Sofiati",
    "descriptor": "Advanced Aesthetic Biomedicine",
    "credential": "CRBM 6277",
    "positioning": "Laser, skin and advanced aesthetic care in Londrina, PR",
    "whatsapp": "(43) 9 9104-3536",
    "email": "sofiatimendonca@gmail.com",
    "instagram": "@fransofiati_biomedica",
    "location": "Londrina, PR",
    "domain": "www.sofiati.com",
    "whatsapp_url": "https://wa.me/5543991043536",
    "instagram_url": "https://www.instagram.com/fransofiati_biomedica/",
    "domain_url": "https://www.sofiati.com",
}

CONCEPTS = [
    ("01", "inspire", "Inspire", "https://joaodermatologista.com.br/", "editorial diagnosis journey", "split masthead with clinical proof rail", "chaptered fullscreen drawer", "business-card editorial footer", "soft reveal with line drawing"),
    ("02", "empower", "Empower", "https://www.clinicadravanessavanzo.com.br/", "boutique contact architecture", "card-like sticky header", "ivory contact-sheet menu", "oversized logo footer", "contact card parallax"),
    ("03", "enhance", "Enhance", "https://drajuliasaldanha.com.br/", "botanical clinic magazine", "sage magazine bar", "folding editorial menu", "journal index footer", "masked image fade"),
    ("04", "renew", "Renew", "https://clinicadermacatarina.com.br/", "laser technology dossier", "monogram technical header", "specification drawer", "clinical columns footer", "accordion glide"),
    ("05", "elevate", "Elevate", "https://clinicapellier.com.br/", "quiet luxury skincare journal", "split wordmark navigation", "image-and-copy mobile menu", "luxury skincare footer", "watermark fade"),
    ("06", "refine", "Refine", "https://clinicamarianagenta.com.br/", "mobile story pathway", "left rail desktop nav", "stepped treatment menu", "botanical route footer", "staggered story cards"),
    ("07", "glow", "Glow", "https://clinicamakino.com.br/londrina/", "clinical proof grid", "minimal evidence header", "bottom-sheet service menu", "legal-light footer", "image rise on scroll"),
    ("08", "balance", "Balance", "https://www.clinicasantez.com.br/", "monogram sanctuary", "centered emblem header", "round botanical menu", "contact-card footer", "orbital monogram reveal"),
    ("09", "radiance", "Radiance", "https://www.iderj.com.br/", "consultation conversion studio", "floating appointment header", "bronze command menu", "magazine conversion footer", "sticky CTA pulse"),
    ("10", "essence", "Essence", "https://clinicadermic.com.br/", "minimal appointment suite", "desktop mega-menu", "story background menu", "split CTA footer", "underline draw"),
    ("11", "bloom", "Bloom", "https://www.institutopontello.com.br/", "institutional authority landing", "dual-row institute header", "services atlas menu", "credentials footer", "stat count reveal"),
    ("12", "vital", "Vital", "https://dermaclinica.com.br/", "dermatology portal", "portal nav header", "category drawer menu", "clinic directory footer", "tabbed service reveal"),
    ("13", "poise", "Poise", "https://www.clinicadaianesaldanha.com.br/", "private boutique columns", "narrow monogram header", "accordion boutique menu", "signature footer", "column slide"),
    ("14", "aura", "Aura", "https://saintbeaute.com.br/", "spa-luxury clinic mood", "champagne capsule header", "soft overlay menu", "ritual footer", "slow opacity bloom"),
    ("15", "clarity", "Clarity", "https://www.clinicasandin.com.br/", "procedure atlas", "indexed treatment header", "alphabetical menu", "compact medical footer", "filter chips"),
    ("16", "grace", "Grace", "https://beauty365.com.br/", "service-commerce shelves", "shop-like service nav", "sliding product menu", "membership footer", "shelf hover lift"),
    ("17", "sculpt", "Sculpt", "https://www.gioesteticaavancada.com.br/unidade/londrina/", "local branch landing", "location-first header", "branch sheet menu", "unit footer", "local badge reveal"),
    ("18", "lumin", "Lumin", "https://www.jkesteticaavancada.com.br/", "high-contrast clinic suite", "bold split header", "panel stack menu", "contrast footer", "sharp mask transitions"),
    ("19", "verda", "Verda", "https://clinicaesteticalondrina.com.br/", "local search landing", "search-intent header", "quick action menu", "local trust footer", "search card reveal"),
    ("20", "halo", "Halo", "https://clinicapio.com.br/", "physician profile pathway", "profile-led header", "bio drawer menu", "professional profile footer", "portrait crop motion"),
    ("21", "calm", "Calm", "https://www.phiclinic.com/", "international private clinic", "concierge header", "private clinic menu", "concierge footer", "calm fade cascade"),
    ("22", "precision", "Precision", "https://www.drwassimtaktouk.com/", "consultant authority", "doctor-signature header", "consultant menu", "appointment footer", "signature trace"),
    ("23", "ritual", "Ritual", "https://skinmedical.com/", "medical skin landing", "treatment proof header", "condition menu", "medical disclosure footer", "clinical reveal"),
    ("24", "signal", "Signal", "https://fineclinic.uk/", "fine clinic calm", "ultra-minimal header", "quiet list menu", "fine-print footer", "low motion dissolve"),
    ("25", "align", "Align", "https://altamedi.com/", "treatment explorer", "explorer header", "filterable service menu", "explorer footer", "filter transition"),
    ("26", "vivant", "Vivant", "https://www.harleystreetskinclinic.com/", "Harley editorial authority", "editorial authority header", "article menu", "Harley-style footer", "editorial wipe"),
    ("27", "form", "Form", "https://www.cosmeticskinclinic.com/", "procedure library", "library header", "mega library menu", "procedure footer", "card index animation"),
    ("28", "pure", "Pure", "https://www.antiwrinkleclinic.co.uk/", "focused wrinkle education", "single-service header", "question-led menu", "education footer", "FAQ slide"),
    ("29", "solace", "Solace", "https://drnooraesthetics.co.uk/", "doctor journal", "journal doctor header", "notebook menu", "personal practice footer", "notebook page reveal"),
    ("30", "method", "Method", "https://www.sloaneclinic.com/", "appointment concierge", "concierge booking header", "booking sheet menu", "Sloane-style footer", "booking stepper"),
    ("31", "evolve", "Evolve", "https://nazarianplasticsurgery.com/", "confidence transformation narrative", "authority hero header", "confidence menu", "authority footer", "before-care timeline"),
    ("32", "serene", "Serene", "https://thenaturalresult.com/", "natural result narrative", "natural proof header", "results-safe menu", "natural results footer", "gentle result reveal"),
    ("33", "elan", "Elan", "https://premiumcareplasticsurgery.com/en/plastic-surgery-colombia/", "destination premium care", "destination header", "journey planner menu", "destination footer", "journey map reveal"),
    ("34", "flora", "Flora", "https://artisanclinics.com/", "artisan boutique clinic", "atelier header", "artisan menu", "crafted footer", "craft card motion"),
    ("35", "atelier", "Atelier", "https://silklaser.com.au/", "laser studio franchise", "laser studio header", "membership laser menu", "studio footer", "membership ticker"),
    ("36", "lumina", "Lumina", "https://www.skinlaundry.com/", "membership skincare bar", "membership header", "pass menu", "membership footer", "scroll progress wash"),
    ("37", "vellum", "Vellum", "https://skinlaundry.uk/", "treatment pass system", "pass-booking header", "pass drawer menu", "pass footer", "slot selector"),
    ("38", "origin", "Origin", "https://drdavidjack.com/", "doctor shop editorial", "doctor shop header", "shop journal menu", "shop editorial footer", "product-card drift"),
    ("39", "kindred", "Kindred", "https://www.drsturm.com/", "scientific skincare brand", "science brand header", "ingredient menu", "science footer", "molecule reveal"),
    ("40", "noble", "Noble", "https://augustinusbader.com/", "prestige product editorial", "prestige header", "formula menu", "prestige footer", "formula shimmer"),
    ("41", "vista", "Vista", "https://www.tatcha.com/", "ritual beauty storytelling", "ritual header", "ritual drawer menu", "story footer", "ritual scroll"),
    ("42", "softline", "Softline", "https://www.aesop.com/", "apothecary minimalism", "apothecary header", "text-only apothecary menu", "apothecary footer", "text reveal"),
    ("43", "meridian", "Meridian", "https://www.laprairie.com/en-int", "luxury maison skincare", "maison header", "collection menu", "maison footer", "collection fade"),
    ("44", "safeguard", "Safeguard", "https://www.lamer.com.br/", "cream skincare commerce", "cream commerce header", "cream category menu", "commerce footer", "cream layer motion"),
    ("45", "silhouette", "Silhouette", "https://111skin.com/", "clinical skincare drops", "drop-commerce header", "regimen menu", "clinical shop footer", "drop reveal"),
    ("46", "curate", "Curate", "https://111skinspa.com/", "spa menu curation", "spa services header", "spa treatment menu", "spa footer", "spa menu reveal"),
    ("47", "proof", "Proof", "https://www.shanidarden.com/", "expert routine blog", "expert routine header", "routine menu", "expert footer", "routine step reveal"),
    ("48", "signature", "Signature", "https://vintnersdaughter.com/", "botanical serum story", "botanical story header", "serum story menu", "botanical footer", "botanical line grow"),
    ("49", "wisdom", "Wisdom", "https://tataharperskincare.com/", "clean farm skincare", "farm-luxury header", "farm story menu", "clean beauty footer", "field note reveal"),
    ("50", "sovereign", "Sovereign", "https://beminimalist.co/", "minimalist ingredient lab", "ingredient lab header", "ingredient drawer menu", "minimal lab footer", "ingredient filter motion"),
]

PAGE_SPECS = [
    ("index", "Home", "index.html", "Laser, skin and advanced aesthetic care in Londrina, PR.", "A premium Sofiati direction shaped around professional evaluation, laser precision, skin quality and ethical care."),
    ("about", "About", "about.html", "Biomedical foundation, aesthetics and laser specialism.", "Franciele Sofiati is presented through clinical pathology background, aesthetics, cosmetology and laser care."),
    ("mission", "Mission", "mission.html", "A mission of natural-looking care with responsibility.", "The mission is careful, personalised care that makes technology feel precise and human."),
    ("values", "Values", "values.html", "Precision, warmth, safety and naturalness.", "The values page turns the Sofiati identity into practical decisions across evaluation, treatment and aftercare."),
    ("care", "Care", "care.html", "A structured path from evaluation to aftercare.", "The care page organises consultation, suitability, planning and responsible follow-up."),
    ("laser", "Laser", "laser.html", "Laser care explained with clinical calm.", "Laser hair removal, laser rejuvenation, technology-based treatments and aftercare are presented as evaluation-led topics."),
    ("skin", "Skin", "skin.html", "Skin quality education for clarity, comfort and confidence.", "Skin cleansing, spots and melasma education, rosacea education, flaccidity and wrinkles education sit inside professional care."),
    ("results", "Results", "results.html", "Results with responsibility and realistic expectations.", "Results are framed by individual characteristics, indication, protocol, number of sessions and aftercare."),
    ("testimonials", "Testimonials", "testimonials.html", "Approval-first social proof without invented claims.", "The testimonial system is ready for approved real stories and does not invent outcomes or quotes."),
    ("journal", "Journal", "journal.html", "Educational notes for laser, skin and aftercare.", "Journal content translates public education themes into safe, evergreen website reading."),
    ("blog", "Blog", "blog.html", "Short-form education with professional boundaries.", "The blog creates compact routes into laser, skin, consultation and aftercare questions."),
    ("faq", "FAQ", "faq.html", "Questions answered with clarity and restraint.", "The FAQ page gives useful educational answers while returning to individual professional evaluation."),
    ("contact", "Contact", "contact.html", "Contact Franciele Sofiati in Londrina, PR.", "WhatsApp, email and Instagram are presented as public contact routes without private location details."),
    ("consultation", "Consultation", "consultation.html", "Request professional evaluation before choosing a protocol.", "The consultation path helps visitors describe goals while understanding that suitability is individual."),
    ("legal", "Legal", "legal.html", "Professional boundaries for the Sofiati presentation.", "Legal copy keeps the site educational and ready for final professional review."),
    ("privacy", "Privacy", "privacy.html", "Privacy-first content for consultation and education.", "Privacy guidance protects patient media, address details and sensitive information."),
    ("cookies", "Cookies", "cookies.html", "Simple cookie preferences and no hidden tracking.", "Cookie guidance explains required preferences and inactive optional tracking."),
    ("accessibility", "Accessibility", "accessibility.html", "Accessible structure across desktop, tablet and mobile.", "Accessibility focuses on keyboard access, readable text, clear states and reduced motion."),
    ("404", "404", "404.html", "Page not found.", "A quiet recovery page returns visitors to consultation, education and contact routes."),
]

SERVICE_TERMS = [
    "Advanced aesthetic biomedicine",
    "Professional evaluation",
    "Personalised care",
    "Laser care",
    "Laser hair removal",
    "Laser rejuvenation",
    "Skin care",
    "Skin cleansing",
    "Skin quality",
    "Spots and melasma education",
    "Rosacea education",
    "Flaccidity and wrinkles education",
    "Technology-based treatments",
    "Aftercare",
    "Consultation",
    "Results with responsibility",
]

IMAGE_BY_PAGE = {
    "index": "home/sofiati-home-hero-botanical-clinical-luxury.webp",
    "about": "about/franciele-sofiati-brand-story-botanical-moodboard.webp",
    "mission": "mission/sofiati-mission-science-care-naturalness.webp",
    "values": "values/sofiati-values-care-confidence-safety-naturalness.webp",
    "care": "care/sofiati-care-botanical-clinical-brand-application.webp",
    "laser": "laser/sofiati-laser-botanical-precision-story-background.webp",
    "skin": "skin/sofiati-skin-care-soft-sage-story-background.webp",
    "results": "results/sofiati-results-ethical-expectations-botanical.webp",
    "testimonials": "testimonials/sofiati-testimonials-approval-first-contact-card.webp",
    "journal": "journal/sofiati-journal-typography-palette-system.webp",
    "blog": "blog/sofiati-blog-palette-care-education.webp",
    "faq": "faq/sofiati-faq-brand-manual-clinical-guidance.webp",
    "contact": "contact/sofiati-contact-business-card-inspired-layout.webp",
    "consultation": "consultation/sofiati-consultation-stationery-care-pathway.webp",
    "legal": "legal/sofiati-legal-monogram-pattern-sage.webp",
    "privacy": "legal/sofiati-legal-monogram-pattern-sage.webp",
    "cookies": "legal/sofiati-legal-monogram-pattern-sage.webp",
    "accessibility": "faq/sofiati-faq-brand-manual-clinical-guidance.webp",
    "404": "legal/sofiati-legal-monogram-pattern-sage.webp",
}

HOME_HERO_IMAGES = [
    "home/sofiati-home-hero-botanical-clinical-luxury.webp",
    "about/franciele-sofiati-brand-story-botanical-moodboard.webp",
    "care/sofiati-care-botanical-clinical-brand-application.webp",
    "laser/sofiati-laser-botanical-precision-story-background.webp",
    "skin/sofiati-skin-care-soft-sage-story-background.webp",
    "results/sofiati-results-ethical-expectations-botanical.webp",
    "journal/sofiati-journal-typography-palette-system.webp",
    "consultation/sofiati-consultation-stationery-care-pathway.webp",
    "contact/sofiati-contact-business-card-inspired-layout.webp",
    "values/sofiati-values-care-confidence-safety-naturalness.webp",
    "mission/sofiati-mission-science-care-naturalness.webp",
    "faq/sofiati-faq-brand-manual-clinical-guidance.webp",
]

SECTION_POOL = [
    ("Evaluation first", "Every route begins with professional evaluation, goals, history, suitability and realistic planning."),
    ("Laser precision", "Laser care is framed around indication, preparation, comfort, intervals and aftercare."),
    ("Skin quality", "Skin care includes cleansing, texture, spots, melasma education, rosacea education and barrier respect."),
    ("Technology with judgement", "Technology-based treatments are tools for carefully selected protocols, not promises."),
    ("Natural-looking direction", "Natural-looking care protects expression and avoids pressure-led aesthetic decisions."),
    ("Aftercare visibility", "Aftercare is visible because results depend on protocol, sessions, individual response and follow-up."),
    ("Privacy and approval", "No unapproved patient images, fake testimonials or private address details are used."),
    ("Londrina contact", "The public contact route is WhatsApp, email, Instagram and Londrina, PR only."),
    ("Education library", "Journal and blog content turn laser and skin topics into calm, responsible learning."),
    ("Consultation path", "The consultation call to action returns visitors to individual evaluation before treatment choice."),
]

SAFE_DISCLAIMER = (
    "Results may vary according to individual characteristics, professional evaluation, treatment indication, "
    "protocol, number of sessions and aftercare. Information on this website is educational and does not replace "
    "an individual professional evaluation."
)


@dataclass(frozen=True)
class Concept:
    number: str
    slug: str
    name: str
    url: str
    archetype: str
    header: str
    menu: str
    footer: str
    motion: str

    @property
    def folder(self) -> str:
        return f"{self.number}-{self.slug}"

    @property
    def accent_index(self) -> int:
        return int(self.number) - 1


def esc(value: object) -> str:
    return escape(str(value), quote=True)


def title_case(value: str) -> str:
    keep = {"and", "with", "for", "of", "the", "a", "an", "to"}
    words = value.replace("-", " ").split()
    return " ".join(word if idx and word.lower() in keep else word[:1].upper() + word[1:] for idx, word in enumerate(words))


def page_href(page_key: str) -> str:
    if page_key == "index":
        return "index.html"
    return f"{page_key}.html"


def nav_links(current: str, compact: bool = False) -> str:
    keys = ["index", "about", "care", "laser", "skin", "results", "blog", "faq", "consultation", "contact"]
    if compact:
        keys = ["index", "care", "laser", "skin", "consultation", "contact"]
    items = []
    for key in keys:
        label = next(label for item_key, label, *_ in PAGE_SPECS if item_key == key)
        current_attr = ' aria-current="page"' if key == current else ""
        items.append(f'<a href="{page_href(key)}"{current_attr}>{label}</a>')
    return "\n".join(items)


def rotated_sections(concept: Concept, page_key: str) -> list[tuple[str, str]]:
    start = (concept.accent_index * 3 + len(page_key)) % len(SECTION_POOL)
    chosen = [SECTION_POOL[(start + idx) % len(SECTION_POOL)] for idx in range(5)]
    if page_key == "laser":
        chosen[:3] = [
            ("Laser hair removal", "Laser hair removal is discussed through preparation, phototype considerations, session planning and aftercare."),
            ("Laser rejuvenation", "Laser rejuvenation education focuses on skin quality, collagen support and responsible expectations."),
            ("Laser care", "Laser care remains evaluation-led and technology-based treatments are explained without fixed outcomes."),
        ]
    if page_key == "skin":
        chosen[:4] = [
            ("Skin cleansing", "Skin cleansing is framed as a professional skin care category with comfort and barrier respect."),
            ("Spots and melasma education", "Spots and melasma education is presented carefully because suitability and response vary."),
            ("Rosacea education", "Rosacea education prioritises sensitivity, redness triggers and professional evaluation."),
            ("Flaccidity and wrinkles education", "Flaccidity and wrinkles education uses natural-looking language and long-view care."),
        ]
    if page_key == "results":
        chosen[:2] = [
            ("Results with responsibility", "The results page explains variables and privacy boundaries before any visual proof is considered."),
            ("What affects results", SAFE_DISCLAIMER),
        ]
    if page_key == "contact":
        chosen[:3] = [
            ("WhatsApp", f"WhatsApp: {BRAND['whatsapp']} is the primary public contact route."),
            ("Email", f"Email: {BRAND['email']} is available for formal questions and approvals."),
            ("Instagram", f"Instagram: {BRAND['instagram']} is linked for public education and brand context."),
        ]
    return chosen


def copy_assets(concept_dir: Path) -> None:
    assets_dir = concept_dir / "assets"
    if assets_dir.exists():
        shutil.rmtree(assets_dir)
    shutil.copytree(ROOT_ASSETS / "brand", assets_dir / "brand")
    shutil.copytree(ROOT_ASSETS / "images", assets_dir / "images")


def header_markup(concept: Concept, current: str) -> str:
    n = int(concept.number)
    layout = [
        "split-wordmark", "card-contact", "magazine-bar", "technical-center", "luxury-split",
        "side-rail", "proof-minimal", "monogram-center", "floating-cta", "mega-calm",
    ][(n - 1) % 10]
    return dedent(
        f"""
        <header class="site-header header-{layout}" data-header="header-{concept.number}-{concept.slug}-{layout}">
          <a class="brand-mark" href="index.html" aria-label="{esc(BRAND['name'])} home">
            <img src="assets/brand/sofiati-logo-primary-sage.png" alt="{esc(BRAND['name'])} logo">
            <span><strong>{esc(BRAND['name'])}</strong><small>{esc(BRAND['descriptor'])}</small></span>
          </a>
          <nav class="desktop-nav" aria-label="Primary navigation">
            {nav_links(current, compact=(n % 3 == 0))}
          </nav>
          <div class="header-actions">
            <a class="mini-contact" href="{BRAND['whatsapp_url']}" rel="noopener" target="_blank">WhatsApp</a>
            <button class="menu-button" type="button" data-menu-toggle aria-controls="mobile-menu" aria-expanded="false">Menu</button>
          </div>
        </header>
        """
    ).strip()


def mobile_menu_markup(concept: Concept, current: str) -> str:
    return dedent(
        f"""
        <aside class="mobile-menu" id="mobile-menu" data-menu="{concept.number}-{concept.slug}-{concept.menu.replace(' ', '-')}" aria-hidden="true">
          <div class="mobile-menu-top">
            <img src="assets/brand/sofiati-logo-primary-white.png" alt="{esc(BRAND['name'])} logo">
            <button type="button" data-menu-close>Close</button>
          </div>
          <nav aria-label="Mobile navigation">
            {nav_links(current)}
          </nav>
          <div class="mobile-menu-note">
            <strong>{esc(concept.name)} menu</strong>
            <p>{esc(concept.menu)} inspired by {esc(concept.archetype)}.</p>
          </div>
        </aside>
        """
    ).strip()


def footer_markup(concept: Concept, current: str) -> str:
    n = int(concept.number)
    cols = ["ledger", "maison", "clinical", "signature", "directory", "concierge", "apothecary"][(n - 1) % 7]
    return dedent(
        f"""
        <footer class="site-footer footer-{cols}" data-footer="footer-{concept.number}-{concept.slug}-{cols}">
          <div class="footer-brand">
            <img src="assets/brand/sofiati-logo-primary-white.png" alt="{esc(BRAND['name'])} logo">
            <p>{esc(BRAND['positioning'])}</p>
          </div>
          <nav aria-label="Footer navigation">
            {nav_links(current)}
            <a href="legal.html">Legal</a>
            <a href="privacy.html">Privacy</a>
            <a href="cookies.html">Cookies</a>
            <a href="accessibility.html">Accessibility</a>
          </nav>
          <address>
            <span>{esc(BRAND['credential'])}</span>
            <a href="{BRAND['whatsapp_url']}" rel="noopener" target="_blank">WhatsApp: {esc(BRAND['whatsapp'])}</a>
            <a href="mailto:{BRAND['email']}">{esc(BRAND['email'])}</a>
            <a href="{BRAND['instagram_url']}" rel="noopener" target="_blank">{esc(BRAND['instagram'])}</a>
            <a href="{BRAND['domain_url']}" rel="noopener" target="_blank">{esc(BRAND['domain'])}</a>
            <span>{esc(BRAND['location'])}</span>
          </address>
        </footer>
        """
    ).strip()


def concept_switcher_partial(concept: Concept) -> str:
    return dedent(
        f"""
        <div class="concept-marker" data-concept-marker="{concept.folder}">
          <span>Concept {concept.number} / 50</span>
          <strong>{esc(concept.name)}</strong>
          <a href="design-notes.md">Design notes</a>
        </div>
        """
    ).strip()


def service_panel(concept: Concept) -> str:
    items = "".join(f"<li>{esc(term)}</li>" for term in SERVICE_TERMS)
    return f'<section class="service-architecture" aria-label="Sofiati service architecture"><h2>Sofiati service architecture</h2><ul>{items}</ul><p>{SAFE_DISCLAIMER}</p></section>'


def page_component(concept: Concept, page_key: str, index: int, title: str, copy: str) -> str:
    variant = (concept.accent_index + index) % 8
    if variant == 0:
        return f'<article class="panel panel-editorial"><span>{index:02d}</span><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>'
    if variant == 1:
        return f'<article class="panel panel-card"><h3>{esc(title)}</h3><p>{esc(copy)}</p><a href="consultation.html">Discuss in consultation</a></article>'
    if variant == 2:
        return f'<article class="panel panel-spec"><small>{concept.number}.{index:02d}</small><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>'
    if variant == 3:
        return f'<details class="panel panel-accordion" {"open" if index == 1 else ""}><summary>{esc(title)}</summary><p>{esc(copy)}</p></details>'
    if variant == 4:
        return f'<article class="panel panel-horizontal"><h3>{esc(title)}</h3><p>{esc(copy)}</p><span>{esc(concept.motion)}</span></article>'
    if variant == 5:
        return f'<article class="panel panel-minimal"><h3>{esc(title)}</h3><p>{esc(copy)}</p></article>'
    if variant == 6:
        return f'<article class="panel panel-numbered"><b>{index:02d}</b><div><h3>{esc(title)}</h3><p>{esc(copy)}</p></div></article>'
    return f'<article class="panel panel-note"><h3>{esc(title)}</h3><p>{esc(copy)}</p><em>{esc(concept.archetype)}</em></article>'


def page_body(concept: Concept, page_key: str, label: str, headline: str, intro: str) -> str:
    n = int(concept.number)
    order_name = [
        "hero-proof-services-journal-contact",
        "hero-contact-services-proof-journal",
        "hero-journal-services-consult-proof",
        "hero-technology-proof-services-contact",
        "hero-ritual-journal-services-consult",
        "hero-story-services-proof-contact",
        "hero-grid-proof-services-faq",
        "hero-monogram-services-journal-contact",
        "hero-consult-services-proof-journal",
        "hero-minimal-services-faq-contact",
    ][(n + len(page_key)) % 10] + f"-{concept.number}"
    img = IMAGE_BY_PAGE.get(page_key, IMAGE_BY_PAGE["index"])
    if page_key == "index":
        img = HOME_HERO_IMAGES[(n - 1) % len(HOME_HERO_IMAGES)]
    mosaic_images = [
        HOME_HERO_IMAGES[(n + offset) % len(HOME_HERO_IMAGES)]
        for offset in (2, 5, 8)
    ]
    hero_mode = (n - 1) % 12
    sections = rotated_sections(concept, page_key)
    section_html = "\n".join(page_component(concept, page_key, idx, title, copy) for idx, (title, copy) in enumerate(sections, start=1))
    cta = dedent(
        f"""
        <section class="consultation-band">
          <p>{esc(BRAND['credential'])} · {esc(BRAND['location'])}</p>
          <h2>Professional evaluation before protocol selection.</h2>
          <a class="button button-primary" href="consultation.html">Request consultation</a>
          <a class="button button-soft" href="{BRAND['whatsapp_url']}" rel="noopener" target="_blank">WhatsApp</a>
        </section>
        """
    ).strip()
    form = ""
    if page_key in {"contact", "consultation"}:
        form = dedent(
            f"""
            <section class="form-section">
              <h2>Consultation request</h2>
              <form data-consultation-form>
                <label>Name<input name="name" autocomplete="name" required></label>
                <label>Email<input name="email" type="email" autocomplete="email" required></label>
                <label>Treatment interest<select name="interest"><option>Professional evaluation</option><option>Laser care</option><option>Skin care</option><option>Results with responsibility</option></select></label>
                <label>Message<textarea name="message" required></textarea></label>
                <button class="button button-primary" type="submit">Send request</button>
                <p class="form-status" role="status"></p>
              </form>
            </section>
            """
        ).strip()
    faq = ""
    if page_key == "faq":
        faq = dedent(
            """
            <section class="faq-cluster">
              <h2>Common questions</h2>
              <details open><summary>Do results vary?</summary><p>Yes. Results vary according to individual characteristics, indication, protocol, sessions and aftercare.</p></details>
              <details><summary>Can I choose a laser directly?</summary><p>Laser suitability should be discussed through professional evaluation before treatment selection.</p></details>
              <details><summary>Is there a public address?</summary><p>The site uses Londrina, PR only and does not publish private location details.</p></details>
            </section>
            """
        ).strip()
    responsible_note = ""
    if page_key in {"laser", "skin", "results", "consultation"}:
        responsible_note = (
            '<section class="responsible-note" aria-label="Responsible results note">'
            f"<h2>Responsible aesthetic information</h2><p>{esc(SAFE_DISCLAIMER)}</p>"
            "</section>"
        )
    return dedent(
        f"""
        <main id="main" class="page-layout layout-{(n - 1) % 50:02d}" data-section-order="{order_name}">
          <section class="hero hero-{(n + len(label)) % 13:02d} hero-mode-{hero_mode:02d}" data-hero="hero-{concept.number}-{concept.slug}">
            <span class="hero-index" aria-hidden="true">{concept.number}</span>
            <img class="hero-monogram" src="assets/brand/sofiati-monogram-bronze.png" alt="">
            <div class="hero-copy">
              <p class="eyebrow">Concept {concept.number} · {esc(concept.name)} · {esc(label)}</p>
              <h1>{esc(headline if page_key != "index" else f"{concept.name}: {title_case(concept.archetype)} for Sofiati.")}</h1>
              <p>{esc(intro if page_key != "index" else f"{intro} This standalone direction uses a {concept.header}, {concept.menu} and {concept.footer}.")}</p>
              <div class="hero-actions">
                <a class="button button-primary" href="consultation.html">Request consultation</a>
                <a class="button button-soft" href="laser.html">Explore laser care</a>
              </div>
            </div>
            <figure class="hero-visual">
              <img src="assets/images/{esc(img)}" alt="Sofiati {esc(label)} visual for {esc(concept.name)}">
              <figcaption>{esc(concept.archetype)} · {esc(concept.motion)}</figcaption>
            </figure>
            <div class="hero-mosaic" aria-hidden="true">
              <img src="assets/images/{esc(mosaic_images[0])}" alt="">
              <img src="assets/images/{esc(mosaic_images[1])}" alt="">
              <img src="assets/images/{esc(mosaic_images[2])}" alt="">
            </div>
          </section>
          {service_panel(concept) if page_key in {"index", "care"} else ""}
          <section class="content-system content-system-{(n + len(page_key)) % 11:02d}">
            <div class="section-heading">
              <p class="eyebrow">{esc(concept.archetype)}</p>
              <h2>{esc(label)} sections designed for {esc(concept.name)}</h2>
            </div>
            <div class="component-grid component-grid-{(n - 1) % 9:02d}">
              {section_html}
            </div>
          </section>
          {faq}
          {form}
          {responsible_note}
          {cta}
        </main>
        """
    ).strip()


def html_page(concept: Concept, page_spec: tuple[str, str, str, str, str]) -> str:
    page_key, label, filename, headline, intro = page_spec
    title = f"{label} | {concept.number} {concept.name} | Franciele Sofiati"
    description = f"{label} page for {concept.name}, a standalone Sofiati concept for laser, skin and advanced aesthetic care in Londrina, PR."
    header = header_markup(concept, page_key)
    menu = mobile_menu_markup(concept, page_key)
    footer = footer_markup(concept, page_key)
    body = page_body(concept, page_key, label, headline, intro)
    json_ld = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "name": title,
        "description": description,
        "url": f"{BRAND['domain_url']}/concepts/{concept.folder}/{filename}",
        "inLanguage": "en",
        "about": {
            "@type": "Person",
            "name": BRAND["name"],
            "jobTitle": BRAND["descriptor"],
            "identifier": BRAND["credential"],
        },
    }
    return dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>{esc(title)}</title>
          <meta name="description" content="{esc(description)}">
          <link rel="canonical" href="{BRAND['domain_url']}/concepts/{concept.folder}/{filename}">
          <meta property="og:title" content="{esc(title)}">
          <meta property="og:description" content="{esc(description)}">
          <meta property="og:image" content="assets/images/home/sofiati-home-hero-botanical-clinical-luxury.webp">
          <link rel="icon" href="assets/brand/sofiati-favicon.svg" type="image/svg+xml">
          <link rel="stylesheet" href="css/style.css">
          <script type="application/ld+json">{json.dumps(json_ld, ensure_ascii=False, separators=(",", ":"))}</script>
        </head>
        <body class="concept concept-{concept.slug} page-{page_key}" data-concept="{concept.folder}" data-layout="{concept.archetype}" data-header="{concept.header}" data-footer="{concept.footer}" data-menu="{concept.menu}">
          <a class="skip-link" href="#main">Skip to main content</a>
          {header}
          {menu}
          {body}
          {footer}
          <script src="js/main.js" defer></script>
        </body>
        </html>
        """
    )


def color_mix(index: int) -> dict[str, str]:
    accents = ["#9A6B35", "#798A80", "#879588", "#8E7B56", "#734011", "#A2AE9F", "#6F8377", "#A17B52", "#7C8E9B", "#B9843D"]
    return {
        "accent": accents[index % len(accents)],
        "deep": ["#252321", "#344039", "#2E3631", "#3A3128", "#273332"][index % 5],
        "soft": ["#F8F7F2", "#F3EFE5", "#F8F4EA", "#EEE8DC", "#F7F2E8"][index % 5],
    }


def hero_mode_css(mode: int, idx: int, radius: int) -> str:
    base = ".hero-mosaic,.hero-index,.hero-monogram{display:none}.hero-mosaic img{width:100%;height:100%;object-fit:cover}"
    if mode == 0:
        return base + ".hero{border-bottom:1px solid var(--line)}"
    if mode == 1:
        return base + ".hero{width:100%;min-height:100vh;padding:0 max(18px,calc((100vw - 1240px)/2));grid-template-columns:minmax(0,760px);align-content:end;color:white;isolation:isolate}.hero:after{content:\"\";position:absolute;inset:0;background:linear-gradient(90deg,rgba(37,35,33,.72),rgba(37,35,33,.22) 56%,rgba(37,35,33,.08));z-index:-1}.hero-copy{z-index:2;padding:clamp(90px,18vw,220px) 0 clamp(40px,8vw,96px)}.hero-copy>p:not(.eyebrow),.hero .eyebrow{color:rgba(255,255,255,.82)}.hero-visual{position:absolute;inset:0;min-height:100%;border-radius:0;box-shadow:none;z-index:-2}.hero-visual img{opacity:.86;mix-blend-mode:normal}.hero-visual figcaption{left:auto;width:min(360px,calc(100% - 32px));background:rgba(37,35,33,.64);color:white}"
    if mode == 2:
        return base + ".hero{grid-template-columns:1fr;text-align:center;justify-items:center;min-height:92vh}.hero-copy{max-width:920px;position:relative;z-index:2}.hero-actions{justify-content:center}.hero-visual{position:absolute;inset:12% 18%;min-height:auto;height:auto;opacity:.16;box-shadow:none;border-radius:50%;z-index:0}.hero-monogram{display:block;width:min(220px,34vw);opacity:.22;margin-bottom:-18px}.hero-copy,.hero-monogram{position:relative;z-index:2}.hero-visual figcaption{display:none}"
    if mode == 3:
        return base + f".hero{{grid-template-columns:minmax(0,1fr) minmax(240px,380px);align-items:end;min-height:86vh;padding-bottom:clamp(42px,8vw,100px)}}.hero-copy h1{{font-size:clamp(3.4rem,9vw,8.5rem)}}.hero-visual{{min-height:clamp(220px,34vw,440px);align-self:end;border-radius:{radius if radius < 30 else 18}px}}.hero-index{{display:block;position:absolute;right:0;top:clamp(80px,14vw,160px);font-family:Georgia,serif;font-size:clamp(8rem,22vw,18rem);line-height:.8;color:color-mix(in srgb,var(--accent) 18%,transparent);z-index:-1}}"
    if mode == 4:
        return base + ".hero{grid-template-columns:.82fr 1.18fr;min-height:94vh}.hero-visual{display:none}.hero-mosaic{display:grid;grid-template-columns:1fr 1fr;grid-template-rows:1fr 1fr;gap:10px;min-height:clamp(360px,54vw,720px)}.hero-mosaic img{border-radius:28px;box-shadow:var(--shadow)}.hero-mosaic img:first-child{grid-row:1/3}.hero-mosaic img:nth-child(2){border-radius:999px 999px 20px 20px}.hero-mosaic img:nth-child(3){border-radius:20px 80px 20px 80px}"
    if mode == 5:
        return base + ".hero{width:100%;grid-template-columns:88px minmax(0,1fr) minmax(280px,42vw);gap:clamp(20px,4vw,60px);padding-left:max(18px,calc((100vw - 1320px)/2));padding-right:max(18px,calc((100vw - 1320px)/2))}.hero-index{display:block;writing-mode:vertical-rl;text-orientation:mixed;font-family:Georgia,serif;font-size:clamp(4rem,10vw,9rem);color:var(--accent);opacity:.45;align-self:center}.hero-visual{min-height:100vh;border-radius:0;box-shadow:none}.hero-visual figcaption{bottom:32px;left:32px;right:32px}"
    if mode == 6:
        return base + ".hero{width:100%;min-height:100vh;background:linear-gradient(135deg,var(--ink),color-mix(in srgb,var(--deep-sage) 80%,black));color:white;padding-left:max(18px,calc((100vw - 1180px)/2));padding-right:max(18px,calc((100vw - 1180px)/2));grid-template-columns:.72fr 1fr}.hero-copy>p:not(.eyebrow),.hero .eyebrow{color:rgba(255,255,255,.78)}.hero-visual{box-shadow:none;border:1px solid rgba(255,255,255,.22);background:rgba(255,255,255,.06)}.hero-visual img{opacity:.72;mix-blend-mode:screen;filter:saturate(.7)}.button-soft{background:rgba(255,255,255,.14);color:white;border-color:rgba(255,255,255,.32)}"
    if mode == 7:
        return base + ".hero{grid-template-columns:1fr 1fr;min-height:92vh}.hero-visual{transform:rotate(-2deg);border-radius:12px;box-shadow:18px 18px 0 color-mix(in srgb,var(--accent) 18%,white)}.hero-mosaic{display:block;position:absolute;right:8%;bottom:8%;width:min(220px,26vw);height:min(220px,26vw);border-radius:50%;overflow:hidden;box-shadow:var(--shadow)}.hero-mosaic img:not(:first-child){display:none}"
    if mode == 8:
        return base + ".hero{grid-template-columns:1fr;align-content:start;min-height:auto;padding-top:clamp(28px,5vw,70px)}.hero-visual{order:-1;width:100%;min-height:clamp(240px,32vw,420px);border-radius:0 0 120px 120px}.hero-copy{width:min(980px,100%);padding-top:clamp(28px,5vw,56px)}.hero-copy h1{max-width:860px}"
    if mode == 9:
        return base + ".hero{grid-template-columns:minmax(280px,.68fr) minmax(0,1.32fr);min-height:92vh}.hero-copy{order:2;border-left:1px solid var(--line);padding-left:clamp(24px,5vw,72px)}.hero-visual{order:1;min-height:clamp(420px,64vw,780px);border-radius:999px 999px 12px 12px}.hero-actions{justify-content:flex-start}"
    if mode == 10:
        return base + ".hero{grid-template-columns:.64fr minmax(0,1fr) .64fr;min-height:90vh}.hero-copy{grid-column:2;text-align:center}.hero-actions{justify-content:center}.hero-visual{grid-column:1;grid-row:1;min-height:clamp(280px,36vw,560px);border-radius:8px}.hero-mosaic{display:grid;grid-column:3;grid-row:1;gap:10px;align-self:center}.hero-mosaic img{height:clamp(110px,12vw,180px);border-radius:999px}.hero-mosaic img:nth-child(2){border-radius:8px}.hero-mosaic img:nth-child(3){border-radius:80px 8px}"
    return base + ".hero{width:100%;min-height:96vh;grid-template-columns:1fr;place-items:center;padding-left:18px;padding-right:18px;isolation:isolate}.hero-visual{position:absolute;inset:0;min-height:100%;border-radius:0;opacity:.24;box-shadow:none;z-index:-2}.hero-visual img{mix-blend-mode:multiply}.hero-copy{max-width:850px;background:rgba(248,247,242,.88);backdrop-filter:blur(20px);border:1px solid var(--line);padding:clamp(26px,5vw,70px);border-radius:8px;box-shadow:var(--shadow);text-align:center}.hero-actions{justify-content:center}.hero-monogram{display:block;position:absolute;width:min(140px,26vw);top:18%;opacity:.3}"


def css_for(concept: Concept) -> str:
    idx = concept.accent_index
    colors = color_mix(idx)
    radius = [2, 4, 8, 12, 18, 26, 999][idx % 7]
    hero_css = hero_mode_css(idx % 12, idx, radius)
    page_max = [1160, 1240, 1320, 1080, 1440][idx % 5]
    nav_position = ["sticky", "sticky", "relative", "sticky", "fixed"][idx % 5]
    hero_grid = [
        "1.05fr .95fr", ".78fr 1.22fr", "1fr 1fr", ".68fr 1.32fr", "1.32fr .68fr",
        ".9fr 1.1fr", "1.18fr .82fr", ".82fr 1.18fr", "1fr .72fr", ".72fr 1fr",
    ][idx % 10]
    component_cols = [
        "repeat(5,minmax(0,1fr))", "repeat(2,minmax(0,1fr))", "minmax(0,1.2fr) repeat(2,minmax(0,.9fr))",
        "repeat(auto-fit,minmax(220px,1fr))", "1fr", "repeat(3,minmax(0,1fr))",
        "minmax(280px,.7fr) minmax(0,1.3fr)", "repeat(auto-fit,minmax(160px,1fr))", "2fr 1fr", "1fr 2fr",
    ][idx % 10]
    hero_shape = [
        "border-radius:0 0 80px 0;", "border-radius:28px;", "border-radius:0;", "border-radius:160px 8px 160px 8px;",
        "border-radius:999px 999px 12px 12px;", "border-radius:50%;aspect-ratio:1;", "clip-path:polygon(0 0,100% 7%,92% 100%,0 92%);",
        "border-radius:8px 80px 8px 80px;", "border-radius:8px;", "border-radius:120px;",
    ][idx % 10]
    return dedent(
        f"""\
        /* {concept.number} {concept.name}: standalone Sofiati design system */
        :root {{
          --sage:#A2AE9F;
          --deep-sage:#798A80;
          --ivory:#F3EFE5;
          --cream:#F8F4EA;
          --soft-white:#F8F7F2;
          --bronze:#9A6B35;
          --champagne:#FDE3B0;
          --ink:{colors['deep']};
          --muted:#706B63;
          --accent:{colors['accent']};
          --surface:{colors['soft']};
          --line:rgba(37,35,33,.14);
          --shadow:0 24px 80px rgba(37,35,33,.13);
          --page:min({page_max}px,calc(100% - 32px));
          --radius:{radius}px;
        }}
        *{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:var(--surface);color:var(--ink);font-family:Inter,ui-sans-serif,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.5}} img{{max-width:100%;display:block}} a{{color:inherit}} button,input,select,textarea{{font:inherit}} h1,h2,h3{{font-family:Georgia,"Times New Roman",serif;font-weight:400;line-height:.98;letter-spacing:0}} h1{{font-size:clamp(2.7rem,7vw,6.8rem);margin:0}} h2{{font-size:clamp(2rem,4vw,4.2rem);margin:0}} h3{{font-size:clamp(1.25rem,2vw,2rem);margin:.2rem 0}} p{{margin:0}} .skip-link{{position:absolute;left:12px;top:12px;z-index:999;background:var(--ink);color:white;padding:10px;transform:translateY(-160%)}}.skip-link:focus{{transform:none}}
        .site-header{{position:{nav_position};top:{'14px' if idx % 5 == 4 else '0'};z-index:30;width:{'min(1180px,calc(100% - 24px))' if idx % 5 == 4 else '100%'};margin:auto;display:grid;grid-template-columns:{'auto 1fr auto' if idx % 4 else '1fr auto 1fr'};align-items:center;gap:18px;padding:{'14px 18px' if idx % 3 else '8px 28px'};background:{'rgba(248,247,242,.88)' if idx % 2 else 'color-mix(in srgb,var(--surface) 86%,white)'};border-bottom:1px solid var(--line);backdrop-filter:blur(18px);{'border-radius:999px;' if idx % 5 == 4 else ''}}}
        .brand-mark{{display:flex;align-items:center;gap:12px;text-decoration:none;min-width:0;{'justify-self:center;flex-direction:column;text-align:center;' if idx % 4 == 0 else ''}}}.brand-mark img{{width:clamp(120px,14vw,210px);max-height:52px;object-fit:contain}}.brand-mark strong{{font-family:Georgia,serif;font-size:1rem;font-weight:400}}.brand-mark small{{display:block;text-transform:uppercase;font-size:.58rem;letter-spacing:.16em;color:var(--muted)}}.desktop-nav{{display:flex;justify-content:center;gap:{'4px' if idx % 2 else '14px'};flex-wrap:wrap}}.desktop-nav a{{text-decoration:none;min-height:34px;display:inline-flex;align-items:center;padding:7px 9px;border-radius:{radius if radius < 40 else 999}px;font-size:.78rem;{'text-transform:uppercase;letter-spacing:.1em;' if idx % 3 == 0 else ''}}}.desktop-nav a[aria-current=page],.desktop-nav a:hover{{background:white;box-shadow:inset 0 0 0 1px var(--line)}}.header-actions{{display:flex;align-items:center;justify-content:end;gap:8px}}.mini-contact,.menu-button,.button{{border:1px solid var(--line);border-radius:{radius if radius < 40 else 999}px;min-height:42px;padding:10px 14px;background:white;text-decoration:none;font-weight:700;color:var(--ink)}}.menu-button{{display:none}}.button-primary{{background:var(--ink);color:white;border-color:var(--ink)}}.button-soft{{background:color-mix(in srgb,var(--accent) 22%,white);color:var(--ink)}}
        .mobile-menu{{position:fixed;inset:{'0 0 auto 0' if idx % 4 == 1 else '0'};z-index:60;min-height:{'72vh' if idx % 4 == 1 else '100vh'};display:grid;grid-template-rows:auto 1fr auto;gap:24px;padding:24px;background:linear-gradient({120 + idx * 11}deg,var(--deep-sage),color-mix(in srgb,var(--accent) 62%,var(--ink)));color:white;transform:{'translateY(-104%)' if idx % 4 == 1 else 'translateX(104%)' if idx % 4 == 2 else 'scale(.94)' if idx % 4 == 3 else 'translateY(104%)'};opacity:0;pointer-events:none;transition:transform .44s ease,opacity .44s ease}}.mobile-menu.is-open{{transform:none;opacity:1;pointer-events:auto}}.mobile-menu-top{{display:flex;align-items:center;justify-content:space-between;gap:18px}}.mobile-menu-top img{{width:210px}}.mobile-menu button{{background:transparent;color:white;border:1px solid rgba(255,255,255,.4);border-radius:999px;padding:10px 16px}}.mobile-menu nav{{display:grid;align-content:center;gap:8px;{'grid-template-columns:repeat(2,minmax(0,1fr));' if idx % 5 == 0 else ''}}}.mobile-menu nav a{{font-family:Georgia,serif;font-size:clamp(2rem,8vw,5rem);line-height:1;text-decoration:none}}.mobile-menu-note{{max-width:420px;color:rgba(255,255,255,.82)}}
        .page-layout{{overflow:hidden}}.hero{{position:relative;min-height:calc(100vh - 84px);display:grid;grid-template-columns:{hero_grid};align-items:center;gap:clamp(24px,5vw,80px);width:var(--page);margin:auto;padding:clamp(42px,8vw,112px) 0}}.hero-copy{{display:grid;gap:20px;{'order:2;' if idx % 6 == 2 else ''}}}.eyebrow{{text-transform:uppercase;font-size:.72rem;letter-spacing:.14em;color:var(--muted);font-weight:800}}.hero-copy>p:not(.eyebrow){{max-width:64ch;color:var(--muted)}}.hero-actions{{display:flex;flex-wrap:wrap;gap:10px}}.hero-visual{{position:relative;margin:0;min-height:clamp(280px,46vw,680px);overflow:hidden;background:color-mix(in srgb,var(--sage) 42%,white);box-shadow:var(--shadow);{hero_shape}}}.hero-visual:before{{content:"";position:absolute;inset:18%;z-index:2;background:url("../assets/brand/sofiati-monogram-white.png") center/contain no-repeat;opacity:.16;pointer-events:none}}.hero-visual img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;{'filter:saturate(.82) contrast(.96);' if idx % 2 else 'mix-blend-mode:multiply;opacity:.88;'}}}.hero-visual figcaption{{position:absolute;left:16px;right:16px;bottom:16px;z-index:3;padding:10px 13px;border-radius:{radius if radius < 30 else 999}px;background:rgba(248,247,242,.86);font-size:.78rem;color:var(--ink)}}
        {hero_css}
        .service-architecture,.content-system,.faq-cluster,.form-section,.responsible-note,.consultation-band{{width:var(--page);margin:auto;padding:clamp(48px,8vw,108px) 0;border-top:1px solid var(--line)}}.service-architecture{{display:grid;grid-template-columns:{'.55fr 1.45fr' if idx % 2 else '1fr'};gap:22px}}.service-architecture ul{{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;list-style:none;margin:0;padding:0}}.service-architecture li{{border:1px solid var(--line);background:white;border-radius:{radius if radius < 24 else 24}px;padding:11px 12px;font-weight:700}}.service-architecture p{{grid-column:1/-1;color:var(--muted);max-width:80ch}}.section-heading{{display:grid;grid-template-columns:{'.75fr 1.25fr' if idx % 3 else '1fr'};gap:16px;margin-bottom:24px}}.component-grid{{display:grid;grid-template-columns:{component_cols};gap:clamp(10px,2vw,22px)}}.panel{{min-height:{130 + (idx % 5) * 18}px;border:1px solid var(--line);background:{'white' if idx % 4 else 'color-mix(in srgb,var(--accent) 8%,white)'};border-radius:{radius if radius < 32 else 26}px;padding:clamp(16px,2.5vw,30px);box-shadow:{'0 12px 40px rgba(37,35,33,.06)' if idx % 2 else 'none'};display:grid;align-content:start;gap:10px}}.panel-editorial{{border-left:4px solid var(--accent)}}.panel-card{{transform:translateY(var(--lift,0))}}.panel-card:hover{{--lift:-4px}}.panel-spec{{font-family:ui-monospace,SFMono-Regular,Menlo,monospace}}.panel-horizontal{{grid-template-columns:{'1fr 1fr' if idx % 2 else '1fr'};align-items:end}}.panel-numbered{{grid-template-columns:48px 1fr}}.panel-numbered b{{font-family:Georgia,serif;font-size:2.4rem;color:var(--accent)}}.panel-note em{{color:var(--muted)}}details.panel summary{{cursor:pointer;font-weight:800}}.faq-cluster{{display:grid;gap:12px}}.form-section form{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px;max-width:860px}}.form-section label{{display:grid;gap:6px;font-weight:800}}.form-section input,.form-section select,.form-section textarea{{width:100%;border:1px solid var(--line);border-radius:{radius if radius < 20 else 20}px;padding:12px;background:white}}.form-section textarea{{min-height:140px;grid-column:1/-1}}.form-section label:has(textarea),.form-section button,.form-status{{grid-column:1/-1}}.responsible-note{{display:grid;grid-template-columns:{'0.7fr 1.3fr' if idx % 2 else '1fr'};gap:16px;color:var(--muted);background:{'color-mix(in srgb,var(--sage) 12%,white)' if idx % 4 == 1 else 'transparent'};padding-left:{'20px' if idx % 4 == 1 else '0'};padding-right:{'20px' if idx % 4 == 1 else '0'}}}.responsible-note h2{{color:var(--ink)}}.consultation-band{{display:flex;align-items:center;justify-content:space-between;gap:18px;flex-wrap:wrap;background:{'color-mix(in srgb,var(--accent) 10%,var(--surface))' if idx % 2 else 'transparent'};padding-left:{'24px' if idx % 2 else '0'};padding-right:{'24px' if idx % 2 else '0'}}}.consultation-band h2{{max-width:680px}}
        .site-footer{{margin-top:clamp(42px,6vw,90px);background:var(--ink);color:white;padding:clamp(44px,8vw,100px) max(18px,calc((100vw - {page_max}px)/2));display:grid;grid-template-columns:{'.9fr 1fr .7fr' if idx % 3 else '1fr'};gap:clamp(22px,5vw,70px)}}.site-footer img{{width:min(280px,80vw);margin-bottom:18px}}.site-footer nav{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px 20px}}.site-footer a{{color:rgba(255,255,255,.82);text-decoration:none}}.site-footer address{{font-style:normal;display:grid;gap:8px;color:rgba(255,255,255,.78)}}.concept-marker{{position:fixed;right:12px;bottom:12px;z-index:20;display:flex;gap:8px;align-items:center;border:1px solid var(--line);background:rgba(248,247,242,.86);backdrop-filter:blur(14px);border-radius:999px;padding:8px 12px;font-size:.76rem}}
        .is-visible{{animation:reveal-{concept.slug} .72s ease both}}@keyframes reveal-{concept.slug}{{from{{opacity:0;transform:translateY({12 + idx % 20}px) scale({'.98' if idx % 2 else '1'});}}to{{opacity:1;transform:none;}}}}
        body[data-js-ready="true"] .sticky-contact{{transform:translate(-50%,0)}}.sticky-contact{{position:fixed;left:50%;bottom:12px;z-index:25;transform:translate(-50%,120%);transition:transform .4s ease;background:var(--ink);color:white;border-radius:999px;padding:10px 14px;text-decoration:none;box-shadow:var(--shadow)}}
        @media(max-width:980px){{.site-header{{grid-template-columns:auto auto;position:sticky;top:0;width:100%;border-radius:0}}.desktop-nav,.mini-contact{{display:none}}.menu-button{{display:inline-flex}}.hero,.service-architecture,.section-heading,.responsible-note,.site-footer{{grid-template-columns:1fr}}.hero{{min-height:auto;padding-top:34px}}.hero-index{{display:none}}.hero-mosaic{{grid-template-columns:1fr 1fr;min-height:auto}}.component-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.form-section form{{grid-template-columns:1fr}}}}
        @media(max-width:620px){{h1{{font-size:clamp(2.25rem,13vw,4.1rem)}}.hero{{grid-template-columns:1fr;gap:18px;width:var(--page);padding-left:0;padding-right:0}}.hero-visual{{min-height:{220 + (idx % 7) * 14}px;{'order:-1;' if idx % 3 == 0 else ''}}}.hero-mosaic{{display:none}}.hero-monogram{{max-width:120px}}.sticky-contact{{display:none}}.component-grid,.service-architecture ul{{grid-template-columns:1fr}}.panel-horizontal,.panel-numbered{{grid-template-columns:1fr}}.site-footer nav{{grid-template-columns:1fr}}.consultation-band{{align-items:stretch;flex-direction:column}}}}
        """
    )


def js_for(concept: Concept) -> str:
    idx = concept.accent_index
    observer_mode = ["threshold", "stagger", "line", "soft", "snap"][idx % 5]
    menu_mode = ["overlay", "sheet", "drawer", "scale", "cascade"][idx % 5]
    return dedent(
        f"""\
        (() => {{
          const concept = {json.dumps(concept.folder)};
          const menuMode = {json.dumps(menu_mode)};
          const observerMode = {json.dumps(observer_mode)};
          document.body.dataset.jsReady = "true";

          const menu = document.querySelector("#mobile-menu");
          const open = document.querySelector("[data-menu-toggle]");
          const close = document.querySelector("[data-menu-close]");
          const setMenu = (active) => {{
            if (!menu) return;
            menu.classList.toggle("is-open", active);
            menu.setAttribute("aria-hidden", String(!active));
            open?.setAttribute("aria-expanded", String(active));
            document.body.classList.toggle("menu-active-" + menuMode, active);
          }};
          open?.addEventListener("click", () => setMenu(true));
          close?.addEventListener("click", () => setMenu(false));
          menu?.querySelectorAll("a").forEach((link, index) => {{
            link.style.setProperty("--menu-index", index);
            link.addEventListener("click", () => setMenu(false));
          }});

          const panels = [...document.querySelectorAll(".panel, .service-architecture, .responsible-note, .consultation-band")];
          if ("IntersectionObserver" in window) {{
            const io = new IntersectionObserver((entries) => {{
              entries.forEach((entry) => {{
                if (!entry.isIntersecting) return;
                const delay = observerMode === "stagger" ? (panels.indexOf(entry.target) % 7) * 70 : 0;
                entry.target.style.transitionDelay = delay + "ms";
                entry.target.classList.add("is-visible");
                io.unobserve(entry.target);
              }});
            }}, {{ threshold: observerMode === "threshold" ? 0.22 : 0.12 }});
            panels.forEach((panel) => io.observe(panel));
          }} else {{
            panels.forEach((panel) => panel.classList.add("is-visible"));
          }}

          document.querySelectorAll("details").forEach((detail) => {{
            detail.addEventListener("toggle", () => {{
              if (detail.open && observerMode === "snap") {{
                detail.scrollIntoView({{ block: "nearest", behavior: "smooth" }});
              }}
            }});
          }});

          document.querySelectorAll("[data-consultation-form]").forEach((form) => {{
            form.addEventListener("submit", (event) => {{
              event.preventDefault();
              const status = form.querySelector(".form-status");
              if (status) status.textContent = "Thank you. This static concept keeps requests local; WhatsApp is available for a direct consultation request.";
            }});
          }});

          const sticky = document.createElement("a");
          sticky.className = "sticky-contact";
          sticky.href = "consultation.html";
          sticky.textContent = concept + " consultation";
          document.body.appendChild(sticky);
          let lastY = 0;
          window.addEventListener("scroll", () => {{
            const active = window.scrollY > 520 && window.scrollY >= lastY;
            sticky.style.opacity = active ? "1" : ".82";
            lastY = window.scrollY;
          }}, {{ passive: true }});
        }})();
        """
    )


def design_notes(concept: Concept) -> str:
    return dedent(
        f"""\
        Concept name:
        {concept.number} — {concept.name}

        Assigned inspiration URL:
        {concept.url}

        What was studied:
        The concept studies the reference as a structural prompt for {concept.archetype}: navigation hierarchy, first-screen rhythm, service grouping, mobile menu posture, footer density and premium pacing. No protected text, brand assets, code or photography from the reference is used.

        How the header differs from the other concepts:
        This concept uses a {concept.header}. The header is assigned the unique runtime marker `header-{concept.number}-{concept.slug}` and a concept-specific CSS composition.

        How the hero differs from the other concepts:
        The hero is shaped around {concept.archetype}, with concept-specific grid, image treatment, radius, motion timing and headline structure.

        How the page layout differs from the other concepts:
        Page sections use a unique section order marker, component grid rhythm and panel mix generated for {concept.name}. The flat pages are not routed through shared root templates.

        How the mobile menu differs from the other concepts:
        The mobile menu uses a {concept.menu} with local JavaScript in `js/main.js` and local markup in `partials/mobile-menu.html`.

        How the footer differs from the other concepts:
        The footer uses a {concept.footer}, local contact hierarchy and concept-specific footer marker `footer-{concept.number}-{concept.slug}`.

        How the motion differs from the other concepts:
        Motion is based on {concept.motion}. The local `main.js` sets unique menu and reveal behaviour for this concept.

        How Sofiati’s brand identity was applied:
        Sage green, ivory, cream, bronze/champagne accents, the Sofiati logo system, FS monogram assets, botanical imagery, clinical calm and responsible advanced aesthetic biomedicine language are applied throughout.

        Why this concept is not a clone of the others:
        It has its own folder, flat HTML pages, `css/style.css`, `js/main.js`, partials, copied assets, design notes, header marker, footer marker, mobile menu marker, hero structure, section order and interaction mode. It does not depend on root `/css`, `/js`, `/partials` or `/assets` at runtime.
        """
    )


def write_partials(concept: Concept, concept_dir: Path) -> None:
    partial_dir = concept_dir / "partials"
    partial_dir.mkdir(parents=True, exist_ok=True)
    (partial_dir / "header.html").write_text(header_markup(concept, "index") + "\n", encoding="utf-8")
    (partial_dir / "footer.html").write_text(footer_markup(concept, "index") + "\n", encoding="utf-8")
    (partial_dir / "mobile-menu.html").write_text(mobile_menu_markup(concept, "index") + "\n", encoding="utf-8")
    (partial_dir / "concept-switcher.html").write_text(concept_switcher_partial(concept) + "\n", encoding="utf-8")


def write_concept(concept: Concept) -> None:
    concept_dir = CONCEPTS_DIR / concept.folder
    concept_dir.mkdir(parents=True, exist_ok=True)
    copy_assets(concept_dir)
    (concept_dir / "css").mkdir(exist_ok=True)
    (concept_dir / "js").mkdir(exist_ok=True)
    (concept_dir / "css" / "style.css").write_text(css_for(concept), encoding="utf-8")
    (concept_dir / "js" / "main.js").write_text(js_for(concept), encoding="utf-8")
    write_partials(concept, concept_dir)
    (concept_dir / "design-notes.md").write_text(design_notes(concept), encoding="utf-8")
    for page in PAGE_SPECS:
        (concept_dir / page[2]).write_text(html_page(concept, page), encoding="utf-8")


def selector_card(concept: Concept) -> str:
    return dedent(
        f"""
        <a class="selector-card" href="concepts/{concept.folder}/index.html">
          <span>{concept.number}</span>
          <strong>{esc(concept.name)}</strong>
          <small>{esc(concept.archetype)}</small>
        </a>
        """
    ).strip()


def write_root_selector(concepts: list[Concept]) -> None:
    cards = "\n".join(selector_card(concept) for concept in concepts)
    html = dedent(
        f"""\
        <!doctype html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <meta name="viewport" content="width=device-width, initial-scale=1">
          <title>Sofiati Standalone Website Concepts</title>
          <meta name="description" content="50 standalone premium website directions for Franciele Sofiati.">
          <link rel="icon" href="assets/brand/sofiati-favicon.svg" type="image/svg+xml">
          <style>
            :root{{--sage:#A2AE9F;--ivory:#F3EFE5;--ink:#252321;--line:rgba(37,35,33,.14)}}*{{box-sizing:border-box}}body{{margin:0;background:var(--ivory);color:var(--ink);font-family:Inter,system-ui,sans-serif}}main{{width:min(1240px,calc(100% - 32px));margin:auto;padding:clamp(32px,7vw,90px) 0}}h1{{font-family:Georgia,serif;font-size:clamp(3rem,8vw,7rem);font-weight:400;line-height:.95;max-width:980px}}.selector-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}}.selector-card{{min-height:170px;display:grid;align-content:space-between;border:1px solid var(--line);background:#F8F7F2;border-radius:8px;padding:16px;text-decoration:none;color:inherit}}.selector-card span{{font-family:Georgia,serif;font-size:2.4rem;color:#798A80}}.selector-card strong{{font-size:1.25rem}}.selector-card small{{color:#706B63;line-height:1.35}}
          </style>
        </head>
        <body>
          <main>
            <p>Franciele Sofiati · Advanced Aesthetic Biomedicine · Londrina, PR</p>
            <h1>50 standalone Sofiati website builds.</h1>
            <div class="selector-grid">{cards}</div>
          </main>
        </body>
        </html>
        """
    )
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    (ROOT / "select.html").write_text(html, encoding="utf-8")


def write_sitemap(concepts: list[Concept]) -> None:
    urls = ["https://www.sofiati.com/"]
    for concept in concepts:
        for _, _, filename, *_ in PAGE_SPECS:
            urls.append(f"https://www.sofiati.com/concepts/{concept.folder}/{filename}")
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    xml.extend(f"  <url><loc>{url}</loc></url>" for url in urls)
    xml.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(xml) + "\n", encoding="utf-8")


def main() -> None:
    concepts = [Concept(*item) for item in CONCEPTS]
    if CONCEPTS_DIR.exists():
        shutil.rmtree(CONCEPTS_DIR)
    CONCEPTS_DIR.mkdir()
    for concept in concepts:
        write_concept(concept)
    write_root_selector(concepts)
    write_sitemap(concepts)
    print(f"Generated {len(concepts)} standalone concepts")
    print(f"Generated {len(concepts) * len(PAGE_SPECS)} flat HTML pages")


if __name__ == "__main__":
    main()
