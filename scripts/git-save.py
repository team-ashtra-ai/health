#!/usr/bin/env python3
"""Create a timestamped Git checkpoint and push it.

Examples:
  python3 scripts/git-save.py
  python3 scripts/git-save.py "Refresh treatment content"
  python3 scripts/git-save.py --no-push
  GIT_SAVE_REMOTE_URL=git@github.com:ORG/REPO.git python3 scripts/git-save.py
"""

from __future__ import annotations

import argparse
from datetime import datetime
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def git(*arguments: str, capture: bool = False) -> subprocess.CompletedProcess[str]:
    """Run Git in the repository and surface its normal output."""

    return subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=capture,
    )


def git_output(*arguments: str) -> str:
    return git(*arguments, capture=True).stdout.strip()


def remote_names() -> list[str]:
    output = git_output("remote")
    return [line.strip() for line in output.splitlines() if line.strip()]


def remote_url(name: str) -> str:
    return git_output("remote", "get-url", name)


def ensure_remote() -> str:
    configured_name = os.environ.get("GIT_SAVE_REMOTE", "").strip()
    configured_url = os.environ.get("GIT_SAVE_REMOTE_URL", "").strip()
    if configured_url:
        name = configured_name or "organization"
        if name in remote_names():
            git("remote", "set-url", name, configured_url)
        else:
            git("remote", "add", name, configured_url)
        return name

    names = remote_names()
    for candidate in ("organization", "cloudflare", "production", "deploy"):
        if candidate in names:
            return candidate
    if "origin" in names:
        url = remote_url("origin")
        if "suportesofiati7/health.git" in url:
            raise RuntimeError(
                "origin still points to the old personal repo "
                f"({url}). Set the organization repo once with "
                "GIT_SAVE_REMOTE_URL=git@github.com:ORG/REPO.git python3 scripts/git-save.py"
            )
        return "origin"
    raise RuntimeError(
        "No Git remote is configured. Set GIT_SAVE_REMOTE_URL to the organization repo URL."
    )


def current_branch() -> str:
    return git_output("branch", "--show-current") or "HEAD"


def main() -> int:
    parser = argparse.ArgumentParser(description="Stage and commit site changes safely.")
    parser.add_argument("message", nargs="*", help="Optional commit message")
    parser.add_argument("--push", action="store_true", help="Push after committing (default)")
    parser.add_argument("--no-push", action="store_true", help="Commit without pushing")
    parser.add_argument("--remote", help="Remote to push to; defaults to organization/cloudflare/origin")
    arguments = parser.parse_args()

    timestamp = datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z")
    message = " ".join(arguments.message).strip() or f"Site update - {timestamp}"

    try:
        git("add", "-A")
        git("commit", "--allow-empty", "-m", message)
        if not arguments.no_push:
            remote = arguments.remote or ensure_remote()
            branch = current_branch()
            print(f"Pushing {branch} to {remote}/{branch}...")
            git("push", "-u", remote, f"HEAD:{branch}")
    except subprocess.CalledProcessError as error:
        return error.returncode
    except RuntimeError as error:
        print(error, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
