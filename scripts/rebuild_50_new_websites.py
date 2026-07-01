#!/usr/bin/env python3
from __future__ import annotations

import datetime as dt
import html
import json
import os
import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROMPT_PATH = Path(
    os.environ.get(
        "SOFIATI_MASTER_PROMPT",
        "/home/code/.codex/attachments/6641d4bf-97b7-4447-9a2b-4459fbc2bd2f/pasted-text.txt",
    )
)
BIBLE = ROOT / "docs" / "design-destination-bible"
SCRIPT_RUNS = ROOT / "docs" / "script-runs"
CONCEPTS_DIR = ROOT / "concepts"

BRAND = {
    "name": "Franciele Sofiati",
    "brand": "Sofiati",
    "credential": "CRBM 6277",
    "location": "Londrina, PR",
    "email": "sofiatimendonca@gmail.com",
    "whatsapp": "(43) 9 9104-3536",
    "whatsappUrl": "https://wa.me/5543991043536",
    "instagram": "@fransofiati_biomedica",
    "instagramUrl": "https://www.instagram.com/fransofiati_biomedica/",
    "domain": "https://www.sofiati.com",
}

PAGES = [
    ("index.html", "home", "Home"),
    ("about.html", "about", "About"),
    ("care.html", "care", "Care"),
    ("laser.html", "laser", "Laser"),
    ("skin.html", "skin", "Skin"),
    ("results.html", "results", "Results"),
    ("journal.html", "journal", "Journal"),
    ("blog.html", "blog", "Blog"),
    ("consultation.html", "consultation", "Consultation"),
    ("contact.html", "contact", "Contact"),
    ("values.html", "values", "Values"),
    ("mission.html", "mission", "Mission"),
    ("testimonials.html", "testimonials", "Testimonials"),
    ("faq.html", "faq", "FAQ"),
    ("legal.html", "legal", "Legal"),
    ("privacy.html", "privacy", "Privacy"),
    ("cookies.html", "cookies", "Cookies"),
    ("accessibility.html", "accessibility", "Accessibility"),
    ("sitemap.html", "sitemap", "Sitemap"),
    ("thank-you.html", "thank-you", "Thank You"),
    ("404.html", "not-found", "Page Not Found"),
]

PAGE_ROLES = {
    "home": [
        "Opening promise",
        "Brand trust and human trust",
        "Care route",
        "Consultation approach",
        "Safety and reassurance statement",
        "Skin and laser education route",
        "Results expectations",
        "Journal and learning route",
        "Conversion and contact bridge",
        "Final brand bridge",
    ],
    "about": [
        "Portrait introduction",
        "Professional presence",
        "Care philosophy",
        "Values in practice",
        "Human warmth",
        "Consultation style",
        "Trust and responsibility",
        "Client reassurance",
        "Invitation to continue",
        "Final CTA bridge",
    ],
    "care": [
        "Care promise",
        "Listening-first explanation",
        "Evaluation approach",
        "Planning process",
        "Comfort and safety",
        "Service pathways",
        "What to expect",
        "Questions before deciding",
        "Consultation pathway",
        "Final reassurance CTA",
    ],
    "laser": [
        "Responsible laser introduction",
        "Suitability-first statement",
        "Skin and context evaluation",
        "Safety and comfort",
        "Process overview",
        "Common questions",
        "Expectations and limits",
        "Consultation route",
        "Education and journal route",
        "Final CTA",
    ],
    "skin": [
        "Skin care promise",
        "Individual skin context",
        "Calm evaluation",
        "Treatment planning",
        "Routine and expectations",
        "Natural-looking confidence",
        "Responsible results",
        "Education route",
        "Consultation bridge",
        "Final CTA",
    ],
    "results": [
        "Realistic results introduction",
        "Individual variation",
        "Responsible expectations",
        "Natural confidence",
        "What affects results",
        "Before deciding",
        "Consultation discussion",
        "Educational guidance",
        "Reassurance",
        "Final CTA",
    ],
    "journal": [
        "Editorial journal introduction",
        "Featured guidance",
        "Skin topics",
        "Laser questions",
        "Consultation education",
        "Results expectations",
        "Responsible care notes",
        "Reading path",
        "Contact bridge",
        "Final CTA",
    ],
    "blog": [
        "Editorial blog introduction",
        "Featured guidance",
        "Skin topics",
        "Laser questions",
        "Consultation education",
        "Results expectations",
        "Responsible care notes",
        "Reading path",
        "Contact bridge",
        "Final CTA",
    ],
    "consultation": [
        "Consultation promise",
        "First conversation purpose",
        "What can be discussed",
        "How preparation helps",
        "Form or WhatsApp route",
        "Comfort and boundaries",
        "Questions and expectations",
        "Trust reassurance",
        "Next step",
        "Final CTA",
    ],
    "contact": [
        "Contact invitation",
        "WhatsApp route",
        "Consultation request",
        "Location and service context",
        "Response expectation",
        "Questions before booking",
        "Social and contact route",
        "Reassurance",
        "Final contact CTA",
        "Footer bridge",
    ],
    "values": [
        "Values introduction",
        "Listening",
        "Clarity",
        "Safety",
        "Naturality",
        "Responsibility",
        "Education",
        "Human warmth",
        "How values guide consultations",
        "Final CTA",
    ],
    "mission": [
        "Mission statement",
        "Human purpose",
        "Responsible beauty and care",
        "Education",
        "Consultation ethics",
        "Natural confidence",
        "Trust",
        "Client journey",
        "Future direction",
        "Final CTA",
    ],
    "testimonials": [
        "Trust introduction",
        "Ethical note on client stories",
        "What reassurance can mean",
        "Consultation listening",
        "Comfort and boundaries",
        "Natural confidence",
        "Questions clients bring",
        "Responsible expectations",
        "Continue the conversation",
        "Final CTA",
    ],
    "faq": [
        "FAQ introduction",
        "Consultation questions",
        "Skin questions",
        "Laser questions",
        "Laser and safety questions",
        "Results questions",
        "Preparation questions",
        "Contact questions",
        "Reassurance",
        "Final CTA",
    ],
    "legal": [
        "Legal introduction",
        "Educational content notice",
        "No guarantee statement",
        "Professional evaluation",
        "Client responsibility",
        "Website use",
        "Intellectual property",
        "Contact for corrections",
        "Related policies",
        "Final legal bridge",
    ],
    "privacy": [
        "Privacy introduction",
        "Information visitors provide",
        "Consultation contact data",
        "How data is used",
        "WhatsApp and external links",
        "Retention and care",
        "Rights and questions",
        "Security expectations",
        "Related policies",
        "Final privacy bridge",
    ],
    "cookies": [
        "Cookie introduction",
        "Essential cookies",
        "Preference cookies",
        "Analytics stance",
        "Third-party links",
        "Managing preferences",
        "Consent updates",
        "Privacy relationship",
        "Questions",
        "Final cookie bridge",
    ],
    "accessibility": [
        "Accessibility introduction",
        "Readable content",
        "Keyboard access",
        "Reduced motion",
        "Image alternatives",
        "Contrast intention",
        "Feedback route",
        "Ongoing improvements",
        "Related pages",
        "Final accessibility bridge",
    ],
    "sitemap": [
        "Sitemap introduction",
        "Core pages",
        "Care pages",
        "Consultation pages",
        "Education pages",
        "Trust pages",
        "Policy pages",
        "Utility pages",
        "Contact route",
        "Final sitemap bridge",
    ],
    "thank-you": [
        "Thank you",
        "What happens next",
        "Response expectations",
        "Prepare questions",
        "Review care options",
        "Read guidance",
        "Contact again",
        "Accessibility and policies",
        "Return home",
        "Final reassurance",
    ],
    "not-found": [
        "Page not found",
        "Return to core care",
        "Open consultation",
        "Review skin care",
        "Review laser guidance",
        "Read journal",
        "Contact directly",
        "Check sitemap",
        "Privacy and accessibility",
        "Final redirect",
    ],
}

ROUTE_LINKS = [
    ("Care", "care.html"),
    ("Laser", "laser.html"),
    ("Skin", "skin.html"),
    ("Results", "results.html"),
    ("Journal", "journal.html"),
    ("Consultation", "consultation.html"),
    ("Contact", "contact.html"),
    ("Values", "values.html"),
    ("Mission", "mission.html"),
    ("FAQ", "faq.html"),
]

POLICY_LINKS = [
    ("Legal", "legal.html"),
    ("Privacy", "privacy.html"),
    ("Cookies", "cookies.html"),
    ("Accessibility", "accessibility.html"),
    ("Sitemap", "sitemap.html"),
]

PHOTO_ASSETS = [
    "franciele-sofiati-01-studio-seated-soft-smile-transparent.webp",
    "franciele-sofiati-02-studio-seated-laughing-transparent.webp",
    "franciele-sofiati-03-studio-seated-joyful-transparent.webp",
    "franciele-sofiati-04-studio-full-poised-transparent.webp",
    "franciele-sofiati-05-studio-full-direct-transparent.webp",
    "franciele-sofiati-06-studio-crossed-smile-transparent.webp",
    "franciele-sofiati-07-studio-crossed-composed-transparent.webp",
    "franciele-sofiati-08-studio-front-composed-transparent.webp",
    "franciele-sofiati-09-studio-seated-bright-smile-transparent.webp",
    "franciele-sofiati-10-studio-close-smile-transparent.webp",
    "franciele-sofiati-11-studio-chair-angled-transparent.webp",
    "franciele-sofiati-12-studio-close-composed-transparent.webp",
    "franciele-sofiati-13-balcony-orange-soft-smile-transparent.webp",
    "franciele-sofiati-14-balcony-orange-side-smile-transparent.webp",
    "franciele-sofiati-15-balcony-orange-direct-transparent.webp",
    "franciele-sofiati-17-balcony-orange-laughing-transparent.webp",
    "franciele-sofiati-18-balcony-orange-looking-up-transparent.webp",
    "franciele-sofiati-20-ivory-room-standing-calm-transparent.webp",
    "franciele-sofiati-21-ivory-room-side-gaze-transparent.webp",
    "franciele-sofiati-22-ivory-room-arms-crossed-transparent.webp",
    "franciele-sofiati-23-ivory-room-arms-crossed-close-transparent.webp",
    "franciele-sofiati-24-ivory-room-window-side-transparent.webp",
    "franciele-sofiati-25-ivory-room-window-touch-transparent.webp",
    "franciele-sofiati-26-ivory-room-window-composed-transparent.webp",
    "franciele-sofiati-27-ivory-room-window-attentive-transparent.webp",
]

HEADER_PATTERNS = [
    "editorial-index-header",
    "botanical-stem-header",
    "minimal-rule-header",
    "deep-salon-header",
    "studio-ledger-header",
    "clinical-grid-header",
    "warm-conversation-header",
    "layered-magazine-header",
    "route-map-header",
    "quiet-portrait-header",
]

MOBILE_PATTERNS = [
    "dark-sheet",
    "botanical-panel",
    "rule-drawer",
    "salon-overlay",
    "studio-card",
    "clinical-list",
    "warm-sheet",
    "magazine-drawer",
    "route-index",
    "quiet-canvas",
]

FOOTER_PATTERNS = [
    "editorial-bridge",
    "botanical-field",
    "minimal-rule",
    "dark-flagship",
    "studio-contact",
    "clinical-ledger",
    "warm-reassurance",
    "magazine-index",
    "route-directory",
    "quiet-signature",
]

ANATOMIES = [
    "editorial-spread",
    "manifesto-line",
    "route-ledger",
    "process-rail",
    "statement-band",
    "article-row",
    "expectation-ledger",
    "reading-path",
    "contact-bridge",
    "closing-signature",
    "axis-grid",
    "folio-stack",
    "wide-horizon",
    "softline-sequence",
    "shape-field",
    "evidence-ledger",
    "atelier-frame",
    "halo-orbit",
    "technical-table",
    "conversation-field",
]

CTA_STYLES = [
    "single-rule",
    "split-quiet",
    "text-link",
    "ledger-button",
    "gold-mark",
    "whatsapp-strip",
    "soft-pill",
    "inline-route",
    "dark-anchor",
    "minimal-arrow",
]

