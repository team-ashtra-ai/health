#!/usr/bin/env python3
"""Build Franciele Sofiati's English Journal from the authoritative Word source.

The document in ``posts/Franciele_Sofiati_Journal_10_Articles_Final.docx`` is
the content authority. This builder extracts its ten articles, prepares the
post imagery, and renders the art-directed Journal index plus one complete
long-form page per article.

Examples:

    python3 scripts/build-journal.py --write --assets
    python3 scripts/build-journal.py --check

Only the image optimisation step relies on ImageMagick. Parsing and rendering
use Python's standard library so the publication remains easy to reproduce.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from html import escape
from pathlib import Path
from typing import Iterable, Sequence
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
DOCX = ROOT / "posts" / "Franciele_Sofiati_Journal_10_Articles_Final.docx"
ARTICLE_DIR = ROOT / "journal"
ASSET_DIR = ROOT / "assets" / "posts" / "journal"
SITE_ORIGIN = "https://www.francielesofiati.com"
SITE_NAME = "Franciele Sofiati Biomédica"
SITE_EMAIL = "suportesofiati@gmail.com"
SITE_TELEPHONE = "+5543991043536"
SITE_INSTAGRAM = "https://www.instagram.com/sofiati_biomedica/"
LOGO_IMAGE = f"{SITE_ORIGIN}/assets/brand/sofiati-logo-primary.png"
SOCIAL_IMAGE = f"{SITE_ORIGIN}/assets/social/sofiati-og-image.png"

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
A = "{http://schemas.openxmlformats.org/drawingml/2006/main}"
R = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"
REL = "{http://schemas.openxmlformats.org/package/2006/relationships}"


@dataclass(frozen=True)
class ArticleConfig:
    number: int
    slug: str
    expected_title: str
    category: str
    category_slug: str
    excerpt: str
    meta_description: str
    feature_filename: str
    feature_alt: str
    portrait_source: str
    portrait_filename: str
    portrait_alt: str
    author_portrait_source: str
    author_portrait_filename: str
    author_portrait_alt: str
    layout: str
    related: tuple[int, int, int]
    contextual_links: tuple[tuple[str, str], ...]


ARTICLE_CONFIGS: tuple[ArticleConfig, ...] = (
    ArticleConfig(
        1,
        "why-aesthetic-care-begins-with-consultation",
        "Before the Treatment: Why Thoughtful Aesthetic Care Begins with a Consultation",
        "Consultation & Care",
        "consultation-care",
        "A good plan begins before a device is chosen: with history, priorities, suitability, realistic expectations and the confidence to wait when necessary.",
        "Franciele Sofiati explains why aesthetic treatment planning begins with consultation, individual assessment, realistic expectations and safe timing.",
        "aesthetic-consultation-treatment-planning.webp",
        "A clinician speaking with a patient during a skin consultation.",
        "postsportraits1.png",
        "franciele-sofiati-white-coat-editorial-portrait.webp",
        "Franciele Sofiati wearing a white clinical coat.",
        "postsportraits2.png",
        "franciele-sofiati-smiling-white-coat-portrait.webp",
        "Franciele Sofiati smiling in a white clinical coat.",
        "split",
        (3, 7, 10),
        (
            ("before-and-after photographs", "../results.html#what-a-photograph-cannot-show"),
            ("consultation", "../consultation.html#consultation-introduction"),
            ("aftercare", "../care.html#aftercare-foundations"),
        ),
    ),
    ArticleConfig(
        2,
        "professional-skin-cleansing-guide",
        "A Clearer Starting Point: What Professional Skin Cleansing Can — and Cannot — Do",
        "Consultation & Care",
        "consultation-care",
        "What careful professional cleansing can clarify, which congestion can be treated safely, and why more pressure never means better care.",
        "A responsible guide to professional skin cleansing, selective extraction, congestion, acne limits, sensitivity and aftercare by Franciele Sofiati.",
        "professional-skin-care-appointment.webp",
        "A clinician concentrating during a professional skin-care appointment.",
        "postsportraits13.png",
        "franciele-sofiati-pale-blue-suit-portrait.webp",
        "Franciele Sofiati wearing a pale blue suit with her arms folded.",
        "postsportraits14.png",
        "franciele-sofiati-blue-suit-editorial-portrait.webp",
        "Franciele Sofiati standing in a blue suit.",
        "title-led",
        (3, 6, 1),
        (
            ("Professional cleansing", "../treatments.html#facial-cleansing"),
            ("acne", "../skin.html#acne-without-punishment"),
            ("aftercare", "../care.html#aftercare-foundations"),
        ),
    ),
    ArticleConfig(
        3,
        "rebuilding-an-overwhelmed-skin-barrier",
        "When More Is Not Better: Rebuilding a Skin Barrier Overwhelmed by Skincare",
        "Consultation & Care",
        "consultation-care",
        "How to recognise an overwhelmed skin barrier, simplify an overactive routine and restore tolerance before adding actives or procedures.",
        "Learn how to recognise an overwhelmed skin barrier, simplify skincare, restore tolerance and prepare skin responsibly before procedures.",
        "skin-barrier-moisturiser-care.webp",
        "An open jar of moisturising cream representing skin-barrier care.",
        "postsportraits9.png",
        "franciele-sofiati-sage-suit-editorial-portrait.webp",
        "Franciele Sofiati wearing a soft sage suit with her arms folded.",
        "postsportraits12.png",
        "franciele-sofiati-lilac-suit-standing-portrait.webp",
        "Franciele Sofiati standing in a lilac suit.",
        "portrait-led",
        (2, 7, 4),
        (
            ("skin barrier", "../skin.html#the-skin-barrier"),
            ("laser treatment", "../laser.html#when-to-wait"),
            ("sun protection", "../care.html#before-treatment"),
        ),
    ),
    ArticleConfig(
        4,
        "understanding-facial-pigmentation",
        "Uneven Tone Is Not One Condition: A More Careful Conversation About Pigmentation",
        "Skin Health",
        "skin-health",
        "Pigmentation has patterns, triggers and memory. Understand why colour must be assessed before choosing how—or whether—to treat it.",
        "A careful guide to facial pigmentation, melasma, sun exposure, inflammation, assessment and realistic long-term treatment planning.",
        "facial-pigmentation-and-freckles.webp",
        "Close-up of natural facial pigmentation and freckles.",
        "postsportraits5.png",
        "franciele-sofiati-deep-rose-suit-portrait.webp",
        "Franciele Sofiati wearing a deep rose suit with her arms folded.",
        "postsportraits6.png",
        "franciele-sofiati-blush-suit-editorial-portrait.webp",
        "Franciele Sofiati wearing a muted blush suit with her arms folded.",
        "panorama",
        (5, 3, 6),
        (
            ("pigmentation", "../skin.html#pigment-sun-and-memory"),
            ("sun protection", "../care.html#before-treatment"),
            ("consultation", "../consultation.html#consultation-introduction"),
        ),
    ),
    ArticleConfig(
        5,
        "persistent-facial-redness-and-vessels",
        "Beyond ‘Sensitive Skin’: Understanding Persistent Redness and Visible Facial Vessels",
        "Laser & Technology",
        "laser-technology",
        "Persistent redness is not one diagnosis. A careful guide to vessels, inflammation, laser and light, and when medical assessment comes first.",
        "Understand persistent facial redness, visible vessels, reactive skin, laser and light treatment limits, safety and medical referral signs.",
        "calming-care-for-reactive-skin.webp",
        "A soft facial mask being applied with a brush during calming skin care.",
        "postsportraits17.png",
        "franciele-sofiati-red-suit-editorial-portrait.webp",
        "Franciele Sofiati standing in a red suit.",
        "postsportraits18.png",
        "franciele-sofiati-red-suit-folded-arms-portrait.webp",
        "Franciele Sofiati wearing a red suit with her arms folded.",
        "split",
        (4, 7, 1),
        (
            ("laser and light", "../laser.html#when-laser-may-be-used"),
            ("redness", "../skin.html#your-skin-concern-atlas"),
            ("consultation", "../consultation.html#consultation-introduction"),
        ),
    ),
    ArticleConfig(
        6,
        "understanding-acne-scar-treatment",
        "Not Every Acne Scar Is the Same: Why Texture Requires a Layered Treatment Plan",
        "Skin Health",
        "skin-health",
        "Acne scars differ in depth, shape and colour. Learn why texture usually needs staged, layered treatment rather than one universal device.",
        "Franciele Sofiati explains acne scar types, texture assessment, layered treatment planning, realistic outcomes and when active acne comes first.",
        "acne-scars-and-natural-skin-texture.webp",
        "Close-up of natural facial texture and post-acne marks.",
        "postsportraits7.png",
        "franciele-sofiati-mauve-suit-editorial-portrait.webp",
        "Franciele Sofiati wearing a mauve suit with her arms folded.",
        "postsportraits8.png",
        "franciele-sofiati-peach-suit-editorial-portrait.webp",
        "Franciele Sofiati wearing a pale peach suit with her arms folded.",
        "title-led",
        (2, 7, 4),
        (
            ("acne scars", "../skin.html#acne-without-punishment"),
            ("microneedling", "../treatments.html#microneedling"),
            ("CO₂ laser", "../laser.html#co-resurfacing"),
        ),
    ),
    ArticleConfig(
        7,
        "fractional-co2-laser-recovery-and-aftercare",
        "Fractional CO₂ Laser Without the Hype: Preparation, Recovery and the Results That Take Time",
        "Laser & Technology",
        "laser-technology",
        "An honest account of fractional CO₂ laser: who may suit it, how preparation shapes safety, what recovery involves and why remodelling takes time.",
        "A medically responsible guide to fractional CO2 laser preparation, visible recovery, aftercare, risks and gradual skin remodelling.",
        "fractional-co2-laser-treatment.webp",
        "A professional laser skin treatment performed with protective eyewear in place.",
        "postsportraits3.png",
        "franciele-sofiati-pale-rose-suit-portrait.webp",
        "Franciele Sofiati wearing a pale rose suit with her arms folded.",
        "postsportraits4.png",
        "franciele-sofiati-peach-blazer-editorial-portrait.webp",
        "Franciele Sofiati smiling in a pale peach blazer.",
        "panorama",
        (1, 6, 8),
        (
            ("Fractional CO₂ laser", "../laser.html#co-resurfacing"),
            ("aftercare", "../care.html#aftercare-foundations"),
            ("results", "../results.html#timing"),
        ),
    ),
    ArticleConfig(
        8,
        "laser-hair-removal-process-and-maintenance",
        "Laser Hair Removal Is a Process, Not a Single Appointment",
        "Laser & Technology",
        "laser-technology",
        "Why the hair cycle makes laser reduction a series, how preparation protects skin, and why maintenance and hormonal context matter.",
        "Learn how laser hair removal follows the hair cycle, why sessions and maintenance vary, and how preparation and skin assessment support safety.",
        "professional-laser-hair-removal-treatment.webp",
        "A laser hair-removal handpiece being used during a professional body treatment.",
        "postsportraits10.png",
        "franciele-sofiati-lilac-suit-folded-arms-portrait.webp",
        "Franciele Sofiati wearing a lilac suit with her arms folded.",
        "postsportraits11.png",
        "franciele-sofiati-lilac-suit-side-portrait.webp",
        "Franciele Sofiati in a lilac suit, turned slightly to the side.",
        "portrait-led",
        (7, 10, 1),
        (
            ("laser hair removal", "../laser.html#laser-hair-reduction"),
            ("tanning", "../laser.html#when-to-wait"),
            ("consultation", "../consultation.html#consultation-introduction"),
        ),
    ),
    ArticleConfig(
        9,
        "ultrasound-radiofrequency-collagen-treatment",
        "Collagen Takes Time: Understanding Ultrasound and Radiofrequency Without Expecting a Facelift",
        "Laser & Technology",
        "laser-technology",
        "How ultrasound and radiofrequency differ, where gradual collagen support can help, and why neither should be framed as a non-surgical facelift.",
        "Understand ultrasound and radiofrequency for gradual collagen support, realistic firmness goals, treatment differences and patient selection.",
        "ultrasound-radiofrequency-collagen-care.webp",
        "An energy-based facial treatment being performed in a professional setting.",
        "postsportraits15.png",
        "franciele-sofiati-blue-grey-suit-portrait.webp",
        "Franciele Sofiati standing in a blue-grey suit.",
        "postsportraits16.png",
        "franciele-sofiati-powder-blue-suit-portrait.webp",
        "Franciele Sofiati wearing a powder-blue suit with her arms folded.",
        "split",
        (7, 1, 4),
        (
            ("microfocused ultrasound", "../treatments.html#featured-treatment"),
            ("radiofrequency", "../treatments.html#treatment-index"),
            ("results", "../results.html#timing"),
        ),
    ),
    ArticleConfig(
        10,
        "hair-thinning-causes-and-scalp-care",
        "Hair Thinning Needs a Cause Before It Needs a Procedure",
        "Hair & Scalp",
        "hair-scalp",
        "Shedding, thinning and breakage need different answers. A cause-led guide to scalp assessment, referral and realistic procedural support.",
        "A cause-led guide to hair thinning, shedding, scalp assessment, medical referral, microneedling support and realistic treatment timelines.",
        "scalp-serum-and-hair-care.webp",
        "Hair serum being applied carefully to a visible scalp parting.",
        "postsportraits19.png",
        "franciele-sofiati-thoughtful-red-suit-portrait.webp",
        "Franciele Sofiati in a red suit resting one hand beneath her chin.",
        "postsportraits20.webp",
        "franciele-sofiati-relaxed-white-blazer-portrait.webp",
        "Franciele Sofiati smiling in a white blazer.",
        "title-led",
        (1, 8, 3),
        (
            ("scalp microneedling", "../treatments.html#scalp-and-microinfusion"),
            ("medical assessment", "../consultation.html#consultation-introduction"),
            ("hair consultation", "../consultation.html#what-to-bring"),
        ),
    ),
)


EDITORIAL_ORDER: tuple[int, ...] = (1, 3, 2, 4, 6, 5, 7, 9, 8, 10)

CATEGORIES: tuple[tuple[str, str, tuple[int, ...]], ...] = (
    ("Consultation & Care", "consultation-care", (1, 2, 3)),
    ("Skin Health", "skin-health", (4, 6)),
    ("Laser & Technology", "laser-technology", (5, 7, 8, 9)),
    ("Hair & Scalp", "hair-scalp", (10,)),
)


@dataclass
class BodyItem:
    kind: str
    text: str


@dataclass
class AuthorBlock:
    name: str = "Franciele Sofiati"
    credentials: list[str] = field(default_factory=list)
    label: str = "ABOUT THE AUTHOR"
    statement: str = "You deserve care that helps you feel informed, confident and completely yourself."
    bio: str = ""
    signoff: str = ""


@dataclass
class Article:
    config: ArticleConfig
    kicker: str
    title: str
    deck: str
    byline: str
    feature_media: str
    caption: str
    at_glance: list[str]
    body: list[BodyItem]
    faq_heading: str
    faqs: list[tuple[str, str]]
    pull_quote: str
    author: AuthorBlock
    word_count: int
    reading_minutes: int


def normalise_space(value: str) -> str:
    return " ".join(value.replace("\u00a0", " ").split())


def node_text(node: ET.Element) -> str:
    return normalise_space("".join(part.text or "" for part in node.iter(W + "t")))


def paragraph_style(paragraph: ET.Element) -> str:
    properties = paragraph.find(W + "pPr")
    if properties is None:
        return ""
    style = properties.find(W + "pStyle")
    return style.get(W + "val", "") if style is not None else ""


def embedded_relationships(node: ET.Element) -> list[str]:
    return [image.get(R + "embed", "") for image in node.findall(".//" + A + "blip") if image.get(R + "embed")]


def table_paragraphs(table: ET.Element) -> list[list[tuple[str, str, list[str]]]]:
    cells: list[list[tuple[str, str, list[str]]]] = []
    for cell in table.findall("./" + W + "tr/" + W + "tc"):
        paragraphs: list[tuple[str, str, list[str]]] = []
        for paragraph in cell.findall("./" + W + "p"):
            paragraphs.append((paragraph_style(paragraph), node_text(paragraph), embedded_relationships(paragraph)))
        cells.append(paragraphs)
    return cells


def parse_author(table: ET.Element) -> AuthorBlock:
    cells = table_paragraphs(table)
    author = AuthorBlock()
    if not cells:
        return author
    for style, text, _ in cells[0]:
        if not text:
            continue
        if style == "AuthorName":
            author.name = text
        elif style == "AuthorCredential":
            author.credentials.append(text)
    if len(cells) > 1:
        unstyled: list[str] = []
        for style, text, _ in cells[1]:
            if not text:
                continue
            if style == "AuthorLabel":
                author.label = text
            elif style == "AuthorStatement":
                author.statement = text
            elif style == "AuthorBio":
                author.bio = text
            elif not style:
                unstyled.append(text)
        if unstyled:
            author.signoff = unstyled[-1]
    return author


def parse_source() -> list[Article]:
    if not DOCX.is_file():
        raise SystemExit(f"Missing authoritative Journal source: {DOCX.relative_to(ROOT)}")

    with ZipFile(DOCX) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
        relationships = ET.fromstring(archive.read("word/_rels/document.xml.rels"))
    relation_targets = {
        relation.get("Id", ""): relation.get("Target", "")
        for relation in relationships.findall(REL + "Relationship")
    }
    body = document.find(W + "body")
    if body is None:
        raise SystemExit("The Journal source has no Word document body.")
    children = list(body)
    starts = [
        index
        for index, child in enumerate(children)
        if child.tag == W + "p" and paragraph_style(child) == "ArticleKicker"
    ]
    if len(starts) != 10:
        raise SystemExit(f"Expected exactly 10 ArticleKicker entries; found {len(starts)}.")

    by_number = {config.number: config for config in ARTICLE_CONFIGS}
    parsed: list[Article] = []
    for article_index, start in enumerate(starts):
        end = starts[article_index + 1] if article_index + 1 < len(starts) else len(children)
        chunk = children[start:end]
        paragraphs = [child for child in chunk if child.tag == W + "p"]
        kicker_paragraph = next(p for p in paragraphs if paragraph_style(p) == "ArticleKicker")
        kicker = node_text(kicker_paragraph)
        number_match = re.match(r"(\d{2})\s*·", kicker)
        if not number_match:
            raise SystemExit(f"Cannot read article number from kicker: {kicker}")
        number = int(number_match.group(1))
        config = by_number[number]
        title = node_text(next(p for p in paragraphs if paragraph_style(p) == "ArticleTitle"))
        deck = node_text(next(p for p in paragraphs if paragraph_style(p) == "ArticleDeck"))
        if title != config.expected_title:
            raise SystemExit(f"Article {number:02d} title changed in the source. Expected {config.expected_title!r}; found {title!r}.")

        title_index = chunk.index(next(p for p in paragraphs if paragraph_style(p) == "ArticleTitle"))
        deck_node = next(p for p in paragraphs if paragraph_style(p) == "ArticleDeck")
        deck_index = chunk.index(deck_node)
        byline = ""
        for child in chunk[deck_index + 1 :]:
            if child.tag != W + "p":
                continue
            text = node_text(child)
            if text:
                byline = text
                break

        feature_relation = ""
        for child in chunk[title_index + 1 :]:
            relations = embedded_relationships(child)
            if relations:
                feature_relation = relations[0]
                break
        feature_target = relation_targets.get(feature_relation, "")
        feature_media = Path(feature_target).name
        if not feature_media:
            raise SystemExit(f"Article {number:02d} has no feature image relationship.")

        caption = node_text(next(p for p in paragraphs if paragraph_style(p) == "Caption"))
        at_glance: list[str] = []
        author = AuthorBlock()
        body_items: list[BodyItem] = []
        faqs: list[tuple[str, str]] = []
        faq_heading = "Questions patients often ask"
        pull_quote = ""
        in_faq = False
        pending_question = ""

        for child in chunk:
            if child.tag == W + "tbl":
                cells = table_paragraphs(child)
                styled = [(style, text) for cell in cells for style, text, _ in cell if text]
                glance = [text for style, text in styled if style == "AtGlance"]
                if glance:
                    at_glance = glance
                    continue
                if any(style == "AuthorName" for style, _ in styled):
                    author = parse_author(child)
                    continue
                table_text = node_text(child)
                if table_text and ("“" in table_text or "\"" in table_text):
                    pull_quote = table_text
                    body_items.append(BodyItem("quote", table_text))
                continue
            if child.tag != W + "p":
                continue
            style = paragraph_style(child)
            text = node_text(child)
            if not text:
                continue
            if style in {"ArticleKicker", "ArticleTitle", "ArticleDeck", "Caption"}:
                continue
            if text == byline:
                continue
            if embedded_relationships(child):
                continue
            if style == "SectionHeading" and text == "Questions patients often ask":
                faq_heading = text
                in_faq = True
                continue
            if in_faq:
                if style == "FAQQuestion":
                    pending_question = re.sub(r"^\d{2}\s+", "", text)
                elif style == "FAQAnswer" and pending_question:
                    faqs.append((pending_question, text))
                    pending_question = ""
                continue
            if style == "SectionHeading":
                body_items.append(BodyItem("heading", text))
            elif style == "EditorialLead":
                body_items.append(BodyItem("lead", text))
            elif style == "EditorialBullet":
                body_items.append(BodyItem("bullet", re.sub(r"^[•\-]\s*", "", text)))
            elif style == "BodyText":
                body_items.append(BodyItem("paragraph", text))

        if len(at_glance) != 5:
            raise SystemExit(f"Article {number:02d} should contain 5 At a Glance points; found {len(at_glance)}.")
        if len(faqs) != 10:
            raise SystemExit(f"Article {number:02d} should contain 10 FAQs; found {len(faqs)}.")
        if not body_items or not pull_quote or not author.bio:
            raise SystemExit(f"Article {number:02d} is missing body, pull quote, or author content.")

        countable = [title, deck, *at_glance]
        countable.extend(item.text for item in body_items)
        countable.extend(text for pair in faqs for text in pair)
        word_count = len(re.findall(r"\b[\w’'-]+\b", " ".join(countable), flags=re.UNICODE))
        parsed.append(
            Article(
                config=config,
                kicker=kicker,
                title=title,
                deck=deck,
                byline=byline,
                feature_media=feature_media,
                caption=caption,
                at_glance=at_glance,
                body=body_items,
                faq_heading=faq_heading,
                faqs=faqs,
                pull_quote=pull_quote,
                author=author,
                word_count=word_count,
                reading_minutes=max(1, math.ceil(word_count / 220)),
            )
        )

    parsed.sort(key=lambda article: article.config.number)
    return parsed


def article_url(article: Article) -> str:
    return f"{SITE_ORIGIN}/journal/{article.config.slug}.html"


def asset_url(filename: str) -> str:
    return f"{SITE_ORIGIN}/assets/posts/journal/{filename}"


def html_id(value: str) -> str:
    value = value.lower().replace("₂", "2").replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    return value or "section"


def json_script(payload: object) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")


def common_schema_nodes() -> list[dict[str, object]]:
    return [
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
            "logo": LOGO_IMAGE,
            "areaServed": {"@type": "City", "name": "Londrina, Paraná, Brazil"},
            "founder": {"@id": f"{SITE_ORIGIN}/#franciele"},
            "sameAs": [SITE_INSTAGRAM],
        },
    ]


def partial_mounts(prefix: str = "") -> str:
    return textwrap.dedent(
        f"""\
        <template data-sf-partial="cookie-banner"></template>
        <template data-sf-partial="floating-widgets"></template>
        <script type="module" src="{prefix}js/main.js"></script>"""
    )


def head_html(
    *,
    title: str,
    description: str,
    canonical: str,
    og_image: str,
    schema: dict[str, object],
    prefix: str = "",
    article: bool = False,
    portuguese_alternate: str | None = None,
) -> str:
    alternate_pt = (
        f'<link rel="alternate" hreflang="pt-BR" href="{escape(portuguese_alternate, quote=True)}"/>\n'
        if portuguese_alternate
        else ""
    )
    og_type = "article" if article else "website"
    return textwrap.dedent(
        f"""\
        <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <meta name="theme-color" content="#66755f"/>
        <meta name="robots" content="index, follow"/>
        <meta name="description" content="{escape(description, quote=True)}"/>
        <title>{escape(title)}</title>
        <link rel="canonical" href="{escape(canonical, quote=True)}"/>
        <link rel="alternate" hreflang="en" href="{escape(canonical, quote=True)}"/>
        {alternate_pt}<link rel="alternate" hreflang="x-default" href="{escape(canonical, quote=True)}"/>
        <meta property="og:title" content="{escape(title, quote=True)}"/>
        <meta property="og:description" content="{escape(description, quote=True)}"/>
        <meta property="og:url" content="{escape(canonical, quote=True)}"/>
        <meta property="og:type" content="{og_type}"/>
        <meta property="og:site_name" content="{SITE_NAME}"/>
        <meta property="og:locale" content="en_US"/>
        <meta property="og:image" content="{escape(og_image, quote=True)}"/>
        <meta property="og:image:width" content="1600"/>
        <meta property="og:image:height" content="900"/>
        <meta name="twitter:card" content="summary_large_image"/>
        <meta name="twitter:title" content="{escape(title, quote=True)}"/>
        <meta name="twitter:description" content="{escape(description, quote=True)}"/>
        <meta name="twitter:image" content="{escape(og_image, quote=True)}"/>
        <script type="application/ld+json">{json_script(schema)}</script>
        <link rel="icon" type="image/png" sizes="96x96" href="{prefix}assets/favicons/sofiati-favicon-96.png"/>
        <link rel="shortcut icon" href="{prefix}favicon.ico"/>
        <link rel="apple-touch-icon" sizes="180x180" href="{prefix}assets/favicons/apple-touch-icon-180.png"/>
        <link rel="manifest" href="{prefix}site.webmanifest"/>
        <link rel="stylesheet" href="{prefix}css/site.css"/>
        </head>"""
    )


def story_meta(article: Article) -> str:
    return (
        f'<span>{article.reading_minutes} min read</span>'
        f'<span aria-hidden="true">·</span><span>Article {article.config.number:02d}</span>'
    )


def story_copy(article: Article, *, label: str | None = None) -> str:
    eyebrow = label or article.config.category
    return textwrap.dedent(
        f"""\
        <div class="sj-story__copy">
          <p class="sj-story__eyebrow"><span>{escape(eyebrow)}</span><span aria-hidden="true">{article.config.number:02d}</span></p>
          <h3 class="sj-story__title">{escape(article.title)}</h3>
          <p class="sj-story__excerpt">{escape(article.config.excerpt)}</p>
          <p class="sj-story__meta">{story_meta(article)}</p>
          <span class="sj-story__read">Read article <span aria-hidden="true">→</span></span>
        </div>"""
    )


def story_anchor(article: Article, class_name: str, *, label: str | None = None, image: bool = True) -> str:
    figure = ""
    if image:
        figure = textwrap.dedent(
            f"""\
            <figure class="sj-story__image">
              <img src="assets/posts/journal/{article.config.feature_filename}" alt="{escape(article.config.feature_alt, quote=True)}" width="1600" height="900" loading="lazy" decoding="async"/>
            </figure>"""
        )
    return textwrap.dedent(
        f"""\
        <article class="{class_name}">
          <a class="sj-story__link" href="journal/{article.config.slug}.html">
            {figure}
            {story_copy(article, label=label)}
          </a>
        </article>"""
    )


def render_journal_index(articles: Sequence[Article]) -> str:
    by_number = {article.config.number: article for article in articles}
    lead = by_number[1]
    schema_graph = common_schema_nodes()
    schema_graph.extend(
        [
            {
                "@type": "BreadcrumbList",
                "@id": f"{SITE_ORIGIN}/journal.html#breadcrumb",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_ORIGIN}/"},
                    {"@type": "ListItem", "position": 2, "name": "Journal", "item": f"{SITE_ORIGIN}/journal.html"},
                ],
            },
            {
                "@type": ["CollectionPage", "Blog"],
                "@id": f"{SITE_ORIGIN}/journal.html#journal",
                "url": f"{SITE_ORIGIN}/journal.html",
                "name": "The Journal | Franciele Sofiati",
                "description": "Professional perspectives on skin health, aesthetic care, laser, prevention, aftercare, scalp health and thoughtful treatment planning.",
                "inLanguage": "en",
                "isPartOf": {"@id": f"{SITE_ORIGIN}/#website"},
                "author": {"@id": f"{SITE_ORIGIN}/#franciele"},
                "breadcrumb": {"@id": f"{SITE_ORIGIN}/journal.html#breadcrumb"},
                "mainEntity": {"@id": f"{SITE_ORIGIN}/journal.html#article-list"},
            },
            {
                "@type": "ItemList",
                "@id": f"{SITE_ORIGIN}/journal.html#article-list",
                "numberOfItems": 10,
                "itemListOrder": "https://schema.org/ItemListOrderAscending",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": position,
                        "url": article_url(by_number[number]),
                        "name": by_number[number].title,
                    }
                    for position, number in enumerate(EDITORIAL_ORDER, start=1)
                ],
            },
        ]
    )
    schema = {"@context": "https://schema.org", "@graph": schema_graph}

    category_links = "\n".join(
        f'<a class="sj-category-index__item sj-category-index__item--{position}" href="#{slug}"><span>{escape(name)}</span><small>{len(numbers):02d} {"essay" if len(numbers) == 1 else "essays"}</small></a>'
        for position, (name, slug, numbers) in enumerate(CATEGORIES, start=1)
    )
    supporting = "\n".join(
        story_anchor(by_number[number], f"sj-support-story sj-support-story--{position}")
        for position, number in enumerate((3, 2), start=1)
    )
    rows = "\n".join(story_anchor(by_number[number], "sj-row-story") for number in (6, 5))
    overlays = "\n".join(
        story_anchor(by_number[number], f"sj-overlay-story sj-overlay-story--{position}")
        for position, number in enumerate((7, 9, 8), start=1)
    )
    edition_entries = "\n".join(
        textwrap.dedent(
            f"""\
            <li>
              <a href="journal/{by_number[number].config.slug}.html">
                <span class="sj-register__number">{number:02d}</span>
                <span class="sj-register__entry"><strong>{escape(by_number[number].title)}</strong><small>{escape(by_number[number].config.category)} · {by_number[number].reading_minutes} min read</small></span>
                <span class="sj-register__arrow" aria-hidden="true">↗</span>
              </a>
            </li>"""
        )
        for number in EDITORIAL_ORDER
    )

    head = head_html(
        title="The Journal | Franciele Sofiati",
        description="Professional perspectives on skin health, aesthetic care, laser, prevention, aftercare, scalp health and thoughtful treatment planning.",
        canonical=f"{SITE_ORIGIN}/journal.html",
        og_image=asset_url(lead.config.feature_filename),
        schema=schema,
        portuguese_alternate=f"{SITE_ORIGIN}/pt/journal.html",
    )
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html data-default-lang="en" lang="en">
        {head}
        <body class="sf-site sf-page sf-family-content sf-journal-index" data-page="journal">
        <a class="skip-link" href="#main">Skip to main content</a>
        <template data-sf-partial="topbar"></template>
        <template data-sf-partial="header"></template>
        <template data-sf-partial="mobile-menu"></template>
        <main class="sf-main sj-main" id="main" aria-label="Journal publication">
          <nav class="sf-breadcrumbs sf-container" aria-label="Breadcrumb">
            <ol><li><a href="index.html">Home</a></li><li><span aria-current="page">Journal</span></li></ol>
          </nav>

          <header class="sj-masthead sf-container">
            <div class="sj-masthead__rail"><span>Franciele Sofiati</span><span class="sj-masthead__place">Professional perspectives · Londrina</span><span class="sj-masthead__edition">10 complete essays</span></div>
            <div class="sj-masthead__title-row">
              <div><p class="sj-publication-label">Skin health · Technology · Considered care</p><h1>Journal</h1></div>
              <p class="sj-masthead__intro">Clear perspectives on skin health, aesthetic treatments, prevention, recovery, scalp care and <em>thoughtful planning.</em></p>
            </div>
          </header>

          <section class="sj-lead sf-container" aria-labelledby="lead-story-title">
            <a class="sj-lead__link" href="journal/{lead.config.slug}.html">
              <figure class="sj-lead__image">
                <img src="assets/posts/journal/{lead.config.feature_filename}" alt="{escape(lead.config.feature_alt, quote=True)}" width="1600" height="900" loading="eager" fetchpriority="high" decoding="async"/>
                <figcaption>Lead essay · Consultation & Care</figcaption>
              </figure>
              <div class="sj-lead__copy">
                <p class="sj-lead__number"><span>Lead story</span><span aria-hidden="true">01</span></p>
                <h2 id="lead-story-title">{escape(lead.title)}</h2>
                <p>{escape(lead.config.excerpt)}</p>
                <p class="sj-story__meta">{story_meta(lead)}</p>
                <span class="sj-story__read">Read the lead essay <span aria-hidden="true">→</span></span>
              </div>
            </a>
          </section>

          <nav class="sj-category-index sf-container" aria-label="Browse Journal subjects">{category_links}</nav>

          <section class="sj-support sf-container" id="consultation-care" aria-labelledby="selected-reading-title">
            <header class="sj-section-heading"><div><p class="sj-section-label">Consultation &amp; Care</p><h2 id="selected-reading-title">Begin with the skin’s context, not a procedure.</h2></div><p class="sj-section-heading__intro">These essays explain why simplifying, observing and assessing carefully can be more useful than immediately adding another treatment or product.</p></header>
            <div class="sj-support__grid">{supporting}</div>
          </section>

          <section class="sj-full-feature" id="skin-health" aria-labelledby="skin-health-title">
            <div class="sj-full-feature__inner sf-container">
              <header class="sj-section-heading"><div><p class="sj-section-label">Skin Health</p><h2 id="skin-health-title">Look closely before trying to correct what you see.</h2></div><p class="sj-section-heading__intro">Colour, texture and redness can look deceptively simple. Responsible planning begins by understanding their pattern, history and possible causes.</p></header>
              <a href="journal/{by_number[4].config.slug}.html" class="sj-full-feature__link">
                <figure><img src="assets/posts/journal/{by_number[4].config.feature_filename}" alt="{escape(by_number[4].config.feature_alt, quote=True)}" width="1600" height="900" loading="lazy" decoding="async"/></figure>
                <div class="sj-full-feature__copy"><p class="sj-story__eyebrow"><span>{escape(by_number[4].config.category)}</span><span aria-hidden="true">04</span></p><h3>{escape(by_number[4].title)}</h3><p class="sj-full-feature__excerpt">{escape(by_number[4].config.excerpt)}</p><p class="sj-story__meta">{story_meta(by_number[4])}</p><span class="sj-story__read">Read article <span aria-hidden="true">→</span></span></div>
              </a>
            </div>
          </section>

          <section class="sj-rows sf-container" aria-labelledby="clinical-notes-title">
            <header class="sj-section-heading sj-section-heading--rule"><div><p class="sj-section-label">Clinical notes</p><h2 id="clinical-notes-title">Different concerns need different plans.</h2></div><p class="sj-section-heading__intro">Acne scarring and persistent redness both reward precise assessment. A device name alone cannot explain what should happen next.</p></header>
            <div class="sj-rows__list">{rows}</div>
          </section>

          <section class="sj-overlays" id="laser-technology" aria-labelledby="technology-perspectives-title">
            <div class="sj-overlays__inner sf-container">
              <header class="sj-section-heading"><div><p class="sj-section-label">Laser &amp; Technology</p><h2 id="technology-perspectives-title">Technology is useful when expectations are clear.</h2></div><p class="sj-section-heading__intro">Preparation, recovery, treatment intervals and biological timing matter as much as the device itself.</p></header>
              <div class="sj-overlays__grid">{overlays}</div>
            </div>
          </section>

          <section class="sj-quiet-feature sf-container" id="hair-scalp" aria-labelledby="hair-scalp-feature-title">
            <header class="sj-section-heading"><div><p class="sj-section-label">Hair &amp; Scalp</p><h2 id="hair-scalp-feature-title">Understand the cause before choosing the procedure.</h2></div><p class="sj-section-heading__intro">Hair thinning can be deeply personal. A responsible first step is to understand what is changing and when medical investigation may be needed.</p></header>
            <a href="journal/{by_number[10].config.slug}.html" class="sj-quiet-feature__link">
              <div class="sj-quiet-feature__copy"><p>10 · Hair &amp; Scalp</p><h3>{escape(by_number[10].title)}</h3><p>{escape(by_number[10].config.excerpt)}</p><p class="sj-story__meta">{story_meta(by_number[10])}</p><span class="sj-story__read">Read article <span aria-hidden="true">→</span></span></div>
              <figure><img src="assets/posts/journal/{by_number[10].config.feature_filename}" alt="{escape(by_number[10].config.feature_alt, quote=True)}" width="1600" height="900" loading="lazy" decoding="async"/></figure>
            </a>
          </section>

          <section class="sj-register sf-container" aria-labelledby="reading-register-title">
            <header class="sj-register__heading"><p class="sj-publication-label">Complete edition · 10 essays</p><h2 id="reading-register-title">Every article, at a glance.</h2><p class="sj-register__intro">A concise index of the complete first edition, ordered to move from assessment and skin health towards technology and scalp care.</p></header>
            <ol class="sj-register__list">{edition_entries}</ol>
          </section>

          <section class="sj-signoff" aria-labelledby="journal-signoff-title">
            <div class="sj-signoff__inner sf-container">
              <figure><img src="assets/posts/journal/{by_number[10].config.author_portrait_filename}" alt="{escape(by_number[10].config.author_portrait_alt, quote=True)}" width="720" height="900" loading="lazy" decoding="async"/></figure>
              <div class="sj-signoff__copy"><p class="sj-publication-label">A note from Franciele</p><h2 id="journal-signoff-title">Read with curiosity. <em>Choose with clarity.</em></h2><p>These articles offer useful context, but they cannot assess your skin or confirm suitability. Bring your questions to a consultation if you would like guidance that reflects your own history and priorities.</p><div class="sj-signoff__actions"><a class="sf-button sf-button--primary" href="consultation.html">Consult</a><a href="treatments.html">View treatments <span aria-hidden="true">→</span></a></div></div>
            </div>
          </section>
        </main>
        <template data-sf-partial="footer"></template>
        {partial_mounts()}
        </body>
        </html>
        """
    ).strip() + "\n"


