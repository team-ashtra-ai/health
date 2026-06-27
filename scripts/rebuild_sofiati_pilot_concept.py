#!/usr/bin/env python3
"""Rebuild 01-inspire as the premium real-photo pilot concept."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONCEPT = ROOT / "concepts" / "01-inspire"
MANIFEST = json.loads((ROOT / "assets" / "brand-photos" / "image-manifest.json").read_text(encoding="utf-8"))

CSS_START = "/* SOFIATI PILOT PREMIUM REBUILD START */"
CSS_END = "/* SOFIATI PILOT PREMIUM REBUILD END */"


def rel(path: str) -> str:
    return "../../" + path


def dims(path: str) -> tuple[int, int]:
    with Image.open(ROOT / path) as image:
        return image.size


ENTRIES = {entry["id"]: entry for entry in MANIFEST["entries"]}


def cutout(image_id: str) -> dict[str, str | int]:
    entry = ENTRIES[image_id]
    path = entry["transparent_webp"]
    width, height = dims(path)
    return {
        "path": rel(path),
        "alt": entry["alt_text"],
        "width": width,
        "height": height,
        "id": image_id,
    }


def opaque(image_id: str, category: str) -> dict[str, str | int]:
    entry = ENTRIES[image_id]
    path = entry["category_files"].get(category) or entry["optimized_file"]
    width, height = dims(path)
    return {
        "path": rel(path),
        "alt": entry["alt_text"],
        "width": width,
        "height": height,
        "id": image_id,
    }


PHOTOS = {
    "authority": cutout("franciele-sofiati-23-ivory-room-arms-crossed-close"),
    "warm": cutout("franciele-sofiati-13-balcony-orange-soft-smile"),
    "consult": cutout("franciele-sofiati-29-ivory-room-seated-side"),
    "precise": cutout("franciele-sofiati-22-ivory-room-arms-crossed"),
    "care": cutout("franciele-sofiati-25-ivory-room-window-touch"),
    "journal": cutout("franciele-sofiati-17-balcony-orange-laughing"),
    "profile": cutout("franciele-sofiati-10-studio-close-smile"),
    "side": cutout("franciele-sofiati-24-ivory-room-window-side"),
    "hero_opaque": opaque("franciele-sofiati-19-ivory-room-standing-direct", "hero"),
    "soft_opaque": opaque("franciele-sofiati-01-studio-seated-soft-smile", "about"),
    "window_opaque": opaque("franciele-sofiati-27-ivory-room-window-attentive", "contact"),
    "skin_opaque": opaque("franciele-sofiati-15-balcony-orange-direct", "skin"),
}


PAGE_DATA = {
    "index": {
        "title": "Personalized Aesthetic Care | Inspire | Franciele Sofiati",
        "description": "A calm, refined introduction to Franciele Sofiati's personalized aesthetic care in Londrina, PR.",
        "eyebrow": "Cuidado, confiança, segurança, naturalidade",
        "h1": "Personalized aesthetic care with a calm, attentive approach.",
        "intro": "A premium Sofiati experience shaped around conversation, observation, professional judgment, and realistic expectations.",
        "primary": ("Request consultation", "consultation.html"),
        "secondary": ("Meet Franciele", "about.html"),
        "hero_photo": "authority",
        "hero_panel": "hero_opaque",
        "sections": [
            ("Human Trust", "Real care begins with a person, not a protocol.", "Franciele's work is presented with discretion, clarity, and a visual language that feels personal instead of generic.", "about.html", "Read the profile", "soft_opaque"),
            ("Care Path", "A thoughtful rhythm before any treatment choice.", "The site guides visitors from first impression to consultation questions, with skin, laser, care planning, and responsible expectations kept separate and clear.", "care.html", "Explore care", "care"),
            ("Education", "Short, useful notes for better decisions.", "Journal content supports better questions before consultation without promising outcomes or simplifying individual needs.", "journal.html", "Open journal", "journal"),
        ],
        "cards": [
            ("01", "Listen", "Goals, routine, comfort level, and timing come first."),
            ("02", "Assess", "Suitability and expectations are framed with professional care."),
            ("03", "Plan", "The next step is chosen with restraint, clarity, and aftercare in mind."),
        ],
    },
    "about": {
        "title": "About Franciele Sofiati | Inspire",
        "description": "A grounded portrait-led introduction to Franciele Sofiati, CRBM 6277, in Londrina, PR.",
        "eyebrow": "Professional presence",
        "h1": "A calm professional profile before aesthetic decisions.",
        "intro": "Franciele Sofiati is presented through a refined, human visual system that supports trust without exaggeration.",
        "primary": ("Start consultation", "consultation.html"),
        "secondary": ("Care values", "values.html"),
        "hero_photo": "profile",
        "hero_panel": "soft_opaque",
        "sections": [
            ("Grounded Profile", "Aesthetic care needs context and conversation.", "This page keeps the introduction concise: professional identity, communication style, and the values that shape each visit.", "consultation.html", "Request evaluation", "authority"),
            ("Care Philosophy", "Cuidado, confiança, segurança, naturalidade.", "The Sofiati tone is quiet and attentive: natural-looking expectations, privacy, and decisions made only after evaluation.", "care.html", "View care path", "care"),
            ("Trust Image", "Real photography replaces generic reassurance.", "Portraits are used as brand presence, not as claims about results or outcomes.", "results.html", "Read result guidance", "side"),
        ],
        "cards": [
            ("Cuidado", "A soft, attentive way to begin the conversation."),
            ("Confiança", "Clear language before protocols or expectations."),
            ("Segurança", "Evaluation-led guidance and respectful boundaries."),
            ("Naturalidade", "A preference for restraint and realistic planning."),
        ],
    },
    "care": {
        "title": "Personalized Care | Inspire | Franciele Sofiati",
        "description": "Personalized aesthetic care explained through consultation, planning, and responsible support.",
        "eyebrow": "Personalized care",
        "h1": "Care that begins with listening and professional evaluation.",
        "intro": "Aesthetic planning becomes calmer when goals, routine, skin characteristics, and comfort level are understood first.",
        "primary": ("Discuss care", "consultation.html"),
        "secondary": ("Skin guidance", "skin.html"),
        "hero_photo": "care",
        "hero_panel": "window_opaque",
        "sections": [
            ("Opening Promise", "A quieter way to understand care options.", "The experience avoids pressure-led language and gives visitors a grounded route into conversation.", "consultation.html", "Begin calmly", "consult"),
            ("Approach", "Observation, conversation, suitability, and aftercare.", "Each step is framed as support for better decisions rather than a promise of a fixed result.", "results.html", "Responsible expectations", "precise"),
            ("Reassurance", "Privacy and comfort stay part of the care path.", "The page keeps the emotional tone warm while respecting boundaries around patient images and private details.", "contact.html", "Contact Franciele", "warm"),
        ],
        "cards": [
            ("Goals", "What you want to improve and what feels realistic."),
            ("Routine", "How care fits your skin, time, and comfort."),
            ("Planning", "What should be considered before any procedure."),
            ("Aftercare", "How guidance continues beyond the first conversation."),
        ],
    },
    "skin": {
        "title": "Skin Guidance | Inspire | Franciele Sofiati",
        "description": "Refined skin guidance for routine, sensitivity, texture, and professional planning.",
        "eyebrow": "Skin quality",
        "h1": "Skin care guidance shaped around routine, goals, and comfort.",
        "intro": "The skin page keeps the tone refined and practical, with botanical warmth and a clear consultation path.",
        "primary": ("Plan skin care", "consultation.html"),
        "secondary": ("Care approach", "care.html"),
        "hero_photo": "warm",
        "hero_panel": "skin_opaque",
        "sections": [
            ("Routine", "Small details help frame better questions.", "Sensitivity, texture, spots, cleansing, and timing should be discussed with context instead of rushed assumptions.", "journal.html", "Read notes", "journal"),
            ("Guidance", "Professional planning stays individual.", "Content supports conversation and observation without reducing skin care to a one-size-fits-all protocol.", "consultation.html", "Request guidance", "profile"),
            ("Botanical Break", "Soft colour rhythm keeps the page warm.", "Sage, ivory, deep green, and gold work with real portraits to create a premium skincare mood.", "contact.html", "Ask a question", "side"),
        ],
        "cards": [
            ("Texture", "Discuss what feels uneven or uncomfortable."),
            ("Clarity", "Frame spots and tone carefully, without promises."),
            ("Sensitivity", "Respect comfort, history, and skin response."),
            ("Routine", "Make planning realistic for daily life."),
        ],
    },
    "laser": {
        "title": "Laser Guidance | Inspire | Franciele Sofiati",
        "description": "Laser care language focused on suitability, preparation, comfort, and realistic expectations.",
        "eyebrow": "Laser with warmth",
        "h1": "Laser decisions begin with suitability, preparation, and clarity.",
        "intro": "The laser page uses a more structured visual rhythm while keeping the Sofiati tone calm and human.",
        "primary": ("Evaluate suitability", "consultation.html"),
        "secondary": ("Skin context", "skin.html"),
        "hero_photo": "precise",
        "hero_panel": "hero_opaque",
        "sections": [
            ("Assessment", "Technology is only useful when it is appropriate.", "Laser guidance is framed through indication, skin characteristics, preparation, session rhythm, and aftercare.", "consultation.html", "Discuss suitability", "authority"),
            ("Expectations", "Responsible information protects trust.", "The page avoids result promises and keeps decisions connected to individual professional evaluation.", "results.html", "Read expectations", "side"),
            ("Support", "A clinical page can still feel warm.", "Deep green bands, ivory panels, and cutout portrait layering keep precision from becoming cold.", "care.html", "Return to care", "care"),
        ],
        "cards": [
            ("Suitability", "Is laser appropriate for the goal and skin context?"),
            ("Preparation", "What should be considered before a session?"),
            ("Comfort", "How expectations and aftercare should be discussed."),
            ("Rhythm", "How timing and follow-up shape the plan."),
        ],
    },
    "results": {
        "title": "Responsible Results | Inspire | Franciele Sofiati",
        "description": "Ethical result guidance focused on planning, realistic expectations, and care.",
        "eyebrow": "Responsible expectations",
        "h1": "Results are discussed through planning, care, and realistic expectations.",
        "intro": "This page does not imply comparative proof. It frames outcomes carefully around individual evaluation.",
        "primary": ("Clarify expectations", "consultation.html"),
        "secondary": ("Care values", "about.html"),
        "hero_photo": "side",
        "hero_panel": "soft_opaque",
        "sections": [
            ("Ethical Trust", "No invented outcomes. No borrowed proof.", "Franciele's portrait is used for professional presence, while result language stays careful, private, and educational.", "consultation.html", "Talk through goals", "profile"),
            ("Process", "Good expectations are built before treatment.", "Planning considers suitability, protocol, session rhythm, individual characteristics, and aftercare.", "care.html", "Understand care", "precise"),
            ("Reassurance", "Naturalidade means restraint, not a promise.", "The goal is clarity and confidence in decision-making, not dramatic claims.", "contact.html", "Contact", "warm"),
        ],
        "cards": [
            ("Before", "Understand goals and boundaries."),
            ("During", "Keep decisions connected to suitability."),
            ("After", "Respect aftercare and individual response."),
        ],
    },
    "consultation": {
        "title": "Consultation | Inspire | Franciele Sofiati",
        "description": "A warm consultation path for goals, questions, comfort level, and professional evaluation.",
        "eyebrow": "Consultation path",
        "h1": "A consultation designed to understand your skin, routine, goals, and comfort level.",
        "intro": "The consultation page is warm, direct, and action-oriented while keeping decisions evaluation-led.",
        "primary": ("Contact on WhatsApp", "https://wa.me/5543991043536"),
        "secondary": ("Contact options", "contact.html"),
        "hero_photo": "consult",
        "hero_panel": "window_opaque",
        "sections": [
            ("What it clarifies", "Goals, timing, questions, and comfort.", "A consultation gives space to describe what matters before a professional path is considered.", "care.html", "Review care", "warm"),
            ("What to expect", "A focused conversation, not pressure.", "The tone stays discreet: understand, assess, explain, and decide only when the next step is appropriate.", "results.html", "Expectations", "authority"),
            ("Action", "Public contact routes stay clear.", "WhatsApp, email, and Instagram are available for consultation requests and approved communication.", "contact.html", "See contact", "profile"),
        ],
        "cards": [
            ("Bring", "Goals, concerns, routine, and questions."),
            ("Discuss", "Skin context, comfort level, and timing."),
            ("Leave with", "A clearer sense of whether a next step makes sense."),
        ],
    },
    "contact": {
        "title": "Contact | Inspire | Franciele Sofiati",
        "description": "Warm public contact routes for consultation requests with Franciele Sofiati in Londrina, PR.",
        "eyebrow": "Contact",
        "h1": "A warm route to ask questions and request professional evaluation.",
        "intro": "Contact remains simple and respectful: WhatsApp, email, and Instagram for public communication.",
        "primary": ("WhatsApp", "https://wa.me/5543991043536"),
        "secondary": ("Consultation", "consultation.html"),
        "hero_photo": "journal",
        "hero_panel": "window_opaque",
        "sections": [
            ("Reassurance", "You can begin with a calm question.", "The contact page supports first messages without pressure or private location details.", "consultation.html", "Consultation path", "consult"),
            ("Routes", "Public channels are presented clearly.", "Use WhatsApp, email, or Instagram for approved communication and consultation requests.", "mailto:sofiatimendonca@gmail.com", "Email", "profile"),
            ("Next Step", "If you are unsure, start with evaluation.", "A professional conversation helps clarify whether a care path is appropriate.", "care.html", "Explore care", "care"),
        ],
        "cards": [
            ("WhatsApp", "(43) 9 9104-3536"),
            ("Email", "sofiatimendonca@gmail.com"),
            ("Instagram", "@fransofiati_biomedica"),
        ],
    },
    "journal": {
        "title": "Journal | Inspire | Franciele Sofiati",
        "description": "Editorial education notes for skin, laser, aftercare, consultation questions, and responsible expectations.",
        "eyebrow": "Editorial notes",
        "h1": "Short education notes for calmer consultation questions.",
        "intro": "The journal uses varied real-photo thumbnails and concise content categories instead of repeated generic cards.",
        "primary": ("Read skin guidance", "skin.html"),
        "secondary": ("Book consultation", "consultation.html"),
        "hero_photo": "warm",
        "hero_panel": "skin_opaque",
        "sections": [
            ("Skin Notes", "Routine, sensitivity, texture, and clarity.", "Short notes help visitors bring better questions into professional evaluation.", "skin.html", "Skin guidance", "journal"),
            ("Laser Notes", "Preparation, suitability, and aftercare.", "Laser education stays structured and warm without promising outcomes.", "laser.html", "Laser guidance", "precise"),
            ("Care Notes", "Values, privacy, planning, and comfort.", "The journal reinforces cuidado, confiança, segurança, and naturalidade through practical topics.", "care.html", "Care path", "care"),
        ],
        "cards": [
            ("Skin", "What to notice before a consultation."),
            ("Laser", "Questions about preparation and suitability."),
            ("Aftercare", "Why guidance continues after decisions."),
            ("Expectations", "How to think about results responsibly."),
        ],
    },
}


def img(photo: dict[str, str | int], cls: str, role: str, lazy: bool = True) -> str:
    loading = "lazy" if lazy else "eager"
    return (
        f'<img class="{cls}" src="{photo["path"]}" alt="{photo["alt"]}" '
        f'width="{photo["width"]}" height="{photo["height"]}" loading="{loading}" '
        f'decoding="async" data-brand-photo="{photo["id"]}" data-photo-role="{role}">'
    )


def section_html(page: str, index: int, data: tuple[str, str, str, str, str, str]) -> str:
    eyebrow, heading, copy, href, link, photo_key = data
    photo = PHOTOS[photo_key]
    flip = " story-section--flip" if index % 2 else ""
    tone = ["sage-section", "ivory-section", "deep-green-section"][index % 3]
    return f"""