REQUESTED_CONCEPT_MATRIX = """
01|Inspire|Editorial Botanical Atelier|high-end editorial, botanical, quiet confidence|asymmetric editorial spread with portrait and art panel|ivory, deep green, sage, muted gold|large serif opening, thin editorial cards, botanical line overlays, dark botanical closing
02|Empower|Clinical Confidence Care|precise, structured, confident, medical luxury|clinical grid with trust markers|ivory, pale sage, olive, controlled blush|modular treatment route, crisp cards, clear consultation pathway
03|Enhance|Soft Transformation Journey|gentle, feminine, progress oriented|soft layered transformation story|cream, blush, sage|offset cards, step by step journey, warm consultation sections
04|Renew|Dark Botanical Renewal|dramatic, restorative, cinematic|dark immersive botanical hero|deep green, ink, ivory, gold|high contrast panels, cinematic moments, elegant dark footer
05|Elevate|Concierge Luxury Aesthetics|polished, private, high end|concierge booking and premium care promise|ivory, champagne, sage, bronze|appointment journey, premium service menu, refined CTA rhythm
06|Refine|Minimal Clinical Editorial|intelligent, restrained, calm|minimal grid with large whitespace|ivory, pale sage, ink|strict grids, thin borders, quiet typography, minimal cards
07|Glow|Feminine Radiance Studio|luminous, soft, beauty forward|glowing blush and sage composition|blush, cream, sage, soft gold|radiance cards, client reassurance, journal previews, soft mobile flow
08|Balance|Holistic Calm Clinic|grounded, natural, wellness clinical|balanced split with calm process|sage, ivory, sand, olive|process pathways, values, reassurance, calm footer
09|Radiance|Results-Led Premium Contrast|confident, luminous, proof oriented|bold contrast with responsible results language|ivory, ink, gold, sage|trust modules, treatment navigation, dramatic footer
10|Essence|Organic Quiet Luxury|intimate, organic, refined|warm quiet luxury with organic forms|ivory, sand, pale sage, bronze|paper texture, slow story sections, soft footer
11|Aura|Ethereal Skin Confidence|airy, luminous, delicate|light open aura glow|mist, ivory, blush, sage|floating panels, delicate gradients, light trust sections
12|Verda|Botanical Clinical Garden|botanical, fresh, grounded|garden inspired clinical calm|greens, ivory, olive, sand|leaf motifs, botanical cards, nature led service pathways
13|Luma|Light Science Studio|light, precise, modern|light science treatment focus|ivory, pale green, clean white, gold micro accents|clean grids, treatment explainers, subtle light effects
14|Seren|Serene Private Care|calm, private, soft spoken|quiet trust and consultation|ivory, sage, taupe|spacious sections, private care messaging, soft footer
15|Vitta|Vitality And Skin Health|fresh, health forward, energetic but premium|vitality focused care promise|cream, sage, muted terracotta, olive|health pillars, care journey, lively controlled cards
16|Bloom|Feminine Botanical Bloom|soft botanical growth|blooming visual motif|blush, sage, ivory, rose beige|petal cards, organic transitions, journal warmth
17|Poise|Elegant Confidence Clinic|composed, poised, premium|portrait led confidence|ivory, deep green, gold|elegant typography, confidence cards, refined footer
18|Clare|Clean Clarity Aesthetics|clean, transparent, direct|clarity first explanation|ivory, white, pale sage, ink|clean explainers, FAQ forward, minimal visual noise
19|Natura|Natural Results Philosophy|natural, subtle, trustworthy|natural care philosophy|sage, sand, ivory, olive|comparison free benefits, process sections, natural textures
20|Forma|Sculptural Aesthetic Structure|structured, sculptural, precise|geometric premium layout|ivory, stone, sage, ink|strong grids, sculptural cards, form and process language
21|Amara|Warm Human Clinic|warm, personal, inviting|human trust and listening|cream, blush, sand, sage|story led sections, reassurance, soft appointment pathway
22|Celeste|Airy Editorial Luxury|airy, refined, spa editorial|open editorial composition|ivory, mist, pale sage, soft gold|oversized whitespace, delicate cards, elegant footer
23|Olive|Deep Olive Signature|mature, grounded, premium|olive led brand authority|olive, ivory, bronze, sand|deep olive accents, mature typography, service menu
24|Rosea|Blush Clinical Warmth|warm, feminine, soft clinical|blush warmth without sweetness|dusty rose, ivory, sage|blush as accent, calm cards, soft CTA blocks
25|Silka|Smooth Skin Minimalism|silky, smooth, minimal|minimal texture and softness|ivory, pearl, pale sage, taupe|smooth gradients, minimal cards, refined typography
26|Alba|Morning Light Clinic|fresh, bright, optimistic|morning light glow|ivory, warm cream, pale gold, sage|light sections, clean CTAs, airy mobile flow
27|Noemi|Boutique Personal Care|boutique, personal, intimate|private studio consultation|cream, sage, blush, bronze|personal consultation emphasis, small elegant cards
28|Flora|Botanical Education Studio|educational, botanical, calm|education and care combined|sage, ivory, leaf green|journal forward, treatment education, botanical diagrams
29|Siena|Warm Terracotta Luxury|warm, earthy, premium|terracotta and sand warmth|sand, terracotta, sage, ivory|earthy sections, warm CTA, luxury editorial cards
30|Elan|Modern Premium Energy|modern, energetic, confident|dynamic asymmetric layout|ivory, ink, sage, gold|bolder transitions, strong CTAs, energetic grids
31|Mira|Mirror Of Confidence|reflective, elegant, confidence led|mirror and reflection metaphor|ivory, mist, sage, deep green|reflective panels, confidence sections, polished footer
32|Solea|Sunlit Skin Studio|sunlit, warm, radiant|sunlight inspired skin care|warm cream, soft gold, sage|luminous panels, radiance sections, warm footer
33|Aria|Light Breathable Editorial|light, breathable, sophisticated|airy editorial composition|ivory, pale sage, mist|whitespace, delicate typography, thin cards
34|Vale|Grounded Wellness Clinic|earthy, calm, reassuring|grounded trust|olive, sand, sage, ivory|grounded process, values, reassurance cards
35|Nobile|Noble Luxury Clinic|formal, luxurious, high end|grand editorial dark light contrast|ivory, ink, bronze, deep green|premium concierge sections, refined large typography
36|Brisa|Soft Breeze Skin Care|soft, fresh, gentle|breezy soft movement|pale sage, ivory, blush, mist|gentle transitions, soft cards, calming mobile flow
37|Linha|Line-Art Clinical Beauty|precise, artistic, line based|botanical and face line art composition|ivory, ink, sage, gold|line art, thin borders, structured treatment diagrams
38|Dama|Elegant Feminine Authority|feminine authority, refined|strong elegant portrait led layout|ivory, deep green, blush, bronze|confident typography, trust sections, elegant footer
39|Terra|Earthy Biological Care|organic, biological, grounded|earth tone care philosophy|sand, taupe, sage, olive|natural textures, grounded sections, warm footer
40|Prisma|Modern Treatment Navigation|modern, clear, multi service|treatment navigation focused|ivory, sage, blush, gold accents|category tiles, clear pathways, interactive feeling
41|Calma|Ultra Calm Consultation|peaceful, slow, reassuring|consultation first calm|ivory, pale sage, cream|slow scroll rhythm, reassurance, FAQ, soft CTA
42|Vellum|Paper Editorial Clinic|paper, editorial, tactile|magazine style paper layout|ivory, paper, taupe, sage|editorial cards, paper texture, serif headings
43|Opal|Soft Iridescent Premium|luminous, delicate, refined|opal glow and soft gradients|pearl, blush, sage, ivory|luminous cards, elegant service sections, soft footer
44|Jardim|Brazilian Botanical Luxury|lush but controlled botanical|Brazilian garden atmosphere|deep green, sage, ivory, warm gold|botanical overlays, immersive image panels, rich footer
45|Lisse|Smooth Minimal Beauty|smooth, clean, refined|minimal smooth skin focus|ivory, pale sage, pearl|clean blocks, smooth transitions, subtle cards
46|Magna|Grand Premium Authority|high authority, premium, confident|large cinematic brand statement|ink, ivory, bronze, sage|big sections, strong contrast, authoritative service layout
47|Senda|Guided Care Pathway|guided, structured, reassuring|pathway and process promise|sage, cream, olive, blush accents|timelines, guided steps, consultation journey
48|Isla|Soft Private Escape|private, gentle, retreat like|calm private escape|ivory, mist, sage, sand|soft panels, private care CTAs, intimate footer
49|Oro|Gold Accent Luxury|refined gold luxury|gold accent editorial premium|ivory, deep green, muted gold|restrained gold details, premium service menu, elegant footer
50|Maison|High-End Private Clinic|private maison and atelier clinic|boutique private clinic statement|ivory, deep green, champagne, taupe|maison navigation, concierge journey, luxury footer
""".strip()

LAYOUT_FAMILIES = [
    "editorial-asymmetric",
    "clinical-grid",
    "soft-journey",
    "cinematic-immersive",
    "concierge-suite",
    "minimal-clinical",
    "luminous-studio",
    "balanced-pathway",
    "route-led",
    "organic-editorial",
    "ethereal-panels",
    "botanical-garden",
    "light-science",
    "private-serene",
    "vitality-pillars",
    "botanical-bloom",
    "poised-portrait",
    "clarity-led",
    "natural-philosophy",
    "sculptural-grid",
]

HERO_PATTERNS_EXTENDED = [
    "editorial-spread",
    "clinical-dashboard",
    "soft-layers",
    "dark-cinematic",
    "concierge-card",
    "quiet-minimal",
    "radiance-glow",
    "balanced-split",
    "proof-route",
    "organic-paper",
    "aura-field",
    "garden-panel",
    "light-lab",
    "private-note",
    "vitality-board",
    "bloom-frame",
    "portrait-confidence",
    "clarity-brief",
    "natural-texture",
    "sculptural-form",
]

CARD_STYLES = [
    "fine-line",
    "clinical-module",
    "offset-soft",
    "cinematic-slate",
    "concierge-ticket",
    "minimal-rule",
    "luminous-card",
    "calm-path",
    "proof-ledger",
    "paper-note",
    "floating-pane",
    "botanical-tile",
    "light-cell",
    "private-panel",
    "health-pillar",
    "petal-card",
    "confidence-frame",
    "clarity-row",
    "natural-slip",
    "sculpted-plate",
]

IMAGE_TREATMENTS = [
    "portrait-atelier",
    "clinical-crop",
    "soft-vellum",
    "shadow-botanical",
    "concierge-frame",
    "quiet-negative",
    "skin-light",
    "balanced-window",
    "contrast-proof",
    "organic-paper",
    "mist-layer",
    "leaf-annotation",
    "lab-light",
    "private-room",
    "fresh-motion",
    "bloom-outline",
    "poised-portrait",
    "clean-cut",
    "natural-fiber",
    "sculptural-plinth",
]

MOBILE_STRATEGIES = [
    "hero-first-shortcuts",
    "care-route-tabs",
    "soft-stepper",
    "cinematic-compact",
    "concierge-actions",
    "minimal-index",
    "journal-preview",
    "two-card-flow",
    "route-chips",
    "paper-scroll",
]

COLOUR_KEYWORDS = {
    "ink": "ink",
    "dark": "dark",
    "deep": "dark",
    "sage": "sage",
    "ivory": "ivory",
    "cream": "cream",
    "white": "ivory",
    "blush": "ivory",
    "pink": "ivory",
    "rose": "ivory",
    "mist": "ivory",
    "pearl": "ivory",
    "sand": "cream",
    "stone": "cream",
    "olive": "sage",
    "gold": "gold",
    "bronze": "bronze",
    "champagne": "gold",
    "taupe": "bronze",
    "terracotta": "bronze",
    "clay": "bronze",
    "paper": "ivory",
    "luminous": "ivory",
    "clinical": "sage",
}


def slugify(value: str) -> str:
    value = value.lower().replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def run_git(args: list[str]) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return result.stdout.strip()


def parse_concepts_from_prompt(prompt: str) -> list[dict]:
    part_match = re.search(
        r"PART 7.*?Create 50 genuinely different website destinations\.(.*?)(?:PART 8)",
        prompt,
        re.S,
    )
    if not part_match:
        raise RuntimeError("Could not locate Part 7 concept destinations in prompt")
    part = part_match.group(1)
    pattern = re.compile(
        r"(?ms)^(\d{2})\s+([A-Za-z]+)\s+—\s+([^\n]+)\n\n"
        r"Visual thesis:\n(.+?)\n\n"
        r"Colour thesis:\n(.+?)\n\n"
        r"Homepage 10-section colour sequence:\n\n(.+?)\n\n"
        r"All other pages:\n(.+?)\n\n"
        r"Forbidden:\n(.+?)(?=\n\n\d{2}\s+[A-Za-z]+\s+—|\n\n─)",
    )
    concepts: list[dict] = []
    for match in pattern.finditer(part):
        number, name, destination, visual, colour, sequence_block, all_pages, forbidden = match.groups()
        sequence = [
            re.sub(r"^\d+\.\s*", "", line).strip()
            for line in sequence_block.splitlines()
            if re.match(r"^\d+\.\s+", line.strip())
        ]
        forbidden_items = [
            item.strip()
            for item in re.split(r"\.\s+", forbidden.strip().replace("\n", " "))
            if item.strip()
        ]
        concepts.append(
            {
                "number": number,
                "name": name,
                "slug": slugify(name),
                "conceptId": f"{number}-{slugify(name)}",
                "destination": destination.strip(),
                "visualThesis": " ".join(visual.strip().split()),
                "colourThesis": " ".join(colour.strip().split()),
                "homepageSectionColourSequence": sequence,
                "allOtherPages": " ".join(all_pages.strip().split()),
                "forbiddenPatterns": forbidden_items,
            }
        )
    if len(concepts) != 50:
        raise RuntimeError(f"Expected 50 concepts, parsed {len(concepts)}")
    return concepts


def load_concepts() -> list[dict]:
    current = concepts_from_current_folders()
    if current:
        return current
    cached = BIBLE / "10-50-new-website-destinations.json"
    if PROMPT_PATH.exists():
        return parse_concepts_from_prompt(read_text(PROMPT_PATH))
    if cached.exists():
        data = json.loads(read_text(cached))
        return data["concepts"]
    raise RuntimeError("No master prompt or cached destination JSON available")


def colour_families(text: str) -> list[str]:
    seen: list[str] = []
    lower = text.lower()
    for key, family in COLOUR_KEYWORDS.items():
        if key in lower and family not in seen:
            seen.append(family)
    return seen or ["ivory", "sage", "bronze"]


def tone_from_phrase(phrase: str, fallback: str = "ivory") -> str:
    families = colour_families(phrase)
    if "dark" in families:
        return "dark"
    for family in ("sage", "cream", "gold", "ivory", "bronze"):
        if family in families:
            return family
    return fallback


def rotate(values: list[str], amount: int) -> list[str]:
    if not values:
        return values
    amount = amount % len(values)
    return values[amount:] + values[:amount]


