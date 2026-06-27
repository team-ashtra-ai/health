#!/usr/bin/env python3
"""Audit required Sofiati internal links and generic anchor risks."""

from __future__ import annotations

import sys

import sofiati_complete_system as sofiati


def report_passes(content: str) -> bool:
    marker = "## Status\n"
    if marker not in content:
        return False
    status = content.split(marker, 1)[1].splitlines()[0].strip()
    return status == "PASS"


def main() -> int:
    content = sofiati.internal_link_report()
    sofiati.write_if_changed(sofiati.REPORTS / "internal-link-validation.md", content)
    print("Internal link validation report written.")
    return 0 if report_passes(content) else 1


if __name__ == "__main__":
    sys.exit(main())
