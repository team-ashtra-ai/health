#!/usr/bin/env python3
"""Render the 21 English pages from ``data/content-master.json``.

The renderer is deliberately conservative.  It replaces only the contents of
each existing ``<main>`` element, so every page keeps its current document
head, body attributes, shared-partial mounts, and script includes.  The
default mode is a dry run: all input and generated HTML is validated in memory
and no page is changed.  Writing requires the explicit ``--write`` flag.

Examples (do not write):

    python3 scripts/render-english-site.py
    python3 scripts/render-english-site.py --dry-run --page about.html
    python3 scripts/render-english-site.py --validate-only

Explicit generation, when the content master has been reviewed:

    python3 scripts/render-english-site.py --write
    python3 scripts/render-english-site.py --write --output-dir /tmp/sofiati-preview

Only Python's standard library is used so the generated site remains a
handwritten, editable static project with no build-system dependency.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
from dataclasses import dataclass
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Iterator, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONTENT = ROOT / "data" / "content-master.json"
SITE_ORIGIN = "https://www.francielesofiati.com"
SITE_NAME = "Franciele Sofiati Biomédica"
SITE_EMAIL = "suportesofiati@gmail.com"
SITE_TELEPHONE = "+5543991043536"
SITE_LOCATION = "Londrina, Paraná, Brazil"
SITE_INSTAGRAM = "https://www.instagram.com/sofiati_biomedica/"
FORM_ENDPOINT = "https://formspree.io/f/xzdldkjy"
OG_IMAGE = f"{SITE_ORIGIN}/assets/social/sofiati-og-image.png"
LOGO_IMAGE = f"{SITE_ORIGIN}/assets/brand/sofiati-logo-primary.png"

HERO_IMAGES: dict[str, tuple[str, str, int, int]] = {
    "404.html": ("assets/hero/hero12.webp", "Franciele Sofiati on the page-not-found guide", 1374, 1900),
    "about.html": ("assets/hero/hero2.webp", "Franciele Sofiati in a professional clinic portrait", 1267, 1900),
    "accessibility.html": ("assets/portraits/portrait4.webp", "Franciele Sofiati introducing website accessibility support", 1507, 1900),
    "blog.html": ("assets/hero/hero10.webp", "Franciele Sofiati introducing educational articles", 1507, 1900),
    "care.html": ("assets/hero/hero3.webp", "Franciele Sofiati in a calm clinic portrait", 1267, 1900),
    "consultation.html": ("assets/hero/hero4.webp", "Franciele Sofiati introducing the consultation process", 1267, 1900),
    "contact.html": ("assets/hero/hero5.webp", "Franciele Sofiati welcoming contact with the clinic", 1267, 1900),
    "cookies.html": ("assets/hero/hero14.webp", "Franciele Sofiati introducing clear cookie choices", 1516, 1900),
    "faq.html": ("assets/portraits/portrait5.webp", "Franciele Sofiati introducing frequently asked questions", 1513, 1900),
    "index.html": ("assets/hero/hero1.webp", "Franciele Sofiati in a luminous clinic portrait", 1267, 1900),
    "journal.html": ("assets/hero/hero15.png", "Franciele Sofiati introducing the journal", 1267, 1900),
    "laser.html": ("assets/portraits/portrait1.webp", "Franciele Sofiati introducing responsible laser guidance", 1433, 1900),
    "legal.html": ("assets/portraits/portrait3.webp", "Franciele Sofiati introducing website legal information", 1374, 1900),
    "mission.html": ("assets/hero/hero7.webp", "Franciele Sofiati in a professional clinic portrait", 1267, 1900),
    "privacy.html": ("assets/hero/hero13.webp", "Franciele Sofiati introducing the privacy notice", 1433, 1900),
    "results.html": ("assets/hero/hero8.webp", "Franciele Sofiati introducing responsible results context", 1400, 1900),
    "skin.html": ("assets/hero/hero9.png", "Franciele Sofiati introducing skin guidance", 1267, 1900),
    "testimonials.html": ("assets/hero/hero11.webp", "Franciele Sofiati introducing patient experiences", 1267, 1900),
    "thank-you.html": ("assets/portraits/portrait6.webp", "Franciele Sofiati thanking the visitor for making contact", 1516, 1900),
    "treatments.html": ("assets/hero/hero6.webp", "Franciele Sofiati introducing the treatment directory", 1267, 1900),
    "values.html": ("assets/portraits/portrait2.webp", "Franciele Sofiati introducing her professional values", 1374, 1900),
}

# Supporting photography is intentionally added by the renderer rather than
# encoded as decorative CSS. This keeps it meaningful to assistive technology
# and gives long pages a human, editorial rhythm without changing page copy.
EDITORIAL_ENVIRONMENTS: tuple[tuple[str, str, int, int], ...] = (
    ("assets/hero/clinic/hero 14.png", "The warm, softly lit Franciele Sofiati clinic interior", 1672, 941),
    ("assets/hero/clinic/hero 12.png", "A calm treatment room inside the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 13.png", "The welcoming reception environment at the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 15.png", "A quiet, carefully prepared clinic treatment space", 1672, 941),
    ("assets/hero/clinic/hero 16.png", "The warm, softly lit Franciele Sofiati clinic interior", 1672, 941),
    ("assets/hero/clinic/hero 18.png", "A calm treatment room inside the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 19.png", "The welcoming reception environment at the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 1 10.png", "A quiet, carefully prepared clinic treatment space", 1672, 941),
    ("assets/hero/clinic/hero 5.png", "The warm, softly lit Franciele Sofiati clinic interior", 1672, 941),
    ("assets/hero/clinic/hero 11.png", "A calm treatment room inside the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 17.png", "The welcoming reception environment at the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 6.png", "A quiet, carefully prepared clinic treatment space", 1672, 941),
    ("assets/hero/clinic/hero 7.png", "The warm, softly lit Franciele Sofiati clinic interior", 1672, 941),
    ("assets/hero/clinic/hero 8.png", "A calm treatment room inside the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 9.png", "The welcoming reception environment at the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 10.png", "A quiet, carefully prepared clinic treatment space", 1672, 941),
    ("assets/hero/clinic/hero 2.png", "The warm, softly lit Franciele Sofiati clinic interior", 1672, 941),
    ("assets/hero/clinic/hero 3.png", "A calm treatment room inside the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 4.png", "The welcoming reception environment at the Franciele Sofiati clinic", 1672, 941),
    ("assets/hero/clinic/hero 20.png", "A quiet, carefully prepared clinic treatment space", 1672, 941),
    ("assets/hero/clinic/hero 1 9.png", "The warm, softly lit Franciele Sofiati clinic interior", 1672, 941),
)

EDITORIAL_TREATMENTS: tuple[tuple[str, str, int, int], ...] = (
    ("assets/treatments/Treatments21.png", "Franciele Sofiati explaining a treatment during an appointment", 1672, 941),
    ("assets/treatments/Treatments22.png", "A considered skin treatment in the clinic environment", 1672, 941),
    ("assets/treatments/Treatments23.png", "Franciele Sofiati carrying out a precise aesthetic treatment", 1672, 941),
    ("assets/treatments/Treatments24.png", "A calm one-to-one treatment moment with Franciele Sofiati", 1672, 941),
    ("assets/treatments/Treatments25.png", "Treatment details prepared with care in the clinic", 1672, 941),
    ("assets/treatments/Treatments27.png", "Franciele Sofiati explaining a treatment during an appointment", 1672, 941),
    ("assets/treatments/Treatments28.png", "A considered skin treatment in the clinic environment", 1672, 941),
    ("assets/treatments/Treatments29.png", "Franciele Sofiati carrying out a precise aesthetic treatment", 1672, 941),
    ("assets/treatments/Treatments30.png", "A calm one-to-one treatment moment with Franciele Sofiati", 1672, 941),
    ("assets/treatments/Treatments20.png", "Treatment details prepared with care in the clinic", 1672, 941),
    ("assets/treatments/Treatments26.png", "Franciele Sofiati explaining a treatment during an appointment", 1672, 941),
    ("assets/treatments/Treatments19.png", "A considered skin treatment in the clinic environment", 1672, 941),
    ("assets/treatments/Treatments18.png", "Franciele Sofiati carrying out a precise aesthetic treatment", 1672, 941),
    ("assets/treatments/Treatments17.png", "A calm one-to-one treatment moment with Franciele Sofiati", 1672, 941),
    ("assets/treatments/Treatments16.png", "Treatment details prepared with care in the clinic", 1672, 941),
    ("assets/treatments/Treatments15.png", "Franciele Sofiati explaining a treatment during an appointment", 1672, 941),
    ("assets/treatments/Treatments14.png", "A considered skin treatment in the clinic environment", 1672, 941),
    ("assets/treatments/Treatments13.png", "Franciele Sofiati carrying out a precise aesthetic treatment", 1672, 941),
    ("assets/treatments/Treatments12.png", "A calm one-to-one treatment moment with Franciele Sofiati", 1672, 941),
    ("assets/treatments/Treatments31.png", "Treatment details prepared with care in the clinic", 1672, 941),
    ("assets/treatments/Treatments11.png", "Franciele Sofiati explaining a treatment during an appointment", 1672, 941),
)

# Supporting photography is selected for the subject of a specific chapter.
# This replaces the former page-index modulo selection, which could put a
# technically valid but narratively arbitrary crop beside the copy.
EDITORIAL_MEDIA_MAP: dict[tuple[str, int], tuple[str, str, int, int]] = {
    ("404.html", 2): ("assets/hero/clinic/hero 13.png", "The welcoming reception at the Franciele Sofiati clinic", 1672, 941),
    ("about.html", 2): ("assets/hero/clinic/hero 12.png", "A calm treatment room inside the Franciele Sofiati clinic", 1672, 941),
    ("about.html", 6): ("assets/treatments/Treatments22.png", "Franciele Sofiati bringing precision and warmth to patient care", 1672, 941),
    ("accessibility.html", 2): ("assets/hero/clinic/hero 13.png", "A clear and welcoming route into the clinic", 1672, 941),
    ("accessibility.html", 6): ("assets/treatments/Treatments23.png", "Franciele Sofiati explaining professional information clearly", 1672, 941),
    ("blog.html", 2): ("assets/treatments/Treatments21.png", "Franciele Sofiati discussing a skin concern before treatment", 1672, 941),
    ("blog.html", 6): ("assets/treatments/Treatments24.png", "Treatment preparation considered before a procedure", 1672, 941),
    ("care.html", 2): ("assets/treatments/Treatments21.png", "A one-to-one conversation used to plan treatment in context", 1672, 941),
    ("care.html", 6): ("assets/treatments/Treatments25.png", "A treatment detail prepared with aftercare in mind", 1672, 941),
    ("consultation.html", 2): ("assets/treatments/Treatments21.png", "Franciele Sofiati listening during a focused consultation", 1672, 941),
    ("contact.html", 6): ("assets/treatments/Treatments27.png", "Franciele Sofiati available for appropriate aftercare questions", 1672, 941),
    ("faq.html", 2): ("assets/hero/clinic/hero 14.png", "A calm clinic setting for clear questions and answers", 1672, 941),
    ("faq.html", 6): ("assets/treatments/Treatments29.png", "A technology-led treatment discussed in clinical context", 1672, 941),
    ("index.html", 2): ("assets/hero/clinic/hero 11.png", "The Franciele Sofiati clinic environment", 1672, 941),
    ("index.html", 6): ("assets/treatments/Treatments21.png", "Franciele Sofiati combining technical precision with personal care", 1672, 941),
    ("journal.html", 2): ("assets/treatments/Treatments21.png", "A thoughtful clinical conversation behind the featured essay", 1672, 941),
    ("journal.html", 6): ("assets/treatments/Treatments26.png", "A close treatment detail supporting an educational article", 1672, 941),
    ("laser.html", 2): ("assets/treatments/Treatments9.png", "A laser platform selected for a specific clinical target", 1672, 941),
    ("laser.html", 6): ("assets/treatments/Treatments10.png", "Laser hair reduction treatment in progress", 1672, 941),
    ("legal.html", 2): ("assets/hero/clinic/hero 14.png", "The professional clinic environment described by the legal information", 1672, 941),
    ("legal.html", 6): ("assets/treatments/Treatments23.png", "Original professional content demonstrated in clinical practice", 1672, 941),
    ("mission.html", 2): ("assets/hero/clinic/hero 3.png", "The welcoming clinic environment behind Franciele Sofiati's mission", 1672, 941),
    ("mission.html", 6): ("assets/treatments/Treatments24.png", "Individual care that preserves the person receiving it", 1672, 941),
    ("privacy.html", 2): ("assets/hero/clinic/hero 13.png", "The clinic contact point for privacy questions", 1672, 941),
    ("results.html", 2): ("assets/treatments/Treatments28.png", "A clinical result considered within the full treatment context", 1672, 941),
    ("results.html", 6): ("assets/treatments/Treatments30.png", "Franciele Sofiati preserving individuality during treatment planning", 1672, 941),
    ("skin.html", 2): ("assets/treatments/Treatments2.png", "A close skin assessment before selecting treatment", 1672, 941),
    ("skin.html", 6): ("assets/treatments/Treatments8.png", "Professional skin planning with protection and continuity", 1672, 941),
    ("testimonials.html", 2): ("assets/hero/clinic/hero 3.png", "A calm treatment room inside the Franciele Sofiati clinic", 1672, 941),
    ("testimonials.html", 6): ("assets/treatments/Treatments13.png", "Franciele Sofiati carrying out a precise aesthetic treatment", 1672, 941),
    ("thank-you.html", 2): ("assets/hero/clinic/hero 13.png", "The clinic reception where an enquiry is received", 1672, 941),
    ("values.html", 2): ("assets/hero/clinic/hero 11.png", "A personal consultation shaped by professional values", 1672, 941),
    ("values.html", 6): ("assets/treatments/Treatments21.png", "Care balancing advanced tools with careful judgment", 1672, 941),
}

TREATMENT_MENU_IMAGES: dict[str, tuple[str, str]] = {
    "Deep Skin Cleansing": ("assets/treatments/Treatments1.png", "Franciele Sofiati preparing a facial cleansing treatment"),
    "Ultrasonic Peel": ("assets/treatments/Treatments2.png", "Gentle facial cleansing technology in use"),
    "Diamond Peel": ("assets/treatments/Treatments3.png", "Franciele Sofiati performing a surface refinement treatment"),
    "Crystal Peel — Microdermabrasion": ("assets/treatments/Treatments4.png", "Microdermabrasion treatment detail in the clinic"),
    "Retinoic Peel": ("assets/treatments/Treatments5.png", "Professional peel planning during skin care"),
    "Jessner Peel": ("assets/treatments/Treatments6.png", "Chemical renewal treatment preparation"),
    "TCA Peel": ("assets/treatments/Treatments7.png", "Targeted chemical peel planning"),
    "Professional Depigmentation Protocol": ("assets/treatments/Treatments8.png", "Pigmentation treatment planning in the clinic"),
    "Harmony Laser Platform": ("assets/treatments/Treatments9.png", "Laser platform treatment in a clinical setting"),
    "LightSheer Duet Laser Hair Reduction": ("assets/treatments/Treatments10.png", "Laser hair reduction treatment in progress"),
    "AcuPulse CO₂ Laser": ("assets/treatments/Treatments11.png", "CO2 laser resurfacing equipment detail"),
    "Ultraformer MPT": ("assets/treatments/Treatments12.png", "Ultrasound firmness treatment in the clinic"),
    "Radiofrequency": ("assets/treatments/Treatments13.png", "Radiofrequency treatment being prepared"),
    "Plasma Technology": ("assets/treatments/Treatments14.png", "Plasma technology treatment detail"),
    "Botulinum Toxin — Upper Face": ("assets/treatments/Treatments15.png", "Facial injectable planning with Franciele Sofiati"),
    "Botulinum Toxin — Platysma and Lower Face": ("assets/treatments/Treatments16.png", "Lower face aesthetic planning in consultation"),
    "MMP — Microinfusion of Medication into the Skin": ("assets/treatments/Treatments17.png", "Microinfusion treatment detail"),
    "Hair Mesotherapy": ("assets/treatments/Treatments18.png", "Scalp care planning in the clinic"),
    "PEIM — Aesthetic Injectable Treatment for Microvessels": ("assets/treatments/Treatments19.png", "Microvessel treatment planning"),
}

ENGLISH_PAGES: tuple[str, ...] = (
    "404.html",
    "about.html",
    "accessibility.html",
    "blog.html",
    "care.html",
    "consultation.html",
    "contact.html",
    "cookies.html",
    "faq.html",
    "index.html",
    "journal.html",
    "laser.html",
    "legal.html",
    "mission.html",
    "privacy.html",
    "results.html",
    "skin.html",
    "testimonials.html",
    "thank-you.html",
    "treatments.html",
    "values.html",
)

# These pages have independent, hand-authored layouts. The general renderer
# must not replace their current structures with the older content-master
# versions. Their visible copy is maintained in the page files and translated
# from the rendered English source.
EXTERNAL_RENDERED_PAGES = frozenset(
    {
        "404.html",
        "about.html",
        "consultation.html",
        "contact.html",
        "cookies.html",
        "index.html",
        "journal.html",
        "legal.html",
    }
)

# One individual art-directed final CTA per public English page.  The number is
# a stable hand-off key between the content renderer and the component CSS.
FINAL_CTA_CONCEPTS: dict[str, str] = {
    filename: f"{index:02d}"
    for index, filename in enumerate(ENGLISH_PAGES, start=1)
}

FINAL_CTA_COPY: dict[str, tuple[str, str, str, str]] = {
    "404.html": ("A useful next step", "Tell me what you need, and I’ll help you find the right route.", "Consult", "Treatments"),
    "about.html": ("Let’s talk about you", "Bring the concern, the questions and the result you hope will feel natural.", "Consult", "Treatments"),
    "accessibility.html": ("Need another format?", "Tell me what is making access difficult and I will try to help.", "Contact", "Treatments"),
    "blog.html": ("Put advice in context", "A consultation can relate general guidance to your skin, history and priorities.", "Consult", "Treatments"),
    "care.html": ("Prepare with confidence", "Your instructions will reflect the procedure, your skin and your planned recovery.", "Consult", "Treatments"),
    "consultation.html": ("Bring your questions", "You do not need to choose a treatment before we speak.", "Consult", "Treatments"),
    "contact.html": ("Ask Franciele", "A short message is enough to begin a helpful conversation.", "Consult", "Treatments"),
    "cookies.html": ("Questions about privacy?", "You can ask how website information and cookie choices are handled.", "Contact", "Treatments"),
    "faq.html": ("Still wondering?", "Franciele can discuss what the general answers mean for your concern.", "Consult", "Treatments"),
    "index.html": ("Ready when you are", "Begin with what you would like to understand, not a treatment name.", "Consult", "Treatments"),
    "journal.html": ("Read, then ask", "Professional guidance can help place general information in your own context.", "Consult", "Treatments"),
    "laser.html": ("Is laser appropriate?", "Assessment helps match the technology, settings and recovery to the individual.", "Consult", "Treatments"),
    "legal.html": ("Questions about terms?", "Ask for clarification before accepting a booking or service agreement.", "Contact", "Treatments"),
    "mission.html": ("Care you understand", "Feel heard, know your options and choose what feels right for you.", "Consult", "Treatments"),
    "privacy.html": ("A privacy question?", "Contact Franciele if you want to understand how your information is used.", "Contact", "Treatments"),
    "results.html": ("Discuss your priorities", "Your starting point and response matter more than another person’s photograph.", "Consult", "Treatments"),
    "skin.html": ("Understand your skin", "Franciele can help you simplify the concern and plan a sensible next step.", "Consult", "Treatments"),
    "testimonials.html": ("Your experience matters", "Meet Franciele, ask questions and decide how the care feels to you.", "Consult", "Treatments"),
    "thank-you.html": ("While you wait", "Keep any useful dates or questions ready for Franciele’s reply.", "Consult", "Treatments"),
    "treatments.html": ("Choose with clarity", "Franciele will explain which options may fit and which ones may not.", "Consult", "Treatments"),
    "values.html": ("See values in practice", "A consultation shows how listening, judgment and restraint shape each recommendation.", "Consult", "Treatments"),
}

PAGE_LABELS: dict[str, str] = {
    "404.html": "Page Not Found",
    "about.html": "About Franciele",
    "accessibility.html": "Accessibility",
    "blog.html": "Blog",
    "care.html": "Care & Aftercare",
    "consultation.html": "Consultation",
    "contact.html": "Contact",
    "cookies.html": "Cookie Notice",
    "faq.html": "Frequently Asked Questions",
    "index.html": "Home",
    "journal.html": "Journal",
    "laser.html": "Laser",
    "legal.html": "Website Terms and Legal Information",
    "mission.html": "Mission",
    "privacy.html": "Privacy Notice",
    "results.html": "Results",
    "skin.html": "Skin",
    "testimonials.html": "Patient Experiences",
    "thank-you.html": "Thank You",
    "treatments.html": "Treatments",
    "values.html": "Values",
}

HERO_EYEBROWS: dict[str, str] = {
    "404.html": "404",
    "about.html": "About",
    "accessibility.html": "Accessibility",
    "blog.html": "Blog",
    "care.html": "Care",
    "consultation.html": "Consultation",
    "contact.html": "Contact",
    "cookies.html": "Cookies",
    "faq.html": "FAQ",
    "index.html": "Home",
    "journal.html": "Journal",
    "laser.html": "Laser",
    "legal.html": "Legal",
    "mission.html": "Mission",
    "privacy.html": "Privacy",
    "results.html": "Results",
    "skin.html": "Skin",
    "testimonials.html": "Testimonials",
    "thank-you.html": "Thanks",
    "treatments.html": "Treatments",
    "values.html": "Values",
}

PAGE_FAMILIES: dict[str, str] = {
    "404.html": "utility",
    "thank-you.html": "utility",
    "about.html": "editorial",
    "mission.html": "editorial",
    "values.html": "editorial",
    "accessibility.html": "policy",
    "cookies.html": "policy",
    "legal.html": "policy",
    "privacy.html": "policy",
    "blog.html": "content",
    "faq.html": "content",
    "journal.html": "content",
    "testimonials.html": "content",
    "consultation.html": "conversion",
    "contact.html": "conversion",
    "care.html": "service",
    "laser.html": "service",
    "results.html": "service",
    "skin.html": "service",
    "treatments.html": "service",
    "index.html": "home",
}

# Every English page has an explicit tonal journey. These hooks are deliberately
# kept in the renderer instead of being inferred with ``:nth-child`` selectors:
# a section can move without silently changing its visual role, and a future
# editor can understand the intended page rhythm from one central map.
PAGE_TONE_JOURNEYS: dict[str, tuple[str, ...]] = {
    "404.html": ("paper", "mist", "paper", "sage", "blush", "paper", "blush", "mist", "sage", "forest"),
    "about.html": ("paper", "mist", "paper", "blush", "mist", "paper", "sage", "mist", "paper", "forest"),
    "accessibility.html": ("paper", "mist", "sage", "paper", "blush", "mist", "paper", "mist", "sage", "forest"),
    "blog.html": ("paper", "mist", "paper", "sage", "sage", "paper", "blush", "mist", "sage", "forest"),
    "care.html": ("paper", "mist", "sage", "mist", "paper", "blush", "paper", "sage", "mist", "forest"),
    "consultation.html": ("paper", "mist", "blush", "paper", "sage", "blush", "paper", "mist", "sage", "forest"),
    "contact.html": ("blush",),
    "cookies.html": ("paper", "blush", "paper", "mist", "sage", "sage", "paper", "mist", "blush", "forest"),
    "faq.html": ("paper", "mist", "paper", "sage", "blush", "paper", "mist", "sage", "paper", "forest"),
    "index.html": ("paper", "mist", "sage", "paper", "blush", "paper", "forest", "sage", "forest"),
    "journal.html": ("paper", "mist", "sage", "paper", "sage", "blush", "paper", "mist", "sage", "forest"),
    "laser.html": ("paper", "mist", "sage", "paper", "sage", "blush", "mist", "paper", "mist", "forest"),
    "legal.html": ("paper", "blush", "sage", "paper", "mist", "sage", "paper", "blush", "mist", "sage"),
    "mission.html": ("paper", "mist", "sage", "paper", "sage", "blush", "paper", "sage", "mist", "forest"),
    "privacy.html": ("paper", "mist", "sage", "paper", "blush", "sage", "paper", "mist", "sage", "forest"),
    "results.html": ("paper", "mist", "sage", "paper", "paper", "blush", "mist", "paper", "mist", "forest"),
    "skin.html": ("paper", "mist", "sage", "paper", "sage", "blush", "paper", "mist", "sage", "forest"),
    "testimonials.html": ("paper", "mist", "forest", "blush", "paper", "sage", "paper", "mist", "blush", "forest"),
    "thank-you.html": ("paper", "mist", "sage", "paper", "sage", "blush", "paper", "mist", "sage", "forest"),
    "treatments.html": ("paper", "paper", "blush", "paper", "sage", "blush", "forest", "paper", "sage", "mist", "forest"),
    "values.html": ("paper", "mist", "blush", "paper", "blush", "sage", "paper", "blush", "mist", "forest"),
}

ON_THIS_PAGE_PAGES = frozenset(
    {
        "accessibility.html",
        "cookies.html",
        "faq.html",
        "laser.html",
        "legal.html",
        "privacy.html",
        "results.html",
        "skin.html",
        "treatments.html",
    }
)

# Existing routes use an explicit page-level composition map. New or rebuilt
# sections should normally declare ``pattern`` in the content master, as the
# Treatments art map does. There is deliberately no modulo/cycling fallback:
# a page's narrative cannot be designed by section position alone.
PAGE_PATTERN_JOURNEYS: dict[str, tuple[str, ...]] = {
    "404.html": ("hero", "evidence_panel", "staggered_cards", "staggered_cards", "quote_panel", "definition_blocks", "quote_panel", "reading_column", "route_map", "final_cta"),
    "about.html": ("hero", "horizontal_bands", "definition_blocks", "route_map", "quote_panel", "page_directory", "staggered_cards", "horizontal_bands", "definition_blocks", "final_cta"),
    "accessibility.html": ("hero", "staggered_cards", "horizontal_bands", "numbered_sequence", "comparison", "evidence_panel", "quote_panel", "form", "horizontal_bands", "final_cta"),
    "blog.html": ("hero", "editorial_split", "route_map", "evidence_panel", "page_directory", "staggered_cards", "horizontal_bands", "definition_blocks", "route_map", "final_cta"),
    "care.html": ("hero", "editorial_split", "numbered_sequence", "quote_panel", "definition_blocks", "reading_column", "quote_panel", "page_directory", "staggered_cards", "final_cta"),
    "consultation.html": ("hero", "editorial_split", "quote_panel", "numbered_sequence", "staggered_cards", "quote_panel", "form", "timeline", "evidence_panel", "final_cta"),
    "contact.html": ("form",),
    "cookies.html": ("hero", "oversized_statement", "definition_blocks", "editorial_split", "evidence_panel", "timeline", "staggered_cards", "form", "definition_blocks", "final_cta"),
    "faq.html": ("hero", "accordion", "accordion", "accordion", "accordion", "accordion", "accordion", "accordion", "accordion", "final_cta"),
    "index.html": ("hero", "evidence_panel", "numbered_sequence", "quote_panel", "horizontal_bands", "definition_blocks", "quote_panel", "evidence_panel", "final_cta"),
    "journal.html": ("hero", "route_map", "evidence_panel", "page_directory", "staggered_cards", "horizontal_bands", "definition_blocks", "route_map", "evidence_panel", "final_cta"),
    "laser.html": ("hero", "route_map", "evidence_panel", "quote_panel", "staggered_cards", "horizontal_bands", "quote_panel", "quote_panel", "numbered_sequence", "final_cta"),
    "legal.html": ("hero", "oversized_statement", "evidence_panel", "editorial_split", "staggered_cards", "timeline", "staggered_cards", "pull_quote", "question_gateway", "final_cta"),
    "mission.html": ("hero", "evidence_panel", "page_directory", "numbered_sequence", "quote_panel", "quote_panel", "numbered_sequence", "quote_panel", "quote_panel", "final_cta"),
    "privacy.html": ("hero", "staggered_cards", "horizontal_bands", "comparison", "route_map", "editorial_split", "definition_blocks", "staggered_cards", "horizontal_bands", "final_cta"),
    "results.html": ("hero", "definition_blocks", "route_map", "evidence_panel", "page_directory", "staggered_cards", "quote_panel", "staggered_cards", "route_map", "final_cta"),
    "skin.html": ("hero", "horizontal_bands", "definition_blocks", "route_map", "evidence_panel", "timeline", "staggered_cards", "horizontal_bands", "quote_panel", "final_cta"),
    "testimonials.html": ("hero", "definition_blocks", "quote_panel", "quote_panel", "quote_panel", "quote_panel", "quote_panel", "quote_panel", "route_map", "final_cta"),
    "thank-you.html": ("hero", "numbered_sequence", "horizontal_bands", "numbered_sequence", "route_map", "horizontal_bands", "quote_panel", "reading_column", "route_map", "final_cta"),
    "values.html": ("hero", "evidence_panel", "quote_panel", "quote_panel", "horizontal_bands", "numbered_sequence", "route_map", "evidence_panel", "numbered_sequence", "final_cta"),
}

# Section scale and scene are authored page journeys, just like composition and
# tone.  They are not derived from position or alternated by CSS selectors.
# The scale describes cadence; the scene describes the material carrying the
# chapter.  Content still determines the final height.
PAGE_SCALE_JOURNEYS: dict[str, tuple[str, ...]] = {
    "404.html": ("immersive", "compact", "standard", "compact", "compact", "standard", "compact", "compact", "compact", "standard"),
    "about.html": ("immersive", "standard", "compact", "compact", "standard", "compact", "standard", "compact", "compact", "standard"),
    "accessibility.html": ("immersive", "compact", "compact", "standard", "compact", "standard", "compact", "standard", "compact", "standard"),
    "blog.html": ("immersive", "standard", "compact", "standard", "compact", "standard", "compact", "compact", "compact", "standard"),
    "care.html": ("immersive", "standard", "compact", "standard", "compact", "compact", "compact", "compact", "compact", "standard"),
    "consultation.html": ("immersive", "standard", "compact", "standard", "compact", "compact", "standard", "compact", "standard", "standard"),
    "contact.html": ("immersive",),
    "cookies.html": ("immersive", "compact", "compact", "compact", "standard", "compact", "compact", "standard", "compact", "standard"),
    "faq.html": ("immersive", "standard", "compact", "compact", "compact", "compact", "compact", "compact", "compact", "standard"),
    "index.html": ("immersive", "standard", "compact", "standard", "compact", "standard", "compact", "standard", "standard"),
    "journal.html": ("immersive", "standard", "standard", "compact", "standard", "compact", "compact", "compact", "standard", "standard"),
    "laser.html": ("immersive", "compact", "standard", "compact", "standard", "compact", "standard", "compact", "standard", "standard"),
    "legal.html": ("immersive", "compact", "compact", "compact", "compact", "compact", "compact", "compact", "compact", "standard"),
    "mission.html": ("immersive", "standard", "compact", "standard", "standard", "compact", "standard", "compact", "standard", "standard"),
    "privacy.html": ("immersive", "compact", "compact", "compact", "compact", "standard", "compact", "compact", "compact", "standard"),
    "results.html": ("immersive", "standard", "compact", "standard", "compact", "standard", "compact", "compact", "compact", "standard"),
    "skin.html": ("immersive", "standard", "compact", "compact", "standard", "compact", "standard", "compact", "standard", "standard"),
    "testimonials.html": ("immersive", "standard", "standard", "compact", "compact", "standard", "standard", "compact", "compact", "standard"),
    "thank-you.html": ("immersive", "compact", "compact", "compact", "compact", "compact", "compact", "compact", "compact", "standard"),
    "treatments.html": ("immersive", "compact", "immersive", "standard", "standard", "immersive", "immersive", "standard", "standard", "standard", "standard"),
    "values.html": ("immersive", "standard", "compact", "compact", "compact", "compact", "compact", "standard", "compact", "standard"),
}

PAGE_SCENE_JOURNEYS: dict[str, tuple[str, ...]] = {
    "404.html": ("hero", "porcelain", "paper-line", "sage-shadow", "rose-metal", "architectural-light", "blush-silk", "porcelain", "rose-metal", "final"),
    "about.html": ("hero", "architectural-light", "blush-silk", "porcelain", "rose-metal", "clinic-light", "sage-shadow", "paper-line", "rose-metal", "final"),
    "accessibility.html": ("hero", "porcelain", "sage-shadow", "paper-line", "blush-silk", "technical-light", "architectural-light", "clinic-light", "porcelain", "final"),
    "blog.html": ("hero", "clinic-light", "porcelain", "sage-shadow", "paper-line", "rose-metal", "blush-silk", "architectural-light", "porcelain", "final"),
    "care.html": ("hero", "clinic-light", "sage-shadow", "rose-metal", "porcelain", "blush-silk", "paper-line", "architectural-light", "rose-metal", "final"),
    "consultation.html": ("hero", "clinic-light", "blush-silk", "porcelain", "sage-shadow", "blush-silk", "architectural-light", "paper-line", "rose-metal", "final"),
    "contact.html": ("contact-form",),
    "cookies.html": ("hero", "blush-silk", "porcelain", "paper-line", "technical-light", "sage-shadow", "architectural-light", "clinic-light", "rose-metal", "final"),
    "faq.html": ("hero", "porcelain", "paper-line", "sage-shadow", "blush-silk", "architectural-light", "porcelain", "sage-shadow", "rose-metal", "final"),
    "index.html": ("hero", "architectural-light", "sage-shadow", "porcelain", "paper-line", "blush-silk", "olive-garden", "clinic-light", "final"),
    "journal.html": ("hero", "clinic-light", "sage-shadow", "porcelain", "paper-line", "blush-silk", "architectural-light", "rose-metal", "sage-shadow", "final"),
    "laser.html": ("hero", "technical-light", "sage-shadow", "porcelain", "paper-line", "rose-metal", "architectural-light", "clinic-light", "blush-silk", "final"),
    "legal.html": ("hero", "porcelain", "technical-light", "blush-silk", "paper-line", "architectural-light", "sage-shadow", "rose-metal", "porcelain", "final"),
    "mission.html": ("hero", "architectural-light", "sage-shadow", "porcelain", "technical-light", "blush-silk", "paper-line", "clinic-light", "rose-metal", "final"),
    "privacy.html": ("hero", "porcelain", "sage-shadow", "paper-line", "blush-silk", "technical-light", "architectural-light", "rose-metal", "porcelain", "final"),
    "results.html": ("hero", "architectural-light", "sage-shadow", "porcelain", "paper-line", "blush-silk", "rose-metal", "clinic-light", "rose-metal", "final"),
    "skin.html": ("hero", "clinic-light", "sage-shadow", "porcelain", "paper-line", "blush-silk", "architectural-light", "rose-metal", "technical-light", "final"),
    "testimonials.html": ("hero", "architectural-light", "olive-garden", "blush-silk", "porcelain", "clinic-light", "sage-shadow", "paper-line", "rose-metal", "final"),
    "thank-you.html": ("hero", "porcelain", "sage-shadow", "paper-line", "technical-light", "blush-silk", "architectural-light", "rose-metal", "porcelain", "final"),
    "treatments.html": ("hero", "porcelain", "blush-silk", "porcelain", "sage-shadow", "rose-metal", "olive-garden", "clinic-light", "sage-shadow", "paper-line", "final"),
    "values.html": ("hero", "architectural-light", "blush-silk", "porcelain", "blush-silk", "sage-shadow", "paper-line", "rose-metal", "porcelain", "final"),
}

# Full-bleed colour is a deliberately sparse page-level rhythm. Each normal
# content route receives two evenly spaced olive interruptions plus its final
# CTA. Contact remains the previously approved single-form composition, so it
# cannot acquire three additional sections without changing that content
# contract.
FULL_BLEED_BANDS_PER_PAGE = 3
FULL_BLEED_EXEMPT_PAGES = frozenset({"contact.html"})


def full_bleed_section_orders(filename: str, total_sections: int) -> frozenset[int]:
    """Return the three stable full-bleed section positions for one page."""

    if filename in FULL_BLEED_EXEMPT_PAGES or total_sections < FULL_BLEED_BANDS_PER_PAGE:
        return frozenset()
    first = max(2, round(total_sections / 3))
    second = max(first + 1, round(total_sections * 2 / 3))
    return frozenset((first, second, total_sections))

PATTERN_CLASSES: dict[str, tuple[str, ...]] = {
    name: (f"sf-composition-{name.replace('_', '-')}",)
    for name in (
        "hero", "editorial_split", "oversized_statement", "numbered_sequence",
        "horizontal_bands", "quote_panel", "comparison", "staggered_cards",
        "definition_blocks", "timeline", "accordion", "question_gateway",
        "route_map", "testimonial_mosaic", "icon_list", "reading_column",
        "educational", "pull_quote", "evidence_panel", "form",
        "page_directory", "final_cta", "table", "treatment_finder",
        "treatment_feature", "treatment_image_story", "treatment_comparison",
        "treatment_intensity", "treatment_technical", "treatment_clinical",
        "treatment_process", "treatment_plate",
    )
}

PATTERN_ALIASES: dict[str, str] = {
    "split": "editorial_split",
    "editorial": "editorial_split",
    "editorial-split": "editorial_split",
    "statement": "oversized_statement",
    "oversized-statement": "oversized_statement",
    "sequence": "numbered_sequence",
    "steps": "numbered_sequence",
    "numbered-sequence": "numbered_sequence",
    "bands": "horizontal_bands",
    "horizontal-bands": "horizontal_bands",
    "quote": "quote_panel",
    "quote-panel": "quote_panel",
    "compare": "comparison",
    "cards": "staggered_cards",
    "staggered-cards": "staggered_cards",
    "definitions": "definition_blocks",
    "definition-blocks": "definition_blocks",
    "faq": "accordion",
    "accordions": "accordion",
    "gateway": "question_gateway",
    "question-led-gateway": "question_gateway",
    "routes": "route_map",
    "route-map": "route_map",
    "testimonials": "testimonial_mosaic",
    "mosaic": "testimonial_mosaic",
    "icons": "icon_list",
    "narrow-reading": "reading_column",
    "reading": "reading_column",
    "education": "educational",
    "caution": "evidence_panel",
    "callout": "evidence_panel",
    "directory": "page_directory",
    "cta": "final_cta",
    "final-cta": "final_cta",
}

BLOCK_ALIASES: dict[str, str] = {
    "text": "paragraph",
    "copy": "paragraph",
    "body": "paragraph",
    "paragraphs": "paragraph",
    "lede": "lead",
    "intro": "lead",
    "bullet_list": "list",
    "bullets": "list",
    "unordered_list": "list",
    "ordered_list": "steps",
    "numbered_list": "steps",
    "sequence": "steps",
    "process": "steps",
    "timeline": "steps",
    "card_grid": "cards",
    "feature_grid": "cards",
    "features": "cards",
    "tiles": "cards",
    "routes": "cards",
    "route_cards": "cards",
    "testimonials": "cards",
    "reviews": "cards",
    "pull_quote": "quote",
    "statement": "quote",
    "buttons": "cta",
    "links": "cta",
    "actions": "cta",
    "two_column": "comparison",
    "columns": "comparison",
    "belief_vs_practice": "comparison",
    "comparison_table": "table",
    "faqs": "accordion",
    "questions": "accordion",
    "details": "accordion",
    "definitions": "definition_list",
    "glossary": "definition_list",
    "note": "callout",
    "alert": "callout",
    "caution": "callout",
    "warning": "callout",
    "treatments": "treatment_group",
    "treatment_directory": "treatment_group",
    "contact_details": "contact_list",
    "contacts": "contact_list",
    "search_form": "search",
    "article_search": "search",
    "media": "image",
    "picture": "image",
    "byline": "meta",
    "author": "meta",
    "group": "group",
    "section_group": "group",
}

INTERNAL_LINKS: dict[str, str] = {
    "about franciele": "about.html",
    "book a consultation": "consultation.html",
    "browse all articles": "blog.html#skin",
    "contact me": "contact.html",
    "contact about privacy": "contact.html",
    "contact the clinic": "contact.html",
    "discover my care approach": "care.html",
    "explore laser treatments": "treatments.html#laser-services",
    "explore my approach": "care.html",
    "explore my care approach": "care.html",
    "explore results": "results.html",
    "explore skin treatments": "treatments.html#facial-services",
    "explore the care approach": "care.html",
    "explore the care guide": "care.html",
    "explore the journal": "journal.html",
    "explore treatment pathways": "treatments.html",
    "explore treatments": "treatments.html",
    "go to the homepage": "index.html",
    "leave a google review": "https://share.google/95oyMN4LpnqCR8NWS",
    "meet franciele": "about.html",
    "open cookie settings": "cookies.html#cookie-settings",
    "professional values": "values.html",
    "read google reviews": "https://share.google/95oyMN4LpnqCR8NWS",
    "read my values": "values.html",
    "read patient experiences": "testimonials.html",
    "read the article": "blog.html#featured-article",
    "read the care guide": "care.html",
    "read the essay": "journal.html#featured-essay",
    "read the faq": "faq.html",
    "read the latest articles": "blog.html#featured-article",
    "read the latest entry": "journal.html#featured-essay",
    "read the privacy notice": "privacy.html",
    "reject optional cookies": "cookies.html#cookie-settings",
    "request a consultation": "consultation.html",
    "request a laser consultation": "consultation.html",
    "request a skin consultation": "consultation.html",
    "return to home": "index.html",
    "save my choices": "cookies.html#cookie-settings",
    "search the blog": "blog.html#article-search",
    "send a message": "contact.html",
    "send a privacy request": "contact.html",
    "send a whatsapp message": "https://wa.me/5543991043536",
    "understand laser care": "laser.html",
    "view all laser treatments": "treatments.html#laser-services",
    "view all reviews on google": "https://share.google/95oyMN4LpnqCR8NWS",
    "view all treatments": "treatments.html",
}

CARD_DESTINATIONS: dict[str, str] = {
    "home": "index.html",
    "homepage": "index.html",
    "about": "about.html",
    "about franciele": "about.html",
    "skin": "skin.html",
    "laser": "laser.html",
    "treatments": "treatments.html",
    "full treatment directory": "treatments.html",
    "care": "care.html",
    "care guide": "care.html",
    "results": "results.html",
    "results guide": "results.html",
    "journal": "journal.html",
    "faq": "faq.html",
    "blog": "blog.html",
    "consultation": "consultation.html",
    "contact": "contact.html",
    "values": "values.html",
    "mission": "mission.html",
    "patient experiences": "testimonials.html",
    "testimonials": "testimonials.html",
    "privacy": "privacy.html",
    "cookies": "cookies.html",
    "accessibility": "accessibility.html",
    "legal": "legal.html",
}

SPECIAL_FORM_PAGES = frozenset(
    {"accessibility.html", "consultation.html", "contact.html"}
)

# The renderer does not source copy from these signatures.  They are guardrails
# that stop a malformed content JSON from silently changing the document's
# exact form labels, help, acknowledgements, or status messages.
FORM_SIGNATURES: dict[str, dict[str, Any]] = {
    "accessibility.html": {
        "fields": (
            ("Name", False, ("How should we address you?",)),
            ("Email or WhatsApp", True, ("Where may we reply?",)),
            (
                "Page or feature",
                False,
                ("Which page, form, button or section caused difficulty?",),
            ),
            (
                "Accessibility need or problem",
                True,
                (
                    "Describe what happened and the assistive technology or browser used, when relevant.",
                ),
            ),
            (
                "Preferred reply format",
                False,
                ("Email", "WhatsApp", "Telephone", "No preference"),
            ),
        ),
        "messages": (),
    },
    "consultation.html": {
        "fields": (
            ("Full name", True, ("How should I address you?",)),
            (
                "Email address",
                True,
                ("yourname@email.com", "Used only to respond to your request."),
            ),
            ("Phone or WhatsApp", True, ("Include your area code",)),
            (
                "Preferred contact method",
                False,
                ("WhatsApp", "Email", "Telephone", "No preference"),
            ),
            (
                "Main topic",
                False,
                (
                    "Skin and skincare",
                    "Acne or texture",
                    "Pigmentation or melasma",
                    "Laser hair reduction",
                    "Laser resurfacing",
                    "Botulinum toxin",
                    "Firmness or contour",
                    "Hair or scalp",
                    "Superficial microvessels",
                    "General consultation",
                    "I am not sure",
                ),
            ),
            (
                "Area of concern",
                False,
                ("For example: face, neck, scalp, underarms, legs or another area",),
            ),
            (
                "Previous treatment in this area",
                False,
                ("Yes", "No", "I am not sure"),
            ),
            (
                "Preferred consultation format",
                False,
                (
                    "In person in Londrina",
                    "Initial online conversation when appropriate",
                    "Please guide me",
                ),
            ),
            (
                "What would you like to understand?",
                True,
                (
                    "Describe what you have noticed, how long it has concerned you and any treatment you would like to discuss.",
                    "Please avoid including sensitive information that is not necessary for this first contact.",
                ),
            ),
            (
                "Important dates",
                False,
                ("Share upcoming travel, events or a preferred treatment period",),
            ),
            (
                "Privacy acknowledgement",
                True,
                (
                    "I understand that my information will be used to respond and organise the appropriate next step.",
                ),
            ),
            (
                "Consultation acknowledgement",
                True,
                (
                    "I understand that this form does not diagnose a condition or confirm treatment suitability.",
                ),
            ),
        ),
        "messages": (
            "Message received",
            "Thank you for contacting me. Your request has been received and will be reviewed before a reply is sent through your preferred contact method.",
            "Submission error",
            "Your message could not be sent. Review the required fields and try again, or contact the clinic through WhatsApp or email.",
        ),
    },
    "contact.html": {
        "fields": (
            ("Full name", True, ("How should I address you?",)),
            (
                "Email address",
                True,
                (
                    "yourname@email.com",
                    "We will use this address only to respond to your enquiry.",
                ),
            ),
            ("Phone or WhatsApp", True, ("Include your area code",)),
            (
                "Preferred reply",
                False,
                ("WhatsApp", "Email", "Telephone", "No preference"),
            ),
            (
                "Reason for contact",
                True,
                (
                    "General question",
                    "Consultation request",
                    "Treatment information",
                    "New appointment",
                    "Existing appointment",
                    "Rescheduling or cancellation",
                    "Existing patient support",
                    "Aftercare question",
                    "Accessibility support",
                    "Other",
                ),
            ),
            (
                "Main topic",
                False,
                (
                    "Skin and skincare",
                    "Acne or congestion",
                    "Pigmentation or melasma",
                    "Laser hair reduction",
                    "Laser resurfacing",
                    "Facial treatment or peel",
                    "Botulinum toxin",
                    "Firmness or contour",
                    "Hair or scalp",
                    "Superficial microvessels",
                    "I am not sure",
                ),
            ),
            (
                "Area of concern",
                False,
                ("For example: face, neck, scalp, underarms, legs or another area",),
            ),
            (
                "Existing patient",
                False,
                ("Yes", "No", "I have an appointment scheduled"),
            ),
            (
                "Appointment or treatment date",
                False,
                ("DD/MM/YYYY, when applicable",),
            ),
            (
                "Preferred contact period",
                False,
                ("Morning", "Afternoon", "Evening", "Any time"),
            ),
            (
                "Your message",
                True,
                (
                    "Share your question, what you have noticed and any date that may affect treatment or recovery.",
                    "Up to 1,500 characters. Avoid sensitive information that is unnecessary for this first contact.",
                ),
            ),
            (
                "Privacy acknowledgement",
                True,
                (
                    "I understand that my information will be used to respond to this enquiry.",
                ),
            ),
            (
                "Purpose acknowledgement",
                True,
                (
                    "I understand that this form does not provide a diagnosis or emergency care.",
                ),
            ),
        ),
        "messages": (
            "Thank you for contacting me",
            "Your message has been received. It will be reviewed and a reply will be sent through your preferred contact method.",
            "Your message could not be sent",
            "Check the required fields and try again, or contact the clinic directly through WhatsApp or email.",
        ),
    },
}

MAIN_RE = re.compile(
    r"(?P<open><main\b[^>]*>)(?P<body>.*?)(?P<close></main\s*>)",
    flags=re.IGNORECASE | re.DOTALL,
)
HEAD_RE = re.compile(
    r"<head\b[^>]*>.*?</head\s*>",
    flags=re.IGNORECASE | re.DOTALL,
)
PARTIAL_RE = re.compile(
    r"<div\b[^>]*\bdata-(?:sofiati-)?partial=[\"'][^\"']+[\"'][^>]*></div>",
    flags=re.IGNORECASE,
)


class RenderError(RuntimeError):
    """Raised when structured content cannot be rendered safely."""


@dataclass(frozen=True)
class FormDefaults:
    attributes: Mapping[str, str]
    honeypot_name: str | None = None


@dataclass(frozen=True)
class PageSkeleton:
    filename: str
    source: str
    main_open: str
    prefix: str
    suffix: str
    partials: tuple[str, ...]
    form_defaults: FormDefaults | None


@dataclass(frozen=True)
class RenderContext:
    filename: str
    page: Mapping[str, Any]
    site: Mapping[str, Any]
    form_defaults: FormDefaults | None

    @property
    def slug(self) -> str:
        return Path(self.filename).stem


def normalise_space(value: Any) -> str:
    return " ".join(str(value or "").replace("\u00a0", " ").split())


def normalise_label(value: Any) -> str:
    text = normalise_space(value)
    text = re.sub(r"\s*\*\s*$", "", text)
    return text.casefold()


def key_token(value: Any) -> str:
    text = normalise_space(value).casefold().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "_", text).strip("_")


def class_token(value: Any) -> str:
    text = normalise_space(value).casefold()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return text or "item"


def slugify(value: Any) -> str:
    return class_token(value)


def html_text(value: Any) -> str:
    """Escape source copy without silently treating JSON strings as HTML."""

    if value is None:
        return ""
    if isinstance(value, Mapping):
        for key in ("text", "label", "title", "value", "name"):
            if key in value:
                return html_text(value[key])
        raise RenderError(f"Cannot convert mapping to text: keys={sorted(value)}")
    return escape(normalise_space(value), quote=True)


def html_prose(value: Any) -> str:
    """Escape prose while preserving intentional Word line breaks."""

    if value is None:
        return ""
    if isinstance(value, Mapping):
        for key in ("text", "label", "title", "value", "name"):
            if key in value:
                return html_prose(value[key])
        raise RenderError(f"Cannot convert mapping to prose: keys={sorted(value)}")
    lines = [normalise_space(line) for line in str(value).replace("\u00a0", " ").splitlines()]
    return "<br/>".join(escape(line, quote=True) for line in lines if line)


def first_value(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping and mapping[key] not in (None, "", [], {}):
            return mapping[key]
    return None


def listify(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return [value]


def strings_in(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield normalise_space(value)
    elif isinstance(value, Mapping):
        for item in value.values():
            yield from strings_in(item)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for item in value:
            yield from strings_in(item)


def canonical_filename(raw: Any, fallback: Any = None) -> str:
    value = normalise_space(raw or fallback)
    if not value:
        raise RenderError("A page entry has no filename or slug")
    value = value.split("?", 1)[0].split("#", 1)[0]
    value = value.replace("\\", "/").lstrip("./")
    if "/" in value:
        value = value.rsplit("/", 1)[-1]
    aliases = {
        "home": "index",
        "homepage": "index",
        "not-found": "404",
        "not_found": "404",
        "patient-experiences": "testimonials",
        "patient_experiences": "testimonials",
        "thank_you": "thank-you",
    }
    stem = value[:-5] if value.casefold().endswith(".html") else value
    stem = aliases.get(stem.casefold(), stem)
    return f"{stem}.html"


def page_entries(payload: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    raw_pages = payload.get("pages")
    if raw_pages is None:
        raise RenderError("content master must contain a top-level 'pages' collection")

    entries: dict[str, Mapping[str, Any]] = {}
    if isinstance(raw_pages, Mapping):
        iterable: Iterable[tuple[Any, Any]] = raw_pages.items()
    elif isinstance(raw_pages, list):
        iterable = enumerate(raw_pages)
    else:
        raise RenderError("'pages' must be an object or array")

    for key, raw_page in iterable:
        if not isinstance(raw_page, Mapping):
            raise RenderError(f"page {key!r} must be an object")
        filename = canonical_filename(
            first_value(raw_page, "filename", "file", "path", "slug", "id"),
            key,
        )
        if filename in entries:
            raise RenderError(f"duplicate page entry for {filename}")
        entries[filename] = raw_page
    return entries


def site_entry(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in ("site", "shared", "global", "shared_site_copy"):
        value = payload.get(key)
        if isinstance(value, Mapping):
            return value
    return {}


def section_entries(page: Mapping[str, Any], filename: str) -> list[Mapping[str, Any]]:
    raw_sections = first_value(page, "sections", "content_sections")
    if isinstance(raw_sections, Mapping):
        result: list[Mapping[str, Any]] = []
        for key, value in raw_sections.items():
            if not isinstance(value, Mapping):
                raise RenderError(f"{filename}: section {key!r} must be an object")
            if not any(name in value for name in ("order", "number", "index")):
                value = {"order": key, **value}
            result.append(value)
        result.sort(key=lambda item: section_order(item, len(result)))
        return result
    if isinstance(raw_sections, list):
        if not all(isinstance(item, Mapping) for item in raw_sections):
            raise RenderError(f"{filename}: every section must be an object")
        result = list(raw_sections)
        if filename == "contact.html":
            # Contact is intentionally one decisive, form-only composition.
            # The longer source document remains available for future editorial
            # use, but neither a hero nor explanatory chapters belong on the
            # published route.
            form_section = next(
                (
                    item
                    for item in result
                    if key_token(
                        first_value(item, "label", "section_label", "eyebrow")
                    )
                    == "contact_form"
                ),
                None,
            )
            if form_section is None:
                raise RenderError(
                    "contact.html: the CONTACT FORM source section is required"
                )
            return [{**form_section, "number": 1, "order": 1}]
        return result
    raise RenderError(f"{filename}: missing structured 'sections' array")


def section_order(section: Mapping[str, Any], fallback: int) -> int:
    raw = first_value(section, "order", "number", "index", "position")
    if raw is None:
        return fallback
    if isinstance(raw, int):
        return raw
    match = re.search(r"\d+", str(raw))
    if not match:
        raise RenderError(f"invalid section order {raw!r}")
    return int(match.group())


def section_label(section: Mapping[str, Any], order: int) -> str:
    value = first_value(
        section,
        "label",
        "kicker",
        "section_label",
        "name",
        "eyebrow",
    )
    if value is None:
        return f"Section {order:02d}"
    return normalise_space(value)


def section_heading(section: Mapping[str, Any]) -> str:
    value = first_value(section, "heading", "headline", "title", "question")
    if value is None:
        raise RenderError("section is missing a heading/headline/title")
    return normalise_space(value)


def section_blocks(section: Mapping[str, Any]) -> list[Any]:
    raw = first_value(section, "blocks", "content", "body_blocks")
    if raw is not None:
        blocks = listify(raw)
        raw_label = first_value(section, "label", "section_label", "name", "eyebrow")
        if key_token(raw_label) == "accessibility_feedback":
            return accessibility_feedback_blocks(blocks)
        return blocks

    # Transitional compatibility for a structured page that exposes its
    # principal blocks by name rather than under one array.
    blocks: list[Any] = []
    for key, block_type in (
        ("paragraphs", "paragraph"),
        ("lists", "list"),
        ("cards", "cards"),
        ("steps", "steps"),
        ("comparison", "comparison"),
        ("quote", "quote"),
        ("faq", "accordion"),
        ("table", "table"),
        ("form", "form"),
        ("ctas", "cta"),
    ):
        if key in section and section[key] not in (None, "", [], {}):
            value = section[key]
            if isinstance(value, Mapping):
                blocks.append({"type": block_type, **value})
            else:
                target_key = "items" if block_type not in {"paragraph", "quote"} else "text"
                blocks.append({"type": block_type, target_key: value})
    return blocks


def block_type(block: Mapping[str, Any]) -> str:
    raw = first_value(block, "type", "kind", "block_type", "layout")
    if raw is None:
        if "fields" in block or "acknowledgements" in block:
            return "form"
        if "question" in block and "answer" in block:
            return "accordion"
        if "quote" in block:
            return "quote"
        if "headers" in block and "rows" in block:
            return "table"
        if "items" in block:
            return "cards"
        if any(key in block for key in ("text", "paragraphs", "body")):
            return "paragraph"
        raise RenderError(f"block has no type and cannot be inferred: keys={sorted(block)}")
    token = key_token(raw)
    return BLOCK_ALIASES.get(token, token)


def card_cells(block: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Return the source cells from an extracted Word card table."""

    result: list[Mapping[str, Any]] = []
    for row in listify(block.get("rows")):
        if not isinstance(row, Mapping):
            continue
        for cell in listify(row.get("cells")):
            if isinstance(cell, Mapping):
                result.append(cell)
    return result