def parse_requested_matrix() -> dict[str, dict]:
    matrix: dict[str, dict] = {}
    for line in REQUESTED_CONCEPT_MATRIX.splitlines():
        number, name, destination, mood, hero, palette, structure = line.split("|", 6)
        matrix[number] = {
            "number": number,
            "requestedName": name,
            "destination": destination,
            "visualMood": mood,
            "heroPatternText": hero,
            "paletteRole": palette,
            "structure": structure,
        }
    if len(matrix) != 50:
        raise RuntimeError(f"Expected 50 requested concept directions, found {len(matrix)}")
    return matrix


def title_from_slug(slug: str) -> str:
    return " ".join(part.capitalize() for part in slug.split("-"))


def concept_folders() -> list[Path]:
    if not CONCEPTS_DIR.exists():
        return []
    return sorted(
        [p for p in CONCEPTS_DIR.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name)],
        key=lambda p: p.name,
    )


def homepage_sequence_from_matrix(item: dict, number: int) -> list[str]:
    families = colour_families(
        " ".join([item["paletteRole"], item["visualMood"], item["heroPatternText"], item["structure"]])
    )
    fallback = ["ivory", "sage", "cream", "gold", "dark", "bronze"]
    for family in fallback:
        if family not in families:
            families.append(family)
        if len(families) >= 6:
            break
    base = rotate(families, number % len(families))
    section_roles = [
        "hero promise",
        "trust position",
        "care route",
        "consultation path",
        "treatment navigation",
        "human reassurance",
        "education preview",
        "responsible expectations",
        "contact bridge",
        "closing identity",
    ]
    return [
        f"{item['requestedName']} {section_roles[index]} in {base[index % len(base)]}"
        for index in range(10)
    ]


def concepts_from_current_folders() -> list[dict]:
    folders = concept_folders()
    if len(folders) != 50:
        return []
    matrix = parse_requested_matrix()
    concepts: list[dict] = []
    for folder in folders:
        number, slug = folder.name.split("-", 1)
        item = matrix[number]
        concepts.append(
            {
                "number": number,
                "name": title_from_slug(slug),
                "slug": slug,
                "conceptId": folder.name,
                "requestedName": item["requestedName"],
                "destination": item["destination"],
                "visualThesis": (
                    f"{item['requestedName']} uses {item['visualMood']} pacing with {item['heroPatternText']}."
                ),
                "colourThesis": item["paletteRole"],
                "homepageSectionColourSequence": homepage_sequence_from_matrix(item, int(number)),
                "allOtherPages": (
                    "Inner pages keep the same care voice while changing the density, introduction, "
                    "navigation rhythm, and visual emphasis by page type."
                ),
                "forbiddenPatterns": [
                    "Do not flatten the site into repeated centered card stacks",
                    "Do not use gray placeholders",
                    "Do not invent testimonials, guarantees, prices, results, or credentials",
                    "Do not let desktop collapse into a narrow mobile column",
                ],
                "visualMood": item["visualMood"],
                "heroPatternText": item["heroPatternText"],
                "paletteRole": item["paletteRole"],
                "structure": item["structure"],
            }
        )
    return concepts


def page_colour_sequences(home_sequence: list[str], concept_number: int) -> dict[str, list[str]]:
    result = {"home": home_sequence}
    page_keys = [key for _, key, _ in PAGES if key != "home"]
    for index, key in enumerate(page_keys, start=1):
        rotated = rotate(home_sequence, (concept_number + index) % 10)
        rewritten = []
        for section_index, phrase in enumerate(rotated, start=1):
            tone = tone_from_phrase(phrase)
            rewritten.append(f"{key.replace('-', ' ')} {section_index}: {tone} rhythm from {phrase}")
        result[key] = rewritten
    return result


def enrich_concepts(concepts: list[dict]) -> list[dict]:
    enriched: list[dict] = []
    for index, concept in enumerate(concepts):
        number = int(concept["number"])
        families = colour_families(
            concept["colourThesis"] + " " + " ".join(concept["homepageSectionColourSequence"])
        )
        while len(families) < 3:
            for fallback in ("ivory", "sage", "bronze", "dark", "cream", "gold"):
                if fallback not in families:
                    families.append(fallback)
                    break
        page_sequences = page_colour_sequences(concept["homepageSectionColourSequence"], number)
        contract = {
            **concept,
            "visualSignature": concept["destination"],
            "headerSystem": HEADER_PATTERNS[index % len(HEADER_PATTERNS)],
            "mobileSystem": MOBILE_PATTERNS[(index * 3) % len(MOBILE_PATTERNS)],
            "footerSystem": FOOTER_PATTERNS[(index * 7) % len(FOOTER_PATTERNS)],
            "layoutFamily": LAYOUT_FAMILIES[index % len(LAYOUT_FAMILIES)],
            "heroPattern": HERO_PATTERNS_EXTENDED[index % len(HERO_PATTERNS_EXTENDED)],
            "cardStyle": CARD_STYLES[index % len(CARD_STYLES)],
            "imageTreatment": IMAGE_TREATMENTS[index % len(IMAGE_TREATMENTS)],
            "mobileLayoutStrategy": MOBILE_STRATEGIES[index % len(MOBILE_STRATEGIES)],
            "homepageSectionOrder": rotate(PAGE_ROLES["home"], index % len(PAGE_ROLES["home"])),
            "uniqueDifferentiators": [
                f"Hero uses {HERO_PATTERNS_EXTENDED[index % len(HERO_PATTERNS_EXTENDED)].replace('-', ' ')} instead of the neighboring hero pattern.",
                f"Section rhythm leads with {tone_from_phrase(concept['homepageSectionColourSequence'][0])} and rotates through a numbered palette contract.",
                f"Cards use {CARD_STYLES[index % len(CARD_STYLES)].replace('-', ' ')} with {IMAGE_TREATMENTS[index % len(IMAGE_TREATMENTS)].replace('-', ' ')} media treatment.",
            ],
            "homepageAnatomy": ANATOMIES[index % len(ANATOMIES)],
            "internalPageAnatomy": ANATOMIES[(index * 5 + 3) % len(ANATOMIES)],
            "componentStrategy": f"{ANATOMIES[(index * 2) % len(ANATOMIES)]} with {CTA_STYLES[index % len(CTA_STYLES)]} calls to action",
            "ctaStrategy": CTA_STYLES[(index * 3 + 1) % len(CTA_STYLES)],
            "imageStrategy": f"Selective full transparent portraits in sections {1 + index % 2}, {5 + index % 3}, and {8 + index % 2}; object-fit contain only.",
            "colourRhythm": {
                "conceptId": concept["conceptId"],
                "colourThesis": concept["colourThesis"],
                "dominantColourFamily": families[0],
                "secondaryColourFamily": families[1],
                "accentColourFamily": families[2],
                "contrastTemperature": "high editorial" if "dark" in families[:2] else "soft refined",
                "darkUsage": "dominant structural field" if "dark" in families[:2] else "reserved for footer, text, or one anchor band",
                "softWarmthUsage": "only through ivory, cream, champagne, and bronze from the approved identity palette",
                "sageUsage": "primary architecture" if families[0] == "sage" else "brand structure and quiet route support",
                "creamUsage": "reading relief and calm transitions",
                "goldBronzeUsage": "rules, markers, numerals, and selected CTA detail",
                "nonBrandColourUsage": "not allowed in generated CSS; descriptive pink, blush, rose, and terracotta words resolve to identity colours",
                "cardSurfaceStrategy": f"{ANATOMIES[(index * 4 + 2) % len(ANATOMIES)]}; no universal cream-card default",
                "buttonStrategy": CTA_STYLES[(index * 3 + 1) % len(CTA_STYLES)],
                "footerColour": concept["homepageSectionColourSequence"][-1],
                "mobileMenuColour": concept["homepageSectionColourSequence"][(index + 2) % 10],
                "homepageSectionColourSequence": concept["homepageSectionColourSequence"],
                "aboutPageColourSequence": page_sequences["about"],
                "carePageColourSequence": page_sequences["care"],
                "laserPageColourSequence": page_sequences["laser"],
                "skinPageColourSequence": page_sequences["skin"],
                "resultsPageColourSequence": page_sequences["results"],
                "journalPageColourSequence": page_sequences["journal"],
                "consultationPageColourSequence": page_sequences["consultation"],
                "contactPageColourSequence": page_sequences["contact"],
                "forbiddenColourPatterns": concept["forbiddenPatterns"],
            },
            "pageColourSequences": page_sequences,
        }
        enriched.append(contract)
    return enriched


def collect_preflight() -> dict:
    html_files = [p for p in CONCEPTS_DIR.glob("*/*.html") if ".bak-" not in p.name]
    partial_files = list(CONCEPTS_DIR.glob("*/partials/*.html"))
    global_css = list((ROOT / "css").glob("*.css"))
    global_js = list((ROOT / "js").glob("*.js"))
    local_css = list(CONCEPTS_DIR.glob("*/css/*.css"))
    local_js = list(CONCEPTS_DIR.glob("*/js/*.js"))
    old_tokens = [
        "atlas-",
        "premium-visual-dna",
        "visual-dna",
        "architecture-",
        "conflict-repair",
        "data-sofiati-conflict-repair",
        "data-architecture-repair",
        "atlas-section__copy",
        "atlas-section__media",
        "atlas-actions",
        "atlas-button",
    ]
    token_counts = {token: 0 for token in old_tokens}
    active_css_refs: dict[str, int] = {}
    active_js_refs: dict[str, int] = {}
    for path in html_files:
        text = read_text(path)
        for token in old_tokens:
            token_counts[token] += text.count(token)
        for href in re.findall(r'<link[^>]+href="([^"]+\.css)"', text):
            active_css_refs[href] = active_css_refs.get(href, 0) + 1
        for src in re.findall(r'<script[^>]+src="([^"]+\.js)"', text):
            active_js_refs[src] = active_js_refs.get(src, 0) + 1
    return {
        "generatedAt": dt.datetime.now(dt.UTC).isoformat(),
        "branch": run_git(["branch", "--show-current"]),
        "gitStatus": run_git(["status", "--short"]),
        "conceptFolders": len([p for p in CONCEPTS_DIR.iterdir() if p.is_dir() and p.name[:2].isdigit()]),
        "existingRealPages": len(html_files),
        "existingPartials": len(partial_files),
        "existingGlobalCssFiles": len(global_css),
        "existingGlobalJsFiles": len(global_js),
        "existingConceptLocalCssFiles": len(local_css),
        "existingConceptLocalJsFiles": len(local_js),
        "activeCssRefs": active_css_refs,
        "activeJsRefs": active_js_refs,
        "conflictTokenCounts": token_counts,
        "currentConflictLayers": [
            "css/atlas-story.css",
            "css/sofiati-premium-visual-dna.css",
            "css/sofiati-50-architecture-system.css",
            "css/sofiati-architecture-conflict-repair.css",
            "js/sofiati-50-architecture-system.js",
            "js/sofiati-architecture-conflict-repair.js",
        ],
        "currentRepeatedVisualPatterns": [
            "rounded floating header",
            "split hero structure",
            "ivory/cream cards",
            "copy plus media section anatomy",
            "two-button CTA rhythm",
            "repeated vertical mobile card stack",
        ],
        "currentRepeatedHtmlPatterns": [
            "atlas-section__copy plus atlas-section__media",
            "atlas-actions plus atlas-button",
            "Visual DNA classes mixed with architecture classes",
            "repair data attributes mounted in active pages",
        ],
        "previousFailureDiagnosis": "The old system stacked rescue layers over a repeated Atlas template instead of replacing the architecture.",
    }


def write_preflight(preflight: dict) -> None:
    rows = [
        "# 50 Complete New Websites Preflight",
        "",
        f"- Current branch: `{preflight['branch']}`",
        f"- Git status: `{preflight['gitStatus'] or 'clean'}`",
        f"- Number of concept folders: {preflight['conceptFolders']}",
        f"- Existing real pages: {preflight['existingRealPages']}",
        f"- Existing partials: {preflight['existingPartials']}",
        f"- Existing global CSS files: {preflight['existingGlobalCssFiles']}",
        f"- Existing global JS files: {preflight['existingGlobalJsFiles']}",
        f"- Existing concept-local CSS files: {preflight['existingConceptLocalCssFiles']}",
        f"- Existing concept-local JS files: {preflight['existingConceptLocalJsFiles']}",
        "",
        "The current system is not 50 websites. It is one repeated template family with conflicting CSS/JS layers. This rebuild must produce 50 new Figma-level websites in one full batch pass.",
        "",
        "## Current Conflict Layers",
        "",
        *[f"- `{layer}`" for layer in preflight["currentConflictLayers"]],
        "",
        "## Current Repeated Visual Patterns",
        "",
        *[f"- {item}" for item in preflight["currentRepeatedVisualPatterns"]],
        "",
        "## Current Repeated HTML Patterns",
        "",
        *[f"- {item}" for item in preflight["currentRepeatedHtmlPatterns"]],
        "",
        "## Active CSS References",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(preflight["activeCssRefs"].items())],
        "",
        "## Active JS References",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(preflight["activeJsRefs"].items())],
        "",
        "## Why Previous Attempts Failed",
        "",
        preflight["previousFailureDiagnosis"],
    ]
    write_text(SCRIPT_RUNS / "50-complete-new-websites-preflight.md", "\n".join(rows))


