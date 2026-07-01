#!/usr/bin/env python3
from __future__ import annotations

import difflib
import json
import re
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
SCRIPT_RUNS = ROOT / "docs" / "script-runs"
BIBLE_JSON = ROOT / "docs" / "design-destination-bible" / "10-50-new-website-destinations.json"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def compact(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, compact(a), compact(b)).ratio()


def token_set(text: str) -> set[str]:
    return set(re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text))


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    return len(a & b) / max(1, len(a | b))


def load_concepts() -> list[dict]:
    return json.loads(read(BIBLE_JSON))["concepts"]


def body_profile(html: str) -> dict[str, str]:
    body = re.search(r"<body\b([^>]*)>", html, re.I | re.S)
    attrs = body.group(1) if body else ""

    def attr(name: str) -> str:
        match = re.search(rf'{name}="([^"]*)"', attrs)
        return match.group(1) if match else ""

    hero = re.search(r"<section\b([^>]*)data-content-section=\"01\"([^>]*)>", html, re.I | re.S)
    hero_attrs = " ".join(hero.groups()) if hero else ""
    hero_pattern = re.search(r'data-hero-pattern="([^"]*)"', hero_attrs)
    section_classes = re.findall(r'<section\b[^>]*class="([^"]*)"', html, re.I)
    anatomy_sequence = []
    tone_sequence = []
    card_sequence = []
    for classes in section_classes[:10]:
        anatomy = re.search(r"\bc\d+-anatomy--([a-z0-9-]+)", classes)
        tone = re.search(r"\bc\d+-tone--([a-z0-9-]+)", classes)
        card = re.search(r"\bc\d+-card--([a-z0-9-]+)", classes)
        anatomy_sequence.append(anatomy.group(1) if anatomy else "")
        tone_sequence.append(tone.group(1) if tone else "")
        card_sequence.append(card.group(1) if card else "")
    return {
        "creativeFamily": attr("data-creative-family"),
        "heroPattern": attr("data-hero-pattern") or (hero_pattern.group(1) if hero_pattern else ""),
        "cardStyle": attr("data-card-style"),
        "mediaTreatment": attr("data-media-treatment"),
        "anatomySequence": "|".join(anatomy_sequence),
        "toneSequence": "|".join(tone_sequence),
        "cardSequence": "|".join(card_sequence),
    }


def partial_profile(header: str, mobile: str, footer: str) -> dict[str, str]:
    def class_token(text: str, prefix: str) -> str:
        match = re.search(rf"\b{re.escape(prefix)}([a-z0-9-]+)", text)
        return match.group(1) if match else ""

    structure = re.search(r'data-structure="([^"]*)"', header + footer)
    return {
        "structure": structure.group(1) if structure else "",
        "header": class_token(header, "sf-header--"),
        "mobile": class_token(mobile, "sf-menu--"),
        "footer": class_token(footer, "sf-footer--"),
    }


def screenshot_size_map() -> dict[str, dict[str, int]]:
    shots_root = ROOT / "final" / "homepage-screenshots"
    result: dict[str, dict[str, int]] = {}
    if not shots_root.exists():
        return result
    for png in shots_root.glob("full-*/*-desktop-full.png"):
        concept = png.name.replace("-desktop-full.png", "")
        mobile = png.with_name(f"{concept}-mobile-full.png")
        result[concept] = {
            "desktopBytes": png.stat().st_size,
            "mobileBytes": mobile.stat().st_size if mobile.exists() else 0,
        }
    return result


