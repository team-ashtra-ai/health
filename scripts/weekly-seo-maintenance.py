#!/usr/bin/env python3
"""Refresh generated SEO files and produce a safe weekly maintenance report.

This script deliberately does not rewrite page copy, titles, descriptions, or
image alt text. Those fields need editorial judgement and keyword research;
the underlying SEO validator reports the exact page-level issues for review.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "maintenance" / "weekly-seo.md"


def run_script(script: str) -> tuple[bool, str]:
    """Run a repository Python script and retain concise evidence for the report."""

    result = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script)],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = "\n".join(
        line.strip() for line in (result.stdout + "\n" + result.stderr).splitlines() if line.strip()
    )
    return result.returncode == 0, output or "No output returned."


def changed_public_pages() -> list[str]:
    """List changed HTML routes so the editor knows what to review this week."""

    result = subprocess.run(
        ["git", "status", "--short", "--", "*.html", "pt/*.html", "journal/*.html"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        return []
    return [line[3:] for line in result.stdout.splitlines() if len(line) > 3]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Refresh robots/sitemap and audit SEO without changing editorial content."
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Audit without regenerating robots.txt or sitemap.xml.",
    )
    arguments = parser.parse_args()

    tasks: list[tuple[str, str]] = []
    if not arguments.check_only:
        tasks.extend(
            [
                ("Refresh robots.txt", "generate-robots.py"),
                ("Refresh sitemap.xml and each URL's last-modified date", "generate-sitemap.py"),
            ]
        )
    tasks.extend(
        [
            ("Verify generated discovery files", "check-seo-files.py"),
            ("Audit titles, descriptions, canonical URLs, schema and image alt text", "check-seo-implementation.py"),
        ]
    )

    results: list[tuple[str, bool, str]] = []
    for label, script in tasks:
        passed, output = run_script(script)
        results.append((label, passed, output))

    changed = changed_public_pages()
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Weekly SEO maintenance report",
        "",
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Result",
        "",
    ]
    for label, passed, output in results:
        lines.extend([f"- {'PASS' if passed else 'FAIL'} — {label}: {output}"])
    lines.extend(
        [
            "",
            "## Pages changed since the last commit",
            "",
            *((f"- `{page}`" for page in changed) if changed else ("- None detected.",)),
            "",
            "## Editorial review boundary",
            "",
            "This maintenance run refreshes generated discovery files and identifies SEO issues. "
            "It never fabricates or rewrites titles, descriptions, body copy, or alt text. "
            "Review the linked SEO validation report before making editorial changes.",
            "",
        ]
    )
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {REPORT.relative_to(ROOT)}")
    return 0 if all(passed for _, passed, _ in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
