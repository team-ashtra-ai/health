#!/usr/bin/env python3
"""Generate sitemap.xml for the public static pages, including /pt/ alternates."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://www.sofiati.com"
PAGES = [
    "index.html",
    "about.html",
    "accessibility.html",
    "blog.html",
    "care.html",
    "consultation.html",
    "contact.html",
    "cookies.html",
    "faq.html",
    "journal.html",
    "laser.html",
    "legal.html",
    "mission.html",
    "privacy.html",
    "results.html",
    "skin.html",
    "testimonials.html",
    "thank-you.html",
    "values.html",
]


def en_url(page: str) -> str:
    return f"{DOMAIN}/" if page == "index.html" else f"{DOMAIN}/{page}"


def pt_url(page: str) -> str:
    return f"{DOMAIN}/pt/" if page == "index.html" else f"{DOMAIN}/pt/{page}"


def url_entry(location: str, en: str, pt: str) -> str:
    return "\n".join(
        [
            "  <url>",
            f"    <loc>{location}</loc>",
            f'    <xhtml:link rel="alternate" hreflang="en" href="{en}" />',
            f'    <xhtml:link rel="alternate" hreflang="pt-BR" href="{pt}" />',
            f'    <xhtml:link rel="alternate" hreflang="x-default" href="{en}" />',
            "  </url>",
        ]
    )


def main() -> int:
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for page in PAGES:
        lines.append(url_entry(en_url(page), en_url(page), pt_url(page)))
        lines.append(url_entry(pt_url(page), en_url(page), pt_url(page)))
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated sitemap.xml with {len(PAGES) * 2} URLs.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