<section class="story-section editorial-section {tone}{flip}" data-story-step="{index + 2}">
  <div class="story-section__copy">
    <p class="eyebrow">{eyebrow}</p>
    <h2>{heading}</h2>
    <p>{copy}</p>
    <a class="button button-soft" href="{href}">{link}</a>
  </div>
  <figure class="botanical-image-wrap photo-frame photo-frame--editorial">
    <span class="gold-divider" aria-hidden="true"></span>
    {img(photo, "photo-cutout photo-cutout--story doctor-portrait doctor-portrait--about", "transparent-story")}
  </figure>
</section>"""


def cards_html(page: str, cards: list[tuple[str, ...]]) -> str:
    cards_out = []
    for card in cards:
        title, copy = card[-2], card[-1]
        label = card[0] if len(card) == 3 else ""
        cards_out.append(
            f'<article class="photo-card"><span>{label}</span><h3>{title}</h3><p>{copy}</p></article>'
        )
    return "\n".join(cards_out)


def main_html(page: str, data: dict[str, object]) -> str:
    hero = PHOTOS[data["hero_photo"]]
    panel = PHOTOS[data["hero_panel"]]
    story = "\n".join(section_html(page, idx, item) for idx, item in enumerate(data["sections"]))
    return f"""
<main id="main" class="pilot-page pilot-page-{page}" data-pilot-page="{page}" data-story-flow="opening-human-trust-explanation-process-colour-break-reassurance-consultation-cta">
  <section class="real-photo-hero brand-colour-band" data-story-step="1">
    <div class="real-photo-hero__copy">
      <p class="eyebrow">{data["eyebrow"]}</p>
      <h1>{data["h1"]}</h1>
      <p>{data["intro"]}</p>
      <div class="hero-actions">
        <a class="button button-primary" href="{data["primary"][1]}">{data["primary"][0]}</a>
        <a class="button button-soft" href="{data["secondary"][1]}">{data["secondary"][0]}</a>
      </div>
    </div>
    <div class="real-photo-hero__visual photo-panel">
      <div class="photo-panel__halo" aria-hidden="true"></div>
      {img(hero, "photo-cutout photo-cutout--hero doctor-portrait doctor-portrait--hero", "transparent-hero", lazy=False)}
      <figure class="premium-image-mask photo-frame photo-frame--sage">
        {img(panel, "doctor-portrait doctor-portrait--hero-support", "support-photo")}
      </figure>
    </div>
  </section>

  <section class="pilot-values sage-section story-break" aria-label="Sofiati values" data-story-step="2">
    <p class="eyebrow">Sofiati care language</p>
    <div class="pilot-values__grid">
      <article><h2>Cuidado</h2><p>Attentive listening before aesthetic planning.</p></article>
      <article><h2>Confiança</h2><p>Clear expectations and discreet communication.</p></article>
      <article><h2>Segurança</h2><p>Professional evaluation before protocol decisions.</p></article>
      <article><h2>Naturalidade</h2><p>Restraint, warmth, and realistic visual goals.</p></article>
    </div>
  </section>

  {story}

  <section class="editorial-section consultation-photo-block deep-green-section" data-story-step="6">
    <div>
      <p class="eyebrow">Approach</p>
      <h2>A clear path from first question to professional evaluation.</h2>
      <p>Each page now moves through a deliberate story: opening promise, human trust, explanation, process, colour break, reassurance, consultation path, and final CTA.</p>
    </div>
    <div class="photo-collage">
      {img(PHOTOS["consult"], "photo-cutout photo-cutout--cta doctor-portrait doctor-portrait--consultation", "transparent-cta")}
      {img(PHOTOS["window_opaque"], "photo-card__image doctor-portrait", "collage-photo")}
    </div>
  </section>

  <section class="pilot-card-band ivory-section" data-story-step="7">
    <div class="section-heading">
      <p class="eyebrow">Details that matter</p>
      <h2>Concise guidance, not generic filler.</h2>
    </div>
    <div class="pilot-card-grid">
      {cards_html(page, data["cards"])}
    </div>
  </section>

  <section class="pilot-final-cta brand-colour-band" data-story-step="8">
    <div>
      <p class="eyebrow">Consultation</p>
      <h2>Begin with a grounded conversation.</h2>
      <p>Use the consultation route to clarify goals, questions, timing, and comfort before considering next steps.</p>
    </div>
    <a class="button button-primary" href="consultation.html">Request consultation</a>
    <a class="button button-soft" href="contact.html">Contact Franciele</a>
  </section>

  <section class="contact-card-section pilot-contact-section" data-section-type="contact">
    <div data-partial-mount="contact-card"></div>
  </section>
