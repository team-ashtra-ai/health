#!/usr/bin/env python3
"""Install maintainable analytics hooks across production HTML and partials.

Run after English rendering, Portuguese generation and the SEO normaliser. The
script is idempotent: it adds the three consent-aware scripts once and annotates
real CTAs, contact links, language links, FAQs, sections and sensitive forms
without changing visible copy or layout.
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Callable
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag


ROOT = Path(__file__).resolve().parents[1]
ORIGIN_HOSTS = {"francielesofiati.com", "www.francielesofiati.com"}
DOWNLOAD_EXTENSIONS = {"pdf", "doc", "docx", "xls", "xlsx", "csv", "zip", "rtf", "txt"}
ANALYTICS_BLOCK_RE = re.compile(
    r"\s*<!-- Consent-aware analytics:.*?-->\s*"
    r"(?:<script\b[^>]*\bsrc=[\"'][^\"']*/?analytics-(?:config)?\.js[\"'][^>]*></script>\s*|"
    r"<script\b[^>]*\bsrc=[\"'][^\"']*/?consent-manager\.js[\"'][^>]*></script>\s*|"
    r"<script\b[^>]*\bsrc=[\"'][^\"']*/?analytics\.js[\"'][^>]*></script>\s*)+",
    re.I | re.S,
)


def public_pages() -> list[Path]:
    pages = list(ROOT.glob("*.html"))
    pages.extend((ROOT / "pt").glob("*.html"))
    pages.extend((ROOT / "journal").glob("*.html"))
    return sorted(path for path in pages if path.is_file())


def partials() -> list[Path]:
    return sorted(path for path in (ROOT / "partials").rglob("*.html") if path.is_file())


def clean_text(value: str, maximum: int = 120) -> str:
    return " ".join(value.split())[:maximum].strip()


def link_location(tag: Tag) -> str:
    if tag.get("data-link-location"):
        return str(tag["data-link-location"])
    if tag.find_parent(["footer"]) or tag.find_parent(attrs={"data-loaded-partial": "footer"}):
        return "footer"
    if tag.find_parent(attrs={"data-loaded-partial": "topbar"}):
        return "topbar"
    if tag.find_parent(attrs={"data-loaded-partial": "header"}):
        return "header"
    if tag.find_parent(attrs={"data-loaded-partial": "floating-widgets"}):
        return "floating"
    if tag.find_parent(attrs={"data-pattern": "hero"}) or tag.find_parent(class_=["sj-masthead", "sja-hero"]):
        return "hero"
    if tag.find_parent("form"):
        return "form"
    return "body"


def internal_link(href: str) -> bool:
    parsed = urlsplit(href)
    return (
        not parsed.scheme
        or parsed.scheme in {"", "http", "https"} and parsed.hostname in ORIGIN_HOSTS
    )


def purpose_for_href(href: str) -> str:
    lower = href.lower()
    for needle, purpose in (
        ("consultation", "consultation"),
        ("contact", "contact"),
        ("treatments", "treatments"),
        ("skin", "skin"),
        ("laser", "laser"),
        ("journal", "journal"),
        ("care", "aftercare"),
        ("results", "results"),
    ):
        if needle in lower:
            return purpose
    return "navigation"


def analytics_link_attributes(tag: Tag) -> dict[str, str]:
    href = str(tag.get("href", "")).strip()
    if not href or tag.find_parent(attrs={"data-analytics-ignore": True}):
        return {}
    parsed = urlsplit(href)
    hostname = (parsed.hostname or "").lower()
    location = link_location(tag)

    if href.lower().startswith("mailto:"):
        return {
            "data-track": "contact",
            "data-contact-method": "email",
            "data-link-location": location,
        }
    if href.lower().startswith("tel:"):
        return {
            "data-track": "contact",
            "data-contact-method": "telephone",
            "data-link-location": location,
        }
    if hostname in {"wa.me", "api.whatsapp.com", "www.api.whatsapp.com"}:
        return {
            "data-track": "contact",
            "data-contact-method": "whatsapp",
            "data-link-location": location,
        }
    if hostname == "instagram.com" or hostname.endswith(".instagram.com"):
        return {
            "data-track": "social",
            "data-social-network": "instagram",
            "data-link-location": location,
        }
    if tag.get("data-lang"):
        return {"data-track": "language", "data-link-location": location}

    extension = parsed.path.rsplit(".", 1)[-1].lower() if "." in parsed.path else ""
    if extension in DOWNLOAD_EXTENSIONS:
        return {"data-track": "download", "data-link-location": location}
    if parsed.scheme in {"http", "https"} and hostname not in ORIGIN_HOSTS:
        return {"data-track": "outbound", "data-link-location": location}

    classes = {str(value) for value in tag.get("class", [])}
    button_like = (
        "sf-button" in classes
        or "sffo-button" in classes
        or any("cta" in value.lower() or value.lower().endswith("-button") for value in classes)
    )
    if button_like and internal_link(href):
        return {
            "data-track": "cta",
            "data-cta-location": location,
            "data-cta-purpose": purpose_for_href(href),
            "data-link-location": location,
        }
    return {}


def section_attributes(tag: Tag, index: int) -> dict[str, str]:
    identifier = str(tag.get("id", "")).strip()
    if not identifier or tag.get("data-pattern") == "hero" or identifier.startswith("sf-"):
        return {}
    heading = tag.find(["h2", "h3"])
    name = clean_text(heading.get_text(" ", strip=True) if heading else identifier.replace("-", " "))
    number = str(tag.get("data-section") or index + 1)
    return {
        "data-track-section": "",
        "data-section-name": name,
        "data-section-number": number,
    }


def faq_attributes(tag: Tag, index: int) -> dict[str, str]:
    summary = tag.find("summary")
    if not summary:
        return {}
    return {
        "data-track-faq": "",
        "data-faq-position": str(index + 1),
        "data-faq-question": clean_text(summary.get_text(" ", strip=True), 160),
    }


def form_attributes(tag: Tag) -> dict[str, str]:
    form_id = str(tag.get("id", "")).strip()
    mapping = {
        "contact-form": ("contact_form", "contact", "contact_enquiry"),
        "consultation-request-form": (
            "consultation_request",
            "consultation",
            "consultation_request",
        ),
        "accessibility-feedback-form": (
            "accessibility_feedback",
            "accessibility",
            "",
        ),
    }
    if form_id not in mapping:
        # The service-terms acknowledgement navigates to the consultation page;
        # it is not a backend lead form and is intentionally excluded.
        if form_id == "service-agreement-acknowledgement":
            return {
                "data-analytics-ignore": "",
                "data-analytics-sensitive": "",
                "data-gtm-form-interact": "false",
                "data-gtm-form-submit": "false",
            }
        return {}
    name, form_type, lead_type = mapping[form_id]
    attributes = {
        "data-analytics-form": name,
        "data-form-type": form_type,
        "data-analytics-method": "formspree",
        "data-analytics-sensitive": "",
        "data-gtm-form-interact": "false",
        "data-gtm-form-submit": "false",
    }
    if lead_type:
        attributes["data-lead-type"] = lead_type
    return attributes


def field_attributes(tag: Tag, _: int) -> dict[str, str]:
    form = tag.find_parent("form")
    if not form:
        return {}
    form_id = str(form.get("id", ""))
    if form_id == "service-agreement-acknowledgement":
        return {
            "data-analytics-sensitive": "",
            "data-analytics-ignore": "",
        }
    if form_id not in {
        "contact-form",
        "consultation-request-form",
        "accessibility-feedback-form",
    }:
        return {}
    attributes = {"data-analytics-sensitive": ""}
    if tag.get("type") == "hidden" or "sf-honeypot" in tag.get("class", []):
        attributes["data-analytics-ignore"] = ""
    return attributes


def consent_attributes(tag: Tag, _: int) -> dict[str, str]:
    if tag.name == "input":
        category = {
            "preferences": "preferences",
            "analytics": "analytics",
            "external_media": "external-media",
        }.get(str(tag.get("name", "")))
        return {"data-consent-category": category} if category else {}
    selectors = (
        ("data-cookie-accept", "accept-all"),
        ("data-cookie-reject", "reject-optional"),
        ("data-cookie-page-accept", "accept-all"),
        ("data-cookie-page-reject", "reject-optional"),
        ("data-cookie-save", "save"),
        ("data-cookie-page-save", "save"),
    )
    for attribute, action in selectors:
        if tag.has_attr(attribute):
            return {"data-consent-action": action}
    return {}


def annotate_tags(
    source: str,
    tag_name: str,
    callback: Callable[[Tag, int], dict[str, str]],
) -> str:
    soup = BeautifulSoup(source, "html.parser")
    parsed_tags = soup.find_all(tag_name)
    pattern = re.compile(rf"<{tag_name}\b[^>]*>", re.I | re.S)
    matches = list(pattern.finditer(source))
    if len(matches) != len(parsed_tags):
        raise RuntimeError(
            f"{tag_name}: source/parser count differs ({len(matches)} != {len(parsed_tags)})"
        )
    replacements: list[tuple[int, int, str]] = []
    for index, (match, parsed_tag) in enumerate(zip(matches, parsed_tags)):
        attributes = callback(parsed_tag, index)
        if not attributes:
            continue
        fragment = BeautifulSoup(match.group(0), "html.parser").find(tag_name)
        if not fragment:
            raise RuntimeError(f"Could not parse opening {tag_name} tag")
        for key, value in attributes.items():
            fragment[key] = value
        rendered_attributes: list[str] = []
        for key, value in fragment.attrs.items():
            if isinstance(value, list):
                value = " ".join(str(item) for item in value)
            escaped = html_escape(str(value), quote=True)
            rendered_attributes.append(f'{key}="{escaped}"')
        # HTML void elements use the HTML form rather than an XML-style slash;
        # this keeps the repository's translation DOM paths stable.
        suffix = ">"
        opening = f"<{tag_name}"
        if rendered_attributes:
            opening += " " + " ".join(rendered_attributes)
        opening += suffix
        replacements.append((match.start(), match.end(), opening))
    for start, end, replacement in reversed(replacements):
        source = source[:start] + replacement + source[end:]
    return source


def html_escape(value: str, quote: bool = True) -> str:
    value = value.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    if quote:
        value = value.replace('"', "&quot;")
    return value


def repair_isolated_tag_serialization(source: str) -> str:
    """Remove closures emitted by the first installer draft for opening tags."""
    markers = {
        "a": r"data-track=",
        "section": r"data-track-section=",
        "details": r"data-track-faq=",
        "form": r"data-analytics-form=",
        "select": r"data-analytics-sensitive=",
        "button": r"data-consent-action=",
    }
    for tag_name, marker in markers.items():
        source = re.sub(
            rf"(<{tag_name}\b(?=[^>]*{marker})[^>]*>)</{tag_name}>",
            r"\1",
            source,
            flags=re.I,
        )
    return source


def add_script_block(path: Path, source: str) -> str:
    source = ANALYTICS_BLOCK_RE.sub("\n", source)
    js_prefix = Path(os.path.relpath(ROOT / "js", path.parent)).as_posix()
    block = (
        "\n  <!-- Consent-aware analytics: GA4 is delivered through GTM only. "
        "GTM waits for analytics permission; do not add another gtag.js install. -->\n"
        f'  <script src="{js_prefix}/analytics-config.js" defer></script>\n'
        f'  <script src="{js_prefix}/consent-manager.js" defer></script>\n'
        f'  <script src="{js_prefix}/analytics.js" defer></script>\n'
    )
    main = re.search(
        r"<script\b(?=[^>]*\bsrc=[\"'][^\"']*js/main\.js[\"'])[^>]*></script>",
        source,
        re.I,
    )
    if main:
        return source[: main.start()] + block + source[main.start() :]
    close = re.search(r"</body\s*>", source, re.I)
    if not close:
        raise RuntimeError(f"{path.relative_to(ROOT)}: no body closing tag")
    return source[: close.start()] + block + source[close.start() :]


def process_page(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    source = repair_isolated_tag_serialization(original)
    source = add_script_block(path, source)
    source = annotate_tags(source, "a", lambda tag, _: analytics_link_attributes(tag))
    source = annotate_tags(source, "section", section_attributes)
    source = annotate_tags(source, "details", faq_attributes)
    source = annotate_tags(source, "form", lambda tag, _: form_attributes(tag))
    for tag_name in ("input", "select", "textarea"):
        source = annotate_tags(source, tag_name, field_attributes)
    for tag_name in ("input", "button"):
        source = annotate_tags(source, tag_name, consent_attributes)
    if source == original:
        return False
    path.write_text(source, encoding="utf-8")
    return True


def process_partial(path: Path) -> bool:
    original = path.read_text(encoding="utf-8")
    source = repair_isolated_tag_serialization(original)
    source = annotate_tags(source, "a", lambda tag, _: analytics_link_attributes(tag))
    for tag_name in ("input", "button"):
        source = annotate_tags(source, tag_name, consent_attributes)
    if source == original:
        return False
    path.write_text(source, encoding="utf-8")
    return True


def main() -> int:
    changed: list[str] = []
    for path in public_pages():
        if process_page(path):
            changed.append(path.relative_to(ROOT).as_posix())
    for path in partials():
        if process_partial(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(
        f"Analytics installer checked {len(public_pages())} pages and "
        f"{len(partials())} partials; updated {len(changed)} files."
    )
    for relative in changed:
        print(f"  {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