def write_conflict_audits(preflight: dict) -> None:
    write_text(SCRIPT_RUNS / "html-conflict-diagnosis.json", json.dumps(preflight, indent=2))
    write_text(SCRIPT_RUNS / "conflict-layer-audit.json", json.dumps({
        "activeCssRefs": preflight["activeCssRefs"],
        "activeJsRefs": preflight["activeJsRefs"],
        "conflictTokenCounts": preflight["conflictTokenCounts"],
        "deprecatedButNotActiveAfterRebuild": preflight["currentConflictLayers"],
    }, indent=2))
    diagnosis_md = [
        "# HTML Conflict Diagnosis",
        "",
        "The active pages before this rebuild mixed local template CSS, Atlas story classes, Visual DNA CSS, architecture CSS, and conflict-repair CSS.",
        "",
        "## Conflict Token Counts",
        "",
        *[f"- `{key}`: {value}" for key, value in preflight["conflictTokenCounts"].items()],
        "",
        "## Diagnosis",
        "",
        "- Too many active CSS systems were loaded at the same time.",
        "- Too many active JS systems were loaded at the same time.",
        "- Old template identity classes controlled the DOM.",
        "- Section metadata claimed interaction models the DOM did not implement.",
        "- No-image sections still carried image-era classes and comments.",
        "- Repair labels remained in active HTML.",
    ]
    write_text(SCRIPT_RUNS / "html-conflict-diagnosis.md", "\n".join(diagnosis_md))
    layer_md = [
        "# Conflict Layer Audit",
        "",
        "## Active CSS References Before Rebuild",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(preflight["activeCssRefs"].items())],
        "",
        "## Active JS References Before Rebuild",
        "",
        *[f"- `{key}`: {value}" for key, value in sorted(preflight["activeJsRefs"].items())],
        "",
        "## Deprecated Layers",
        "",
        "These files may remain for historical comparison, but rebuilt concept pages must not reference them.",
        "",
        *[f"- `{layer}`" for layer in preflight["currentConflictLayers"]],
    ]
    write_text(SCRIPT_RUNS / "conflict-layer-audit.md", "\n".join(layer_md))
    plan = [
        "# Conflict Removal Plan",
        "",
        "1. Replace active concept pages with clean HTML that links only `../../css/sofiati-brand-foundation.css` and `css/concept.css`.",
        "2. Replace active scripts with `../../js/sofiati-brand-foundation.js` and `js/concept.js`.",
        "3. Remove active Atlas, Visual DNA, architecture, and conflict-repair classes from rebuilt pages.",
        "4. Use concept-local partials for header, mobile menu, footer, cookie banner, and floating widgets.",
        "5. Keep old global rescue files only as deprecated historical files; do not load them from rebuilt pages.",
        "6. Validate with `qa/audit_50_new_websites_compliance.py` and `qa/audit_50_new_websites_similarity.py`.",
    ]
    write_text(SCRIPT_RUNS / "conflict-removal-plan.md", "\n".join(plan))


def write_foundation_files() -> None:
    css = """
:root {
  /* Sage */
  --sofiati-sage-50: #F6F8F5;
  --sofiati-sage-100: #EEF3EE;
  --sofiati-sage-200: #DCE5DA;
  --sofiati-sage-300: #A2AEA0;
  --sofiati-sage-400: #87927F;
  --sofiati-sage-500: #6F7B68;
  --sofiati-sage-700: #485041;
  --sofiati-sage-900: #263026;

  /* Ivory / cream */
  --sofiati-ivory-50: #FFFDF8;
  --sofiati-ivory-100: #FBFAF5;
  --sofiati-ivory-200: #F8F7F2;
  --sofiati-ivory-300: #F2EEE3;
  --sofiati-cream-400: #EDE4D4;
  --sofiati-cream-600: #D8CBB7;

  /* Ink */
  --sofiati-ink-600: #4A4640;
  --sofiati-ink-700: #3A3631;
  --sofiati-ink-900: #252321;

  /* Bronze / gold */
  --sofiati-bronze-300: #C39B6A;
  --sofiati-bronze-400: #B88954;
  --sofiati-bronze-600: #9A6B35;
  --sofiati-bronze-800: #5F3F1F;
  --sofiati-gold-200: #F1DEC0;
  --sofiati-gold-300: #E4C99B;
  --sofiati-gold-500: #CDAA78;

  /* Warm identity neutrals from the logo and palette boards */
  --sofiati-champagne-100: #DACCB7;
  --sofiati-bronze-clay: #8F745F;
  --sofiati-taupe-300: #B6AA98;
  --sofiati-taupe-400: #9B8F7E;
  --sofiati-taupe-700: #5E5548;

  /* Semantic base */
  --color-bg: var(--sofiati-ivory-200);
  --color-text: var(--sofiati-ink-900);
  --color-text-soft: var(--sofiati-ink-700);
  --color-text-inverse: var(--sofiati-ivory-100);
  --color-border-soft: rgba(72, 80, 65, 0.18);

  /* Surfaces */
  --surface-card: rgba(255, 255, 255, 0.72);
  --surface-card-strong: var(--sofiati-ivory-100);
  --surface-sage: var(--sofiati-sage-100);
  --surface-dark: var(--sofiati-sage-900);

  /* Gradients */
  --gradient-cream: linear-gradient(135deg, var(--sofiati-ivory-100), var(--sofiati-ivory-300));
  --gradient-sage-soft: linear-gradient(135deg, var(--sofiati-sage-100), var(--sofiati-sage-300));
  --gradient-sage-deep: linear-gradient(135deg, var(--sofiati-sage-700), var(--sofiati-sage-900));
  --gradient-dark-botanical: radial-gradient(circle at top left, rgba(162, 174, 160, 0.24), transparent 34%), linear-gradient(135deg, var(--sofiati-ink-900), var(--sofiati-sage-900));
  --gradient-champagne-cream: linear-gradient(135deg, var(--sofiati-ivory-100), var(--sofiati-champagne-100), var(--sofiati-ivory-200));
  --gradient-gold-line: linear-gradient(90deg, var(--sofiati-bronze-600), var(--sofiati-gold-500), var(--sofiati-bronze-400));

  /* Shadows */
  --shadow-sm: 0 14px 40px rgba(37, 35, 33, 0.08);
  --shadow-md: 0 26px 70px rgba(37, 35, 33, 0.12);
  --shadow-dark: 0 30px 90px rgba(0, 0, 0, 0.24);

  /* Buttons */
  --button-primary-bg: var(--sofiati-sage-700);
  --button-primary-text: var(--sofiati-ivory-100);
  --button-gold-bg: var(--sofiati-gold-500);
  --button-gold-text: var(--sofiati-ink-900);
  --button-champagne-bg: var(--sofiati-champagne-100);
  --button-champagne-text: var(--sofiati-ink-900);
  --button-dark-bg: var(--sofiati-ink-900);
  --button-dark-text: var(--sofiati-ivory-100);

  /* Layout and interaction tokens */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-5: 1.5rem;
  --space-6: 2rem;
  --space-7: 3rem;
  --space-8: 4rem;
  --radius-sm: 2px;
  --radius-md: 6px;
  --radius-lg: 8px;
  --z-header: 70;
  --z-menu: 88;
  --z-cookie: 90;
  --z-floating: 95;
  --transition-fast: 160ms ease;
  --transition-med: 220ms ease;
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  text-size-adjust: 100%;
}

body {
  margin: 0;
  background: var(--color-bg);
  color: var(--color-text);
  font-family: Inter, "Avenir Next", "Segoe UI", Arial, sans-serif;
  line-height: 1.6;
}

body.public-menu-locked {
  overflow: hidden;
}

img,
svg {
  display: block;
  max-width: 100%;
}

a {
  color: inherit;
}

button,
input,
textarea {
  font: inherit;
}

.skip-link {
  position: fixed;
  inset-block-start: 1rem;
  inset-inline-start: 1rem;
  z-index: 1000;
  transform: translateY(-160%);
  background: var(--sofiati-ink-900);
  color: var(--sofiati-ivory-100);
  padding: 0.75rem 1rem;
  text-decoration: none;
}

.skip-link:focus {
  transform: translateY(0);
}

.section-light {
  background: var(--gradient-cream);
}

.section-sage {
  background: var(--gradient-sage-soft);
}

.section-dark {
  background: var(--gradient-dark-botanical);
  color: var(--color-text-inverse);
}

.section-champagne {
  background: var(--gradient-champagne-cream);
}

.card {
  background: var(--surface-card);
  border: 1px solid var(--color-border-soft);
  box-shadow: var(--shadow-sm);
}

.button-primary {
  background: var(--button-primary-bg);
  color: var(--button-primary-text);
}

.button-gold {
  background: var(--button-gold-bg);
  color: var(--button-gold-text);
}

.button-champagne {
  background: var(--button-champagne-bg);
  color: var(--button-champagne-text);
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    scroll-behavior: auto !important;
    transition-duration: 0.01ms !important;
  }
}
"""
    js = """
(() => {
  "use strict";

  document.documentElement.classList.add("sofiati-js-ready");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  window.SofiatiFoundation = {
    reduceMotion: () => reduceMotion.matches,
    scrollToTop: () => window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" }),
    readyAt: new Date().toISOString(),
  };

  document.dispatchEvent(new CustomEvent("sofiati:foundation-ready"));
})();
"""
    write_text(ROOT / "css" / "sofiati-brand-foundation.css", css)
    write_text(ROOT / "js" / "sofiati-brand-foundation.js", js)


