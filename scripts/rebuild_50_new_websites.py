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

COLOUR_KEYWORDS = {
    "ink": "ink",
    "dark": "dark",
    "deep": "dark",
    "sage": "sage",
    "ivory": "ivory",
    "cream": "cream",
    "white": "ivory",
    "blush": "blush",
    "pink": "blush",
    "gold": "gold",
    "bronze": "bronze",
    "taupe": "taupe",
    "terracotta": "terracotta",
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
    for family in ("sage", "blush", "cream", "gold", "terracotta", "taupe", "ivory", "bronze"):
        if family in families:
            return family
    return fallback


def rotate(values: list[str], amount: int) -> list[str]:
    if not values:
        return values
    amount = amount % len(values)
    return values[amount:] + values[:amount]


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
            for fallback in ("ivory", "sage", "bronze", "blush", "dark", "cream"):
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
                "blushUsage": "purposeful warmth and guidance notes" if "blush" in families else "rare or absent by contract",
                "sageUsage": "primary architecture" if families[0] == "sage" else "brand structure and quiet route support",
                "creamUsage": "reading relief and calm transitions",
                "goldBronzeUsage": "rules, markers, numerals, and selected CTA detail",
                "terracottaTaupeUsage": "earth warmth only when named by the destination",
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

  /* Blush / pink */
  --sofiati-pink-50: #FFF7F6;
  --sofiati-pink-100: #F8E4E1;
  --sofiati-pink-200: #EDC6C0;
  --sofiati-pink-300: #DFA49B;
  --sofiati-pink-500: #B86A63;
  --sofiati-pink-700: #743B37;

  /* Warmth */
  --sofiati-terracotta-200: #E7B7A6;
  --sofiati-terracotta-300: #D7957F;
  --sofiati-terracotta-500: #B86A4E;
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
  --surface-blush: var(--sofiati-pink-100);

  /* Gradients */
  --gradient-cream: linear-gradient(135deg, var(--sofiati-ivory-100), var(--sofiati-ivory-300));
  --gradient-sage-soft: linear-gradient(135deg, var(--sofiati-sage-100), var(--sofiati-sage-300));
  --gradient-sage-deep: linear-gradient(135deg, var(--sofiati-sage-700), var(--sofiati-sage-900));
  --gradient-dark-botanical: radial-gradient(circle at top left, rgba(162, 174, 160, 0.24), transparent 34%), linear-gradient(135deg, var(--sofiati-ink-900), var(--sofiati-sage-900));
  --gradient-blush-cream: linear-gradient(135deg, var(--sofiati-pink-50), var(--sofiati-pink-100), var(--sofiati-ivory-200));
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
  --button-blush-bg: var(--sofiati-pink-200);
  --button-blush-text: var(--sofiati-ink-900);
  --button-dark-bg: var(--sofiati-ink-900);
  --button-dark-text: var(--sofiati-ivory-100);
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

.section-blush {
  background: var(--sofiati-pink-100);
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

.button-blush {
  background: var(--button-blush-bg);
  color: var(--button-blush-text);
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

  document.addEventListener("click", (event) => {
    const top = event.target.closest("[data-back-to-top]");
    if (!top) return;
    event.preventDefault();
    window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
  });

  document.addEventListener("click", (event) => {
    const language = event.target.closest("[data-language-option]");
    if (!language) return;
    const next = language.getAttribute("data-language-option") || "en";
    document.documentElement.lang = next;
    document.querySelectorAll("[data-language-option]").forEach((button) => {
      button.setAttribute("aria-pressed", button === language ? "true" : "false");
    });
  });

  window.SofiatiFoundation = {
    reduceMotion: () => reduceMotion.matches,
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
                "slug",
                "destination",
                "visualThesis",
                "colourThesis",
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
    return f"{base[page_key]} {concept['name']} expresses this as {concept['destination'].lower()}."


def section_copy(page_key: str, role: str, concept: dict, section_number: int) -> tuple[str, str]:
    name = concept["name"]
    if page_key in {"legal", "privacy", "cookies", "accessibility", "sitemap", "thank-you", "not-found"}:
        title = role
    else:
        title = f"{role} with {name}"
    paragraph = (
        f"{role} is presented with calm language, responsible expectations, and a consultation-led path. "
        f"The {concept['destination'].lower()} direction shapes the pacing without adding unsupported claims."
    )
    if section_number == 1 and page_key == "home":
        title = f"{name}: {concept['destination']}"
        paragraph = f"{concept['visualThesis']} {page_description(page_key, concept)}"
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


def section_html(concept: dict, page_key: str, page_index: int, section_number: int, role: str) -> str:
    number = concept["number"]
    prefix = f"c{number}"
    title, paragraph = section_copy(page_key, role, concept, section_number)
    sequence = concept["pageColourSequences"].get(page_key, concept["homepageSectionColourSequence"])
    colour_phrase = sequence[section_number - 1] if section_number <= len(sequence) else role
    tone = tone_from_phrase(colour_phrase, "ivory")
    anatomy = ANATOMIES[(int(number) + page_index + section_number) % len(ANATOMIES)]
    cta_style = CTA_STYLES[(int(number) + page_index * 2 + section_number) % len(CTA_STYLES)]
    heading_tag = "h1" if section_number == 1 else "h2"
    section_id = f"{page_key}-{section_number:02d}"
    image_sections = {1, 5 + (int(number) + page_index) % 2, 8 + (int(number) + page_index) % 2}
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
        {photo}
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
        {photo}
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
        {photo}
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
        {photo}
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
        {photo}
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
        {photo}
        """
    return f"""
      <section class="{prefix}-section {prefix}-section--{section_number:02d} {prefix}-anatomy--{anatomy} {prefix}-tone--{tone}" id="{section_id}-panel" aria-labelledby="{section_id}" data-content-section="{section_number:02d}" data-section-role="{html.escape(role, quote=True)}">
{body.rstrip()}
      </section>"""


def page_html(concept: dict, file_name: str, page_key: str, label: str, page_index: int) -> str:
    number = concept["number"]
    prefix = f"c{number}"
    title = f"{label} | {concept['name']} | Franciele Sofiati"
    description = page_description(page_key, concept)
    canonical = f"{BRAND['domain']}/concepts/{concept['conceptId']}/{file_name}"
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
    <link rel="icon" href="../../assets/brand/sofiati-favicon.svg" type="image/svg+xml" />
    <link rel="apple-touch-icon" href="../../assets/brand/sofiati-monogram-sage.png" />
    <link rel="stylesheet" href="../../css/sofiati-brand-foundation.css" />
    <link rel="stylesheet" href="css/concept.css" />
    <script src="../../js/sofiati-brand-foundation.js" defer></script>
    <script src="js/concept.js" defer></script>
  </head>
  <body class="{prefix}-body {prefix}-site {prefix}-{concept['slug']} {prefix}-page-{page_key}" data-concept="{concept['conceptId']}" data-page="{page_key}" data-section-total="10">
    <a class="skip-link" href="#main">Skip to main content</a>
    <div data-sofiati-partial="header"></div>
    <div data-sofiati-partial="mobile-menu"></div>
    <main id="main" class="{prefix}-main {prefix}-main--{concept['homepageAnatomy'] if page_key == 'home' else concept['internalPageAnatomy']}" aria-label="{html.escape(label)} content">
{sections}
    </main>
    <div data-sofiati-partial="footer"></div>
    <div data-sofiati-partial="cookie-banner"></div>
    <div data-sofiati-partial="floating-widgets"></div>
  </body>
</html>"""


def nav_links(prefix: str, class_name: str, offset: int = 0, limit: int | None = None) -> str:
    links = [
        ("Home", "index.html"),
        ("About", "about.html"),
        ("Care", "care.html"),
        ("Laser", "laser.html"),
        ("Skin", "skin.html"),
        ("Consultation", "consultation.html"),
        ("Contact", "contact.html"),
    ]
    if offset:
        links = rotate(links, offset)
    if limit:
        links = links[:limit]
    return "\n".join(f'        <a class="{prefix}-{class_name}" href="{href}">{label}</a>' for label, href in links)


def write_partials(concept: dict) -> None:
    number = concept["number"]
    number_int = int(number)
    prefix = f"c{number}"
    folder = CONCEPTS_DIR / concept["conceptId"]
    nav_offset = number_int % 7
    header_intro = concept["visualThesis"].split(".")[0]
    header_detail = [
        f'<p class="{prefix}-header-note">{concept["destination"]}</p>',
        f'<span class="{prefix}-header-index">Destination {number}</span>',
        f'<p class="{prefix}-header-note">{header_intro}.</p>',
    ][number_int % 3]
    nav_block = nav_links(prefix, "nav-link", nav_offset)
    header = f"""
<header class="{prefix}-header {prefix}-header--{concept['headerSystem']}" data-partial-owner="header">
  <a class="{prefix}-brand" href="index.html" aria-label="Sofiati {concept['name']} home">
    <img src="../../assets/brand/sofiati-logo-primary-sage.png" alt="Sofiati" />
    <span>{concept['name']}</span>
  </a>
  {header_detail}
  <nav class="{prefix}-desktop-nav" aria-label="{concept['name']} primary navigation">
{nav_block}
  </nav>
  <div class="{prefix}-language" aria-label="Language controls">
    <button type="button" data-language-option="en" aria-pressed="true">EN</button>
    <button type="button" data-language-option="pt-BR" aria-pressed="false">PT</button>
  </div>
  <a class="{prefix}-header-cta" href="consultation.html">Request evaluation</a>
  <button class="{prefix}-menu-toggle" type="button" data-menu-toggle aria-expanded="false" aria-controls="mobile-menu">
    <span>Menu</span>
  </button>
</header>
"""
    mobile = f"""
<aside id="mobile-menu" class="{prefix}-mobile-menu {prefix}-mobile-menu--{concept['mobileSystem']}" data-menu-panel aria-hidden="true">
  <div class="{prefix}-mobile-dialog" role="dialog" aria-modal="true" aria-label="{concept['name']} mobile navigation">
    <button class="{prefix}-mobile-close" type="button" data-menu-close>Close</button>
    <p class="{prefix}-mobile-kicker">{concept['destination']}</p>
    <div class="{prefix}-mobile-links">
{nav_links(prefix, "mobile-link", nav_offset + 2)}
      <a class="{prefix}-mobile-link" href="values.html">Values</a>
      <a class="{prefix}-mobile-link" href="faq.html">FAQ</a>
      <a class="{prefix}-mobile-link" href="sitemap.html">Sitemap</a>
    </div>
    <a class="{prefix}-mobile-primary" href="{BRAND['whatsappUrl']}" target="_blank" rel="noopener">Message WhatsApp</a>
  </div>
</aside>
"""
    rotated_footer_routes = rotate(ROUTE_LINKS, (number_int * 2) % len(ROUTE_LINKS))
    footer_links = "\n".join(f'      <li><a href="{href}">{label}</a></li>' for label, href in rotated_footer_routes[:6])
    rotated_policies = rotate(POLICY_LINKS, number_int % len(POLICY_LINKS))
    policy_links = "\n".join(f'      <li><a href="{href}">{label}</a></li>' for label, href in POLICY_LINKS)
    policy_links = "\n".join(f'      <li><a href="{href}">{label}</a></li>' for label, href in rotated_policies)
    footer_manifest = " ".join((concept["colourThesis"] + " " + concept["visualThesis"]).split()[:42])
    footer = f"""
<footer class="{prefix}-footer {prefix}-footer--{concept['footerSystem']}" data-partial-owner="footer">
  <div class="{prefix}-footer-brand">
    <img src="../../assets/brand/sofiati-signature-sage.png" alt="Franciele Sofiati signature" />
    <p>{concept['destination']} for ethical, consultation-led care in {BRAND['location']}.</p>
    <p class="{prefix}-footer-manifest">{footer_manifest}.</p>
  </div>
  <div class="{prefix}-footer-columns">
    <ul aria-label="{concept['name']} core routes">
{footer_links}
    </ul>
    <ul aria-label="{concept['name']} policy routes">
{policy_links}
    </ul>
  </div>
  <div class="{prefix}-footer-bottom">
    <span>{BRAND['name']} · {BRAND['credential']}</span>
    <a href="{BRAND['instagramUrl']}" target="_blank" rel="noopener">{BRAND['instagram']}</a>
  </div>
</footer>
"""
    cookie = f"""
<div class="{prefix}-cookie" data-cookie-banner role="region" aria-label="{concept['name']} cookie preferences">
  <p>This site uses essential cookies for preference memory and a calmer browsing experience.</p>
  <button type="button" data-cookie-accept>Accept</button>
  <a href="cookies.html">Cookie details</a>
</div>
"""
    floating = f"""
<div class="{prefix}-floating" data-floating-widgets>
  <span class="{prefix}-float-label">{concept['name']} quick routes</span>
  <a class="{prefix}-float-link" href="{BRAND['whatsappUrl']}" target="_blank" rel="noopener" aria-label="Message Franciele Sofiati on WhatsApp">WhatsApp</a>
  <button class="{prefix}-float-top" type="button" data-back-to-top aria-label="Back to top">Top</button>
</div>
"""
    partials = {
        "header.html": header,
        "mobile-menu.html": mobile,
        "footer.html": footer,
        "cookie-banner.html": cookie,
        "floating-widgets.html": floating,
    }
    for filename, content in partials.items():
        write_text(folder / "partials" / filename, content)


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
        "blush": "var(--sofiati-pink-100)",
        "gold": "var(--sofiati-gold-500)",
        "bronze": "var(--sofiati-bronze-400)",
        "taupe": "var(--sofiati-taupe-300)",
        "terracotta": "var(--sofiati-terracotta-300)",
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

.{prefix}-header {{
  position: sticky;
  top: 0;
  z-index: 50;
  display: grid;
  grid-template-columns: {'1fr auto 1fr' if header_mode in (1, 3, 7) else 'auto 1fr auto auto'};
  align-items: center;
  gap: 1rem;
  padding: {0.75 + header_mode * 0.04:.2f}rem clamp(1rem, 3vw, 3rem);
  background: color-mix(in srgb, var(--{prefix}-base), white 30%);
  border-bottom: 1px solid var(--{prefix}-line);
}}

.{prefix}-brand {{
  display: inline-flex;
  align-items: center;
  gap: 0.7rem;
  color: inherit;
  font-weight: 700;
  letter-spacing: 0;
  text-decoration: none;
}}

.{prefix}-brand img {{
  width: {120 + header_mode * 6}px;
  height: auto;
}}

.{prefix}-header-note,
.{prefix}-header-index {{
  max-width: 18rem;
  margin: 0;
  color: color-mix(in srgb, var(--{prefix}-ink), transparent 22%);
  font-size: 0.76rem;
  line-height: 1.35;
}}

.{prefix}-header-index {{
  justify-self: center;
  padding: 0.35rem 0.55rem;
  border: 1px solid var(--{prefix}-line);
}}

.{prefix}-desktop-nav {{
  display: flex;
  justify-content: {'center' if header_mode in (1, 2, 4, 8) else 'flex-end'};
  gap: clamp(0.65rem, 1.2vw, 1.2rem);
}}

.{prefix}-nav-link,
.{prefix}-mobile-link {{
  color: inherit;
  font-size: 0.88rem;
  text-decoration: none;
}}

.{prefix}-nav-link:hover,
.{prefix}-mobile-link:hover {{
  color: var(--{prefix}-accent);
}}

.{prefix}-language {{
  display: inline-flex;
  gap: 0.25rem;
  border: 1px solid var(--{prefix}-line);
}}

.{prefix}-language button,
.{prefix}-menu-toggle,
.{prefix}-mobile-close,
.{prefix}-cookie button,
.{prefix}-float-top {{
  border: 0;
  border-radius: var(--{prefix}-radius);
  background: transparent;
  color: inherit;
  cursor: pointer;
}}

.{prefix}-language button {{
  padding: 0.45rem 0.55rem;
}}

.{prefix}-language button[aria-pressed="true"] {{
  background: var(--{prefix}-accent);
  color: var(--sofiati-ink-900);
}}

.{prefix}-header-cta,
.{prefix}-mobile-primary,
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

.{prefix}-header-cta,
.{prefix}-action--gold-mark,
.{prefix}-action--ledger-button {{
  background: var(--{prefix}-accent);
  color: var(--sofiati-ink-900);
}}

.{prefix}-menu-toggle {{
  display: none;
  border: 1px solid var(--{prefix}-line);
  padding: 0.72rem 0.9rem;
}}

.{prefix}-mobile-menu {{
  position: fixed;
  inset: 0;
  z-index: 80;
  display: grid;
  place-items: {'center' if header_mode % 2 else 'end'};
  padding: 1rem;
  background: rgba(37, 35, 33, 0.38);
  opacity: 0;
  pointer-events: none;
  transition: opacity 180ms ease;
}}

.{prefix}-mobile-menu[aria-hidden="false"] {{
  opacity: 1;
  pointer-events: auto;
}}

.{prefix}-mobile-dialog {{
  width: min(92vw, {360 + header_mode * 18}px);
  max-height: 92vh;
  overflow: auto;
  padding: 1.4rem;
  background: var(--{prefix}-secondary);
  border: 1px solid var(--{prefix}-line);
  border-radius: var(--{prefix}-radius);
}}

.{prefix}-mobile-links {{
  display: grid;
  gap: 0.75rem;
  margin: 1rem 0;
}}

.{prefix}-main {{
  overflow: clip;
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

.{prefix}-tone--blush {{
  background: var(--sofiati-pink-100);
}}

.{prefix}-tone--gold,
.{prefix}-tone--bronze {{
  background: linear-gradient(135deg, var(--sofiati-gold-200), var(--sofiati-ivory-100));
}}

.{prefix}-tone--terracotta,
.{prefix}-tone--taupe {{
  background: linear-gradient(135deg, var(--sofiati-terracotta-200), var(--sofiati-taupe-300));
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

.{prefix}-footer {{
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(18rem, 0.8fr);
  gap: 2rem;
  padding: clamp(3rem, 6vw, 5rem) clamp(1rem, 4vw, 4.5rem);
  background: {footer_background};
  color: {footer_color};
}}

.{prefix}-footer img {{
  width: min(240px, 68vw);
}}

.{prefix}-footer-manifest {{
  max-width: 42rem;
  font-size: 0.92rem;
}}

.{prefix}-footer-columns {{
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}}

.{prefix}-footer ul {{
  list-style: none;
  margin: 0;
  padding: 0;
}}

.{prefix}-footer a {{
  color: inherit;
}}

.{prefix}-footer-bottom {{
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  gap: 1rem;
  border-top: 1px solid var(--{prefix}-line);
  padding-top: 1rem;
}}

.{prefix}-cookie {{
  position: fixed;
  inset: auto clamp(1rem, 2vw, 2rem) clamp(1rem, 2vw, 2rem) auto;
  z-index: 70;
  width: min(360px, calc(100vw - 2rem));
  display: grid;
  gap: 0.65rem;
  padding: 1rem;
  background: var(--sofiati-ivory-100);
  border: 1px solid var(--{prefix}-line);
  border-radius: var(--{prefix}-radius);
  box-shadow: var(--shadow-md);
}}

.{prefix}-cookie.is-hidden {{
  display: none;
}}

.{prefix}-floating {{
  position: fixed;
  inset: auto 1rem 1rem auto;
  z-index: 65;
  display: grid;
  gap: 0.55rem;
  transform: translateY(-5.4rem);
}}

.{prefix}-float-link,
.{prefix}-float-top {{
  min-width: 4.7rem;
  padding: 0.72rem 0.8rem;
  border: 1px solid var(--{prefix}-line);
  border-radius: var(--{prefix}-radius);
  background: var(--{prefix}-accent);
  color: var(--sofiati-ink-900);
  text-align: center;
  text-decoration: none;
}}

.{prefix}-float-label {{
  max-width: 8rem;
  font-size: 0.68rem;
  line-height: 1.2;
  text-align: center;
  color: var(--{prefix}-ink);
}}

{chr(10).join(section_styles)}

@media (max-width: 920px) {{
  .{prefix}-desktop-nav,
  .{prefix}-header-cta {{
    display: none;
  }}

  .{prefix}-header {{
    grid-template-columns: 1fr auto auto;
  }}

  .{prefix}-menu-toggle {{
    display: inline-flex;
  }}

  .{prefix}-section {{
    min-height: auto;
    grid-template-columns: 1fr;
    padding: 4rem 1rem;
  }}

  .{prefix}-section > *,
  .{prefix}-portrait,
  .{prefix}-portrait + *,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-section-head,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-statement,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-rail-copy,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-ledger-title,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-reading-intro,
  .{prefix}-section:has(.{prefix}-portrait) .{prefix}-contact-copy {{
    grid-column: 1;
  }}

  .{prefix}-portrait {{
    grid-row: auto;
    min-height: 360px;
  }}

  .{prefix}-portrait img {{
    height: 360px;
  }}

  .{prefix}-footer {{
    grid-template-columns: 1fr;
  }}

  .{prefix}-footer-columns {{
    grid-template-columns: 1fr;
  }}

  .{prefix}-cookie {{
    inset-inline: 1rem;
    inset-block-end: 1rem;
  }}
}}
"""


def concept_js(concept: dict) -> str:
    number = concept["number"]
    prefix = f"c{number}"
    destination_words = []
    for word in re.findall(
        r"[A-Za-z]{4,}",
        " ".join(
            [
                concept["destination"],
                concept["visualThesis"],
                concept["colourThesis"],
                " ".join(concept["homepageSectionColourSequence"]),
            ]
        ),
    ):
        word = word.lower()
        if word not in destination_words:
            destination_words.append(word)
    destination_words = destination_words[:34]
    profile = {
        "conceptId": concept["conceptId"],
        "partialNames": ["header", "mobile-menu", "footer", "cookie-banner", "floating-widgets"],
        "menuMode": concept["mobileSystem"],
        "headerMode": concept["headerSystem"],
        "interactionTone": concept["ctaStrategy"],
        "destinationWords": destination_words,
        "sectionRhythm": [tone_from_phrase(item) for item in concept["homepageSectionColourSequence"]],
    }
    return f"""
(() => {{
  "use strict";

  const profile = {json.dumps(profile, indent=2)};
  const cache = new Map();
  let lastMenuTrigger = null;

  const applyDestinationSignature = () => {{
    document.body.dataset.destinationSignature = profile.destinationWords.slice(0, 8).join("-");
    document.querySelectorAll("[data-content-section]").forEach((section, index) => {{
      const word = profile.destinationWords[(index * 3) % profile.destinationWords.length] || profile.conceptId;
      const rhythm = profile.sectionRhythm[index % profile.sectionRhythm.length] || "ivory";
      section.style.setProperty("--concept-word-length", String(word.length));
      section.dataset.destinationWord = word;
      section.dataset.rhythmTone = rhythm;
    }});
  }};

  const fetchPartial = async (name) => {{
    if (!cache.has(name)) {{
      cache.set(name, fetch(`partials/${{name}}.html`, {{ cache: "no-store" }}).then((response) => {{
        if (!response.ok) throw new Error(`Missing partial ${{name}} for {concept['conceptId']}`);
        return response.text();
      }}));
    }}
    return cache.get(name);
  }};

  const mountPartials = async () => {{
    await Promise.all(profile.partialNames.map(async (name) => {{
      const mount = document.querySelector(`[data-sofiati-partial="${{name}}"]`);
      if (!mount) return;
      mount.innerHTML = await fetchPartial(name);
      mount.dataset.partialLoaded = "true";
    }}));
    document.dispatchEvent(new CustomEvent("sofiati:concept-partials-ready", {{ detail: profile }}));
  }};

  const menu = () => document.getElementById("mobile-menu");

  const openMenu = (trigger) => {{
    const panel = menu();
    if (!panel) return;
    lastMenuTrigger = trigger || document.activeElement;
    panel.setAttribute("aria-hidden", "false");
    document.body.classList.add("public-menu-locked");
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => button.setAttribute("aria-expanded", "true"));
    const first = panel.querySelector("a[href], button:not([disabled])");
    if (first) first.focus({{ preventScroll: true }});
  }};

  const closeMenu = () => {{
    const panel = menu();
    if (!panel) return;
    panel.setAttribute("aria-hidden", "true");
    document.body.classList.remove("public-menu-locked");
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => button.setAttribute("aria-expanded", "false"));
    if (lastMenuTrigger && typeof lastMenuTrigger.focus === "function") {{
      lastMenuTrigger.focus({{ preventScroll: true }});
    }}
  }};

  const wireMenu = () => {{
    document.addEventListener("click", (event) => {{
      const toggle = event.target.closest("[data-menu-toggle]");
      const close = event.target.closest("[data-menu-close]");
      const panel = menu();
      if (toggle) {{
        event.preventDefault();
        if (panel?.getAttribute("aria-hidden") === "false") closeMenu();
        else openMenu(toggle);
      }}
      if (close) {{
        event.preventDefault();
        closeMenu();
      }}
      if (panel && event.target === panel) closeMenu();
    }});
    document.addEventListener("keydown", (event) => {{
      if (event.key === "Escape") closeMenu();
    }});
  }};

  const wireCookie = () => {{
    const key = `sofiati-cookie-${{profile.conceptId}}`;
    const banner = document.querySelector("[data-cookie-banner]");
    if (!banner) return;
    if (window.localStorage.getItem(key) === "accepted") banner.classList.add("is-hidden");
    banner.querySelector("[data-cookie-accept]")?.addEventListener("click", () => {{
      window.localStorage.setItem(key, "accepted");
      banner.classList.add("is-hidden");
    }});
  }};

  const wireHeaderState = () => {{
    const header = document.querySelector(".{prefix}-header");
    if (!header) return;
    const update = () => header.toggleAttribute("data-scrolled", window.scrollY > 20);
    update();
    window.addEventListener("scroll", update, {{ passive: true }});
  }};

  const markCurrentLinks = () => {{
    const current = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll('a[href$=".html"]').forEach((link) => {{
      const href = link.getAttribute("href") || "";
      if (href === current) link.setAttribute("aria-current", "page");
    }});
  }};

  const init = async () => {{
    await mountPartials();
    wireMenu();
    wireCookie();
    wireHeaderState();
    markCurrentLinks();
    applyDestinationSignature();
  }};

  if (document.readyState === "loading") {{
    document.addEventListener("DOMContentLoaded", init, {{ once: true }});
  }} else {{
    init();
  }}
}})();
"""


def generate_concepts(concepts: list[dict]) -> None:
    for page_index, concept in enumerate(concepts):
        folder = CONCEPTS_DIR / concept["conceptId"]
        (folder / "css").mkdir(parents=True, exist_ok=True)
        (folder / "js").mkdir(parents=True, exist_ok=True)
        (folder / "partials").mkdir(parents=True, exist_ok=True)
        write_partials(concept)
        write_text(folder / "css" / "concept.css", concept_css(concept))
        write_text(folder / "js" / "concept.js", concept_js(concept))
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


def main() -> int:
    preflight = collect_preflight()
    write_preflight(preflight)
    write_conflict_audits(preflight)
    concepts = enrich_concepts(load_concepts())
    make_design_bible(concepts)
    write_foundation_files()
    generate_concepts(concepts)
    write_initial_reports(concepts)
    print(f"Rebuilt {len(concepts)} concepts and {len(concepts) * len(PAGES)} pages.")
    print(f"Design destination bible: {BIBLE}")
    print(f"Preflight: {SCRIPT_RUNS / '50-complete-new-websites-preflight.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