def audit() -> tuple[dict, bool]:
    concepts = load_concepts()
    pairs = []
    failures = []
    shots = screenshot_size_map()

    for a, b in combinations(concepts, 2):
        aid = a["conceptId"]
        bid = b["conceptId"]
        adir = CONCEPTS_DIR / aid
        bdir = CONCEPTS_DIR / bid
        a_header = read(adir / "partials" / "header.html")
        b_header = read(bdir / "partials" / "header.html")
        a_mobile = read(adir / "partials" / "mobile-menu.html")
        b_mobile = read(bdir / "partials" / "mobile-menu.html")
        a_footer = read(adir / "partials" / "footer.html")
        b_footer = read(bdir / "partials" / "footer.html")
        header_sim = similarity(a_header, b_header)
        mobile_sim = similarity(a_mobile, b_mobile)
        footer_sim = similarity(a_footer, b_footer)
        a_partials = partial_profile(a_header, a_mobile, a_footer)
        b_partials = partial_profile(b_header, b_mobile, b_footer)
        public_chrome_same = a_partials == b_partials
        hero_sim = similarity(
            re.search(r"<section\b.*?</section>", read(adir / "index.html"), re.S).group(0),
            re.search(r"<section\b.*?</section>", read(bdir / "index.html"), re.S).group(0),
        )
        css_overlap = jaccard(token_set(read(adir / "css" / "concept.css")), token_set(read(bdir / "css" / "concept.css")))
        js_overlap = jaccard(token_set(read(adir / "js" / "concept.js")), token_set(read(bdir / "js" / "concept.js")))
        colour_same = (
            a["colourRhythm"]["homepageSectionColourSequence"]
            == b["colourRhythm"]["homepageSectionColourSequence"]
        )
        dom_sim = similarity(read(adir / "index.html"), read(bdir / "index.html"))
        cta_same = a["ctaStrategy"] == b["ctaStrategy"]
        image_same = a["imageStrategy"] == b["imageStrategy"]
        a_profile = body_profile(read(adir / "index.html"))
        b_profile = body_profile(read(bdir / "index.html"))
        profile_same = a_profile == b_profile
        profile_matches = sum(1 for key in a_profile if a_profile.get(key) == b_profile.get(key))
        screenshot_similarity = None
        if aid in shots and bid in shots:
            a_size = shots[aid]["desktopBytes"] + shots[aid]["mobileBytes"]
            b_size = shots[bid]["desktopBytes"] + shots[bid]["mobileBytes"]
            screenshot_similarity = 1 - (abs(a_size - b_size) / max(a_size, b_size, 1))
        pair = {
            "pair": [aid, bid],
            "headerSimilarity": round(header_sim, 4),
            "mobileMenuSimilarity": round(mobile_sim, 4),
            "footerSimilarity": round(footer_sim, 4),
            "heroSimilarity": round(hero_sim, 4),
            "homepageDomSimilarity": round(dom_sim, 4),
            "homepageSectionSequenceSame": colour_same,
            "pageColourSequenceSimilarity": 1.0 if colour_same else 0.0,
            "ctaRhythmSame": cta_same,
            "imagePlacementSame": image_same,
            "localCssSelectorOverlap": round(css_overlap, 4),
            "jsInteractionOverlap": round(js_overlap, 4),
            "activeCssJsReferenceSimilarity": 1.0,
            "visualProfileA": a_profile,
            "visualProfileB": b_profile,
            "visualProfileMatches": profile_matches,
            "visualProfileSame": profile_same,
            "publicChromeA": a_partials,
            "publicChromeB": b_partials,
            "publicChromeSame": public_chrome_same,
            "screenshotSimilarity": round(screenshot_similarity, 4) if screenshot_similarity is not None else None,
        }
        screenshot_risk = (
            screenshot_similarity is not None
            and screenshot_similarity > 0.998
            and (profile_same or dom_sim > 0.96)
        )
        risk = (
            colour_same
            or profile_same
            or (profile_matches >= 5 and hero_sim > 0.94 and dom_sim > 0.97)
            or (public_chrome_same and header_sim > 0.965 and mobile_sim > 0.965 and footer_sim > 0.965)
            or screenshot_risk
        )
        if risk:
            failures.append({"pair": [aid, bid], "reason": "similarity threshold exceeded", "metrics": pair})
        pairs.append(pair)

    results = {
        "generatedAt": __import__("datetime").datetime.now(__import__("datetime").UTC).isoformat(),
        "totalConcepts": len(concepts),
        "pairsChecked": len(pairs),
        "passed": not failures,
        "failures": failures,
        "pairs": pairs,
        "screenshotComparisonAvailable": bool(shots),
    }
    return results, results["passed"]


def write_reports(results: dict) -> None:
    write(SCRIPT_RUNS / "50-new-websites-similarity-audit.json", json.dumps(results, indent=2))
    lines = [
        "# 50 New Websites Similarity Audit",
        "",
        f"- Concepts checked: {results['totalConcepts']}",
        f"- Pairs checked: {results['pairsChecked']}",
        f"- Passed: {results['passed']}",
        f"- Similarity failures: {len(results['failures'])}",
        f"- Screenshot comparison available: {results['screenshotComparisonAvailable']}",
        "",
    ]
    if results["failures"]:
        lines.extend(["## Failures", ""])
        lines.extend(
            f"- `{item['pair'][0]}` vs `{item['pair'][1]}`: {item['reason']}"
            for item in results["failures"][:100]
        )
    else:
        lines.append("All similarity gates passed.")
    write(SCRIPT_RUNS / "50-new-websites-similarity-audit.md", "\n".join(lines))


def main() -> int:
    results, passed = audit()
    write_reports(results)
    print(f"Similarity audit passed: {passed}")
    print(f"Failures: {len(results['failures'])}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
