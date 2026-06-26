#!/usr/bin/env python3
"""Rendered audit for Sofiati public header and top navigation behavior."""

from __future__ import annotations

import json
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


REPORT_JSON = ROOT / "audit" / "reports" / "header-interaction-audit.json"
REPORT_MD = ROOT / "audit" / "reports" / "header-interaction-audit.md"
PRIMARY = ["Home", "About", "Care", "Laser", "Skin", "Results", "Consultation", "Contact"]
VIEWPORTS = [
    ("mobile-390", 390, 844, True),
    ("desktop-1024", 1024, 900, False),
    ("desktop-1366", 1366, 960, False),
]


def install_error_capture(client: DevToolsClient) -> None:
    source = r"""
(() => {
  window.__sofiatiHeaderErrors = [];
  window.addEventListener("error", (event) => {
    window.__sofiatiHeaderErrors.push(event.message || "window error");
  });
  window.addEventListener("unhandledrejection", (event) => {
    window.__sofiatiHeaderErrors.push(String(event.reason || "unhandled rejection"));
  });
  const originalError = console.error;
  console.error = (...args) => {
    window.__sofiatiHeaderErrors.push(args.map((value) => String(value)).join(" "));
    originalError.apply(console, args);
  };
})();
"""
    client.command("Page.addScriptToEvaluateOnNewDocument", {"source": source})


