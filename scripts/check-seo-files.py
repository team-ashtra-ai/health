#!/usr/bin/env python3
"""Validate generated discovery files and the curated llms.txt index."""

from __future__ import annotations

from datetime import date
import importlib.util
import json
from pathlib import Path
import re
import sys
from types import ModuleType
from urllib.parse import urlparse
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
SITEMAP = ROOT / "sitemap.xml"
ROBOTS = ROOT / "robots.txt"
LLMS = ROOT / "llms.txt"
MARKDOWN_LINK_RE = re.compile(r"^- \[([^\]]+)\]\((https://[^)]+)\)(?:: .+)?$", re.MULTILINE)
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def load_script(name: str, filename: str) -> ModuleType:
    path = ROOT / "scripts" / filename
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {path.relative_to(ROOT)}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        raise RuntimeError(f"Could not read {path.relative_to(ROOT)}: {error}") from error


def validate_generated_files() -> tuple[int, int]:
    sitemap_generator = load_script("sofiati_generate_sitemap", "generate-sitemap.py")
    robots_generator = load_script("sofiati_generate_robots", "generate-robots.py")

    actual_sitemap = read_text(SITEMAP)
    expected_sitemap = sitemap_generator.render_sitemap()
    if actual_sitemap != expected_sitemap:
        raise RuntimeError("sitemap.xml is stale; run python3 scripts/generate-sitemap.py")

    actual_robots = read_text(ROBOTS)
    expected_robots = robots_generator.render_robots()
    if actual_robots != expected_robots:
        raise RuntimeError("robots.txt is stale; run python3 scripts/generate-robots.py")

    try:
        root = ET.fromstring(actual_sitemap)
    except ET.ParseError as error:
        raise RuntimeError(f"sitemap.xml is not valid XML: {error}") from error
    urls = [node for node in root if node.tag.rsplit("}", 1)[-1] == "url"]
    locations: list[str] = []
    for node in urls:
        location_nodes = [child for child in node if child.tag.rsplit("}", 1)[-1] == "loc"]
        modified_nodes = [child for child in node if child.tag.rsplit("}", 1)[-1] == "lastmod"]
        if len(location_nodes) != 1 or not (location_nodes[0].text or "").strip():
            raise RuntimeError("Every sitemap URL must contain exactly one non-empty loc")
        if len(modified_nodes) != 1:
            raise RuntimeError("Every sitemap URL must contain exactly one lastmod")
        try:
            modified = date.fromisoformat((modified_nodes[0].text or "").strip())
        except ValueError as error:
            raise RuntimeError("Every sitemap lastmod must use YYYY-MM-DD") from error
        if modified > date.today():
            raise RuntimeError(f"Sitemap lastmod is in the future: {modified.isoformat()}")
        locations.append((location_nodes[0].text or "").strip())
    if len(locations) != len(set(locations)):
        raise RuntimeError("sitemap.xml contains duplicate loc values")

    if "User-agent: *" not in actual_robots or "Allow: /" not in actual_robots:
        raise RuntimeError("robots.txt must allow public crawling for the universal user agent")
    if re.search(r"(?im)^\s*Disallow\s*:\s*/\s*$", actual_robots):
        raise RuntimeError("robots.txt must not block the entire site")
    if re.search(r"(?im)^\s*Crawl-delay\s*:", actual_robots):
        raise RuntimeError("robots.txt must not use the non-portable Crawl-delay directive")
    disallowed_paths = {
        line.split(":", 1)[1].strip()
        for line in actual_robots.splitlines()
        if line.casefold().startswith("disallow:")
    }
    for runtime_path in ("/assets/", "/css/", "/data/", "/js/", "/partials/"):
        if runtime_path in disallowed_paths:
            raise RuntimeError(f"robots.txt blocks a required render path: {runtime_path}")
    return len(urls), len(robots_generator.NON_PUBLIC_PATHS)


def local_file_for_url(url: str, origin: str) -> Path:
    parsed = urlparse(url)
    expected = urlparse(origin)
    if parsed.scheme != "https" or parsed.netloc != expected.netloc:
        raise RuntimeError(f"llms.txt link must use the canonical HTTPS origin: {url}")
    if parsed.query or parsed.fragment:
        raise RuntimeError(f"llms.txt links must be clean canonical URLs: {url}")
    path = parsed.path
    if path == "/":
        return ROOT / "index.html"
    if path.endswith("/"):
        return ROOT / path.lstrip("/") / "index.html"
    return ROOT / path.lstrip("/")


def validate_llms() -> int:
    try:
        seo = json.loads((ROOT / "data" / "seo.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read data/seo.json: {error}") from error
    origin = str(seo.get("domain") or "").rstrip("/")
    text = read_text(LLMS)
    if text.startswith("\ufeff"):
        raise RuntimeError("llms.txt should be UTF-8 without a byte-order mark")
    if not text.endswith("\n"):
        raise RuntimeError("llms.txt must end with a newline")

    headings = HEADING_RE.findall(text)
    if not headings or headings[0] != ("#", "Franciele Sofiati · Biomedical Practitioner · Aesthetician · Cosmetologist"):
        raise RuntimeError("llms.txt must begin with the canonical site name as its H1")
    if sum(1 for level, _ in headings if level == "#") != 1:
        raise RuntimeError("llms.txt must contain exactly one H1")
    if any(level not in {"#", "##"} for level, _ in headings):
        raise RuntimeError("llms.txt file-list sections must use H2 headings")
    if "## Optional" not in text:
        raise RuntimeError("llms.txt must retain the specification's Optional section")

    lines = text.splitlines()
    if len(lines) < 3 or not lines[2].startswith("> "):
        raise RuntimeError("llms.txt must place a summary blockquote directly after its H1")

    links = MARKDOWN_LINK_RE.findall(text)
    urls = [url for _, url in links]
    if len(urls) < 25:
        raise RuntimeError("llms.txt is missing the expected curated site coverage")
    if len(urls) != len(set(urls)):
        raise RuntimeError("llms.txt contains duplicate links")
    for url in urls:
        local_path = local_file_for_url(url, origin)
        if not local_path.is_file():
            raise RuntimeError(f"llms.txt links to a missing local publication file: {url}")

    required = {
        f"{origin}/",
        f"{origin}/about.html",
        f"{origin}/consultation.html",
        f"{origin}/contact.html",
        f"{origin}/treatments.html",
        f"{origin}/journal.html",
        f"{origin}/pt/",
        f"{origin}/legal.html",
        f"{origin}/privacy.html",
        f"{origin}/sitemap.xml",
        f"{origin}/robots.txt",
    }
    missing = sorted(required - set(urls))
    if missing:
        raise RuntimeError(f"llms.txt is missing required canonical links: {missing}")

    sections = re.split(r"(?m)^## .+\n", text)[1:]
    for section in sections:
        content_lines = [line for line in section.splitlines() if line.strip()]
        if not content_lines or any(not MARKDOWN_LINK_RE.fullmatch(line) for line in content_lines):
            raise RuntimeError("Every llms.txt H2 section must contain only Markdown file-list entries")
    return len(urls)


def main() -> int:
    sitemap_urls, excluded_paths = validate_generated_files()
    llms_links = validate_llms()
    print(
        "SEO discovery checks passed: "
        f"{sitemap_urls} sitemap URLs, {excluded_paths} robots exclusions, "
        f"and {llms_links} curated llms.txt links."
    )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as error:
        print(f"SEO discovery check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