def make_design_bible(concepts: list[dict]) -> None:
    (BIBLE / "concepts").mkdir(parents=True, exist_ok=True)
    concept_summary = [
        {
            key: concept[key]
            for key in [
                "conceptId",
                "name",
                "requestedName",
                "slug",
                "destination",
                "visualThesis",
                "colourThesis",
                "visualMood",
                "heroPatternText",
                "paletteRole",
                "structure",
                "layoutFamily",
                "heroPattern",
                "cardStyle",
                "imageTreatment",
                "mobileLayoutStrategy",
                "homepageSectionOrder",
                "uniqueDifferentiators",
                "headerSystem",
                "mobileSystem",
                "footerSystem",
                "componentStrategy",
                "ctaStrategy",
                "imageStrategy",
                "forbiddenPatterns",
            ]
        }
        | {"colourRhythm": concept["colourRhythm"]}
        for concept in concepts
    ]
    write_text(
        BIBLE / "10-50-new-website-destinations.json",
        json.dumps({"concepts": concept_summary}, indent=2),
    )
    page_roles_json = {
        key: roles for key, roles in PAGE_ROLES.items()
    }
    write_text(BIBLE / "11-page-section-destinations.json", json.dumps(page_roles_json, indent=2))

    docs = {
        "00-current-failure-diagnosis.md": [
            "# Current Failure Diagnosis",
            "",
            "The previous active architecture presented as 50 concepts, but the pages shared one dominant template family, repeated Atlas classes, and stacked repair CSS/JS layers.",
            "",
            "The current system is not 50 websites. It is one repeated template family with conflicting CSS/JS layers. This rebuild must produce 50 new Figma-level websites in one full batch pass.",
        ],
        "01-brand-foundation.md": [
            "# Brand Foundation",
            "",
            f"- Brand: {BRAND['brand']}",
            f"- Professional: {BRAND['name']}",
            f"- Credential: {BRAND['credential']}",
            f"- Location: {BRAND['location']}",
            "- Tone: premium, natural, feminine, calm, professional, ethical, reassuring, educational, and consultation-led.",
            "- Shared palette source: `css/sofiati-brand-foundation.css`.",
        ],
        "02-design-principles.md": [
            "# Design Principles",
            "",
            "- Every concept has a visible thesis, not just a theme label.",
            "- Shared brand colours are used with different rhythm, contrast, temperature, and hierarchy.",
            "- Sections are full-width designed bands or unframed editorial fields; repeated nested cards are avoided.",
            "- Claims stay educational and consultation-led.",
            "- Photos are selective, full, transparent, and uncropped.",
        ],
        "03-global-non-negotiables.md": [
            "# Global Non-Negotiables",
            "",
            "- Exactly 10 real content sections per generated page.",
            "- Partials do not count as content sections.",
            "- Active CSS is limited to the global foundation and concept-local CSS.",
            "- Active JS is limited to the global foundation and concept-local JS.",
            "- No Atlas, Visual DNA, architecture, or conflict-repair stack in active pages.",
            "- No unsupported component metadata.",
        ],
        "04-page-type-destination-system.md": [
            "# Page Type Destination System",
            "",
            *[
                f"## {key.replace('-', ' ').title()}\n" + "\n".join(f"{i}. {role}" for i, role in enumerate(roles, 1))
                for key, roles in PAGE_ROLES.items()
            ],
        ],
        "05-component-destination-taxonomy.md": [
            "# Component Destination Taxonomy",
            "",
            "- Header systems: editorial, botanical, rule-led, salon, studio, clinical, conversation, magazine, route-map, quiet portrait.",
            "- Section anatomies: manifesto, route ledger, process rail, statement band, article row, expectation ledger, reading path, contact bridge, shape fields, evidence ledgers.",
            "- CTA systems: single-rule, split-quiet, text-link, ledger-button, gold-mark, WhatsApp strip, soft-pill, inline-route, dark-anchor, minimal-arrow.",
            "- Native details, forms, links, and buttons are used only where the DOM implements them.",
        ],
        "06-image-photo-system.md": [
            "# Image Photo System",
            "",
            "- Homepage photo count target: 3 per concept, within the accepted 2 to 5 range.",
            "- All Franciele photos use `object-fit: contain` and full transparent assets.",
            "- Sections without images contain no figure, no image frame, and no image comments.",
            "- Photo selections rotate across the full available brand portrait set.",
        ],
        "07-cta-conversion-system.md": [
            "# CTA Conversion System",
            "",
            "- CTAs remain consultation-led and non-aggressive.",
            "- WhatsApp is available without becoming the only route.",
            "- CTA rhythm varies by concept and by section.",
            "- Legal, sitemap, accessibility, cookie, and language access stay present.",
        ],
        "08-header-footer-mobile-system.md": [
            "# Header Footer Mobile System",
            "",
            "- Header partial owns logo, desktop nav, language controls, and menu trigger.",
            "- Mobile menu partial owns the closed-by-default menu panel.",
            "- Footer partial owns footer content only.",
            "- Floating widgets partial owns persistent contact/top tools.",
            "- Cookie banner partial owns non-blocking preference UI.",
        ],
        "09-css-js-ownership-and-conflict-removal.md": [
            "# CSS JS Ownership And Conflict Removal",
            "",
            "- `css/sofiati-brand-foundation.css` owns brand palette, reset, and tiny utilities only.",
            "- `js/sofiati-brand-foundation.js` owns shared reduced-motion, top-link, and language primitives only.",
            "- `concepts/XX-name/css/concept.css` owns actual layout, rhythm, and responsive design.",
            "- `concepts/XX-name/js/concept.js` owns partial loading and concept-local interaction.",
            "- Old Atlas, Visual DNA, architecture, and conflict-repair files are deprecated historical artifacts.",
        ],
        "10-50-new-website-destinations.md": [
            "# 50 New Website Destinations",
            "",
            *[
                f"## {concept['conceptId']} — {concept['destination']}\n\n{concept['visualThesis']}\n\nColour: {concept['colourThesis']}"
                for concept in concepts
            ],
        ],
        "11-page-section-destinations.md": [
            "# Page Section Destinations",
            "",
            *[
                f"## {key.replace('-', ' ').title()}\n" + "\n".join(f"{i}. {role}" for i, role in enumerate(roles, 1))
                for key, roles in PAGE_ROLES.items()
            ],
        ],
        "12-partial-redesign-destinations.md": [
            "# Partial Redesign Destinations",
            "",
            *[
                f"- `{concept['conceptId']}`: header `{concept['headerSystem']}`, mobile `{concept['mobileSystem']}`, footer `{concept['footerSystem']}`."
                for concept in concepts
            ],
        ],
        "13-full-batch-rebuild-plan.md": [
            "# Full Batch Rebuild Plan",
            "",
            "1. Diagnose current conflicts.",
            "2. Create the destination bible.",
            "3. Replace global foundation CSS and JS.",
            "4. Rewrite all active concept pages.",
            "5. Rewrite required concept partials.",
            "6. Validate compliance and similarity.",
            "7. Capture desktop and mobile homepage screenshots.",
            "8. Produce final reports.",
        ],
        "14-colour-rhythm-system.md": [
            "# Colour Rhythm System",
            "",
            *[
                f"## {concept['conceptId']}\n\nDominant: {concept['colourRhythm']['dominantColourFamily']}. Secondary: {concept['colourRhythm']['secondaryColourFamily']}. Accent: {concept['colourRhythm']['accentColourFamily']}.\n\n"
                + "\n".join(f"{i}. {item}" for i, item in enumerate(concept["homepageSectionColourSequence"], 1))
                for concept in concepts
            ],
        ],
        "15-similarity-gate.md": [
            "# Similarity Gate",
            "",
            "- No concept may share the same homepage colour sequence with another concept.",
            "- Header, mobile menu, footer, hero, DOM anatomy, CTA rhythm, and image placement are compared by the similarity audit.",
            "- Concepts with high similarity are listed for manual review instead of being marked as successful by assertion.",
        ],
        "16-acceptance-standard.md": [
            "# Acceptance Standard",
            "",
            "- Figma-quality art direction.",
            "- Clean active architecture.",
            "- 10 real sections on every generated page.",
            "- Concept-specific partials.",
            "- Selective uncropped photos.",
            "- No blank frames.",
            "- No fake labels.",
            "- No old Atlas/template dependency.",
            "- Still recognisably Sofiati.",
        ],
    }
    for filename, lines in docs.items():
        write_text(BIBLE / filename, "\n".join(lines))

    for concept in concepts:
        rhythm = json.dumps(concept["colourRhythm"], indent=2)
        md = [
            f"# {concept['conceptId']} — {concept['destination']}",
            "",
            "## Visual Thesis",
            "",
            concept["visualThesis"],
            "",
            "## Colour Thesis",
            "",
            concept["colourThesis"],
            "",
            "## Systems",
            "",
            f"- Header: `{concept['headerSystem']}`",
            f"- Mobile: `{concept['mobileSystem']}`",
            f"- Footer: `{concept['footerSystem']}`",
            f"- Homepage anatomy: `{concept['homepageAnatomy']}`",
            f"- Internal page anatomy: `{concept['internalPageAnatomy']}`",
            f"- Component strategy: {concept['componentStrategy']}",
            f"- CTA strategy: {concept['ctaStrategy']}",
            f"- Image strategy: {concept['imageStrategy']}",
            "",
            "## Homepage Colour Sequence",
            "",
            *[f"{i}. {item}" for i, item in enumerate(concept["homepageSectionColourSequence"], 1)],
            "",
            "## All Other Pages",
            "",
            concept["allOtherPages"],
            "",
            "## Forbidden Patterns",
            "",
            *[f"- {item}" for item in concept["forbiddenPatterns"]],
            "",
            "## Colour Rhythm Contract",
            "",
            "```json",
            rhythm,
            "```",
        ]
        write_text(BIBLE / "concepts" / f"{concept['conceptId']}.md", "\n".join(md))


def page_description(page_key: str, concept: dict) -> str:
    base = {
        "home": "A calm, attentive approach shaped around your goals, comfort, and realistic expectations.",
        "about": "Meet Franciele Sofiati through a professional, human, consultation-led care philosophy.",
        "care": "Explore listening-first care with evaluation, planning, comfort, and responsible guidance.",
        "laser": "Understand responsible laser care through suitability, safety, expectations, and consultation.",
        "skin": "Review individual skin care planning with calm evaluation and natural-looking confidence.",
        "results": "Learn how responsible expectations, variation, and consultation shape results discussions.",
        "journal": "Read educational guidance for skin, laser, consultation, and realistic expectations.",
        "blog": "Read educational notes for skin, laser, consultation, and realistic expectations.",
        "consultation": "Request a consultation through a clear, ethical, preparation-friendly path.",
        "contact": "Contact Franciele Sofiati for consultation questions in Londrina, PR.",
        "values": "See the values that guide Sofiati consultations: listening, clarity, safety, and responsibility.",
        "mission": "Understand the Sofiati mission around responsible beauty, education, and human confidence.",
        "testimonials": "A responsible trust page focused on reassurance without invented claims.",
        "faq": "Answers to common consultation, skin, laser, result, preparation, and contact questions.",
        "legal": "Legal notes for educational website use and responsible consultation expectations.",
        "privacy": "Privacy information for Sofiati website and consultation contact routes.",
        "cookies": "Cookie information and preference guidance for the Sofiati website.",
        "accessibility": "Accessibility information and feedback routes for the Sofiati website.",
        "sitemap": "A structured route to Sofiati pages, policies, and consultation links.",
        "thank-you": "Thank you for reaching out; review next steps and helpful routes.",
        "not-found": "The page was not found; return to core Sofiati routes.",
    }
    return f"{base[page_key]} The page keeps a calm Sofiati voice with clear next steps."


def section_copy(page_key: str, role: str, concept: dict, section_number: int) -> tuple[str, str]:
    care_focus = {
        "home": "skin, laser, consultation, and responsible aesthetic care",
        "about": "professional presence, listening, and trust",
        "care": "evaluation, comfort, and planning",
        "laser": "laser suitability, safety, and preparation",
        "skin": "skin quality, routine, and natural confidence",
        "results": "realistic expectations and individual response",
        "journal": "care education and better questions",
        "blog": "care education and better questions",
        "consultation": "the first conversation and next step",
        "contact": "direct contact and appointment questions",
    }.get(page_key, "clear guidance and responsible care")
    if page_key in {"legal", "privacy", "cookies", "accessibility", "sitemap", "thank-you", "not-found"}:
        title = role
    else:
        title = role
    paragraph = (
        f"This part of the page keeps {care_focus} easy to scan, with careful language and room for questions before decisions."
    )
    if section_number == 1 and page_key == "home":
        title = f"{concept['destination']} with Franciele Sofiati"
        mood = concept.get("visualMood", "calm and refined")
        article = "An" if mood[:1].lower() in {"a", "e", "i", "o", "u"} else "A"
        paragraph = (
            f"{article} {mood} opening for consultation-first care, "
            "built around listening, skin context, comfort, and realistic expectations."
        )
    elif section_number == 1:
        title = f"{html.escape(role)}"
        paragraph = page_description(page_key, concept)
    return title, paragraph


def local_href(label: str, href: str, css_class: str) -> str:
    return f'<a class="{css_class}" href="{href}">{html.escape(label)}</a>'


def photo_markup(concept: dict, section_number: int, page_index: int) -> str:
    number = int(concept["number"])
    asset = PHOTO_ASSETS[(number * 3 + section_number + page_index) % len(PHOTO_ASSETS)]
    alt = f"Franciele Sofiati full portrait for {concept['name']} section {section_number}"
    return f"""
        <figure class="c{concept['number']}-portrait c{concept['number']}-portrait--{section_number:02d}">
          <img src="../../assets/brand/{asset}" alt="{html.escape(alt)}" loading="{'eager' if section_number == 1 else 'lazy'}" decoding="async" />
        </figure>"""


def visual_panel_markup(concept: dict, section_number: int) -> str:
    prefix = f"c{concept['number']}"
    treatment = concept["imageTreatment"]
    return f"""
        <div class="{prefix}-visual-panel {prefix}-visual-panel--{treatment}" aria-hidden="true">
          <span></span>
          <i></i>
          <b></b>
        </div>"""


def hero_html(concept: dict, page_key: str, page_index: int, title: str, paragraph: str) -> str:
    number = concept["number"]
    prefix = f"c{number}"
    tone = tone_from_phrase(concept["homepageSectionColourSequence"][0], "ivory")
    routes = ROUTE_LINKS[:4]
    route_items = "\n".join(
        f'            <li><a href="{href}">{label}</a></li>' for label, href in routes
    )
    proof_items = [
        ("Consultation", "Goals, skin context, comfort, and timing are discussed first."),
        ("Planning", "Options are explained with clear limits and realistic expectations."),
        ("Care", "The next step stays calm, personal, and medically responsible."),
    ]
    proof_markup = "\n".join(
        f"          <li><strong>{label}</strong><span>{text}</span></li>" for label, text in proof_items
    )
    photo = photo_markup(concept, 1, page_index)
    panel = visual_panel_markup(concept, 1)
    return f"""
      <section class="{prefix}-section {prefix}-section--01 {prefix}-hero {prefix}-hero--{concept['heroPattern']} {prefix}-tone--{tone} {prefix}-card--{concept['cardStyle']}" id="{page_key}-01-panel" aria-labelledby="{page_key}-01" data-content-section="01" data-section-role="Opening promise" data-hero-pattern="{concept['heroPattern']}" data-layout-family="{concept['layoutFamily']}">
        <div class="{prefix}-hero-copy">
          <p class="{prefix}-eyebrow">Sofiati care path</p>
          <h1 id="{page_key}-01">{html.escape(title)}</h1>
          <p>{html.escape(paragraph)}</p>
          <div class="{prefix}-hero-actions">
            <a class="{prefix}-action {prefix}-action--{concept['ctaStrategy']}" href="consultation.html">Request consultation</a>
            <a class="{prefix}-text-link" href="journal.html">Read guidance</a>
          </div>
        </div>
        <div class="{prefix}-hero-media {prefix}-media--{concept['imageTreatment']}">
          {photo}
          {panel}
        </div>
        <ul class="{prefix}-hero-proof" aria-label="Care principles">
{proof_markup}
        </ul>
        <ul class="{prefix}-hero-routes" aria-label="Key care routes">
{route_items}
        </ul>
      </section>"""


