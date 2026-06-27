#!/usr/bin/env python3
"""Polish the Sofiati rebuild with shorter copy, better photo hierarchy, and SEO alt text."""

from __future__ import annotations

import json
import re
from datetime import date
from html import escape
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS = sorted(path for path in (ROOT / "concepts").iterdir() if path.is_dir() and re.match(r"^\d{2}-", path.name))
MANIFEST_PATH = ROOT / "assets" / "brand-photos" / "image-manifest.json"
MANIFEST = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
ENTRIES = {entry["id"]: entry for entry in MANIFEST["entries"]}

CSS_START = "/* SOFIATI EDITORIAL POLISH START */"
CSS_END = "/* SOFIATI EDITORIAL POLISH END */"

MAJOR_PAGES = ["index", "about", "care", "skin", "laser", "results", "consultation", "contact", "journal"]
PHOTO_CATEGORIES = {"hero", "about", "care", "skin", "laser", "results", "consultation", "contact", "journal"}

FAMILIES = [
    ("sage-cutout-editorial", "Sage Editorial", "sage panels, soft cutout accents, and calm clinical trust"),
    ("deep-green-luxury", "Green Luxury", "deep green contrast, ivory relief, and restrained gold"),
    ("ivory-oval-portrait", "Ivory Portrait", "oval portraits, cream space, and gentle human warmth"),
    ("botanical-collage", "Botanical Collage", "layered photos, botanical rhythm, and soft movement"),
    ("minimal-gold-clinic", "Gold Clinic", "precise spacing, gold lines, and quiet authority"),
    ("warm-consultation-led", "Consultation Warmth", "approachable contact blocks and reassuring portraits"),
    ("magazine-asymmetry", "Magazine Flow", "asymmetric editorial panels and varied photo scale"),
    ("structured-clinical", "Clinical Structure", "orderly process notes and confident spacing"),
    ("airy-skincare", "Airy Skin", "cream fields, window-lit photos, and softer pacing"),
    ("dark-muted-premium", "Muted Premium", "dark green bands, high contrast, and polished restraint"),
]

CUTOUT_PRIMARY_IDS = [
    "franciele-sofiati-04-studio-full-poised",
    "franciele-sofiati-05-studio-full-direct",
    "franciele-sofiati-08-studio-front-composed",
    "franciele-sofiati-10-studio-close-smile",
    "franciele-sofiati-12-studio-close-composed",
    "franciele-sofiati-13-balcony-orange-soft-smile",
    "franciele-sofiati-15-balcony-orange-direct",
    "franciele-sofiati-16-balcony-orange-tilt-smile",
    "franciele-sofiati-17-balcony-orange-laughing",
    "franciele-sofiati-19-ivory-room-standing-direct",
    "franciele-sofiati-20-ivory-room-standing-calm",
    "franciele-sofiati-22-ivory-room-arms-crossed",
    "franciele-sofiati-23-ivory-room-arms-crossed-close",
]

CUTOUT_SUPPORT_IDS = [
    entry["id"]
    for entry in MANIFEST["entries"]
    if entry.get("transparent_alpha_verified") and entry["id"] not in CUTOUT_PRIMARY_IDS
]


def concept_number(path: Path) -> int:
    return int(path.name.split("-", 1)[0])


def concept_label(path: Path) -> str:
    return path.name.split("-", 1)[1].replace("-", " ").title()


def pick(items: list[str], seed: int, salt: int) -> str:
    return items[(seed * 11 + salt * 5) % len(items)]


def rel(path: str) -> str:
    return "../../" + path


def dims(path: str) -> tuple[int, int]:
    with Image.open(ROOT / path) as image:
        return image.size


def category_ids(category: str) -> list[str]:
    ids = [entry["id"] for entry in MANIFEST["entries"] if category in entry.get("category_files", {})]
    return ids or [entry["id"] for entry in MANIFEST["entries"]]


def photo(image_id: str, kind: str, category: str | None = None) -> dict[str, str | int]:
    entry = ENTRIES[image_id]
    if kind == "cutout":
        path = entry["transparent_webp"]
    elif category:
        path = entry.get("category_files", {}).get(category) or entry["optimized_file"]
    else:
        path = entry["optimized_file"]
    width, height = dims(path)
    return {"id": image_id, "path": rel(path), "width": width, "height": height}