def link_text_once(text: str, links: Sequence[tuple[str, str]], used: set[str]) -> str:
    candidates: list[tuple[int, int, str, str]] = []
    for phrase, href in links:
        key = phrase.casefold()
        if key in used:
            continue
        match = re.search(re.escape(phrase), text, flags=re.IGNORECASE)
        if match:
            candidates.append((match.start(), match.end(), phrase, href))
    if not candidates:
        return escape(text)
    start, end, phrase, href = sorted(candidates, key=lambda candidate: candidate[0])[0]
    used.add(phrase.casefold())
    return f"{escape(text[:start])}<a href=\"{escape(href, quote=True)}\">{escape(text[start:end])}</a>{escape(text[end:])}"


def render_body(article: Article) -> str:
    output: list[str] = []
    section_open = False
    bullet_buffer: list[str] = []
    used_links: set[str] = set()

    def flush_bullets() -> None:
        if not bullet_buffer:
            return
        items: list[str] = []
        for bullet in bullet_buffer:
            if " — " in bullet:
                label, detail = bullet.split(" — ", 1)
                linked = link_text_once(detail, article.config.contextual_links, used_links)
                items.append(f"<li><strong>{escape(label)}</strong><span> — {linked}</span></li>")
            else:
                items.append(f"<li>{link_text_once(bullet, article.config.contextual_links, used_links)}</li>")
        output.append(f'<ul class="sja-editorial-list">{"".join(items)}</ul>')
        bullet_buffer.clear()

    for item in article.body:
        if item.kind == "bullet":
            bullet_buffer.append(item.text)
            continue
        flush_bullets()
        if item.kind == "heading":
            if section_open:
                output.append("</section>")
            section_id = f"article-{article.config.number:02d}-{html_id(item.text)}"
            output.append(f'<section class="sja-reading-section" aria-labelledby="{section_id}"><h2 id="{section_id}">{escape(item.text)}</h2>')
            section_open = True
        elif item.kind == "paragraph":
            output.append(f"<p>{link_text_once(item.text, article.config.contextual_links, used_links)}</p>")
        elif item.kind == "lead":
            output.append(f'<p class="sja-editorial-lead">{link_text_once(item.text, article.config.contextual_links, used_links)}</p>')
        elif item.kind == "quote":
            output.append(f'<blockquote class="sja-pullquote"><p>{escape(item.text)}</p></blockquote>')
    flush_bullets()
    if section_open:
        output.append("</section>")
    return "\n".join(output)


