#!/usr/bin/env python3
"""Synchronize non-rendering shared-component placeholders in public pages."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAIR_MANIFEST = ROOT / "data" / "page-pairs.json"
PARTIAL_ROOT = ROOT / "partials"
INTERFACE_COPY = json.loads((ROOT / "data" / "interface-copy.json").read_text(encoding="utf-8"))
PARTIALS = (
    "topbar",
    "header",
    "mobile-menu",
    "footer",
    "cookie-banner",
    "floating-widgets",
)
PARTIAL_FILENAMES = {"topbar": "top-bar"}
LEGACY_BODY_CLASSES = {
    "sofiati-theme",
    "sf-final2",
    "c01-body",
    "c01-site",
    "c01-inspire",
    "sofiati-polished",
    "luminoso-rosa-botanico",
    "sf-page-rebuilt",
}
LEGACY_SECTION_CLASSES = {
    "sf-split-hero",
    "sf-bottom-cta",
}


def load_pairs() -> list[dict[str, str]]:
    payload = json.loads(PAIR_MANIFEST.read_text(encoding="utf-8"))
    pairs = payload.get("pages", [])
    if not pairs or any("en" not in pair or "pt-BR" not in pair for pair in pairs):
        raise SystemExit("data/page-pairs.json has no usable page pairs.")
    return pairs


def partial_path(name: str, language: str) -> Path:
    filename = PARTIAL_FILENAMES.get(name, name) + ".html"
    root = PARTIAL_ROOT / "pt-BR" if language == "pt-BR" else PARTIAL_ROOT
    path = root / filename
    if not path.is_file():
        raise SystemExit(f"Missing localized partial: {path.relative_to(ROOT)}")
    return path


def marker_pattern(name: str) -> re.Pattern[str]:
    return re.compile(
        rf"<!-- SHARED:{re.escape(name)}:START -->.*?<!-- SHARED:{re.escape(name)}:END -->",
        re.DOTALL,
    )


def legacy_slot_pattern(name: str) -> re.Pattern[str]:
    values = [name]
    if name == "topbar":
        values.append("top-bar")
    value_pattern = "|".join(re.escape(value) for value in values)
    return re.compile(
        rf"<div\s+(?=[^>]*(?:data-partial|data-sofiati-partial)=[\"'](?:{value_pattern})[\"'])[^>]*>\s*</div>",
        re.IGNORECASE,
    )


def template_pattern(name: str) -> re.Pattern[str]:
    return re.compile(
        rf"<template\b(?=[^>]*\bdata-sf-partial=[\"']{re.escape(name)}[\"'])[^>]*>\s*</template>",
        re.IGNORECASE,
    )


def normalize_page_markup(content: str) -> str:
    """Remove historical presentation aliases from the rendered page shell."""
    body_pattern = re.compile(r'(<body\b[^>]*\bclass=")([^"]*)(")', re.IGNORECASE)

    def normalize_body(match: re.Match[str]) -> str:
        classes = match.group(2).split()
        retained = [
            value
            for value in classes
            if value not in LEGACY_BODY_CLASSES and not value.startswith("c01-page-")
        ]
        ordered = ["sf-site", "sf-page", *retained]
        unique = list(dict.fromkeys(ordered))
        return f'{match.group(1)}{" ".join(unique)}{match.group(3)}'

    content = body_pattern.sub(normalize_body, content, count=1)
    section_pattern = re.compile(
        r'(<section\b[^>]*\bclass=")([^"]*)("[^>]*\bdata-pattern=")([^"]+)(")',
        re.IGNORECASE,
    )

    def normalize_section(match: re.Match[str]) -> str:
        classes = match.group(2).split()
        retained = [
            value
            for value in classes
            if value not in LEGACY_SECTION_CLASSES
            and not value.startswith("sf-generated-")
            and not value.startswith("sf-section--")
            and not value.startswith("sf-tone--")
            and not value.startswith("sf-composition-")
        ]
        composition = "sf-composition-" + match.group(4).strip().replace("_", "-")
        ordered = ["sf-section", composition, *retained]
        unique = list(dict.fromkeys(ordered))
        return (
            f'{match.group(1)}{" ".join(unique)}{match.group(3)}'
            f'{match.group(4)}{match.group(5)}'
        )

    content = section_pattern.sub(normalize_section, content)

    def remove_generated_aliases(match: re.Match[str]) -> str:
        classes = [
            value for value in match.group(1).split()
            if not value.startswith("sf-generated-")
        ]
        return f'class="{" ".join(classes)}"'

    return re.sub(r'class="([^"]*)"', remove_generated_aliases, content)


def set_data_attributes(tag: str, values: dict[str, str]) -> str:
    updated = tag
    for name, value in values.items():
        updated = re.sub(rf"\s+{re.escape(name)}=(?:\"[^\"]*\"|'[^']*')", "", updated)
        escaped = html.escape(value, quote=True)
        updated = updated[:-1] + f' {name}="{escaped}">'
    return updated


def apply_interface_copy(content: str, language: str) -> str:
    copy = INTERFACE_COPY[language]
    content = re.sub(
        r'<form\b(?=[^>]*\bclass="[^"]*\bsf-form\b[^"]*")[^>]*>',
        lambda match: set_data_attributes(match.group(0), {
            "data-message-required": copy["forms"]["required"],
            "data-message-email": copy["forms"]["email"],
            "data-message-review": copy["forms"]["review"],
        }),
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(
        r'<p\b(?=[^>]*\bdata-treatment-filter-status(?:="")?)[^>]*>',
        lambda match: set_data_attributes(match.group(0), {
            "data-label-singular": copy["treatments"]["singular"],
            "data-label-plural": copy["treatments"]["plural"],
        }),
        content,
        flags=re.IGNORECASE,
    )
    content = re.sub(
        r'<p\b(?=[^>]*\bdata-cookie-page-status(?:="")?)[^>]*>',
        lambda match: set_data_attributes(
            match.group(0), {"data-saved-message": copy["cookies"]["saved"]}
        ),
        content,
        flags=re.IGNORECASE,
    )
    return content


def compile_page(path: Path, language: str) -> tuple[str, bool]:
    content = path.read_text(encoding="utf-8")
    updated = apply_interface_copy(normalize_page_markup(content), language)
    for name in PARTIALS:
        partial_path(name, language)
        placeholder = f'<template data-sf-partial="{name}"></template>'
        pattern = marker_pattern(name)
        marker_count = len(pattern.findall(updated))
        if marker_count > 1:
            raise RuntimeError(f"{path.relative_to(ROOT)} has {marker_count} marked blocks for {name}")
        if marker_count == 1:
            updated = pattern.sub(lambda _match: placeholder, updated, count=1)
            continue
        template = template_pattern(name)
        template_count = len(template.findall(updated))
        if template_count > 1:
            raise RuntimeError(f"{path.relative_to(ROOT)} has {template_count} placeholders for {name}")
        if template_count == 1:
            updated = template.sub(lambda _match: placeholder, updated, count=1)
            continue
        slot = legacy_slot_pattern(name)
        slot_count = len(slot.findall(updated))
        if slot_count != 1:
            raise RuntimeError(
                f"{path.relative_to(ROOT)} must have exactly one placeholder, legacy slot, or marked block for {name}"
            )
        updated = slot.sub(lambda _match: placeholder, updated, count=1)
    # Final calls-to-action now live inside each page's rendered main content.
    # Remove the former shared footer CTA so visitors see only the assigned
    # page-specific concept before the footer.
    transition_pattern = re.compile(
        r"<!-- SHARED:footer-transition:START -->.*?<!-- SHARED:footer-transition:END -->",
        re.DOTALL,
    )
    updated = transition_pattern.sub("", updated)
    return updated, updated != content


def atomic_write(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if public pages have stale partial placeholders.")
    args = parser.parse_args()
    pairs = load_pairs()
    changed: list[str] = []
    failures: list[str] = []

    total = len(pairs) * 2
    current = 0
    for pair in pairs:
        for language in ("en", "pt-BR"):
            current += 1
            relative = pair[language]
            path = ROOT / relative
            try:
                output, is_changed = compile_page(path, language)
                status = "stale" if is_changed and args.check else "updated" if is_changed else "current"
                print(f"[{current:02}/{total}] {relative}: {status}")
                if is_changed:
                    changed.append(relative)
                    if not args.check:
                        atomic_write(path, output)
            except Exception as error:
                failures.append(f"{relative}: {error}")
                print(f"[{current:02}/{total}] {relative}: ERROR {error}")

    print(f"Partial placeholders: {total} pages checked; {len(changed)} changed; {len(failures)} failures.")
    if failures:
        return 2
    if args.check and changed:
        print("Run python3 scripts/build-shared-chrome.py to refresh partial placeholders.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