def clean_card_title(value: Any) -> str:
    title = normalise_space(value)
    return re.sub(
        r"^(?:\d{2}\s*[·.]?|[✦◇○◎↗⌁◌✓＋→!?])\s+",
        "",
        title,
    ).strip()


def accessibility_feedback_blocks(blocks: Sequence[Any]) -> list[Any]:
    """Promote the document's accessibility field cards into a real form.

    The Word source labels this section ``ACCESSIBILITY FEEDBACK`` rather than
    ``... FORM``, so the lossless extractor leaves its five field tables as
    cards. They are visibly form controls in the approved copy. This adapter
    keeps every source string while applying the shared endpoint, accessible
    validation, state handling and honeypot protection.
    """

    introductory: list[Any] = []
    fields: list[dict[str, Any]] = []
    submit_label = ""
    for block in blocks:
        if not isinstance(block, Mapping):
            introductory.append(block)
            continue
        kind = block_type(block)
        if kind == "cards":
            cells = card_cells(block)
            if len(cells) != 1:
                raise RenderError(
                    "accessibility feedback field cards must contain one cell"
                )
            nested = listify(first_value(cells[0], "blocks", "content"))
            copy = [
                normalise_space(first_value(item, "text", "body", "value"))
                for item in nested
                if isinstance(item, Mapping)
                and first_value(item, "text", "body", "value")
            ]
            if len(copy) < 2:
                raise RenderError(
                    "accessibility feedback field needs a label and helper text"
                )
            raw_label, helper = copy[0], copy[1]
            required = raw_label.rstrip().endswith("*")
            label = re.sub(r"\s*\*\s*$", "", raw_label)
            field: dict[str, Any] = {
                "name": key_token(label),
                "label": label,
                "type": "text",
                "required": required,
                "helper": helper,
            }
            if label == "Accessibility need or problem":
                field["type"] = "textarea"
                field["rows"] = 6
            elif label == "Preferred reply format":
                field["type"] = "select"
                field["options"] = [
                    value.strip()
                    for value in re.split(r"\s+·\s+", helper)
                    if value.strip()
                ]
                field.pop("helper", None)
            fields.append(field)
            continue
        if kind == "cta":
            items = listify(first_value(block, "items", "links", "actions"))
            if len(items) != 1 or not isinstance(items[0], Mapping):
                raise RenderError(
                    "accessibility feedback form needs one document submit action"
                )
            submit_label = normalise_space(
                first_value(items[0], "label", "text", "title")
            )
            continue
        introductory.append(block)

    if len(fields) != 5 or not submit_label:
        raise RenderError(
            "accessibility feedback copy did not yield five fields and a submit label"
        )
    introductory.append(
        {
            "type": "form",
            "fields": fields,
            "submit": {"label": submit_label},
            "hidden_fields": {"_subject": "Sofiati accessibility feedback"},
        }
    )
    return introductory