PAGE_SCHEMA = {
    "index": {
        "noun": "Care",
        "prefix": "Personalized aesthetic care",
        "meta": "Premium aesthetic care with Franciele Sofiati, using calm evaluation, realistic planning, and real brand photography.",
        "eyebrow": "Cuidado, confiança, segurança, naturalidade",
        "intro": "Personalized care begins with listening, evaluation, and realistic expectations.",
        "primary": ("Consultation", "consultation.html"),
        "secondary": ("About", "about.html"),
        "sections": [
            ("Real Care", "A human first impression before any protocol.", ["Franciele on page", "Clear services", "No borrowed proof"], "about.html", "Profile", "about"),
            ("Care Map", "A simple route through skin, laser, and planning.", ["Assess", "Explain", "Guide"], "care.html", "Care", "care"),
            ("Calm Start", "The next step stays conversational and discreet.", ["Questions", "Comfort", "Timing"], "consultation.html", "Start", "consultation"),
        ],
        "cards": [("Listen", "Goals and routine."), ("Assess", "Skin context."), ("Guide", "Clear next step.")],
    },
    "about": {
        "noun": "Profile",
        "prefix": "About Franciele Sofiati",
        "meta": "A concise professional profile for Franciele Sofiati with calm, real-photo trust and grounded aesthetic-care language.",
        "eyebrow": "Professional presence",
        "intro": "A calm profile should feel human, precise, and credible.",
        "primary": ("Consultation", "consultation.html"),
        "secondary": ("Values", "values.html"),
        "sections": [
            ("Real Presence", "Portraits support trust without exaggeration.", ["Professional tone", "Warm image", "Clear boundaries"], "consultation.html", "Consult", "about"),
            ("Care Values", "The brand stays anchored in four care words.", ["Cuidado", "Confiança", "Segurança"], "care.html", "Values", "profile"),
            ("Quiet Trust", "Confidence comes from clarity, not dramatic claims.", ["Private choices", "Natural goals", "Evaluation first"], "results.html", "Results", "results"),
        ],
        "cards": [("Cuidado", "Listen first."), ("Confianca", "Explain clearly."), ("Seguranca", "Evaluate carefully."), ("Naturalidade", "Plan softly.")],
    },
    "care": {
        "noun": "Planning",
        "prefix": "Personalized care",
        "meta": "Personalized aesthetic-care planning with Franciele Sofiati, focused on suitability, comfort, and responsible guidance.",
        "eyebrow": "Evaluation first",
        "intro": "Care becomes better when goals, history, and comfort are understood.",
        "primary": ("Discuss Care", "consultation.html"),
        "secondary": ("Skin", "skin.html"),
        "sections": [
            ("First Listen", "The conversation sets the clinical context.", ["Goals", "Routine", "Comfort"], "consultation.html", "Talk", "consultation"),
            ("Suitability", "Planning considers whether a path is appropriate.", ["Skin context", "Timing", "Aftercare"], "results.html", "Expectations", "care"),
            ("Support", "The page stays warm without becoming vague.", ["Privacy", "Clarity", "Follow-up"], "contact.html", "Contact", "contact"),
        ],
        "cards": [("Goals", "What matters."), ("Routine", "Daily context."), ("Timing", "Real schedule."), ("Aftercare", "Ongoing support.")],
    },
    "skin": {
        "noun": "Skin",
        "prefix": "Skin guidance",
        "meta": "Refined skin guidance with Franciele Sofiati for routine, sensitivity, texture, and consultation-ready questions.",
        "eyebrow": "Skin quality",
        "intro": "Skin planning should be practical, soft, and specific to the person.",
        "primary": ("Skin Plan", "consultation.html"),
        "secondary": ("Care", "care.html"),
        "sections": [
            ("Skin History", "Routine and sensitivity change the conversation.", ["Texture", "Spots", "Sensitivity"], "journal.html", "Read", "skin"),
            ("Daily Rhythm", "Good advice has to fit real life.", ["Products", "Sun care", "Comfort"], "consultation.html", "Guide", "journal"),
            ("Soft Clarity", "A refined page can still feel clinical.", ["Observation", "Restraint", "Planning"], "contact.html", "Ask", "about"),
        ],
        "cards": [("Texture", "Describe feel."), ("Tone", "Discuss carefully."), ("Sensitivity", "Respect history."), ("Routine", "Keep realistic.")],
    },
    "laser": {
        "noun": "Laser",
        "prefix": "Laser guidance",
        "meta": "Laser guidance with Franciele Sofiati, focused on skin suitability, preparation, comfort, and realistic expectations.",
        "eyebrow": "Clinical warmth",
        "intro": "Laser decisions need suitability, preparation, and careful expectation-setting.",
        "primary": ("Evaluate", "consultation.html"),
        "secondary": ("Skin", "skin.html"),
        "sections": [
            ("Indication", "Technology only helps when it fits the case.", ["Phototype", "Sensitivity", "Goal"], "consultation.html", "Evaluate", "laser"),
            ("Preparation", "The plan should discuss timing and skin history.", ["Recent sun", "Routine", "Comfort"], "results.html", "Expect", "care"),
            ("Aftercare", "Follow-up language keeps precision human.", ["Guidance", "Recovery", "Questions"], "care.html", "Care", "about"),
        ],
        "cards": [("Fit", "Is it suitable?"), ("Prep", "What changes first?"), ("Comfort", "What to expect?"), ("Rhythm", "How to plan?")],
    },
    "results": {
        "noun": "Results",
        "prefix": "Responsible results",
        "meta": "Responsible aesthetic result guidance with Franciele Sofiati, centered on planning, privacy, and realistic expectations.",
        "eyebrow": "Realistic expectations",
        "intro": "Result conversations should be careful, private, and evaluation-led.",
        "primary": ("Clarify", "consultation.html"),
        "secondary": ("Values", "about.html"),
        "sections": [
            ("No Hype", "The page avoids borrowed proof and dramatic claims.", ["No fake outcomes", "No guarantees", "No pressure"], "consultation.html", "Talk", "results"),
            ("Before Care", "Expectations are shaped before treatment choices.", ["Suitability", "Protocol", "Aftercare"], "care.html", "Care", "laser"),
            ("Natural Goals", "Naturalidade means restraint and clear boundaries.", ["Private", "Measured", "Individual"], "contact.html", "Contact", "profile"),
        ],
        "cards": [("Before", "Clarify goals."), ("During", "Stay suitable."), ("After", "Respect response.")],
    },
    "consultation": {
        "noun": "Consultation",
        "prefix": "Consultation",
        "meta": "A warm consultation path with Franciele Sofiati for goals, skin context, comfort, timing, and professional evaluation.",
        "eyebrow": "First conversation",
        "intro": "The best next step starts with a calm, useful conversation.",
        "primary": ("WhatsApp", "https://wa.me/5543991043536"),
        "secondary": ("Contact", "contact.html"),
        "sections": [
            ("Questions", "A consultation gives shape to what matters.", ["Goals", "Concerns", "Timing"], "care.html", "Care", "consultation"),
            ("Evaluation", "Decisions stay connected to professional assessment.", ["Skin context", "Comfort", "Suitability"], "results.html", "Results", "about"),
            ("Next Step", "Contact routes stay simple and respectful.", ["WhatsApp", "Email", "Instagram"], "contact.html", "Contact", "contact"),
        ],
        "cards": [("Bring", "Questions."), ("Discuss", "Context."), ("Leave", "Clarity.")],
    },
    "contact": {
        "noun": "Contact",
        "prefix": "Contact",
        "meta": "Contact Franciele Sofiati for aesthetic-care consultation requests through clear, respectful public communication routes.",
        "eyebrow": "Public routes",
        "intro": "Contact should feel simple, respectful, and easy to begin.",
        "primary": ("WhatsApp", "https://wa.me/5543991043536"),
        "secondary": ("Consultation", "consultation.html"),
        "sections": [
            ("Start Simple", "A first message can be calm and direct.", ["Question", "Goal", "Timing"], "consultation.html", "Consult", "contact"),
            ("Clear Routes", "Public channels are presented without pressure.", ["WhatsApp", "Email", "Instagram"], "mailto:sofiatimendonca@gmail.com", "Email", "profile"),
            ("Care Path", "A professional conversation clarifies fit.", ["Listen", "Assess", "Guide"], "care.html", "Care", "care"),
        ],
        "cards": [("WhatsApp", "(43) 9 9104-3536"), ("Email", "sofiatimendonca@gmail.com"), ("Instagram", "@fransofiati_biomedica")],
    },
    "journal": {
        "noun": "Journal",
        "prefix": "Journal",
        "meta": "Concise Sofiati journal notes for skin, laser, care planning, aftercare, and better consultation questions.",
        "eyebrow": "Editorial notes",
        "intro": "Short notes help clients ask clearer, safer questions.",
        "primary": ("Skin Notes", "skin.html"),
        "secondary": ("Consultation", "consultation.html"),
        "sections": [
            ("Skin Notes", "Education starts with observation.", ["Routine", "Texture", "Sensitivity"], "skin.html", "Skin", "journal"),
            ("Laser Notes", "Preparation and suitability matter.", ["Timing", "Phototype", "Aftercare"], "laser.html", "Laser", "laser"),
            ("Care Notes", "Good content protects expectations.", ["Values", "Privacy", "Restraint"], "care.html", "Care", "about"),
        ],
        "cards": [("Skin", "What to notice."), ("Laser", "What to ask."), ("Aftercare", "What continues."), ("Expectations", "What stays realistic.")],
    },
}

