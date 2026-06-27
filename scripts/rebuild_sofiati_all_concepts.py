#!/usr/bin/env python3
"""Scale the Sofiati premium real-photo rebuild across all concepts."""

from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts import rebuild_sofiati_pilot_concept as pilot


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS = sorted(path for path in (ROOT / "concepts").iterdir() if path.is_dir())

FAMILIES = [
    ("sage-cutout-editorial", "Sage cutout editorial", "calm sage structure and portrait-led confidence"),
    ("deep-green-luxury", "Deep green luxury", "deep green contrast, gold restraint, and quiet authority"),
    ("ivory-oval-portrait", "Ivory oval portrait", "soft ivory portrait rhythm and warm professional clarity"),
    ("botanical-collage", "Botanical collage", "layered botanical portrait compositions and gentle movement"),
    ("minimal-gold-clinic", "Minimal gold clinic", "precise spacing, gold dividers, and clinical warmth"),
    ("warm-consultation-led", "Warm consultation-led", "approachable consultation flow and human reassurance"),
    ("magazine-asymmetry", "Magazine asymmetry", "editorial offsets, varied scale, and stronger visual pacing"),
    ("structured-clinical", "Structured clinical", "orderly process sections and deep green reassurance"),
    ("airy-skincare", "Airy skincare", "window-lit softness, cream spacing, and skin-focused calm"),
    ("dark-muted-premium", "Dark muted green premium", "restrained luxury, darker bands, and high-trust portraits"),
]

TRANSPARENT_IDS = [entry["id"] for entry in pilot.MANIFEST["entries"] if entry.get("transparent_alpha_verified")]
CATEGORY_IDS = {
    category: [
        entry["id"]
        for entry in pilot.MANIFEST["entries"]
        if category in entry.get("category_files", {})
    ]
    for category in ["hero", "about", "contact", "skin", "journal", "consultation"]
}

PAGE_PREFIX = {
    "index": "Personalized Aesthetic Care",
    "about": "About Franciele Sofiati",
    "care": "Personalized Care",
    "skin": "Skin Guidance",
    "laser": "Laser Guidance",
    "results": "Responsible Results",
    "consultation": "Consultation",
    "contact": "Contact",
    "journal": "Journal",
}

PAGE_H1_VARIANTS = {
    "index": [
        "Personalized aesthetic care with calm, attentive precision.",
        "A refined Sofiati experience for natural-looking aesthetic planning.",
        "Warm professional care shaped around trust and realistic expectations.",
        "A calm first step into personalized aesthetic guidance.",
        "Editorial, human, evaluation-led care for skin and confidence.",
    ],
    "about": [
        "A grounded professional presence before aesthetic decisions.",
        "Meet Franciele through care, clarity, and discreet confidence.",
        "A human introduction to the professional behind the care.",
        "Professional trust presented with warmth and restraint.",
        "A portrait-led view of calm aesthetic guidance.",
    ],
    "care": [
        "Care begins with listening, context, and professional evaluation.",
        "A thoughtful care path before any treatment decision.",
        "Personalized planning shaped around goals, routine, and comfort.",
        "A calm approach to aesthetic choices and aftercare.",
        "Care that protects clarity before protocol selection.",
    ],
    "skin": [
        "Skin guidance shaped around routine, comfort, and goals.",
        "A refined path for skin quality questions and planning.",
        "Skin care conversations with softness, clarity, and context.",
        "A calm way to discuss texture, sensitivity, and routine.",
        "Professional skin guidance without rushed assumptions.",
    ],
    "laser": [
        "Laser decisions begin with suitability, preparation, and clarity.",
        "Technology-led care with warmth, context, and restraint.",
        "A structured way to discuss laser suitability and aftercare.",
        "Laser guidance framed by evaluation and realistic expectations.",
        "Precision, comfort, and planning before laser decisions.",
    ],
    "results": [
        "Results are discussed through planning, care, and realistic expectations.",
        "A responsible way to understand aesthetic expectations.",
        "Confidence begins with clear, careful guidance.",
        "Outcome conversations stay private, realistic, and evaluation-led.",
        "Result guidance without exaggerated promises.",
    ],
    "consultation": [
        "A consultation designed to understand skin, routine, goals, and comfort.",
        "Begin with a calm conversation before choosing a protocol.",
        "A warm evaluation path for questions, timing, and expectations.",
        "Professional guidance starts with listening.",
        "A discreet route from first question to considered planning.",
    ],
    "contact": [
        "A warm route to ask questions and request professional evaluation.",
        "Contact Franciele through clear public communication routes.",
        "Begin with a calm message and a responsible next step.",
        "Simple contact, discreet communication, and consultation guidance.",
        "A clear contact path for thoughtful aesthetic care.",
    ],
    "journal": [
        "Short education notes for calmer consultation questions.",
        "Editorial notes for skin, laser, care, and expectations.",
        "Useful reading before professional evaluation.",
        "A calm journal for better aesthetic care questions.",
        "Education shaped by care, restraint, and clarity.",
    ],
}

