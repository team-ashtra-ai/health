#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "docs" / "script-runs"
REPORT_DIR = ROOT / "audit" / "reports"
MASTER = REPORT_DIR / "MASTER-ALL-ISSUES.md"

PYTHON = sys.executable

SAFE_FIXERS = [
    "scripts/fix_language_toggle_runtime.py",
    "scripts/refactor_header_system.py",
]

AUDITS = [
    "scripts/audit_static_site.py",
    "scripts/audit_internal_links.py",
    "scripts/audit_layout_signatures.py",
    "scripts/audit_public_partials.py",
    "scripts/audit_header_interactions.py",
    "scripts/audit_rendered_concepts.py",
]

SCREENSHOTS = [
    "scripts/capture_homepage_screenshots.py",
    "scripts/capture_header_footer_screenshots.py",
    "scripts/run_screenshot_design_qa.py",
]

DOCS = [
    "scripts/generate_agent_brief_system.py",
]

WIDE_FIXERS = [
    "scripts/restore_global_widgets.py",
    "scripts/refactor_sofiati_cookie_notices.py",
    "scripts/refactor_public_partials.py",
    "scripts/repair_screenshot_design_qa.py",
]

DANGEROUS_BIG_SYSTEM = [
    "scripts/sofiati_complete_system.py",
]


def run_command(label: str, command: list[str], timeout: int = 900) -> dict:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_path = LOG_DIR / f"{label}.txt"

    print(f"\n=== {label} ===")
    print(" ".join(command))

    with log_path.open("w", encoding="utf-8") as log:
        log.write(f"$ {' '.join(command)}\n\n")
        try:
            result = subprocess.run(
                command,
                cwd=ROOT,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                check=False,
            )
            output = result.stdout or ""
            print(output)
            log.write(output)
            return {
                "label": label,
                "command": " ".join(command),
                "returncode": result.returncode,
                "log": str(log_path.relative_to(ROOT)),
                "timed_out": False,
            }
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
            print(output)
            print(f"TIMEOUT after {timeout}s")
            log.write(output)
            log.write(f"\nTIMEOUT after {timeout}s\n")
            return {
                "label": label,
                "command": " ".join(command),
                "returncode": 124,
                "log": str(log_path.relative_to(ROOT)),
                "timed_out": True,
            }


def script_exists(script: str) -> bool:
    return (ROOT / script).exists()


def run_script_group(title: str, scripts: list[str], prefix: str, timeout: int, results: list[dict]) -> None:
    print(f"\n\n######## {title} ########")
    for index, script in enumerate(scripts, 1):
        if not script_exists(script):
            print(f"SKIP missing: {script}")
            results.append({
                "label": f"{prefix}_{index:02d}_{Path(script).stem}",
                "command": f"{PYTHON} {script}",
                "returncode": 127,
                "log": "",
                "timed_out": False,
                "missing": True,
            })
            continue

        label = f"{prefix}_{index:02d}_{Path(script).stem}"
        results.append(run_command(label, [PYTHON, script], timeout=timeout))


def kill_stale_browsers(results: list[dict]) -> None:
    patterns = [
        "chrome.*remote-debugging",
        "chromium.*remote-debugging",
        "google-chrome.*remote-debugging",
        "python3 -m http.server",
    ]
    for i, pattern in enumerate(patterns, 1):
        results.append(
            run_command(
                f"00_cleanup_{i}",
                ["bash", "-lc", f"pkill -f '{pattern}' || true"],
                timeout=30,
            )
        )


def git_snapshot(results: list[dict], label: str) -> None:
    results.append(run_command(f"{label}_git_status", ["git", "status", "--short"], timeout=30))
    results.append(run_command(f"{label}_git_diff_stat", ["git", "diff", "--stat"], timeout=30))