SECONDARY_PAGE_HEADINGS = {
    "404": ("Page Note", "Back To Care"),
    "accessibility": ("Accessibility", "Access Support"),
    "blog": ("Journal", "Editorial Notes"),
    "cookies": ("Cookies", "Cookie Choice"),
    "faq": ("FAQ", "Clear Answers"),
    "legal": ("Legal", "Care Boundaries"),
    "mission": ("Mission", "Calm Care"),
    "privacy": ("Privacy", "Data Use"),
    "sitemap": ("Sitemap", "Site Map"),
    "testimonials": ("Trust", "Care Notes"),
    "values": ("Values", "Care Values"),
}


def alt_text(image_id: str, page: str, role: str) -> str:
    entry = ENTRIES.get(image_id, {})
    setting = "studio"
    if "balcony" in image_id:
        setting = "warm editorial"
    elif "ivory-room" in image_id:
        setting = "ivory consultation"
    if role in {"hero-main", "support-photo"}:
        return f"Franciele Sofiati in a {setting} portrait for {PAGE_SCHEMA.get(page, PAGE_SCHEMA['index'])['prefix'].lower()}"
    if "consult" in role or page == "consultation":
        return "Franciele Sofiati in a professional consultation portrait for aesthetic care"
    if page == "skin":
        return "Franciele Sofiati portrait for refined skin care guidance"
    if page == "laser":
        return "Franciele Sofiati portrait for laser suitability guidance"
    if page == "contact":
        return "Franciele Sofiati portrait for contact and consultation requests"
    if page == "journal":
        return "Editorial portrait of Franciele Sofiati for aesthetic education notes"
    return entry.get("alt_text") or "Professional portrait of Franciele Sofiati for aesthetic care"


