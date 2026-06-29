#!/usr/bin/env python3
"""Create and push an empty commit with a timestamped message."""

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
        description="Create an empty commit and push it to the current remote."
    )
    parser.add_argument(
        "-m",
        "--message",
        default="Empty update",
        help="Optional custom commit message prefix.",
    )
    args = parser.parse_args()

    commit_message = f"{args.message} - {timestamp_comment()}"
    run(["git", "commit", "--allow-empty", "-m", commit_message])
    run(["git", "push"])
    print(commit_message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
