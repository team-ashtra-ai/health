#!/usr/bin/env python3
"""Render the compact concept selector pages from data/concepts.json."""

from __future__ import annotations

import json
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_PATH = ROOT / "data" / "concepts.json"


def title_case(value: str) -> str:
    keep_lower = {"and", "with", "for", "of", "the", "a", "an"}
    words = value.replace("-", " ").split()
    titled = []
    for index, word in enumerate(words):
        lower = word.lower()
        if index and lower in keep_lower:
            titled.append(lower)
        else:
            titled.append(word[:1].upper() + word[1:])
    return " ".join(titled)


def card(concept: dict[str, object]) -> str:
    number = escape(str(concept["number"]))
    name = escape(str(concept["name"]))
    direction = escape(str(concept["layoutDirection"]))
    mood = escape(str(concept["mood"]))
    menu = escape(str(concept["mobileMenuStyle"]))
    href = f"concepts/{number}/home/"
    return (
        f'<a class="selector-card" href="{href}" aria-label="Open concept {number} {name}">'
        f'<span class="selector-number">{number}</span>'
        f'<span class="selector-name" data-no-translate>{name}</span>'
        f'<strong>{direction}</strong>'
        f'<span class="selector-meta">{mood}</span>'
        f'<span class="selector-menu">Mobile: {menu}</span>'
        f'<span class="selector-open">Open concept</span>'
        f"</a>"
    )


def quick_link(concept: dict[str, object]) -> str:
    number = escape(str(concept["number"]))
    name = escape(str(concept["name"]))
    return (
        f'<a href="concepts/{number}/home/" aria-label="Open concept {number} {escape(name)}">'
        f"{number}"
        f"</a>"
    )


def page(canonical: str, concepts: list[dict[str, object]]) -> str:
    cards = "".join(card(concept) for concept in concepts)
    quick = "".join(quick_link(concept) for concept in concepts)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Sofiati Premium Website Concepts</title>
<meta name="description" content="Premium bilingual concept selector for 50 Franciele Sofiati website directions.">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="Sofiati Premium Website Concepts">
<meta property="og:description" content="50 bilingual website concepts for Franciele Sofiati Advanced Aesthetic Biomedicine.">
<meta property="og:image" content="https://www.sofiati.com/assets/og/sofiati-open-graph.webp">
<link rel="icon" href="assets/brand/sofiati-favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="css/tokens.css">
<link rel="stylesheet" href="css/base.css">
<link rel="stylesheet" href="css/typography.css">
<link rel="stylesheet" href="css/components.css">
<link rel="stylesheet" href="css/concept-components.css">
<link rel="stylesheet" href="css/utilities.css">
</head>
<body class="selector-page" data-concept="01" data-page="home">
<a class="skip-link" href="#main">Skip to main content</a>
<div class="partial-slot" data-partial="header"></div>
<div class="partial-slot" data-partial="mobile-menu"></div>
<main id="main">
<section class="selector-hero" aria-labelledby="selector-title">
<div class="selector-hero-inner">
<div class="selector-kicker-row">
<p class="eyebrow">Franciele Sofiati - CRBM 6277 - Londrina, PR</p>
<span>50 concepts</span>
</div>
<div class="selector-hero-grid">
<div>
<h1 id="selector-title">Choose a Sofiati website concept without fighting the page.</h1>
<p class="lede">A compact bilingual dashboard for reviewing every homepage direction, comparing the mood quickly and opening any concept in one click.</p>
<div class="hero-actions mt">
<a class="button primary" href="concepts/01/home/">Open concept 01</a>
<a class="button" href="#all-concepts">View all concepts</a>
</div>
</div>
<aside class="selector-summary" aria-label="Selector summary">
<span><strong>50</strong> homepage concepts</span>
<span><strong>19</strong> pages per concept</span>
<span><strong>PT</strong> default language</span>
</aside>
</div>
<nav class="selector-number-rail" aria-label="Quick concept links">
{quick}
</nav>
</div>
</section>
<section class="selector-board" id="all-concepts" aria-labelledby="all-concepts-title">
<div class="selector-board-head">
<div>
<p class="eyebrow">All website options</p>
<h2 id="all-concepts-title">Every concept, arranged for fast scanning</h2>
</div>
<p>Each tile opens the live homepage for that numbered direction. The compact layout keeps the full set visible without card overflow or leaking text.</p>
</div>
<div class="selector-grid" aria-label="All 50 concepts">
{cards}
</div>
</section>
</main>
<div class="partial-slot" data-partial="footer"></div>
<script src="js/partials.js" defer data-root="./"></script>
<script src="js/translations.js" defer></script>
<script src="js/language-switcher.js" defer></script>
<script src="js/navigation.js" defer></script>
<script src="js/cookies.js" defer></script>
</body>
</html>
"""


def main() -> None:
    concepts = json.loads(CONCEPTS_PATH.read_text(encoding="utf-8"))
    pages = {
        "index.html": "https://www.sofiati.com/",
        "select.html": "https://www.sofiati.com/select.html",
    }
    for filename, canonical in pages.items():
        (ROOT / filename).write_text(page(canonical, concepts), encoding="utf-8")
        print(f"Rendered {filename}")


if __name__ == "__main__":
    main()