def img(photo_data: dict[str, str | int], cls: str, page: str, role: str, lazy: bool = True) -> str:
    loading = "lazy" if lazy else "eager"
    alt = escape(alt_text(str(photo_data["id"]), page, role), quote=True)
    return (
        f'<img class="{cls}" src="{photo_data["path"]}" alt="{alt}" '
        f'width="{photo_data["width"]}" height="{photo_data["height"]}" loading="{loading}" '
        f'decoding="async" data-brand-photo="{photo_data["id"]}" data-photo-role="{role}">'
    )


def photo_set(idx: int, page: str) -> dict[str, dict[str, str | int]]:
    category = "hero" if page == "index" else page if page in {"about", "care", "skin", "laser", "results", "consultation", "contact", "journal"} else "about"
    return {
        "hero": photo(pick(category_ids(category), idx, 1), "opaque", category),
        "support": photo(pick(category_ids("about"), idx, 2), "opaque", "about"),
        "story": photo(pick(category_ids(category), idx, 3), "opaque", category),
        "journal": photo(pick(category_ids("journal"), idx, 4), "opaque", "journal"),
        "cutout": photo(pick(CUTOUT_PRIMARY_IDS, idx, 5), "cutout"),
        "accent": photo(pick(CUTOUT_PRIMARY_IDS, idx, 6), "cutout"),
        "support_cutout": photo(pick(CUTOUT_SUPPORT_IDS, idx, 7), "cutout"),
    }


def section_html(item: tuple[str, str, list[str], str, str, str], photos: dict[str, dict[str, str | int]], page: str, idx: int, seed: int) -> str:
    heading, copy, bullets, href, link, photo_role = item
    tone = ["sage-section", "ivory-section", "deep-green-section"][idx % 3]
    variant = ["story-section--photo-left", "story-section--note", "story-section--process"][idx % 3]
    category = photo_role if photo_role in PHOTO_CATEGORIES else page
    story_photo = photo(pick(category_ids(category), seed, idx + 8), "opaque", category)
    accent_photo = photo(pick(CUTOUT_PRIMARY_IDS, seed, idx + 13), "cutout")
    bullet_html = "".join(f"<li>{escape(bullet)}</li>" for bullet in bullets)
    return f"""
  <section class="story-section editorial-section {tone} {variant}" data-story-step="{idx + 3}">
    <figure class="story-photo photo-frame photo-frame--editorial">
      {img(story_photo, "doctor-portrait doctor-portrait--about", page, "story-photo")}
      {img(accent_photo, "photo-cutout photo-cutout--accent", page, "story-accent")}
    </figure>
    <div class="story-section__copy">
      <p class="eyebrow">{escape(photo_role.title())}</p>
      <h2>{escape(heading)}</h2>
      <p>{escape(copy)}</p>
      <ul class="story-points">{bullet_html}</ul>
      <a class="button button-soft" href="{href}">{escape(link)}</a>
    </div>
  </section>"""


def cards_html(cards: list[tuple[str, str]]) -> str:
    return "\n".join(f'<article class="photo-card"><h3>{escape(title)}</h3><p>{escape(copy)}</p></article>' for title, copy in cards)


def page_data(concept: Path, page: str, family: tuple[str, str, str]) -> dict[str, object]:
    schema = PAGE_SCHEMA[page]
    label = concept_label(concept)
    h1 = f"{label} {schema['noun']}"
    if len(h1.split()) > 3:
        h1 = schema["noun"]
    return {
        **schema,
        "h1": h1,
        "title": f"{schema['prefix']} | {label} | Franciele Sofiati",
        "description": f"{schema['meta']} This {label} concept uses {family[2]}.",
        "family_label": family[1],
        "family_note": family[2],
    }