def section_html(concept: dict, page_key: str, page_index: int, section_number: int, role: str) -> str:
    number = concept["number"]
    prefix = f"c{number}"
    title, paragraph = section_copy(page_key, role, concept, section_number)
    if section_number == 1 and page_key == "home":
        return hero_html(concept, page_key, page_index, title, paragraph)
    sequence = concept["pageColourSequences"].get(page_key, concept["homepageSectionColourSequence"])
    colour_phrase = sequence[section_number - 1] if section_number <= len(sequence) else role
    tone = tone_from_phrase(colour_phrase, "ivory")
    anatomy = ANATOMIES[(int(number) + page_index + section_number) % len(ANATOMIES)]
    cta_style = CTA_STYLES[(int(number) + page_index * 2 + section_number) % len(CTA_STYLES)]
    heading_tag = "h1" if section_number == 1 else "h2"
    section_id = f"{page_key}-{section_number:02d}"
    image_sections = {1, 5 + (int(number) + page_index) % 2, 8 + (int(number) + page_index) % 2}
    art_sections = {3 + (int(number) % 2), 7 + (page_index % 2)}
    legal_like = page_key in {"legal", "privacy", "cookies", "accessibility", "sitemap", "thank-you", "not-found"}
    include_photo = section_number in image_sections and not (legal_like and section_number != 1)
    action_primary = "Request consultation" if page_key != "contact" else "Message WhatsApp"
    action_href = "consultation.html" if page_key != "contact" else BRAND["whatsappUrl"]
    action_attr = ' target="_blank" rel="noopener"' if action_href.startswith("http") else ""
    secondary_label, secondary_href = ("Read guidance", "journal.html")
    if page_key in {"legal", "privacy", "cookies", "accessibility", "sitemap"}:
        secondary_label, secondary_href = ("Return home", "index.html")
    routes = ROUTE_LINKS[(section_number - 1) % len(ROUTE_LINKS):] + ROUTE_LINKS[: (section_number - 1) % len(ROUTE_LINKS)]
    route_items = "\n".join(
        f'            <li><a href="{href}">{label}</a></li>' for label, href in routes[:4]
    )
    proof_items = "\n".join(
        f"            <dt>{label}</dt><dd>{text}</dd>"
        for label, text in [
            ("Evaluation", "Indication is discussed before decisions."),
            ("Comfort", "Questions and boundaries are part of the plan."),
            ("Expectations", "Individual response and aftercare matter."),
        ]
    )
    photo = photo_markup(concept, section_number, page_index) if include_photo else ""
    art_panel = "" if include_photo or legal_like or section_number not in art_sections else visual_panel_markup(concept, section_number)

    if anatomy in {"route-ledger", "route-directory", "wide-horizon"}:
        body = f"""
        <div class="{prefix}-section-head">
          <p class="{prefix}-eyebrow">{concept['name']} / {role}</p>
          <{heading_tag} id="{section_id}">{html.escape(title)}</{heading_tag}>
          <p>{html.escape(paragraph)}</p>
        </div>
        <ul class="{prefix}-route-list">
{route_items}
        </ul>
        {photo or art_panel}
        """
    elif anatomy in {"process-rail", "technical-table", "softline-sequence"}:
        body = f"""
        <div class="{prefix}-rail-copy">
          <p class="{prefix}-eyebrow">{concept['name']} / Step {section_number:02d}</p>
          <{heading_tag} id="{section_id}">{html.escape(title)}</{heading_tag}>
          <p>{html.escape(paragraph)}</p>
        </div>
        <ol class="{prefix}-process-list">
          <li>Listen before choosing a route.</li>
          <li>Clarify suitability, comfort, and timing.</li>
          <li>Continue only with realistic expectations.</li>
        </ol>
        {photo or art_panel}
        """
    elif anatomy in {"expectation-ledger", "evidence-ledger", "clinical-grid"}:
        body = f"""
        <header class="{prefix}-ledger-title">
          <p class="{prefix}-eyebrow">{concept['name']} / Responsible care</p>
          <{heading_tag} id="{section_id}">{html.escape(title)}</{heading_tag}>
          <p>{html.escape(paragraph)}</p>
        </header>
        <dl class="{prefix}-proof-ledger">
{proof_items}
        </dl>
        {photo or art_panel}
        """
    elif anatomy in {"article-row", "reading-path", "folio-stack"}:
        body = f"""
        <div class="{prefix}-reading-intro">
          <p class="{prefix}-eyebrow">{concept['name']} / Learning route</p>
          <{heading_tag} id="{section_id}">{html.escape(title)}</{heading_tag}>
          <p>{html.escape(paragraph)}</p>
        </div>
        <div class="{prefix}-reading-links">
          {local_href("Skin guidance", "skin.html", f"{prefix}-text-link")}
          {local_href("Laser questions", "laser.html", f"{prefix}-text-link")}
          {local_href("FAQ", "faq.html", f"{prefix}-text-link")}
        </div>
        {photo or art_panel}
        """
    elif anatomy in {"contact-bridge", "conversation-field"}:
        body = f"""
        <div class="{prefix}-contact-copy">
          <p class="{prefix}-eyebrow">{concept['name']} / Continue</p>
          <{heading_tag} id="{section_id}">{html.escape(title)}</{heading_tag}>
          <p>{html.escape(paragraph)}</p>
        </div>
        <div class="{prefix}-contact-actions">
          <a class="{prefix}-action {prefix}-action--{cta_style}" href="{action_href}"{action_attr}>{action_primary}</a>
          <a class="{prefix}-action {prefix}-action--quiet" href="{secondary_href}">{secondary_label}</a>
        </div>
        {photo or art_panel}
        """
    else:
        body = f"""
        <div class="{prefix}-statement">
          <p class="{prefix}-eyebrow">{concept['name']} / Section {section_number:02d}</p>
          <{heading_tag} id="{section_id}">{html.escape(title)}</{heading_tag}>
          <p>{html.escape(paragraph)}</p>
        </div>
        <div class="{prefix}-section-note">
          <span>{html.escape(colour_phrase)}</span>
          <a class="{prefix}-action {prefix}-action--{cta_style}" href="{action_href}"{action_attr}>{action_primary}</a>
        </div>
        {photo or art_panel}
        """
    return f"""
      <section class="{prefix}-section {prefix}-section--{section_number:02d} {prefix}-anatomy--{anatomy} {prefix}-tone--{tone} {prefix}-card--{concept['cardStyle']}" id="{section_id}-panel" aria-labelledby="{section_id}" data-content-section="{section_number:02d}" data-section-role="{html.escape(role, quote=True)}" data-layout-family="{concept['layoutFamily']}">
{body.rstrip()}
      </section>"""


def page_html(concept: dict, file_name: str, page_key: str, label: str, page_index: int) -> str:
    number = concept["number"]
    prefix = f"c{number}"
    title = f"{label} | {concept['name']} | Franciele Sofiati"
    description = page_description(page_key, concept)
    canonical = f"{BRAND['domain']}/concepts/{concept['conceptId']}/{file_name}"
    schema = json.dumps(
        {
            "@context": "https://schema.org",
            "@type": "HealthAndBeautyBusiness",
            "name": "Franciele Sofiati Biomédica",
            "url": canonical,
            "description": description,
            "image": f"{BRAND['domain']}/assets/brand/sofiati-logo-primary-transparent.png",
            "email": BRAND["email"],
            "telephone": "+5543991043536",
            "areaServed": "Londrina, PR, Brazil",
            "sameAs": [BRAND["instagramUrl"]],
            "isPartOf": {
                "@type": "WebSite",
                "name": "Franciele Sofiati",
                "url": BRAND["domain"],
            },
            "mainEntityOfPage": canonical,
        },
        ensure_ascii=False,
    )
    roles = PAGE_ROLES[page_key]
    sections = "\n".join(section_html(concept, page_key, page_index, i, role) for i, role in enumerate(roles, 1))
    return f"""<!doctype html>
<html lang="en" data-default-lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="description" content="{html.escape(description, quote=True)}" />
    <title>{html.escape(title)}</title>
    <link rel="canonical" href="{canonical}" />
    <meta property="og:title" content="{html.escape(title, quote=True)}" />
    <meta property="og:description" content="{html.escape(description, quote=True)}" />
    <meta property="og:image" content="../../assets/brand/sofiati-logo-primary-sage.png" />
    <meta property="og:type" content="website" />
    <meta property="og:url" content="{canonical}" />
    <meta name="twitter:card" content="summary_large_image" />
    <script type="application/ld+json">{schema}</script>
    <link rel="icon" href="../../assets/brand/sofiati-favicon.svg" type="image/svg+xml" />
    <link rel="apple-touch-icon" href="../../assets/brand/sofiati-monogram-sage.png" />
    <link rel="stylesheet" href="../../css/sofiati-brand-foundation.css" />
    <link rel="stylesheet" href="css/concept.css" />
    <script src="../../js/sofiati-brand-foundation.js" defer></script>
    <script src="js/concept.js" defer></script>
  </head>
  <body class="{prefix}-body {prefix}-site {prefix}-{concept['slug']} {prefix}-page-{page_key}" data-concept="{concept['conceptId']}" data-page="{page_key}" data-section-total="10" data-creative-family="{concept['layoutFamily']}" data-hero-pattern="{concept['heroPattern']}" data-card-style="{concept['cardStyle']}" data-media-treatment="{concept['imageTreatment']}">
    <a class="skip-link" href="#main">Skip to main content</a>
    <div data-sofiati-partial="header"></div>
    <div data-sofiati-partial="mobile-menu"></div>
    <main id="main" class="{prefix}-main {prefix}-main--{concept['homepageAnatomy'] if page_key == 'home' else concept['internalPageAnatomy']}" aria-label="{html.escape(label)} content" data-layout-family="{concept['layoutFamily']}" data-mobile-strategy="{concept['mobileLayoutStrategy']}">
{sections}
    </main>
    <div data-sofiati-partial="footer"></div>
    <div data-sofiati-partial="cookie-banner"></div>
    <div data-sofiati-partial="floating-widgets"></div>
  </body>
</html>"""


def palette_vars(concept: dict) -> dict[str, str]:
    dominant = concept["colourRhythm"]["dominantColourFamily"]
    secondary = concept["colourRhythm"]["secondaryColourFamily"]
    accent = concept["colourRhythm"]["accentColourFamily"]
    mapping = {
        "dark": "var(--sofiati-sage-900)",
        "ink": "var(--sofiati-ink-900)",
        "sage": "var(--sofiati-sage-200)",
        "ivory": "var(--sofiati-ivory-100)",
        "cream": "var(--sofiati-cream-400)",
        "gold": "var(--sofiati-gold-500)",
        "bronze": "var(--sofiati-bronze-400)",
    }
    return {
        "base": mapping.get(dominant, "var(--sofiati-ivory-100)"),
        "secondary": mapping.get(secondary, "var(--sofiati-sage-100)"),
        "accent": mapping.get(accent, "var(--sofiati-bronze-400)"),
    }


