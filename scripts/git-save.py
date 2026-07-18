#!/usr/bin/env python3
"""Create a timestamped Git checkpoint, with an optional push.

Examples:
  python3 scripts/git-save.py
  python3 scripts/git-save.py "Refresh treatment content"
  python3 scripts/git-save.py --push
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def git(*arguments: str) -> None:
    """Run Git in the repository and surface its normal output."""

    subprocess.run(["git", *arguments], cwd=ROOT, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage and commit site changes safely.")
    parser.add_argument("message", nargs="*", help="Optional commit message")
    parser.add_argument("--push", action="store_true", help="Push after committing")
    arguments = parser.parse_args()

    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    message = " ".join(arguments.message).strip() or f"Site update - {timestamp}"

    try:
        git("add", "-A")
        git("commit", "--allow-empty", "-m", message)
        if arguments.push:
            git("push")
    except subprocess.CalledProcessError as error:
        return error.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