def main_html(concept: Path, page: str, family: tuple[str, str, str]) -> str:
    idx = concept_number(concept)
    data = page_data(concept, page, family)
    photos = photo_set(idx, page)
    sections = list(data["sections"])
    rotate = (idx + len(page)) % len(sections)
    sections = sections[rotate:] + sections[:rotate]
    story = "\n".join(section_html(item, photos, page, i, idx) for i, item in enumerate(sections))
    cards = list(data["cards"])
    rotate_cards = idx % len(cards)
    cards = cards[rotate_cards:] + cards[:rotate_cards]
    return f"""
<main id="main" class="pilot-page editorial-page editorial-page-{page}" data-pilot-page="{page}" data-story-flow="promise-trust-context-process-reassurance-contact">
  <section class="real-photo-hero brand-colour-band editorial-hero" data-story-step="1">
    <div class="real-photo-hero__copy">
      <p class="eyebrow">{escape(data["eyebrow"])} · {escape(data["family_label"])}</p>
      <h1>{escape(data["h1"])}</h1>
      <p>{escape(data["intro"])}</p>
      <ul class="hero-points">
        <li>Evaluation first</li>
        <li>Natural goals</li>
        <li>Discreet guidance</li>
      </ul>
      <div class="hero-actions">
        <a class="button button-primary" href="{data["primary"][1]}">{escape(data["primary"][0])}</a>
        <a class="button button-soft" href="{data["secondary"][1]}">{escape(data["secondary"][0])}</a>
      </div>
    </div>
    <div class="real-photo-hero__visual photo-panel editorial-hero__visual">
      <figure class="hero-frame photo-frame photo-frame--sage">
        {img(photos["hero"], "doctor-portrait doctor-portrait--hero", page, "hero-main", lazy=False)}
      </figure>
      <figure class="hero-cutout-card" aria-label="Franciele Sofiati brand portrait">
        {img(photos["cutout"], "photo-cutout photo-cutout--hero photo-cutout--accent", page, "hero-accent", lazy=False)}
      </figure>
    </div>
  </section>

  <section class="pilot-values story-break editorial-values" aria-label="Sofiati values" data-story-step="2">
    <p class="eyebrow">Sofiati method</p>
    <div class="pilot-values__grid">
      <article><h2>Cuidado</h2><p>Listen first.</p></article>
      <article><h2>Confiança</h2><p>Explain clearly.</p></article>
      <article><h2>Segurança</h2><p>Assess carefully.</p></article>
      <article><h2>Naturalidade</h2><p>Plan softly.</p></article>
    </div>
  </section>

  {story}

  <section class="editorial-section consultation-photo-block deep-green-section editorial-process" data-story-step="6">
    <div>
      <p class="eyebrow">Process</p>
      <h2>Care Path</h2>
      <p>Short, calm steps keep the experience understandable.</p>
      <ul class="story-points">
        <li>Listen</li>
        <li>Evaluate</li>
        <li>Guide</li>
      </ul>
    </div>
    <div class="photo-collage">
      {img(photos["accent"], "photo-cutout photo-cutout--cta doctor-portrait doctor-portrait--consultation", page, "consultation-accent")}
      {img(photos["support"], "photo-card__image doctor-portrait", page, "support-photo")}
    </div>
  </section>

  <section class="pilot-card-band ivory-section editorial-card-band" data-story-step="7">
    <div class="section-heading">
      <p class="eyebrow">Details</p>
      <h2>Useful Notes</h2>
    </div>
    <div class="pilot-card-grid">
      {cards_html(cards)}
    </div>
  </section>

  <section class="pilot-final-cta brand-colour-band editorial-final" data-story-step="8">
    <div>
      <p class="eyebrow">Consultation</p>
      <h2>Start Calmly</h2>
      <p>Bring one question. Leave with a clearer next step.</p>
    </div>
    <a class="button button-primary" href="consultation.html">Consultation</a>
    <a class="button button-soft" href="contact.html">Contact</a>
  </section>

  <section class="contact-card-section pilot-contact-section" data-section-type="contact">
    <div data-partial-mount="contact-card"></div>
  </section>
</main>"""


def add_body_state(tag: str, page: str, data: dict[str, object], family_slug: str, idx: int) -> str:
    match = re.search(r'class="([^"]*)"', tag)
    classes = match.group(1).split() if match else []
    for cls in ("sf-pilot-rebuild", "sf-editorial-polish", "sf-global-rebuild", f"design-family-{family_slug}"):
        if cls not in classes:
            classes.append(cls)
    classes = [cls for cls in classes if not (cls.startswith("design-family-") and cls != f"design-family-{family_slug}")]
    if match:
        tag = tag[: match.start(1)] + " ".join(classes) + tag[match.end(1) :]
    else:
        tag = tag.replace("<body", f'<body class="{" ".join(classes)}"', 1)
    attrs = {
        "data-design-family": family_slug,
        "data-pilot-page": page,
        "data-page-title": str(data["title"]),
        "data-page-description": str(data["description"]),
        "style": (
            f"--concept-hero-radius:{['24px 96px 24px 24px','120px 24px 120px 24px','180px 180px 18px 18px','16px 120px 16px 120px','18px'][idx % 5]};"
            f"--concept-card-radius:{[6,18,28,42,10][idx % 5]}px;"
            f"--concept-photo-scale:{[0.9,0.94,0.98,0.92,0.88][idx % 5]};"
        ),
    }
    for attr, value in attrs.items():
        if f"{attr}=" in tag:
            tag = re.sub(rf'{attr}="[^"]*"', f'{attr}="{escape(value, quote=True)}"', tag, count=1)
        else:
            tag = tag[:-1] + f' {attr}="{escape(value, quote=True)}">'
    return tag


def update_major_page(concept: Path, page: str, family: tuple[str, str, str]) -> None:
    path = concept / f"{page}.html"
    html = path.read_text(encoding="utf-8")
    idx = concept_number(concept)
    data = page_data(concept, page, family)
    html = re.sub(r"<title>.*?</title>", f"<title>{escape(data['title'])}</title>", html, count=1, flags=re.S)
    for pattern, value in [
        (r'<meta name="description" content="[^"]*">', data["description"]),
        (r'<meta property="og:title" content="[^"]*">', data["title"]),
        (r'<meta property="og:description" content="[^"]*">', data["description"]),
        (r'<meta name="twitter:title" content="[^"]*">', data["title"]),
        (r'<meta name="twitter:description" content="[^"]*">', data["description"]),
    ]:
        replacement = pattern.split(" content=")[0] + f' content="{escape(str(value), quote=True)}">'
        html = re.sub(pattern, replacement, html, count=1)
    html = re.sub(r"<body([^>]*)>", lambda m: add_body_state(m.group(0), page, data, family[0], idx), html, count=1)
    html = re.sub(r'<main id="main".*?</main>', main_html(concept, page, family), html, count=1, flags=re.S)
    path.write_text(html, encoding="utf-8")


