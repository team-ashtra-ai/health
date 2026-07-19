#!/usr/bin/env python3
"""Create one editable, side-by-side English/PT-BR content inventory.

This is an extraction-only tool.  It reads the English HTML source and writes
two delivery artefacts outside the production site:

* exports/Franciele_Sofiati_Bilingual_Content_Editable.docx
* exports/Franciele_Sofiati_Bilingual_Content_Map.json

The JSON map deliberately records a source selector, the exact original value,
its source-file SHA-256 and a deterministic entry ID.  A later reinsertion
tool can therefore refuse to apply changes if the source has drifted, while
still targeting the same text node or attribute without changing markup.
"""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from datetime import date
from pathlib import Path
from xml.sax.saxutils import escape

from bs4 import BeautifulSoup, Comment, NavigableString, Tag


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "exports"
DOCX_OUTPUT = OUTPUT_DIR / "Franciele_Sofiati_Bilingual_Content_Editable.docx"
MAP_OUTPUT = OUTPUT_DIR / "Franciele_Sofiati_Bilingual_Content_Map.json"

SKIP_ANCESTORS = {"script", "style", "svg", "template", "noscript"}
HIDDEN_CLASSES = {"sf-visually-hidden", "sf-honeypot"}
PUBLIC_ATTRIBUTES = (
    # These are rendered as text in the visible page interface, either directly
    # or when the visitor interacts with it. Deliberately exclude SEO metadata,
    # image alt text and screen-reader-only ARIA labels from this export.
    "placeholder",
    # These data attributes are rendered by site JavaScript as public UI copy.
    "data-tooltip", "data-label-open", "data-label-close", "data-message-email",
    "data-message-required", "data-message-review", "data-label-empty",
    "data-label-singular", "data-label-plural", "data-saved-message",
)


def sha256(value: str | bytes) -> str:
    payload = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(payload).hexdigest()


def display(value: str) -> str:
    """Keep the source value in the map but make whitespace readable in Word."""
    return re.sub(r"\s+", " ", value).strip()


def css_path(tag: Tag) -> str:
    """A deterministic CSS path, sufficient when checked against the file hash."""
    parts: list[str] = []
    current: Tag | None = tag
    while current is not None and current.name not in {"[document]", None}:
        parent = current.parent if isinstance(current.parent, Tag) else None
        if current.get("id"):
            parts.append(f"{current.name}#{current['id']}")
        else:
            siblings = parent.find_all(current.name, recursive=False) if parent is not None else [current]
            # BeautifulSoup Tags compare structurally, so use identity rather than
            # list.index()/equality: repeated empty options are otherwise ambiguous.
            index = next(index for index, sibling in enumerate(siblings, start=1)
                         if sibling is current)
            parts.append(f"{current.name}:nth-of-type({index})")
        current = parent
    return " > ".join(reversed(parts))


def ancestor_is_excluded(node: NavigableString) -> bool:
    for parent in node.parents:
        if not isinstance(parent, Tag):
            continue
        if parent.name in SKIP_ANCESTORS:
            return True
        classes = set(parent.get("class", []))
        if classes & HIDDEN_CLASSES or parent.get("type") == "hidden":
            return True
    return False


def text_node_index(tag: Tag, node: NavigableString) -> int:
    nodes = [item for item in tag.descendants if isinstance(item, NavigableString) and not isinstance(item, Comment)]
    return nodes.index(node)


def record(records: list[dict], *, source: str, source_hash: str, selector: str,
           kind: str, value: str, attribute: str | None = None,
           node_index: int | None = None, context: str = "", language: str = "en") -> None:
    if not display(value):
        return
    records.append({
        "id": f"{language.upper()}-{len(records) + 1:05d}",
        "language": language,
        "source_file": source,
        "source_sha256": source_hash,
        "selector": selector,
        "kind": kind,
        "attribute": attribute,
        "text_node_index": node_index,
        "original_value": value,
        "original_value_sha256": sha256(value),
        "display_value": display(value),
        "context": context,
    })


