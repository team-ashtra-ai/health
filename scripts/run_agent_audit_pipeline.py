#!/usr/bin/env python3
"""Run the Sofiati audit, screenshot and review pipeline.

Default behavior is audit/review only. Use --fix-safe-labels for the one
deterministic fix this script is allowed to make: public Brand labels become
About labels. Visual header/footer/CSS fixes remain agent-guided because they
must preserve concept-specific design.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "audit" / "reports" / "agent-pipeline-review.md"

STATIC_AUDITS = [
    ("Static site audit", "scripts/audit_static_site.py"),
    ("Internal link audit", "scripts/audit_internal_links.py"),
    ("Layout signature audit", "scripts/audit_layout_signatures.py"),
    ("Ethics/contact audit", "scripts/audit_ethics.py"),
]

SCREENSHOT_RUNS = [
    ("Header/footer/mobile-menu screenshots", "scripts/capture_header_footer_screenshots.py"),
    ("Design QA screenshots", "scripts/run_screenshot_design_qa.py"),
    ("Homepage screenshots", "scripts/capture_homepage_screenshots.py"),
]

PARTIAL_AUDITS = [
    ("Public partial audit", "scripts/audit_public_partials.py"),
]

SAFE_LABEL_REPLACEMENTS = [
    ('aria-label="Brand and Trust"', 'aria-label="About"'),
    ("aria-label='Brand and Trust'", "aria-label='About'"),
    ('aria-label="Brand"', 'aria-label="About"'),
    ("aria-label='Brand'", "aria-label='About'"),
    (">Brand and Trust<", ">About<"),
    (">Brand<", ">About<"),
    (">Brand and education<", ">About and education<"),
]


@dataclass
class StepResult:
    name: str
    command: str
    returncode: int
    output: str


@dataclass
class FixResult:
    path: Path
    replacements: int


def concept_dirs() -> list[Path]:
    return sorted(path for path in (ROOT / "concepts").iterdir() if path.is_dir() and re.match(r"\d{2}-", path.name))


def run_step(name: str, script: str) -> StepResult:
    command = [sys.executable, script]
    print(f"\n==> {name}")
    print("$ " + " ".join(command))
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    status = "PASS" if result.returncode == 0 else f"FAIL ({result.returncode})"
    print(f"<== {name}: {status}")
    return StepResult(name=name, command=" ".join(command), returncode=result.returncode, output=result.stdout)


def apply_safe_label_fixes(dry_run: bool) -> list[FixResult]:
    targets: list[Path] = []
    for concept in concept_dirs():
        targets.extend([concept / "partials" / "footer.html", concept / "sitemap.html"])

    changes: list[FixResult] = []
    for path in targets:
        if not path.exists():
            continue
        original = path.read_text(encoding="utf-8")
        updated = original
        replacements = 0
        for source, target in SAFE_LABEL_REPLACEMENTS:
            count = updated.count(source)
            if count:
                updated = updated.replace(source, target)
                replacements += count
        if updated != original:
            changes.append(FixResult(path=path, replacements=replacements))
            if not dry_run:
                path.write_text(updated, encoding="utf-8")
    return changes


def grep_files(paths: list[Path], pattern: str) -> list[str]:
    regex = re.compile(pattern)
    hits: list[str] = []
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for line_no, line in enumerate(text.splitlines(), start=1):
            if regex.search(line):
                hits.append(f"{path.relative_to(ROOT)}:{line_no}: {line.strip()}")
    return hits


def screenshot_manifest(path: Path, expected: int) -> tuple[str, int | None, int]:
    if not path.exists():
        return ("missing", None, expected)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ("invalid-json", None, expected)
    count = data.get("count")
    return ("present", int(count) if isinstance(count, int) else None, expected)


def build_review(results: list[StepResult], fixes: list[FixResult], args: argparse.Namespace) -> tuple[str, int]:
    footer_paths = [concept / "partials" / "footer.html" for concept in concept_dirs()]
    sitemap_paths = [concept / "sitemap.html" for concept in concept_dirs()]
    footer_label_hits = grep_files(footer_paths, r'Brand and Trust|>Brand<|aria-label="Brand"')
    sitemap_label_hits = grep_files(sitemap_paths, r"Brand and education")

    manifests = [
        ("Header/footer screenshots", ROOT / "audit" / "screenshots" / "manifest.json", 100),
        ("Design QA screenshots", ROOT / "audit" / "screenshots" / "design-qa" / "manifest.json", 500),
        ("Homepage screenshots", ROOT / "final" / "homepage-screenshots" / "manifest.json", 102),
    ]

    remaining_automated_issues = len(footer_label_hits) + len(sitemap_label_hits)
    remaining_automated_issues += sum(1 for result in results if result.returncode != 0)

    lines = [
        "# Agent Audit Pipeline Review",
        "",
        f"Generated: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## Scope",
        "- Runs static audits, public-partial checks and screenshot capture scripts.",
        "- Writes this review report for the next agent pass.",
        "- Applies only deterministic public-label fixes when `--fix-safe-labels` is used.",
        "- Does not auto-edit visual CSS/header/footer layout issues because concept uniqueness requires rendered review.",
        "",
        "## Fix Mode",
        f"- `--fix-safe-labels`: {'on' if args.fix_safe_labels else 'off'}",
        f"- `--dry-run-fixes`: {'on' if args.dry_run_fixes else 'off'}",
        f"- Safe-fix files changed or proposed: {len(fixes)}",
    ]
    for fix in fixes[:80]:
        action = "would update" if args.dry_run_fixes else "updated"
        lines.append(f"  - {action} `{fix.path.relative_to(ROOT)}` ({fix.replacements} replacements)")
    if len(fixes) > 80:
        lines.append(f"  - ... {len(fixes) - 80} more files")

    lines.extend(["", "## Command Results", "", "| Step | Result | Command |", "| --- | --- | --- |"])
    for result in results:
        status = "PASS" if result.returncode == 0 else f"FAIL {result.returncode}"
        lines.append(f"| {result.name} | {status} | `{result.command}` |")

    lines.extend(["", "## Screenshot Manifests", "", "| Set | Status | Count | Expected |", "| --- | --- | --- | --- |"])
    for label, path, expected in manifests:
        skipped = (
            args.skip_screenshots
            or (args.skip_design_qa and label == "Design QA screenshots")
            or (args.skip_homepage_screenshots and label == "Homepage screenshots")
        )
        if skipped:
            lines.append(f"| {label} | skipped | n/a | {expected} |")
            continue
        status, count, expected_count = screenshot_manifest(path, expected)
        count_display = "n/a" if count is None else str(count)
        if count != expected_count:
            remaining_automated_issues += 1
        lines.append(f"| {label} | {status} | {count_display} | {expected_count} |")

    lines.extend(
        [
            "",
            "## Automated Issue Scan",
            f"- Footer Brand-label hits: {len(footer_label_hits)}",
            f"- Sitemap Brand-label hits: {len(sitemap_label_hits)}",
        ]
    )
    for hit in (footer_label_hits + sitemap_label_hits)[:80]:
        lines.append(f"  - `{hit}`")
    if len(footer_label_hits) + len(sitemap_label_hits) > 80:
        lines.append(f"  - ... {len(footer_label_hits) + len(sitemap_label_hits) - 80} more hits")

    lines.extend(
        [
            "",
            "## Human/Agent Review Queue",
            "1. Open the contact sheets in `audit/screenshots/` and `audit/screenshots/design-qa/`.",
            "2. Use `docs/agent-system/19-known-errors-and-regressions.md` for exact concept priorities.",
            "3. Use `docs/agent-system/prompts/prompt-02-fix-header-nav.md` for header/nav fixes.",
            "4. Use `docs/agent-system/prompts/prompt-03-fix-footer.md` for footer fixes.",
            "5. Use `docs/agent-system/prompts/prompt-04-fix-language-switcher.md` for Concepts 3 and 28.",
            "6. After implementation, rerun this script and update `docs/agent-system/20-implementation-task-ledger.md` plus `docs/sofiati-task-ledger.md`.",
            "",
            "## Exit Guidance",
            "- PASS means automated checks found no remaining known machine-detectable issue.",
            "- FAIL means at least one audit command failed, a screenshot manifest is missing/incomplete, or Brand-label hits remain.",
        ]
    )

    status = "PASS" if remaining_automated_issues == 0 else "FAIL"
    lines.insert(2, f"Status: {status}")
    return "\n".join(lines).rstrip() + "\n", remaining_automated_issues


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Sofiati audits, screenshots, review reporting and safe fixes.")
    parser.add_argument("--fix-safe-labels", action="store_true", help="Apply deterministic Brand-to-About public label fixes before auditing.")
    parser.add_argument("--dry-run-fixes", action="store_true", help="Report safe label fixes without writing files.")
    parser.add_argument("--skip-static-audits", action="store_true", help="Skip static Python audit scripts.")
    parser.add_argument("--skip-screenshots", action="store_true", help="Skip all screenshot capture scripts.")
    parser.add_argument("--skip-design-qa", action="store_true", help="Skip the 500-image design QA screenshot pass.")
    parser.add_argument("--skip-homepage-screenshots", action="store_true", help="Skip selector/homepage screenshot capture.")
    parser.add_argument("--skip-public-partial-audit", action="store_true", help="Skip header/menu/footer public partial audit.")
    parser.add_argument("--no-strict", action="store_true", help="Always exit 0 after writing the review report.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if Path.cwd() != ROOT:
        print(f"Running from {ROOT}")

    fixes: list[FixResult] = []
    if args.fix_safe_labels:
        print("\n==> Safe label fixes")
        fixes = apply_safe_label_fixes(dry_run=args.dry_run_fixes)
        verb = "would update" if args.dry_run_fixes else "updated"
        print(f"<== Safe label fixes: {verb} {len(fixes)} files")

    results: list[StepResult] = []
    if not args.skip_static_audits:
        for name, script in STATIC_AUDITS:
            results.append(run_step(name, script))

    if not args.skip_screenshots:
        for name, script in SCREENSHOT_RUNS:
            if args.skip_design_qa and script == "scripts/run_screenshot_design_qa.py":
                continue
            if args.skip_homepage_screenshots and script == "scripts/capture_homepage_screenshots.py":
                continue
            results.append(run_step(name, script))

    if not args.skip_public_partial_audit:
        for name, script in PARTIAL_AUDITS:
            results.append(run_step(name, script))

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    review, issue_count = build_review(results, fixes, args)
    REPORT.write_text(review, encoding="utf-8")
    print(f"\nReview written to {REPORT.relative_to(ROOT)}")

    if args.no_strict:
        return 0
    return 1 if issue_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
