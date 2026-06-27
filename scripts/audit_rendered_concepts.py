#!/usr/bin/env python3
"""Measure rendered responsive behavior for all Sofiati concepts.

This is an audit-only script. It starts the local static server and Chrome,
loads each concept homepage at several viewport widths, opens the mobile menu
where relevant, and writes JSON/Markdown diagnostics.
"""

from __future__ import annotations

import json
import argparse
import tempfile
import time
from pathlib import Path

from capture_homepage_screenshots import (
    BASE_URL,
    CONCEPTS,
    DevToolsClient,
    ROOT,
    chrome_binary,
    ensure_chrome,
    ensure_server,
    websocket_url,
)


REPORT_JSON = ROOT / "audit" / "reports" / "rendered-responsive-diagnostic.json"
REPORT_MD = ROOT / "audit" / "reports" / "rendered-responsive-diagnostic.md"

VIEWPORTS = [
    ("mobile-360", 360, 844, True),
    ("mobile-390", 390, 844, True),
    ("tablet-768", 768, 960, True),
    ("desktop-1024", 1024, 900, False),
    ("desktop-1366", 1366, 960, False),
    ("desktop-1440", 1440, 1100, False),
]


def evaluate_page(client: DevToolsClient, folder: str, viewport: str, width: int, height: int, mobile: bool, settle: float) -> dict[str, object]:
    client.command(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile,
        },
    )
    client.command("Page.navigate", {"url": f"{BASE_URL}/concepts/{folder}/index.html"})
    client.wait_for_event("Page.loadEventFired", timeout=30)
    time.sleep(settle)

    expression = r"""
(() => {
  const visible = (node) => {
    if (!node) return false;
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
  };
  const rectData = (node) => {
    if (!node) return null;
    const rect = node.getBoundingClientRect();
    return {left: rect.left, right: rect.right, top: rect.top, bottom: rect.bottom, width: rect.width, height: rect.height};
  };
  const viewportWidth = window.innerWidth;
  const pageWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
  const header = document.querySelector('.public-header, .site-header');
  const navLinks = Array.from(document.querySelectorAll('.public-header .desktop-nav a, .site-header .desktop-nav a')).filter(visible);
  const navRows = new Set(navLinks.map((node) => Math.round(node.getBoundingClientRect().top))).size;
  const headerCta = document.querySelector('.header-consultation');
  const language = Array.from(document.querySelectorAll('.public-language, .language-switcher')).filter(visible);
  const languageOutOfBounds = language.filter((node) => {
    const rect = node.getBoundingClientRect();
    return rect.left < -1 || rect.right > viewportWidth + 1;
  }).length;
  const footer = document.querySelector('.public-footer, .site-footer');
  const shell = document.querySelector('.public-footer-shell') || footer;
  const copyright = Array.from(document.querySelectorAll('.footer-bottom-row p, .public-footer p, .site-footer p')).find((node) => /2026|rights reserved/i.test(node.textContent || ''));
  const shellRect = shell ? shell.getBoundingClientRect() : null;
  const copyrightRect = copyright ? copyright.getBoundingClientRect() : null;
  const copyrightDelta = shellRect && copyrightRect ? Math.round((copyrightRect.left + copyrightRect.width / 2) - (shellRect.left + shellRect.width / 2)) : null;
  const whatsApp = document.querySelector('a[href*="wa.me/5543991043536"]');
  const form = document.querySelector('form.consultation-form, [data-partial-mount="consultation-form"] form, [data-partial-mount="consultation-form"]');
  const menu = document.querySelector('#mobile-menu');
  let menuMetrics = null;
  if (menu) {
    menu.classList.add('is-open');
    menu.setAttribute('aria-hidden', 'false');
    document.body.classList.add('public-menu-locked');
    const menuRect = menu.getBoundingClientRect();
    const menuLanguage = Array.from(menu.querySelectorAll('.public-language, .language-switcher')).filter(visible);
    const close = menu.querySelector('[data-menu-close], .public-menu-close');
    menuMetrics = {
      visible: visible(menu),
      right: Math.round(menuRect.right),
      width: Math.round(menuRect.width),
      overflowRight: Math.round(Math.max(0, menuRect.right - viewportWidth)),
      languageOutOfBounds: menuLanguage.filter((node) => {
        const rect = node.getBoundingClientRect();
        return rect.left < -1 || rect.right > viewportWidth + 1;
      }).length,
      closeVisible: visible(close),
      linkCount: Array.from(menu.querySelectorAll('a')).filter(visible).length
    };
    menu.classList.remove('is-open');
    menu.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('public-menu-locked');
  }
  return {
    viewport: '__VIEWPORT__',
    width: viewportWidth,
    pageOverflow: Math.round(pageWidth - viewportWidth),
    headerVisible: visible(header),
    headerOverflowRight: header ? Math.round(Math.max(0, header.getBoundingClientRect().right - viewportWidth)) : null,
    navLinkCount: navLinks.length,
    navRows,
    headerCtaVisible: visible(headerCta),
    languageCount: language.length,
    languageOutOfBounds,
    footerVisible: visible(footer),
    copyrightDelta,
    whatsAppVisible: visible(whatsApp),
    formVisibleOrMounted: visible(form),
    menu: menuMetrics
  };
})()
""".replace("__VIEWPORT__", viewport)
    result = client.command("Runtime.evaluate", {"expression": expression, "returnByValue": True}, timeout=30)
    value = result.get("result", {}).get("result", {}).get("value")
    if not isinstance(value, dict):
        raise RuntimeError(f"No rendered metrics for {folder} {viewport}")
    issues: list[dict[str, object]] = []
    if value["pageOverflow"] and value["pageOverflow"] > 2:
        issues.append({"kind": "responsive-overflow", "severity": "critical", "detail": f"Page overflow {value['pageOverflow']}px"})
    if width >= 1024 and value["navLinkCount"] and value["navRows"] and value["navRows"] > 1:
        issues.append({"kind": "desktop-nav-wrap", "severity": "critical", "detail": f"Desktop nav uses {value['navRows']} rows"})
    if width >= 1024 and not value["headerCtaVisible"]:
        issues.append({"kind": "header-cta-missing", "severity": "high", "detail": "Header consultation CTA is not visible"})
    if value["languageOutOfBounds"]:
        issues.append({"kind": "language-overflow", "severity": "critical", "detail": f"{value['languageOutOfBounds']} language switcher elements exceed viewport"})
    if width >= 1024 and isinstance(value["copyrightDelta"], int) and abs(value["copyrightDelta"]) > 40:
        issues.append({"kind": "footer-copyright-offset", "severity": "high", "detail": f"Copyright center delta {value['copyrightDelta']}px"})
    menu = value.get("menu")
    if mobile and isinstance(menu, dict):
        if menu.get("overflowRight", 0) > 2:
            issues.append({"kind": "mobile-menu-overflow", "severity": "critical", "detail": f"Menu overflow {menu['overflowRight']}px"})
        if menu.get("languageOutOfBounds", 0):
            issues.append({"kind": "mobile-language-overflow", "severity": "critical", "detail": "Mobile menu language switcher exceeds viewport"})
        if not menu.get("closeVisible"):
            issues.append({"kind": "mobile-menu-close-hidden", "severity": "high", "detail": "Mobile menu close control is not visible"})
    if not value["whatsAppVisible"]:
        issues.append({"kind": "whatsapp-not-visible", "severity": "medium", "detail": "WhatsApp link not visible or not mounted"})
    value["issues"] = issues
    return value


