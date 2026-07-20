#!/usr/bin/env python3
"""Apply edits from the editable bilingual Word export without changing HTML structure.

Applies approved edits directly after validation.  The command refuses to write if any source
file differs from the snapshot hash in the companion map, or if a Word row can
not be found exactly.  It performs only source-text/attribute substitutions;
tags, attributes, classes, IDs, CSS and JavaScript are never rewritten.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import sys
import zipfile
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DOCUMENT = ROOT / "exports" / "Franciele_Sofiati_Bilingual_Content_Editable.docx"
DEFAULT_MAP = ROOT / "exports" / "Franciele_Sofiati_Bilingual_Content_Map.json"
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def display(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def offset_for(source: str, line: int, column: int) -> int:
    lines = source.splitlines(keepends=True)
    return sum(len(part) for part in lines[:line - 1]) + column


@dataclass
class Node:
    name: str
    selector: str
    children: dict[str, int] = field(default_factory=dict)
    text_count: int = 0


class SourceLocator(HTMLParser):
    """Find raw source spans for mapped CSS selectors without serialising HTML."""

    def __init__(self, source: str):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.stack: list[Node] = []
        self.tags: dict[str, tuple[int, int]] = {}
        self.text: dict[tuple[str, int], tuple[int, int, str]] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        start = offset_for(self.source, *self.getpos())
        raw = self.get_starttag_text() or ""
        parent = self.stack[-1] if self.stack else None
        index = (parent.children.get(tag, 0) + 1) if parent else 1
        if parent:
            parent.children[tag] = index
        attrs_dict = dict(attrs)
        segment = f"{tag}#{attrs_dict['id']}" if attrs_dict.get("id") else f"{tag}:nth-of-type({index})"
        selector = f"{parent.selector} > {segment}" if parent else segment
        self.tags[selector] = (start, start + len(raw))
        if tag not in VOID:
            self.stack.append(Node(tag, selector))

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if self.stack and self.stack[-1].name == tag:
            self.stack.pop()

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index].name == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if not self.stack:
            return
        start = offset_for(self.source, *self.getpos())
        # Text runs end at the next literal markup delimiter.  Literal '<' in
        # public text is entity-encoded, so it cannot be confused with markup.
        end = self.source.find("<", start)
        if end == -1:
            end = len(self.source)
        current = self.stack[-1]
        self.text[(current.selector, current.text_count)] = (start, end, data)
        for node in self.stack:
            node.text_count += 1


def read_word_rows(document: Path) -> dict[str, str]:
    with zipfile.ZipFile(document) as archive:
        xml = archive.read("word/document.xml")
    root = ET.fromstring(xml)
    edits: dict[str, str] = {}
    for row in root.iter(W + "tr"):
        cells = row.findall(W + "tc")
        if len(cells) != 6:
            continue
        values = ["".join(node.text or "" for node in cell.iter(W + "t")) for cell in cells]
        if re.fullmatch(r"EN-\d{5}", values[0].strip()):
            edits[values[0].strip()] = values[4]
        if re.fullmatch(r"PT-\d{5}", values[1].strip()):
            edits[values[1].strip()] = values[5]
    return edits


def replace_attribute(raw_tag: str, attribute: str, original: str, revised: str) -> str:
    pattern = re.compile(r"(\s" + re.escape(attribute) + r"\s*=\s*)([\"'])(.*?)\2", re.I | re.S)
    matches = list(pattern.finditer(raw_tag))
    for match in matches:
        if html.unescape(match.group(3)) == original:
            escaped = html.escape(revised, quote=True)
            return raw_tag[:match.start(3)] + escaped + raw_tag[match.end(3):]
    raise ValueError(f"attribute {attribute!r} with its expected original value was not found")


def revised_text(original: str, edited: str) -> str:
    """Retain source indentation/newlines while replacing only user-visible text."""
    leading = re.match(r"^\s*", original).group(0)
    trailing = re.search(r"\s*$", original).group(0)
    return leading + edited.strip() + trailing


def plan_html_changes(source_path: Path, entries: list[dict], edits: dict[str, str]) -> list[tuple[int, int, str, str]]:
    source = source_path.read_text(encoding="utf-8")
    locator = SourceLocator(source)
    locator.feed(source)
    locator.close()
    changes: list[tuple[int, int, str, str]] = []
    for entry in entries:
        edited = edits.get(entry["id"])
        if edited is None or edited == entry["display_value"]:
            continue
        if entry["attribute"]:
            span = locator.tags.get(entry["selector"])
            if span is None:
                raise ValueError(f"{entry['id']}: selector not found")
            start, end = span
            replacement = replace_attribute(source[start:end], entry["attribute"], entry["original_value"], edited.strip())
            changes.append((start, end, replacement, entry["id"]))
        else:
            key = (entry["selector"], entry["text_node_index"])
            span = locator.text.get(key)
            if span is None:
                raise ValueError(f"{entry['id']}: text-node target not found")
            start, end, decoded = span
            if decoded != entry["original_value"]:
                raise ValueError(f"{entry['id']}: source text no longer matches the export")
            replacement = html.escape(revised_text(decoded, edited), quote=False)
            changes.append((start, end, replacement, entry["id"]))
    return changes


def plan_json_changes(source_path: Path, entries: list[dict], edits: dict[str, str]) -> list[tuple[int, int, str, str]]:
    """Replace mapped JSON string literals while retaining all surrounding formatting."""
    source = source_path.read_text(encoding="utf-8")
    changes: list[tuple[int, int, str, str]] = []
    for entry in entries:
        edited = edits.get(entry["id"])
        if edited is None or edited == entry["display_value"]:
            continue
        key = entry["attribute"]
        pattern = re.compile(r'("' + re.escape(key) + r'"\s*:\s*)("(?:\\.|[^"\\])*")')
        for match in pattern.finditer(source):
            if json.loads(match.group(2)) == entry["original_value"]:
                changes.append((match.start(2), match.end(2), json.dumps(edited.strip(), ensure_ascii=False), entry["id"]))
                break
        else:
            raise ValueError(f"{entry['id']}: JSON key/value target not found")
    return changes


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--document", type=Path, default=DEFAULT_DOCUMENT)
    parser.add_argument("--map", dest="map_path", type=Path, default=DEFAULT_MAP)
    parser.add_argument(
        "--allow-source-changes",
        action="store_true",
        help=("Apply despite changes made after export. Exact mapped targets are still "
              "validated, so overlapping edits are refused."),
    )
    args = parser.parse_args()
    mapping = json.loads(args.map_path.read_text(encoding="utf-8"))
    edits = read_word_rows(args.document)
    expected_ids = {entry["id"] for entry in mapping["entries"]}
    missing = expected_ids - set(edits)
    extra = set(edits) - expected_ids
    if missing or extra:
        raise SystemExit(f"The Word document IDs do not match the map (missing={len(missing)}, extra={len(extra)}).")
    changed = [entry for entry in mapping["entries"] if edits[entry["id"]] != entry["display_value"]]
    by_source: dict[str, list[dict]] = {}
    for entry in changed:
        by_source.setdefault(entry["source_file"], []).append(entry)
    plans: dict[Path, list[tuple[int, int, str, str]]] = {}
    for source, entries in by_source.items():
        path = ROOT / source
        current = path.read_text(encoding="utf-8")
        expected_hash = mapping["source_files"][source]
        if digest(current) != expected_hash and not args.allow_source_changes:
            raise SystemExit(f"Refusing to apply: {source} changed after the export. Regenerate the export first.")
        if digest(current) != expected_hash:
            print(f"Warning: {source} changed after export; validating only mapped targets.", file=sys.stderr)
        plans[path] = (plan_json_changes(path, entries, edits) if source == "site.webmanifest"
                       else plan_html_changes(path, entries, edits))
    print(f"Edited Word rows detected: {len(changed)}")
    print(f"Source files affected: {len(plans)}")
    for path, changes in plans.items():
        print(f"  {path.relative_to(ROOT)}: {len(changes)} text-only replacement(s)")
    print("\nApplying changes...")

    for path, changes in plans.items():
        source = path.read_text(encoding="utf-8")

        for start, end, replacement, _entry_id in sorted(changes, reverse=True):
            source = source[:start] + replacement + source[end:]

        path.write_text(source, encoding="utf-8")

    print(
        "✓ Applied successfully. "
        "HTML structure, CSS, JavaScript, classes and IDs were preserved."
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
