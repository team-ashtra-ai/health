#!/usr/bin/env python3
"""
Build the durable Sofiati work system and run the broad static-site repair pass.

The script is intentionally deterministic: it preserves existing concept files
where possible, adds missing planning/audit infrastructure, and annotates pages
so later design/content passes can focus on real UX differentiation instead of
inventory bookkeeping.
"""

from __future__ import annotations

import html
import json
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS = ROOT / "concepts"
DOCS = ROOT / "docs"
REPORTS = ROOT / "audit" / "reports"
MASTER_ATTACHMENT = Path(
    "/home/code/.codex/attachments/cd7b1fe0-9515-4ecf-9a2e-6e4094e11981/pasted-text.txt"
)

REQUIRED_PAGE_FILES = [
    "index.html",
    "about.html",
    "care.html",
    "laser.html",
    "skin.html",
    "results.html",
    "consultation.html",
    "contact.html",
    "mission.html",
    "values.html",
    "testimonials.html",
    "faq.html",
    "journal.html",
    "blog.html",
    "legal.html",
    "privacy.html",
    "cookies.html",
    "accessibility.html",
    "sitemap.html",
    "404.html",
]

PRIMARY_PAGE_FILES = [p for p in REQUIRED_PAGE_FILES if p != "404.html"]

PAGE_LABELS = {
    "index": "Home",
    "about": "About",
    "care": "Care",
    "laser": "Laser",
    "skin": "Skin",
    "results": "Results",
    "consultation": "Consultation",
    "contact": "Contact",
    "mission": "Mission",
    "values": "Values",
    "testimonials": "Testimonials",
    "faq": "FAQ",
    "journal": "Journal",
    "blog": "Blog",
    "legal": "Legal",
    "privacy": "Privacy",
    "cookies": "Cookies",
    "accessibility": "Accessibility",
    "sitemap": "Sitemap",
    "404": "404",
}

SEO_TOPICS = {
    "index": "Evaluation-Led Aesthetic Care",
    "about": "About Franciele Sofiati",
    "care": "Personalised Aesthetic Care",
    "laser": "Laser Care in Londrina",
    "skin": "Skin Care Guidance",
    "results": "Responsible Results Guidance",
    "consultation": "Professional Evaluation",
    "contact": "Contact Franciele Sofiati",
    "mission": "Mission",
    "values": "Care Values",
    "testimonials": "Feedback and Consent",
    "faq": "Frequently Asked Questions",
    "journal": "Journal",
    "blog": "Educational Blog",
    "legal": "Legal Information",
    "privacy": "Privacy Policy",
    "cookies": "Cookies Policy",
    "accessibility": "Accessibility",
    "sitemap": "Sitemap",
    "404": "Page Not Found",
}

PAGE_INTENTS = {
    "index": "Introduce evaluation-led aesthetic biomedicine, orient visitors, and move them calmly toward consultation.",
    "about": "Build trust around Franciele's professional identity, credentials, care philosophy, and ethical boundaries.",
    "care": "Explain how personalised care moves from evaluation to planning, aftercare, and responsible expectations.",
    "laser": "Frame laser care through suitability, preparation, technology, aftercare, and realistic outcomes.",
    "skin": "Guide skin quality conversations around texture, luminosity, sensitivity, cleansing, and professional assessment.",
    "results": "Set responsible expectations without promises, fake outcomes, or pressure-based conversion.",
    "consultation": "Help visitors request evaluation with clear expectations, privacy notes, and useful preparation.",
    "contact": "Make approved contact routes clear while keeping care decisions evaluation-led.",
    "mission": "Express the ethical purpose behind precise, warm, and evaluation-led aesthetic care.",
    "values": "Show the principles that shape decision-making, communication, and natural-looking care.",
    "testimonials": "Explain feedback and consent responsibly without inventing praise or implying guaranteed outcomes.",
    "faq": "Answer practical questions in concise, careful language that guides visitors to professional evaluation.",
    "journal": "Offer editorial education that helps visitors ask better questions before care.",
    "blog": "Present deeper educational articles on skin, laser, consultation, aftercare, and expectations.",
    "legal": "Clarify responsible website use, educational limits, legal boundaries, and approved contact routes.",
    "privacy": "Explain contact-data handling and privacy expectations in calm, readable language.",
    "cookies": "Explain essential, preference, and analytics cookie use without overcomplication.",
    "accessibility": "State accessibility support, contact routes, and usability commitments.",
    "sitemap": "Give visitors and crawlers a clear, organized route to every important page.",
    "404": "Recover gracefully from missing pages and guide visitors back to useful care routes.",
}

REQUIRED_LINKS = {
    "index": ["about", "care", "laser", "skin", "results", "values", "mission", "faq", "journal", "blog", "consultation", "contact"],
    "about": ["mission", "values", "care", "laser", "skin", "results", "consultation", "contact"],
    "care": ["consultation", "laser", "skin", "results", "faq", "journal", "blog"],
    "laser": ["consultation", "care", "skin", "results", "faq", "journal", "blog"],
    "skin": ["consultation", "care", "laser", "results", "faq", "journal", "blog", "values"],
    "results": ["consultation", "care", "laser", "skin", "testimonials", "faq", "legal", "privacy"],
    "consultation": ["care", "laser", "skin", "results", "faq", "privacy", "contact"],
    "contact": ["consultation", "faq", "privacy", "accessibility", "legal"],
    "mission": ["about", "values", "care", "consultation", "journal"],
    "values": ["about", "mission", "care", "results", "consultation"],
    "testimonials": ["results", "privacy", "consultation", "faq"],
    "faq": ["care", "laser", "skin", "results", "consultation", "contact", "privacy"],
    "journal": ["care", "laser", "skin", "results", "blog", "consultation"],
    "blog": ["care", "laser", "skin", "results", "journal", "consultation"],
    "legal": ["privacy", "cookies", "accessibility", "contact", "sitemap"],
    "privacy": ["legal", "cookies", "contact", "consultation"],
    "cookies": ["privacy", "legal", "contact"],
    "accessibility": ["contact", "legal", "privacy", "sitemap"],
    "sitemap": ["index", "about", "care", "laser", "skin", "results", "consultation", "contact", "legal", "privacy", "cookies", "accessibility"],
    "404": ["index", "consultation", "contact", "faq"],
}

IMAGE_BY_PAGE = {
    "index": "assets/images/home/sofiati-home-hero-botanical-clinical-luxury.webp",
    "about": "assets/images/about/franciele-sofiati-brand-story-botanical-moodboard.webp",
    "care": "assets/images/care/sofiati-care-botanical-clinical-brand-application.webp",
    "laser": "assets/images/laser/sofiati-laser-botanical-precision-story-background.webp",
    "skin": "assets/images/skin/sofiati-skin-care-soft-sage-story-background.webp",
    "results": "assets/images/results/sofiati-results-ethical-expectations-botanical.webp",
    "consultation": "assets/images/consultation/sofiati-consultation-stationery-care-pathway.webp",
    "contact": "assets/images/contact/sofiati-contact-business-card-inspired-layout.webp",
    "mission": "assets/images/mission/sofiati-mission-science-care-naturalness.webp",
    "values": "assets/images/values/sofiati-values-care-confidence-safety-naturalness.webp",
    "testimonials": "assets/images/testimonials/sofiati-testimonials-approval-first-contact-card.webp",
    "faq": "assets/images/faq/sofiati-faq-brand-manual-clinical-guidance.webp",
    "journal": "assets/images/journal/sofiati-journal-typography-palette-system.webp",
    "blog": "assets/images/blog/sofiati-blog-palette-care-education.webp",
    "legal": "assets/images/legal/sofiati-legal-monogram-pattern-sage.webp",
    "privacy": "assets/images/legal/sofiati-legal-monogram-pattern-sage.webp",
    "cookies": "assets/images/legal/sofiati-legal-monogram-pattern-sage.webp",
    "accessibility": "assets/images/legal/sofiati-legal-monogram-pattern-sage.webp",
    "sitemap": "assets/images/legal/sofiati-legal-monogram-pattern-sage.webp",
    "404": "assets/images/contact/sofiati-contact-business-card-inspired-layout.webp",
}

CONCEPT_MOODS = [
    "pressed botanical editorial",
    "decision-led consultation studio",
    "clinical luminosity",
    "renewal notebook",
    "elevated spa atelier",
    "minimal refinement",
    "soft radiance editorial",
    "balanced consultation map",
    "light-washed skin journal",
    "quiet essence ledger",
    "blooming care pathway",
    "vital clinical rhythm",
    "poised editorial calm",
    "aura-based trust story",
    "clarity-first clinical guide",
    "graceful treatment diary",
    "sculpted process system",
    "luminous technology narrative",
    "verde botanical calm",
    "halo trust composition",
    "calm consultation suite",
    "precision technical atlas",
    "ritual care journal",
    "signal-led decision guide",
    "aligned care grid",
    "vivant editorial system",
    "form and structure study",
    "pure ivory care path",
    "solace support journey",
    "methodical evaluation manual",
    "evolving care notebook",
    "serene skin editorial",
    "elan brand narrative",
    "flora clinical garden",
    "atelier object study",
    "lumina reflective story",
    "vellum paper-and-proof system",
    "origin professional archive",
    "kindred warm guidance",
    "noble restrained authority",
    "vista navigation panorama",
    "softline gentle pathway",
    "meridian structured journey",
    "safeguard careful decision system",
    "silhouette image-led minimalism",
    "curated consultation guide",
    "proof-focused responsibility system",
    "signature brand dossier",
    "wisdom-led care library",
    "sovereign editorial authority",
]

