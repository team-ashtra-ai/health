#!/usr/bin/env python3
"""
Mobile visual QA screenshot/audit generator for Sofiati concept sites.

It captures, at mobile viewport:
- full page
- header/nav
- open mobile menu if a toggle is found
- hero
- widgets/floating actions
- footer

It also writes a Markdown + JSON audit report flagging:
- broken vertical brand text
- missing/separate EN/PT banner
- missing nav links
- missing footer sitemap links
- public concept titles in H1
- debug widget labels
- duplicate WhatsApp controls
- repeated/placeholder-like structure clues
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import time
import zipfile
import threading
from dataclasses import dataclass, asdict
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any


MAIN_LINKS = [
    "Home",
    "About",
    "Care",
    "Laser",
    "Skin",
    "Results",
    "Journal",
    "Contact",
]

FOOTER_LINKS = [
    "Home",
    "About",
    "Care",
    "Laser",
    "Skin",
    "Results",
    "Journal",
    "Contact",
    "Consultation",
    "Values",
    "Mission",
    "Testimonials",
    "FAQ",
    "Privacy",
    "Cookies",
    "Accessibility",
    "Sitemap",
]

INTERNAL_CONCEPT_WORDS = {
    "inspire", "empower", "enhance", "renew", "elevate", "refine", "glow",
    "balance", "radiance", "essence", "bloom", "vital", "poise", "aura",
    "clarity", "grace", "sculpt", "lumin", "verda", "halo", "calm",
    "precision", "ritual", "signal", "align", "vivant", "form", "pure",
    "solace", "method", "evolve", "serene", "elan", "flora", "atelier",
    "lumina", "vellum", "origin", "kindred", "noble", "vista", "softline",
    "meridian", "safeguard", "silhouette", "curate", "proof", "signature",
    "wisdom", "sovereign",
}

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    ".cache",
    ".pytest_cache",
    "docs/qa/mobile-partial-audit",
}


@dataclass
class PageAudit:
    name: str
    url: str
    output_prefix: str
    screenshots: dict[str, str]
    top_banner_readable: bool
    en_pt_visible: bool
    vertical_brand_issue: bool
    grey_placeholder_logo_risk: bool
    public_concept_title_risk: bool
    debug_widget_label_visible: bool
    duplicate_whatsapp_risk: bool
    main_links_visible_after_menu: list[str]
    missing_main_links_after_menu: list[str]
    footer_links_visible: list[str]
    missing_footer_links: list[str]
    footer_link_count_ok: bool
    issues: list[str]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args: Any) -> None:
        return


def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip().lower()


def slugify(text: str) -> str:
    text = re.sub(r"[^a-zA-Z0-9._-]+", "-", text.strip())
    text = re.sub(r"-+", "-", text).strip("-")
    return text[:100] or "page"


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


def find_free_port(start: int = 8765) -> int:
    for port in range(start, start + 200):
        if port_is_free(port):
            return port
    raise RuntimeError("No free local port found.")


def start_server(root: Path, port: int) -> ThreadingHTTPServer:
    handler = partial(QuietHandler, directory=str(root))
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def is_excluded(path: Path, root: Path) -> bool:
    rel = path.relative_to(root).as_posix()
    parts = set(Path(rel).parts)
    if parts & {".git", "node_modules", ".venv", "venv", "__pycache__", ".cache", ".pytest_cache"}:
        return True
    if rel.startswith("docs/qa/mobile-partial-audit"):
        return True
    return False


def discover_html_pages(root: Path, limit: int | None) -> list[Path]:
    candidates: list[Path] = []

    for p in root.rglob("*.html"):
        if is_excluded(p, root):
            continue
        if p.name.lower() in {"index.html", "home.html"}:
            candidates.append(p)

    if not candidates:
        for p in root.rglob("*.html"):
            if not is_excluded(p, root):
                candidates.append(p)

    def sort_key(p: Path) -> tuple[int, str]:
        rel = p.relative_to(root).as_posix()
        m = re.search(r"(^|/)(\d{1,3})[-_]", rel)
        num = int(m.group(2)) if m else 9999
        return (num, rel)

    candidates = sorted(set(candidates), key=sort_key)

    if limit:
        candidates = candidates[:limit]

    return candidates


def rel_url_for_file(root: Path, file_path: Path, port: int) -> str:
    rel = file_path.relative_to(root).as_posix()
    return f"http://127.0.0.1:{port}/{rel}"


def load_playwright():
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
        return sync_playwright, PlaywrightTimeoutError
    except Exception:
        print("\nPlaywright is not installed.")
        print("Run:")
        print("  python3 -m pip install --user playwright")
        print("  python3 -m playwright install chromium")
        print("\nThen run this script again.\n")
        sys.exit(2)


def first_visible_locator(page, selectors: list[str]):
    for sel in selectors:
        try:
            loc = page.locator(sel).first()
            if loc.count() and loc.is_visible(timeout=500):
                return loc, sel
        except Exception:
            continue
    return None, None


def safe_screenshot_locator(locator, path: Path) -> bool:
    try:
        locator.scroll_into_view_if_needed(timeout=2500)
        time.sleep(0.25)
        locator.screenshot(path=str(path), timeout=6000)
        return True
    except Exception:
        return False


def try_click_mobile_menu(page) -> bool:
    selectors = [
        "button[aria-label*='menu' i]",
        "button[aria-label*='nav' i]",
        "button[aria-controls]",
        "[data-menu-toggle]",
        "[data-nav-toggle]",
        "[data-mobile-menu-toggle]",
        ".menu-toggle",
        ".nav-toggle",
        ".hamburger",
        ".mobile-menu-toggle",
        ".mobile-nav-toggle",
        "button:has-text('Menu')",
        "button:has-text('☰')",
        "[role='button']:has-text('Menu')",
        "[role='button']:has-text('☰')",
    ]

    for sel in selectors:
        try:
            loc = page.locator(sel).first()
            if loc.count() and loc.is_visible(timeout=500):
                loc.click(timeout=2000)
                page.wait_for_timeout(800)
                return True
        except Exception:
            continue

    # Fallback: click any small visible button/icon near the header that looks like a menu control.
    try:
        clicked = page.evaluate(
            """
            () => {
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 8 && r.height > 8 &&
                       s.display !== 'none' &&
                       s.visibility !== 'hidden' &&
                       Number(s.opacity) !== 0;
              };
              const candidates = [...document.querySelectorAll('button,a,[role="button"],.hamburger,.menu,.menu-button')];
              for (const el of candidates) {
                const txt = (el.innerText || el.textContent || el.getAttribute('aria-label') || '').trim().toLowerCase();
                const r = el.getBoundingClientRect();
                if (visible(el) && r.top < 240 && (txt.includes('menu') || txt.includes('☰') || el.className.toString().toLowerCase().includes('hamburger'))) {
                  el.click();
                  return true;
                }
              }
              return false;
            }
            """
        )
        if clicked:
            page.wait_for_timeout(800)
            return True
    except Exception:
        pass

    return False


def collect_visible_text(page, scope_selector: str | None = None) -> str:
    script = """
    (scopeSelector) => {
      const root = scopeSelector ? document.querySelector(scopeSelector) : document.body;
      if (!root) return "";
      const visible = (el) => {
        const r = el.getBoundingClientRect();
        const s = getComputedStyle(el);
        return r.width > 1 && r.height > 1 &&
               s.display !== "none" &&
               s.visibility !== "hidden" &&
               Number(s.opacity) !== 0;
      };
      return [...root.querySelectorAll("a,button,h1,h2,h3,p,span,li,div")]
        .filter(visible)
        .map(el => (el.innerText || el.textContent || "").trim())
        .filter(Boolean)
        .join("\\n");
    }
    """
    try:
        return page.evaluate(script, scope_selector)
    except Exception:
        return ""


def collect_footer_text(page) -> str:
    selectors = ["footer", ".site-footer", "#footer", "[data-partial*='footer' i]", "[class*='footer' i]"]
    for sel in selectors:
        try:
            if page.locator(sel).first().count():
                txt = collect_visible_text(page, sel)
                if txt.strip():
                    return txt
        except Exception:
            continue
    return ""


def visible_links_present(text: str, required: list[str]) -> list[str]:
    nt = normalize(text)
    found = []
    for link in required:
        pattern = r"\b" + re.escape(link.lower()) + r"\b"
        if re.search(pattern, nt):
            found.append(link)
    return found


def audit_vertical_brand(page) -> bool:
    try:
        matches = page.evaluate(
            """
            () => {
              const bad = [];
              const els = [...document.querySelectorAll("header *, [class*='banner' i] *, [class*='brand' i] *, [class*='logo' i] *")];
              const visible = (el) => {
                const r = el.getBoundingClientRect();
                const s = getComputedStyle(el);
                return r.width > 1 && r.height > 1 &&
                       r.top < 280 &&
                       s.display !== "none" &&
                       s.visibility !== "hidden" &&
                       Number(s.opacity) !== 0;
              };
              for (const el of els) {
                if (!visible(el)) continue;
                const txt = (el.innerText || el.textContent || "").trim();
                if (!/(Franciele|Sofiati|Biomédica|Biomedica)/i.test(txt)) continue;
                const r = el.getBoundingClientRect();
                const cs = getComputedStyle(el);
                const fs = parseFloat(cs.fontSize) || 12;
                const lh = parseFloat(cs.lineHeight) || fs * 1.25;
                const approxLines = r.height / lh;
                if ((r.width < 140 && r.height > 45) || approxLines > 2.6 || /\\n/.test(txt)) {
                  bad.push({text: txt, width: r.width, height: r.height, lines: approxLines});
                }
              }
              return bad;
            }
            """
        )
        return bool(matches)
    except Exception:
        return False


def audit_placeholder_logo_risk(page) -> bool:
    try:
        return bool(
            page.evaluate(
                """
                () => {
                  const els = [...document.querySelectorAll("header img, header svg, header .logo, header [class*='logo' i], header [class*='mark' i]")];
                  const visible = (el) => {
                    const r = el.getBoundingClientRect();
                    const s = getComputedStyle(el);
                    return r.width > 4 && r.height > 4 &&
                           r.top < 260 &&
                           s.display !== "none" &&
                           s.visibility !== "hidden" &&
                           Number(s.opacity) !== 0;
                  };
                  for (const el of els) {
                    if (!visible(el)) continue;
                    const r = el.getBoundingClientRect();
                    const txt = (el.innerText || el.textContent || el.getAttribute("alt") || "").trim();
                    const bg = getComputedStyle(el).backgroundColor;
                    const src = el.getAttribute("src") || "";
                    const looksBlankGrey = bg.includes("rgb(217") || bg.includes("rgb(218") || bg.includes("rgb(219") || bg.includes("rgb(220") || bg.includes("rgb(221") || bg.includes("rgb(222") || bg.includes("rgb(223");
                    if (!txt && !src && r.width > 10 && r.height > 20 && looksBlankGrey) return true;
                  }
                  return false;
                }
                """
            )
        )
    except Exception:
        return False


def audit_public_concept_title(page) -> bool:
    try:
        h1s = page.evaluate(
            """
            () => [...document.querySelectorAll("h1")]
              .map(h => (h.innerText || h.textContent || "").trim())
              .filter(Boolean)
            """
        )
    except Exception:
        h1s = []

    for h1 in h1s:
        m = re.match(r"^([A-Za-zÀ-ÿ-]+)\s*:", h1.strip())
        if m and m.group(1).lower() in INTERNAL_CONCEPT_WORDS:
            return True

    return False


def section_screenshots(page, outdir: Path, prefix: str) -> dict[str, str]:
    screenshots: dict[str, str] = {}

    section_selectors = {
        "header": [
            "header",
            ".site-header",
            "#header",
            "[data-partial*='header' i]",
            "[class*='header' i]",
            "nav",
        ],
        "hero": [
            ".hero",
            "section.hero",
            "[data-section*='hero' i]",
            "[class*='hero' i]",
            "main section:first-of-type",
        ],
        "widgets": [
            "[class*='widget' i]",
            "[id*='widget' i]",
            "[class*='floating' i]",
            "[id*='floating' i]",
            "[data-component*='floating' i]",
            "[data-partial*='widget' i]",
        ],
        "footer": [
            "footer",
            ".site-footer",
            "#footer",
            "[data-partial*='footer' i]",
            "[class*='footer' i]",
        ],
    }

    for name, selectors in section_selectors.items():
        loc, used = first_visible_locator(page, selectors)
        if not loc:
            continue
        path = outdir / f"{prefix}-mobile-{name}.png"
        if safe_screenshot_locator(loc, path):
            screenshots[name] = str(path)

    return screenshots


def audit_one_page(page, url: str, name: str, outdir: Path, width: int, height: int) -> PageAudit:
    prefix = slugify(name)

    screenshots: dict[str, str] = {}

    page.goto(url, wait_until="networkidle", timeout=30000)
    page.wait_for_timeout(1000)

    full_path = outdir / f"{prefix}-mobile-full.png"
    page.screenshot(path=str(full_path), full_page=True, timeout=15000)
    screenshots["full"] = str(full_path)

    screenshots.update(section_screenshots(page, outdir, prefix))

    menu_opened = try_click_mobile_menu(page)
    if menu_opened:
        menu_path = outdir / f"{prefix}-mobile-menu-open-full.png"
        page.screenshot(path=str(menu_path), full_page=True, timeout=15000)
        screenshots["menu_open_full"] = str(menu_path)

        menu_loc, _ = first_visible_locator(
            page,
            [
                "[aria-modal='true']",
                "[role='dialog']",
                ".mobile-menu",
                ".mobile-nav",
                ".menu-open",
                ".nav-open",
                "[class*='drawer' i]",
                "[class*='overlay' i]",
                "nav",
            ],
        )
        if menu_loc:
            menu_crop = outdir / f"{prefix}-mobile-menu-open-crop.png"
            if safe_screenshot_locator(menu_loc, menu_crop):
                screenshots["menu_open_crop"] = str(menu_crop)

    body_text = collect_visible_text(page)
    footer_text = collect_footer_text(page)

    found_main = visible_links_present(body_text, MAIN_LINKS)
    missing_main = [x for x in MAIN_LINKS if x not in found_main]

    found_footer = visible_links_present(footer_text, FOOTER_LINKS)
    missing_footer = [x for x in FOOTER_LINKS if x not in found_footer]

    en_pt_visible = bool(re.search(r"\b(EN\s*/\s*PT|PT\s*/\s*EN|EN\s+PT|PT\s+EN)\b", body_text, re.I))
    vertical_brand_issue = audit_vertical_brand(page)
    placeholder_logo_risk = audit_placeholder_logo_risk(page)
    public_concept_title_risk = audit_public_concept_title(page)
    debug_widget_label_visible = bool(re.search(r"WIDGETS\s*/\s*FLOATING\s*ACTIONS|HEADER\s*/\s*NAVIGATION|\\bHERO\\b|\\bFOOTER\\b", body_text, re.I))

    whatsapp_count = len(re.findall(r"WhatsApp", body_text, re.I))
    duplicate_whatsapp_risk = whatsapp_count > 3

    issues: list[str] = []

    if vertical_brand_issue:
        issues.append("Top/header brand text appears to wrap vertically or across too many lines.")
    if not en_pt_visible:
        issues.append("EN/PT language switcher not visibly detected.")
    if placeholder_logo_risk:
        issues.append("Header logo/mark looks like a placeholder grey block or missing asset.")
    if public_concept_title_risk:
        issues.append("Hero H1 appears to expose internal concept name before a colon.")
    if debug_widget_label_visible:
        issues.append("Debug/audit labels appear visible in public screenshot output.")
    if duplicate_whatsapp_risk:
        issues.append(f"Possible duplicate WhatsApp controls detected ({whatsapp_count} visible mentions).")
    if missing_main:
        issues.append("Missing main mobile/menu links: " + ", ".join(missing_main))
    if missing_footer:
        issues.append("Missing footer sitemap links: " + ", ".join(missing_footer))
    if not menu_opened:
        issues.append("Mobile menu toggle was not found/clicked; open-menu screenshot not captured.")

    top_banner_readable = not vertical_brand_issue and en_pt_visible

    return PageAudit(
        name=name,
        url=url,
        output_prefix=prefix,
        screenshots=screenshots,
        top_banner_readable=top_banner_readable,
        en_pt_visible=en_pt_visible,
        vertical_brand_issue=vertical_brand_issue,
        grey_placeholder_logo_risk=placeholder_logo_risk,
        public_concept_title_risk=public_concept_title_risk,
        debug_widget_label_visible=debug_widget_label_visible,
        duplicate_whatsapp_risk=duplicate_whatsapp_risk,
        main_links_visible_after_menu=found_main,
        missing_main_links_after_menu=missing_main,
        footer_links_visible=found_footer,
        missing_footer_links=missing_footer,
        footer_link_count_ok=len(missing_footer) == 0,
        issues=issues,
    )


def write_reports(audits: list[PageAudit], outdir: Path) -> None:
    json_path = outdir / "mobile-audit-report.json"
    md_path = outdir / "mobile-audit-report.md"

    json_path.write_text(
        json.dumps([asdict(a) for a in audits], indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    lines: list[str] = []
    lines.append("# Sofiati Mobile Partial Audit Report\n")
    lines.append("This report is generated from mobile viewport screenshots.\n")
    lines.append("## Summary\n")

    total = len(audits)
    with_issues = sum(1 for a in audits if a.issues)
    lines.append(f"- Pages audited: {total}")
    lines.append(f"- Pages with issues: {with_issues}")
    lines.append("")

    lines.append("## Issue Counts\n")
    issue_counter: dict[str, int] = {}
    for a in audits:
        for issue in a.issues:
            key = re.sub(r"\\s*\\([^)]*\\)", "", issue)
            issue_counter[key] = issue_counter.get(key, 0) + 1

    for issue, count in sorted(issue_counter.items(), key=lambda x: (-x[1], x[0])):
        lines.append(f"- {count} × {issue}")
    lines.append("")

    lines.append("## Page-by-page audit\n")

    for a in audits:
        status = "FAILED" if a.issues else "PASSED"
        lines.append(f"### {a.name}")
        lines.append(f"- Status: **{status}**")
        lines.append(f"- URL: `{a.url}`")
        lines.append(f"- Top banner readable: `{a.top_banner_readable}`")
        lines.append(f"- EN/PT visible: `{a.en_pt_visible}`")
        lines.append(f"- Main links found: `{len(a.main_links_visible_after_menu)}/8`")
        lines.append(f"- Footer links found: `{len(a.footer_links_visible)}/17`")
        lines.append("- Screenshots:")
        for key, path in a.screenshots.items():
            lines.append(f"  - {key}: `{path}`")
        if a.issues:
            lines.append("- Issues:")
            for issue in a.issues:
                lines.append(f"  - {issue}")
        lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")


def zip_output(outdir: Path) -> Path:
    zip_path = outdir / "mobile-audit-output.zip"
    if zip_path.exists():
        zip_path.unlink()

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for p in outdir.rglob("*"):
            if p == zip_path:
                continue
            if p.is_file():
                z.write(p, p.relative_to(outdir))

    return zip_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repo/site root to serve locally.")
    parser.add_argument("--out", default="docs/qa/mobile-partial-audit", help="Output folder.")
    parser.add_argument("--limit", type=int, default=50, help="Max local HTML pages to audit.")
    parser.add_argument("--width", type=int, default=390, help="Mobile viewport width.")
    parser.add_argument("--height", type=int, default=844, help="Mobile viewport height.")
    parser.add_argument("--port", type=int, default=0, help="Local server port. 0 = auto.")
    parser.add_argument("--urls", default="", help="Comma-separated URLs to audit instead of discovering local HTML files.")
    parser.add_argument("--headed", action="store_true", help="Show browser window.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    outdir = Path(args.out).resolve()
    outdir.mkdir(parents=True, exist_ok=True)

    sync_playwright, PlaywrightTimeoutError = load_playwright()

    server = None
    urls: list[tuple[str, str]] = []

    if args.urls.strip():
        for i, url in enumerate([u.strip() for u in args.urls.split(",") if u.strip()], start=1):
            urls.append((f"{i:02d}-{slugify(url)}", url))
    else:
        html_pages = discover_html_pages(root, args.limit)
        if not html_pages:
            print("No HTML pages found.")
            return 1

        port = args.port or find_free_port()
        server = start_server(root, port)
        print(f"Serving {root} at http://127.0.0.1:{port}/")

        for p in html_pages:
            rel = p.relative_to(root).as_posix()
            name = p.parent.name if p.name.lower() == "index.html" else p.stem
            urls.append((name, rel_url_for_file(root, p, port)))

    audits: list[PageAudit] = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not args.headed)
            context = browser.new_context(
                viewport={"width": args.width, "height": args.height},
                device_scale_factor=2,
                is_mobile=True,
                has_touch=True,
                user_agent=(
                    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                    "Mobile/15E148 Safari/604.1"
                ),
            )

            for index, (name, url) in enumerate(urls, start=1):
                page = context.new_page()
                safe_name = f"{index:02d}-{slugify(name)}"
                print(f"[{index}/{len(urls)}] Auditing mobile: {name}")
                try:
                    audit = audit_one_page(page, url, safe_name, outdir, args.width, args.height)
                    audits.append(audit)
                    print(f"  issues: {len(audit.issues)}")
                except Exception as e:
                    fail = PageAudit(
                        name=safe_name,
                        url=url,
                        output_prefix=safe_name,
                        screenshots={},
                        top_banner_readable=False,
                        en_pt_visible=False,
                        vertical_brand_issue=False,
                        grey_placeholder_logo_risk=False,
                        public_concept_title_risk=False,
                        debug_widget_label_visible=False,
                        duplicate_whatsapp_risk=False,
                        main_links_visible_after_menu=[],
                        missing_main_links_after_menu=MAIN_LINKS.copy(),
                        footer_links_visible=[],
                        missing_footer_links=FOOTER_LINKS.copy(),
                        footer_link_count_ok=False,
                        issues=[f"Script/browser error: {e}"],
                    )
                    audits.append(fail)
                    print(f"  ERROR: {e}")
                finally:
                    page.close()

            context.close()
            browser.close()

    finally:
        if server:
            server.shutdown()

    write_reports(audits, outdir)
    zip_path = zip_output(outdir)

    print("\nDONE")
    print(f"Output folder: {outdir}")
    print(f"Markdown report: {outdir / 'mobile-audit-report.md'}")
    print(f"JSON report: {outdir / 'mobile-audit-report.json'}")
    print(f"ZIP: {zip_path}")

    failed = sum(1 for a in audits if a.issues)
    print(f"\nAudited: {len(audits)}")
    print(f"With issues: {failed}")
    print("\nUpload the mobile screenshots from the output folder or the ZIP here.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
