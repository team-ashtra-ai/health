"""Block-aware Portuguese site generation, manifests, backups and reports."""

from __future__ import annotations

import json
import os
import re
import shutil
import tempfile
from dataclasses import dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Protocol

from .html_document import TranslationBlock, digest, extract_blocks, normalized, render_portuguese_html


MANIFEST_VERSION = "pt-br-argos-blocks-v3"


class TranslationEngine(Protocol):
    identifier: str

    def translate(self, text: str) -> str: ...


@dataclass(frozen=True)
class GenerationConfig:
    root: Path
    mode: str = "incremental"
    preserve_overrides: bool = True
    fresh_translation: bool = False
    yes: bool = False
    delete_obsolete: bool = False
    color: bool = True

    @property
    def pt_dir(self) -> Path:
        return self.root / "pt"

    @property
    def localized_partials_dir(self) -> Path:
        return self.root / "partials" / "pt-BR"

    @property
    def manifest_path(self) -> Path:
        return self.root / ".translation-cache.json"

    @property
    def glossary_path(self) -> Path:
        return self.root / "data" / "translation" / "pt-BR-glossary.json"

    @property
    def memory_path(self) -> Path:
        return self.root / "data" / "translation" / "pt-BR-memory.json"

    @property
    def overrides_path(self) -> Path:
        return self.root / "data" / "translation" / "pt-BR-overrides.json"

    @property
    def report_dir(self) -> Path:
        return self.root / "reports" / "translation"

    @property
    def backup_root(self) -> Path:
        return self.root / "backups" / "pt"


@dataclass(frozen=True)
class TranslationUnit:
    key: str
    source: Path
    output: Path
    page: str
    partial: bool = False


@dataclass
class Conflict:
    unit: str
    block_key: str
    previous_english: str
    new_english: str
    manual_portuguese: str


@dataclass
class UnitResult:
    unit: str
    status: str
    source_blocks: int = 0
    overrides: int = 0
    conflicts: list[Conflict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


@dataclass
class RunSummary:
    scanned: int = 0
    created: int = 0
    updated: int = 0
    skipped: int = 0
    overrides: int = 0
    conflicts: list[Conflict] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)
    obsolete: list[str] = field(default_factory=list)
    deleted: list[str] = field(default_factory=list)
    results: list[UnitResult] = field(default_factory=list)
    backup: Path | None = None
    report: Path | None = None


class Terminal:
    COLORS = {
        "green": "\033[32m", "yellow": "\033[33m", "red": "\033[31m",
        "cyan": "\033[36m", "bold": "\033[1m", "reset": "\033[0m",
    }

    def __init__(self, color: bool = True):
        self.color = color and os.isatty(1) and os.environ.get("NO_COLOR") is None

    def _wrap(self, value: str, color: str) -> str:
        if not self.color:
            return value
        return f"{self.COLORS[color]}{value}{self.COLORS['reset']}"

    def info(self, value: str) -> None:
        print(self._wrap("•", "cyan"), value, flush=True)

    def success(self, value: str) -> None:
        print(self._wrap("✓", "green"), value, flush=True)

    def warning(self, value: str) -> None:
        print(self._wrap("!", "yellow"), value, flush=True)

    def error(self, value: str) -> None:
        print(self._wrap("✗", "red"), value, flush=True)

    def heading(self, value: str) -> None:
        print(f"\n{self._wrap(value, 'bold')}", flush=True)


def _read_json(path: Path, default: Any) -> Any:
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Cannot read JSON file {path}: {error}") from error


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temp_path = Path(temporary)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, path)
    finally:
        temp_path.unlink(missing_ok=True)


def atomic_json(path: Path, payload: Any) -> None:
    content = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return
    atomic_write(path, content)


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def discover_units(config: GenerationConfig) -> list[TranslationUnit]:
    pages: list[TranslationUnit] = []
    for source in sorted(config.root.glob("*.html")):
        text = source.read_text(encoding="utf-8", errors="ignore")
        if "<main" not in text.lower():
            continue
        pages.append(TranslationUnit(source.name, source, config.pt_dir / source.name, source.name))

    partials: list[TranslationUnit] = []
    partial_root = config.root / "partials"
    for source in sorted(partial_root.glob("*.html")):
        key = f"partials/{source.name}"
        partials.append(
            TranslationUnit(key, source, config.localized_partials_dir / source.name, "index.html", partial=True)
        )
    return pages + partials