def faq_accordion_blocks(blocks: Sequence[Any]) -> list[Any]:
    """Group visible FAQ heading/answer pairs into keyboard-native details."""

    items: list[dict[str, str]] = []
    trailing: list[Any] = []
    index = 0
    while index < len(blocks):
        block = blocks[index]
        if not isinstance(block, Mapping) or block_type(block) != "heading":
            trailing.append(block)
            index += 1
            continue
        question = normalise_space(first_value(block, "text", "heading", "title"))
        answers: list[str] = []
        cursor = index + 1
        while cursor < len(blocks):
            candidate = blocks[cursor]
            if isinstance(candidate, Mapping) and block_type(candidate) == "heading":
                break
            if isinstance(candidate, Mapping) and block_type(candidate) in {"paragraph", "lead"}:
                answers.extend(
                    normalise_space(value)
                    for value in listify(
                        first_value(candidate, "text", "body", "paragraphs")
                    )
                    if normalise_space(value)
                )
                cursor += 1
                continue
            break
        if question and answers:
            items.append({"question": question, "answer": " ".join(answers)})
        else:
            trailing.append(block)
        index = max(cursor, index + 1)
    if not items:
        return list(blocks)
    return [{"type": "accordion", "items": items}, *trailing]


def first_card_copy(block: Mapping[str, Any]) -> tuple[str, list[str]]:
    cells = card_cells(block)
    if not cells:
        return "", []
    cell = cells[0]
    title = clean_card_title(first_value(cell, "title_text", "title"))
    nested = listify(first_value(cell, "blocks", "content"))
    copy = [
        normalise_space(first_value(item, "text", "body", "value"))
        for item in nested
        if isinstance(item, Mapping)
        and first_value(item, "text", "body", "value")
    ]
    source_title = normalise_space(first_value(cell, "title"))
    if copy and copy[0] == source_title:
        copy = copy[1:]
    return title, copy


