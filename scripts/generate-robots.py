#!/usr/bin/env python3
"""Generate a concise robots.txt for the public static site."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEO_DATA = ROOT / "data" / "seo.json"
ROBOTS = ROOT / "robots.txt"

# These paths are repository sources or QA artifacts, not public site content.
# robots.txt is only crawl guidance; the deployment should still publish from a
# clean allowlisted artifact rather than exposing the repository root.
NON_PUBLIC_PATHS = (
    "/.agents/",
    "/.codex/",
    "/.git/",
    "/__pycache__/",
    "/backups/",
    "/css/src/",
    "/docs/",
    "/node_modules/",
    "/posts/",
    "/qa/",
    "/references/",
    "/reports/",
    "/screenshots/",
    "/scripts/",
    "/tests/",
    "/.gitignore",
    "/.translation-cache.json",
    "/README.md",
    "/requirements-translation.txt",
)


def site_origin() -> str:
    try:
        data = json.loads(SEO_DATA.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Could not read data/seo.json: {error}") from error
    origin = str(data.get("domain") or "").rstrip("/")
    if not origin.startswith("https://"):
        raise RuntimeError("data/seo.json domain must be an absolute HTTPS origin")
    return origin


def render_robots() -> str:
    disallow = "\n".join(f"Disallow: {path}" for path in NON_PUBLIC_PATHS)
    return (
        "# Franciele Sofiati · Biomedical Practitioner · Aesthetician · Cosmetologist\n"
        "# Public pages and the assets required to render them are crawlable.\n"
        "# Excluded paths are repository sources or QA artifacts, not private access controls.\n\n"
        "User-agent: *\n"
        "Allow: /\n"
        f"{disallow}\n\n"
        f"Sitemap: {site_origin()}/sitemap.xml\n"
    )


def main() -> int:
    ROBOTS.write_text(render_robots(), encoding="utf-8")
    print(f"Generated robots.txt with {len(NON_PUBLIC_PATHS)} non-public path exclusions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
