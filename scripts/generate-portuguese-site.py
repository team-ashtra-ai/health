#!/usr/bin/env python3
"""Generate Brazilian Portuguese pages and shared partials with local Argos.

Run without arguments for the interactive menu. Automation can use
``--mode incremental``, ``--mode full``, ``--mode dry-run`` or ``--fresh``.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("ARGOS_DEVICE_TYPE", "cpu")
os.environ.setdefault("CUDA_VISIBLE_DEVICES", "")

# Make the documented project-local installation transparent: after setup,
# `python3 scripts/generate-portuguese-site.py` still works in PEP 668 managed
# environments because it hands execution to the ignored Argos virtualenv.
if os.environ.get("SOFIATI_ARGOS_REEXEC") != "1":
    local_candidates = (
        ROOT / ".venv-argos" / "bin" / "python",
        ROOT / ".venv-argos" / "Scripts" / "python.exe",
    )
    local_python = next((path for path in local_candidates if path.exists()), None)
    local_environment = ROOT / ".venv-argos"
    if local_python and Path(sys.prefix).resolve() != local_environment.resolve():
        environment = dict(os.environ, SOFIATI_ARGOS_REEXEC="1")
        os.execve(str(local_python), [str(local_python), str(Path(__file__).resolve()), *sys.argv[1:]], environment)

if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

from pt_translation import ArgosEngine, ArgosUnavailableError, GenerationConfig, PortugueseSiteGenerator  # noqa: E402
from pt_translation.generator import Terminal, atomic_write  # noqa: E402
from pt_translation.validation import validate_site  # noqa: E402


def yes_no(prompt: str, *, default: bool = False) -> bool:
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        answer = input(f"{prompt} {suffix} ").strip().casefold()
        if not answer:
            return default
        if answer in {"y", "yes", "s", "sim"}:
            return True
        if answer in {"n", "no", "não", "nao"}:
            return False
        print("Please answer yes or no.")


def interactive_mode() -> tuple[str, bool, bool]:
    print(
        """
Brazilian Portuguese generation

  1. Incremental update
     Process only new or changed English sources and preserve manual PT edits.

  2. Complete regeneration
     Rebuild every PT page and localized partial from the English source.

  3. Dry run
     Analyse changes without writing files.