def render_article_page(article: Article, all_articles: Sequence[Article]) -> str:
    by_number = {entry.config.number: entry for entry in all_articles}
    position = EDITORIAL_ORDER.index(article.config.number)
    previous_article = by_number[EDITORIAL_ORDER[position - 1]] if position > 0 else None
    next_article = by_number[EDITORIAL_ORDER[position + 1]] if position + 1 < len(EDITORIAL_ORDER) else None
    canonical = article_url(article)
    feature_url = asset_url(article.config.feature_filename)

    breadcrumb = {
        "@type": "BreadcrumbList",
        "@id": f"{canonical}#breadcrumb",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE_ORIGIN}/"},
            {"@type": "ListItem", "position": 2, "name": "Journal", "item": f"{SITE_ORIGIN}/journal.html"},
            {"@type": "ListItem", "position": 3, "name": article.title, "item": canonical},
        ],
    }
    schema_graph = common_schema_nodes()
    schema_graph.extend(
        [
            breadcrumb,
            {
                "@type": "ImageObject",
                "@id": f"{feature_url}#primaryimage",
                "url": feature_url,
                "contentUrl": feature_url,
                "width": 1600,
                "height": 900,
                "caption": article.config.feature_alt,
            },
            {
                "@type": "BlogPosting",
                "@id": f"{canonical}#article",
                "url": canonical,
                "mainEntityOfPage": {"@id": canonical},
                "headline": article.title,
                "description": article.config.meta_description,
                "articleSection": article.config.category,
                "wordCount": article.word_count,
                "inLanguage": "en",
                "author": {"@id": f"{SITE_ORIGIN}/#franciele"},
                "publisher": {"@id": f"{SITE_ORIGIN}/#practice"},
                "isPartOf": {"@id": f"{SITE_ORIGIN}/journal.html#journal"},
                "image": {"@id": f"{feature_url}#primaryimage"},
                "breadcrumb": {"@id": f"{canonical}#breadcrumb"},
            },
            {
                "@type": "WebPage",
                "@id": canonical,
                "url": canonical,
                "name": article.title,
                "description": article.config.meta_description,
                "inLanguage": "en",
                "isPartOf": {"@id": f"{SITE_ORIGIN}/#website"},
                "about": {"@id": f"{canonical}#article"},
                "primaryImageOfPage": {"@id": f"{feature_url}#primaryimage"},
            },
        ]
    )
    schema = {"@context": "https://schema.org", "@graph": schema_graph}
    page_title = f"{article.title} | Franciele Sofiati"
    head = head_html(
        title=page_title,
        description=article.config.meta_description,
        canonical=canonical,
        og_image=feature_url,
        schema=schema,
        prefix="../",
        article=True,
    )

    at_glance = "".join(f"<li>{escape(point)}</li>" for point in article.at_glance)
    faqs = "\n".join(
        textwrap.dedent(
            f"""\
            <details class="sja-faq">
              <summary><span class="sja-faq__number">{index:02d}</span><span class="sja-faq__question">{escape(question)}</span><span class="sja-faq__icon" aria-hidden="true">+</span></summary>
              <div><p>{escape(answer)}</p></div>
            </details>"""
        )
        for index, (question, answer) in enumerate(article.faqs, start=1)
    )
    related = "\n".join(
        textwrap.dedent(
            f"""\
            <article class="sja-related-card">
              <a href="{by_number[number].config.slug}.html">
                <figure><img src="../assets/posts/journal/{by_number[number].config.feature_filename}" alt="{escape(by_number[number].config.feature_alt, quote=True)}" width="1600" height="900" loading="lazy" decoding="async"/></figure>
                <div><p>{escape(by_number[number].config.category)} · {by_number[number].reading_minutes} min</p><h3>{escape(by_number[number].title)}</h3><span>Read next <span aria-hidden="true">→</span></span></div>
              </a>
            </article>"""
        )
        for number in article.config.related
    )

    nav_items: list[str] = []
    if previous_article:
        nav_items.append(
            f'<a rel="prev" href="{previous_article.config.slug}.html"><span>← Previous essay</span><strong>{escape(previous_article.title)}</strong></a>'
        )
    else:
        nav_items.append('<a href="../journal.html"><span>← Publication</span><strong>Return to the complete Journal</strong></a>')
    if next_article:
        nav_items.append(
            f'<a rel="next" href="{next_article.config.slug}.html"><span>Next essay →</span><strong>{escape(next_article.title)}</strong></a>'
        )
    else:
        nav_items.append('<a href="../journal.html#reading-register-title"><span>Complete edition →</span><strong>Browse all ten essays</strong></a>')

    credentials = "".join(f"<span>{escape(line)}</span>" for line in article.author.credentials)
    body_html = render_body(article)
    return textwrap.dedent(
        f"""\
        <!DOCTYPE html>
        <html data-default-lang="en" lang="en">
        {head}
        <body class="sf-site sf-page sf-family-content sf-journal-article" data-page="journal" data-site-root="../" data-article="{article.config.slug}">
        <a class="skip-link" href="#main">Skip to main content</a>
        <template data-sf-partial="topbar"></template>
        <template data-sf-partial="header"></template>
        <template data-sf-partial="mobile-menu"></template>
        <main class="sf-main sja-main" id="main" aria-label="Journal article">
          <nav class="sf-breadcrumbs sf-container" aria-label="Breadcrumb">
            <ol><li><a href="../index.html">Home</a></li><li><a href="../journal.html">Journal</a></li><li><span aria-current="page">{escape(article.title)}</span></li></ol>
          </nav>
          <article class="sja-article">
            <header class="sja-hero sja-hero--{article.config.layout} sf-container">
              <div class="sja-hero__intro">
                <p class="sja-publication"><a href="../journal.html">Journal</a><span aria-hidden="true">/</span><span>{escape(article.config.category)}</span><span aria-hidden="true">{article.config.number:02d}</span></p>
                <h1>{escape(article.title)}</h1>
                <p class="sja-standfirst">{escape(article.deck)}</p>
                <div class="sja-byline"><span>By Franciele Sofiati</span><span>{article.reading_minutes} min read</span><span>{article.word_count:,} words</span></div>
              </div>
              <figure class="sja-hero__feature">
                <img src="../assets/posts/journal/{article.config.feature_filename}" alt="{escape(article.config.feature_alt, quote=True)}" width="1600" height="900" loading="eager" fetchpriority="high" decoding="async"/>
                <figcaption>{escape(article.caption)}</figcaption>
              </figure>
              <figure class="sja-hero__portrait">
                <img src="../assets/posts/journal/{article.config.portrait_filename}" alt="{escape(article.config.portrait_alt, quote=True)}" width="720" height="900" loading="lazy" decoding="async"/>
              </figure>
            </header>

            <div class="sja-reading-grid sf-container">
              <aside class="sja-at-glance" aria-labelledby="at-a-glance-title">
                <div><p>Article {article.config.number:02d}</p><h2 id="at-a-glance-title">At a glance</h2><ol>{at_glance}</ol><a href="#questions">Skip to questions <span aria-hidden="true">↓</span></a></div>
              </aside>
              <div class="sja-prose">{body_html}</div>
            </div>

            <section class="sja-faqs" id="questions" aria-labelledby="questions-title">
              <div class="sja-faqs__inner sf-container"><header><p class="sja-label">Practical guidance</p><h2 id="questions-title">{escape(article.faq_heading)}</h2><p class="sja-faqs__intro">General information supports understanding, but personal suitability and safety still depend on individual assessment.</p></header><div class="sja-faqs__list">{faqs}</div></div>
            </section>

            <section class="sja-author sf-container" aria-labelledby="author-title-{article.config.number:02d}">
              <figure><img src="../assets/posts/journal/{article.config.author_portrait_filename}" alt="{escape(article.config.author_portrait_alt, quote=True)}" width="720" height="900" loading="lazy" decoding="async"/></figure>
              <div><p class="sja-label">{escape(article.author.label)}</p><h2 id="author-title-{article.config.number:02d}">{escape(article.author.name)}</h2><p class="sja-author__credentials">{credentials}</p><blockquote>{escape(article.author.statement)}</blockquote><p class="sja-author__bio">{escape(article.author.bio)}</p></div>
            </section>

            <section class="sja-consultation" aria-labelledby="consultation-invitation-title-{article.config.number:02d}">
              <div class="sja-consultation__inner sf-container"><p class="sja-label">Care, in context</p><h2 id="consultation-invitation-title-{article.config.number:02d}">Bring the information into <em>your</em> context.</h2><p class="sja-consultation__copy">{escape(article.author.signoff or 'Treatment suitability depends on individual assessment, clear expectations and a plan shaped around the person receiving care.')}</p><p class="sja-consultation__copy">An assessment can consider your history, preparation, recovery and alternatives. Reading an article does not confirm that a procedure is suitable for you.</p><div><a class="sf-button sf-button--primary" href="../consultation.html">Consult</a><a href="../treatments.html">View treatments <span aria-hidden="true">→</span></a></div></div>
            </section>

            <section class="sja-related sf-container" aria-labelledby="related-reading-title-{article.config.number:02d}">
              <header><p class="sja-label">Continue reading</p><h2 id="related-reading-title-{article.config.number:02d}">Related perspectives</h2></header><div class="sja-related__grid">{related}</div>
            </section>
            <nav class="sja-article-nav sf-container" aria-label="Article navigation">{''.join(nav_items)}</nav>
          </article>
        </main>
        <template data-sf-partial="footer"></template>
        {partial_mounts('../')}
        </body>
        </html>
        """
    ).strip() + "\n"