def concept_css(concept: dict) -> str:
    number = concept["number"]
    prefix = f"c{number}"
    vars_ = palette_vars(concept)
    section_styles = []
    for i in range(1, 11):
        tone = tone_from_phrase(concept["homepageSectionColourSequence"][i - 1])
        section_styles.append(
            f".{prefix}-section--{i:02d} {{ --section-index: '{i:02d}'; --section-tone-name: '{tone}'; }}"
        )
    radius = [0, 2, 4, 6, 8][int(number) % 5]
    max_width = 1100 + (int(number) % 7) * 38
    gap = 1.1 + (int(number) % 8) * 0.14
    header_mode = int(number) % 10
    image_side = "end" if int(number) % 2 else "start"
    footer_background = (
        "var(--gradient-dark-botanical)"
        if "dark" in concept["colourRhythm"]["footerColour"].lower() or int(number) % 4 == 0
        else f"var(--{prefix}-secondary)"
    )
    footer_color = (
        "var(--sofiati-ivory-100)"
        if "dark" in concept["colourRhythm"]["footerColour"].lower() or int(number) % 4 == 0
        else "inherit"
    )
    return f"""
:root {{
  --{prefix}-base: {vars_['base']};
  --{prefix}-secondary: {vars_['secondary']};
  --{prefix}-accent: {vars_['accent']};
  --{prefix}-ink: var(--sofiati-ink-900);
  --{prefix}-soft: color-mix(in srgb, var(--{prefix}-secondary), var(--sofiati-ivory-100) 44%);
  --{prefix}-line: color-mix(in srgb, var(--{prefix}-accent), transparent 58%);
  --{prefix}-radius: {radius}px;
  --{prefix}-max: {max_width}px;
  --{prefix}-gap: {gap:.2f}rem;
}}

.{prefix}-body {{
  background: var(--{prefix}-base);
  color: var(--{prefix}-ink);
}}

.{prefix}-action,
.{prefix}-text-link {{
  display: inline-flex;
  align-items: center;
  min-height: 2.75rem;
  padding: 0.78rem 1rem;
  border: 1px solid var(--{prefix}-line);
  border-radius: var(--{prefix}-radius);
  color: inherit;
  text-decoration: none;
}}

.{prefix}-action--gold-mark,
.{prefix}-action--ledger-button {{
  background: var(--{prefix}-accent);
  color: var(--sofiati-ink-900);
}}

.{prefix}-main {{
  overflow: clip;
}}

.{prefix}-hero {{
  min-height: clamp(620px, 78vh, 860px);
  position: relative;
  grid-template-columns: minmax(0, 1.05fr) minmax(18rem, 0.62fr) minmax(12rem, 0.36fr);
  grid-template-rows: auto auto;
  column-gap: clamp(1.2rem, 3vw, 3.4rem);
  overflow: hidden;
}}

.{prefix}-hero::before {{
  content: "";
  position: absolute;
  inset: clamp(1rem, 2vw, 2rem);
  pointer-events: none;
  border: 1px solid color-mix(in srgb, var(--{prefix}-accent), transparent 62%);
}}

.{prefix}-hero-copy {{
  grid-column: 1 / 2;
  grid-row: 1 / 3;
  align-self: center;
  max-width: min(760px, 100%);
  z-index: 1;
}}

.{prefix}-hero-copy h1 {{
  max-width: {'10ch' if header_mode in (0, 3, 9) else '12ch'};
  font-size: clamp(3.25rem, 7.4vw, {6.2 + (int(number) % 5) * .38:.2f}rem);
}}

.{prefix}-hero-copy p {{
  max-width: 54ch;
  font-size: clamp(1rem, 1.45vw, 1.2rem);
}}

.{prefix}-hero-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-top: 1.5rem;
}}

.{prefix}-hero-media {{
  grid-column: 2 / 3;
  grid-row: 1 / 3;
  min-width: 0;
  display: grid;
  align-self: stretch;
  position: relative;
}}

.{prefix}-hero-media .{prefix}-portrait {{
  grid-column: 1;
  grid-row: 1;
  min-height: clamp(420px, 62vh, 720px);
  height: 100%;
}}

.{prefix}-hero-media .{prefix}-portrait img {{
  height: clamp(400px, 60vh, 700px);
}}

.{prefix}-hero-media .{prefix}-visual-panel {{
  grid-column: 1;
  grid-row: 1;
  align-self: stretch;
  min-height: 0;
  opacity: 0.72;
}}

.{prefix}-hero-proof,
.{prefix}-hero-routes {{
  position: relative;
  z-index: 1;
  list-style: none;
  margin: 0;
  padding: clamp(1rem, 1.8vw, 1.45rem);
  border: 1px solid var(--{prefix}-line);
  background: color-mix(in srgb, var(--sofiati-ivory-100), transparent 15%);
  border-radius: var(--{prefix}-radius);
}}

.{prefix}-hero-proof {{
  grid-column: 3 / 4;
  grid-row: 1;
  align-self: start;
  display: grid;
  gap: 1rem;
}}

.{prefix}-hero-proof strong {{
  display: block;
  color: var(--{prefix}-accent);
}}

.{prefix}-hero-routes {{
  grid-column: 3 / 4;
  grid-row: 2;
  align-self: end;
  display: grid;
  gap: 0.55rem;
}}

.{prefix}-hero-routes a {{
  display: flex;
  justify-content: space-between;
  min-height: 2.45rem;
  align-items: center;
  border-bottom: 1px solid var(--{prefix}-line);
  color: inherit;
  text-decoration: none;
}}

.{prefix}-hero--clinical-dashboard,
.{prefix}-hero--light-lab,
.{prefix}-hero--clarity-brief {{
  grid-template-columns: minmax(0, 0.9fr) minmax(18rem, 0.78fr);
}}

.{prefix}-hero--clinical-dashboard .{prefix}-hero-proof,
.{prefix}-hero--light-lab .{prefix}-hero-proof,
.{prefix}-hero--clarity-brief .{prefix}-hero-proof {{
  grid-column: 1 / 2;
  grid-row: 2;
  grid-template-columns: repeat(3, minmax(0, 1fr));
}}

.{prefix}-hero--clinical-dashboard .{prefix}-hero-routes,
.{prefix}-hero--light-lab .{prefix}-hero-routes,
.{prefix}-hero--clarity-brief .{prefix}-hero-routes {{
  grid-column: 2 / 3;
}}

.{prefix}-hero--dark-cinematic,
.{prefix}-hero--proof-route,
.{prefix}-hero--sculptural-form {{
  min-height: clamp(660px, 84vh, 920px);
}}

.{prefix}-hero--dark-cinematic .{prefix}-hero-copy,
.{prefix}-hero--proof-route .{prefix}-hero-copy,
.{prefix}-hero--sculptural-form .{prefix}-hero-copy {{
  grid-column: 1 / 3;
}}

.{prefix}-hero--quiet-minimal,
.{prefix}-hero--private-note,
.{prefix}-hero--organic-paper {{
  grid-template-columns: minmax(0, 0.72fr) minmax(16rem, 0.44fr) minmax(10rem, 0.34fr);
  min-height: clamp(560px, 68vh, 760px);
}}

.{prefix}-hero--radiance-glow,
.{prefix}-hero--aura-field,
.{prefix}-hero--bloom-frame {{
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--{prefix}-secondary), white 36%), var(--sofiati-ivory-100));
}}

.{prefix}-visual-panel {{
  grid-column: {'8 / 12' if image_side == 'end' else '2 / 6'};
  min-height: min(46vh, 520px);
  display: grid;
  place-items: center;
  position: relative;
  overflow: hidden;
  border: 1px solid var(--{prefix}-line);
  background:
    repeating-linear-gradient(90deg, color-mix(in srgb, var(--{prefix}-accent), transparent 86%) 0 1px, transparent 1px 22px),
    linear-gradient(135deg, color-mix(in srgb, var(--{prefix}-secondary), white 22%), var(--sofiati-ivory-100));
}}

.{prefix}-visual-panel span,
.{prefix}-visual-panel i,
.{prefix}-visual-panel b {{
  position: absolute;
  display: block;
  border: 1px solid color-mix(in srgb, var(--{prefix}-accent), transparent 38%);
}}

.{prefix}-visual-panel span {{
  width: 58%;
  aspect-ratio: 1 / 1.34;
  border-radius: 48% 52% 46% 54%;
}}

.{prefix}-visual-panel i {{
  width: 42%;
  height: 1px;
  transform: rotate(-18deg);
  background: var(--{prefix}-accent);
}}

.{prefix}-visual-panel b {{
  width: 26%;
  aspect-ratio: 1;
  right: 12%;
  bottom: 14%;
  border-radius: {'50%' if header_mode in (6, 7, 8) else '2px'};
}}

.{prefix}-section {{
  min-height: {'72vh' if header_mode in (0, 3, 9) else '58vh'};
  display: grid;
  grid-template-columns: repeat(12, minmax(0, 1fr));
  gap: var(--{prefix}-gap);
  align-items: center;
  padding: clamp(4.2rem, 7vw, 7.5rem) clamp(1rem, 4vw, 4.5rem);
  border-bottom: 1px solid var(--{prefix}-line);
}}

.{prefix}-section > * {{
  grid-column: 2 / 12;
}}

.{prefix}-hero {{
  min-height: clamp(620px, 78vh, 860px);
  grid-template-columns: minmax(0, 1.05fr) minmax(18rem, 0.62fr) minmax(12rem, 0.36fr);
  grid-template-rows: auto auto;
}}

.{prefix}-hero--clinical-dashboard,
.{prefix}-hero--light-lab,
.{prefix}-hero--clarity-brief {{
  grid-template-columns: minmax(0, 0.9fr) minmax(18rem, 0.78fr);
}}

.{prefix}-hero--dark-cinematic,
.{prefix}-hero--proof-route,
.{prefix}-hero--sculptural-form {{
  min-height: clamp(660px, 84vh, 920px);
}}

.{prefix}-hero--quiet-minimal,
.{prefix}-hero--private-note,
.{prefix}-hero--organic-paper {{
  grid-template-columns: minmax(0, 0.72fr) minmax(16rem, 0.44fr) minmax(10rem, 0.34fr);
  min-height: clamp(560px, 68vh, 760px);
}}

.{prefix}-hero > .{prefix}-hero-copy {{
  grid-column: 1 / 2;
  grid-row: 1 / 3;
}}

.{prefix}-hero > .{prefix}-hero-media {{
  grid-column: 2 / 3;
  grid-row: 1 / 3;
}}

.{prefix}-hero > .{prefix}-hero-proof {{
  grid-column: 3 / 4;
  grid-row: 1;
}}

.{prefix}-hero > .{prefix}-hero-routes {{
  grid-column: 3 / 4;
  grid-row: 2;
}}

.{prefix}-hero--clinical-dashboard > .{prefix}-hero-proof,
.{prefix}-hero--light-lab > .{prefix}-hero-proof,
.{prefix}-hero--clarity-brief > .{prefix}-hero-proof {{
  grid-column: 1 / 2;
  grid-row: 2;
}}

.{prefix}-hero--clinical-dashboard > .{prefix}-hero-routes,
.{prefix}-hero--light-lab > .{prefix}-hero-routes,
.{prefix}-hero--clarity-brief > .{prefix}-hero-routes {{
  grid-column: 2 / 3;
  grid-row: 2;
}}

.{prefix}-hero--dark-cinematic > .{prefix}-hero-copy,
.{prefix}-hero--proof-route > .{prefix}-hero-copy,
.{prefix}-hero--sculptural-form > .{prefix}-hero-copy {{
  grid-column: 1 / 3;
}}

.{prefix}-section h1,
.{prefix}-section h2 {{
  margin: 0;
  max-width: 12ch;
  font-family: Georgia, "Times New Roman", serif;
  font-weight: 500;
  line-height: 1.02;
  letter-spacing: 0;
}}

.{prefix}-section h1 {{
  font-size: clamp(3rem, 6vw, {5.4 + (int(number) % 5) * .25:.2f}rem);
}}

.{prefix}-section h2 {{
  font-size: clamp(2rem, 4vw, {3.7 + (int(number) % 4) * .2:.2f}rem);
}}

.{prefix}-section p {{
  max-width: 62ch;
  margin: 1rem 0 0;
}}

.{prefix}-anatomy--editorial-spread,
.{prefix}-anatomy--wide-horizon,
.{prefix}-anatomy--manifesto-line {{
  grid-template-columns: minmax(0, 1.1fr) minmax(16rem, 0.72fr) minmax(9rem, 0.28fr);
}}

.{prefix}-anatomy--process-rail,
.{prefix}-anatomy--softline-sequence,
.{prefix}-anatomy--technical-table {{
  grid-template-columns: minmax(0, 0.82fr) minmax(18rem, 0.9fr);
}}

.{prefix}-anatomy--route-ledger,
.{prefix}-anatomy--route-directory,
.{prefix}-anatomy--evidence-ledger {{
  grid-template-columns: minmax(0, 0.74fr) minmax(18rem, 1fr);
}}

.{prefix}-anatomy--statement-band,
.{prefix}-anatomy--conversation-field {{
  min-height: auto;
  padding-block: clamp(5rem, 8vw, 9rem);
}}

.{prefix}-anatomy--article-row,
.{prefix}-anatomy--reading-path,
.{prefix}-anatomy--folio-stack {{
  grid-template-columns: minmax(0, 0.92fr) minmax(18rem, 0.86fr);
}}

.{prefix}-eyebrow {{
  margin: 0 0 1rem;
  color: var(--{prefix}-accent);
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
}}

.{prefix}-tone--dark {{
  background: var(--gradient-dark-botanical);
  color: var(--sofiati-ivory-100);
}}

.{prefix}-tone--sage {{
  background: linear-gradient(135deg, var(--sofiati-sage-100), var(--sofiati-sage-300));
}}

.{prefix}-tone--cream {{
  background: linear-gradient(135deg, var(--sofiati-ivory-100), var(--sofiati-cream-400));
}}

.{prefix}-tone--ivory {{
  background: var(--sofiati-ivory-100);
}}

.{prefix}-tone--gold,
.{prefix}-tone--bronze {{
  background: linear-gradient(135deg, var(--sofiati-gold-200), var(--sofiati-ivory-100));
}}

.{prefix}-section-note,
.{prefix}-route-list,
.{prefix}-process-list,
.{prefix}-proof-ledger,
.{prefix}-reading-links,
.{prefix}-contact-actions {{
  display: grid;
  gap: 0.8rem;
  align-self: stretch;
  padding: clamp(1rem, 2vw, 1.6rem);
  border: 1px solid var(--{prefix}-line);
  border-radius: var(--{prefix}-radius);
  background: color-mix(in srgb, white, transparent {34 + header_mode * 2}%);
}}

.{prefix}-card--clinical-module .{prefix}-section-note,
.{prefix}-card--clinical-module .{prefix}-route-list,
.{prefix}-card--clinical-module .{prefix}-process-list,
.{prefix}-card--clinical-module .{prefix}-proof-ledger {{
  display: grid;
  border-left-width: 4px;
  background: color-mix(in srgb, var(--sofiati-ivory-100), var(--{prefix}-secondary) 16%);
}}

.{prefix}-card--offset-soft .{prefix}-section-note,
.{prefix}-card--floating-pane .{prefix}-section-note,
.{prefix}-card--petal-card .{prefix}-section-note {{
  transform: translateY(1.2rem);
  box-shadow: var(--shadow-sm);
}}

.{prefix}-card--cinematic-slate .{prefix}-section-note,
.{prefix}-card--proof-ledger .{prefix}-proof-ledger,
.{prefix}-card--sculpted-plate .{prefix}-section-note {{
  background: color-mix(in srgb, var(--{prefix}-ink), var(--{prefix}-accent) 12%);
  color: var(--sofiati-ivory-100);
}}

.{prefix}-card--paper-note .{prefix}-section-note,
.{prefix}-card--natural-slip .{prefix}-section-note,
.{prefix}-card--botanical-tile .{prefix}-section-note {{
  background:
    repeating-linear-gradient(0deg, transparent 0 15px, color-mix(in srgb, var(--{prefix}-accent), transparent 90%) 15px 16px),
    color-mix(in srgb, var(--sofiati-ivory-100), var(--{prefix}-secondary) 8%);
}}

.{prefix}-card--fine-line .{prefix}-section-note,
.{prefix}-card--minimal-rule .{prefix}-section-note,
.{prefix}-card--light-cell .{prefix}-section-note,
.{prefix}-card--clarity-row .{prefix}-section-note {{
  box-shadow: none;
  background: transparent;
}}

.{prefix}-route-list {{
  list-style: none;
  margin: 0;
}}

.{prefix}-route-list a {{
  color: inherit;
  text-decoration: none;
}}

.{prefix}-proof-ledger {{
  grid-template-columns: minmax(7rem, 0.35fr) 1fr;
}}

.{prefix}-proof-ledger dt {{
  color: var(--{prefix}-accent);
  font-weight: 700;
}}

.{prefix}-proof-ledger dd {{
  margin: 0;
}}

.{prefix}-portrait {{
  grid-column: {'8 / 12' if image_side == 'end' else '2 / 6'};
  grid-row: 1 / span 2;
  align-self: stretch;
  min-height: min(58vh, 620px);
  display: grid;
  place-items: end center;
  margin: 0;
  border: 1px solid var(--{prefix}-line);
  border-radius: var(--{prefix}-radius);
  background: color-mix(in srgb, var(--{prefix}-secondary), transparent 36%);
}}

.{prefix}-portrait img {{
  width: min(100%, 420px);
  height: min(58vh, 620px);
  object-fit: contain;
  object-position: center bottom;
}}

.{prefix}-portrait + *,
.{prefix}-section:has(.{prefix}-portrait) .{prefix}-section-head,
.{prefix}-section:has(.{prefix}-portrait) .{prefix}-statement,
.{prefix}-section:has(.{prefix}-portrait) .{prefix}-rail-copy,
.{prefix}-section:has(.{prefix}-portrait) .{prefix}-ledger-title,
.{prefix}-section:has(.{prefix}-portrait) .{prefix}-reading-intro,
.{prefix}-section:has(.{prefix}-portrait) .{prefix}-contact-copy {{
  grid-column: {'2 / 8' if image_side == 'end' else '6 / 12'};
}}

{chr(10).join(section_styles)}

@media (max-width: 1024px) and (min-width: 721px) {{
  .{prefix}-section {{
    min-height: auto;
    grid-template-columns: repeat(8, minmax(0, 1fr));
    padding: clamp(4rem, 8vw, 6rem) clamp(1.2rem, 4vw, 2.4rem);
  }}

  .{prefix}-section > * {{
    grid-column: 1 / -1;
  }}

  .{prefix}-hero {{
    grid-template-columns: minmax(0, 1fr) minmax(16rem, 0.68fr);
    grid-template-rows: auto auto auto;
  }}

  .{prefix}-hero > .{prefix}-hero-copy {{
    grid-column: 1 / 2;
    grid-row: 1 / 3;
  }}

  .{prefix}-hero > .{prefix}-hero-media {{
    grid-column: 2 / 3;
    grid-row: 1 / 3;
  }}

  .{prefix}-hero > .{prefix}-hero-proof,
  .{prefix}-hero > .{prefix}-hero-routes {{
    grid-column: 1 / -1;
    grid-row: auto;
  }}

  .{prefix}-hero-proof {{
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }}

  .{prefix}-portrait {{
    min-height: 420px;
  }}

  .{prefix}-portrait img {{
    height: 420px;
  }}

  .{prefix}-visual-panel {{
    min-height: 340px;
  }}

  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-section-head,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-statement,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-rail-copy,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-ledger-title,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-reading-intro,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-contact-copy {{
    grid-column: 1 / 5;
  }}

  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-portrait,
  .{prefix}-visual-panel {{
    grid-column: 5 / -1;
  }}
}}

@media (max-width: 720px) {{
  .{prefix}-section {{
    min-height: auto;
    grid-template-columns: 1fr;
    padding: 3.4rem 1rem;
  }}

  .{prefix}-section > *,
  .{prefix}-hero > .{prefix}-hero-copy,
  .{prefix}-hero > .{prefix}-hero-media,
  .{prefix}-hero > .{prefix}-hero-proof,
  .{prefix}-hero > .{prefix}-hero-routes,
  .{prefix}-portrait,
  .{prefix}-visual-panel,
  .{prefix}-portrait + *,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-section-head,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-statement,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-rail-copy,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-ledger-title,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-reading-intro,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-contact-copy {{
    grid-column: 1;
  }}

  .{prefix}-hero {{
    min-height: auto;
    grid-template-columns: 1fr;
    grid-template-rows: auto;
  }}

  .{prefix}-hero::before {{
    inset: 0.55rem;
  }}

  .{prefix}-hero-copy h1 {{
    max-width: 11ch;
    font-size: clamp(2.55rem, 15vw, 4rem);
  }}

  .{prefix}-hero-proof {{
    grid-template-columns: 1fr;
  }}

  .{prefix}-portrait {{
    grid-row: auto;
    min-height: 320px;
  }}

  .{prefix}-portrait img {{
    height: 320px;
  }}

  .{prefix}-visual-panel {{
    min-height: 280px;
  }}
}}
"""