def evaluate(client: DevToolsClient, concept: str, viewport: str, width: int, height: int, mobile: bool) -> dict[str, object]:
    client.command(
        "Emulation.setDeviceMetricsOverride",
        {
            "width": width,
            "height": height,
            "deviceScaleFactor": 1,
            "mobile": mobile,
        },
    )
    client.command("Page.navigate", {"url": f"{BASE_URL}/concepts/{concept}/index.html"})
    client.wait_for_event("Page.loadEventFired", timeout=30)
    time.sleep(1.0)
    expression = r"""
(async () => {
  const required = __PRIMARY__;
  const visible = (node) => {
    if (!node) return false;
    const style = getComputedStyle(node);
    const rect = node.getBoundingClientRect();
    return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
  };
  const inBounds = (node) => {
    if (!node) return false;
    const rect = node.getBoundingClientRect();
    return rect.left >= -1 && rect.right <= window.innerWidth + 1;
  };
  const wait = (ms = 100) => new Promise((resolve) => window.setTimeout(resolve, ms));
  const pageWidth = Math.max(document.documentElement.scrollWidth, document.body.scrollWidth);
  const utility = document.querySelector(".public-utility.status-banner");
  const utilityName = utility?.querySelector(".public-utility-name");
  const utilityLanguage = utility?.querySelector(".public-language");
  const pt = utility?.querySelector('[data-lang-switch="pt"]');
  const en = utility?.querySelector('[data-lang-switch="en"]');
  const header = document.querySelector(".public-header");
  const cta = document.querySelector(".header-consultation");
  const menuButton = document.querySelector("[data-menu-toggle]");
  const navLinks = Array.from(document.querySelectorAll(".public-header .desktop-nav a")).filter(visible);
  const navLabels = navLinks.map((node) => (node.textContent || "").trim());
  const navRows = new Set(navLinks.map((node) => Math.round(node.getBoundingClientRect().top))).size;
  const contact = navLinks.find((node) => (node.textContent || "").trim() === "Contact");
  let ptActive = false;
  let enActive = false;
  if (pt && en) {
    pt.click();
    await wait(180);
    ptActive = pt.getAttribute("aria-pressed") === "true" && document.documentElement.lang === "pt-BR";
    en.click();
    await wait(180);
    enActive = en.getAttribute("aria-pressed") === "true" && document.documentElement.lang === "en";
  }
  const menu = document.querySelector("#mobile-menu");
  let menuMetrics = null;
  if (__MOBILE__) {
    menuButton?.click();
    await wait(160);
    const close = menu?.querySelector("[data-menu-close]");
    const mobileCta = menu?.querySelector(".public-mobile-cta");
    menuMetrics = {
      triggerVisible: visible(menuButton),
      open: Boolean(menu?.classList.contains("is-open") && menu?.getAttribute("aria-hidden") === "false" && visible(menu)),
      closeVisible: visible(close),
      ctaVisible: visible(mobileCta),
      languageInBounds: inBounds(menu?.querySelector(".public-language")),
      linkCount: Array.from(menu?.querySelectorAll(".public-mobile-primary a") || []).filter(visible).length,
    };
    close?.click();
    await wait(120);
    menuMetrics.closed = Boolean(!menu?.classList.contains("is-open") && menu?.getAttribute("aria-hidden") === "true");
  }
  return {
    viewport: "__VIEWPORT__",
    pageOverflow: Math.round(pageWidth - window.innerWidth),
    utilityVisible: visible(utility),
    utilityName: (utilityName?.textContent || "").trim(),
    utilityNameVisible: visible(utilityName),
    utilityLanguageVisible: visible(utilityLanguage),
    utilityLanguageInBounds: inBounds(utilityLanguage),
    languageToggleWorks: ptActive && enActive,
    headerVisible: visible(header),
    ctaVisible: visible(cta),
    menuButtonVisible: visible(menuButton),
    navLabels,
    navRows,
    contactVisible: visible(contact),
    menu: menuMetrics,
    errors: window.__sofiatiHeaderErrors || [],
    required,
  };
})()
""".replace("__PRIMARY__", json.dumps(PRIMARY)).replace("__MOBILE__", "true" if mobile else "false").replace("__VIEWPORT__", viewport)
    result = client.command("Runtime.evaluate", {"expression": expression, "awaitPromise": True, "returnByValue": True}, timeout=30)
    value = result.get("result", {}).get("result", {}).get("value")
    if not isinstance(value, dict):
        raise RuntimeError(f"No header metrics for {concept} {viewport}")
    issues: list[dict[str, str]] = []
    if value.get("pageOverflow", 0) > 2:
        issues.append({"severity": "critical", "kind": "page-overflow", "detail": f"Page overflow {value['pageOverflow']}px"})
    if not value.get("utilityVisible"):
        issues.append({"severity": "critical", "kind": "utility-hidden", "detail": "Utility bar is not visible"})
    if value.get("utilityName") != "Franciele Sofiati" or not value.get("utilityNameVisible"):
        issues.append({"severity": "high", "kind": "utility-name", "detail": f"Utility name is {value.get('utilityName')!r}"})
    if not value.get("utilityLanguageVisible") or not value.get("utilityLanguageInBounds"):
        issues.append({"severity": "critical", "kind": "utility-language-bounds", "detail": "Utility language switcher is hidden or out of bounds"})
    if not value.get("languageToggleWorks"):
        issues.append({"severity": "high", "kind": "language-toggle", "detail": "EN/PT controls did not update active language state"})
    if not value.get("headerVisible"):
        issues.append({"severity": "critical", "kind": "header-hidden", "detail": "Header is not visible"})
    if not value.get("ctaVisible"):
        issues.append({"severity": "high", "kind": "header-cta-hidden", "detail": "Consultation CTA is not visible"})
    if not mobile:
        if value.get("navLabels") != PRIMARY:
            issues.append({"severity": "critical", "kind": "desktop-nav-labels", "detail": "Desktop nav labels are incomplete or out of order"})
        if value.get("navRows") != 1:
            issues.append({"severity": "critical", "kind": "desktop-nav-wrap", "detail": f"Desktop nav rows: {value.get('navRows')}"})
        if not value.get("contactVisible"):
            issues.append({"severity": "critical", "kind": "desktop-contact-hidden", "detail": "Contact link is not visible"})
        if value.get("menuButtonVisible"):
            issues.append({"severity": "high", "kind": "desktop-menu-button-visible", "detail": "Desktop menu button is visible"})
    menu = value.get("menu")
    if mobile and isinstance(menu, dict):
        if not menu.get("triggerVisible"):
            issues.append({"severity": "critical", "kind": "mobile-menu-trigger-hidden", "detail": "Menu trigger is not visible"})
        if not menu.get("open"):
            issues.append({"severity": "critical", "kind": "mobile-menu-open", "detail": "Menu did not open"})
        if not menu.get("closed"):
            issues.append({"severity": "critical", "kind": "mobile-menu-close", "detail": "Menu did not close"})
        if not menu.get("closeVisible"):
            issues.append({"severity": "high", "kind": "mobile-close-hidden", "detail": "Close control is not visible"})
        if not menu.get("ctaVisible"):
            issues.append({"severity": "high", "kind": "mobile-cta-hidden", "detail": "Mobile Consultation CTA is not visible"})
        if not menu.get("languageInBounds"):
            issues.append({"severity": "critical", "kind": "mobile-language-bounds", "detail": "Mobile language switcher is out of bounds"})
        if menu.get("linkCount") != len(PRIMARY):
            issues.append({"severity": "critical", "kind": "mobile-nav-count", "detail": f"Mobile links: {menu.get('linkCount')}"})
    if value.get("errors"):
        issues.append({"severity": "high", "kind": "browser-errors", "detail": "; ".join(value["errors"][:3])})
    value["issues"] = issues
    return value