class BrazilianTranslator:
    TOKEN_PATTERN = re.compile(
        r"(?:https?://\S+|[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}|\+?\d[\d\s().-]{6,}\d|"
        r"Franciele Sofiati(?: Biomédica)?|Sofiati|CRBM\s*\d+|WhatsApp|Instagram|Google)",
        re.I,
    )

    def __init__(
        self,
        engine: TranslationEngine,
        glossary: dict[str, Any],
        memory: dict[str, Any],
        glossary_hash: str,
    ):
        self.engine = engine
        self.exact = {normalized(k): v for k, v in glossary.get("exact", {}).items()}
        self.preferred_terms = {
            normalized(k): normalized(str(v))
            for k, v in glossary.get("preferred_terms", {}).items()
            if normalized(k) and normalized(str(v))
        }
        self.post_replacements = glossary.get("post_replacements", {})
        self.glossary_hash = glossary_hash
        self.memory = memory
        self.memory.setdefault("version", 1)
        self.memory.setdefault("locale", "pt-BR")
        self.memory.setdefault("entries", {})

    def _protect(self, text: str) -> tuple[str, dict[str, str]]:
        protected: dict[str, str] = {}

        def replace(match: re.Match[str]) -> str:
            token = f"ZXQ{len(protected):04d}QXZ"
            protected[token] = match.group(0)
            return token

        result = self.TOKEN_PATTERN.sub(replace, text)

        # Protect glossary phrases as opaque tokens so Argos cannot choose a
        # conflicting translation. They are restored as approved pt-BR terms.
        for source, translation in sorted(self.preferred_terms.items(), key=lambda item: len(item[0]), reverse=True):
            pattern = rf"(?<!\w){re.escape(source)}(?!\w)"

            def replace_term(match: re.Match[str], approved: str = translation) -> str:
                token = f"ZXQ{len(protected):04d}QXZ"
                protected[token] = approved
                return token

            result = re.sub(pattern, replace_term, result, flags=re.I)
        return result, protected

    @staticmethod
    def _restore(text: str, protected: dict[str, str]) -> str:
        result = text
        for token, value in protected.items():
            result = re.sub(re.escape(token), value, result, flags=re.I)
        return result

    def _brazilianize(self, text: str) -> str:
        result = text
        for source, target in self.post_replacements.items():
            result = re.sub(rf"\b{re.escape(source)}\b", target, result, flags=re.I)
        result = result.replace("Brasil brasileiro", "Brasil")
        return result

    def translate(self, source: str) -> tuple[str, str]:
        source = normalized(source)
        if source in self.exact:
            return str(self.exact[source]), "glossary"
        key = digest(source)
        entry = self.memory["entries"].get(key)
        if (
            entry
            and entry.get("source") == source
            and entry.get("translation")
            and (entry.get("approved") is True or entry.get("glossary_hash") == self.glossary_hash)
        ):
            return self._brazilianize(str(entry["translation"])), "memory"

        protected_source, protected = self._protect(source)
        translated = self.engine.translate(protected_source)
        translated = self._brazilianize(self._restore(translated, protected)).strip()
        if not translated:
            raise RuntimeError("translation result is empty")
        self.memory["entries"][key] = {
            "source": source,
            "translation": translated,
            "engine": self.engine.identifier,
            "approved": False,
            "glossary_hash": self.glossary_hash,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
        return translated, "argos"

    def approve_manual(self, source: str, translation: str) -> None:
        source = normalized(source)
        translation = normalized(translation)
        key = digest(source)
        previous = self.memory["entries"].get(key, {})
        if (
            previous.get("source") == source
            and previous.get("translation") == translation
            and previous.get("approved") is True
        ):
            return
        self.memory["entries"][key] = {
            "source": source,
            "translation": translation,
            "engine": "manual-override",
            "approved": True,
            "glossary_hash": self.glossary_hash,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }


class PortugueseSiteGenerator:
    def __init__(
        self,
        config: GenerationConfig,
        engine: TranslationEngine | None,
        terminal: Terminal | None = None,
    ):
        self.config = config
        self.engine = engine
        self.terminal = terminal or Terminal(config.color)
        self.units = discover_units(config)
        self.glossary = _read_json(config.glossary_path, {"exact": {}, "post_replacements": {}})
        self.glossary_hash = _file_hash(config.glossary_path) if config.glossary_path.exists() else digest("{}")
        # A fresh pass intentionally does not reuse machine or manual memory.
        # The approved glossary remains active for consistent Brazilian terms.
        self.memory = (
            {"version": 1, "locale": "pt-BR", "entries": {}}
            if config.fresh_translation
            else _read_json(config.memory_path, {"version": 1, "locale": "pt-BR", "entries": {}})
        )
        self.explicit_overrides = _read_json(config.overrides_path, {"version": 1, "locale": "pt-BR", "blocks": {}})
        overrides_hash = _file_hash(config.overrides_path) if config.overrides_path.exists() else digest("{}")
        self.translation_config_hash = digest(f"{self.glossary_hash}:{overrides_hash}")
        self.manifest = _read_json(config.manifest_path, {"version": MANIFEST_VERSION, "pages": {}})
        self.legacy_manifest = self.manifest.get("version") != MANIFEST_VERSION
        if self.legacy_manifest:
            self.manifest = {
                "version": MANIFEST_VERSION,
                "locale": "pt-BR",
                "engine": None,
                "updated_at": None,
                "pages": {},
                "migration_note": "Previous page-level cache migrated; first v3 write establishes block history.",
            }
        self.translation_config_changed = (
            self.manifest.get("translation_config_hash") != self.translation_config_hash
        )
        self.translator = BrazilianTranslator(engine, self.glossary, self.memory, self.glossary_hash) if engine else None

    def _current_blocks(self, unit: TranslationUnit) -> dict[str, TranslationBlock]:
        if not unit.output.exists():
            return {}
        return extract_blocks(unit.output.read_text(encoding="utf-8"))

    def _manual_values(
        self,
        unit: TranslationUnit,
        old_page: dict[str, Any],
        current_blocks: dict[str, TranslationBlock],
    ) -> dict[str, str]:
        if not self.config.preserve_overrides:
            return {}
        manual: dict[str, str] = {}
        if not unit.partial:
            for key, record in old_page.get("blocks", {}).items():
                current = current_blocks.get(key)
                generated = record.get("generated_translation")
                if current and generated is not None and normalized(current.source) != normalized(str(generated)):
                    manual[key] = current.source
        for key, value in self.explicit_overrides.get("blocks", {}).get(unit.key, {}).items():
            if isinstance(value, str):
                manual[key] = normalized(value)
        return manual

    def _plan_status(self, unit: TranslationUnit, source_hash: str, old_page: dict[str, Any]) -> str:
        if not unit.output.exists():
            return "created"
        if unit.partial:
            return "updated"
        if self.config.mode == "full":
            return "updated"
        if (
            old_page.get("source_hash") == source_hash
            and not self.legacy_manifest
            and not self.translation_config_changed
        ):
            return "skipped"
        return "updated"

    def analyze(self) -> tuple[list[tuple[TranslationUnit, str]], list[str]]:
        plans: list[tuple[TranslationUnit, str]] = []
        manifest_pages = self.manifest.get("pages", {})
        for unit in self.units:
            plans.append((unit, self._plan_status(unit, _file_hash(unit.source), manifest_pages.get(unit.key, {}))))
        expected = {unit.output.resolve() for unit in self.units}
        existing = {
            *self.config.pt_dir.glob("*.html"),
            *self.config.localized_partials_dir.glob("*.html"),
        }
        obsolete = sorted(path.relative_to(self.config.root).as_posix() for path in existing if path.resolve() not in expected)
        return plans, obsolete

    def _backup(self, units: list[TranslationUnit], extra_paths: list[Path] | None = None) -> Path | None:
        existing = [unit.output for unit in units if unit.output.exists()]
        existing.extend(path for path in (extra_paths or []) if path.exists())
        existing = list(dict.fromkeys(existing))
        if not existing:
            return None
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        destination = self.config.backup_root / stamp
        for output in existing:
            relative = output.relative_to(self.config.root)
            target = destination / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(output, target)
        if self.config.manifest_path.exists():
            shutil.copy2(self.config.manifest_path, destination / self.config.manifest_path.name)
        if self.config.fresh_translation and self.config.memory_path.exists():
            shutil.copy2(self.config.memory_path, destination / self.config.memory_path.name)
        return destination

    def _translate_unit(self, unit: TranslationUnit, status: str) -> tuple[str, dict[str, Any], UnitResult]:
        if self.translator is None:
            raise RuntimeError("Argos is required to create or update Portuguese output")
        source_html = unit.source.read_text(encoding="utf-8")
        source_blocks = extract_blocks(source_html)
        old_page = self.manifest.get("pages", {}).get(unit.key, {})
        current_blocks = self._current_blocks(unit)
        manual = self._manual_values(unit, old_page, current_blocks)
        translations: dict[str, str] = {}
        records: dict[str, Any] = {}
        conflicts: list[Conflict] = []
        now = datetime.now(timezone.utc).isoformat()

        for key, block in source_blocks.items():
            old_record = old_page.get("blocks", {}).get(key, {})
            explicit = manual.get(key)
            if explicit is not None:
                previous_source = str(old_record.get("source", block.source))
                changed_source = old_record.get("source_hash") not in {None, block.source_hash}
                if changed_source:
                    machine, origin = self.translator.translate(block.source)
                    conflicts.append(Conflict(unit.key, key, previous_source, block.source, explicit))
                else:
                    machine = str(old_record.get("generated_translation", explicit))
                    origin = str(old_record.get("origin", "manual"))
                    self.translator.approve_manual(block.source, explicit)
                translations[key] = explicit
                records[key] = {
                    "kind": block.kind,
                    "source": block.source,
                    "source_hash": block.source_hash,
                    "generated_translation": machine,
                    "generated_hash": digest(machine),
                    "current_translation": explicit,
                    "manual_override": True,
                    "review_required": changed_source,
                    "origin": origin,
                }
                continue

            if (
                not unit.partial
                and not self.config.fresh_translation
                and not self.translation_config_changed
                and old_record.get("source_hash") == block.source_hash
                and old_record.get("generated_translation")
            ):
                translated = str(old_record["generated_translation"])
                origin = str(old_record.get("origin", "manifest"))
            else:
                translated, origin = self.translator.translate(block.source)
            translations[key] = translated
            records[key] = {
                "kind": block.kind,
                "source": block.source,
                "source_hash": block.source_hash,
                "generated_translation": translated,
                "generated_hash": digest(translated),
                "current_translation": translated,
                "manual_override": False,
                "review_required": False,
                "origin": origin,
            }

        for key, value in manual.items():
            if key not in source_blocks:
                old_record = old_page.get("blocks", {}).get(key, {})
                conflicts.append(
                    Conflict(unit.key, key, str(old_record.get("source", "")), "[block removed]", value)
                )

        output = render_portuguese_html(source_html, translations, unit.page, partial=unit.partial)
        page_record = {
            "source_path": unit.source.relative_to(self.config.root).as_posix(),
            "output_path": unit.output.relative_to(self.config.root).as_posix(),
            "source_hash": _file_hash(unit.source),
            "output_hash": digest(output),
            "last_translated": now,
            "engine": self.engine.identifier if self.engine else None,
            "manual_override": bool(manual),
            "manual_review_required": bool(conflicts),
            "blocks": records,
        }
        return output, page_record, UnitResult(
            unit.key,
            status,
            source_blocks=len(source_blocks),
            overrides=len(manual),
            conflicts=conflicts,
        )

    def _refresh_skipped_manifest(self, unit: TranslationUnit, old_page: dict[str, Any]) -> UnitResult:
        current = self._current_blocks(unit)
        manual = self._manual_values(unit, old_page, current)
        for key, record in old_page.get("blocks", {}).items():
            if key in manual:
                record["manual_override"] = True
                record["current_translation"] = manual[key]
                record["review_required"] = False
                self.translator and self.translator.approve_manual(str(record.get("source", "")), manual[key])
            else:
                record["manual_override"] = False
                record["current_translation"] = record.get("generated_translation")
        old_page["manual_override"] = bool(manual)
        old_page["manual_review_required"] = False
        if unit.output.exists():
            old_page["output_hash"] = _file_hash(unit.output)
        return UnitResult(unit.key, "skipped", source_blocks=len(old_page.get("blocks", {})), overrides=len(manual))

    def _write_report(self, summary: RunSummary) -> Path:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        report = self.config.report_dir / f"portuguese-generation-{stamp}.md"
        latest = self.config.report_dir / "latest.md"
        lines = [
            "# Portuguese generation review",
            "",
            f"Generated: {datetime.now(timezone.utc).isoformat()}",
            f"Mode: `{self.config.mode}`",
            f"Engine: `{self.engine.identifier if self.engine else 'not loaded'}`",
            "",
            "## Summary",
            "",
            f"- Units scanned: {summary.scanned}",
            f"- Pages/partials created: {summary.created}",
            f"- Pages/partials updated: {summary.updated}",
            f"- Unchanged units skipped: {summary.skipped}",
            f"- Manual overrides preserved: {summary.overrides}",
            f"- Conflicts requiring review: {len(summary.conflicts)}",
            f"- Failures: {len(summary.failures)}",
            f"- Obsolete outputs deleted: {len(summary.deleted)}",
            f"- Backup: `{summary.backup.relative_to(self.config.root) if summary.backup else 'not required'}`",
            f"- Manifest: `{self.config.manifest_path.relative_to(self.config.root)}`",
            "",
            "## Files",
            "",
        ]
        lines.extend(f"- `{result.unit}` — {result.status}" for result in summary.results)
        lines.extend(["", "## Override conflicts", ""])
        if summary.conflicts:
            for conflict in summary.conflicts:
                lines.extend(
                    [
                        f"### `{conflict.unit}` · `{conflict.block_key}`",
                        "",
                        f"- Previous English: {conflict.previous_english}",
                        f"- New English: {conflict.new_english}",
                        f"- Current manual Portuguese: {conflict.manual_portuguese}",
                        "",
                    ]
                )
        else:
            lines.append("No override conflicts were found.")
        lines.extend(["", "## Obsolete outputs", ""])
        lines.extend(f"- `{value}`" for value in summary.obsolete) if summary.obsolete else lines.append("None.")
        if summary.deleted:
            lines.extend(["", "Deleted after confirmation:", ""])
            lines.extend(f"- `{value}`" for value in summary.deleted)
        lines.extend(["", "## Failures and warnings", ""])
        lines.extend(f"- {value}" for value in summary.failures) if summary.failures else lines.append("None.")
        content = "\n".join(lines) + "\n"
        atomic_write(report, content)
        atomic_write(latest, content)
        return report

    def run(self) -> RunSummary:
        manifest_before = json.dumps(self.manifest, ensure_ascii=False, sort_keys=True)
        plans, obsolete = self.analyze()
        summary = RunSummary(scanned=len(plans), obsolete=obsolete)
        self.terminal.heading("Portuguese generation plan")
        self.terminal.info(f"English pages found: {sum(not unit.partial for unit, _ in plans)}")
        self.terminal.info(f"Shared partials found: {sum(unit.partial for unit, _ in plans)}")
        self.terminal.info(f"Existing Portuguese pages: {len(list(self.config.pt_dir.glob('*.html')))}")
        if self.legacy_manifest:
            self.terminal.warning("Legacy page-level cache detected; v3 block history will be established on write.")
        for unit, status in plans:
            self.terminal.info(f"{status.upper():7} {unit.key}")
        for value in obsolete:
            self.terminal.warning(f"Obsolete output (not deleted): {value}")

        if self.config.mode == "dry-run":
            for unit, status in plans:
                try:
                    source_blocks = extract_blocks(unit.source.read_text(encoding="utf-8"))
                    old_page = self.manifest.get("pages", {}).get(unit.key, {})
                    manual = self._manual_values(unit, old_page, self._current_blocks(unit))
                    conflicts: list[Conflict] = []
                    for key, value in manual.items():
                        old_record = old_page.get("blocks", {}).get(key, {})
                        current_source = source_blocks.get(key)
                        if current_source is None:
                            conflicts.append(Conflict(
                                unit.key, key, str(old_record.get("source", "")), "[block removed]", value
                            ))
                        elif old_record.get("source_hash") not in {None, current_source.source_hash}:
                            conflicts.append(Conflict(
                                unit.key,
                                key,
                                str(old_record.get("source", "")),
                                current_source.source,
                                value,
                            ))
                    result = UnitResult(
                        unit.key,
                        status,
                        source_blocks=len(source_blocks),
                        overrides=len(manual),
                        conflicts=conflicts,
                    )
                    summary.overrides += len(manual)
                    summary.conflicts.extend(conflicts)
                    summary.results.append(result)
                    setattr(summary, status, getattr(summary, status) + 1)
                    if manual:
                        self.terminal.info(f"Would preserve {len(manual)} manual override(s): {unit.key}")
                    for conflict in conflicts:
                        self.terminal.warning(f"Would require review: {conflict.unit} · {conflict.block_key}")
                except Exception as error:
                    message = f"{unit.key}: dry-run analysis failed: {type(error).__name__}: {error}"
                    summary.failures.append(message)
                    summary.results.append(UnitResult(unit.key, "failed", error=message))
                    self.terminal.error(message)
            return summary

        changed = [unit for unit, status in plans if status != "skipped"]
        obsolete_paths = [self.config.root / value for value in obsolete] if self.config.delete_obsolete else []
        summary.backup = self._backup(
            self.units if self.config.mode == "full" else changed,
            obsolete_paths,
        )
        if summary.backup:
            self.terminal.success(f"Backup created: {summary.backup.relative_to(self.config.root)}")

        manifest_pages = self.manifest.setdefault("pages", {})
        total = len(plans)
        for index, (unit, status) in enumerate(plans, start=1):
            self.terminal.info(f"[{index}/{total}] {unit.key}")
            try:
                if status == "skipped":
                    result = self._refresh_skipped_manifest(unit, manifest_pages.get(unit.key, {}))
                    summary.skipped += 1
                    self.terminal.success(f"Skipped unchanged: {unit.key}")
                else:
                    output, page_record, result = self._translate_unit(unit, status)
                    atomic_write(unit.output, output)
                    manifest_pages[unit.key] = page_record
                    if status == "created":
                        summary.created += 1
                        self.terminal.success(f"Created: {unit.output.relative_to(self.config.root)}")
                    else:
                        summary.updated += 1
                        self.terminal.success(f"Updated: {unit.output.relative_to(self.config.root)}")
                summary.overrides += result.overrides
                summary.conflicts.extend(result.conflicts)
                if result.overrides:
                    self.terminal.info(f"Preserved {result.overrides} manual override(s)")
                for conflict in result.conflicts:
                    self.terminal.warning(f"Override conflict: {conflict.unit} · {conflict.block_key}")
                summary.results.append(result)
            except Exception as error:
                message = f"{unit.key}: {type(error).__name__}: {error}"
                summary.failures.append(message)
                summary.results.append(UnitResult(unit.key, "failed", error=message))
                self.terminal.error(message)

        if self.config.delete_obsolete:
            for relative in obsolete:
                path = self.config.root / relative
                try:
                    path.unlink(missing_ok=True)
                    summary.deleted.append(relative)
                    self.terminal.success(f"Deleted confirmed obsolete output: {relative}")
                except OSError as error:
                    message = f"{relative}: could not delete obsolete output: {error}"
                    summary.failures.append(message)
                    self.terminal.error(message)

        self.manifest.update({
            "version": MANIFEST_VERSION,
            "locale": "pt-BR",
            "engine": self.engine.identifier if self.engine else None,
            "glossary_hash": self.glossary_hash,
            "translation_config_hash": self.translation_config_hash,
        })
        if json.dumps(self.manifest, ensure_ascii=False, sort_keys=True) != manifest_before:
            self.manifest["updated_at"] = datetime.now(timezone.utc).isoformat()
        atomic_json(self.config.manifest_path, self.manifest)
        atomic_json(self.config.memory_path, self.memory)
        summary.report = self._write_report(summary)
        return summary