def extract_html(path: Path, language: str) -> list[dict]:
    source = path.relative_to(ROOT).as_posix()
    payload = path.read_text(encoding="utf-8")
    source_hash = sha256(payload)
    soup = BeautifulSoup(payload, "html.parser")
    records: list[dict] = []

    container: Tag | BeautifulSoup = soup.body if soup.body is not None else soup
    for node in container.descendants:
        if not isinstance(node, NavigableString) or isinstance(node, Comment) or ancestor_is_excluded(node):
            continue
        parent = node.parent
        if not isinstance(parent, Tag):
            continue
        record(records, source=source, source_hash=source_hash, selector=css_path(parent),
               kind="visible_text", value=str(node), node_index=text_node_index(parent, node),
               context=parent.name, language=language)

    # Accessible, form and visual-description strings that may not appear as a text node.
    for tag in container.find_all(True):
        if tag.name in SKIP_ANCESTORS:
            continue
        classes = set(tag.get("class", []))
        if classes & HIDDEN_CLASSES or tag.get("type") == "hidden":
            continue
        for attribute in PUBLIC_ATTRIBUTES:
            if tag.has_attr(attribute):
                kind = "form_placeholder" if attribute == "placeholder" else "runtime_ui_copy"
                record(records, source=source, source_hash=source_hash, selector=css_path(tag),
                       kind=kind, attribute=attribute, value=str(tag[attribute]), context=tag.name,
                       language=language)
    return records


def english_source_files() -> list[Path]:
    pages = sorted(ROOT.glob("*.html")) + sorted((ROOT / "journal").glob("*.html"))
    partials = sorted((ROOT / "partials").glob("*.html"))
    return pages + partials


def portuguese_source_files() -> list[Path]:
    return sorted((ROOT / "pt").glob("*.html")) + sorted((ROOT / "partials" / "pt-BR").glob("*.html"))


def counterpart_source(source: str, language: str) -> str | None:
    """Return the same page/partial in the other published language."""
    if language == "en":
        if source.startswith("journal/"):
            return None  # Long-form journal articles do not have PT-BR pages.
        return f"partials/pt-BR/{source.removeprefix('partials/')}" if source.startswith("partials/") else f"pt/{source}"
    if source.startswith("partials/pt-BR/"):
        return f"partials/{source.removeprefix('partials/pt-BR/')}"
    return source.removeprefix("pt/")


def pairing_key(item: dict) -> tuple[str, str, str | None, int | None]:
    return item["selector"], item["kind"], item["attribute"], item["text_node_index"]


def paragraph(text: str, style: str = "Normal") -> str:
    return (f'<w:p><w:pPr><w:pStyle w:val="{style}"/></w:pPr>'
            f'<w:r><w:t xml:space="preserve">{escape(text)}</w:t></w:r></w:p>')


def cell(text: str, width: int, bold: bool = False) -> str:
    run_props = "<w:b/>" if bold else ""
    return (f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
            f'<w:p><w:r><w:rPr>{run_props}</w:rPr><w:t xml:space="preserve">'
            f'{escape(text)}</w:t></w:r></w:p></w:tc>')


def table_row(values: list[str], widths: list[int], header: bool = False) -> str:
    return '<w:tr>' + ''.join(cell(value, width, header) for value, width in zip(values, widths)) + '</w:tr>'


def source_label(record: dict) -> str:
    if record["kind"] == "visible_text":
        return "Visible text"
    return record["kind"].replace("_", " ").title() + (f" ({record['attribute']})" if record["attribute"] else "")


