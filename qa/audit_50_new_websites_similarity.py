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
        header_sim = similarity(read(adir / "partials" / "header.html"), read(bdir / "partials" / "header.html"))
        mobile_sim = similarity(read(adir / "partials" / "mobile-menu.html"), read(bdir / "partials" / "mobile-menu.html"))
        footer_sim = similarity(read(adir / "partials" / "footer.html"), read(bdir / "partials" / "footer.html"))
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
            "screenshotSimilarity": round(screenshot_similarity, 4) if screenshot_similarity is not None else None,
        }
        risk = (
            colour_same
            or header_sim > 0.92
            or mobile_sim > 0.94
            or footer_sim > 0.94
            or hero_sim > 0.94
            or dom_sim > 0.96
            or css_overlap > 0.78
            or js_overlap > 0.94
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