""".strip()
    )
    while True:
        choice = input("Choose 1, 2 or 3: ").strip()
        if choice == "1":
            delete = yes_no("If obsolete Portuguese outputs are found, back them up and delete them?", default=False)
            return "incremental", True, delete
        if choice == "2":
            print(
                "\nWARNING: complete regeneration can replace generated Portuguese text.\n"
                "A timestamped backup is always created before any file is changed."
            )
            preserve = yes_no("Preserve Portuguese text detected as a manual override?", default=True)
            if not yes_no("Continue with complete regeneration?", default=False):
                raise KeyboardInterrupt
            delete = yes_no("If obsolete Portuguese outputs are found, delete them after backup?", default=False)
            return "full", preserve, delete
        if choice == "3":
            return "dry-run", True, False
        print("Invalid choice. Please enter 1, 2 or 3.")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("incremental", "full", "dry-run"))
    parser.add_argument("--overrides", choices=("preserve", "discard"), default="preserve")
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Rebuild all Portuguese output from current English, ignoring prior PT overrides and translation memory.",
    )
    parser.add_argument("--yes", action="store_true", help="Confirm non-interactive destructive prompts.")
    parser.add_argument("--install-model", action="store_true", help="Download/install the free Argos en->pt-BR model if needed.")
    parser.add_argument("--delete-obsolete", action="store_true", help="Delete confirmed obsolete PT outputs after backup.")
    parser.add_argument("--no-color", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT, help=argparse.SUPPRESS)
    # Compatibility aliases from the previous generator.
    parser.add_argument("--force", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--use-argos", action="store_true", help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def append_validation_report(report: Path | None, failures: list[str], warnings: list[str]) -> None:
    if report is None:
        return
    content = ["", "## Post-generation validation", ""]
    content.append(f"- Errors: {len(failures)}")
    content.append(f"- Warnings: {len(warnings)}")
    content.append("")
    if failures:
        content.extend(f"- ERROR: {value}" for value in failures)
    if warnings:
        content.extend(f"- REVIEW: {value}" for value in warnings)
    if not failures and not warnings:
        content.append("All structural and language checks passed without warnings.")
    addition = "\n".join(content) + "\n"
    atomic_write(report, report.read_text(encoding="utf-8") + addition)
    latest = report.parent / "latest.md"
    if latest.exists():
        atomic_write(latest, latest.read_text(encoding="utf-8") + addition)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    interactive = args.mode is None and not args.force and not args.fresh
    try:
        if interactive:
            mode, preserve, delete_obsolete = interactive_mode()
        else:
            mode = "full" if (args.force or args.fresh) else (args.mode or "incremental")
            preserve = False if args.fresh else args.overrides == "preserve"
            delete_obsolete = args.delete_obsolete
            if mode == "full" and not args.yes:
                print("Complete regeneration requires --yes in non-interactive mode.", file=sys.stderr)
                return 2
            if delete_obsolete and not args.yes:
                print("Deleting obsolete outputs requires --yes in non-interactive mode.", file=sys.stderr)
                return 2
    except (EOFError, KeyboardInterrupt):
        print("\nPortuguese generation cancelled. No files were changed.")
        return 130

    config = GenerationConfig(
        root=args.root.resolve(),
        mode=mode,
        preserve_overrides=preserve,
        fresh_translation=args.fresh,
        yes=args.yes,
        delete_obsolete=delete_obsolete,
        color=not args.no_color,
    )
    terminal = Terminal(config.color)
    terminal.heading("Argos model check")
    engine = None
    try:
        engine = ArgosEngine.install_model() if args.install_model else ArgosEngine.load_installed()
        terminal.success(
            f"Local model ready: {engine.model.source_name} ({engine.model.source_code}) → "
            f"{engine.model.target_name} ({engine.model.target_code})"
        )
        if engine.model.target_code not in {"pb", "pt_BR", "pt-BR", "pt_br"}:
            terminal.info("Argos provides generic Portuguese; the configured glossary enforces Brazilian terminology.")
    except ArgosUnavailableError as error:
        if mode == "dry-run":
            terminal.warning(str(error))
            terminal.info("Dry run will continue because it does not translate or write content.")
        else:
            terminal.error(str(error))
            return 2
    except Exception as error:
        terminal.error(f"Argos model setup failed: {type(error).__name__}: {error}")
        return 2

    generator = PortugueseSiteGenerator(config, engine, terminal)
    summary = generator.run()

    terminal.heading("Run summary")
    print(f"Pages/partials scanned:       {summary.scanned}")
    print(f"Created:                      {summary.created}")
    print(f"Updated:                      {summary.updated}")
    print(f"Skipped unchanged:            {summary.skipped}")
    print(f"Manual overrides preserved:   {summary.overrides}")
    print(f"Conflicts requiring review:   {len(summary.conflicts)}")
    print(f"Failures:                     {len(summary.failures)}")
    print(f"Obsolete outputs deleted:     {len(summary.deleted)}")
    print(f"Backup:                       {summary.backup.relative_to(config.root) if summary.backup else 'not required'}")
    print(f"Manifest:                     {config.manifest_path.relative_to(config.root)}")
    print(f"Review report:                {summary.report.relative_to(config.root) if summary.report else 'dry run — not written'}")

    if mode == "dry-run":
        terminal.success("Dry run complete. No files were modified.")
        return 0

    terminal.heading("Synchronize shared-component placeholders")
    chrome_build = subprocess.run(
        [sys.executable, str(config.root / "scripts" / "build-shared-chrome.py")],
        cwd=config.root,
        text=True,
    )
    if chrome_build.returncode != 0:
        summary.failures.append("Shared-component placeholder synchronization failed")
        terminal.error("Shared-component placeholders could not be synchronized.")
    else:
        terminal.success("All public pages contain non-rendering shared-component placeholders.")

    terminal.heading("Post-generation validation")
    validation = validate_site(config.root)
    failures = [f"{issue.unit}: {issue.message}" for issue in validation.failures]
    warnings = [f"{issue.unit}: {issue.message}" for issue in validation.warnings]
    append_validation_report(summary.report, failures, warnings)
    if failures:
        terminal.error(f"Validation found {len(failures)} error(s). See the review report.")
    else:
        terminal.success(f"Validated {validation.checked} English/PT pages and shared partials.")
    if warnings:
        terminal.warning(f"Validation recorded {len(warnings)} item(s) for human review.")
    return 1 if summary.failures or failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
