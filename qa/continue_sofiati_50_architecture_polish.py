#!/usr/bin/env python3
"""Resumable Sofiati 50 architecture rebuild runner."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
NODE_SCRIPT = ROOT / "qa" / "rebuild_sofiati_50_architecture.mjs"
PROGRESS_PATH = ROOT / "docs" / "script-runs" / "sofiati-50-architecture-progress.json"
CONCEPTS_ROOT = ROOT / "concepts"


def concept_ids() -> list[str]:
    return sorted(
        path.name
        for path in CONCEPTS_ROOT.iterdir()
        if path.is_dir() and len(path.name) > 3 and path.name[:2].isdigit()
    )


def load_progress() -> dict[str, dict]:
    if not PROGRESS_PATH.exists():
        return {}
    return json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))


def run_node(*args: str) -> None:
    cmd = ["node", str(NODE_SCRIPT), *args]
    print("running:", " ".join(cmd), flush=True)
    subprocess.run(cmd, cwd=ROOT, check=True)


def ensure_ledger() -> dict[str, dict]:
    progress = load_progress()
    if progress:
        return progress
    run_node("--validate-only")
    return load_progress()


def incomplete_concepts(progress: dict[str, dict]) -> list[str]:
    ordered = concept_ids()
    return [
        concept_id
        for concept_id in ordered
        if progress.get(concept_id, {}).get("status") != "complete"
    ]


def print_status(progress: dict[str, dict]) -> None:
    ordered = concept_ids()
    counts: dict[str, int] = {}
    for concept_id in ordered:
        status = progress.get(concept_id, {}).get("status", "not-started")
        counts[status] = counts.get(status, 0) + 1
    print("Sofiati 50 architecture status")
    for status in ["complete", "in-progress", "blocked", "not-started"]:
        print(f"- {status}: {counts.get(status, 0)}")
    next_items = incomplete_concepts(progress)[:5]
    print("- next:", ", ".join(next_items) if next_items else "none")


def run_batch(size: int) -> None:
    progress = ensure_ledger()
    targets = incomplete_concepts(progress)[:size]
    if not targets:
        print("No incomplete concepts found. Running validation report.")
        run_node("--validate-only")
        return
    for concept_id in targets:
        run_node("--concept", concept_id)
    run_node("--validate-only")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--status", action="store_true")
    group.add_argument("--next", action="store_true")
    group.add_argument("--batch", type=int)
    group.add_argument("--all", action="store_true")
    group.add_argument("--concept")
    group.add_argument("--validate-only", action="store_true")
    group.add_argument("--report", action="store_true")
    args = parser.parse_args()

    try:
        if args.status:
            print_status(ensure_ledger())
            return 0
        if args.next:
            run_batch(1)
            print_status(load_progress())
            return 0
        if args.batch is not None:
            if args.batch < 1:
                raise SystemExit("--batch must be at least 1")
            run_batch(args.batch)
            print_status(load_progress())
            return 0
        if args.all:
            run_node("--all")
            print_status(load_progress())
            return 0
        if args.concept:
            if args.concept not in concept_ids():
                raise SystemExit(f"Unknown concept: {args.concept}")
            run_node("--concept", args.concept)
            run_node("--validate-only")
            print_status(load_progress())
            return 0
        if args.validate_only:
            run_node("--validate-only")
            print_status(load_progress())
            return 0
        if args.report:
            run_node("--report")
            print_status(load_progress())
            return 0
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}", file=sys.stderr)
        return exc.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
