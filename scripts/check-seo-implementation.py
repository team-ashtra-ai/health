#!/usr/bin/env python3
"""Validate the complete static SEO implementation and write its audit report."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

from bs4 import BeautifulSoup
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "validation" / "seo.md"
SEO = json.loads((ROOT / "data" / "seo.json").read_text(encoding="utf-8"))
ORIGIN = str(SEO["domain"]).rstrip("/")
INDEX_ROBOTS = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
NOINDEX = {"404.html", "obrigada.html", "en/404.html", "en/thank-you.html"}
JUMP_EXEMPT = {"404.html", "index.html", "en/404.html", "en/index.html"}
FORBIDDEN_SCHEMA_KEYS = {
    "address",
    "openinghours",
    "openinghoursspecification",
    "pricerange",
    "aggregaterating",
    "ratingvalue",
    "review",
    "reviews",
    "award",
    "awards",
}
SOCIAL_PROPERTIES = {
    "og:type",
    "og:site_name",
    "og:locale",
    "og:title",
    "og:description",
    "og:url",
    "og:image",
    "og:image:secure_url",
    "og:image:type",
    "og:image:width",
    "og:image:height",
    "og:image:alt",
}
TWITTER_NAMES = {
    "twitter:card",
    "twitter:title",
    "twitter:description",
    "twitter:image",
    "twitter:image:alt",
}


def public_pages() -> list[Path]:
    page_data = json.loads((ROOT / "data" / "page-pairs.json").read_text(encoding="utf-8"))
    route_names = {
        item[language]
        for item in page_data.get("pages", [])
        if isinstance(item, dict)
        for language in ("en", "pt-BR")
        if isinstance(item.get(language), str)
    }
    pages = [ROOT / route for route in route_names]
    pages.extend(path for path in ROOT.glob("*.html") if "noindex" in path.read_text(encoding="utf-8", errors="ignore").lower())
    pages.extend(path for path in (ROOT / "journal").glob("*.html") if "noindex" in path.read_text(encoding="utf-8", errors="ignore").lower())
    return sorted({path for path in pages if path.exists()}, key=lambda path: path.relative_to(ROOT).as_posix())


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def canonical(relative_path: str) -> str:
    if relative_path == "index.html":
        return f"{ORIGIN}/"
    if relative_path == "en/index.html":
        return f"{ORIGIN}/en/"
    return f"{ORIGIN}/{relative_path}"


def normalize(text: str) -> str:
    return " ".join(text.split())


def type_set(value: Any) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        current = value.get("@type")
        if isinstance(current, list):
            found.update(str(item) for item in current)
        elif current:
            found.add(str(current))
        for child in value.values():
            found.update(type_set(child))
    elif isinstance(value, list):
        for child in value:
            found.update(type_set(child))
    return found


def keyed_values(value: Any, target: str) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key.casefold() == target.casefold():
                found.append(child)
            found.extend(keyed_values(child, target))
    elif isinstance(value, list):
        for child in value:
            found.extend(keyed_values(child, target))
    return found


def local_path_from_url(page: Path, value: str) -> Path | None:
    parsed = urlparse(value)
    if parsed.scheme or parsed.netloc:
        if f"{parsed.scheme}://{parsed.netloc}".rstrip("/") != ORIGIN:
            return None
        route = unquote(parsed.path.lstrip("/"))
        if route in {"", "index.html"}:
            return ROOT / "index.html"
        if route in {"en", "en/"}:
            return ROOT / "en" / "index.html"
        return ROOT / route
    clean = unquote(value.split("#", 1)[0].split("?", 1)[0])
    if not clean:
        return None
    return (ROOT / clean.lstrip("/")) if clean.startswith("/") else (page.parent / clean).resolve()


def expected_schema(relative_path: str) -> set[str]:
    key = relative_path.removeprefix("en/")
    slug_keys = {
        "sobre.html": "about.html",
        "consulta.html": "consultation.html",
        "contato.html": "contact.html",
        "perguntas-frequentes.html": "faq.html",
        "blog.html": "journal.html",
        "missao.html": "mission.html",
        "resultados.html": "results.html",
        "pele.html": "skin.html",
        "depoimentos.html": "testimonials.html",
        "tratamentos.html": "treatments.html",
        "valores.html": "values.html",
    }
    key = slug_keys.get(key, key)
    common = {"WebSite", "Person", "HealthAndBeautyBusiness", "ImageObject", "BreadcrumbList"}
    if relative_path.startswith("journal/") or relative_path.startswith("en/journal/"):
        return common | {"BlogPosting", "WebPage"}
    additions = {
        "about.html": {"AboutPage", "ProfilePage"},
        "consultation.html": {"WebPage", "Service"},
        "contact.html": {"ContactPage"},
        "faq.html": {"FAQPage"},
        "journal.html": {"CollectionPage", "Blog", "ItemList"},
        "laser.html": {"WebPage", "MedicalWebPage", "Service"},
        "mission.html": {"AboutPage"},
        "skin.html": {"WebPage", "MedicalWebPage", "Service"},
        "treatments.html": {"CollectionPage", "ItemList", "Service"},
        "values.html": {"AboutPage"},
    }
    return common | additions.get(key, {"WebPage"})


def schema_label(types: set[str]) -> str:
    page_types = [
        value
        for value in (
            "WebPage",
            "AboutPage",
            "ProfilePage",
            "ContactPage",
            "CollectionPage",
            "Blog",
            "BlogPosting",
            "FAQPage",
            "MedicalWebPage",
            "Service",
            "ItemList",
        )
        if value in types
    ]
    return ", ".join(page_types)


def main() -> int:
    pages = public_pages()
    page_data = json.loads((ROOT / "data" / "page-pairs.json").read_text(encoding="utf-8"))
    page_pairs = [
        item for item in page_data.get("pages", [])
        if isinstance(item, dict) and isinstance(item.get("en"), str) and isinstance(item.get("pt-BR"), str)
    ]
    portuguese_by_english = {item["en"]: item["pt-BR"] for item in page_pairs}
    english_by_portuguese = {item["pt-BR"]: item["en"] for item in page_pairs if not item["en"].startswith("en/journal/")}
    canonical_routes = set(portuguese_by_english) | set(english_by_portuguese)
    errors: list[str] = []
    warnings: list[str] = []
    records: list[dict[str, Any]] = []
    titles: list[str] = []
    descriptions: list[str] = []
    image_count = 0
    decorative_count = 0
    faq_status: list[str] = []

    for path in pages:
        rel = relative(path)
        source = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(source, "html.parser")
        scope = f"[{rel}]"

        if not soup.html:
            errors.append(f"{scope} missing html element")
            continue
        expected_lang = "en" if rel.startswith("en/") else "pt-BR"
        if soup.html.get("lang") != expected_lang:
            errors.append(f"{scope} html lang must be {expected_lang}")
        robot_tags = soup.find_all("meta", attrs={"name": "robots"})
        robot_value = str(robot_tags[0].get("content", "")) if len(robot_tags) == 1 else ""
        is_noindex = "noindex" in robot_value.casefold()
        if is_noindex and rel not in canonical_routes:
            if robot_value != "noindex, follow":
                errors.append(f"{scope} must use noindex, follow")
            canonical_tags = soup.find_all("link", rel=lambda value: value and "canonical" in value)
            if len(canonical_tags) != 1:
                errors.append(f"{scope} must contain one redirect canonical")
            continue
        if len(soup.find_all("main")) != 1:
            errors.append(f"{scope} must contain exactly one main element")
        if len(soup.find_all("h1")) != 1:
            errors.append(f"{scope} must contain exactly one h1")
        ids = [str(tag["id"]) for tag in soup.select("[id]")]
        duplicates = sorted(value for value, count in Counter(ids).items() if count > 1)
        if duplicates:
            errors.append(f"{scope} duplicate IDs: {', '.join(duplicates)}")

        title_tags = soup.find_all("title")
        description_tags = soup.find_all("meta", attrs={"name": "description"})
        title_valid = len(title_tags) == 1 and bool(normalize(title_tags[0].get_text()))
        if not title_valid:
            errors.append(f"{scope} must contain one non-empty title")
            title = ""
        else:
            title = normalize(title_tags[0].get_text())
        if len(description_tags) != 1 or not str(description_tags[0].get("content", "")).strip():
            errors.append(f"{scope} must contain one non-empty meta description")
            description = ""
        else:
            description = str(description_tags[0]["content"]).strip()
        if rel not in NOINDEX:
            titles.append(title.casefold())
            descriptions.append(description.casefold())
            if len(title) > 70:
                warnings.append(f"{scope} title is {len(title)} characters")
            if not 120 <= len(description) <= 170:
                warnings.append(f"{scope} description is {len(description)} characters")

        canonical_tags = soup.find_all("link", rel=lambda value: value and "canonical" in value)
        expected_canonical = canonical(rel)
        if len(canonical_tags) != 1 or canonical_tags[0].get("href") != expected_canonical:
            errors.append(f"{scope} canonical must be {expected_canonical}")
        if rel in NOINDEX:
            if robot_value != "noindex, follow":
                errors.append(f"{scope} must use noindex, follow")
            records.append(
                {
                    "page": rel,
                    "title_length": len(title),
                    "description_length": len(description),
                    "robots": robot_value,
                    "schema": "noindex utility",
                }
            )
            continue
        elif robot_value != INDEX_ROBOTS:
            errors.append(f"{scope} has incomplete index robots directives")

        pair_exists = (rel in portuguese_by_english or rel in english_by_portuguese) and not rel.startswith("en/journal/")
        alternates = {
            str(tag.get("hreflang")): str(tag.get("href"))
            for tag in soup.find_all("link", rel=lambda value: value and "alternate" in value)
            if tag.get("hreflang")
        }
        if pair_exists:
            english_route = english_by_portuguese.get(rel, rel)
            portuguese_route = portuguese_by_english.get(rel, rel)
            expected_alternates = {
                "en": canonical(english_route),
                "pt-BR": canonical(portuguese_route),
                "x-default": canonical(portuguese_route),
            }
        else:
            expected_alternates = {"en": expected_canonical, "x-default": expected_canonical}
        if alternates != expected_alternates:
            errors.append(f"{scope} hreflang set is not reciprocal or points to a missing route")
        for value in alternates.values():
            target = local_path_from_url(path, value)
            if target is not None and not target.is_file():
                errors.append(f"{scope} hreflang target is missing: {value}")

        properties = {
            str(tag.get("property")): str(tag.get("content", ""))
            for tag in soup.find_all("meta", attrs={"property": True})
        }
        names = {
            str(tag.get("name")): str(tag.get("content", ""))
            for tag in soup.find_all("meta", attrs={"name": True})
        }
        missing_social = sorted(SOCIAL_PROPERTIES - properties.keys())
        missing_twitter = sorted(TWITTER_NAMES - names.keys())
        if missing_social or missing_twitter:
            errors.append(
                f"{scope} missing social metadata: {', '.join(missing_social + missing_twitter)}"
            )
        if properties.get("og:url") != expected_canonical:
            errors.append(f"{scope} og:url does not match canonical")
        if properties.get("og:title") != title or names.get("twitter:title") != title:
            errors.append(f"{scope} social titles do not match the document title")
        if properties.get("og:description") != description or names.get("twitter:description") != description:
            errors.append(f"{scope} social descriptions do not match the meta description")
        social_image = properties.get("og:image", "")
        if properties.get("og:image:secure_url") != social_image or names.get("twitter:image") != social_image:
            errors.append(f"{scope} social image URLs are inconsistent")
        social_path = local_path_from_url(path, social_image)
        if social_path is None or not social_path.is_file():
            errors.append(f"{scope} social image is missing: {social_image}")
        else:
            with Image.open(social_path) as image:
                actual_width, actual_height = image.size
            if properties.get("og:image:width") != str(actual_width) or properties.get("og:image:height") != str(actual_height):
                errors.append(f"{scope} social image dimensions are inaccurate")
        if not properties.get("og:image:alt") or not names.get("twitter:image:alt"):
            errors.append(f"{scope} social image alt text is missing")

        jsonld = soup.select("script[type='application/ld+json']")
        if len(jsonld) != 1:
            errors.append(f"{scope} must contain one JSON-LD graph")
            payload: dict[str, Any] = {}
        else:
            try:
                payload = json.loads(jsonld[0].string or jsonld[0].get_text())
            except json.JSONDecodeError as error:
                errors.append(f"{scope} JSON-LD is invalid: {error}")
                payload = {}
        types = type_set(payload)
        missing_types = expected_schema(rel) - types
        if missing_types:
            errors.append(f"{scope} missing expected schema: {', '.join(sorted(missing_types))}")
        schema_ids = {value for value in keyed_values(payload, "@id") if isinstance(value, str)}
        for required_id in (f"{ORIGIN}/#website", f"{ORIGIN}/#franciele", f"{ORIGIN}/#practice"):
            if required_id not in schema_ids:
                errors.append(f"{scope} missing consistent entity ID {required_id}")
        schema_urls = {value for value in keyed_values(payload, "url") if isinstance(value, str)}
        if expected_canonical not in schema_urls:
            errors.append(f"{scope} schema does not identify its canonical page URL")
        forbidden = sorted(
            key
            for key in FORBIDDEN_SCHEMA_KEYS
            if keyed_values(payload, key)
        )
        if forbidden:
            errors.append(f"{scope} contains unconfirmed schema fields: {', '.join(forbidden)}")

        for image in soup.find_all("img"):
            image_count += 1
            if not image.has_attr("alt"):
                errors.append(f"{scope} image lacks an alt attribute: {image.get('src')}")
            elif image.get("alt") == "":
                decorative_count += 1
            if not image.get("width") or not image.get("height"):
                errors.append(f"{scope} image lacks intrinsic dimensions: {image.get('src')}")
            target = local_path_from_url(path, str(image.get("src", "")))
            if target is not None and not target.is_file():
                errors.append(f"{scope} image is missing: {image.get('src')}")

        for hero_image in soup.select(
            "[data-pattern='hero'] .sf-hero-figure img, .sj-masthead img, .sja-hero__feature img"
        ):
            if hero_image.get("loading") == "lazy":
                errors.append(f"{scope} main hero/LCP image must not be lazy-loaded")

        jump_links = soup.select("a.skip-past-hero")
        targets = soup.select("#main-content")
        if rel in JUMP_EXEMPT:
            if jump_links or targets:
                errors.append(f"{scope} homepage/404 must not contain post-hero navigation")
        else:
            if len(jump_links) != 1 or jump_links[0].get("href") != "#main-content":
                errors.append(f"{scope} must contain one post-hero link to #main-content")
            if len(targets) != 1:
                errors.append(f"{scope} must contain one unique #main-content target")
            if source.find('class="skip-past-hero"') > source.find('id="main-content"'):
                errors.append(f"{scope} main-content target occurs before its post-hero link")

        for tag in soup.find_all(["a", "img", "script", "link"]):
            attribute = "href" if tag.name in {"a", "link"} else "src"
            value = tag.get(attribute)
            if not isinstance(value, str) or not value or value.startswith(("#", "mailto:", "tel:", "javascript:", "data:")):
                continue
            if re.search(r"\(\d+\)", value):
                errors.append(f"{scope} upload-suffix URL remains: {value}")
            target = local_path_from_url(path, value)
            if target is not None and not target.exists():
                errors.append(f"{scope} broken internal reference: {value}")

        if rel in {"faq.html", "pt/faq.html"} and payload:
            visible = [
                (
                    details.summary.get_text(" ", strip=True).removesuffix("+").strip(),
                    " ".join(paragraph.get_text(" ", strip=True) for paragraph in details.find_all("p")),
                )
                for details in soup.select("details.sf-accordion-item")
                if details.summary
            ]
            faq_nodes = [
                node
                for node in payload.get("@graph", [])
                if isinstance(node, dict) and "FAQPage" in type_set(node)
            ]
            schema_faq = [
                (
                    item.get("name", ""),
                    item.get("acceptedAnswer", {}).get("text", ""),
                )
                for item in (faq_nodes[0].get("mainEntity", []) if faq_nodes else [])
            ]
            if visible != schema_faq:
                errors.append(f"{scope} visible FAQ and FAQPage schema differ")
            faq_status.append(f"{rel}: {len(visible)} visible answers exactly match schema")

        records.append(
            {
                "page": rel,
                "title_length": len(title),
                "description_length": len(description),
                "robots": robot_value,
                "schema": schema_label(types),
            }
        )

    duplicate_titles = sorted(value for value, count in Counter(titles).items() if count > 1)
    duplicate_descriptions = sorted(value for value, count in Counter(descriptions).items() if count > 1)
    if duplicate_titles:
        errors.append(f"Duplicate indexable titles: {duplicate_titles}")
    if duplicate_descriptions:
        errors.append(f"Duplicate indexable descriptions: {duplicate_descriptions}")

    sitemap = ET.parse(ROOT / "sitemap.xml").getroot()
    sitemap_locations = [
        node.text or ""
        for node in sitemap.iter()
        if node.tag.endswith("loc")
    ]
    indexable_urls = {
        canonical(relative(path))
        for path in pages
        if relative(path) not in NOINDEX
        and "noindex" not in path.read_text(encoding="utf-8", errors="ignore").casefold()
    }
    if set(sitemap_locations) != indexable_urls:
        errors.append("sitemap.xml does not exactly match canonical, indexable routes")
    if any("thank-you" in url or "/404" in url for url in sitemap_locations):
        errors.append("sitemap.xml contains a noindex utility route")

    robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {ORIGIN}/sitemap.xml" not in robots:
        errors.append("robots.txt does not advertise the production sitemap")
    for path in ("/assets/", "/css/site.css", "/js/"):
        if f"Disallow: {path}" in robots:
            errors.append(f"robots.txt blocks render-critical path {path}")

    manifest = json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
    for field in ("id", "name", "short_name", "start_url", "scope", "display", "theme_color", "background_color", "icons"):
        if not manifest.get(field):
            errors.append(f"site.webmanifest is missing {field}")
    for icon in manifest.get("icons", []):
        icon_path = ROOT / str(icon.get("src", ""))
        if not icon_path.is_file():
            errors.append(f"site.webmanifest icon is missing: {icon.get('src')}")
        elif icon.get("sizes"):
            with Image.open(icon_path) as image:
                actual = f"{image.width}x{image.height}"
            if icon["sizes"] != actual:
                errors.append(f"site.webmanifest icon size is inaccurate: {icon.get('src')}")

    placeholders = [
        "GOOGLE_SITE_VERIFICATION_REPLACE_ME"
    ] if "GOOGLE_SITE_VERIFICATION_REPLACE_ME" in (ROOT / "index.html").read_text(encoding="utf-8") else []
    status = "PASS" if not errors else "FAIL"
    lines = [
        "# SEO Validation Report",
        "",
        f"**Status:** {status}",
        "",
        "## Coverage",
        "",
        f"- Public HTML pages parsed: {len(pages)}",
        f"- Canonical, indexable URLs in sitemap: {len(sitemap_locations)}",
        f"- Images audited: {image_count}",
        f"- Decorative images with empty alt text: {decorative_count}",
        f"- Post-hero navigation targets: {len(pages) - len(JUMP_EXEMPT)}",
        "",
        "## Validation summary",
        "",
        f"- Metadata: {'passed' if not any('title' in item.lower() or 'description' in item.lower() for item in errors) else 'failed'}",
        f"- Canonicals and hreflang: {'passed' if not any('canonical' in item.lower() or 'hreflang' in item.lower() for item in errors) else 'failed'}",
        f"- Structured data: {'passed' if not any('schema' in item.lower() or 'json-ld' in item.lower() for item in errors) else 'failed'}",
        f"- Sitemap and robots: {'passed' if not any('sitemap' in item.lower() or 'robots' in item.lower() for item in errors) else 'failed'}",
        f"- Image alt text and dimensions: {'passed' if not any('image' in item.lower() for item in errors) else 'failed'}",
        f"- Broken internal links and targets: {'passed' if not any('broken' in item.lower() or 'target' in item.lower() for item in errors) else 'failed'}",
        f"- FAQ parity: {'; '.join(faq_status)}",
        "",
        "## Page metadata and schema",
        "",
        "| Page | Title | Description | Robots | Page-specific schema |",
        "| --- | ---: | ---: | --- | --- |",
    ]
    lines.extend(
        f"| `{item['page']}` | {item['title_length']} chars | {item['description_length']} chars | "
        f"`{item['robots']}` | {item['schema']} |"
        for item in records
    )
    lines.extend(
        [
            "",
            "## Remaining placeholders",
            "",
            *(
                ["- `GOOGLE_SITE_VERIFICATION_REPLACE_ME` on the English homepage, intentionally retained for HTML-tag verification."]
                if placeholders
                else ["- None."]
            ),
            "",
            "## Client confirmation still required",
            "",
            "- Exact street address, opening hours and prices remain omitted because they are not confirmed in repository data.",
            "- No ratings, review totals or awards are represented in structured data.",
            "- Confirm a real Google Search Console token only if HTML-tag verification is chosen; DNS Domain verification needs no token.",
            "",
            "## Deployment actions",
            "",
            "- Deploy the repository from a clean public artifact so source, QA and backup folders are not published.",
            "- Verify the production domain in Google Search Console, preferably through DNS.",
            "- Submit `https://www.francielesofiati.com/sitemap.xml` after deployment.",
            "- Request indexing for the homepage and principal service pages after the production crawl succeeds.",
            "",
            "## Warnings",
            "",
            *([f"- {item}" for item in warnings] if warnings else ["- None."]),
            "",
            "## Errors",
            "",
            *([f"- {item}" for item in errors] if errors else ["- None."]),
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"SEO implementation validation: {status}; {len(pages)} pages, {len(errors)} errors, {len(warnings)} warnings.")
    print(f"Report: {REPORT}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