def write_reports(results: list[dict[str, object]]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    issue_rows = []
    for result in results:
        for issue in result["metrics"].get("issues", []):
            issue_rows.append((result["concept"], result["viewport"], issue["severity"], issue["kind"], issue["detail"]))
    lines = [
        "# Rendered Responsive Diagnostic",
        "",
        f"Concept viewport checks: {len(results)}",
        f"Issues found: {len(issue_rows)}",
        "",
        "This audit measures rendered homepages at 360, 390, 768, 1024, 1366 and 1440px widths. It checks horizontal overflow, desktop nav wrapping, header CTA visibility, language switcher bounds, footer copyright centering, WhatsApp mounting and mobile-menu containment.",
        "",
        "| Concept | Viewport | Severity | Issue | Detail |",
        "| --- | --- | --- | --- | --- |",
    ]
    for concept, viewport, severity, kind, detail in issue_rows:
        lines.append(f"| {concept} | {viewport} | {severity} | {kind} | {detail} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit rendered responsive behavior for Sofiati concepts.")
    parser.add_argument("--start-at", default="", help="Start at a concept folder such as 30-method.")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of concepts audited.")
    parser.add_argument("--settle", type=float, default=0.55, help="Seconds to wait after page load.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    server = ensure_server()
    chrome = chrome_binary()
    chrome_process = None
    client = None
    results: list[dict[str, object]] = []
    try:
        with tempfile.TemporaryDirectory(prefix="sofiati-rendered-audit-", ignore_cleanup_errors=True) as tmp:
            chrome_process = ensure_chrome(chrome, Path(tmp) / "chrome-profile")
            client = DevToolsClient(websocket_url())
            client.command("Page.enable")
            concepts = list(CONCEPTS)
            if args.start_at:
                concepts = [concept for concept in concepts if concept >= args.start_at]
            if args.limit:
                concepts = concepts[: args.limit]
            total = len(concepts) * len(VIEWPORTS)
            done = 0
            for folder in concepts:
                for viewport, width, height, mobile in VIEWPORTS:
                    metrics = evaluate_page(client, folder, viewport, width, height, mobile, args.settle)
                    done += 1
                    results.append({"concept": folder, "viewport": viewport, "metrics": metrics})
                    print(f"[{done:03d}/{total:03d}] {folder} {viewport}: {len(metrics['issues'])} issues", flush=True)
    except KeyboardInterrupt:
        print("Interrupted; writing partial rendered diagnostic report.", flush=True)
    finally:
        if client:
            client.close()
        if chrome_process:
            chrome_process.terminate()
        if server:
            server.terminate()
    write_reports(results)
    issue_count = sum(len(result["metrics"].get("issues", [])) for result in results)
    print(f"Rendered responsive diagnostic written to {REPORT_MD.relative_to(ROOT)}")
    return 1 if issue_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
