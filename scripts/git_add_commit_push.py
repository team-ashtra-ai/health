#!/usr/bin/env python3
"""Stage all changes, commit with a timestamped message, and push to GitHub."""

from __future__ import annotations

import argparse
import subprocess
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(cmd: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True, check=check)


def timestamp_comment() -> str:
    return datetime.now().strftime("%A, %B %d, %Y %H:%M:%S")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Stage all changes, commit them, and push to the current remote."
    )
    parser.add_argument(
        "-m",
        "--message",
        default=None,
        help="Optional custom commit message prefix.",
    )
    args = parser.parse_args()

    run(["git", "add", "-A"])
    status = run(["git", "status", "--porcelain"]).stdout.strip()
    if not status:
        raise SystemExit("No changes to commit.")

    stamp = timestamp_comment()
    message = args.message or "Update"
    commit_message = f"{message} - {stamp}"

    run(["git", "commit", "-m", commit_message])
    run(["git", "push"])
    print(commit_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