def blog_search_blocks(blocks: Sequence[Any]) -> list[Any]:
    """Render the document's search-field cards as a semantic search form."""

    card_blocks = [
        block
        for block in blocks
        if isinstance(block, Mapping) and block_type(block) == "cards"
    ]
    action_blocks = [
        block
        for block in blocks
        if isinstance(block, Mapping) and block_type(block) == "cta"
    ]
    if len(card_blocks) < 3 or len(action_blocks) != 1:
        return list(blocks)
    label, search_copy = first_card_copy(card_blocks[0])
    filter_label, filter_copy = first_card_copy(card_blocks[1])
    empty_title, empty_copy = first_card_copy(card_blocks[-1])
    action_items = listify(
        first_value(action_blocks[0], "items", "links", "actions")
    )
    button = "Search the Blog"
    if action_items and isinstance(action_items[0], Mapping):
        button = normalise_space(
            first_value(action_items[0], "label", "text", "title") or button
        )
    topics = [
        value.strip()
        for value in re.split(r"\s+·\s+", filter_copy[0] if filter_copy else "")
        if value.strip()
    ]
    if not label or not search_copy or not filter_label or not topics:
        return list(blocks)
    return [
        {
            "type": "search",
            "label": label,
            "placeholder": search_copy[0],
            "filter_label": filter_label,
            "topics": topics,
            "button": button,
            "no_results": {
                "title": empty_title,
                "text": " ".join(empty_copy),
            },
        }
    ]


def treatment_directory_blocks(blocks: Sequence[Any]) -> list[Any]:
    """Group H3 treatment records into concise brochure-menu entries."""

    prefix: list[Any] = []
    treatments: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    current_field: str | None = None

    field_labels = {
        "what it is": "what_it_is",
        "what it may support": "what_it_may_support",
        "important to know": "important_to_know",
    }

    def add_to_current(block: Any) -> None:
        if current is None:
            return
        if current_field:
            existing = current.get(current_field)
            if existing is None:
                current[current_field] = block
            elif isinstance(existing, list):
                existing.append(block)
            else:
                current[current_field] = [existing, block]
            return
        current["blocks"].append(block)

    for block in blocks:
        is_treatment_heading = False
        if isinstance(block, Mapping) and block_type(block) == "heading":
            heading_text = normalise_space(first_value(block, "text", "title", "heading"))
            try:
                level = int(first_value(block, "level") or 3)
            except (TypeError, ValueError):
                level = 0
            is_treatment_heading = level == 3
            if current is not None and level >= 4 and heading_text.casefold() in field_labels:
                current_field = field_labels[heading_text.casefold()]
                continue
            if current is not None and level >= 4:
                current_field = None
        if is_treatment_heading:
            current = {
                "name": heading_text,
                "blocks": [],
            }
            source, alt = TREATMENT_MENU_IMAGES.get(
                heading_text,
                ("assets/treatments/Treatments1.png", f"{heading_text} treatment at the clinic"),
            )
            current["image"] = {"src": source, "alt": alt, "width": 1672, "height": 941}
            treatments.append(current)
            current_field = None
            continue
        if current is None:
            prefix.append(block)
        else:
            add_to_current(block)
    if not treatments:
        return list(blocks)
    return [*prefix, {"type": "treatment_group", "items": treatments}]


def cookie_settings_blocks(blocks: Sequence[Any]) -> list[Any]:
    """Turn the document's cookie-category cards into functional controls."""

    categories: list[dict[str, Any]] = []
    save_label = "Save My Choices"
    reject_label = "Reject Optional Cookies"
    accept_label = "Accept All Optional Cookies"
    for block in blocks:
        if not isinstance(block, Mapping):
            continue
        kind = block_type(block)
        if kind == "cards":
            title, copy = first_card_copy(block)
            if title:
                categories.append({"name": key_token(title), "label": title, "copy": copy})
        elif kind == "cta":
            actions = listify(first_value(block, "items", "links", "actions"))
            labels = [
                normalise_space(first_value(item, "label", "text", "title"))
                for item in actions
                if isinstance(item, Mapping)
            ]
            if labels:
                save_label = labels[0]
            if len(labels) > 1:
                reject_label = labels[1]
        elif kind in {"paragraph", "lead"}:
            text = normalise_space(first_value(block, "text", "body"))
            match = re.match(r"Additional button:\s*(.+)$", text, flags=re.I)
            if match:
                accept_label = match.group(1)
    if [category["name"] for category in categories] != [
        "essential",
        "preferences",
        "analytics",
        "external_media",
    ]:
        return list(blocks)
    return [
        {
            "type": "cookie_controls",
            "categories": categories,
            "save_label": save_label,
            "reject_label": reject_label,
            "accept_label": accept_label,
        }
    ]


def semantic_section_blocks(
    blocks: Sequence[Any], filename: str, order: int
) -> list[Any]:
    if filename == "faq.html":
        return faq_accordion_blocks(blocks)
    if filename == "blog.html" and order == 10:
        return blog_search_blocks(blocks)
    if filename == "treatments.html" and 2 <= order <= 9:
        return treatment_directory_blocks(blocks)
    if filename == "cookies.html" and order == 8:
        return cookie_settings_blocks(blocks)
    return list(blocks)


class FirstFormParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.form_attributes: dict[str, str] | None = None
        self.in_form = False
        self.honeypot_name: str | None = None

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        attr_map = {name: value or "" for name, value in attrs}
        if tag.casefold() == "form" and self.form_attributes is None:
            self.form_attributes = attr_map
            self.in_form = True
        elif tag.casefold() == "input" and self.in_form:
            classes = attr_map.get("class", "").split()
            if (
                "sf-honeypot" in classes
                or attr_map.get("name", "").casefold() in {"website", "_gotcha"}
            ) and attr_map.get("name"):
                self.honeypot_name = attr_map["name"]

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "form" and self.in_form:
            self.in_form = False


def form_defaults_from_source(source: str) -> FormDefaults | None:
    parser = FirstFormParser()
    parser.feed(source)
    if parser.form_attributes is None:
        return None
    keep = {
        key: value
        for key, value in parser.form_attributes.items()
        if key in {"action", "method", "accept-charset", "enctype", "novalidate"}
        or key.startswith("data-")
    }
    return FormDefaults(keep, parser.honeypot_name)


def page_url(filename: str, portuguese: bool = False) -> str:
    prefix = "/pt" if portuguese else ""
    if filename == "index.html":
        return f"{SITE_ORIGIN}{prefix}/"
    return f"{SITE_ORIGIN}{prefix}/{filename}"


def seo_entry(page: Mapping[str, Any]) -> Mapping[str, Any]:
    value = first_value(page, "seo", "metadata")
    return value if isinstance(value, Mapping) else {}


def faq_schema_entities(page: Mapping[str, Any], filename: str) -> list[dict[str, Any]]:
    if filename != "faq.html":
        return []
    entities: list[dict[str, Any]] = []
    for section in section_entries(page, filename):
        blocks = section_blocks(section)
        index = 0
        while index < len(blocks):
            block = blocks[index]
            if not isinstance(block, Mapping) or block_type(block) != "heading":
                index += 1
                continue
            question = normalise_space(first_value(block, "text", "heading", "title"))
            answers: list[str] = []
            cursor = index + 1
            while cursor < len(blocks):
                candidate = blocks[cursor]
                if isinstance(candidate, Mapping) and block_type(candidate) == "heading":
                    break
                if isinstance(candidate, Mapping) and block_type(candidate) in {"paragraph", "lead"}:
                    value = first_value(candidate, "text", "body", "paragraphs")
                    answers.extend(
                        normalise_space(item)
                        for item in listify(value)
                        if normalise_space(item)
                    )
                cursor += 1
            if question and answers:
                entities.append(
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": " ".join(answers),
                        },
                    }
                )
            index = max(cursor, index + 1)
    return entities


def structured_data(page: Mapping[str, Any], filename: str) -> dict[str, Any]:
    url = page_url(filename)
    title = normalise_space(first_value(seo_entry(page), "title", "seo_title"))
    description = normalise_space(
        first_value(seo_entry(page), "meta_description", "description")
    )
    page_id = f"{url}#webpage"
    breadcrumb_id = f"{url}#breadcrumb"
    breadcrumb_items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Home",
            "item": page_url("index.html"),
        }
    ]
    if filename != "index.html":
        breadcrumb_items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": page_title(page, filename),
                "item": url,
            }
        )
    webpage_type = "FAQPage" if filename == "faq.html" else "WebPage"
    webpage: dict[str, Any] = {
        "@type": webpage_type,
        "@id": page_id,
        "url": url,
        "name": title,
        "description": description,
        "inLanguage": "en",
        "isPartOf": {"@id": f"{SITE_ORIGIN}/#website"},
        "about": {"@id": f"{SITE_ORIGIN}/#franciele"},
        "breadcrumb": {"@id": breadcrumb_id},
        "primaryImageOfPage": {"@id": f"{OG_IMAGE}#primaryimage"},
    }
    faq_entities = faq_schema_entities(page, filename)
    if faq_entities:
        webpage["mainEntity"] = faq_entities
    return {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebSite",
                "@id": f"{SITE_ORIGIN}/#website",
                "url": f"{SITE_ORIGIN}/",
                "name": SITE_NAME,
                "inLanguage": ["en", "pt-BR"],
            },
            {
                "@type": "Person",
                "@id": f"{SITE_ORIGIN}/#franciele",
                "name": "Franciele Sofiati",
                "jobTitle": "Biomedical Practitioner, Aesthetician and Cosmetologist",
                "email": SITE_EMAIL,
                "telephone": SITE_TELEPHONE,
                "worksFor": {"@id": f"{SITE_ORIGIN}/#practice"},
                "sameAs": [SITE_INSTAGRAM],
            },
            {
                "@type": "HealthAndBeautyBusiness",
                "@id": f"{SITE_ORIGIN}/#practice",
                "name": SITE_NAME,
                "url": f"{SITE_ORIGIN}/",
                "email": SITE_EMAIL,
                "telephone": SITE_TELEPHONE,
                "image": OG_IMAGE,
                "logo": LOGO_IMAGE,
                "areaServed": {
                    "@type": "City",
                    "name": "Londrina, Paraná, Brazil",
                },
                "founder": {"@id": f"{SITE_ORIGIN}/#franciele"},
                "sameAs": [SITE_INSTAGRAM],
            },
            {
                "@type": "ImageObject",
                "@id": f"{OG_IMAGE}#primaryimage",
                "url": OG_IMAGE,
                "contentUrl": OG_IMAGE,
                "width": 1134,
                "height": 1183,
            },
            {
                "@type": "BreadcrumbList",
                "@id": breadcrumb_id,
                "itemListElement": breadcrumb_items,
            },
            webpage,
        ],
    }