def write_reports(results: list[dict[str, object]]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(results, indent=2), encoding="utf-8")
    issue_rows = []
    for result in results:
        metrics = result["metrics"]
        assert isinstance(metrics, dict)
        for issue in metrics.get("issues", []):
            issue_rows.append((result["concept"], result["viewport"], issue["severity"], issue["kind"], issue["detail"]))
    lines = [
        "# Header Interaction Audit",
        "",
        f"Concept viewport checks: {len(results)}",
        f"Issues found: {len(issue_rows)}",
        "",
        "This audit loads each concept homepage at mobile 390px, desktop 1024px and desktop 1366px. It checks the utility bar, canonical name, EN/PT active state, desktop nav row count, Contact visibility, Consultation CTA, mobile menu open/close, mobile CTA, overflow and captured browser errors.",
        "",
        "| Concept | Viewport | Severity | Issue | Detail |",
        "| --- | --- | --- | --- | --- |",
    ]
    for concept, viewport, severity, kind, detail in issue_rows:
        lines.append(f"| {concept} | {viewport} | {severity} | {kind} | {detail} |")
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    server = ensure_server()
    chrome = chrome_binary()
    chrome_process = None
    client = None
    results: list[dict[str, object]] = []
    try:
        with tempfile.TemporaryDirectory(prefix="sofiati-header-audit-", ignore_cleanup_errors=True) as tmp:
            chrome_process = ensure_chrome(chrome, Path(tmp) / "chrome-profile")
            client = DevToolsClient(websocket_url())
            client.command("Page.enable")
            install_error_capture(client)
            total = len(CONCEPTS) * len(VIEWPORTS)
            done = 0
            for concept in CONCEPTS:
                for viewport, width, height, mobile in VIEWPORTS:
                    metrics = evaluate(client, concept, viewport, width, height, mobile)
                    results.append({"concept": concept, "viewport": viewport, "metrics": metrics})
                    done += 1
                    print(f"[{done:03d}/{total:03d}] {concept} {viewport}: {len(metrics['issues'])} issues", flush=True)
    finally:
        if client:
            client.close()
        if chrome_process:
            chrome_process.terminate()
        if server:
            server.terminate()
    write_reports(results)
    issue_count = sum(len(result["metrics"].get("issues", [])) for result in results)
    print(f"Header interaction audit written to {REPORT_MD.relative_to(ROOT)}")
    return 1 if issue_count else 0


if __name__ == "__main__":
    raise SystemExit(main())