def build_docx(rows: list[tuple[dict | None, dict | None]]) -> bytes:
    body: list[str] = [
        paragraph("Franciele Sofiati — Bilingual Content Export", "Title"),
        paragraph("Editable, side-by-side extraction of public English and Brazilian Portuguese website content", "Subtitle"),
        paragraph(f"Export date: {date.today().isoformat()}"),
        paragraph(
            "Editing instruction: edit either Current English text or Current Portuguese text, as needed. Keep both stable ID columns unchanged. "
            "The companion JSON map identifies the exact source file, selector, node/attribute and source hash for every entry. "
            "No website source file was changed to create this export."
        ),
        paragraph(
            "Scope: visibly rendered page text, form placeholders and text that appears through visible interface interactions. "
            "Shared partials are listed once because they are reused sitewide. SEO/social metadata, browser-title metadata, image alt text, "
            "screen-reader-only labels, scripts, styles, templates and hidden decorative text are excluded."
        ),
        paragraph(f"Editable rows: {len(rows)}"),
    ]
    grouped: dict[str, list[tuple[dict | None, dict | None]]] = {}
    for english, portuguese in rows:
        source = english["source_file"] if english else portuguese["source_file"]
        grouped.setdefault(source, []).append((english, portuguese))
    widths = [900, 900, 1400, 2000, 3800, 3800]
    for source, items in grouped.items():
        body.append(paragraph(source, "Heading1"))
        source_hashes = [item["source_sha256"] for pair in items for item in pair if item]
        body.append(paragraph(f"Source SHA-256: {', '.join(source_hashes[:2])}"))
        table_rows = [table_row(["English ID", "Portuguese ID", "Type", "Source target", "Current English text", "Current Portuguese text"], widths, True)]
        for english, portuguese in items:
            item = english or portuguese
            target = item["selector"] + (f" @ {item['attribute']}" if item["attribute"] else "")
            table_rows.append(table_row([
                english["id"] if english else "—",
                portuguese["id"] if portuguese else "—",
                source_label(item), target,
                english["display_value"] if english else "Not published in English",
                portuguese["display_value"] if portuguese else "Not published in Portuguese",
            ], widths))
        body.append('<w:tbl><w:tblPr><w:tblW w:w="9900" w:type="dxa"/>'
                    '<w:tblBorders><w:top w:val="single" w:sz="4"/><w:left w:val="single" w:sz="4"/>'
                    '<w:bottom w:val="single" w:sz="4"/><w:right w:val="single" w:sz="4"/>'
                    '<w:insideH w:val="single" w:sz="2"/><w:insideV w:val="single" w:sz="2"/>'
                    '</w:tblBorders></w:tblPr>' + ''.join(table_rows) + '</w:tbl>')
    body.append('<w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="900" w:right="720" w:bottom="900" w:left="720"/></w:sectPr>')
    document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>'
                + ''.join(body) + '</w:body></w:document>')
    styles = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:rPr><w:sz w:val="18"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:rPr><w:b/><w:sz w:val="34"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Subtitle"><w:name w:val="Subtitle"/><w:rPr><w:sz w:val="22"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:rPr><w:b/><w:sz w:val="26"/></w:rPr></w:style>
</w:styles>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/><Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/></Types>'''
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
    document_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/></Relationships>'''
    import io
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", content_types)
        archive.writestr("_rels/.rels", rels)
        archive.writestr("word/document.xml", document)
        archive.writestr("word/styles.xml", styles)
        archive.writestr("word/_rels/document.xml.rels", document_rels)
    return output.getvalue()


def main() -> None:
    english = [item for path in english_source_files() for item in extract_html(path, "en")]
    portuguese = [item for path in portuguese_source_files() for item in extract_html(path, "pt")]
    for index, item in enumerate(english, start=1):
        item["id"] = f"EN-{index:05d}"
    for index, item in enumerate(portuguese, start=1):
        item["id"] = f"PT-{index:05d}"
    portuguese_by_target = {(item["source_file"], pairing_key(item)): item for item in portuguese}
    paired_pt_ids: set[str] = set()
    rows: list[tuple[dict | None, dict | None]] = []
    for item in english:
        target = counterpart_source(item["source_file"], "en")
        match = portuguese_by_target.get((target, pairing_key(item))) if target else None
        if match:
            paired_pt_ids.add(match["id"])
        rows.append((item, match))
    rows.extend((None, item) for item in portuguese if item["id"] not in paired_pt_ids)
    records = english + portuguese
    OUTPUT_DIR.mkdir(exist_ok=True)
    source_hashes = {item["source_file"]: item["source_sha256"] for item in records}
    payload = {
        "schema_version": 2,
        "purpose": "Extraction-only map for reinserting manually revised English and Brazilian Portuguese content without changing markup or design.",
        "generated_on": date.today().isoformat(),
        "source_languages": ["en", "pt-BR"],
        "word_document": DOCX_OUTPUT.name,
        "source_files": source_hashes,
        "entry_count": len(records),
        "row_count": len(rows),
        "reinsertion_contract": {
            "require_source_sha256_match": True,
            "visible_text": "Select selector, then replace the descendant NavigableString at text_node_index only if original_value_sha256 matches.",
            "attributes": "Select selector, then replace attribute only if original_value_sha256 matches.",
            "json": "Replace the JSON key at selector only if original_value_sha256 matches.",
        },
        "entries": records,
    }
    MAP_OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    DOCX_OUTPUT.write_bytes(build_docx(rows))
    print(f"Created {DOCX_OUTPUT.relative_to(ROOT)} ({len(rows)} bilingual editable rows)")
    print(f"Created {MAP_OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