def optimise_image(source: Path, destination: Path, width: int | None = None) -> None:
    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick is required for --assets but the 'magick' command is unavailable.")
    destination.parent.mkdir(parents=True, exist_ok=True)
    command = [magick, str(source), "-auto-orient"]
    if width:
        command.extend(["-resize", f"{width}x>"])
    command.extend(["-strip", "-quality", "84", "-define", "webp:method=6", str(destination)])
    subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if not destination.is_file() or destination.stat().st_size == 0:
        raise SystemExit(f"Image optimisation failed for {source}")


def optimise_portrait(
    source: Path,
    destination: Path,
    temporary_root: Path,
    *,
    remove_checkerboard: bool = False,
) -> None:
    """Prepare a consistent 4:5 portrait without the supplied baked checkerboard.

    Portraits 3–19 are opaque PNG exports whose light grey checker pattern is
    part of the pixels, rather than real transparency. Their background is
    neutral and near-white while Franciele's clothing, hair and skin retain
    colour, so a restrained chroma/luminance mask removes the pattern without
    bleaching the subject. The two white-coat portraits use the clean versions
    embedded in the authoritative article document instead.
    """

    magick = shutil.which("magick")
    if not magick:
        raise SystemExit("ImageMagick is required for --assets but the 'magick' command is unavailable.")

    destination.parent.mkdir(parents=True, exist_ok=True)
    prepared = source
    if remove_checkerboard:
        mask = temporary_root / f"{source.stem}-foreground-mask.png"
        cutout = temporary_root / f"{source.stem}-cutout.png"
        mask_expression = (
            "(max(u.r,max(u.g,u.b))-min(u.r,min(u.g,u.b)))<0.025 "
            "&& (u.r+u.g+u.b)/3>0.87 ? 1 : 0"
        )
        subprocess.run(
            [
                magick,
                str(source),
                "-alpha",
                "off",
                "-fx",
                mask_expression,
                "-morphology",
                "Dilate",
                "Disk:1",
                "-blur",
                "0x0.45",
                "-negate",
                str(mask),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        subprocess.run(
            [
                magick,
                str(source),
                str(mask),
                "-alpha",
                "off",
                "-compose",
                "CopyOpacity",
                "-composite",
                str(cutout),
            ],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        prepared = cutout

    subprocess.run(
        [
            magick,
            str(prepared),
            "-auto-orient",
            "-resize",
            "720x900",
            "-gravity",
            "center",
            "-background",
            "none",
            "-extent",
            "720x900",
            "-strip",
            "-quality",
            "84",
            "-define",
            "webp:method=6",
            str(destination),
        ],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if not destination.is_file() or destination.stat().st_size == 0:
        raise SystemExit(f"Portrait optimisation failed for {source}")


def prepare_assets(articles: Sequence[Article]) -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    with ZipFile(DOCX) as archive, tempfile.TemporaryDirectory(prefix="sofiati-journal-") as temporary:
        temporary_root = Path(temporary)
        for article in articles:
            source_member = f"word/media/{article.feature_media}"
            source_path = temporary_root / article.feature_media
            source_path.write_bytes(archive.read(source_member))
            optimise_image(source_path, ASSET_DIR / article.config.feature_filename)

        clean_white_coats = {
            "postsportraits1.png": "image11.jpg",
            "postsportraits2.png": "image12.jpg",
        }
        prepared_portraits: set[str] = set()
        for article in articles:
            for source_name, destination_name in (
                (article.config.portrait_source, article.config.portrait_filename),
                (article.config.author_portrait_source, article.config.author_portrait_filename),
            ):
                if destination_name in prepared_portraits:
                    continue
                prepared_portraits.add(destination_name)

                embedded_name = clean_white_coats.get(source_name)
                if embedded_name:
                    source = temporary_root / embedded_name
                    source.write_bytes(archive.read(f"word/media/{embedded_name}"))
                    remove_checkerboard = False
                else:
                    source = ROOT / "assets" / "posts" / source_name
                    if not source.is_file():
                        raise SystemExit(f"Missing supplied Journal portrait: {source.relative_to(ROOT)}")
                    match = re.fullmatch(r"postsportraits(\d+)\.png", source_name)
                    remove_checkerboard = bool(match and 3 <= int(match.group(1)) <= 19)

                optimise_portrait(
                    source,
                    ASSET_DIR / destination_name,
                    temporary_root,
                    remove_checkerboard=remove_checkerboard,
                )


def validate_configuration(articles: Sequence[Article]) -> None:
    if len(ARTICLE_CONFIGS) != 10 or len(articles) != 10:
        raise SystemExit("The Journal must contain exactly ten configured and parsed articles.")
    numbers = [article.config.number for article in articles]
    if numbers != list(range(1, 11)):
        raise SystemExit(f"Expected article numbers 1 through 10; found {numbers}.")
    if sorted(EDITORIAL_ORDER) != list(range(1, 11)):
        raise SystemExit("EDITORIAL_ORDER must contain every article exactly once.")
    slugs = [article.config.slug for article in articles]
    if len(set(slugs)) != 10:
        raise SystemExit("Article slugs must be unique.")
    descriptions = [article.config.meta_description for article in articles]
    if len(set(descriptions)) != 10:
        raise SystemExit("Article meta descriptions must be unique.")
    asset_names = [
        filename
        for article in articles
        for filename in (
            article.config.feature_filename,
            article.config.portrait_filename,
            article.config.author_portrait_filename,
        )
    ]
    if len(asset_names) != 30 or len(set(asset_names)) != 30:
        raise SystemExit("Journal delivery assets must contain 30 unique configured filenames.")
    too_long = [(article.config.number, len(article.config.meta_description)) for article in articles if len(article.config.meta_description) > 165]
    if too_long:
        raise SystemExit(f"Meta descriptions exceed 165 characters: {too_long}")
    category_numbers = [number for _, _, numbers in CATEGORIES for number in numbers]
    if sorted(category_numbers) != list(range(1, 11)):
        raise SystemExit("Category indexes must represent every article exactly once.")
    for article in articles:
        if article.config.number in article.config.related or len(set(article.config.related)) != 3:
            raise SystemExit(f"Article {article.config.number:02d} related reading must contain three distinct other articles.")


def expected_outputs(articles: Sequence[Article]) -> dict[Path, str]:
    outputs = {ROOT / "journal.html": render_journal_index(articles)}
    outputs.update({ARTICLE_DIR / f"{article.config.slug}.html": render_article_page(article, articles) for article in articles})
    return outputs


def write_outputs(outputs: dict[Path, str]) -> None:
    ARTICLE_DIR.mkdir(parents=True, exist_ok=True)
    expected_article_files = {path for path in outputs if path.parent == ARTICLE_DIR}
    for existing in ARTICLE_DIR.glob("*.html"):
        if existing not in expected_article_files:
            raise SystemExit(f"Unexpected article page already exists and was not removed: {existing.relative_to(ROOT)}")
    for path, content in outputs.items():
        path.write_text(content, encoding="utf-8", newline="\n")


def check_outputs(outputs: dict[Path, str], articles: Sequence[Article]) -> int:
    failures: list[str] = []
    for path, expected in outputs.items():
        if not path.is_file():
            failures.append(f"missing generated page: {path.relative_to(ROOT)}")
        elif path.read_text(encoding="utf-8") != expected:
            failures.append(f"stale generated page: {path.relative_to(ROOT)}")
    actual_articles = sorted(ARTICLE_DIR.glob("*.html")) if ARTICLE_DIR.is_dir() else []
    if len(actual_articles) != 10:
        failures.append(f"expected exactly 10 article files; found {len(actual_articles)}")
    expected_assets = {
        filename
        for article in articles
        for filename in (
            article.config.feature_filename,
            article.config.portrait_filename,
            article.config.author_portrait_filename,
        )
    }
    actual_assets = {path.name for path in ASSET_DIR.iterdir() if path.is_file()} if ASSET_DIR.is_dir() else set()
    if actual_assets != expected_assets:
        missing = sorted(expected_assets - actual_assets)
        extra = sorted(actual_assets - expected_assets)
        failures.append(f"optimised asset set differs; missing={missing}, extra={extra}")
    if failures:
        print("Journal build check failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("Journal build is current: 1 publication index, 10 complete articles, and 30 optimised post images.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write the Journal index and ten article pages.")
    parser.add_argument("--assets", action="store_true", help="Extract and optimise the supplied post imagery.")
    parser.add_argument("--check", action="store_true", help="Verify generated pages and assets are current without writing.")
    args = parser.parse_args()
    if not (args.write or args.check):
        parser.error("choose --write, --check, or both")

    articles = parse_source()
    validate_configuration(articles)
    if args.assets:
        prepare_assets(articles)
        print(f"Prepared 30 optimised Journal images in {ASSET_DIR.relative_to(ROOT)}.")
    outputs = expected_outputs(articles)
    if args.write:
        write_outputs(outputs)
        print("Wrote journal.html and exactly 10 complete Journal article pages.")
    if args.check:
        return check_outputs(outputs, articles)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