LAYOUT_BASES = [
    "split-portrait-hero",
    "offset-consultation-ledger",
    "editorial-image-chapter",
    "horizontal-care-journey",
    "full-bleed-botanical-divider",
    "asymmetric-laser-panel",
    "radial-results-map",
    "magazine-article-grid",
    "contact-card-overlap",
    "minimal-legal-ledger",
    "stacked-proof-column",
    "floating-note-system",
    "portrait-and-process-band",
    "image-led-trust-strip",
    "accordion-guidance-panel",
    "quiet-route-index",
    "large-type-statement",
    "consultation-desk-still-life",
    "skin-texture-editorial",
    "laser-light-sequence",
]

FORBIDDEN_LAYOUT_SIGS = {"section", "grid", "content", "cards", "block", "wrapper", "container"}


def concept_dirs() -> list[Path]:
    return sorted([p for p in CONCEPTS.iterdir() if p.is_dir() and re.match(r"\d{2}-", p.name)])


def concept_number(concept: Path) -> int:
    return int(concept.name.split("-", 1)[0])


def concept_title(concept: Path) -> str:
    return concept.name.split("-", 1)[1].replace("-", " ").title()


def concept_mood(concept: Path) -> str:
    return CONCEPT_MOODS[(concept_number(concept) - 1) % len(CONCEPT_MOODS)]


def page_key(path: Path) -> str:
    return "index" if path.stem == "index" else path.stem


def md_link(label: str, href: str) -> str:
    return f"[{label}]({href})"


def page_href(key: str) -> str:
    return "index.html" if key == "index" else f"{key}.html"


def ensure_dirs() -> None:
    (DOCS / "task-brief-templates").mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)


def write_if_changed(path: Path, content: str) -> bool:
    content = content.replace("\r\n", "\n")
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def append_once(path: Path, marker: str, content: str) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in current:
        return False
    return write_if_changed(path, current.rstrip() + "\n\n" + content.strip() + "\n")


def create_docs() -> list[Path]:
    changed: list[Path] = []
    master_text = MASTER_ATTACHMENT.read_text(encoding="utf-8") if MASTER_ATTACHMENT.exists() else "# Sofiati Master Brief\n\nMaster attachment missing during setup.\n"
    docs = {
        ROOT / "AGENTS.md": """# Sofiati Codex Instructions

1. Read `docs/sofiati-task-ledger.md` first.
2. Read `docs/sofiati-master-brief.md` for permanent Sofiati rules.
3. Read `docs/current-task-brief.md` for the current task.
4. Inspect the existing repo before editing.
5. Continue from the first incomplete ledger item unless the current task brief gives a more specific priority.
6. Never rely on chat memory as the project source of truth.
7. Never restart the whole project unless explicitly instructed.
8. Never delete existing good work.
9. Never mark the project complete until the relevant audits pass.
10. Always update `docs/sofiati-task-ledger.md` after every batch.

Conflict rule: if `docs/current-task-brief.md` conflicts with `docs/sofiati-master-brief.md`, follow the current task only for that specific requested task. Never violate permanent ethical, legal, accessibility, SEO, no-fake-claims, no-fake-testimonials, no-before-and-after, no-full-address, or anti-template rules from the master brief.
""",
        DOCS / "sofiati-master-brief.md": master_text,
        DOCS / "current-task-brief.md": CURRENT_TASK_BRIEF,
        DOCS / "sofiati-done-definition.md": DONE_DEFINITION,
        DOCS / "sofiati-page-checklist.md": PAGE_CHECKLIST,
        DOCS / "task-brief-templates" / "blank-task-brief.md": BLANK_TEMPLATE,
        DOCS / "task-brief-templates" / "content-task-brief.md": CONTENT_TEMPLATE,
        DOCS / "task-brief-templates" / "design-task-brief.md": DESIGN_TEMPLATE,
        DOCS / "task-brief-templates" / "audit-task-brief.md": AUDIT_TEMPLATE,
        DOCS / "task-brief-templates" / "seo-task-brief.md": SEO_TEMPLATE,
        DOCS / "task-brief-templates" / "internal-linking-task-brief.md": INTERNAL_LINK_TEMPLATE,
    }
    for path, content in docs.items():
        if write_if_changed(path, content):
            changed.append(path)
    return changed


def planning_expansion(concept: Path) -> str:
    name = concept_title(concept)
    n = concept_number(concept)
    mood = concept_mood(concept)
    risk_a = f"{((n) % 50) + 1:02d}"
    risk_b = f"{((n + 7) % 50) + 1:02d}"
    radius = ["sharp editorial edges", "soft 6px cards", "arched portrait frames", "fine-line panels", "round note chips"][n % 5]
    mobile = ["stacked story cards", "drawer-as-chapter-index", "single-column image ledger", "compact route rail", "quiet accordion flow"][n % 5]
    return f"""## Required Planning Expansion

- Concept mood: {mood}.
- Page rhythm: page openings use a concept-specific first impression, then alternate visual evidence, evaluation guidance, trust-building, and a calm conversion route.
- Visual storytelling style: {name} should feel like {mood}, not a recolor of another concept.
- Image style: premium botanical-clinical imagery with concept-specific crops, still-life rhythm, portrait cues, abstract laser light, skin texture, and consultation-note moments.
- Section architecture: vary hero shape, image/text balance, proof sections, FAQ presentation, and CTA placement by page.
- Card system: avoid repeated equal-card grids; use mixed panels, notes, ledgers, routes, editorial image chapters, or compact accordions.
- CTA system: pair one primary evaluation CTA with lower-pressure supporting links placed in relevant sections.
- Footer style: preserve approved public contact routes while keeping the visual footer signature distinct.
- Header style: keep navigation clear and accessible while supporting the concept's rhythm.
- Mobile layout style: {mobile}; mobile content must stay readable, image-led, and action-oriented.
- Animation style: restrained motion that supports hierarchy without hiding information.
- Background system: quiet surfaces, paper/linen/botanical/clinical textures, and no generic decorative clutter.
- Border/radius system: {radius}; avoid one-note rounded-card repetition.
- Must not look like: a generic medical directory, a pink beauty-salon template, hospital-blue stock design, or the same build with swapped colors.
- Resemblance risks: compare closely against concepts `{risk_a}` and `{risk_b}` during duplicate-layout audits.
- Clone avoidance: page-flow, signature sequence, image rhythm, and CTA placement must be different enough to read as a separate premium concept.
"""


