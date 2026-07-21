#!/usr/bin/env python3
"""Generate the canonical, localized XML sitemap from authoritative site data."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
SEO_DATA = ROOT / "data" / "seo.json"
PAGE_PAIRS = ROOT / "data" / "page-pairs.json"
SITEMAP = ROOT / "sitemap.xml"
SITEMAP_NAMESPACE = "http://www.sitemaps.org/schemas/sitemap/0.9"
XHTML_NAMESPACE = "http://www.w3.org/1999/xhtml"


@dataclass(frozen=True)
class SitemapPage:
    """One canonical URL and the language alternates that describe it."""

    source: Path
    location: str
    alternates: tuple[tuple[str, str], ...]


class MetadataParser(HTMLParser):
    """Collect only the metadata needed to decide sitemap eligibility."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.canonicals: list[str] = []
        self.robots: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name.casefold(): value or "" for name, value in attrs}
        if tag.casefold() == "link" and "canonical" in attributes.get("rel", "").casefold().split():
            self.canonicals.append(attributes.get("href", ""))
        if tag.casefold() == "meta" and attributes.get("name", "").casefold() == "robots":
            self.robots.append(attributes.get("content", ""))


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read {path.relative_to(ROOT)}: {error}") from error
    if not isinstance(value, dict):
        raise RuntimeError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def site_origin() -> str:
    origin = str(load_json(SEO_DATA).get("domain") or "").rstrip("/")
    if not origin.startswith("https://"):
        raise RuntimeError("data/seo.json domain must be an absolute HTTPS origin")
    return origin


def public_url(origin: str, relative_path: str) -> str:
    normalized = relative_path.lstrip("/")
    if normalized == "index.html":
        return f"{origin}/"
    if normalized in {"pt/index.html", "en/index.html"}:
        return f"{origin}/{normalized.split('/', 1)[0]}/"
    return f"{origin}/{normalized}"


def metadata(relative_path: str, expected_canonical: str) -> MetadataParser:
    path = ROOT / relative_path
    if not path.is_file():
        raise RuntimeError(f"Public route is missing: {relative_path}")
    parser = MetadataParser()
    try:
        parser.feed(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError) as error:
        raise RuntimeError(f"Could not read {relative_path}: {error}") from error
    if parser.canonicals != [expected_canonical]:
        raise RuntimeError(
            f"{relative_path} must declare exactly one canonical URL, {expected_canonical!r}; "
            f"found {parser.canonicals!r}"
        )
    return parser


def is_indexable(page_metadata: MetadataParser) -> bool:
    directives = {
        directive.strip().casefold()
        for content in page_metadata.robots
        for directive in content.split(",")
        if directive.strip()
    }
    return "noindex" not in directives


def source_last_modified(path: Path) -> str:
    """Return an accurate content date, preferring Git history for clean files."""

    relative = path.relative_to(ROOT).as_posix()
    try:
        dirty = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", relative],
            cwd=ROOT,
            check=False,
            capture_output=True,
            timeout=10,
        )
        if dirty.returncode == 0:
            committed = subprocess.run(
                ["git", "log", "-1", "--format=%cs", "--", relative],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
                timeout=10,
            )
            value = committed.stdout.strip()
            if committed.returncode == 0 and value:
                datetime.strptime(value, "%Y-%m-%d")
                return value
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).date().isoformat()


def sitemap_pages(origin: str) -> list[SitemapPage]:
    page_data = load_json(PAGE_PAIRS)
    default_language = str(page_data.get("defaultLanguage") or "en")
    raw_pages = page_data.get("pages")
    if not isinstance(raw_pages, list):
        raise RuntimeError("data/page-pairs.json must contain a pages array")

    pages: list[SitemapPage] = []
    for item in raw_pages:
        if not isinstance(item, dict):
            raise RuntimeError("Every data/page-pairs.json page entry must be an object")
        english_path = str(item.get("en") or "")
        portuguese_path = str(item.get("pt-BR") or "")
        if not english_path or not portuguese_path:
            raise RuntimeError(f"Page pair is missing an English or Portuguese route: {item!r}")

        english_url = public_url(origin, english_path)
        english_metadata = metadata(english_path, english_url)

        # Individual Journal articles currently have no one-to-one Portuguese
        # translation. The shared Portuguese Blog hub is not an alternate.
        if english_path.startswith("journal/") or english_path.startswith("en/journal/"):
            if is_indexable(english_metadata):
                alternates = (("en", english_url), ("x-default", english_url))
                pages.append(SitemapPage(ROOT / english_path, english_url, alternates))
            continue

        portuguese_url = public_url(origin, portuguese_path)
        portuguese_metadata = metadata(portuguese_path, portuguese_url)
        english_indexable = is_indexable(english_metadata)
        portuguese_indexable = is_indexable(portuguese_metadata)
        if english_indexable != portuguese_indexable:
            raise RuntimeError(
                f"Language pair has inconsistent indexability: {english_path} and {portuguese_path}"
            )
        if not english_indexable:
            continue

        default_url = portuguese_url if default_language == "pt-BR" else english_url
        alternates = (
            ("en", english_url),
            ("pt-BR", portuguese_url),
            ("x-default", default_url),
        )
        pages.append(SitemapPage(ROOT / english_path, english_url, alternates))
        pages.append(SitemapPage(ROOT / portuguese_path, portuguese_url, alternates))

    locations = [page.location for page in pages]
    duplicates = sorted({location for location in locations if locations.count(location) > 1})
    if duplicates:
        raise RuntimeError(f"Duplicate canonical sitemap URLs: {duplicates}")
    return pages


def url_block(page: SitemapPage) -> str:
    lines = [
        "  <url>",
        f"    <loc>{escape(page.location)}</loc>",
        f"    <lastmod>{source_last_modified(page.source)}</lastmod>",
    ]
    lines.extend(
        f'    <xhtml:link rel="alternate" hreflang="{escape(language)}" href="{escape(url)}" />'
        for language, url in page.alternates
    )
    lines.append("  </url>")
    return "\n".join(lines)


def render_sitemap() -> str:
    pages = sitemap_pages(site_origin())
    body = "\n\n".join(url_block(page) for page in pages)
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        "<urlset\n"
        f'  xmlns="{SITEMAP_NAMESPACE}"\n'
        f'  xmlns:xhtml="{XHTML_NAMESPACE}">\n'
        f"{body}\n"
        "</urlset>\n"
    )


def main() -> int:
    rendered = render_sitemap()
    SITEMAP.write_text(rendered, encoding="utf-8")
    count = rendered.count("  <url>")
    print(f"Generated sitemap.xml with {count} canonical, indexable URLs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