def render_head(page: Mapping[str, Any], filename: str) -> str:
    seo = seo_entry(page)
    title = normalise_space(first_value(seo, "title", "seo_title"))
    description = normalise_space(
        first_value(seo, "meta_description", "description")
    )
    if not title or not description:
        raise RenderError(f"{filename}: SEO title and description are required")
    url = page_url(filename)
    pt_url = page_url(filename, portuguese=True)
    robots = (
        "noindex, follow"
        if filename in {"404.html", "thank-you.html"}
        else "index, follow"
    )
    schema = json.dumps(
        structured_data(page, filename),
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    return "\n".join(
        (
            "<head>",
            '<meta charset="utf-8"/>',
            '<meta name="viewport" content="width=device-width, initial-scale=1"/>',
            '<meta name="theme-color" content="#66755f"/>',
            f'<meta name="robots" content="{robots}"/>',
            f'<meta name="description" content="{escape(description, quote=True)}"/>',
            f"<title>{html_text(title)}</title>",
            f'<link rel="canonical" href="{escape(url, quote=True)}"/>',
            f'<link rel="alternate" hreflang="en" href="{escape(url, quote=True)}"/>',
            f'<link rel="alternate" hreflang="pt-BR" href="{escape(pt_url, quote=True)}"/>',
            f'<link rel="alternate" hreflang="x-default" href="{escape(url, quote=True)}"/>',
            f'<meta property="og:title" content="{escape(title, quote=True)}"/>',
            f'<meta property="og:description" content="{escape(description, quote=True)}"/>',
            f'<meta property="og:url" content="{escape(url, quote=True)}"/>',
            '<meta property="og:type" content="website"/>',
            '<meta property="og:site_name" content="Franciele Sofiati Biomédica"/>',
            '<meta property="og:locale" content="en_US"/>',
            f'<meta property="og:image" content="{OG_IMAGE}"/>',
            '<meta property="og:image:width" content="1134"/>',
            '<meta property="og:image:height" content="1183"/>',
            '<meta name="twitter:card" content="summary_large_image"/>',
            f'<meta name="twitter:title" content="{escape(title, quote=True)}"/>',
            f'<meta name="twitter:description" content="{escape(description, quote=True)}"/>',
            f'<meta name="twitter:image" content="{OG_IMAGE}"/>',
            f'<script type="application/ld+json">{schema}</script>',
            '<link rel="icon" type="image/png" sizes="96x96" href="assets/favicons/sofiati-favicon-96.png"/>',
            '<link rel="shortcut icon" href="favicon.ico"/>',
            '<link rel="apple-touch-icon" sizes="180x180" href="assets/favicons/apple-touch-icon-180.png"/>',
            '<link rel="manifest" href="site.webmanifest"/>',
            '<link rel="stylesheet" href="css/site.css"/>',
            "</head>",
        )
    )


def apply_document_head(source: str, page: Mapping[str, Any], filename: str) -> str:
    matches = list(HEAD_RE.finditer(source))
    if len(matches) != 1:
        raise RenderError(f"{filename}: expected exactly one <head>, found {len(matches)}")
    return HEAD_RE.sub(lambda _match: render_head(page, filename), source, count=1)


def read_skeleton(
    root: Path, filename: str, page: Mapping[str, Any] | None = None
) -> PageSkeleton:
    path = root / filename
    if not path.is_file():
        raise RenderError(f"missing existing page skeleton: {path}")
    original_source = path.read_text(encoding="utf-8")
    defaults = form_defaults_from_source(original_source)
    source = apply_document_head(original_source, page, filename) if page else original_source
    matches = list(MAIN_RE.finditer(source))
    if len(matches) != 1:
        raise RenderError(f"{filename}: expected exactly one <main>, found {len(matches)}")
    match = matches[0]
    return PageSkeleton(
        filename=filename,
        source=source,
        main_open=match.group("open"),
        prefix=source[: match.end("open")],
        suffix=source[match.start("close") :],
        partials=tuple(PARTIAL_RE.findall(source)),
        form_defaults=defaults,
    )


def common_form_defaults(skeletons: Mapping[str, PageSkeleton]) -> FormDefaults | None:
    candidates = [
        skeleton.form_defaults
        for filename, skeleton in skeletons.items()
        if filename in {"contact.html", "consultation.html"}
        and skeleton.form_defaults is not None
    ]
    if not candidates:
        return None
    first = candidates[0]
    if all(candidate.attributes == first.attributes for candidate in candidates[1:]):
        honeypot = next(
            (candidate.honeypot_name for candidate in candidates if candidate.honeypot_name),
            None,
        )
        return FormDefaults(first.attributes, honeypot)
    return None


def page_title(page: Mapping[str, Any], filename: str) -> str:
    value = first_value(page, "page_title", "display_title", "title", "name")
    if value:
        return normalise_space(value)
    return PAGE_LABELS[filename]


def render_hero_brand() -> str:
    return (
        '<p class="sf-hero-brand" translate="no">'
        '<img src="assets/brand/sofiati-logo-menu.webp" alt="" '
        'width="32" height="32" loading="eager" decoding="async"/>'
        '<span>Franciele Sofiati · Biomedical Aesthetics</span>'
        '</p>'
    )


def render_contact_form_guide() -> str:
    """Keep the practical contact context inside the single form scene."""

    whatsapp = SITE_TELEPHONE.removeprefix("+")
    return (
        '<aside class="sf-contact-form-guide" aria-label="Other ways to reach the clinic">'
        '<p class="sf-contact-form-guide__promise">'
        'A personal reply <span aria-hidden="true">·</span> Your privacy matters '
        '<span aria-hidden="true">·</span> An enquiry is not a booking</p>'
        '<h2>Would you rather contact Franciele directly?</h2>'
        '<ul class="sf-contact-form-guide__routes">'
        '<li><a href="https://wa.me/'
        f'{escape(whatsapp, quote=True)}"><span>WhatsApp</span>'
        '<strong>(43) 9 9104-3536</strong></a></li>'
        f'<li><a href="mailto:{escape(SITE_EMAIL, quote=True)}"><span>Email</span>'
        f'<strong>{escape(SITE_EMAIL)}</strong></a></li>'
        '<li><span>Clinic</span><strong>Londrina, Paraná, Brazil</strong></li>'
        '</ul>'
        '<p class="sf-contact-form-guide__safety"><strong>Important:</strong> '
        'the contact form is not an emergency service.</p>'
        '</aside>'
    )


def render_breadcrumbs(page: Mapping[str, Any], filename: str) -> str:
    current = html_text(page_title(page, filename))
    if filename == "index.html":
        items = f'<li><span aria-current="page">{current}</span></li>'
    else:
        items = (
            '<li><a href="index.html">Home</a></li>'
            f'<li><span aria-current="page">{current}</span></li>'
        )
    return (
        '<nav class="sf-breadcrumbs sf-container" aria-label="Breadcrumb">\n'
        f'<ol>{items}</ol>\n'
        "</nav>"
    )


def explicit_pattern(section: Mapping[str, Any]) -> str | None:
    raw = first_value(section, "pattern", "presentation", "section_pattern")
    if raw is None:
        return None
    token = class_token(raw).replace("-", "_")
    token = PATTERN_ALIASES.get(token.replace("_", "-"), token)
    token = PATTERN_ALIASES.get(token, token)
    return token


def infer_pattern(
    section: Mapping[str, Any], blocks: Sequence[Any], filename: str, order: int
) -> str:
    requested = explicit_pattern(section)
    if requested:
        return requested
    journey = PAGE_PATTERN_JOURNEYS.get(filename)
    if not journey or order > len(journey):
        raise RenderError(
            f"{filename}: section {order} needs an explicit pattern in the content art map"
        )
    return journey[order - 1]


def block_title(block: Mapping[str, Any]) -> Any:
    return first_value(block, "title", "heading", "name", "label")


def render_paragraphs(values: Any, class_name: str = "") -> str:
    result: list[str] = []
    for value in listify(values):
        if isinstance(value, Mapping):
            text = first_value(value, "text", "body", "value", "paragraph")
        else:
            text = value
        if text not in (None, ""):
            class_attr = f' class="{escape(class_name, quote=True)}"' if class_name else ""
            result.append(f"<p{class_attr}>{html_prose(text)}</p>")
    return "\n".join(result)


def render_link(link: Any, class_name: str = "sf-button sf-button--outline") -> str:
    if isinstance(link, str):
        label = normalise_space(link)
        href = INTERNAL_LINKS.get(label.casefold())
        if href is None:
            raise RenderError(f"CTA {label!r} needs an explicit href")
        data: Mapping[str, Any] = {}
    elif isinstance(link, Mapping):
        label = normalise_space(first_value(link, "label", "text", "title", "name"))
        href = first_value(link, "href", "url", "path")
        if not href and label:
            href = INTERNAL_LINKS.get(label.casefold())
        data = link
    else:
        raise RenderError(f"invalid CTA/link: {link!r}")
    if not label or not href:
        raise RenderError(f"CTA/link requires label and href: {link!r}")
    css = normalise_space(first_value(data, "class", "class_name") or class_name)
    attrs = [f'class="{escape(css, quote=True)}"', f'href="{escape(str(href), quote=True)}"']
    if label.casefold() == "open cookie settings":
        attrs.append("data-cookie-manage")
    if data.get("target"):
        attrs.append(f'target="{escape(str(data["target"]), quote=True)}"')
        if str(data["target"]) == "_blank":
            attrs.append('rel="noopener noreferrer"')
    return f"<a {' '.join(attrs)}>{html_text(label)}</a>"


def render_cta(block: Mapping[str, Any]) -> str:
    links: list[Any] = []
    links.extend(listify(first_value(block, "links", "items", "buttons", "actions")))
    for key in ("primary", "secondary", "tertiary"):
        if block.get(key):
            links.append(block[key])
    if not links and first_value(block, "label", "text"):
        links.append(block)
    if not links:
        raise RenderError("CTA block has no links")
    rendered = []
    for index, link in enumerate(links):
        css = "sf-button sf-button--primary" if index == 0 else "sf-button sf-button--outline"
        rendered.append(render_link(link, css))
    return f'<div class="sf-button-row">{"".join(rendered)}</div>'


def render_list_item(item: Any) -> str:
    if isinstance(item, str):
        return f"<li>{html_text(item)}</li>"
    if not isinstance(item, Mapping):
        return f"<li>{html_text(item)}</li>"
    title = first_value(item, "title", "heading", "name", "label", "term")
    body = first_value(item, "text", "body", "description", "definition", "answer")
    pieces: list[str] = []
    if title:
        pieces.append(f"<strong>{html_text(title)}</strong>")
    if body:
        pieces.append(f"<span>{html_text(body)}</span>")
    nested = first_value(item, "items", "points", "bullets")
    if nested:
        pieces.append(render_list(nested, ordered=False))
    cta = first_value(item, "link", "cta")
    if cta:
        pieces.append(render_link(cta, "sf-text-link"))
    return f"<li>{''.join(pieces)}</li>"


def render_list(items: Any, ordered: bool = False, class_name: str = "") -> str:
    tag = "ol" if ordered else "ul"
    classes = class_name or ("sf-numbered-list" if ordered else "sf-botanical-list")
    body = "".join(render_list_item(item) for item in listify(items))
    return f'<{tag} class="{escape(classes, quote=True)}">{body}</{tag}>'


def render_item_body(item: Mapping[str, Any], heading_level: int = 3) -> str:
    pieces: list[str] = []
    title = block_title(item)
    if title:
        pieces.append(f"<h{heading_level}>{html_text(title)}</h{heading_level}>")
    subtitle = first_value(item, "subtitle", "eyebrow", "kicker")
    if subtitle:
        pieces.insert(0, f'<p class="sf-eyebrow">{html_text(subtitle)}</p>')
    body = first_value(item, "paragraphs", "body", "text", "description", "answer")
    if body:
        pieces.append(render_paragraphs(body))
    points = first_value(item, "items", "points", "bullets", "list")
    if points:
        pieces.append(render_list(points, ordered=bool(item.get("ordered"))))
    nested = first_value(item, "blocks", "content")
    if nested:
        pieces.append(render_blocks(listify(nested), heading_level + 1))
    cta = first_value(item, "cta", "link")
    if cta:
        pieces.append(render_link(cta, "sf-text-link"))
    return "\n".join(piece for piece in pieces if piece)


def render_cards(block: Mapping[str, Any], heading_level: int = 3) -> str:
    title = block_title(block)
    pieces = [f"<h{heading_level}>{html_text(title)}</h{heading_level}>"] if title else []
    items = listify(first_value(block, "items", "cards", "entries", "routes", "quotes"))
    if not items and block.get("rows"):
        for cell in card_cells(block):
            nested = listify(first_value(cell, "blocks", "content"))
            raw_title = clean_card_title(
                first_value(cell, "title_text", "title", "heading", "name")
            )
            source_title = normalise_space(first_value(cell, "title"))
            if nested and isinstance(nested[0], Mapping):
                first_text = normalise_space(
                    first_value(nested[0], "text", "body", "value")
                )
                if first_text and first_text == source_title:
                    nested = nested[1:]
            item: dict[str, Any] = {"blocks": nested}
            if raw_title:
                item["title"] = raw_title
            if cell.get("marker"):
                item["marker"] = cell["marker"]
            items.append(item)
    if not items:
        raise RenderError("cards block has no items")
    cards: list[str] = []
    for item in items:
        if isinstance(item, str):
            body = f"<p>{html_text(item)}</p>"
        elif isinstance(item, Mapping):
            body = render_item_body(item, heading_level=heading_level)
        else:
            body = f"<p>{html_text(item)}</p>"
        marker = normalise_space(item.get("marker")) if isinstance(item, Mapping) else ""
        tone = {
            "✓": "support",
            "✦": "support",
            "◇": "consideration",
            "!": "caution",
            "○": "neutral",
            "◎": "focus",
            "↗": "focus",
            "⌁": "neutral",
            "◌": "neutral",
            "＋": "standard",
            "→": "standard",
        }.get(marker, "standard")
        href = None
        if isinstance(item, Mapping):
            href = first_value(item, "href", "url")
            if not href:
                item_title = normalise_space(block_title(item)).casefold()
                href = CARD_DESTINATIONS.get(item_title)
        if href:
            cards.append(
                f'<a class="sf-content-card sf-content-card--{tone} sf-content-card--link" '
                f'href="{escape(str(href), quote=True)}">{body}</a>'
            )
        else:
            cards.append(
                f'<article class="sf-content-card sf-content-card--{tone}">{body}</article>'
            )
    pieces.append(
        f'<div class="sf-content-card-grid" data-card-count="{len(cards)}">'
        f'{"".join(cards)}</div>'
    )
    return "\n".join(pieces)


def render_steps(block: Mapping[str, Any]) -> str:
    items = listify(first_value(block, "items", "steps", "entries"))
    if not items:
        raise RenderError("steps block has no items")
    rendered: list[str] = []
    for index, item in enumerate(items, start=1):
        if isinstance(item, Mapping):
            body = render_item_body(item)
        else:
            body = f"<p>{html_text(item)}</p>"
        rendered.append(
            '<li class="sf-step">'
            f'<span class="sf-step-number" aria-hidden="true">{index:02d}</span>'
            f'<div class="sf-step-copy">{body}</div></li>'
        )
    return f'<ol class="sf-process-list">{"".join(rendered)}</ol>'


def render_quote(
    block: Mapping[str, Any], context: RenderContext | None = None
) -> str:
    quote = first_value(block, "quote", "text", "body", "statement")
    if not quote:
        raise RenderError("quote block has no quote/text")
    quote_text = str(quote).strip()
    if (
        len(quote_text) > 1
        and quote_text[0] in {'“', '"'}
        and quote_text[-1] in {'”', '"'}
    ):
        quote_text = quote_text[1:-1].strip()
    attribution = first_value(block, "attribution", "cite", "source", "author")
    if not attribution:
        statement_class = (
            ""
            if context and context.filename == "testimonials.html"
            else " sf-practitioner-statement"
        )
        return (
            f'<aside class="sf-pull-quote{statement_class}">'
            f'<p>{html_text(quote_text)}</p></aside>'
        )
    quote_kind = (
        "sf-testimonial-quote"
        if "patient" in str(attribution).lower()
        else "sf-practitioner-quote"
    )
    footer = f"<figcaption><cite>{html_text(attribution)}</cite></figcaption>"
    return (
        f'<figure class="{quote_kind}">'
        f'<blockquote class="sf-pull-quote"><p>{html_text(quote_text)}</p></blockquote>'
        f"{footer}</figure>"
    )


def render_comparison(block: Mapping[str, Any]) -> str:
    sides = listify(first_value(block, "sides", "columns", "items", "panels"))
    if not sides:
        left = block.get("left")
        right = block.get("right")
        sides = [item for item in (left, right) if item]
    if len(sides) < 2:
        raise RenderError("comparison block needs at least two sides")
    rendered = []
    for side in sides:
        if isinstance(side, Mapping):
            body = render_item_body(side)
        else:
            body = f"<p>{html_text(side)}</p>"
        rendered.append(f'<article class="sf-comparison-panel">{body}</article>')
    return f'<div class="sf-comparison-grid">{"".join(rendered)}</div>'


def render_table(block: Mapping[str, Any]) -> str:
    headers = listify(first_value(block, "headers", "columns"))
    rows = listify(first_value(block, "rows", "items", "entries"))
    if not rows:
        raise RenderError("table block has no rows")
    caption = first_value(block, "caption", "title")
    caption_html = f"<caption>{html_text(caption)}</caption>" if caption else ""
    head_html = ""
    if headers:
        head_html = "<thead><tr>" + "".join(
            f'<th scope="col">{html_text(header)}</th>' for header in headers
        ) + "</tr></thead>"
    rendered_rows: list[str] = []
    for row in rows:
        if isinstance(row, Mapping):
            cells = listify(first_value(row, "cells", "values", "items"))
            if not cells and headers:
                cells = [row.get(normalise_space(header), "") for header in headers]
        else:
            cells = listify(row)
        rendered_cells = []
        for index, cell in enumerate(cells):
            tag = "th" if index == 0 else "td"
            scope = ' scope="row"' if tag == "th" else ""
            rendered_cells.append(f"<{tag}{scope}>{html_text(cell)}</{tag}>")
        rendered_rows.append(f"<tr>{''.join(rendered_cells)}</tr>")
    return (
        '<div class="sf-table-scroll" tabindex="0" role="region" '
        'aria-label="Scrollable table">'
        f'<table class="sf-content-table">{caption_html}{head_html}'
        f"<tbody>{''.join(rendered_rows)}</tbody></table></div>"
    )


def render_accordion(block: Mapping[str, Any]) -> str:
    items = listify(first_value(block, "items", "questions", "entries", "faqs"))
    if not items and first_value(block, "question", "title"):
        items = [block]
    if not items:
        raise RenderError("accordion block has no questions")
    rendered: list[str] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise RenderError("accordion questions must be objects")
        question = first_value(item, "question", "title", "summary")
        answer = first_value(item, "answer", "body", "text", "content")
        if not question or not answer:
            raise RenderError("accordion item requires question and answer")
        if isinstance(answer, (list, Mapping)) and not isinstance(answer, str):
            if isinstance(answer, Mapping):
                answer_html = render_item_body(answer, heading_level=4)
            else:
                answer_html = render_paragraphs(answer)
        else:
            answer_html = f"<p>{html_text(answer)}</p>"
        rendered.append(
            '<details class="sf-accordion-item">'
            f"<summary>{html_text(question)}</summary>"
            f'<div class="sf-accordion-answer">{answer_html}</div></details>'
        )
    return f'<div class="sf-accordion">{"".join(rendered)}</div>'


def render_definition_list(block: Mapping[str, Any]) -> str:
    items = listify(first_value(block, "items", "definitions", "entries"))
    rendered: list[str] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise RenderError("definition-list entries must be objects")
        term = first_value(item, "term", "title", "name", "label")
        definition = first_value(item, "definition", "body", "text", "description")
        if not term or not definition:
            raise RenderError("definition-list entry requires term and definition")
        rendered.append(f"<dt>{html_text(term)}</dt><dd>{html_text(definition)}</dd>")
    return f'<dl class="sf-definition-list">{"".join(rendered)}</dl>'


def render_callout(block: Mapping[str, Any]) -> str:
    title = block_title(block)
    body = first_value(block, "body", "text", "paragraphs", "message")
    tone = class_token(first_value(block, "tone", "level", "variant") or "note")
    role = ' role="alert"' if tone in {"warning", "danger", "urgent", "error"} else ""
    pieces = [f"<h3>{html_text(title)}</h3>"] if title else []
    if body:
        pieces.append(render_paragraphs(body))
    points = first_value(block, "items", "points", "bullets")
    if points:
        pieces.append(render_list(points))
    return f'<aside class="sf-callout sf-callout--{tone}"{role}>{"".join(pieces)}</aside>'


def treatment_detail_blocks(blocks: Sequence[Any]) -> list[Any]:
    """Keep treatment detail headings as sibling H4 groups under the treatment H3."""
    rendered: list[Any] = []
    for block in blocks:
        if isinstance(block, Mapping) and block_type(block) == "heading":
            rendered.append({**block, "level": 4})
        else:
            rendered.append(block)
    return rendered


def treatment_text(value: Any, fallback: str = "") -> str:
    parts: list[str] = []
    for item in listify(value):
        if isinstance(item, Mapping):
            if block_type(item) in {"paragraph", "lead"}:
                text = first_value(item, "text", "body", "paragraphs")
                parts.extend(normalise_space(part) for part in listify(text) if normalise_space(part))
            elif block_type(item) == "list":
                for point in listify(first_value(item, "items", "points", "bullets")):
                    if isinstance(point, Mapping):
                        parts.append(normalise_space(first_value(point, "text", "label", "title")))
                    else:
                        parts.append(normalise_space(point))
        elif item:
            parts.append(normalise_space(item))
    text = " ".join(part for part in parts if part)
    if not text:
        return fallback
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return normalise_space(sentences[0] if sentences else text)


def treatment_points(value: Any, limit: int = 3) -> list[str]:
    points: list[str] = []
    for item in listify(value):
        if isinstance(item, Mapping) and block_type(item) == "list":
            raw_points = first_value(item, "items", "points", "bullets")
        else:
            raw_points = item if isinstance(item, list) else [item]
        for point in listify(raw_points):
            if isinstance(point, Mapping):
                text = first_value(point, "text", "label", "title", "value")
            else:
                text = point
            clean = normalise_space(text).rstrip(";.")
            if clean:
                points.append(clean)
            if len(points) >= limit:
                return points
    return points


def treatment_filter_tokens(value: Any) -> str:
    tokens = [class_token(item) for item in listify(value) if normalise_space(item)]
    return " ".join(dict.fromkeys(tokens))


def render_treatment_group(block: Mapping[str, Any]) -> str:
    treatments = listify(first_value(block, "items", "treatments", "entries"))
    if not treatments:
        raise RenderError("treatment group has no treatments")
    variant = class_token(first_value(block, "variant", "presentation") or "standard")
    group_title = first_value(block, "title", "heading")
    group_intro = first_value(block, "intro", "description")
    heading_tag = "h4" if group_title else "h3"
    rendered: list[str] = []
    for treatment in treatments:
        if not isinstance(treatment, Mapping):
            raise RenderError("treatment entries must be objects")
        name = first_value(treatment, "name", "title", "heading")
        if not name:
            raise RenderError("treatment entry has no name")
        image = treatment.get("image") if isinstance(treatment.get("image"), Mapping) else {}
        src = first_value(image, "src") or "assets/treatments/Treatments1.png"
        alt = first_value(image, "alt") or f"{name} treatment at the clinic"
        width = int(first_value(image, "width") or 1672)
        height = int(first_value(image, "height") or 941)
        definition = treatment_text(treatment.get("what_it_is"))
        supports = treatment_points(treatment.get("what_it_may_support"), limit=3)
        note = treatment_text(treatment.get("important_to_know"))
        technology = treatment_text(treatment.get("technology_label"))
        recovery = treatment_text(treatment.get("recovery_label"))
        filter_attributes = []
        for field in ("concern", "area", "technology", "recovery"):
            value = treatment_filter_tokens(treatment.get(field))
            if value:
                filter_attributes.append(
                    f'data-treatment-{field}="{escape(value, quote=True)}"'
                )
        attributes = " ".join(filter_attributes)
        support_html = ""
        if supports:
            support_html = (
                '<ul class="sf-treatment-menu-tags">'
                + "".join(f"<li>{html_text(point)}</li>" for point in supports)
                + "</ul>"
            )
        note_html = (
            f'<aside class="sf-treatment-menu-note"><strong>Important:</strong> {html_text(note)}</aside>'
            if note
            else ""
        )
        cta = first_value(treatment, "cta", "link")
        cta_html = render_link(cta, "sf-text-link") if cta else ""
        metadata_html = ""
        if technology or recovery:
            rows = []
            if technology:
                rows.append(
                    '<div><dt>Technology</dt>'
                    f'<dd>{html_text(technology)}</dd></div>'
                )
            if recovery:
                rows.append(
                    '<div><dt>Recovery note</dt>'
                    f'<dd>{html_text(recovery)}</dd></div>'
                )
            metadata_html = f'<dl class="sf-treatment-meta">{"".join(rows)}</dl>'
        rendered.append(
            '<article class="sf-treatment-entry sf-treatment-menu-card" '
            f'data-treatment-entry {attributes}>'
            '<figure class="sf-treatment-menu-card__media">'
            f'<img src="{escape(str(src), quote=True)}" alt="{escape(str(alt), quote=True)}" '
            f'width="{width}" height="{height}" loading="lazy" decoding="async" '
            'sizes="(max-width: 48rem) 100vw, 50vw"/>'
            '</figure>'
            '<div class="sf-treatment-menu-card__copy">'
            f'<p class="sf-treatment-menu-card__label">Service</p>'
            f'<{heading_tag}>{html_text(name)}</{heading_tag}>'
            f'<p>{html_text(definition)}</p>'
            f"{support_html}{metadata_html}{note_html}{cta_html}"
            '</div></article>'
        )
    heading_html = ""
    if group_title:
        heading_html = '<header class="sf-treatment-group-head">'
        heading_html += f'<h3>{html_text(group_title)}</h3>'
        if group_intro:
            heading_html += f'<p>{html_text(group_intro)}</p>'
        heading_html += '</header>'
    return (
        f'<div class="sf-treatment-directory sf-treatment-menu" '
        f'data-treatment-layout="{escape(variant, quote=True)}">'
        f'{heading_html}{"".join(rendered)}</div>'
    )


def render_treatment_finder(block: Mapping[str, Any]) -> str:
    fields = listify(first_value(block, "fields", "filters"))
    if not fields:
        raise RenderError("treatment finder requires filter fields")
    rendered_fields: list[str] = []
    for field in fields:
        if not isinstance(field, Mapping):
            raise RenderError("treatment finder fields must be objects")
        name = class_token(first_value(field, "name", "id", "label"))
        label = first_value(field, "label", "title", "name")
        if not label:
            raise RenderError("treatment finder field requires a label")
        control_id = f"treatment-filter-{name}"
        options = [
            f'<option value="">{html_text(first_value(field, "all_label") or "Any")}</option>'
        ]
        for option in listify(first_value(field, "options", "items")):
            if isinstance(option, Mapping):
                value = class_token(first_value(option, "value", "id", "label"))
                option_label = first_value(option, "label", "title", "value")
            else:
                value = class_token(option)
                option_label = option
            options.append(
                f'<option value="{escape(value, quote=True)}">{html_text(option_label)}</option>'
            )
        rendered_fields.append(
            '<div class="sf-treatment-finder__field">'
            f'<label for="{control_id}">{html_text(label)}</label>'
            f'<select id="{control_id}" data-treatment-facet="{escape(name, quote=True)}">'
            f'{"".join(options)}</select></div>'
        )
    action_label = first_value(block, "action_label", "reset_label") or "Explore all"
    singular = first_value(block, "status_singular") or "{count} treatment shown"
    plural = first_value(block, "status_plural") or "{count} treatments shown"
    empty = first_value(block, "empty_status") or "No treatments match every choice."
    return (
        '<div class="sf-treatment-finder" data-treatment-filter role="search" '
        'aria-label="Filter treatment directory">'
        f'<div class="sf-treatment-finder__fields">{"".join(rendered_fields)}</div>'
        '<div class="sf-treatment-finder__footer">'
        f'<button class="sf-treatment-finder__reset" type="button" data-treatment-reset>{html_text(action_label)}</button>'
        '<p class="sf-treatment-finder__status" data-treatment-filter-status role="status" '
        f'data-label-singular="{escape(str(singular), quote=True)}" '
        f'data-label-plural="{escape(str(plural), quote=True)}" '
        f'data-label-empty="{escape(str(empty), quote=True)}"></p>'
        '</div></div>'
    )


def render_contact_list(block: Mapping[str, Any]) -> str:
    items = listify(first_value(block, "items", "contacts", "entries"))
    rendered: list[str] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise RenderError("contact-list entries must be objects")
        label = first_value(item, "label", "title", "name", "type")
        value = first_value(item, "value", "text", "address")
        href = first_value(item, "href", "url")
        if not label or not value:
            raise RenderError("contact-list entry requires label and value")
        content = html_text(value)
        if href:
            content = f'<a href="{escape(str(href), quote=True)}">{content}</a>'
        rendered.append(
            '<div class="sf-contact-item">'
            f"<dt>{html_text(label)}</dt><dd>{content}</dd></div>"
        )
    return f'<dl class="sf-contact-list">{"".join(rendered)}</dl>'


def render_required_marker(required: bool) -> str:
    if not required:
        return ""
    return (
        '<span class="sf-required" aria-hidden="true"> *</span>'
        '<span class="sf-visually-hidden"> (required)</span>'
    )


def field_help_values(field: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("helper", "help", "description", "note", "instructions"):
        for value in listify(field.get(key)):
            if value not in (None, ""):
                values.append(normalise_space(value))
    return values


def field_options(field: Mapping[str, Any]) -> list[Any]:
    return listify(first_value(field, "options", "choices", "values"))


def render_field(field: Mapping[str, Any], form_id: str, index: int) -> str:
    raw_label = first_value(field, "label", "title", "name")
    if not raw_label:
        raise RenderError("form field has no label")
    label = re.sub(r"\s*\*\s*$", "", normalise_space(raw_label))
    name = normalise_space(first_value(field, "name", "key", "id") or slugify(label)).replace("-", "_")
    field_id = f"{form_id}-{slugify(first_value(field, 'id') or name or index)}"
    required = bool(field.get("required")) or normalise_space(raw_label).endswith("*")
    raw_type = key_token(first_value(field, "type", "control", "input_type") or "")
    options = field_options(field)
    if not raw_type:
        raw_type = "select" if options else "text"
    if raw_type in {"acknowledgement", "consent"}:
        raw_type = "checkbox"
    if raw_type in {"radio_group", "radios"}:
        raw_type = "radio"

    placeholder = first_value(field, "placeholder", "example")
    helpers = field_help_values(field)
    if raw_type == "date" and placeholder:
        helpers.insert(0, normalise_space(placeholder))
    help_id = f"{field_id}-help" if helpers else ""
    error_id = f"{field_id}-error"
    described_by = " ".join(value for value in (help_id, error_id) if value)
    required_attr = " required" if required else ""
    common = (
        f'id="{escape(field_id, quote=True)}" '
        f'name="{escape(name, quote=True)}"'
        f'{required_attr} aria-describedby="{escape(described_by, quote=True)}"'
    )
    marker = render_required_marker(required)
    helper_html = ""
    if helpers:
        helper_html = f'<p class="sf-field-help" id="{help_id}">' + " ".join(
            html_text(value) for value in helpers
        ) + "</p>"
    error_html = (
        f'<p class="sf-form-error" id="{error_id}" data-error-for="{field_id}" '
        'role="alert" hidden></p>'
    )

    if raw_type == "checkbox":
        consent = first_value(field, "text", "value", "acknowledgement", "statement")
        consent_text = normalise_space(consent or label)
        return (
            '<div class="sf-field sf-field--checkbox">'
            f'<label for="{field_id}"><input {common} type="checkbox" value="yes"/>'
            f"<span>{html_text(consent_text)}{marker}</span></label>"
            f"{helper_html}{error_html}</div>"
        )

    if raw_type == "radio":
        if not options:
            raise RenderError(f"radio field {label!r} has no options")
        radios: list[str] = []
        for option_index, option in enumerate(options):
            if isinstance(option, Mapping):
                option_label = first_value(option, "label", "text", "value")
                option_value = first_value(option, "value", "id") or option_label
            else:
                option_label = option
                option_value = option
            option_id = f"{field_id}-{option_index + 1}"
            radios.append(
                f'<label for="{option_id}"><input id="{option_id}" '
                f'name="{escape(name, quote=True)}" type="radio" '
                f'value="{escape(str(option_value), quote=True)}"{required_attr}/>'
                f"<span>{html_text(option_label)}</span></label>"
            )
        return (
            f'<fieldset class="sf-field sf-field--choices" aria-describedby="{described_by}">'
            f"<legend>{html_text(label)}{marker}</legend>"
            f'<div class="sf-choice-list">{"".join(radios)}</div>'
            f"{helper_html}{error_html}</fieldset>"
        )

    label_html = f'<label for="{field_id}">{html_text(label)}{marker}</label>'
    placeholder_attr = (
        f' placeholder="{escape(str(placeholder), quote=True)}"'
        if placeholder and raw_type != "date"
        else ""
    )
    autocomplete = first_value(field, "autocomplete")
    autocomplete_attr = (
        f' autocomplete="{escape(str(autocomplete), quote=True)}"' if autocomplete else ""
    )
    maxlength = first_value(field, "maxlength", "max_length")
    maxlength_attr = f' maxlength="{int(maxlength)}"' if maxlength else ""

    if raw_type in {"textarea", "long_text", "message"}:
        rows = int(first_value(field, "rows") or 6)
        control = (
            f"<textarea {common} rows=\"{rows}\"{placeholder_attr}"
            f"{maxlength_attr}></textarea>"
        )
    elif raw_type == "select":
        if not options:
            raise RenderError(f"select field {label!r} has no options")
        option_html = ['<option value=""></option>']
        for option in options:
            if isinstance(option, Mapping):
                option_label = first_value(option, "label", "text", "value")
                option_value = first_value(option, "value", "id") or option_label
            else:
                option_label = option
                option_value = option
            option_html.append(
                f'<option value="{escape(str(option_value), quote=True)}">'
                f"{html_text(option_label)}</option>"
            )
        control = f"<select {common}>{''.join(option_html)}</select>"
    else:
        allowed_types = {
            "text",
            "email",
            "tel",
            "date",
            "url",
            "number",
            "search",
        }
        input_type = raw_type if raw_type in allowed_types else "text"
        inputmode = first_value(field, "inputmode", "input_mode")
        inputmode_attr = (
            f' inputmode="{escape(str(inputmode), quote=True)}"' if inputmode else ""
        )
        control = (
            f'<input {common} type="{input_type}"{placeholder_attr}'
            f"{autocomplete_attr}{inputmode_attr}{maxlength_attr}/>"
        )
    return f'<div class="sf-field">{label_html}{control}{helper_html}{error_html}</div>'


def form_endpoint_from_site(site: Mapping[str, Any]) -> tuple[str | None, str | None]:
    forms = first_value(site, "forms", "form")
    if isinstance(forms, Mapping):
        endpoint = first_value(forms, "endpoint", "action", "url")
        method = first_value(forms, "method")
        return (
            normalise_space(endpoint) if endpoint else None,
            normalise_space(method) if method else None,
        )
    endpoint = first_value(site, "form_endpoint", "form_action")
    return (normalise_space(endpoint) if endpoint else None, None)


def render_form(block: Mapping[str, Any], context: RenderContext) -> str:
    fields = listify(first_value(block, "fields", "controls", "inputs"))
    acknowledgements = listify(
        first_value(block, "acknowledgements", "consents", "checkboxes")
    )
    existing_names = {
        key_token(first_value(field, "name", "label", "title"))
        for field in fields
        if isinstance(field, Mapping)
    }
    for acknowledgement in acknowledgements:
        if isinstance(acknowledgement, Mapping):
            acknowledgement_name = key_token(
                first_value(acknowledgement, "name", "label", "title")
            )
            if acknowledgement_name in existing_names:
                continue
            fields.append({"type": "checkbox", **acknowledgement})
            existing_names.add(acknowledgement_name)
        else:
            fields.append(
                {
                    "type": "checkbox",
                    "label": normalise_space(acknowledgement),
                    "text": normalise_space(acknowledgement),
                    "required": True,
                }
            )
    if not fields:
        raise RenderError(f"{context.filename}: form block has no fields")
    if not all(isinstance(field, Mapping) for field in fields):
        raise RenderError(f"{context.filename}: form fields must be objects")

    default_id = {
        "accessibility.html": "accessibility-feedback-form",
        "consultation.html": "consultation-request-form",
        "contact.html": "contact-form",
    }.get(context.filename, f"{context.slug}-form")
    form_id = slugify(first_value(block, "id", "form_id") or default_id)

    inherited = dict(context.form_defaults.attributes) if context.form_defaults else {}
    site_endpoint, site_method = form_endpoint_from_site(context.site)
    inherited_action = inherited.pop("action", None)
    inherited.pop("method", None)
    action = (
        first_value(block, "action", "endpoint")
        or site_endpoint
        or FORM_ENDPOINT
        or inherited_action
    )
    method = first_value(block, "method") or site_method or "post"
    if str(action).startswith("https://formspree.io/"):
        method = "post"
    attributes = [
        f'id="{escape(form_id, quote=True)}"',
        'class="sf-form"',
        f'action="{escape(str(action or ""), quote=True)}"',
        f'method="{escape(str(method).casefold(), quote=True)}"',
        'data-enhanced-form="true"',
    ]
    for name, value in inherited.items():
        if name in {"class", "id", "data-enhanced-form"}:
            continue
        if value:
            attributes.append(f'{name}="{escape(str(value), quote=True)}"')
        else:
            attributes.append(name)

    hidden_html: list[str] = []
    honeypot = first_value(block, "honeypot_name")
    if not honeypot and context.form_defaults:
        honeypot = context.form_defaults.honeypot_name
    if honeypot:
        hidden_html.append(
            '<div class="sf-honeypot" aria-hidden="true">'
            f'<label for="{form_id}-website">Leave this field empty</label>'
            f'<input class="sf-honeypot" id="{form_id}-website" name="{escape(str(honeypot), quote=True)}" '
            'type="text" tabindex="-1" autocomplete="off"/></div>'
        )
    hidden_fields = first_value(block, "hidden_fields", "hidden")
    if isinstance(hidden_fields, Mapping):
        for name, value in hidden_fields.items():
            hidden_html.append(
                f'<input type="hidden" name="{escape(str(name), quote=True)}" '
                f'value="{escape(str(value), quote=True)}"/>'
            )

    field_html = "".join(
        render_field(field, form_id, index)
        for index, field in enumerate(fields, start=1)
    )
    submit = first_value(block, "submit_label", "submit", "button_label", "cta")
    if isinstance(submit, Mapping):
        submit = first_value(submit, "label", "text", "title")
    if not submit:
        raise RenderError(f"{context.filename}: form is missing its document submit label")

    states = first_value(block, "states", "messages", "status", "status_messages")
    states = states if isinstance(states, Mapping) else {}
    if "loading" not in states:
        states = {"loading": "Sending your message…", **states}
    state_html: list[str] = []
    for state, role in (("loading", "status"), ("success", "status"), ("error", "alert")):
        value = states.get(state)
        if isinstance(value, Mapping):
            state_title = first_value(value, "title", "heading", "label")
            state_message = first_value(value, "message", "text", "body")
            pieces = []
            if state_title:
                pieces.append(f"<strong>{html_text(state_title)}</strong>")
            if state_message:
                pieces.append(f"<span>{html_text(state_message)}</span>")
            value_html = "".join(pieces)
        else:
            value_html = html_text(value) if value else ""
        state_html.append(
            f'<div class="sf-form-state sf-form-state--{state}" '
            f'data-form-state="{state}" role="{role}" aria-live="polite" hidden>'
            f"{value_html}</div>"
        )

    return (
        f"<form {' '.join(attributes)}>"
        f"{''.join(hidden_html)}"
        f'<div class="sf-form-grid">{field_html}</div>'
        f'<button class="sf-button sf-button--primary" type="submit">{html_text(submit)}</button>'
        f'<div class="sf-form-states">{"".join(state_html)}</div>'
        "</form>"
    )


def render_cookie_controls(block: Mapping[str, Any]) -> str:
    categories = listify(block.get("categories"))
    rendered: list[str] = []
    for category in categories:
        if not isinstance(category, Mapping):
            raise RenderError("cookie category must be an object")
        name = key_token(category.get("name"))
        label = normalise_space(category.get("label"))
        copy = [normalise_space(value) for value in listify(category.get("copy"))]
        if not name or not label or not copy:
            raise RenderError("cookie category needs a name, label and copy")
        control_id = f"cookie-page-{name}"
        if name == "essential":
            state = copy[0]
            description = " ".join(copy[1:])
            control = (
                f'<input id="{control_id}" type="checkbox" checked disabled '
                'aria-describedby="cookie-page-essential-copy"/>'
            )
        else:
            state = copy[0]
            description = " ".join(copy[1:])
            control = (
                f'<input id="{control_id}" name="{name}" type="checkbox" '
                f'aria-describedby="{control_id}-copy"/>'
            )
        copy_id = (
            "cookie-page-essential-copy" if name == "essential" else f"{control_id}-copy"
        )
        rendered.append(
            '<div class="sf-cookie-choice">'
            f'<label for="{control_id}">{control}<span><strong>{html_text(label)}</strong>'
            f'<small>{html_text(state)}</small></span></label>'
            f'<p id="{copy_id}">{html_text(description)}</p></div>'
        )
    return (
        '<div class="sf-cookie-settings" data-cookie-page-settings>'
        f'<div class="sf-cookie-choice-list">{"".join(rendered)}</div>'
        '<div class="sf-button-row">'
        f'<button class="sf-button sf-button--primary" type="button" data-cookie-page-save>{html_text(block.get("save_label"))}</button>'
        f'<button class="sf-button sf-button--outline" type="button" data-cookie-page-reject>{html_text(block.get("reject_label"))}</button>'
        f'<button class="sf-button sf-button--outline" type="button" data-cookie-page-accept>{html_text(block.get("accept_label"))}</button>'
        "</div>"
        '<p class="sf-cookie-page-status" data-cookie-page-status role="status" aria-live="polite"></p>'
        "</div>"
    )


def render_search(block: Mapping[str, Any]) -> str:
    label = first_value(block, "label", "search_label", "title")
    placeholder = first_value(block, "placeholder", "example")
    button = first_value(block, "button", "submit_label") or "Search"
    topics = listify(first_value(block, "topics", "filters", "options"))
    if not label:
        raise RenderError("search block requires a visible label")
    select_html = ""
    if topics:
        filter_label = first_value(block, "filter_label") or "Filter by topic"
        options = "".join(
            f'<option value="{escape(class_token(option), quote=True)}">{html_text(option)}</option>'
            for option in topics
        )
        select_html = (
            '<div class="sf-field"><label for="article-topic">'
            f"{html_text(filter_label)}</label>"
            f'<select id="article-topic" name="topic">{options}</select></div>'
        )
    no_results = first_value(block, "no_results", "empty_state")
    if isinstance(no_results, Mapping):
        no_results_html = render_item_body(no_results)
    elif no_results:
        no_results_html = f"<p>{html_text(no_results)}</p>"
    else:
        no_results_html = ""
    return (
        '<form class="sf-search-form" data-blog-search role="search" action="blog.html" method="get">'
        f'<div class="sf-field"><label for="article-search">{html_text(label)}</label>'
        f'<input id="article-search" name="q" type="search"'
        f'{f" placeholder={json.dumps(str(placeholder))}" if placeholder else ""}/></div>'
        f"{select_html}"
        f'<button class="sf-button sf-button--primary" type="submit">{html_text(button)}</button>'
        "</form>"
        f'<div class="sf-search-empty" data-search-empty role="status" hidden>{no_results_html}</div>'
    )


def render_image(block: Mapping[str, Any]) -> str:
    src = first_value(block, "src", "path", "url")
    alt = first_value(block, "alt", "alternative_text")
    if not src or alt is None:
        raise RenderError("image block requires src and alt (empty alt is allowed)")
    width = first_value(block, "width")
    height = first_value(block, "height")
    if not width or not height:
        raise RenderError(f"image {src!r} requires explicit width and height")
    loading = first_value(block, "loading") or "lazy"
    caption = first_value(block, "caption")
    caption_html = f"<figcaption>{html_text(caption)}</figcaption>" if caption else ""
    return (
        '<figure class="sf-content-image">'
        f'<img src="{escape(str(src), quote=True)}" alt="{escape(str(alt), quote=True)}" '
        f'width="{int(width)}" height="{int(height)}" loading="{escape(str(loading), quote=True)}" '
        'decoding="async"/>'
        f"{caption_html}</figure>"
    )


def render_meta(block: Mapping[str, Any]) -> str:
    items = listify(first_value(block, "items", "values", "entries"))
    if not items:
        for key in ("author", "reviewed_by", "date", "updated", "reading_time"):
            if block.get(key):
                items.append({"label": key.replace("_", " ").title(), "value": block[key]})
    rendered: list[str] = []
    for item in items:
        if isinstance(item, Mapping):
            label = first_value(item, "label", "name", "type")
            value = first_value(item, "value", "text", "content")
            if label and value:
                rendered.append(f"<dt>{html_text(label)}</dt><dd>{html_text(value)}</dd>")
        elif item:
            rendered.append(f"<dd>{html_text(item)}</dd>")
    return f'<dl class="sf-content-meta">{"".join(rendered)}</dl>'


def render_group(block: Mapping[str, Any], heading_level: int) -> str:
    pieces: list[str] = []
    title = block_title(block)
    if title:
        pieces.append(f"<h{heading_level}>{html_text(title)}</h{heading_level}>")
    body = first_value(block, "body", "text", "paragraphs")
    if body:
        pieces.append(render_paragraphs(body))
    children = first_value(block, "blocks", "content", "items")
    if children:
        pieces.append(render_blocks(listify(children), heading_level + 1))
    return f'<div class="sf-content-group">{"".join(pieces)}</div>'


def render_block(block: Any, heading_level: int, context: RenderContext | None) -> str:
    if isinstance(block, str):
        return f"<p>{html_text(block)}</p>"
    if not isinstance(block, Mapping):
        raise RenderError(f"content block must be a string or object, got {type(block).__name__}")
    kind = block_type(block)
    if kind in {"paragraph", "lead"}:
        values = first_value(block, "paragraphs", "text", "body", "content")
        style = key_token(first_value(block, "style", "source_style"))
        if kind == "lead" or style == "lead":
            css = "sf-lede"
        elif style in {"small", "caption"}:
            css = "sf-small-copy"
        else:
            css = ""
        return render_paragraphs(values, css)
    if kind == "heading":
        value = first_value(block, "text", "title", "heading")
        source_level = first_value(block, "level", "heading_level")
        try:
            level = int(source_level) if source_level is not None else heading_level
        except (TypeError, ValueError):
            level = heading_level
        level = max(heading_level, min(level, 6))
        return f"<h{level}>{html_text(value)}</h{level}>"
    if kind == "list":
        return render_list(first_value(block, "items", "points", "bullets"))
    if kind == "steps":
        return render_steps(block)
    if kind == "cards":
        return render_cards(block, heading_level=heading_level)
    if kind == "quote":
        return render_quote(block, context)
    if kind == "cta":
        return render_cta(block)
    if kind == "comparison":
        return render_comparison(block)
    if kind == "table":
        return render_table(block)
    if kind == "accordion":
        return render_accordion(block)
    if kind == "definition_list":
        return render_definition_list(block)
    if kind == "callout":
        return render_callout(block)
    if kind == "treatment_group":
        return render_treatment_group(block)
    if kind == "treatment_finder":
        return render_treatment_finder(block)
    if kind == "contact_list":
        return render_contact_list(block)
    if kind == "form":
        if context is None:
            raise RenderError("form rendering requires a page context")
        return render_form(block, context)
    if kind == "cookie_controls":
        return render_cookie_controls(block)
    if kind == "search":
        return render_search(block)
    if kind == "image":
        return render_image(block)
    if kind == "meta":
        return render_meta(block)
    if kind == "group":
        return render_group(block, heading_level)
    raise RenderError(f"unsupported block type {kind!r}")


def render_blocks(
    blocks: Sequence[Any],
    heading_level: int = 3,
    context: RenderContext | None = None,
) -> str:
    rendered: list[str] = []
    card_grid = re.compile(
        r'^<div class="sf-content-card-grid" data-card-count="(?P<count>\d+)">'
        r'(?P<cards>.*)</div>$',
        re.DOTALL,
    )
    for block in blocks:
        html = render_block(block, min(heading_level, 6), context)
        current_grid = card_grid.fullmatch(html)
        previous_grid = card_grid.fullmatch(rendered[-1]) if rendered else None
        if current_grid and previous_grid:
            rendered[-1] = (
                '<div class="sf-content-card-grid" data-card-count="'
                f'{int(previous_grid.group("count")) + int(current_grid.group("count"))}">'
                f'{previous_grid.group("cards")}{current_grid.group("cards")}'
                '</div>'
            )
        else:
            rendered.append(html)
    return "\n".join(rendered)


def section_inner(
    pattern: str, head_html: str, body_html: str, *, contained: bool = True
) -> str:
    rail = " sf-canvas" if contained else ""
    if pattern == "hero":
        return f'<div class="sf-hero-copy">{head_html}{body_html}</div>'
    if pattern in {"editorial_split", "comparison"}:
        return (
            f'<div class="sf-editorial-split{rail}">'
            f'<header class="sf-editorial-kicker">{head_html}</header>'
            f'<div class="sf-editorial-copy">{body_html}</div></div>'
        )
    if pattern == "reading_column":
        return (
            f'<div class="sf-reading-column{rail}">'
            f'<header class="sf-section-head">{head_html}</header>{body_html}</div>'
        )
    if pattern == "form":
        return (
            f'<div class="sf-form-section-layout{rail}">'
            f'<header class="sf-form-section-intro">{head_html}</header>'
            f'<div class="sf-form-section-body">{body_html}</div></div>'
        )
    if pattern in {"quote_panel", "oversized_statement", "pull_quote"}:
        return (
            f'<div class="sf-statement-inner{rail}">'
            f'<header class="sf-section-head">{head_html}</header>{body_html}</div>'
        )
    if pattern == "final_cta":
        return (
            f'<div class="sf-bottom-cta__inner{rail}">'
            f'<header class="sf-section-head">{head_html}</header>{body_html}</div>'
        )
    if pattern.startswith("treatment_"):
        return (
            f'<div class="sf-treatment-scene{rail}">'
            f'<header class="sf-section-head">{head_html}</header>{body_html}</div>'
        )
    return f'<div class="sf-section-inner{rail}"><header class="sf-section-head">{head_html}</header>{body_html}</div>'


def render_final_cta_concept(filename: str) -> str:
    concept = FINAL_CTA_CONCEPTS[filename]
    title, copy, primary, secondary = FINAL_CTA_COPY[filename]
    return (
        '<div class="sf-bottom-cta__inner sf-canvas" '
        f'data-cta-concept="{concept}">'
        '<div class="sf-final-cta-lockup">'
        '<img src="assets/brand/sofiati-logo-gold-transparent.webp" alt="" '
        'width="58" height="58" loading="lazy" decoding="async">'
        '<span>Franciele Sofiati · Biomedical Aesthetics</span></div>'
        '<header class="sf-section-head">'
        f'<p class="sf-eyebrow">When you are ready</p><h2>{escape(title)}</h2></header>'
        f'<p class="sf-final-cta-copy">{escape(copy)}</p>'
        '<div class="sf-button-row">'
        f'<a class="sf-button sf-button--primary" href="consultation.html">{escape(primary)}</a>'
        f'<a class="sf-button sf-button--outline" href="treatments.html">{escape(secondary)}</a>'
        '</div></div>'
    )


def render_editorial_media(filename: str, order: int) -> str:
    """Return a meaningful supporting image for selected editorial chapters."""
    selected = EDITORIAL_MEDIA_MAP.get((filename, order))
    if not selected:
        return ""
    source, alt, width, height = selected
    return (
        '<figure class="sf-editorial-media">'
        f'<img src="{escape(source, quote=True)}" alt="{escape(alt, quote=True)}" '
        f'width="{width}" height="{height}" loading="lazy" decoding="async"/>'
        '</figure>'
    )


def render_hero_image(filename: str) -> str:
    source, alt, width, height = HERO_IMAGES[filename]
    stem = Path(source).stem
    responsive_root = "assets/hero/responsive"
    responsive_640 = f"{responsive_root}/{stem}-640.webp"
    responsive_960 = f"{responsive_root}/{stem}-960.webp"
    srcset = ""
    if (ROOT / responsive_640).exists() and (ROOT / responsive_960).exists():
        srcset = (
            f' srcset="{responsive_640} 640w, '
            f'{responsive_960} 960w, {escape(source, quote=True)} {width}w"'
        )
    return (
        '<figure class="sf-hero-figure">'
        '<span class="sf-hero-botanical" aria-hidden="true"></span>'
        f'<img src="{escape(source, quote=True)}" alt="{escape(alt, quote=True)}" '
        f'{srcset} '
        'sizes="(max-width: 700px) 92vw, (max-width: 1200px) 44vw, 560px" '
        f'width="{width}" height="{height}" loading="eager" fetchpriority="high" '
        'decoding="async"/>'
        "</figure>"
    )


def render_section(
    section: Mapping[str, Any], order: int, total_sections: int, context: RenderContext
) -> tuple[str, str]:
    label = section_label(section, order)
    heading = section_heading(section)
    source_blocks = section_blocks(section)
    if order == 1:
        source_blocks = [
            {**block, "level": max(2, int(block.get("level", 3)) - 1)}
            if isinstance(block, Mapping)
            and block_type(block) == "heading"
            and str(block.get("level", "3")).isdigit()
            else block
            for block in source_blocks
        ]
    blocks = semantic_section_blocks(source_blocks, context.filename, order)
    pattern = infer_pattern(section, blocks, context.filename, order)
    if pattern not in PATTERN_CLASSES:
        raise RenderError(
            f"{context.filename}: section {order} uses unsupported pattern {pattern!r}"
        )
    heading_id = slugify(
        first_value(section, "heading_id", "id")
        or f"{context.slug}-{order:02d}-{heading}"
    )
    default_section_id = slugify(label)
    if context.filename == "cookies.html" and order == 8:
        default_section_id = "cookie-settings"
    elif pattern == "form":
        default_section_id = f"{default_section_id}-section"
    section_id = slugify(first_value(section, "section_id") or default_section_id)
    tag = "h1" if order == 1 else "h2"
    eyebrow_text = HERO_EYEBROWS[context.filename] if pattern == "hero" else label
    eyebrow = f'<p class="sf-eyebrow">{html_text(eyebrow_text)}</p>'
    chapter = ""
    if order > 1 and pattern not in {"hero", "final_cta"}:
        chapter = (
            '<span class="sf-chapter-number" aria-hidden="true">'
            f'{order - 1:02d}</span>'
        )
    if pattern == "hero":
        eyebrow = (
            f"{eyebrow}"
            f'<span class="sf-visually-hidden">{html_text(label)}</span>'
            f"{render_hero_brand()}"
        )
    head = f'{chapter}{eyebrow}<{tag} id="{heading_id}">{html_text(heading)}</{tag}>'
    if context.filename == "contact.html" and pattern == "form":
        head += render_contact_form_guide()
    body = render_blocks(
        blocks,
        heading_level=2 if order == 1 else 3,
        context=context,
    )
    if context.filename == "treatments.html" and pattern.startswith("treatment_") and pattern != "treatment_finder":
        body += (
            '<a class="sf-treatment-back" href="#treatment-index">'
            'Back to treatment index <span aria-hidden="true">↑</span></a>'
        )
    media = render_editorial_media(context.filename, order)
    compact_disclosure = (
        context.filename == "contact.html" and 3 <= order <= 4
    ) or (
        context.filename == "contact.html" and 6 <= order <= 9
    ) or (
        context.filename == "consultation.html" and 5 <= order <= 6
    ) or (
        context.filename == "thank-you.html" and 4 <= order <= 9
    )
    if compact_disclosure:
        disclosure_rail = "" if media else " sf-canvas"
        inner = (
            f'<div class="sf-section-inner{disclosure_rail}">'
            '<details class="sf-section-disclosure">'
            f'<summary>{head}<span class="sf-section-disclosure__toggle" aria-hidden="true"></span></summary>'
            f'<div class="sf-section-disclosure__body">{body}</div>'
            '</details></div>'
        )
    else:
        inner = section_inner(pattern, head, body, contained=not bool(media))
    if pattern == "final_cta":
        inner = render_final_cta_concept(context.filename)
    if pattern == "hero":
        inner = (
            '<div class="sf-hero-layout sf-canvas">'
            f"{inner}</div>"
        )
    else:
        if media:
            inner = f'<div class="sf-editorial-media-layout sf-canvas">{inner}{media}</div>'
    journey = PAGE_TONE_JOURNEYS.get(context.filename)
    if not journey or order > len(journey):
        raise RenderError(f"{context.filename}: incomplete art-direction tone journey")
    full_bleed = order in full_bleed_section_orders(
        context.filename, total_sections
    )
    tone = class_token(first_value(section, "tone") or journey[order - 1])
    if full_bleed:
        tone = "forest"
    elif tone == "forest":
        tone = "sage"
    scale_journey = PAGE_SCALE_JOURNEYS.get(context.filename)
    if not scale_journey or order > len(scale_journey):
        raise RenderError(f"{context.filename}: incomplete section-scale journey")
    scale = class_token(
        first_value(section, "scale", "section_scale") or scale_journey[order - 1]
    )
    scene_journey = PAGE_SCENE_JOURNEYS.get(context.filename)
    if not scene_journey or order > len(scene_journey):
        raise RenderError(f"{context.filename}: incomplete scene journey")
    scene = class_token(first_value(section, "scene") or scene_journey[order - 1])
    if full_bleed:
        scene = "final" if pattern == "final_cta" else "olive-garden"
    elif scene == "olive-garden":
        scene = "porcelain"
    classes = " ".join(
        (
            "sf-section",
            *PATTERN_CLASSES[pattern],
            *(('section--full-bleed',) if full_bleed else ()),
        )
    )
    comment_label = re.sub(r"\s+", " ", label).strip().upper()
    comment = (
        "<!-- ==================================================\n"
        f"     SECTION {order:02d}: {comment_label}\n"
        "=================================================== -->"
    )
    chapter_attribute = f' data-chapter="{order - 1:02d}"' if chapter else ""
    filterable_attribute = (
        ' data-treatment-filterable'
        if context.filename == "treatments.html" and pattern.startswith("treatment_") and pattern != "treatment_finder"
        else ""
    )
    html = (
        f"{comment}\n"
        f'<section class="{classes}" id="{section_id}" data-section="{order}" '
        f'data-pattern="{pattern.replace("_", "-")}" data-tone="{tone}" '
        f'data-scale="{scale}" data-scene="{scene}"'
        f'{chapter_attribute}{filterable_attribute} '
        f'aria-labelledby="{heading_id}">'
        f"{inner}</section>"
    )
    return html, pattern


def render_main(
    page: Mapping[str, Any],
    filename: str,
    site: Mapping[str, Any],
    form_defaults: FormDefaults | None,
) -> tuple[str, tuple[str, ...]]:
    context = RenderContext(filename, page, site, form_defaults)
    sections = section_entries(page, filename)
    rendered_sections: list[str] = []
    toc_items: list[str] = []
    treatment_nav_items: list[str] = []
    patterns: list[str] = []
    for index, section in enumerate(sections, start=1):
        # Every page ends with one of the approved art-led CTA concepts.
        # Keep the authored copy and links, but standardise the final section's
        # component shell so it has a reliable final-page position.
        if index == len(sections) and filename != "contact.html":
            section = {**section, "pattern": "final_cta"}
        html, pattern = render_section(section, index, len(sections), context)
        rendered_sections.append(html)
        patterns.append(pattern)
        if index > 1:
            section_match = re.search(r'<section[^>]+id="([^"]+)"', html)
            if section_match:
                section_id = section_match.group(1)
                toc_items.append(
                    '<li>'
                    f'<a href="#{escape(section_id, quote=True)}">'
                    f'<span aria-hidden="true">{index - 1:02d}</span>'
                    f'{html_text(section_heading(section))}</a></li>'
                )
                if filename == "treatments.html" and 3 <= index <= 10:
                    nav_label = first_value(section, "nav_label") or section_label(section, index)
                    current = ' aria-current="location"' if index == 3 else ""
                    treatment_nav_items.append(
                        f'<a href="#{escape(section_id, quote=True)}" data-treatment-category-link{current}>'
                        f'<span aria-hidden="true">{index - 1:02d}</span>'
                        f'{html_text(nav_label)}</a>'
                    )
    rendered: list[str] = [render_breadcrumbs(page, filename)]
    toc_html = ""
    treatment_nav_html = ""
    if treatment_nav_items:
        treatment_nav_html = (
            '<nav class="sf-treatment-index" id="treatment-index" '
            'aria-label="Treatment categories" data-treatment-category-nav>'
            '<div class="sf-treatment-index__inner sf-canvas">'
            '<span class="sf-treatment-index__label">Explore by category</span>'
            f'<div class="sf-treatment-index__links">{"".join(treatment_nav_items)}</div>'
            '</div></nav>'
        )
    faq_search_html = ""
    if filename == "faq.html":
        faq_search_html = (
            '<div class="sf-faq-search sf-container" role="search">'
            '<label for="faq-search">Search questions</label>'
            '<input id="faq-search" type="search" data-faq-search '
            'placeholder="Type a topic or treatment" autocomplete="off"/>'
            '</div>'
        )
    if filename == "treatments.html" and rendered_sections:
        rendered.append(rendered_sections[0])
        if len(rendered_sections) > 1:
            rendered.append(rendered_sections[1])
        if treatment_nav_html:
            rendered.append(treatment_nav_html)
        rendered.extend(rendered_sections[2:])
    elif filename in {"index.html", "about.html"} and rendered_sections:
        rendered.append(rendered_sections[0])
        rendered.append(
            '<aside class="sf-credentials-line" aria-label="Professional details">'
            '<div class="sf-credentials-line__inner sf-container">'
            '<span>Franciele Sofiati</span>'
            '<span>Biomedical Practitioner · Aesthetician · Cosmetologist</span>'
            '<span>CRBM 6277</span>'
            '<span>Londrina · Paraná</span>'
            '</div></aside>'
        )
        rendered.extend(rendered_sections[1:])
    else:
        if rendered_sections:
            rendered.append(rendered_sections[0])
        if toc_html:
            rendered.append(toc_html)
        if faq_search_html:
            rendered.append(faq_search_html)
        rendered.extend(rendered_sections[1:])
    return "\n".join(rendered), tuple(patterns)


def merge_main(skeleton: PageSkeleton, main_html: str) -> str:
    return f"{skeleton.prefix}\n{format_main_html(main_html)}\n{skeleton.suffix}"


MAIN_BLOCK_TAGS = (
    "main",
    "nav",
    "ol",
    "ul",
    "li",
    "section",
    "article",
    "aside",
    "div",
    "figure",
    "form",
    "fieldset",
    "details",
    "summary",
    "blockquote",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "p",
)
MAIN_BLOCK_RE = re.compile(
    rf"\s*(</?(?:{'|'.join(MAIN_BLOCK_TAGS)})\b[^>]*>)\s*", re.I
)


def format_main_html(html: str) -> str:
    """Format structural boundaries without rewriting tags or visible copy."""

    separated = MAIN_BLOCK_RE.sub(r"\n\1\n", html)
    lines = [line.strip() for line in separated.splitlines() if line.strip()]
    output: list[str] = []
    depth = 1
    block_names = "|".join(MAIN_BLOCK_TAGS)
    closing = re.compile(rf"^</(?:{block_names})\b", re.I)
    opening = re.compile(rf"^<(?:{block_names})\b[^>]*>$", re.I)
    for line in lines:
        if line.startswith("SECTION "):
            output.append(f"     {line}")
            continue
        if closing.match(line):
            depth = max(1, depth - 1)
        output.append(f"{'  ' * depth}{line}")
        if opening.match(line) and not line.startswith("</"):
            depth += 1
    return "\n".join(output)


def form_blocks_in(page: Mapping[str, Any], filename: str) -> list[Mapping[str, Any]]:
    found: list[Mapping[str, Any]] = []

    def visit(value: Any) -> None:
        if isinstance(value, Mapping):
            try:
                kind = block_type(value)
            except RenderError:
                kind = ""
            if kind == "form":
                found.append(value)
                return
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    for section in section_entries(page, filename):
        for block in section_blocks(section):
            visit(block)
    return found


def validate_form_copy(filename: str, form: Mapping[str, Any]) -> list[str]:
    signature = FORM_SIGNATURES[filename]
    fields = listify(first_value(form, "fields", "controls", "inputs"))
    known_names = {
        key_token(first_value(field, "name", "label", "title"))
        for field in fields
        if isinstance(field, Mapping)
    }
    for acknowledgement in listify(
        first_value(form, "acknowledgements", "consents", "checkboxes")
    ):
        if not isinstance(acknowledgement, Mapping):
            fields.append(acknowledgement)
            continue
        name = key_token(first_value(acknowledgement, "name", "label", "title"))
        if name not in known_names:
            fields.append(acknowledgement)
            known_names.add(name)
    actual: dict[str, Mapping[str, Any]] = {}
    for field in fields:
        if isinstance(field, Mapping):
            label = first_value(field, "label", "title", "name")
            if label:
                actual[normalise_label(label)] = field

    errors: list[str] = []
    expected_labels = [normalise_label(label) for label, _, _ in signature["fields"]]
    if list(actual) != expected_labels:
        errors.append(
            f"{filename}: form labels/order differ from the document; "
            f"expected {[item[0] for item in signature['fields']]}, "
            f"found {[normalise_space(first_value(field, 'label', 'title', 'name')) for field in fields if isinstance(field, Mapping)]}"
        )
        return errors

    for label, required, snippets in signature["fields"]:
        field = actual[normalise_label(label)]
        raw_label = normalise_space(first_value(field, "label", "title", "name"))
        actual_required = bool(field.get("required")) or raw_label.endswith("*")
        if actual_required != required:
            errors.append(
                f"{filename}: field {label!r} required={actual_required}; expected {required}"
            )
        field_strings = set(strings_in(field))
        for snippet in snippets:
            if normalise_space(snippet) not in field_strings:
                errors.append(
                    f"{filename}: field {label!r} is missing exact document copy {snippet!r}"
                )

    form_strings = set(strings_in(form))
    for message in signature["messages"]:
        if normalise_space(message) not in form_strings:
            errors.append(
                f"{filename}: form is missing exact document status text {message!r}"
            )
    return errors


def validate_content(
    payload: Mapping[str, Any], pages: Mapping[str, Mapping[str, Any]]
) -> list[str]:
    errors: list[str] = []
    missing = sorted(set(ENGLISH_PAGES) - set(pages))
    extra = sorted(set(pages) - set(ENGLISH_PAGES))
    if missing:
        errors.append(f"content master is missing pages: {', '.join(missing)}")
    if extra:
        errors.append(f"content master has unexpected English pages: {', '.join(extra)}")

    for filename in ENGLISH_PAGES:
        page = pages.get(filename)
        if page is None:
            continue
        try:
            total_sections = len(section_entries(page, filename))
        except RenderError:
            total_sections = 0
        full_bleed_orders = full_bleed_section_orders(filename, total_sections)
        if filename not in FULL_BLEED_EXEMPT_PAGES:
            if len(full_bleed_orders) != FULL_BLEED_BANDS_PER_PAGE:
                errors.append(
                    f"{filename}: expected exactly {FULL_BLEED_BANDS_PER_PAGE} "
                    f"full-bleed bands, found {sorted(full_bleed_orders)}"
                )
            elif total_sections not in full_bleed_orders:
                errors.append(
                    f"{filename}: the final CTA must be a full-bleed band"
                )
        try:
            sections = section_entries(page, filename)
        except RenderError as error:
            errors.append(str(error))
            continue
        if not sections:
            errors.append(f"{filename}: expected at least one section")
        orders: list[int] = []
        for index, section in enumerate(sections, start=1):
            try:
                orders.append(section_order(section, index))
                section_heading(section)
                section_blocks(section)
            except RenderError as error:
                errors.append(f"{filename}: section {index}: {error}")
        expected_orders = list(range(1, len(sections) + 1))
        if orders != expected_orders:
            errors.append(f"{filename}: section order must be {expected_orders}, found {orders}")

        seo = first_value(page, "seo", "metadata")
        if isinstance(seo, Mapping):
            seo_strings = {
                key_token(key): value for key, value in seo.items() if value not in (None, "")
            }
        else:
            seo_strings = {
                "title": first_value(page, "seo_title", "title"),
                "meta_description": first_value(page, "meta_description", "description"),
                "search_themes": first_value(page, "search_themes", "keywords"),
            }
        if not any(key in seo_strings for key in ("title", "seo_title")):
            errors.append(f"{filename}: missing SEO title in structured content")
        if not any(
            key in seo_strings
            for key in ("description", "meta_description", "meta_description_text")
        ):
            errors.append(f"{filename}: missing meta description in structured content")

        forms = form_blocks_in(page, filename)
        if filename in SPECIAL_FORM_PAGES:
            if len(forms) != 1:
                errors.append(
                    f"{filename}: expected exactly one document-defined form, found {len(forms)}"
                )
            else:
                errors.extend(validate_form_copy(filename, forms[0]))
        elif forms:
            errors.append(f"{filename}: unexpected form block outside the three form pages")
    return errors


class GeneratedHTMLAudit(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.main_count = 0
        self.h1_count = 0
        self.section_orders: list[int] = []
        self.breadcrumbs = 0
        self.ids: list[str] = []
        self.controls: list[tuple[str, str]] = []
        self.label_fors: set[str] = set()
        self.form_count = 0

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.casefold()
        attr_map = {name.casefold(): value or "" for name, value in attrs}
        if attr_map.get("id"):
            self.ids.append(attr_map["id"])
        if tag == "main":
            self.main_count += 1
            self.in_main = True
        if tag == "h1":
            self.h1_count += 1
        if self.in_main and tag == "section" and attr_map.get("data-section"):
            try:
                self.section_orders.append(int(attr_map["data-section"]))
            except ValueError:
                self.section_orders.append(-1)
        if self.in_main and tag == "nav" and attr_map.get("aria-label", "").casefold() == "breadcrumb":
            self.breadcrumbs += 1
        if self.in_main and tag == "form":
            self.form_count += 1
        if self.in_main and tag == "label" and attr_map.get("for"):
            self.label_fors.add(attr_map["for"])
        if self.in_main and tag in {"input", "select", "textarea"}:
            control_type = attr_map.get("type", "text").casefold()
            if control_type not in {"hidden", "button", "submit", "reset"}:
                self.controls.append((attr_map.get("id", ""), control_type))

    def handle_endtag(self, tag: str) -> None:
        if tag.casefold() == "main":
            self.in_main = False


def validate_generated(
    filename: str,
    generated: str,
    skeleton: PageSkeleton,
    expected_form: bool,
    expected_section_count: int,
    patterns: Sequence[str],
) -> list[str]:
    errors: list[str] = []
    audit = GeneratedHTMLAudit()
    audit.feed(generated)
    if audit.main_count != 1:
        errors.append(f"{filename}: generated document has {audit.main_count} main elements")
    if audit.h1_count != 1:
        errors.append(f"{filename}: generated document has {audit.h1_count} H1 elements")
    expected_orders = list(range(1, expected_section_count + 1))
    if audit.section_orders != expected_orders:
        errors.append(
            f"{filename}: generated section data order is {audit.section_orders}, expected {expected_orders}"
        )
    if audit.breadcrumbs != 1:
        errors.append(f"{filename}: expected one breadcrumb navigation")
    duplicates = sorted({item for item in audit.ids if audit.ids.count(item) > 1})
    if duplicates:
        errors.append(f"{filename}: duplicate IDs: {', '.join(duplicates)}")
    unlabeled = sorted(
        control_id
        for control_id, _ in audit.controls
        if not control_id or control_id not in audit.label_fors
    )
    if unlabeled:
        errors.append(f"{filename}: form controls without associated labels: {unlabeled}")
    if expected_form and audit.form_count < 1:
        errors.append(f"{filename}: expected a rendered form")
    if not expected_form and audit.form_count:
        # Blog search is an intentional exception and remains semantic.
        if filename != "blog.html":
            errors.append(f"{filename}: unexpected rendered form")
    minimum_patterns = 1 if filename == "contact.html" else (2 if filename == "faq.html" else 4)
    if len(set(patterns)) < minimum_patterns:
        errors.append(
            f"{filename}: section presentation is insufficiently varied ({patterns})"
        )
    for partial in skeleton.partials:
        if partial not in generated:
            errors.append(f"{filename}: shared partial mount changed or disappeared: {partial}")
    if generated[: len(skeleton.prefix)] != skeleton.prefix:
        errors.append(f"{filename}: content before <main> was not preserved byte-for-byte")
    if not generated.endswith(skeleton.suffix):
        errors.append(f"{filename}: content from </main> onward was not preserved byte-for-byte")
    return errors


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
        temporary.replace(path)
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise


def choose_pages(values: Sequence[str] | None) -> tuple[str, ...]:
    if not values:
        return tuple(page for page in ENGLISH_PAGES if page not in EXTERNAL_RENDERED_PAGES)
    selected: list[str] = []
    for value in values:
        filename = canonical_filename(value)
        if filename not in ENGLISH_PAGES:
            raise RenderError(f"unknown English page {value!r}")
        if filename in EXTERNAL_RENDERED_PAGES:
            raise RenderError(
                f"{filename} is rendered by scripts/build-journal.py from its authoritative article document"
            )
        if filename not in selected:
            selected.append(filename)
    return tuple(selected)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--content",
        type=Path,
        default=DEFAULT_CONTENT,
        help="Structured content JSON (default: data/content-master.json).",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="Repository root containing the existing English HTML skeletons.",
    )
    parser.add_argument(
        "--page",
        action="append",
        help="Render one page (repeatable). All 21 are selected by default.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--write",
        action="store_true",
        help="Explicitly write generated pages. Without this flag nothing is changed.",
    )
    mode.add_argument(
        "--dry-run",
        action="store_true",
        help="Render and validate in memory without writing (the default).",
    )
    mode.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate JSON and existing page skeletons without rendering HTML.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="With --write, write preview pages here instead of replacing root pages.",
    )
    parser.add_argument(
        "--report-json",
        action="store_true",
        help="Print the dry-run/write report as JSON.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.resolve()
    content_path = args.content.resolve()
    if args.output_dir and not args.write:
        raise RenderError("--output-dir requires the explicit --write flag")
    if not content_path.is_file():
        raise RenderError(f"content master not found: {content_path}")
    try:
        payload = json.loads(content_path.read_text(encoding="utf-8-sig"))
    except json.JSONDecodeError as error:
        raise RenderError(f"invalid JSON in {content_path}: {error}") from error
    if not isinstance(payload, Mapping):
        raise RenderError("content master root must be a JSON object")

    pages = page_entries(payload)
    content_errors = validate_content(payload, pages)
    site = site_entry(payload)
    skeletons: dict[str, PageSkeleton] = {}
    for filename in ENGLISH_PAGES:
        try:
            skeletons[filename] = read_skeleton(root, filename, pages.get(filename))
        except RenderError as error:
            content_errors.append(str(error))
    if content_errors:
        raise RenderError("validation failed:\n- " + "\n- ".join(content_errors))
    if args.validate_only:
        print(f"Validated structured content and skeletons for {len(ENGLISH_PAGES)} pages; no files written.")
        return 0

    selected = choose_pages(args.page)
    common_defaults = common_form_defaults(skeletons)
    report: list[dict[str, Any]] = []
    output_root = args.output_dir.resolve() if args.output_dir else root
    generated_errors: list[str] = []
    generated_pages: dict[str, str] = {}

    for filename in selected:
        skeleton = skeletons[filename]
        defaults = skeleton.form_defaults or common_defaults
        try:
            main_html, patterns = render_main(pages[filename], filename, site, defaults)
            generated = merge_main(skeleton, main_html)
            errors = validate_generated(
                filename,
                generated,
                skeleton,
                filename in SPECIAL_FORM_PAGES,
                len(section_entries(pages[filename], filename)),
                patterns,
            )
        except RenderError as error:
            generated_errors.append(f"{filename}: {error}")
            continue
        if errors:
            generated_errors.extend(errors)
            continue
        generated_pages[filename] = generated
        digest = hashlib.sha256(generated.encode("utf-8")).hexdigest()[:12]
        report.append(
            {
                "page": filename,
                "mode": "write" if args.write else "dry-run",
                "destination": str(output_root / filename),
                "characters": len(generated),
                "sha256": digest,
                "patterns": list(patterns),
            }
        )

    if generated_errors:
        raise RenderError("generated HTML validation failed:\n- " + "\n- ".join(generated_errors))

    if args.write:
        for filename, generated in generated_pages.items():
            atomic_write(output_root / filename, generated)

    if args.report_json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        action = "WROTE" if args.write else "DRY-RUN"
        for item in report:
            print(
                f"{action:7} {item['page']:<20} {item['characters']:>7} chars "
                f"sha256:{item['sha256']}"
            )
        if not args.write:
            print(f"Validated {len(report)} rendered pages in memory; no files written.")
        elif args.output_dir:
            print(f"Wrote {len(report)} preview pages under {output_root}.")
        else:
            print(f"Wrote {len(report)} English pages under {root}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RenderError as error:
        print(f"error: {error}", file=sys.stderr)
        raise SystemExit(2)