FAMILY_CSS = """
.sf-pilot-rebuild {
  --concept-hero-radius: 0 0 92px 0;
  --concept-card-radius: 4px;
  --concept-photo-scale: 1;
}
.sf-pilot-rebuild .real-photo-hero { border-radius: var(--concept-hero-radius); }
.sf-pilot-rebuild .photo-cutout--hero { transform: scale(var(--concept-photo-scale)); transform-origin: bottom center; }
.sf-pilot-rebuild .photo-card,
.sf-pilot-rebuild .pilot-values article { border-radius: var(--concept-card-radius); }
.design-family-deep-green-luxury .brand-colour-band,
.design-family-dark-muted-premium .brand-colour-band { background: linear-gradient(135deg,#18241f,#4c5b50 58%,#252321); }
.design-family-ivory-oval-portrait .brand-colour-band,
.design-family-airy-skincare .brand-colour-band { background: linear-gradient(135deg,#F3EFE5,#A2AE9F); color: var(--ink); }
.design-family-ivory-oval-portrait .real-photo-hero__copy p:not(.eyebrow),
.design-family-airy-skincare .real-photo-hero__copy p:not(.eyebrow) { color: color-mix(in srgb,var(--ink) 72%,transparent); }
.design-family-botanical-collage .real-photo-hero { grid-template-columns: minmax(320px,.75fr) minmax(0,.9fr); }
.design-family-botanical-collage .real-photo-hero__visual { order: -1; }
.design-family-minimal-gold-clinic .story-section,
.design-family-structured-clinical .story-section { border-radius: 4px; box-shadow: inset 0 0 0 1px color-mix(in srgb,var(--sofiati-gold) 18%,transparent); }
.design-family-warm-consultation-led .pilot-values { order: 0; border-radius: 44px 4px 44px 4px; }
.design-family-magazine-asymmetry .story-section:nth-of-type(odd) { transform: translateX(min(2vw,22px)); }
.design-family-magazine-asymmetry .story-section:nth-of-type(even) { transform: translateX(max(-2vw,-22px)); }
.design-family-structured-clinical .pilot-card-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }
.design-family-dark-muted-premium .sage-section { background: linear-gradient(135deg,#29352f,#798A80); color: white; }
@media(max-width: 980px) {
  .design-family-botanical-collage .real-photo-hero { grid-template-columns: 1fr; }
  .design-family-magazine-asymmetry .story-section { transform: none !important; }
}
"""


def concept_number(path: Path) -> int:
    return int(path.name.split("-", 1)[0])


def concept_label(path: Path) -> str:
    return path.name.split("-", 1)[1].replace("-", " ").title()


def pick(items: list[str], seed: int, salt: int) -> str:
    return items[(seed * 7 + salt * 3) % len(items)]


def photo_map(seed: int) -> dict[str, dict[str, str | int]]:
    return {
        "authority": pilot.cutout(pick(TRANSPARENT_IDS, seed, 1)),
        "warm": pilot.cutout(pick(TRANSPARENT_IDS, seed, 2)),
        "consult": pilot.cutout(pick(TRANSPARENT_IDS, seed, 3)),
        "precise": pilot.cutout(pick(TRANSPARENT_IDS, seed, 4)),
        "care": pilot.cutout(pick(TRANSPARENT_IDS, seed, 5)),
        "journal": pilot.cutout(pick(TRANSPARENT_IDS, seed, 6)),
        "profile": pilot.cutout(pick(TRANSPARENT_IDS, seed, 7)),
        "side": pilot.cutout(pick(TRANSPARENT_IDS, seed, 8)),
        "hero_opaque": pilot.opaque(pick(CATEGORY_IDS["hero"], seed, 9), "hero"),
        "soft_opaque": pilot.opaque(pick(CATEGORY_IDS["about"], seed, 10), "about"),
        "window_opaque": pilot.opaque(pick(CATEGORY_IDS["contact"], seed, 11), "contact"),
        "skin_opaque": pilot.opaque(pick(CATEGORY_IDS["skin"], seed, 12), "skin"),
    }