POLISH_CSS = f"""
{CSS_START}
.sf-editorial-polish {{
  --sofiati-sage: #A2AE9F;
  --sofiati-ivory: #F3EFE5;
  --sofiati-green: #798A80;
  --sofiati-gold: #C7A66A;
  --sofiati-cream: #F8F4EA;
  --sofiati-deep: #2f3d35;
  background:
    radial-gradient(circle at 8% 18%, color-mix(in srgb,var(--sofiati-sage) 18%,transparent), transparent 30%),
    linear-gradient(180deg,var(--sofiati-cream),var(--sofiati-ivory));
}}
.sf-editorial-polish .editorial-page {{
  overflow: hidden;
}}
.sf-editorial-polish .real-photo-hero,
.sf-editorial-polish .editorial-section,
.sf-editorial-polish .pilot-values,
.sf-editorial-polish .pilot-card-band,
.sf-editorial-polish .pilot-final-cta {{
  width: min(1160px, calc(100% - 36px));
}}
.sf-editorial-polish .editorial-hero {{
  min-height: min(760px, calc(100vh - 76px));
  grid-template-columns: minmax(0,.82fr) minmax(360px,.78fr);
  gap: clamp(24px,5vw,76px);
  padding: clamp(44px,7vw,96px);
  border-radius: var(--concept-hero-radius, 24px 96px 24px 24px);
}}
.sf-editorial-polish .real-photo-hero__copy {{
  gap: 16px;
  max-width: 560px;
}}
.sf-editorial-polish .real-photo-hero__copy h1 {{
  font-size: clamp(3.4rem,9vw,8.4rem);
  line-height: .88;
  max-width: 6ch;
}}
.sf-editorial-polish .real-photo-hero__copy p:not(.eyebrow) {{
  max-width: 34ch;
  font-size: clamp(1rem,1.25vw,1.14rem);
}}
.hero-points,
.story-points {{
  list-style: none;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 0;
  margin: 0;
}}
.hero-points li,
.story-points li {{
  border: 1px solid color-mix(in srgb,currentColor 22%,transparent);
  background: color-mix(in srgb,currentColor 7%,transparent);
  border-radius: 999px;
  padding: 7px 10px;
  font-size: .78rem;
  font-weight: 800;
}}
.brand-colour-band .hero-points li,
.deep-green-section .story-points li,
.deep-green-section .hero-points li {{
  color: rgba(255,255,255,.9);
  border-color: rgba(255,255,255,.24);
  background: rgba(255,255,255,.1);
}}
.ivory-section .story-points li,
.sage-section .story-points li {{
  color: var(--sofiati-deep);
  border-color: color-mix(in srgb,var(--sofiati-gold) 24%,transparent);
  background: rgba(255,255,255,.58);
}}
.editorial-hero__visual {{
  min-height: clamp(420px,48vw,650px);
  place-items: center;
}}
.hero-frame {{
  position: relative;
  z-index: 1;
  width: min(78%,430px);
  aspect-ratio: 4 / 5;
  overflow: hidden;
  border-radius: 999px 999px 18px 18px;
  margin: 0;
  background: var(--sofiati-ivory);
  box-shadow: 0 28px 80px rgba(16,22,18,.2);
}}
.hero-frame img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}}
.hero-cutout-card {{
  position: absolute;
  right: 0;
  bottom: 0;
  z-index: 2;
  width: min(42%,220px);
  min-height: 210px;
  display: grid;
  align-items: end;
  justify-items: center;
  margin: 0;
  border-radius: 999px 999px 18px 18px;
  background: linear-gradient(145deg,color-mix(in srgb,var(--sofiati-sage) 54%,white),var(--sofiati-ivory));
  border: 1px solid color-mix(in srgb,var(--sofiati-gold) 30%,transparent);
  overflow: hidden;
  box-shadow: 0 18px 45px rgba(16,22,18,.18);
}}
.sf-editorial-polish .photo-cutout--hero {{
  max-height: 270px;
  width: min(94%,190px);
  transform: scale(var(--concept-photo-scale,.94));
  filter: drop-shadow(0 18px 24px rgba(16,22,18,.18));
}}
.editorial-values {{
  margin-top: clamp(18px,4vw,52px);
  padding: clamp(22px,4vw,48px);
  background: linear-gradient(135deg,var(--sofiati-ivory),color-mix(in srgb,var(--sofiati-sage) 22%,white));
  border-radius: 18px;
}}
.editorial-values .pilot-values__grid {{
  gap: 10px;
}}
.editorial-values article,
.sf-editorial-polish .photo-card {{
  min-height: auto;
  padding: 18px;
  border-radius: var(--concept-card-radius,10px);
}}
.editorial-values h2,
.sf-editorial-polish .photo-card h3 {{
  font-size: clamp(1.2rem,2vw,1.75rem);
}}
.sf-editorial-polish .story-section {{
  grid-template-columns: minmax(300px,.72fr) minmax(0,.9fr);
  gap: clamp(22px,4vw,58px);
  padding: clamp(30px,5.5vw,76px);
  border-radius: 18px 72px 18px 18px;
}}
.sf-editorial-polish .story-section--note {{
  grid-template-columns: minmax(0,.9fr) minmax(300px,.72fr);
  border-radius: 72px 18px 18px 18px;
}}
.sf-editorial-polish .story-section--note .story-photo {{
  order: 2;
}}
.story-photo {{
  position: relative;
  min-height: clamp(300px,36vw,500px);
  margin: 0;
  overflow: hidden;
  border-radius: 999px 999px 18px 18px;
  background: var(--sofiati-ivory);
}}
.story-photo > img:not(.photo-cutout) {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center top;
}}
.story-photo .photo-cutout--accent {{
  position: absolute;
  right: 8%;
  bottom: 0;
  width: min(34%,150px);
  max-height: 210px;
  padding-top: 22px;
  border-radius: 999px 999px 10px 10px;
  background: color-mix(in srgb,var(--sofiati-sage) 42%,white);
}}
.sf-editorial-polish .story-section__copy {{
  gap: 14px;
  max-width: 520px;
}}
.sf-editorial-polish .story-section__copy h2,
.sf-editorial-polish .consultation-photo-block h2,
.sf-editorial-polish .pilot-final-cta h2,
.sf-editorial-polish .section-heading h2 {{
  font-size: clamp(2rem,4.8vw,5.4rem);
  line-height: .9;
  max-width: 8ch;
}}
.sf-editorial-polish .story-section__copy p:not(.eyebrow),
.sf-editorial-polish .consultation-photo-block p,
.sf-editorial-polish .pilot-final-cta p {{
  max-width: 34ch;
}}
.editorial-process {{
  align-items: center;
  overflow: hidden;
}}
.editorial-process .photo-collage {{
  min-height: 360px;
}}
.editorial-process .photo-cutout--cta {{
  max-height: 360px;
  width: min(64%,300px);
}}
.editorial-card-band {{
  padding: clamp(28px,5vw,62px);
  border-radius: 72px 18px 72px 18px;
}}
.editorial-card-band .pilot-card-grid {{
  grid-template-columns: repeat(4,minmax(0,1fr));
}}
.editorial-final {{
  align-items: center;
  border-radius: 18px 18px 92px 18px;
}}
.design-family-deep-green-luxury.sf-editorial-polish .brand-colour-band,
.design-family-dark-muted-premium.sf-editorial-polish .brand-colour-band {{
  background: linear-gradient(135deg,#17231e,#46584d 58%,#23231f);
}}
.design-family-ivory-oval-portrait.sf-editorial-polish .brand-colour-band,
.design-family-airy-skincare.sf-editorial-polish .brand-colour-band {{
  background: linear-gradient(135deg,#F3EFE5,#A2AE9F);
  color: #2f3d35;
}}
.design-family-ivory-oval-portrait.sf-editorial-polish .real-photo-hero__copy p:not(.eyebrow),
.design-family-airy-skincare.sf-editorial-polish .real-photo-hero__copy p:not(.eyebrow) {{
  color: color-mix(in srgb,#2f3d35 74%,transparent);
}}
.design-family-botanical-collage.sf-editorial-polish .editorial-hero,
.design-family-magazine-asymmetry.sf-editorial-polish .editorial-hero {{
  grid-template-columns: minmax(360px,.78fr) minmax(0,.82fr);
}}
.design-family-botanical-collage.sf-editorial-polish .real-photo-hero__visual,
.design-family-magazine-asymmetry.sf-editorial-polish .real-photo-hero__visual {{
  order: -1;
}}
.design-family-structured-clinical.sf-editorial-polish .story-section,
.design-family-minimal-gold-clinic.sf-editorial-polish .story-section {{
  border-radius: 10px;
  box-shadow: inset 0 0 0 1px color-mix(in srgb,var(--sofiati-gold) 24%,transparent);
}}
@media(max-width: 980px) {{
  .sf-editorial-polish .editorial-hero,
  .sf-editorial-polish .story-section,
  .sf-editorial-polish .story-section--note,
  .sf-editorial-polish .consultation-photo-block {{
    grid-template-columns: 1fr;
  }}
  .sf-editorial-polish .story-section--note .story-photo,
  .design-family-botanical-collage.sf-editorial-polish .real-photo-hero__visual,
  .design-family-magazine-asymmetry.sf-editorial-polish .real-photo-hero__visual {{
    order: 0;
  }}
  .editorial-card-band .pilot-card-grid {{
    grid-template-columns: repeat(2,minmax(0,1fr));
  }}
}}
@media(max-width: 620px) {{
  .sf-editorial-polish .real-photo-hero,
  .sf-editorial-polish .editorial-section,
  .sf-editorial-polish .pilot-values,
  .sf-editorial-polish .pilot-card-band,
  .sf-editorial-polish .pilot-final-cta {{
    width: min(100% - 24px,420px);
  }}
  .sf-editorial-polish .editorial-hero {{
    padding: 24px 16px 28px;
    gap: 18px;
  }}
  .sf-editorial-polish .real-photo-hero__copy h1 {{
    font-size: clamp(2.9rem,15vw,4.6rem);
    max-width: 5.5ch;
  }}
  .hero-points li,
  .story-points li {{
    font-size: .72rem;
    padding: 6px 8px;
  }}
  .editorial-hero__visual {{
    min-height: 330px;
    order: -1;
  }}
  .hero-frame {{
    width: min(78%,280px);
  }}
  .hero-cutout-card {{
    width: min(38%,140px);
    min-height: 150px;
  }}
  .sf-editorial-polish .photo-cutout--hero {{
    max-height: 178px;
    width: min(94%,124px);
  }}
  .sf-editorial-polish .story-section,
  .sf-editorial-polish .consultation-photo-block,
  .sf-editorial-polish .pilot-card-band,
  .sf-editorial-polish .pilot-final-cta {{
    padding: 24px 16px;
  }}
  .story-photo {{
    min-height: 260px;
  }}
  .story-photo .photo-cutout--accent {{
    width: min(34%,118px);
    max-height: 160px;
  }}
  .sf-editorial-polish .story-section__copy h2,
  .sf-editorial-polish .consultation-photo-block h2,
  .sf-editorial-polish .pilot-final-cta h2,
  .sf-editorial-polish .section-heading h2 {{
    font-size: clamp(2rem,11vw,3.4rem);
  }}
  .editorial-card-band .pilot-card-grid {{
    grid-template-columns: 1fr;
  }}
  .page-contact .editorial-hero__visual {{
    min-height: 230px;
  }}
  .page-contact .hero-frame {{
    width: min(66%,220px);
  }}
  .page-contact .hero-cutout-card {{
    display: none;
  }}
}}
{CSS_END}
"""


