#!/usr/bin/env python3
"""Validate local links and asset references in HTML, CSS, JS, and manifest files."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.glob("*.html")) + sorted((ROOT / "partials").glob("*.html"))
TEXT_FILES = [*HTML_FILES, *sorted((ROOT / "css").glob("*.css")), *sorted((ROOT / "js").glob("*.js")), ROOT / "site.webmanifest"]
ATTRS = {"href", "src", "srcset", "content"}
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "sms", "whatsapp"}


class ReferenceParser(HTMLParser):
    def __init__(self, path: Path) -> None:
        super().__init__()
        self.path = path
        self.refs: list[tuple[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name in ATTRS and value:
                if name == "content" and not value.startswith(("assets/", "/assets/", "favicon.ico", "site.webmanifest")):
                    continue
                self.refs.append((name, value))


def is_local(value: str) -> bool:
    parsed = urlparse(value)
    return not parsed.scheme or parsed.scheme not in SKIP_SCHEMES


def candidate_paths(value: str) -> list[str]:
    value = value.split("#", 1)[0].split("?", 1)[0]
    if not value or value.startswith("data:"):
        return []
    if "," in value and " " in value:
        return [part.strip().split()[0] for part in value.split(",")]
    return [value]


def resolve(base: Path, value: str) -> Path:
    if value.startswith("/"):
        return ROOT / value.lstrip("/")
    if ROOT / "partials" in base.parents:
        return (ROOT / value).resolve()
    return (base.parent / value).resolve()


def main() -> int:
    failures: list[str] = []

    for path in HTML_FILES:
        parser = ReferenceParser(path)
        parser.feed(path.read_text(encoding="utf-8"))
        for attr, value in parser.refs:
            for candidate in candidate_paths(value):
                if not is_local(candidate):
                    continue
                target = resolve(path, candidate)
                if not target.exists():
                    failures.append(f"{path.relative_to(ROOT)}: missing {attr} -> {candidate}")

    for path in TEXT_FILES:
        text = path.read_text(encoding="utf-8")
        for match in re.finditer(r"url\\(([^)]+)\\)", text):
            value = match.group(1).strip("\"'")
            if value.startswith("data:"):
                continue
            target = resolve(path, value)
            if not target.exists():
                failures.append(f"{path.relative_to(ROOT)}: missing css url -> {value}")

    if failures:
        print("\n".join(failures), file=sys.stderr)
        return 1

    print("All local links and asset references resolved.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