def data_for(concept: Path, page: str, family: tuple[str, str, str]) -> dict[str, object]:
    idx = concept_number(concept)
    label = concept_label(concept)
    data = copy.deepcopy(pilot.PAGE_DATA[page])
    data["title"] = f"{PAGE_PREFIX[page]} | {label} | Franciele Sofiati"
    data["description"] = f"{PAGE_PREFIX[page]} for Franciele Sofiati in Londrina, PR, with {family[2]}."
    data["eyebrow"] = f"{label} · cuidado, confiança, segurança, naturalidade"
    data["h1"] = PAGE_H1_VARIANTS[page][(idx + len(page)) % len(PAGE_H1_VARIANTS[page])]
    data["intro"] = f"{data['intro']} This {label} concept emphasizes {family[2]}."
    sections = data["sections"]
    rotate = idx % len(sections)
    data["sections"] = sections[rotate:] + sections[:rotate]
    cards = data["cards"]
    rotate_cards = idx % len(cards)
    data["cards"] = cards[rotate_cards:] + cards[:rotate_cards]
    return data


def add_body_class(tag: str, page: str, data: dict[str, object], family_slug: str, idx: int) -> str:
    match = re.search(r'class="([^"]*)"', tag)
    classes = match.group(1).split() if match else []
    for cls in ("sf-pilot-rebuild", "sf-global-rebuild", f"design-family-{family_slug}"):
        if cls not in classes:
            classes.append(cls)
    classes = [cls for cls in classes if not (cls.startswith("design-family-") and cls != f"design-family-{family_slug}")]
    tag = tag[: match.start(1)] + " ".join(classes) + tag[match.end(1) :] if match else tag.replace("<body", f'<body class="{" ".join(classes)}"', 1)
    vars_css = (
        f"--concept-hero-radius:{['0 0 92px 0','92px 0 92px 0','160px 160px 8px 8px','4px 96px 4px 96px','4px'][idx % 5]};"
        f"--concept-card-radius:{[4,18,32,56,2][idx % 5]}px;"
        f"--concept-photo-scale:{[0.94,1,1.04,1.08,0.98][idx % 5]};"
    )
    attrs = {
        "data-design-family": family_slug,
        "data-pilot-page": page,
        "data-page-title": str(data["title"]),
        "data-page-description": str(data["description"]),
        "style": vars_css,
    }
    for attr, value in attrs.items():
        if f"{attr}=" in tag:
            tag = re.sub(rf'{attr}="[^"]*"', f'{attr}="{value}"', tag, count=1)
        else:
            tag = tag[:-1] + f' {attr}="{value}">'
    return tag


def update_html(concept: Path, page: str, data: dict[str, object], family_slug: str) -> None:
    path = concept / f"{page}.html"
    html = path.read_text(encoding="utf-8")
    html = re.sub(r"<title>.*?</title>", f"<title>{data['title']}</title>", html, count=1, flags=re.S)
    html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{data["description"]}">', html, count=1)
    html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{data["title"]}">', html, count=1)
    html = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{data["description"]}">', html, count=1)
    html = re.sub(r'<meta name="twitter:title" content="[^"]*">', f'<meta name="twitter:title" content="{data["title"]}">', html, count=1)
    html = re.sub(r'<meta name="twitter:description" content="[^"]*">', f'<meta name="twitter:description" content="{data["description"]}">', html, count=1)
    idx = concept_number(concept)
    html = re.sub(r"<body([^>]*)>", lambda m: add_body_class(m.group(0), page, data, family_slug, idx), html, count=1)
    html = re.sub(r'<main id="main".*?</main>', pilot.main_html(page, data), html, count=1, flags=re.S)
    path.write_text(html, encoding="utf-8")


def update_css(concept: Path) -> None:
    path = concept / "css" / "style.css"
    css = path.read_text(encoding="utf-8")
    replacement = pilot.PILOT_CSS.replace(pilot.CSS_END, FAMILY_CSS + "\n" + pilot.CSS_END)
    css = re.sub(re.escape(pilot.CSS_START) + r".*?" + re.escape(pilot.CSS_END) + r"\n?", "", css, flags=re.S).rstrip()
    path.write_text(css + "\n\n" + replacement + "\n", encoding="utf-8")


def main() -> None:
    page_names = list(pilot.PAGE_DATA)
    results = []
    for concept in CONCEPTS:
        idx = concept_number(concept)
        family = FAMILIES[(idx - 1) // 5]
        pilot.PHOTOS = photo_map(idx)
        for page in page_names:
            update_html(concept, page, data_for(concept, page, family), family[0])
        update_css(concept)
        results.append({"concept": concept.name, "family": family[0], "pages": len(page_names)})
    print(json.dumps({"concepts": len(results), "pages_per_concept": len(page_names), "families": FAMILIES, "results_sample": results[:5]}, indent=2))


if __name__ == "__main__":
    main()
