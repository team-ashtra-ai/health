#!/usr/bin/env python3
"""Stage every change, commit with a timestamped message, and push."""

from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(command: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    print("$ " + " ".join(command))
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    if result.stdout:
        print(result.stdout.rstrip())
    if check and result.returncode != 0:
        raise SystemExit(result.returncode)
    return result


def current_branch() -> str:
    result = run(["git", "branch", "--show-current"], check=False)
    branch = result.stdout.strip()
    if not branch:
        print("No current branch found. Are you in detached HEAD?", file=sys.stderr)
        raise SystemExit(1)
    return branch


def has_staged_changes() -> bool:
    return run(["git", "diff", "--cached", "--quiet"], check=False).returncode != 0


def has_upstream() -> bool:
    return (
        run(
            ["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"],
            check=False,
        ).returncode
        == 0
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-m",
        "--message",
        default="Site update",
        help="Commit message prefix. The current date and time are added automatically.",
    )
    args = parser.parse_args()

    branch = current_branch()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"{args.message} - {timestamp}"

    run(["git", "add", "-A"])

    if has_staged_changes():
        run(["git", "commit", "-m", message])
    else:
        print("No file changes to commit.")

    if has_upstream():
        run(["git", "push"])
    else:
        run(["git", "push", "--set-upstream", "origin", branch])

    print(f"Done on branch '{branch}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
