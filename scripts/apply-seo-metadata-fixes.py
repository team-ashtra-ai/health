#!/usr/bin/env python3
"""Preview or apply reviewed SEO metadata fixes without touching page design.

The fixes below are editorially reviewed Portuguese descriptions. They update
the standard, Open Graph and Twitter description on each affected page, plus
the approved Portuguese translation memory so future localization runs retain
the correction. Add future reviewed fixes to ``FIXES``; never use this script
to generate speculative marketing language.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import html
import json
from pathlib import Path
import re
import sys

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
MEMORY_PATH = ROOT / "data" / "translation" / "pt-BR-memory.json"
DESCRIPTION_TAG = re.compile(
    r'<meta\b(?=[^>]*(?:name="(?:description|twitter:description)"|property="og:description"))[^>]*>',
    re.IGNORECASE,
)
CONTENT_ATTRIBUTE = re.compile(r'(\bcontent=")[^"]*(")', re.IGNORECASE)

# Keep each description between 120 and 170 characters. These are reviewed,
# specific corrections for the warnings currently reported by the validator.
FIXES = {
    "pt/consultation.html": "Agende uma consulta estética com Franciele Sofiati em Londrina e receba um plano personalizado para pele, laser, rosto, couro cabeludo ou corpo.",
    "pt/index.html": "Cuidados personalizados para pele, laser, couro cabeludo e estética em Londrina com Franciele Sofiati, com planejamento e acompanhamento.",
    "pt/legal.html": "Leia as condições de agendamento, pagamento, cancelamento, tratamentos, consentimento informado e cuidados posteriores de Franciele Sofiati em Londrina.",
    "pt/privacy.html": "Entenda como Franciele Sofiati trata dados de contato, consulta e navegação segundo os princípios brasileiros de proteção de dados.",
    "pt/values.html": "Conheça os valores de escuta, clareza, segurança e continuidade que orientam a prática estética centrada na paciente de Franciele Sofiati em Londrina.",
}


def meta_description(path: Path) -> str:
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    tag = soup.find("meta", attrs={"name": "description"})
    if not tag or not tag.get("content"):
        raise RuntimeError(f"{path.relative_to(ROOT)} has no standard meta description")
    return str(tag["content"])


def replace_description_tags(source: str, description: str) -> tuple[str, int]:
    """Replace only description meta content attributes, retaining page formatting."""

    replacement = html.escape(description, quote=True)
    count = 0

    def update_tag(match: re.Match[str]) -> str:
        nonlocal count
        tag, substitutions = CONTENT_ATTRIBUTE.subn(rf'\g<1>{replacement}\g<2>', match.group(0), count=1)
        count += substitutions
        return tag

    updated = DESCRIPTION_TAG.sub(update_tag, source)
    return updated, count


def update_translation_memory(memory: dict[str, object], english: str, portuguese: str) -> bool:
    records = memory.get("entries")
    if not isinstance(records, dict):
        raise RuntimeError("Translation memory has no entries object")
    matches = [record for record in records.values() if isinstance(record, dict) and record.get("source") == english]
    if len(matches) != 1:
        raise RuntimeError(f"Expected one translation-memory record for: {english!r}; found {len(matches)}")
    record = matches[0]
    changed = record.get("translation") != portuguese or record.get("approved") is not True
    record["translation"] = portuguese
    record["approved"] = True
    record["engine"] = "manual:seo-metadata"
    record["updated_at"] = datetime.now(timezone.utc).isoformat()
    return changed


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply reviewed Portuguese SEO description corrections.")
    parser.add_argument("--apply", action="store_true", help="Write page and translation-memory changes")
    arguments = parser.parse_args()

    memory = json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    changed_pages: list[str] = []
    for relative, description in FIXES.items():
        if not 120 <= len(description) <= 170:
            raise RuntimeError(f"Configured description for {relative} is {len(description)} characters")
        portuguese_path = ROOT / relative
        english_path = ROOT / relative.removeprefix("pt/")
        current = portuguese_path.read_text(encoding="utf-8")
        updated, tags_updated = replace_description_tags(current, description)
        if tags_updated != 3:
            raise RuntimeError(f"{relative} expected 3 description tags, found {tags_updated}")
        update_translation_memory(memory, meta_description(english_path), description)
        changed_pages.append(f"{relative} ({len(description)} characters)")
        if arguments.apply and updated != current:
            portuguese_path.write_text(updated, encoding="utf-8")

    if arguments.apply:
        MEMORY_PATH.write_text(json.dumps(memory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("Applied reviewed metadata fixes:")
    else:
        print("Preview only. Run again with --apply to write these reviewed fixes:")
    for item in changed_pages:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