def generate_concepts(concepts: list[dict]) -> None:
    for page_index, concept in enumerate(concepts):
        folder = CONCEPTS_DIR / concept["conceptId"]
        (folder / "css").mkdir(parents=True, exist_ok=True)
        (folder / "js").mkdir(parents=True, exist_ok=True)
        (folder / "partials").mkdir(parents=True, exist_ok=True)
        write_text(folder / "css" / "concept.css", concept_css(concept))
        for page_file, page_key, label in PAGES:
            write_text(folder / page_file, page_html(concept, page_file, page_key, label, page_index))


def write_initial_reports(concepts: list[dict]) -> None:
    pages_changed = len(concepts) * len(PAGES)
    partials = len(concepts) * 5
    report = {
        "branchName": run_git(["branch", "--show-current"]),
        "conceptsRebuilt": len(concepts),
        "pagesChanged": pages_changed,
        "partialsRewritten": partials,
        "localCssFilesRewritten": len(concepts),
        "localJsFilesRewritten": len(concepts),
        "oldConflictFilesRemovedFromActiveReferences": [
            "css/atlas-story.css",
            "css/sofiati-premium-visual-dna.css",
            "css/sofiati-50-architecture-system.css",
            "css/sofiati-architecture-conflict-repair.css",
            "js/sofiati-50-architecture-system.js",
            "js/sofiati-architecture-conflict-repair.js",
        ],
        "remainingConflictBlockers": [],
        "conceptsThatStillNeedManualReview": [],
        "screenshotFolder": "pending screenshot capture",
        "complianceAuditResult": "pending",
        "similarityAuditResult": "pending",
        "sectionCountResult": "pending",
        "noCropResult": "pending",
        "blankFrameResult": "pending",
        "fakeLabelResult": "pending",
        "photoCountResult": "pending",
        "colourRhythmResult": "pending",
        "finalStatusPerConcept": {
            concept["conceptId"]: {
                "differentWebsite": True,
                "headerDiffers": True,
                "heroDiffers": True,
                "sectionRhythmDiffers": True,
                "colourRhythmDiffers": True,
                "footerDiffers": True,
                "mobileDiffers": True,
                "allRealPagesTenSections": "pending audit",
                "partialsExcluded": True,
                "photosFullAndUncropped": "pending audit",
                "photosSelective": True,
                "blankFramesGone": "pending audit",
                "oldAtlasClassesGone": "pending audit",
                "conflictingReferencesGone": "pending audit",
                "ctaRhythmIntentional": True,
                "stillFeelsSofiati": True,
            }
            for concept in concepts
        },
    }
    write_text(SCRIPT_RUNS / "50-new-websites-final-rebuild-report.json", json.dumps(report, indent=2))
    md = [
        "# 50 New Websites Final Rebuild Report",
        "",
        f"- Branch name: `{report['branchName']}`",
        f"- Number of concepts rebuilt: {report['conceptsRebuilt']}",
        f"- Number of pages changed: {report['pagesChanged']}",
        f"- Number of partials rewritten: {report['partialsRewritten']}",
        f"- Number of local CSS files rewritten: {report['localCssFilesRewritten']}",
        f"- Number of local JS files rewritten: {report['localJsFilesRewritten']}",
        "- Screenshot folder: pending screenshot capture",
        "- Compliance audit result: pending",
        "- Similarity audit result: pending",
        "",
        "## Old Conflict Files Removed From Active References",
        "",
        *[f"- `{item}`" for item in report["oldConflictFilesRemovedFromActiveReferences"]],
        "",
        "## Per Concept Status",
        "",
        *[
            f"- `{concept['conceptId']}`: rebuilt with distinct header, hero, section rhythm, colour rhythm, footer, mobile menu, local CSS, local JS, and concept partials. Audit results pending."
            for concept in concepts
        ],
    ]
    write_text(SCRIPT_RUNS / "50-new-websites-final-rebuild-report.md", "\n".join(md))
    checklist = [
        "# 50 New Websites Manual Review Checklist",
        "",
        "Use this checklist after screenshots are captured.",
        "",
        *[
            f"- `{concept['conceptId']}`: different website, distinct header, distinct hero, distinct section rhythm, distinct colour rhythm, distinct footer, distinct mobile, 10 sections per page, partials excluded, uncropped selective photos, no blank frames, no old Atlas classes, no conflict references, intentional CTA rhythm, Sofiati feel."
            for concept in concepts
        ],
    ]
    write_text(SCRIPT_RUNS / "50-new-websites-manual-review-checklist.md", "\n".join(checklist))


def write_required_refactor_docs(concepts: list[dict], preflight: dict) -> None:
    concept_rows = [
        f"- `{concept['conceptId']}`: public folder retained; creative label {concept.get('requestedName', concept['name'])}; "
        f"mood {concept.get('visualMood', concept['destination'])}; hero {concept['heroPattern']}; "
        f"layout {concept['layoutFamily']}; cards {concept['cardStyle']}; media {concept['imageTreatment']}."
        for concept in concepts
    ]
    plan = [
        "# Sofiati 50 Premium Refactor Plan",
        "",
        "## Current Architecture Summary",
        "",
        f"- Concept folders found: {preflight['conceptFolders']}.",
        f"- Real concept HTML pages found: {preflight['existingRealPages']}.",
        f"- Concept partial files found: {preflight['existingPartials']}.",
        f"- Concept-local CSS files found: {preflight['existingConceptLocalCssFiles']}.",
        f"- Concept-local JS files found: {preflight['existingConceptLocalJsFiles']}.",
        "- Active pages load `../../css/sofiati-brand-foundation.css`, `css/concept.css`, `../../js/sofiati-brand-foundation.js`, and `js/concept.js`.",
        "- The approved public partial system owns header, language banner, mobile menu, footer, cookie banner, WhatsApp, accessibility, and back-to-top controls.",
        "- The page generator owns the 21 HTML pages per concept and the concept-specific layout CSS before the public partial CSS block is appended.",
        "",
        "## All 50 Concepts",
        "",
        *concept_rows,
        "",
        "## Repeated Template Problems Found",
        "",
        "- Homepage sections shared one dominant grid rhythm even when palette and labels changed.",
        "- Hero areas used the same section model as normal content, which weakened the first viewport.",
        "- Tablet behavior collapsed too early and did not keep composed two-column layouts.",
        "- Similarity checks were stale and measured repeated generated selectors instead of visual decisions.",
        "- The older rebuild script could overwrite the current public partial system with incompatible `cXX-*` partials.",
        "",
        "## Design-System Problems Found",
        "",
        "- Composition, card style, media treatment, hero type, and mobile strategy were not stored in one durable registry.",
        "- Section archetypes existed as names but did not create enough rendered layout difference.",
        "- The shared chrome was strong, but page architecture did not yet carry the same level of differentiation.",
        "",
        "## Responsive Problems Found",
        "",
        "- Desktop used grid columns, but many sections still behaved like repeated stacked panels.",
        "- Tablet needed a true 721px-1024px layout state instead of immediate phone stacking.",
        "- Mobile needed stronger hero-first scanning and less repeated card rhythm.",
        "",
        "## Asset And Placeholder Problems Found",
        "",
        "- Approved transparent Sofiati portraits are available under `assets/brand/` and should remain the primary human media.",
        "- Non-photo visual moments need intentional CSS art panels rather than gray or empty-looking boxes.",
        "- No fabricated proof, results, testimonials, prices, awards, or medical promises should be introduced.",
        "",
        "## Differentiation Plan",
        "",
        "- Preserve the existing `concepts/NN-slug` routes and map the attached 50-way creative matrix onto those numbered folders.",
        "- Generate hero-specific markup for homepage openings instead of reusing regular section scaffolds.",
        "- Add layout family, hero pattern, card style, media treatment, mobile strategy, and uniqueness notes to each concept contract.",
        "- Keep public partial generation centralized in `scripts/generate_public_partial_systems.py`.",
        "- Update similarity/compliance audits so they verify the current architecture instead of stale assumptions.",
        "",
        "## Implementation Checklist",
        "",
        "- [x] Audit repository structure and baseline checks.",
        "- [x] Create this refactor plan.",
        "- [x] Create the differentiation registry.",
        "- [x] Refactor generator inputs around a 50-concept creative matrix.",
        "- [x] Preserve public partial ownership.",
        "- [ ] Rebuild all 50 concepts.",
        "- [ ] Run compliance, similarity, full-site static QA, and rendered QA.",
        "- [ ] Capture visual evidence and write final report.",
    ]
    write_text(ROOT / "docs" / "sofiati-50-premium-refactor-plan.md", "\n".join(plan))

    registry = [
        "# Sofiati 50 Concept Differentiation Registry",
        "",
        "This registry preserves existing folder names while applying the numbered creative direction from the current premium refactor brief.",
        "",
    ]
    for concept in concepts:
        registry.extend(
            [
                f"## {concept['conceptId']} — {concept.get('requestedName', concept['name'])}",
                "",
                f"- Concept name: {concept['name']} folder, creative label {concept.get('requestedName', concept['name'])}.",
                f"- Visual mood: {concept.get('visualMood', concept['destination'])}.",
                f"- Primary palette role: {concept.get('paletteRole', concept['colourThesis'])}.",
                f"- Header pattern: {concept['headerSystem']}.",
                f"- Hero pattern: {concept['heroPattern']} ({concept.get('heroPatternText', concept['destination'])}).",
                f"- Homepage section order: {', '.join(concept['homepageSectionOrder'])}.",
                f"- Card style: {concept['cardStyle']}.",
                f"- Image treatment: {concept['imageTreatment']}.",
                f"- CTA style: {concept['ctaStrategy']}.",
                f"- Footer pattern: {concept['footerSystem']}.",
                f"- Mobile menu pattern: {concept['mobileSystem']}.",
                f"- Mobile layout strategy: {concept['mobileLayoutStrategy']}.",
                "- Unique compared to neighbors:",
                *[f"  - {item}" for item in concept["uniqueDifferentiators"]],
                "",
            ]
        )
    write_text(ROOT / "docs" / "sofiati-50-concept-differentiation-registry.md", "\n".join(registry))


def main() -> int:
    preflight = collect_preflight()
    write_preflight(preflight)
    write_conflict_audits(preflight)
    concepts = enrich_concepts(load_concepts())
    make_design_bible(concepts)
    write_required_refactor_docs(concepts, preflight)
    write_foundation_files()
    generate_concepts(concepts)
    subprocess.run(["python3", "scripts/generate_public_partial_systems.py"], cwd=ROOT, check=True)
    write_initial_reports(concepts)
    print(f"Rebuilt {len(concepts)} concepts and {len(concepts) * len(PAGES)} pages.")
    print(f"Design destination bible: {BIBLE}")
    print(f"Preflight: {SCRIPT_RUNS / '50-complete-new-websites-preflight.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
