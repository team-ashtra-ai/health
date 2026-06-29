#!/usr/bin/env python3
import subprocess
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def run(cmd, check=True):
    print("\n$ " + " ".join(cmd))
    p = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    if p.stdout:
        print(p.stdout)
    if p.stderr:
        print(p.stderr, file=sys.stderr)
    if check and p.returncode != 0:
        print(f"\nFAILED: {' '.join(cmd)}", file=sys.stderr)
        raise SystemExit(p.returncode)
    return p

def main():
    print(f"Repo: {ROOT}")

    run(["git", "--version"])
    run(["git", "status", "--short"], check=False)
    run(["git", "remote", "-v"], check=False)

    branch = run(["git", "branch", "--show-current"], check=False).stdout.strip()
    if not branch:
        print("No current branch found. You may be in detached HEAD.", file=sys.stderr)
        run(["git", "status"])
        return 1

    print(f"Current branch: {branch}")

    run(["git", "add", "-A"])

    staged = run(["git", "diff", "--cached", "--quiet"], check=False)
    if staged.returncode == 0:
        print("No changes to commit.")
    else:
        msg = "Update site work " + datetime.now().strftime("%Y-%m-%d %H:%M")
        run(["git", "commit", "-m", msg])

    upstream = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"], check=False)

    if upstream.returncode != 0:
        print("No upstream branch set. Setting upstream now.")
        push = run(["git", "push", "--set-upstream", "origin", branch], check=False)
    else:
        print(f"Upstream: {upstream.stdout.strip()}")
        push = run(["git", "push"], check=False)

    if push.returncode == 0:
        print("\nDONE: changes committed and pushed.")
        return 0

    print("\nPush failed. Running diagnostics...\n", file=sys.stderr)

    run(["git", "status"], check=False)
    run(["git", "remote", "-v"], check=False)
    run(["git", "branch", "-vv"], check=False)

    print("""
Common fixes:

1) If authentication failed:
   gh auth status
   gh auth login
   git push

2) If remote rejected because branch is behind:
   git pull --rebase
   git push

3) If no upstream branch:
   git push --set-upstream origin """ + branch + """

4) If GitHub token/key problem:
   gh auth refresh
""", file=sys.stderr)

    return push.returncode

if __name__ == "__main__":
    raise SystemExit(main())