def update_css(concept: Path) -> None:
    path = concept / "css" / "style.css"
    css = path.read_text(encoding="utf-8")
    css = re.sub(re.escape(CSS_START) + r".*?" + re.escape(CSS_END) + r"\n?", "", css, flags=re.S).rstrip()
    path.write_text(css + "\n\n" + POLISH_CSS + "\n", encoding="utf-8")


def short_words(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÿ0-9]+", text))


def replace_heading(match: re.Match[str], replacement: str, limit: int) -> str:
    attrs, text = match.group(1), re.sub(r"<.*?>", "", match.group(2)).strip()
    if short_words(text) <= limit:
        return match.group(0)
    return f"<{match.group(3)}{attrs}>{replacement}</{match.group(3)}>"


def polish_secondary_page(path: Path) -> None:
    page = path.stem
    if page in MAJOR_PAGES:
        return
    h1, h2 = SECONDARY_PAGE_HEADINGS.get(page, ("Care Note", "Useful Note"))
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"<h1([^>]*)>(.*?)</h1>", lambda m: f"<h1{m.group(1)}>{h1}</h1>", html, count=1, flags=re.S)
    html = re.sub(r"<(h2)([^>]*)>(.*?)</h2>", lambda m: f"<h2{m.group(2)}>{h2}</h2>" if short_words(re.sub(r"<.*?>", "", m.group(3))) > 5 else m.group(0), html, flags=re.S)
    html = re.sub(r"<(h3|h4|h5|h6)([^>]*)>(.*?)</\1>", lambda m: f"<{m.group(1)}{m.group(2)}>Care Note</{m.group(1)}>" if short_words(re.sub(r"<.*?>", "", m.group(3))) > 5 else m.group(0), html, flags=re.S)
    path.write_text(html, encoding="utf-8")


