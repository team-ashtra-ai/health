#!/usr/bin/env python3
"""Validate local static asset references in HTML, CSS, and partials."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "node_modules", "screenshots", "references", "reports", "__pycache__"}
SOURCE_GLOBS = ("*.html", "en/*.html", "en/journal/*.html", "css/*.css", "partials/*.html", "partials/pt-BR/*.html")
LOCAL_PREFIXES = ("/assets/", "assets/", "../assets/", "../../assets/", "css/", "../css/", "../../css/", "js/", "../js/", "../../js/")
URL_PATTERN = re.compile(
    r"(?:src|href|content)=[\"']([^\"']+)[\"']|url\((?:[\"'])?([^\"')]+)(?:[\"'])?\)",
    re.I,
)


def source_files() -> list[Path]:
    files: list[Path] = []
    for pattern in SOURCE_GLOBS:
        files.extend(ROOT.glob(pattern))
    return sorted(
        path
        for path in files
        if not any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts)
    )


def local_refs(text: str) -> list[str]:
    refs: list[str] = []
    for match in URL_PATTERN.finditer(text):
        value = match.group(1) or match.group(2) or ""
        if value.startswith(LOCAL_PREFIXES):
            refs.append(value)
    return refs


def resolve(path: Path, value: str) -> Path:
    clean = value.split("#", 1)[0].split("?", 1)[0]
    if clean.startswith("/assets/"):
        return ROOT / clean.removeprefix("/")
    if path.parent.name == "partials" and clean.startswith("assets/"):
        return ROOT / clean
    if path.parent == ROOT / "partials" / "pt-BR" and clean.startswith("../assets/"):
        return ROOT / clean.removeprefix("../")
    if path.parent == ROOT and clean.startswith("../assets/icons/"):
        # Icon masks are assigned through CSS custom properties in HTML, so
        # browsers resolve them relative to the stylesheet that consumes them.
        return ROOT / clean.removeprefix("../")
    return (path.parent / clean).resolve()


def main() -> int:
    missing: list[str] = []
    for path in source_files():
        text = path.read_text(encoding="utf-8", errors="ignore")
        for value in local_refs(text):
            target = resolve(path, value)
            if not target.exists():
                rel = path.relative_to(ROOT).as_posix()
                missing.append(f"{rel}: {value} -> {target.relative_to(ROOT.parent).as_posix()}")

    if missing:
        print("Missing local asset references:", file=sys.stderr)
        print("\n".join(missing), file=sys.stderr)
        return 1

    print("Local asset references passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