def collect_reports(results: list[dict]) -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    markdown_reports = sorted(
        path for path in REPORT_DIR.glob("*.md")
        if path.name != MASTER.name
    )

    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    git_status = subprocess.run(
        ["git", "status", "--short"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    ).stdout

    git_diff_stat = subprocess.run(
        ["git", "diff", "--stat"],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    ).stdout

    with MASTER.open("w", encoding="utf-8") as out:
        out.write("# Sofiati Master Audit, Fix, Screenshot and Issue Report\n\n")
        out.write(f"Generated: {now}\n\n")

        out.write("## Run Summary\n\n")
        out.write("| Step | Return | Log | Command |\n")
        out.write("| --- | ---: | --- | --- |\n")
        for result in results:
            missing = " missing" if result.get("missing") else ""
            timeout = " timeout" if result.get("timed_out") else ""
            status = f"{result.get('returncode')}{missing}{timeout}"
            out.write(
                f"| {result.get('label')} | {status} | "
                f"`{result.get('log', '')}` | `{result.get('command')}` |\n"
            )

        out.write("\n## Git Status After Run\n\n")
        out.write("```text\n")
        out.write(git_status.strip() or "clean")
        out.write("\n```\n\n")

        out.write("## Git Diff Stat After Run\n\n")
        out.write("```text\n")
        out.write(git_diff_stat.strip() or "no diff")
        out.write("\n```\n\n")

        out.write("## Quick Remaining-Issue Scan\n\n")
        out.write("This section is a rough grep-style scan. The detailed reports below are the source of truth.\n\n")
        out.write("```text\n")
        for report in markdown_reports:
            text = report.read_text(encoding="utf-8", errors="replace")
            hits = []
            for line in text.splitlines():
                low = line.lower()
                if any(token in low for token in [
                    "issues found",
                    "critical",
                    " high ",
                    "| high |",
                    "| critical |",
                    "failed",
                    "failure",
                    "error",
                    "overflow",
                    "did not",
                    "missing",
                    "not visible",
                    "needs",
                    "risk",
                ]):
                    hits.append(line)
            if hits:
                out.write(f"\n--- {report.name} ---\n")
                out.write("\n".join(hits[:120]))
                out.write("\n")
        out.write("\n```\n\n")

        out.write("## Combined Detailed Reports\n\n")
        for report in markdown_reports:
            out.write(f"\n\n---\n\n# Included Report: {report.name}\n\n")
            out.write(report.read_text(encoding="utf-8", errors="replace"))
            out.write("\n")

    print(f"\nMaster report written to {MASTER.relative_to(ROOT)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run full Sofiati fixes, audits, screenshots and one master report.")
    parser.add_argument("--no-fixes", action="store_true", help="Do not run safe fixers.")
    parser.add_argument("--no-screenshots", action="store_true", help="Do not regenerate screenshots.")
    parser.add_argument("--docs", action="store_true", help="Regenerate agent brief docs too.")
    parser.add_argument("--wide-fixes", action="store_true", help="Run broader fixer scripts after safe fixers.")
    parser.add_argument("--dangerous-big-system", action="store_true", help="Also run sofiati_complete_system.py. Use only after committing.")
    args = parser.parse_args()

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []

    kill_stale_browsers(results)
    git_snapshot(results, "01_before")

    if not args.no_fixes:
        run_script_group("SAFE FIXERS", SAFE_FIXERS, "02_safe_fix", 600, results)

    if args.wide_fixes:
        run_script_group("WIDE FIXERS", WIDE_FIXERS, "03_wide_fix", 900, results)

    if args.dangerous_big_system:
        run_script_group("DANGEROUS BIG SYSTEM", DANGEROUS_BIG_SYSTEM, "04_big_system", 1200, results)

    run_script_group("AUDITS", AUDITS, "05_audit", 1200, results)

    if not args.no_screenshots:
        run_script_group("SCREENSHOTS AND VISUAL QA", SCREENSHOTS, "06_screenshots", 1800, results)

    if args.docs:
        run_script_group("DOCS", DOCS, "07_docs", 900, results)

    git_snapshot(results, "08_after")
    collect_reports(results)

    failing = [r for r in results if r.get("returncode") not in (0, None)]
    if failing:
        print("\nSome steps failed or timed out. Check the master report and logs.")
        return 1

    print("\nFull sweep completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