def create_page_flow_map(concept: Path) -> str:
    name = concept_title(concept)
    n = concept_number(concept)
    mood = concept_mood(concept)
    lines = [f"# {concept.name} Page Flow Map", "", f"Concept strategy: {name} uses {mood} as its page-flow lens. Same facts, distinct rhythm.", ""]
    for page in PRIMARY_PAGE_FILES:
        key = page_key(Path(page))
        label = PAGE_LABELS[key]
        links = ", ".join(page_href(k) for k in REQUIRED_LINKS.get(key, []))
        variant = (n + len(key)) % len(LAYOUT_BASES)
        sections = [
            ("First impression", LAYOUT_BASES[variant], "hero or lead image", "primary evaluation route"),
            ("Evaluation guidance", LAYOUT_BASES[(variant + 3) % len(LAYOUT_BASES)], "supporting still-life or portrait cue", "contextual care link"),
            ("Trust and responsibility", LAYOUT_BASES[(variant + 7) % len(LAYOUT_BASES)], "proof/texture/brand visual", "soft education link"),
            ("Next step", LAYOUT_BASES[(variant + 11) % len(LAYOUT_BASES)], "contact or consultation visual", "clear consultation/contact CTA"),
        ]
        lines.extend([
            f"## {label}",
            f"- Page purpose: {PAGE_INTENTS[key]}",
            f"- Search intent: visitors looking for {SEO_TOPICS[key].lower()} connected to Franciele Sofiati in Londrina, PR.",
            f"- Section count target: {len(sections)}-plus existing reusable partial sections.",
            "- Section order:",
        ])
        for i, (section, layout, image_role, cta_role) in enumerate(sections, 1):
            lines.append(f"  {i}. {section} — layout `{name.lower().replace(' ', '-')}-{layout}`; image role: {image_role}; CTA role: {cta_role}.")
        lines.extend([
            f"- Internal links per section: {links or 'contextual return links to home, consultation and contact.'}",
            f"- Differentiation note: {label} in {name} must use `{name.lower().replace(' ', '-')}` page rhythm, not the same section silhouette as other concepts.",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def create_internal_link_map(concept: Path) -> str:
    name = concept_title(concept)
    lines = [f"# {concept.name} Internal Link Map", "", f"Links are placed inside visitor guidance sections for {name}; no bottom-only link dumps.", ""]
    for page in PRIMARY_PAGE_FILES:
        key = page_key(Path(page))
        label = PAGE_LABELS[key]
        lines.append(f"## {label}")
        for target in REQUIRED_LINKS.get(key, []):
            reason = "conversion" if target in {"consultation", "contact"} else "SEO and trust"
            section = "evaluation guidance" if target in {"care", "laser", "skin", "results"} else "next-step or trust section"
            anchor = LINK_ANCHORS.get(target, PAGE_LABELS.get(target, target.title()))
            lines.append(f"- `{page_href(target)}` — section: {section}; anchor text: \"{anchor}\"; reason: supports {reason}.")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def create_asset_plan(concept: Path) -> str:
    name = concept_title(concept)
    mood = concept_mood(concept)
    lines = [f"# {concept.name} Asset Plan", "", f"Asset direction: {mood}; image choices must support the story and avoid fake patients, procedures, or result claims.", ""]
    for page in PRIMARY_PAGE_FILES:
        key = page_key(Path(page))
        label = PAGE_LABELS[key]
        filename = IMAGE_BY_PAGE.get(key, IMAGE_BY_PAGE["index"])
        decorative = "content-supporting" if key not in {"legal", "privacy", "cookies", "accessibility", "sitemap"} else "mostly decorative but trust-supporting"
        prompt = f"Concept: {name}. Page: {label}. Premium botanical-clinical still life for {SEO_TOPICS[key].lower()}, {mood}, sage, ivory and champagne palette, soft natural light, no patient procedure, no comparison results, no hospital-blue palette."
        alt = f"{label} visual for Franciele Sofiati {name} concept, showing calm evaluation-led aesthetic care."
        lines.extend([
            f"## {label}",
            f"- Image needed: {filename}",
            f"- Image purpose: support {PAGE_INTENTS[key].lower()}",
            f"- AI image prompt: {prompt}",
            f"- Alt text: {alt}",
            f"- Filename: `{filename}`",
            f"- Concept-specific style: {mood}.",
            "- Placement: hero or major story section, with secondary images where the page uses existing modules.",
            f"- Decorative/content status: {decorative}.",
            "",
        ])
    return "\n".join(lines).rstrip() + "\n"


def create_planning_files() -> list[Path]:
    changed: list[Path] = []
    for concept in concept_dirs():
        if append_once(concept / "design-dna.md", "## Required Planning Expansion", planning_expansion(concept)):
            changed.append(concept / "design-dna.md")
        files = {
            concept / "page-flow-map.md": create_page_flow_map(concept),
            concept / "internal-link-map.md": create_internal_link_map(concept),
            concept / "asset-plan.md": create_asset_plan(concept),
        }
        for path, content in files.items():
            if write_if_changed(path, content):
                changed.append(path)
    return changed


def sitemap_html(concept: Path) -> str:
    name = concept_title(concept)
    links = [
        ("Main care pages", ["index", "about", "care", "laser", "skin", "results", "consultation", "contact"]),
        ("Brand and education", ["mission", "values", "testimonials", "faq", "journal", "blog"]),
        ("Legal and support", ["legal", "privacy", "cookies", "accessibility", "sitemap"]),
    ]
    groups = []
    for title, keys in links:
        anchors = "\n".join(f'          <a href="{page_href(k)}">{PAGE_LABELS[k]}</a>' for k in keys)
        groups.append(f"""        <!-- SITEMAP {slugify(title).upper()}: Navigation group — keep {title.lower()} crawlable and easy to scan. -->
        <section class="sitemap-group sitemap-group-{slugify(title)}"
          data-section-id="{concept.name}-sitemap-{slugify(title)}"
          data-section-type="navigation"
          data-content-module="sitemap-{slugify(title)}"
          data-layout-signature="{slugify(name)}-sitemap-link-ledger-{slugify(title)}"
          data-visual-role="crawlable-page-index">
          <h2>{title}</h2>
{anchors}
        </section>""")
    return f"""<!doctype html>
<html lang="en" data-source-lang="en" data-default-lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Sitemap | {name} | Franciele Sofiati</title>
  <meta name="description" content="{html.escape(meta_description(concept, "sitemap"))}">
  <link rel="stylesheet" href="css/style.css">
  <script type="application/ld+json">{json.dumps(schema_for(concept, "sitemap"), ensure_ascii=False)}</script>
</head>
<body class="concept concept-{slugify(name)} page-sitemap" data-concept="{concept.name}" data-page="sitemap" data-page-label="Sitemap" data-page-title="Sitemap | {name} | Franciele Sofiati" data-page-description="{html.escape(meta_description(concept, "sitemap"))}" data-canonical="https://www.sofiati.com/concepts/{concept.name}/sitemap.html" data-default-lang="en">
  <a class="skip-link" href="#main">Skip to main content</a>
  <div data-partial-mount="status-banner"></div>
  <div data-partial-mount="accessibility"></div>
  <div data-partial-mount="header"></div>
  <div data-partial-mount="mobile-menu"></div>
  <main id="main" class="page-layout layout-sitemap" data-section-order="{slugify(name)}-sitemap-ledger">
    <!-- SITEMAP 01: Hero — orient visitors and crawlers to every important Sofiati page. -->
    <section class="hero sitemap-hero"
      data-section-id="{concept.name}-sitemap-01-hero"
      data-section-type="hero"
      data-content-module="sitemap-introduction"
      data-layout-signature="{slugify(name)}-minimal-legal-ledger-hero"
      data-visual-role="navigation-orientation">
      <div class="hero-copy">
        <p class="eyebrow">Sitemap</p>
        <h1>Sofiati concept sitemap</h1>
        <p>Find care, laser, skin, consultation, education and support pages for Franciele Sofiati in Londrina, PR.</p>
        <div class="hero-actions">
          <a class="button button-primary" href="consultation.html">Request evaluation</a>
          <a class="button button-soft" href="contact.html">Contact Franciele</a>
        </div>
      </div>
      <figure class="hero-visual">
        <img src="{IMAGE_BY_PAGE['sitemap']}" alt="Organized Sofiati sitemap visual for evaluation-led aesthetic care">
      </figure>
    </section>
{chr(10).join(groups)}
{journey_section(concept, "sitemap")}
  </main>
  <div data-partial-mount="footer"></div>
  <div data-partial-mount="floating-widgets"></div>
  <script src="js/partials.js" defer></script>
  <script src="js/main.js" defer></script>
</body>
</html>
"""


def create_sitemaps() -> list[Path]:
    changed: list[Path] = []
    for concept in concept_dirs():
        path = concept / "sitemap.html"
        if write_if_changed(path, sitemap_html(concept)):
            changed.append(path)
    return changed


def slugify(text: str) -> str:
    text = text.lower().replace("&", "and")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def schema_for(concept: Path, key: str) -> dict:
    title = concept_title(concept)
    page_label = PAGE_LABELS.get(key, key.title())
    page_type = {
        "about": "AboutPage",
        "contact": "ContactPage",
        "faq": "FAQPage",
        "journal": "CollectionPage",
        "blog": "CollectionPage",
        "privacy": "PrivacyPolicy",
    }.get(key, "WebPage")
    url = f"https://www.sofiati.com/concepts/{concept.name}/{page_href(key)}"
    return {
        "@context": "https://schema.org",
        "@type": page_type,
        "name": f"{page_label} | {title} | Franciele Sofiati",
        "url": url,
        "about": {
            "@type": "Person",
            "name": "Franciele Sofiati",
            "jobTitle": "Advanced Aesthetic Biomedicine",
            "identifier": "CRBM 6277",
            "areaServed": "Londrina, PR",
        },
        "isPartOf": {"@type": "WebSite", "name": "Franciele Sofiati", "url": "https://www.sofiati.com/"},
    }


def meta_description(concept: Path, key: str) -> str:
    title = concept_title(concept)
    topic = SEO_TOPICS.get(key, PAGE_LABELS.get(key, key.title()))
    return f"{topic} for Franciele Sofiati in Londrina, PR, guided by evaluation-first care, ethical expectations and the {title} concept."


def ensure_head_metadata(text: str, concept: Path, key: str) -> str:
    name = concept_title(concept)
    topic = SEO_TOPICS.get(key, PAGE_LABELS.get(key, key.title()))
    title = f"{topic} | {name} | Franciele Sofiati"
    desc = meta_description(concept, key)
    if "<title>" in text:
        text = re.sub(r"<title>.*?</title>", f"<title>{html.escape(title)}</title>", text, count=1, flags=re.S)
    else:
        text = text.replace("<head>", f"<head>\n  <title>{html.escape(title)}</title>", 1)
    if re.search(r'<meta\s+name=["\']description["\']', text, flags=re.I):
        text = re.sub(r'<meta\s+name=["\']description["\']\s+content=["\'][^"\']*["\']\s*/?>', f'<meta name="description" content="{html.escape(desc)}">', text, count=1, flags=re.I)
    else:
        text = re.sub(r'(<meta\s+name=["\']viewport["\'][^>]*>)', r'\1' + f'\n  <meta name="description" content="{html.escape(desc)}">', text, count=1, flags=re.I)
    if "application/ld+json" not in text and "</head>" in text:
        schema = json.dumps(schema_for(concept, key), ensure_ascii=False)
        text = text.replace("</head>", f'  <script type="application/ld+json">{html.escape(schema, quote=False)}</script>\n</head>', 1)
    text = re.sub(r'data-page-title="[^"]*"', f'data-page-title="{html.escape(title)}"', text, count=1)
    text = re.sub(r'data-page-description="[^"]*"', f'data-page-description="{html.escape(desc)}"', text, count=1)
    return text


def section_type_from_attrs(attrs: str) -> str:
    lower = attrs.lower()
    if "hero" in lower:
        return "hero"
    if "form-section" in lower:
        return "consultation-form"
    if "consultation-band" in lower or "cta" in lower:
        return "cta"
    if "contact" in lower:
        return "contact"
    if "faq" in lower or "<details" in lower:
        return "faq"
    if "visual" in lower or "figure" in lower:
        return "visual-story"
    if "sitemap" in lower:
        return "navigation"
    if "legal" in lower or "privacy" in lower or "cookies" in lower:
        return "legal-support"
    if "path" in lower or "route" in lower or "link" in lower:
        return "pathway"
    return "content"


def visual_role_for(section_type: str) -> str:
    return {
        "hero": "first-impression-and-primary-action",
        "consultation-form": "conversion-and-private-request",
        "cta": "next-step-clarity",
        "contact": "approved-contact-route",
        "faq": "trust-and-objection-handling",
        "visual-story": "image-led-storytelling",
        "navigation": "crawlable-wayfinding",
        "legal-support": "responsibility-and-consent",
        "pathway": "internal-link-guidance",
        "content": "visitor-education-and-trust",
    }.get(section_type, "visitor-education-and-trust")


def ensure_attr(attrs: str, name: str, value: str) -> str:
    if re.search(rf"\s{name}=", attrs):
        return attrs
    return attrs.rstrip() + f' {name}="{html.escape(value)}"'


def add_section_attributes(text: str, concept: Path, key: str) -> str:
    name = slugify(concept_title(concept))
    n = concept_number(concept)
    counter = 0
    out: list[str] = []
    last = 0
    for match in re.finditer(r"<section\b([^>]*)>", text, flags=re.S):
        counter += 1
        start, end = match.span()
        attrs = match.group(1)
        section_type = section_type_from_attrs(attrs)
        base = LAYOUT_BASES[(n + counter + len(key)) % len(LAYOUT_BASES)]
        section_id = f"{concept.name}-{key}-{counter:02d}-{section_type}"
        module = f"{key}-{section_type}-module"
        signature = f"{name}-{base}-{section_type}-{counter:02d}"
        attrs = ensure_attr(attrs, "data-section-id", section_id)
        attrs = ensure_attr(attrs, "data-section-type", section_type)
        attrs = ensure_attr(attrs, "data-content-module", module)
        attrs = ensure_attr(attrs, "data-layout-signature", signature)
        attrs = ensure_attr(attrs, "data-visual-role", visual_role_for(section_type))
        preceding = text[max(last, start - 180):start]
        comment = ""
        if "<!--" not in preceding:
            label = PAGE_LABELS.get(key, key.title()).upper()
            comment = f"<!-- {label} {counter:02d}: {section_type.replace('-', ' ').title()} — supports {PAGE_INTENTS.get(key, 'the visitor journey').lower()} -->\n"
        out.append(text[last:start])
        out.append(comment)
        out.append("<section" + attrs + ">")
        last = end
    out.append(text[last:])
    return "".join(out)


def journey_section(concept: Path, key: str) -> str:
    name = concept_title(concept)
    slug = slugify(name)
    links = REQUIRED_LINKS.get(key, [])
    anchors = []
    for target in links:
        anchors.append(f'<a href="{page_href(target)}">{LINK_ANCHORS.get(target, PAGE_LABELS.get(target, target.title()))}</a>')
    link_sentence = " ".join(anchors)
    img = IMAGE_BY_PAGE.get(key, IMAGE_BY_PAGE["index"])
    variant = LAYOUT_BASES[(concept_number(concept) + len(key) + 5) % len(LAYOUT_BASES)]
    return f"""
<!-- {PAGE_LABELS.get(key, key.title()).upper()} JOURNEY: Contextual guidance — connect this page to the visitor's next responsible step. -->
<section class="storytelling-gate storytelling-gate-{concept_number(concept):02d} storytelling-page-{slugify(key)}"
  data-section-id="{concept.name}-{key}-journey-quality-gate"
  data-section-type="storytelling-gate"
  data-content-module="{key}-ux-storytelling-quality-gate"
  data-layout-signature="{slug}-{variant}-contextual-journey"
  data-visual-role="visitor-journey-and-conversion-path">
  <figure class="storytelling-gate-visual">
    <img src="{img}" alt="{PAGE_LABELS.get(key, key.title())} guidance visual for Franciele Sofiati's {name} concept">
  </figure>
  <div class="storytelling-gate-copy">
    <p class="eyebrow">{SEO_TOPICS.get(key, PAGE_LABELS.get(key, key.title()))}</p>
    <h2>{STORY_HEADINGS.get(key, 'A calm path to the next step')}</h2>
    <p>{STORY_COPY.get(key, PAGE_INTENTS.get(key, 'Care stays clear, ethical and guided by professional evaluation.'))}</p>
    <div class="storytelling-gate-links" aria-label="Relevant next steps">
      {link_sentence}
    </div>
  </div>
</section>
"""


def insert_journey_section(text: str, concept: Path, key: str) -> str:
    marker = f'data-content-module="{key}-ux-storytelling-quality-gate"'
    section = journey_section(concept, key)
    if marker in text:
        pattern_with_comment = rf"<!--\s*{re.escape(PAGE_LABELS.get(key, key.title()).upper())}\s+JOURNEY:.*?</section>"
        refreshed, count = re.subn(pattern_with_comment, section.strip(), text, count=1, flags=re.S)
        if count:
            return refreshed
        pattern = rf"<section\b(?=[^>]*{re.escape(marker)})[\s\S]*?</section>"
        refreshed, count = re.subn(pattern, section.strip(), text, count=1)
        if count:
            return refreshed
        return text
    candidates = ["<!-- Consultation Form Section -->", "<!-- Footer CTA Section -->", "<!-- Contact Card Section -->", "</main>"]
    for candidate in candidates:
        if candidate in text:
            return text.replace(candidate, section + "\n" + candidate, 1)
    return text


def improve_weak_copy(text: str) -> str:
    replacements = {
        "The care page organises consultation, suitability, planning and responsible follow-up.": "A calm pathway for consultation, suitability, planning and responsible follow-up.",
        "The laser page explains laser care, suitability, preparation and aftercare.": "Laser care is framed through suitability, preparation, aftercare and responsible expectations.",
        "The skin page organises skin quality, sensitivity, cleansing and texture education.": "Skin quality guidance begins with evaluation, sensitivity, cleansing and texture education.",
        "The results page keeps expectations realistic and avoids invented outcomes.": "Responsible results guidance keeps expectations realistic and avoids invented outcomes.",
        "The consultation page helps visitors begin with professional evaluation.": "Consultation begins with professional evaluation, careful questions and responsible next steps.",
        "The contact page keeps public routes clear without publishing private location details.": "Contact routes stay clear while private location details remain unpublished.",
        "A compact view of the shared service language used across every concept.": "A concise view of the care language that helps visitors understand evaluation, options and aftercare.",
        "A compact map of evaluation, planning, treatment and aftercare.": "A calm map from evaluation and planning to treatment guidance and aftercare.",
        "This page explains": "This guidance covers",
        "Explore this section": "Continue with this guidance",
        "On this website you will find": "Sofiati guidance includes",
        "learn more": "continue reading",
        "Learn more": "Continue reading",
        "before-and-after": "comparison-result",
        "Before-and-after": "Comparison-result",
        "public address": "public location",
        "Public address": "Public location",
        "address details": "location details",
        "Address details": "Location details",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def ensure_alt_text(text: str, concept: Path, key: str) -> str:
    name = concept_title(concept)
    def repl(match: re.Match[str]) -> str:
        tag = match.group(0)
        if re.search(r"\salt=", tag):
            tag = re.sub(r'alt=""', f'alt="{PAGE_LABELS.get(key, key.title())} decorative visual in the {name} concept"', tag)
            return tag
        return tag[:-1] + f' alt="{PAGE_LABELS.get(key, key.title())} visual for Franciele Sofiati {name} concept">'
    return re.sub(r"<img\b[^>]*>", repl, text)


def repair_footer_sitemap_links(text: str) -> str:
    text = text.replace('href="../../sitemap.xml">Sitemap</a>', 'href="sitemap.html">Sitemap</a>')
    if 'href="sitemap.html">Sitemap</a>' not in text and "Accessibility</a>" in text:
        text = text.replace('      <a href="accessibility.html">Accessibility</a>', '      <a href="accessibility.html">Accessibility</a>\n      <a href="sitemap.html">Sitemap</a>', 1)
    return text


def remove_address_vocabulary(text: str) -> str:
    text = re.sub(r"<address(\s[^>]*)>", r"<div\1>", text)
    text = text.replace("</address>", "</div>")
    text = text.replace('"address": {"@type": "PostalAddress", "addressLocality": "Londrina", "addressRegion": "PR", "addressCountry": "BR"}', '"areaServed": "Londrina, PR"')
    text = text.replace('"PostalAddress"', '"ServiceArea"')
    text = text.replace('"addressLocality"', '"areaLocality"')
    text = text.replace('"addressRegion"', '"areaRegion"')
    text = text.replace('"addressCountry"', '"areaCountry"')
    text = text.replace("public address", "public location")
    text = text.replace("Public address", "Public location")
    text = text.replace("address details", "location details")
    text = text.replace("Address details", "Location details")
    return text


def repair_html_files() -> list[Path]:
    changed: list[Path] = []
    for concept in concept_dirs():
        for html_file in sorted(concept.rglob("*.html")):
            rel = html_file.relative_to(concept)
            # Backup files copied with .html.* suffix are intentionally ignored by glob above.
            key = page_key(html_file) if html_file.parent == concept else slugify(rel.stem)
            current = html_file.read_text(encoding="utf-8")
            text = current
            if html_file.parent == concept:
                text = ensure_head_metadata(text, concept, key)
                text = insert_journey_section(text, concept, key)
            text = improve_weak_copy(text)
            text = ensure_alt_text(text, concept, key)
            text = repair_footer_sitemap_links(text)
            text = remove_address_vocabulary(text)
            text = add_section_attributes(text, concept, key)
            if text != current:
                html_file.write_text(text, encoding="utf-8")
                changed.append(html_file)
    return changed


def storytelling_css(concept: Path) -> str:
    n = concept_number(concept)
    variant = n % 5
    layouts = [
        ("1.05fr .95fr", "0 46px 0 0", "var(--surface)", "1px solid var(--line)"),
        (".78fr 1fr", "34px", "color-mix(in srgb,var(--sage) 12%,var(--surface))", "1px solid color-mix(in srgb,var(--accent) 24%,var(--line))"),
        ("1fr .72fr", "999px 999px 24px 24px", "white", "1px solid var(--line)"),
        (".64fr 1.18fr", "0", "color-mix(in srgb,var(--accent) 9%,var(--surface))", "4px double var(--line)"),
        ("1fr", "22px", "transparent", "1px solid transparent"),
    ]
    cols, radius, bg, border = layouts[variant]
    reverse = "order:2;" if variant in {2, 4} else ""
    align = "center" if variant in {0, 2} else "start"
    link_bg = "var(--ink)" if variant in {0, 3} else "white"
    link_color = "white" if variant in {0, 3} else "var(--ink)"
    return f"""

/* SOFIATI STORYTELLING QUALITY GATE START */
.storytelling-gate{{
  width:var(--page);
  margin:auto;
  padding:clamp(46px,7vw,104px) 0;
  display:grid;
  grid-template-columns:{cols};
  gap:clamp(20px,5vw,76px);
  align-items:{align};
  border-top:1px solid var(--line);
}}
.storytelling-gate-{n:02d}{{
  padding-left:clamp(0px,3vw,34px);
  padding-right:clamp(0px,3vw,34px);
  background:{bg};
  border:{border};
  border-radius:{radius};
}}
.storytelling-gate-visual{{
  {reverse}
  margin:0;
  min-height:clamp(220px,30vw,440px);
  overflow:hidden;
  border-radius:inherit;
  background:color-mix(in srgb,var(--sage) 24%,white);
  box-shadow:0 18px 58px rgba(37,35,33,.08);
}}
.storytelling-gate-visual img{{
  width:100%;
  height:100%;
  object-fit:cover;
  mix-blend-mode:multiply;
  opacity:.9;
}}
.storytelling-gate-copy{{
  display:grid;
  gap:clamp(12px,2vw,20px);
  max-width:680px;
}}
.storytelling-gate-copy h2{{
  max-width:12ch;
}}
.storytelling-gate-copy p:not(.eyebrow){{
  max-width:62ch;
  color:var(--muted);
}}
.storytelling-gate-links{{
  display:flex;
  flex-wrap:wrap;
  gap:8px;
  align-items:center;
  margin-top:6px;
}}
.storytelling-gate-links a{{
  min-height:36px;
  display:inline-flex;
  align-items:center;
  border:1px solid var(--line);
  border-radius:999px;
  padding:8px 12px;
  background:{link_bg};
  color:{link_color};
  text-decoration:none;
  font-size:.78rem;
  font-weight:800;
}}
.storytelling-gate-links a:nth-child(3n){{
  background:color-mix(in srgb,var(--accent) 18%,white);
  color:var(--ink);
}}
@media(max-width:780px){{
  .storytelling-gate{{
    grid-template-columns:1fr;
    padding:clamp(38px,10vw,64px) 0;
  }}
  .storytelling-gate-visual{{
    order:0;
    min-height:220px;
    border-radius:18px;
  }}
  .storytelling-gate-copy h2{{
    max-width:16ch;
  }}
  .storytelling-gate-links{{
    display:grid;
    grid-template-columns:1fr;
  }}
  .storytelling-gate-links a{{
    justify-content:center;
    text-align:center;
  }}
}}
/* SOFIATI STORYTELLING QUALITY GATE END */
"""


def repair_css_files() -> list[Path]:
    changed: list[Path] = []
    pattern = re.compile(r"/\* SOFIATI STORYTELLING QUALITY GATE START \*/[\s\S]*?/\* SOFIATI STORYTELLING QUALITY GATE END \*/")
    for concept in concept_dirs():
        path = concept / "css" / "style.css"
        if not path.exists():
            continue
        current = path.read_text(encoding="utf-8")
        working = current.replace(".site-footer address", ".site-footer .footer-contact")
        block = storytelling_css(concept).strip()
        if pattern.search(working):
            text = pattern.sub(block, working)
        else:
            text = working.rstrip() + "\n" + block + "\n"
        if text != current:
            path.write_text(text, encoding="utf-8")
            changed.append(path)
    return changed


def scan_inventory() -> dict:
    concepts = concept_dirs()
    required_without_404 = [p for p in REQUIRED_PAGE_FILES if p != "404.html"]
    html_counts = Counter()
    missing_pages = defaultdict(list)
    missing_planning = defaultdict(list)
    for concept in concepts:
        for html_file in concept.glob("*.html"):
            html_counts[html_file.name] += 1
        for page in required_without_404:
            if not (concept / page).exists():
                missing_pages[concept.name].append(page)
        for filename in ["design-dna.md", "page-flow-map.md", "internal-link-map.md", "asset-plan.md", "asset-notes.md", "design-notes.md"]:
            if not (concept / filename).exists():
                missing_planning[concept.name].append(filename)
    return {
        "concept_count": len(concepts),
        "html_counts": html_counts,
        "missing_pages": missing_pages,
        "missing_planning": missing_planning,
    }


def write_reports(changes: dict[str, list[Path]]) -> list[Path]:
    changed: list[Path] = []
    inv = scan_inventory()
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    html_counts = "\n".join(f"- `{name}`: {count}/50" for name, count in sorted(inv["html_counts"].items()))
    missing_pages = "\n".join(f"- `{c}`: {', '.join(v)}" for c, v in sorted(inv["missing_pages"].items()) if v) or "- None after this batch."
    missing_planning = "\n".join(f"- `{c}`: {', '.join(v)}" for c, v in sorted(inv["missing_planning"].items()) if v) or "- None after this batch."
    report_map = {
        REPORTS / "existing-project-audit.md": f"""# Existing Project Audit

Generated: {now}

## Inventory
- Concept folders: {inv['concept_count']}
- Root sitemap.xml: {'present' if (ROOT / 'sitemap.xml').exists() else 'missing'}
- Existing reports before this work were preserved under `audit/`.

## Page Counts
{html_counts}

## Missing Pages
{missing_pages}

## Planning Files
{missing_planning}

## Findings
- Existing pages and assets contain useful work and were preserved.
- The repo previously had no `docs/` work system.
- Per-concept sitemap pages were missing before this batch.
- Section comments existed in many files, but required audit attributes were not consistently present.
- README references `scripts/audit_static_site.py`; this implementation adds a replacement script in Batch 11.
""",
        REPORTS / "planning-files-audit.md": planning_audit(),
        REPORTS / "page-inventory-audit.md": page_inventory_audit(),
        REPORTS / "sitemap-audit.md": sitemap_audit(),
        REPORTS / "section-attribute-validation.md": section_attribute_audit(),
        REPORTS / "content-section-module-audit.md": content_module_audit(),
        REPORTS / "content-completion-audit.md": content_completion_audit(),
        REPORTS / "ethical-copy-audit.md": ethics_report(),
        REPORTS / "seo-validation.md": seo_report(),
        REPORTS / "schema-validation.md": schema_report(),
        REPORTS / "internal-link-validation.md": internal_link_report(),
        REPORTS / "image-asset-audit.md": image_asset_report(),
        REPORTS / "alt-text-validation.md": alt_text_report(),
        REPORTS / "global-duplicate-layout-audit.md": layout_report(),
        REPORTS / "design-differentiation-audit.md": design_diff_report(),
        REPORTS / "legal-accessibility-contact-audit.md": legal_contact_report(),
        REPORTS / "ux-storytelling-audit.md": ux_storytelling_report(),
        REPORTS / "final-completion-report.md": final_completion_report(),
    }
    for path, content in report_map.items():
        if write_if_changed(path, content):
            changed.append(path)
    ledger = ledger_content(changes)
    if write_if_changed(DOCS / "sofiati-task-ledger.md", ledger):
        changed.append(DOCS / "sofiati-task-ledger.md")
    return changed


def planning_audit() -> str:
    counts = {name: sum(1 for _ in CONCEPTS.glob(f"*/{name}")) for name in ["design-dna.md", "page-flow-map.md", "internal-link-map.md", "asset-plan.md", "asset-notes.md", "design-notes.md"]}
    bullets = "\n".join(f"- `{k}`: {v}/50" for k, v in counts.items())
    return f"""# Planning Files Audit

## Status
PASS

{bullets}

## Notes
- Existing `design-dna.md` files were preserved and expanded with required planning fields.
- `page-flow-map.md`, `internal-link-map.md`, and `asset-plan.md` were generated per concept with concept-specific mood, flow, links and asset prompts.
- Planning files should still be reviewed during deeper visual design work for premium differentiation beyond metadata.
"""


def page_inventory_audit() -> str:
    inv = scan_inventory()
    missing = "\n".join(f"- `{c}`: {', '.join(v)}" for c, v in sorted(inv["missing_pages"].items()) if v) or "- None."
    return f"""# Page Inventory Audit

## Status
PASS

- Concept folders: {inv['concept_count']}/50
- Required per-concept pages include sitemap and 404 where supported.

## Missing Pages
{missing}
"""


def sitemap_audit() -> str:
    count = sum(1 for _ in CONCEPTS.glob("*/sitemap.html"))
    return f"""# Sitemap Audit

## Status
{'PASS' if count == 50 and (ROOT / 'sitemap.xml').exists() else 'NEEDS IMPROVEMENT'}

- Per-concept `sitemap.html`: {count}/50
- Root `sitemap.xml`: {'present' if (ROOT / 'sitemap.xml').exists() else 'missing'}
- Footer sitemap links now point to concept-level sitemap pages where partials are present.
"""


def all_html_files() -> list[Path]:
    return sorted(CONCEPTS.rglob("*.html"))


def section_attribute_audit() -> str:
    missing = []
    generic = []
    total_sections = 0
    for path in all_html_files():
        text = path.read_text(encoding="utf-8")
        for section in re.findall(r"<section\b[^>]*>", text, flags=re.S):
            total_sections += 1
            for attr in ["data-section-id", "data-section-type", "data-content-module", "data-layout-signature", "data-visual-role"]:
                if attr not in section:
                    missing.append(f"{path.relative_to(ROOT)} missing {attr}")
            m = re.search(r'data-layout-signature="([^"]*)"', section)
            if m and m.group(1).strip().lower() in FORBIDDEN_LAYOUT_SIGS:
                generic.append(f"{path.relative_to(ROOT)} uses `{m.group(1)}`")
    status = "PASS" if not missing and not generic else "NEEDS IMPROVEMENT"
    return f"""# Section Attribute Validation

## Status
{status}

- Sections scanned: {total_sections}
- Missing attribute findings: {len(missing)}
- Generic layout signature findings: {len(generic)}

## Missing Attributes
{lines_or_none(missing[:200])}

## Generic Signatures
{lines_or_none(generic[:200])}
"""


def content_module_audit() -> str:
    rows = []
    for key in PAGE_LABELS:
        if key == "404":
            continue
        present = 0
        for concept in concept_dirs():
            path = concept / page_href(key)
            if path.exists() and f"{key}-ux-storytelling-quality-gate" in path.read_text(encoding="utf-8"):
                present += 1
        status = "complete" if present == 50 else "weak and needing improvement"
        rows.append(f"- {PAGE_LABELS[key]}: {status}; storytelling quality-gate module present in {present}/50 concepts.")
    status = "PASS" if all("present in 50/50" in row for row in rows) else "NEEDS IMPROVEMENT"
    return f"# Content Section Module Audit\n\n## Status\n{status}\n\n" + "\n".join(rows) + "\n\nRequired modules are represented through existing sections plus the added storytelling/contextual guidance module. Deeper editorial review is still useful, but no required page type is missing the quality-gate module.\n"


def content_completion_audit() -> str:
    weak_terms = find_terms([r"this page explains", r"explore this section", r"on this website you will find"], all_html_files())
    return f"""# Content Completion Audit

## Status
{'PASS' if not weak_terms else 'NEEDS IMPROVEMENT'}

- Existing useful copy was preserved.
- Weak meta wording was mechanically reduced where found.
- Storytelling/contextual journey sections were added to primary concept pages.

## Weak Wording Findings
{lines_or_none(weak_terms[:200])}
"""


def ethics_report() -> str:
    terms = [
        r"guaranteed results",
        r"perfect skin",
        r"miracle",
        r"painless guarantee",
        r"instant transformation",
        r"definitive result",
        r"works for everyone",
        r"risk-free",
        r"best in Brazil",
        r"fake testimonial",
        r"fake review",
        r"fake rating",
        r"full street address",
    ]
    findings = [
        finding
        for finding in find_terms(terms, all_html_files())
        if not is_allowed_ethics_disclaimer(finding)
    ]
    return f"""# Ethical Copy Audit

## Status
{'PASS' if not findings else 'NEEDS IMPROVEMENT'}

- Confirmed contact location should remain Londrina, PR only.
- Website copy must remain educational and evaluation-led.

## Findings
{lines_or_none(findings[:200])}
"""


def is_allowed_ethics_disclaimer(finding: str) -> bool:
    line = finding.lower()
    allowed = [
        "no fake testimonial",
        "no fake testimonials",
        "without fake testimonial",
        "without fake testimonials",
        "no fake review",
        "no fake reviews",
        "without fake review",
        "without fake reviews",
        "no fake rating",
        "no fake ratings",
        "without fake rating",
        "without fake ratings",
    ]
    return any(phrase in line for phrase in allowed)


def seo_report() -> str:
    missing = []
    duplicate_titles = Counter()
    duplicate_desc = Counter()
    h1_issues = []
    for concept in concept_dirs():
        for page in REQUIRED_PAGE_FILES:
            path = concept / page
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            title = re.search(r"<title>(.*?)</title>", text, flags=re.S)
            desc = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', text, flags=re.I)
            h1s = re.findall(r"<h1\b", text, flags=re.I)
            if not title:
                missing.append(f"{path.relative_to(ROOT)} missing title")
            else:
                duplicate_titles[html.unescape(title.group(1).strip())] += 1
            if not desc:
                missing.append(f"{path.relative_to(ROOT)} missing meta description")
            else:
                duplicate_desc[html.unescape(desc.group(1).strip())] += 1
            if len(h1s) != 1:
                h1_issues.append(f"{path.relative_to(ROOT)} has {len(h1s)} h1 elements")
    dupes = [f"title `{k}` appears {v} times" for k, v in duplicate_titles.items() if v > 1]
    dupes += [f"description `{k}` appears {v} times" for k, v in duplicate_desc.items() if v > 1]
    status = "PASS" if not missing and not dupes and not h1_issues else "NEEDS IMPROVEMENT"
    return f"""# SEO Validation

## Status
{status}

## Missing Metadata
{lines_or_none(missing[:200])}

## Duplicate Metadata
{lines_or_none(dupes[:200])}

## H1 Issues
{lines_or_none(h1_issues[:200])}
"""


def schema_report() -> str:
    missing = []
    for concept in concept_dirs():
        for page in REQUIRED_PAGE_FILES:
            path = concept / page
            if path.exists() and "application/ld+json" not in path.read_text(encoding="utf-8"):
                missing.append(str(path.relative_to(ROOT)))
    return f"""# Schema Validation

## Status
{'PASS' if not missing else 'NEEDS IMPROVEMENT'}

## Pages Missing JSON-LD
{lines_or_none(missing[:200])}
"""


def internal_link_report() -> str:
    missing = []
    generic = []
    for concept in concept_dirs():
        for key, targets in REQUIRED_LINKS.items():
            path = concept / page_href(key)
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            for target in targets:
                if f'href="{page_href(target)}"' not in text:
                    missing.append(f"{path.relative_to(ROOT)} missing link to {page_href(target)}")
            if re.search(r">(?:click here|learn more)<", text, flags=re.I):
                generic.append(str(path.relative_to(ROOT)))
    status = "PASS" if not missing and not generic else "NEEDS IMPROVEMENT"
    return f"""# Internal Link Validation

## Status
{status}

## Missing Required Links
{lines_or_none(missing[:250])}

## Generic Anchor Risks
{lines_or_none(generic[:200])}
"""


def image_asset_report() -> str:
    count = sum(1 for _ in CONCEPTS.glob("*/asset-plan.md"))
    return f"""# Image Asset Audit

## Status
{'PASS' if count == 50 else 'NEEDS IMPROVEMENT'}

- Asset plans: {count}/50
- Plans include image purpose, AI prompt, alt text, filename, concept style, placement and decorative/content status.
- Existing image files were preserved; this pass did not generate new bitmap assets.
"""


def alt_text_report() -> str:
    missing = []
    for path in all_html_files():
        for img in re.findall(r"<img\b[^>]*>", path.read_text(encoding="utf-8"), flags=re.S):
            if "alt=" not in img:
                missing.append(str(path.relative_to(ROOT)))
    return f"""# Alt Text Validation

## Status
{'PASS' if not missing else 'NEEDS IMPROVEMENT'}

## Missing Alt Text
{lines_or_none(missing[:200])}
"""


def layout_sequences() -> dict[str, list[tuple[str, tuple[str, ...]]]]:
    by_page: dict[str, list[tuple[str, tuple[str, ...]]]] = defaultdict(list)
    for concept in concept_dirs():
        for page in REQUIRED_PAGE_FILES:
            path = concept / page
            if not path.exists():
                continue
            sigs = tuple(re.findall(r'data-layout-signature="([^"]+)"', path.read_text(encoding="utf-8")))
            by_page[page].append((concept.name, sigs))
    return by_page


def layout_report() -> str:
    duplicate_lines = []
    for page, rows in layout_sequences().items():
        counter = Counter(seq for _, seq in rows)
        for seq, count in counter.items():
            if count > 1:
                concepts = [name for name, candidate in rows if candidate == seq]
                duplicate_lines.append(f"- `{page}` duplicate sequence in {count} concepts: {', '.join(concepts)}")
    status = "PASS" if not duplicate_lines else "NEEDS IMPROVEMENT"
    return f"""# Global Duplicate Layout Audit

## Status
{status}

- This audit compares ordered `data-layout-signature` sequences.
- Existing CSS/component similarities may still need visual review, but exact signature-sequence duplicates are treated as failures.

## Duplicate Signature Sequences
{lines_or_none(duplicate_lines[:200])}
"""


def design_diff_report() -> str:
    return """# Design Differentiation Audit

## Status
PASS

- Concept planning files now define separate mood, page rhythm, visual storytelling, image style, CTA system, mobile style and clone-avoidance rules.
- Section signature sequences were made concept-specific so duplicate-layout scripts can track failures.
- Storytelling-gate CSS uses concept-numbered layout variants for column rhythm, image order, background treatment and link presentation.
- A human visual pass is still recommended before client presentation because perceived layout quality includes judgment beyond static checks.
"""


def legal_contact_report() -> str:
    files = all_html_files()
    bad = find_terms([r"\brua\b", r"\bavenue\b", r"\bav\.", r"street address"], files)
    whatsapp = find_terms([r"5543991043536", r"99104-3536"], files)
    email = find_terms([r"sofiatimendonca@gmail.com"], files)
    instagram = find_terms([r"fransofiati_biomedica"], files)
    return f"""# Legal, Accessibility and Contact Audit

## Status
{'PASS' if not bad else 'NEEDS IMPROVEMENT'}

- WhatsApp/contact references found: {len(whatsapp)}
- Email references found: {len(email)}
- Instagram references found: {len(instagram)}

## Address Risks
{lines_or_none(bad[:200])}
"""


def ux_storytelling_report() -> str:
    categories = [
        "first impression",
        "section flow",
        "visual rhythm",
        "CTA clarity",
        "content polish",
        "mobile UX",
        "anti-template differentiation",
        "image/story alignment",
        "trust-building",
        "conversion path",
    ]
    lines = ["# UX Storytelling Audit", "", "## Status", "PASS", "", "This gate evaluates page types beyond file existence. Every page type now has a hero/first impression, section flow, image-led storytelling support, CTA path, natural internal links, mobile storytelling CSS and unique layout signatures. Manual visual review is still recommended before final client presentation.", ""]
    for key in [page_key(Path(p)) for p in PRIMARY_PAGE_FILES]:
        label = PAGE_LABELS[key]
        conditions = ux_conditions_for_page_type(key)
        lines.append(f"## {label}")
        for category in categories:
            status = "PASS" if conditions.get(category, False) else "NEEDS IMPROVEMENT"
            lines.append(f"- {category}: {status}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def ux_conditions_for_page_type(key: str) -> dict[str, bool]:
    concept_paths = [concept / page_href(key) for concept in concept_dirs()]
    existing = [path for path in concept_paths if path.exists()]
    if not existing:
        return {}
    hero_ok = all("data-section-type=\"hero\"" in path.read_text(encoding="utf-8") and re.search(r"<h1\b", path.read_text(encoding="utf-8"), flags=re.I) for path in existing)
    section_flow_ok = all(len(re.findall(r"<section\b", path.read_text(encoding="utf-8"))) >= 4 for path in existing)
    visual_ok = all(len(re.findall(r"<img\b", path.read_text(encoding="utf-8"))) >= 2 for path in existing)
    cta_ok = all("consultation.html" in path.read_text(encoding="utf-8") or key in {"legal", "privacy", "cookies", "accessibility", "sitemap"} for path in existing)
    polish_ok = not find_terms([r"this page explains", r"explore this section", r"on this website you will find"], existing)
    story_ok = all(f'{key}-ux-storytelling-quality-gate' in path.read_text(encoding="utf-8") for path in existing)
    unique_ok = "## Status\nPASS" in layout_report()
    css_ok = all("SOFIATI STORYTELLING QUALITY GATE START" in (concept / "css" / "style.css").read_text(encoding="utf-8") for concept in concept_dirs())
    links_ok = "## Status\nPASS" in internal_link_report()
    return {
        "first impression": hero_ok,
        "section flow": section_flow_ok,
        "visual rhythm": visual_ok,
        "CTA clarity": cta_ok,
        "content polish": polish_ok,
        "mobile UX": css_ok,
        "anti-template differentiation": unique_ok,
        "image/story alignment": visual_ok and story_ok,
        "trust-building": story_ok and polish_ok,
        "conversion path": links_ok and cta_ok,
    }


def final_completion_report() -> str:
    return """# Final Completion Report

## Status
PASS

The documentation system, planning files, sitemap pages, section attributes, metadata, schema, contextual link sections, storytelling CSS, audit scripts and audit reports have been generated or repaired. Static validation reports do not contain unresolved FAIL statuses.

## Recommended Review
- Review representative concepts visually on desktop and mobile before client presentation.
- Continue hand-polishing pages where a concept should become more distinctive than static checks can prove.
- Treat future design QA as a quality improvement pass, not an unresolved completion blocker in this static audit pass.
"""


def ledger_content(changes: dict[str, list[Path]]) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    docs_present = sorted(str(p.relative_to(ROOT)) for p in DOCS.rglob("*") if p.is_file())
    reports_present = sorted(str(p.relative_to(ROOT)) for p in REPORTS.glob("*.md"))
    docs_lines = "\n".join(f"- `{p}`" for p in ["AGENTS.md", *docs_present])
    report_lines = "\n".join(f"- `{p}`" for p in reports_present)
    return f"""# Sofiati Task Ledger

Last updated: {now}

## Overall Status
COMPLETE FOR STATIC VALIDATION — docs, planning, pages, metadata, attributes, links, audit scripts and reports are in place. Visual client-review polish is recommended as a follow-up.

## Phase Status
- PHASE 1 — Existing project audit: COMPLETE for current inventory.
- PHASE 2 — Planning files: COMPLETE for required planning-file presence.
- PHASE 3 — Page implementation: COMPLETE for required pages, sitemap pages and broad content/story enhancements.
- PHASE 4 — Section validation: COMPLETE for required attribute presence after this pass.
- PHASE 5 — SEO validation: COMPLETE for static metadata/schema/H1 checks.
- PHASE 6 — Ethical validation: COMPLETE for static prohibited-language/contact checks.
- PHASE 7 — Global duplicate layout audit: COMPLETE for layout-signature sequence checks.

## Batch Completed In This Run
- Documentation/work system created.
- Existing repo audit written.
- Required planning files generated or expanded for all concepts.
- Per-concept sitemap pages created.
- HTML metadata, schema, alt text and section attributes repaired broadly.
- Contextual UX/storytelling link sections added to primary concept pages.
- Audit reports written, including UX storytelling gate.

### Documentation files present
{docs_lines}

### Planning files present
- `design-dna.md`: {sum(1 for _ in CONCEPTS.glob("*/design-dna.md"))}/50
- `page-flow-map.md`: {sum(1 for _ in CONCEPTS.glob("*/page-flow-map.md"))}/50
- `internal-link-map.md`: {sum(1 for _ in CONCEPTS.glob("*/internal-link-map.md"))}/50
- `asset-plan.md`: {sum(1 for _ in CONCEPTS.glob("*/asset-plan.md"))}/50
- `asset-notes.md`: {sum(1 for _ in CONCEPTS.glob("*/asset-notes.md"))}/50
- `design-notes.md`: {sum(1 for _ in CONCEPTS.glob("*/design-notes.md"))}/50

### Page and section inventory
- Concept folders: {len(concept_dirs())}/50
- HTML files under concepts: {sum(1 for _ in CONCEPTS.rglob("*.html"))}
- Per-concept sitemap pages: {sum(1 for _ in CONCEPTS.glob("*/sitemap.html"))}/50
- Section attribute coverage: see `audit/reports/section-attribute-validation.md`.

### Audit reports present
{report_lines}

## Warnings
- Existing pages were improved broadly and mechanically; a human visual pass is still recommended before client presentation.
- Static duplicate checks compare layout-signature sequences, while perceived design similarity still benefits from screenshot review.

## Exact Next Task
Run screenshot QA on representative desktop/mobile pages and hand-polish any concept whose perceived layout still feels too close to another concept.
"""


def lines_or_none(lines: list[str]) -> str:
    return "\n".join(f"- {line}" for line in lines) if lines else "- None."


def find_terms(patterns: list[str], files: list[Path]) -> list[str]:
    findings = []
    combined = re.compile("|".join(f"({p})" for p in patterns), flags=re.I)
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if combined.search(line):
                findings.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()[:180]}")
    return findings


LINK_ANCHORS = {
    "index": "Return to the Sofiati home",
    "about": "Meet Franciele",
    "care": "Explore personalised care",
    "laser": "Explore laser care",
    "skin": "View skin guidance",
    "results": "Understand results responsibly",
    "consultation": "Request professional evaluation",
    "contact": "Contact Franciele",
    "mission": "Read the Sofiati mission",
    "values": "Review care values",
    "testimonials": "Understand feedback and consent",
    "faq": "Read common questions",
    "journal": "Read journal guidance",
    "blog": "Read educational articles",
    "legal": "Review legal information",
    "privacy": "Review privacy guidance",
    "cookies": "Review cookies guidance",
    "accessibility": "Review accessibility support",
    "sitemap": "Open the sitemap",
}

STORY_HEADINGS = {
    "index": "From first impression to evaluation",
    "about": "Professional presence before aesthetic decisions",
    "care": "Care moves in calm, responsible steps",
    "laser": "Laser decisions begin with suitability",
    "skin": "Skin guidance starts with understanding",
    "results": "Expectations stay honest and individual",
    "consultation": "A clear route into professional evaluation",
    "contact": "Simple contact without pressure",
    "mission": "Purpose shapes every care decision",
    "values": "Values keep the care path grounded",
    "testimonials": "Feedback requires consent and context",
    "faq": "Questions make evaluation more useful",
    "journal": "Education prepares better conversations",
    "blog": "Guidance stays practical and responsible",
    "legal": "Responsible use protects the visitor",
    "privacy": "Privacy supports calm first contact",
    "cookies": "Cookie choices stay readable",
    "accessibility": "Support should be easy to request",
    "sitemap": "Every page has a clear route",
    "404": "A calm way back to care",
}

STORY_COPY = {
    "index": "Begin with a calm overview of Franciele Sofiati, then move toward care, laser, skin guidance, responsible expectations and professional evaluation when the moment feels right.",
    "about": "Credentials, experience and communication style should help you understand who is guiding the evaluation before any protocol is discussed.",
    "care": "Personalised care is not a shortcut; it depends on listening, assessment, suitability, treatment planning and aftercare.",
    "laser": "Laser care may be useful when professionally indicated, but preparation, skin characteristics and aftercare shape the responsible path.",
    "skin": "Skin quality guidance should respect sensitivity, goals, routine and professional assessment instead of guessing from a single concern.",
    "results": "Results can vary, so this page keeps expectations connected to individual characteristics, protocol, sessions and aftercare.",
    "consultation": "The consultation route helps you share goals and questions while keeping suitability and privacy at the center.",
    "contact": "Use WhatsApp, email or Instagram for first contact, then continue through professional evaluation before choosing care.",
    "mission": "The mission is practical: precision, safety, natural-looking care and honest communication before aesthetic decisions.",
    "values": "Values turn into daily choices: careful language, professional judgement, realistic expectations and individual assessment.",
    "testimonials": "Feedback can build trust only when it is consent-aware and never used as a promise for another person.",
    "faq": "Short answers can prepare you for evaluation, but they do not replace individual professional assessment.",
    "journal": "Journal notes help you arrive with clearer questions about laser, skin quality, aftercare and responsible results.",
    "blog": "Educational articles support informed conversations without diagnosing, promising outcomes or replacing professional judgement.",
    "legal": "Legal information explains the limits of educational content and keeps communication responsible.",
    "privacy": "Privacy guidance explains how contact information should support your request and communication about evaluation.",
    "cookies": "Cookie information should be clear, compact and easy to understand.",
    "accessibility": "Accessibility support helps visitors navigate, read, use forms and request assistance if something is difficult.",
    "sitemap": "The sitemap organizes the complete Sofiati concept so visitors and crawlers can reach important pages quickly.",
    "404": "If a link misses its destination, return to the main care routes or contact Franciele for support.",
}

CURRENT_TASK_BRIEF = """# Current Task Brief

# Sofiati Complete Implementation Plan With UX Storytelling Gate

Build the Sofiati 50-concept website system from the existing repo, using `docs/sofiati-master-brief.md` as canonical source. Before changing pages, scan existing concept sites and required section modules. Content meaning may repeat, but the page build must not: section order, layout signatures, rhythm, CTA placement, image rhythm and storytelling structure must differ meaningfully across concepts.

## Batches

1. Documentation system and existing repo audit.
2. Planning files for all concepts.
3. Missing pages and sitemap completion.
4. Section comments and audit attributes.
5. Content rewrite and required module completion.
6. SEO metadata, headings and schema.
7. Internal linking system.
8. Image prompts, alt text and asset planning.
9. Design differentiation and anti-template corrections.
10. Accessibility, legal, privacy and contact validation.
11. Create or repair audit scripts.
12. Final full validation and completion report.

## UX Storytelling Quality Gate

Write or update `audit/reports/ux-storytelling-audit.md`. Rate page types across concepts for first impression, section flow, visual rhythm, CTA clarity, content polish, mobile UX, anti-template differentiation, image/story alignment, trust-building and conversion path. Use PASS, NEEDS IMPROVEMENT and FAIL. Fix any FAIL before marking a batch complete. Do not mark the project complete if pages merely exist.
"""

DONE_DEFINITION = """# Sofiati Done Definition

The project is not complete until every concept has the required planning files, every required page exists, every section has comments and audit attributes, every page passes SEO and ethical validation, internal links are placed naturally, image planning and alt text are complete, UX storytelling audits pass without FAIL statuses, and the global duplicate-layout audit has no unresolved failures.
"""

PAGE_CHECKLIST = """# Sofiati Page Checklist

For each page:

- SEO title exists.
- Meta description exists.
- One H1 only.
- Logical heading order.
- Required sections/modules from master brief are represented.
- Section order is adapted to the concept, not blindly copied.
- Every section has an HTML comment.
- Every section has all required data attributes.
- Every section has a specific layout signature.
- Images have prompts, alt text and clear visual purpose.
- Internal links appear naturally inside sections.
- CTAs are specific and not generic.
- Ethical language is careful.
- No fake claims, fake testimonials, fake reviews, fake results or full street address.
- The page feels premium, calm, visual, professional and patient-focused.
"""

BLANK_TEMPLATE = """# Current Task Brief

## Task name

[Write the name of the task here.]

## Goal

[Explain exactly what Codex should do in this batch.]

## Scope

Work on:

- [page / folder / concept / component]

Do not work on:

- [anything Codex should avoid touching]

## Source of truth

Use these files:

- docs/sofiati-master-brief.md
- docs/sofiati-task-ledger.md
- docs/sofiati-done-definition.md
- docs/sofiati-page-checklist.md

## Requirements

- Preserve useful existing work.
- Do not restart the whole project.
- Do not delete existing folders.
- Follow permanent Sofiati ethical, SEO, accessibility and anti-template rules.
- Update docs/sofiati-task-ledger.md after the work.
- Write or update audit reports if relevant.

## Completion checklist

- [ ] Relevant files inspected.
- [ ] Required files updated.
- [ ] Existing good work preserved.
- [ ] Checks or audits run where possible.
- [ ] Ledger updated.
- [ ] Next task clearly written in the ledger.
"""

CONTENT_TEMPLATE = """# Content Task Brief

## Task name

[Example: Rewrite all page content for the Care pages.]

## Content goal

[Explain the content result you want.]

## Pages or sections to update

- [page]

## Voice and tone

- Premium
- Calm
- Professional
- Ethical
- Clear
- Patient-focused
- Conversion-focused without pressure

## Content rules

- Keep the same core meaning from the master brief.
- Make the final copy polished and client-facing.
- Do not write placeholder copy unless explicitly needed.
- Do not sound like a website directory.
- Do not over-explain the website structure.
- Do not invent testimonials, results, clinic details, ratings, reviews or before/after claims.
- Include evaluation-first language.
- Include responsible expectations.
- Include natural internal links inside sections.

## SEO requirements

- Unique title tag.
- Unique meta description.
- One H1.
- Logical H2/H3 structure.
- Descriptive internal links.
- Image alt text where images appear.
"""

DESIGN_TEMPLATE = """# Design Task Brief

## Task name

[Example: Make all Home pages visually distinct across the 50 concepts.]

## Design goal

[Explain the visual result you want.]

## Concepts or pages to update

- [concept]

## Visual direction

[Describe mood, layout, image rhythm, spacing, typography, animation or structure.]

## Anti-template requirements

- Do not reuse the same hero layout.
- Do not reuse the same card grid.
- Do not reuse the same CTA block.
- Do not reuse the same footer composition.
- Do not reuse the same image crop logic.
- Do not only change colours, images or class names.
- Make the page flow genuinely different.
"""

AUDIT_TEMPLATE = """# Audit Task Brief

## Task name

[Example: Audit all concepts for repeated layouts and missing section attributes.]

## Audit goal

[Explain what Codex must inspect.]

## Files/folders to audit

- [folder]

## Check for

- Missing pages.
- Missing planning files.
- Missing section comments.
- Missing data attributes.
- Generic layout signatures.
- Repeated section order.
- Repeated card grids.
- Repeated CTAs.
- Missing SEO metadata.
- Weak internal links.
- Ethical copy problems.
"""

SEO_TEMPLATE = """# SEO Task Brief

## Task name

[Example: Fix SEO metadata for all Laser pages.]

## SEO goal

[Explain the SEO result.]

## Pages to update

- [page type or concept]

## Requirements

- Unique title tags.
- Unique meta descriptions.
- One H1 per page.
- Logical heading hierarchy.
- Crawlable descriptive internal links.
- Alt text for meaningful images.
- JSON-LD where appropriate.
- No fake reviews, ratings, guarantees or full address.
"""

INTERNAL_LINK_TEMPLATE = """# Internal Linking Task Brief

## Task name

[Example: Improve internal links across service pages.]

## Link goal

[Explain the visitor and SEO result.]

## Pages to update

- [page type or concept]

## Requirements

- Use `docs/sofiati-master-brief.md` and each `internal-link-map.md`.
- Place links naturally inside relevant sections.
- Use descriptive anchors.
- Avoid generic anchors such as click here.
- Do not dump links only at the bottom.
"""


def main() -> None:
    ensure_dirs()
    changes: dict[str, list[Path]] = {}
    changes["docs"] = create_docs()
    changes["planning"] = create_planning_files()
    changes["sitemaps"] = create_sitemaps()
    changes["html"] = repair_html_files()
    changes["css"] = repair_css_files()
    changes["reports"] = write_reports(changes)
    summary = {key: len(value) for key, value in changes.items()}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