</main>"""


PILOT_CSS = f"""
{CSS_START}
:root {{
  --sofiati-sage: #A2AE9F;
  --sofiati-ivory: #F3EFE5;
  --sofiati-green: #798A80;
  --sofiati-gold: #CDAA78;
  --sofiati-cream: #F8F4EA;
  --sofiati-deep: #344039;
}}
.sf-pilot-rebuild {{
  background:
    radial-gradient(circle at 12% 12%, color-mix(in srgb, var(--sofiati-sage) 22%, transparent), transparent 32%),
    linear-gradient(180deg, var(--sofiati-cream), var(--sofiati-ivory));
  color: var(--ink);
}}
.sf-pilot-rebuild > .skip-link:not(:focus),
.sf-pilot-rebuild .public-accessibility .skip-link:not(:focus),
.sf-pilot-rebuild .public-accessibility .accessibility-page-link:not(:focus) {{
  position: fixed;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  transform: none;
}}
.sf-pilot-rebuild > .skip-link:focus,
.sf-pilot-rebuild .public-accessibility .skip-link:focus,
.sf-pilot-rebuild .public-accessibility .accessibility-page-link:focus {{
  width: auto;
  height: auto;
  padding: 10px 12px;
  margin: 0;
  overflow: visible;
  clip-path: none;
  transform: none;
}}
.sf-pilot-rebuild .pilot-page {{
  overflow: hidden;
}}
.sf-pilot-rebuild .real-photo-hero,
.sf-pilot-rebuild .editorial-section,
.sf-pilot-rebuild .pilot-values,
.sf-pilot-rebuild .pilot-card-band,
.sf-pilot-rebuild .pilot-final-cta {{
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
}}
.brand-colour-band {{
  position: relative;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--sofiati-deep) 92%, #111), color-mix(in srgb, var(--sofiati-green) 78%, #fff));
  color: white;
  border: 1px solid color-mix(in srgb, var(--sofiati-gold) 26%, transparent);
  box-shadow: 0 30px 90px rgba(37,35,33,.16);
}}
.real-photo-hero {{
  min-height: min(820px, calc(100vh - 70px));
  display: grid;
  grid-template-columns: minmax(0, .92fr) minmax(360px, .78fr);
  align-items: center;
  gap: clamp(28px, 5vw, 86px);
  padding: clamp(56px, 8vw, 118px) clamp(18px, 5vw, 72px);
  border-radius: 0 0 92px 0;
  margin-top: clamp(28px, 4vw, 54px);
}}
.real-photo-hero::before,
.story-section::before,
.consultation-photo-block::before {{
  content: "";
  position: absolute;
  inset: 22px 22px auto auto;
  width: min(180px, 28vw);
  aspect-ratio: 1;
  border: 1px solid color-mix(in srgb, var(--sofiati-gold) 48%, transparent);
  border-radius: 999px 0 999px 999px;
  opacity: .55;
  pointer-events: none;
}}
.real-photo-hero__copy {{
  display: grid;
  gap: 20px;
  max-width: 680px;
}}
.real-photo-hero__copy h1 {{
  color: inherit;
  font-size: clamp(3rem, 7.6vw, 7.4rem);
  line-height: .92;
}}
.real-photo-hero__copy p:not(.eyebrow) {{
  max-width: 54ch;
  color: rgba(255,255,255,.78);
  font-size: clamp(1rem, 1.35vw, 1.18rem);
}}
.photo-panel {{
  position: relative;
  min-height: clamp(440px, 54vw, 720px);
  display: grid;
  place-items: end center;
}}
.photo-panel__halo {{
  position: absolute;
  inset: 9% 0 8% 8%;
  border-radius: 999px 999px 18px 999px;
  background:
    radial-gradient(circle at 44% 30%, rgba(255,255,255,.55), transparent 26%),
    linear-gradient(145deg, color-mix(in srgb, var(--sofiati-sage) 70%, white), color-mix(in srgb, var(--sofiati-gold) 30%, var(--sofiati-ivory)));
  box-shadow: inset 0 0 0 1px rgba(255,255,255,.34), 0 30px 90px rgba(0,0,0,.18);
}}
.photo-cutout {{
  position: relative;
  z-index: 2;
  width: min(88%, 520px);
  height: auto;
  object-fit: contain;
  filter: drop-shadow(0 28px 46px rgba(16,22,18,.26));
}}
.photo-cutout--hero {{
  align-self: end;
  max-height: 680px;
}}
.premium-image-mask {{
  position: absolute;
  left: 0;
  bottom: 4%;
  z-index: 1;
  width: min(260px, 42%);
  aspect-ratio: 4 / 5;
  border-radius: 160px 160px 8px 8px;
  overflow: hidden;
  opacity: .92;
}}
.premium-image-mask img,
.photo-frame img {{
  width: 100%;
  height: 100%;
  object-fit: cover;
}}
.sage-section {{
  background: linear-gradient(135deg, color-mix(in srgb, var(--sofiati-sage) 42%, white), var(--sofiati-cream));
}}
.ivory-section {{
  background: linear-gradient(135deg, var(--sofiati-ivory), color-mix(in srgb, var(--sofiati-gold) 12%, white));
}}
.deep-green-section {{
  background: linear-gradient(135deg, var(--sofiati-deep), color-mix(in srgb, var(--sofiati-green) 72%, #1a211d));
  color: white;
}}
.pilot-values,
.pilot-card-band {{
  margin-top: clamp(24px, 5vw, 70px);
  padding: clamp(36px, 6vw, 84px);
  border: 1px solid color-mix(in srgb, var(--sofiati-gold) 22%, transparent);
}}
.pilot-values__grid,
.pilot-card-grid {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}}
.pilot-values article,
.photo-card {{
  background: rgba(255,255,255,.62);
  border: 1px solid color-mix(in srgb, var(--sofiati-gold) 22%, transparent);
  padding: clamp(18px, 2.5vw, 30px);
  min-height: 180px;
}}
.pilot-values h2,
.photo-card h3 {{
  font-size: clamp(1.35rem, 2.4vw, 2.2rem);
}}
.story-section {{
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, .9fr) minmax(320px, .72fr);
  gap: clamp(24px, 5vw, 76px);
  align-items: center;
  padding: clamp(44px, 7vw, 104px);
  margin-top: clamp(24px, 5vw, 70px);
  border: 1px solid color-mix(in srgb, var(--sofiati-gold) 22%, transparent);
  border-radius: 4px 72px 4px 4px;
  box-shadow: 0 24px 70px rgba(37,35,33,.1);
}}
.story-section--flip {{
  grid-template-columns: minmax(320px, .72fr) minmax(0, .9fr);
}}
.story-section--flip .story-section__copy {{
  order: 2;
}}
.story-section__copy {{
  display: grid;
  gap: 16px;
}}
.story-section__copy h2,
.consultation-photo-block h2,
.pilot-final-cta h2 {{
  font-size: clamp(2rem, 4.5vw, 5rem);
  line-height: .98;
}}
.story-section__copy p:not(.eyebrow),
.consultation-photo-block p,
.pilot-final-cta p {{
  max-width: 58ch;
  color: color-mix(in srgb, currentColor 72%, transparent);
}}
.botanical-image-wrap {{
  min-height: clamp(360px, 44vw, 620px);
  display: grid;
  align-items: end;
  justify-items: center;
  overflow: visible;
  border-radius: 999px 999px 8px 8px;
  background:
    radial-gradient(circle at 48% 42%, rgba(255,255,255,.86), transparent 34%),
    linear-gradient(145deg, color-mix(in srgb, var(--sofiati-sage) 42%, white), color-mix(in srgb, var(--sofiati-gold) 16%, var(--sofiati-ivory)));
}}
.botanical-image-wrap .photo-cutout {{
  max-height: 570px;
  width: min(96%, 450px);
}}
.gold-divider {{
  position: absolute;
  top: 14%;
  left: 14%;
  width: 42%;
  height: 1px;
  background: var(--sofiati-gold);
}}
.consultation-photo-block {{
  position: relative;
  display: grid;
  grid-template-columns: minmax(0, .82fr) minmax(320px, .7fr);
  gap: clamp(28px, 5vw, 80px);
  align-items: center;
  padding: clamp(44px, 7vw, 104px);
  margin-top: clamp(24px, 5vw, 70px);
  border-radius: 72px 4px 72px 4px;
}}
.photo-collage {{
  position: relative;
  min-height: 440px;
  display: grid;
  place-items: end center;
}}
.photo-collage .photo-cutout {{
  max-height: 520px;
}}
.photo-card__image {{
  position: absolute;
  left: 0;
  top: 5%;
  z-index: 1;
  width: 45%;
  aspect-ratio: 1;
  border-radius: 999px;
  object-fit: cover;
  border: 8px solid rgba(255,255,255,.72);
}}
.pilot-final-cta {{
  margin-top: clamp(24px, 5vw, 70px);
  padding: clamp(38px, 6vw, 80px);
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  align-items: end;
  justify-content: space-between;
  border-radius: 4px 4px 92px 4px;
}}
.pilot-final-cta div {{
  display: grid;
  gap: 12px;
  max-width: 680px;
}}
.pilot-contact-section {{
  padding: clamp(42px, 6vw, 86px) 0;
}}
@media(max-width: 980px) {{
  .real-photo-hero,
  .story-section,
  .story-section--flip,
  .consultation-photo-block {{
    grid-template-columns: 1fr;
  }}
  .story-section--flip .story-section__copy {{
    order: 0;
  }}
  .pilot-values__grid,
  .pilot-card-grid {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }}
}}
@media(max-width: 620px) {{
  .sf-pilot-rebuild .real-photo-hero,
  .sf-pilot-rebuild .editorial-section,
  .sf-pilot-rebuild .pilot-values,
  .sf-pilot-rebuild .pilot-card-band,
  .sf-pilot-rebuild .pilot-final-cta {{
    width: min(100% - 24px, 420px);
  }}
  .real-photo-hero {{
    padding: 28px 16px 36px;
    border-radius: 0 0 44px 0;
    min-height: auto;
  }}
  .real-photo-hero__visual {{
    order: -1;
  }}
  .photo-panel {{
    min-height: 430px;
  }}
  .photo-cutout--hero {{
    max-height: 430px;
  }}
  .real-photo-hero__copy h1 {{
    font-size: clamp(2.6rem, 15vw, 4.7rem);
  }}
  .page-contact .real-photo-hero {{
    gap: 12px;
    padding-top: 20px;
    padding-bottom: 24px;
  }}
  .page-contact .photo-panel {{
    min-height: 268px;
  }}
  .page-contact .photo-cutout--hero {{
    max-height: 268px;
    width: min(78%, 320px);
  }}
  .page-contact .premium-image-mask {{
    width: min(122px, 34%);
    bottom: 2%;
  }}
  .page-contact .real-photo-hero__copy {{
    gap: 10px;
  }}
  .page-contact .real-photo-hero__copy h1 {{
    font-size: clamp(1.85rem, 8.8vw, 3rem);
    line-height: .98;
  }}
  .page-contact .real-photo-hero__copy p:not(.eyebrow) {{
    font-size: .9rem;
    line-height: 1.45;
  }}
  .page-contact .hero-actions {{
    gap: 6px;
  }}
  .page-contact .hero-actions .button {{
    min-height: 38px;
    padding: 7px 10px;
    font-size: .78rem;
  }}
  .pilot-values,
  .pilot-card-band,
  .story-section,
  .consultation-photo-block,
  .pilot-final-cta {{
    padding: 28px 16px;
  }}
  .pilot-values__grid,
  .pilot-card-grid {{
    grid-template-columns: 1fr;
  }}
  .botanical-image-wrap {{
    min-height: 360px;
  }}
  .botanical-image-wrap .photo-cutout {{
    max-height: 340px;
  }}
  .photo-collage {{
    min-height: 360px;
  }}
  .photo-collage .photo-cutout {{
    max-height: 360px;
  }}
  .photo-card__image {{
    width: 110px;
  }}
}}
{CSS_END}
"""


def update_html(page: str, data: dict[str, object]) -> None:
    path = CONCEPT / f"{page}.html"
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"<title>.*?</title>", f"<title>{data['title']}</title>", html, count=1, flags=re.S)
    html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{data["description"]}">', html, count=1)
    html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{data["title"]}">', html, count=1)
    html = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{data["description"]}">', html, count=1)
    html = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{data["title"]}">', html, count=1)
    html = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{data["description"]}">', html, count=1)
    html = re.sub(r"<body([^>]*)>", lambda m: add_body_class(m.group(0), page, data), html, count=1)
    html = re.sub(r'<main id="main".*?</main>', main_html(page, data), html, count=1, flags=re.S)
    path.write_text(html, encoding="utf-8")


def add_body_class(tag: str, page: str, data: dict[str, object]) -> str:
    match = re.search(r'class="([^"]*)"', tag)
    classes = match.group(1).split() if match else []
    for cls in ("sf-pilot-rebuild", "design-family-sage-cutout-editorial"):
        if cls not in classes:
            classes.append(cls)
    tag = tag[: match.start(1)] + " ".join(classes) + tag[match.end(1) :] if match else tag.replace("<body", f'<body class="{" ".join(classes)}"', 1)
    for attr, value in (
        ("data-design-family", "sage-cutout-editorial"),
        ("data-pilot-page", page),
        ("data-page-title", str(data["title"])),
        ("data-page-description", str(data["description"])),
    ):
        if f"{attr}=" in tag:
            tag = re.sub(rf'{attr}="[^"]*"', f'{attr}="{value}"', tag, count=1)
        else:
            tag = tag[:-1] + f' {attr}="{value}">'
    return tag


def update_css() -> None:
    path = CONCEPT / "css" / "style.css"
    css = path.read_text(encoding="utf-8")
    css = re.sub(re.escape(CSS_START) + r".*?" + re.escape(CSS_END) + r"\n?", "", css, flags=re.S).rstrip()
    path.write_text(css + "\n\n" + PILOT_CSS + "\n", encoding="utf-8")


def main() -> None:
    for page, data in PAGE_DATA.items():
        update_html(page, data)
    update_css()
    print(json.dumps({"pilot": "01-inspire", "pages_rebuilt": sorted(PAGE_DATA), "css": "concepts/01-inspire/css/style.css"}, indent=2))


if __name__ == "__main__":
    main()