def update_img_alts(path: Path) -> None:
    page = path.stem
    html = path.read_text(encoding="utf-8")

    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        id_match = re.search(r'data-brand-photo="([^"]+)"', tag)
        if not id_match:
            return tag
        role_match = re.search(r'data-photo-role="([^"]+)"', tag)
        alt = escape(alt_text(id_match.group(1), page, role_match.group(1) if role_match else "photo"), quote=True)
        if re.search(r'alt="[^"]*"', tag):
            return re.sub(r'alt="[^"]*"', f'alt="{alt}"', tag, count=1)
        return tag.replace("<img", f'<img alt="{alt}"', 1)

    html = re.sub(r"<img\b[^>]*>", repl, html)
    path.write_text(html, encoding="utf-8")


def update_manifest() -> None:
    for entry in MANIFEST["entries"]:
        image_id = entry["id"]
        entry["alt_text"] = alt_text(image_id, "index", "manifest")
        entry["seo_alt_text"] = entry["alt_text"]
        entry["transparent_quality"] = "primary-accent" if image_id in CUTOUT_PRIMARY_IDS else "support-only"
        entry["transparent_usage_note"] = (
            "Use as a smaller layered accent over sage or ivory framing."
            if image_id in CUTOUT_PRIMARY_IDS
            else "Avoid large hero use; prefer opaque crops because foreground props or edge detail can read less cleanly."
        )
    MANIFEST["editorial_polish"] = {
        "updated_at": date.today().isoformat(),
        "heading_rule": "H1 targets 1-3 words; H2-H6 targets 1-5 words.",
        "photo_rule": "Opaque real-photo crops carry major image weight; transparent cutouts are used as smaller premium accents.",
        "alt_text_rule": "Alt text names Franciele Sofiati and page context without fake claims or keyword stuffing.",
    }
    MANIFEST_PATH.write_text(json.dumps(MANIFEST, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main() -> None:
    update_manifest()
    updated_pages = 0
    for concept in CONCEPTS:
        idx = concept_number(concept)
        family = FAMILIES[(idx - 1) // 5]
        for page in MAJOR_PAGES:
            update_major_page(concept, page, family)
            updated_pages += 1
        for html_path in concept.glob("*.html"):
            polish_secondary_page(html_path)
            update_img_alts(html_path)
        update_css(concept)
    print(json.dumps({"concepts": len(CONCEPTS), "major_pages_polished": updated_pages, "manifest": str(MANIFEST_PATH)}, indent=2))


if __name__ == "__main__":
    main()
