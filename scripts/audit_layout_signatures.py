#!/usr/bin/env python3
"""Audit repeated Sofiati section-order and layout-signature sequences."""

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
    reports = {
        "global-duplicate-layout-audit.md": sofiati.layout_report(),
        "design-differentiation-audit.md": sofiati.design_diff_report(),
        "ux-storytelling-audit.md": sofiati.ux_storytelling_report(),
    }
    failed = False
    for filename, content in reports.items():
        sofiati.write_if_changed(sofiati.REPORTS / filename, content)
        if not report_passes(content):
            failed = True
    print("Layout signature audit reports written.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
