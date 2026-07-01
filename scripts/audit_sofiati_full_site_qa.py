#!/usr/bin/env python3
"""Full Sofiati QA audit across every concept page and requested breakpoint."""

from __future__ import annotations

import argparse
import html
import json
import re
import socket
import subprocess
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
DOCS_DIR = ROOT / "docs" / "script-runs"
VIEWPORTS = [1440, 1024, 768, 360]

REQUIRED_MAIN = ["Home", "About", "Care", "Laser", "Skin", "Results", "Journal", "Contact"]
REQUIRED_FOOTER = [
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

PUBLIC_COPY_FAIL_RE = re.compile(
    r"\b("
    r"is presented with calm language|Final CTA|CTA bridge|Footer bridge|Contact bridge|"
    r"concept|theme|layout|system|wireframe|debug|placeholder|website direction|"
    r"design system|dark premium|portal tiles|Section\s+\d+|Step\s+\d+|should feel"
    r")\b",
    re.I,
)

OLD_LOGO_RE = re.compile(
    r"sofiati-(?:logo-primary-sage|logo-primary-white|logo-primary-bronze|signature-sage|signature-white|monogram-sage|monogram-white|monogram-bronze)\.png"
)


class VisibleText(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.skip = 0
        self.parts: list[str] = []
        self.h1_count = 0
        self.title = ""
        self.meta_description = ""
        self.alt_values: list[str] = []
        self.hrefs: list[str] = []
        self.assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip += 1
            return
        attr = {key.lower(): value or "" for key, value in attrs}
        if tag == "meta" and attr.get("name") == "description":
            self.meta_description = html.unescape(attr.get("content", "")).strip()
            if self.meta_description:
                self.parts.append(self.meta_description)
        if tag == "meta" and attr.get("property") in {"og:title", "og:description"}:
            value = html.unescape(attr.get("content", "")).strip()
            if value:
                self.parts.append(value)
        if tag == "img":
            src = attr.get("src", "")
            alt = html.unescape(attr.get("alt", "")).strip()
            if src:
                self.assets.append(src)
            if alt:
                self.alt_values.append(alt)
                self.parts.append(alt)
        if tag == "script":
            asset = attr.get("src")
            if asset:
                self.assets.append(asset)
        if tag == "link":
            rel = {part.strip().lower() for part in attr.get("rel", "").split()}
            if rel & {"stylesheet", "icon", "apple-touch-icon", "manifest", "preload", "modulepreload"}:
                asset = attr.get("href")
                if asset:
                    self.assets.append(asset)
        if tag == "a":
            href = attr.get("href", "")
            if href and not href.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                self.hrefs.append(href)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data: str) -> None:
        if self.skip:
            return
        value = html.unescape(data).strip()
        if not value:
            return
        self.parts.append(value)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)

    @property
    def text(self) -> str:
        return " ".join(self.parts)


@dataclass
class StaticPageResult:
    concept: str
    page: str
    path: str
    failures: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "PASS" if not self.failures else "FAIL"


def concept_dirs() -> list[Path]:
    return sorted(
        [path for path in CONCEPTS_DIR.iterdir() if path.is_dir() and re.match(r"^\d{2}-", path.name)],
        key=lambda path: path.name,
    )


def page_paths(concepts: list[Path]) -> list[Path]:
    paths: list[Path] = []
    for concept in concepts:
        paths.extend(path for path in sorted(concept.glob("*.html")) if ".bak" not in path.name)
    return paths


def parse_page(path: Path) -> VisibleText:
    parser = VisibleText()
    parser.feed(path.read_text(encoding="utf-8", errors="ignore"))
    return parser


def local_target(page: Path, ref: str) -> Path | None:
    if ref.startswith(("http://", "https://", "//", "data:", "javascript:")):
        return None
    clean = ref.split("#", 1)[0].split("?", 1)[0]
    if not clean:
        return None
    if clean.startswith("/"):
        return ROOT / clean.lstrip("/")
    return page.parent / clean


def static_audit() -> list[StaticPageResult]:
    concepts = concept_dirs()
    results: list[StaticPageResult] = []
    for path in page_paths(concepts):
        concept = path.parent.name
        result = StaticPageResult(concept=concept, page=path.name, path=str(path.relative_to(ROOT)))
        raw = path.read_text(encoding="utf-8", errors="ignore")
        parsed = parse_page(path)
        text = parsed.text

        if PUBLIC_COPY_FAIL_RE.search(text):
            result.failures.append("public copy contains internal/debug/template language")
        if OLD_LOGO_RE.search(raw):
            result.failures.append("stale logo reference")
        if ">FS<" in raw or re.search(r">\s*FS\s*<", raw):
            result.failures.append("raw FS text mark")
        if raw.count("<h1") != 1:
            result.failures.append(f"h1 count {raw.count('<h1')}")
        if not re.search(r"<title>[^<]{8,}</title>", raw):
            result.failures.append("missing meaningful title")
        if not parsed.meta_description or len(parsed.meta_description) < 80:
            result.failures.append("missing meaningful meta description")
        if "sofiati-logo-primary-transparent.png" not in raw and "sofiati-favicon.svg" not in raw:
            result.failures.append("approved social/favicon logo missing")
        for alt in parsed.alt_values:
            if PUBLIC_COPY_FAIL_RE.search(alt):
                result.failures.append("placeholder/internal image alt")
                break
        for href in parsed.hrefs:
            target = local_target(path, href)
            if target and not target.exists():
                result.failures.append(f"broken internal link: {href}")
                break
        for asset in parsed.assets:
            target = local_target(path, asset)
            if target and not target.exists():
                result.failures.append(f"missing asset: {asset}")
                break
        results.append(result)
    return results


def free_port(start: int = 8100) -> int:
    for port in range(start, start + 120):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free local port found")


def run_server(port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def rendered_audit(port: int, limit: int | None = None) -> list[dict]:
    pages = [str(path.relative_to(ROOT)) for path in page_paths(concept_dirs())]
    if limit:
        pages = pages[:limit]
    node_script = f"""
const {{ chromium }} = require('playwright');
const pages = {json.dumps(pages)};
const widths = {json.dumps(VIEWPORTS)};
const requiredMain = {json.dumps(REQUIRED_MAIN)};
const requiredFooter = {json.dumps(REQUIRED_FOOTER)};
const port = {port};

const waitForPartials = async (page) => {{
  await page.waitForFunction(() => {{
    const names = ['header', 'mobile-menu', 'footer', 'cookie-banner', 'floating-widgets'];
    return names.every((name) => document.querySelector(`[data-sofiati-partial="${{name}}"]`)?.dataset.partialLoaded === 'true');
  }}, null, {{ timeout: 12000 }});
  await page.waitForLoadState('networkidle', {{ timeout: 300 }}).catch(() => {{}});
  await page.waitForFunction(() => {{
    const logos = [...document.querySelectorAll('.sf-logo-img')];
    return logos.length >= 3 && logos.every((img) => img.complete && img.naturalWidth > 0);
  }}, null, {{ timeout: 1200 }}).catch(() => {{}});
}};

const visibleImagesLoaded = async (page) => {{
  return await page.evaluate(() => {{
    const visibleImages = [...document.images].filter((img) => {{
      const rect = img.getBoundingClientRect();
      const style = getComputedStyle(img);
      return (
        rect.width > 4 &&
        rect.height > 4 &&
        rect.bottom >= 0 &&
        rect.top <= window.innerHeight &&
        style.display !== 'none' &&
        style.visibility !== 'hidden' &&
        Number(style.opacity || 1) > 0.01
      );
    }});
    return visibleImages.every((img) => img.complete && img.naturalWidth > 0);
  }});
}};

const textOf = (el) => (el?.textContent || '').replace(/\\s+/g, ' ').trim();
const isVisible = (el) => {{
  if (!el) return false;
  const style = getComputedStyle(el);
  const rect = el.getBoundingClientRect();
  return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0.01 && rect.width > 0 && rect.height > 0;
}};

(async () => {{
  const browser = await chromium.launch({{ headless: true }});
  const results = [];
  for (const width of widths) {{
    const context = await browser.newContext({{ viewport: {{ width, height: 980 }}, deviceScaleFactor: 1 }});
    const page = await context.newPage();
    for (const rel of pages) {{
      const record = {{ page: rel, width, failures: [], warnings: [] }};
      const failedRequests = [];
      const consoleErrors = [];
      page.removeAllListeners('requestfailed');
      page.removeAllListeners('response');
      page.removeAllListeners('console');
      page.on('requestfailed', (request) => failedRequests.push(request.url()));
      page.on('response', (response) => {{
        if (response.status() >= 400) failedRequests.push(`${{response.status()}} ${{response.url()}}`);
      }});
      page.on('console', (message) => {{
        if (message.type() === 'error') consoleErrors.push(message.text());
      }});
      try {{
        await page.goto(`http://127.0.0.1:${{port}}/${{rel}}`, {{ waitUntil: 'domcontentloaded', timeout: 18000 }});
        await waitForPartials(page);
        record.visibleImagesLoadedTop = await visibleImagesLoaded(page);
        const metrics = await page.evaluate(({{ requiredMain, requiredFooter }}) => {{
          const textOf = (el) => (el?.textContent || '').replace(/\\s+/g, ' ').trim();
          const isVisible = (el) => {{
            if (!el) return false;
            const style = getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return style.display !== 'none' && style.visibility !== 'hidden' && Number(style.opacity || 1) > 0.01 && rect.width > 0 && rect.height > 0;
          }};
          const by = (selector) => [...document.querySelectorAll(selector)];
          const desktopLinks = by('.sf-desktop-nav [data-main-nav="true"]');
          const mobileLinks = by('.sf-mobile-nav [data-main-nav="true"]');
          const footerLinks = by('.sf-footer-sitemap [data-footer-link="true"]');
          const desktopLabels = desktopLinks.map(textOf).map((value) => value.replace(/^\\d{{2}}\\s*/, ''));
          const mobileLabels = mobileLinks.map(textOf).map((value) => value.replace(/^\\d{{2}}\\s*/, ''));
          const footerLabels = footerLinks.map(textOf).map((value) => value.replace(/^\\d{{2}}\\s*/, ''));
          const banner = document.querySelector('.sf-identity-banner');
          const bannerStyle = banner ? getComputedStyle(banner) : null;
          const bannerRect = banner?.getBoundingClientRect();
          const header = document.querySelector('.sf-public-header');
          const headerRect = header?.getBoundingClientRect();
          const hero = document.querySelector('main section:first-of-type');
          const heroRect = hero?.getBoundingClientRect();
          const footer = document.querySelector('.sf-public-footer');
          const menuButton = document.querySelector('[data-menu-toggle]');
          const h1s = by('main h1');
          const bodyText = textOf(document.body);
          const textFits = by('.sf-public-header a, .sf-public-header button, .sf-mobile-menu a, .sf-mobile-menu button, .sf-public-footer a, .sf-cookie-banner a, .sf-cookie-banner button').every((el) => {{
            return el.scrollWidth <= el.clientWidth + 3 || getComputedStyle(el).whiteSpace !== 'nowrap';
          }});
          const desktopVisible = desktopLinks.filter(isVisible);
          const navRects = desktopVisible.map((el) => {{
            const rect = el.getBoundingClientRect();
            return {{ left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom }};
          }});
          let navOverlap = false;
          for (let i = 0; i < navRects.length; i += 1) {{
            for (let j = i + 1; j < navRects.length; j += 1) {{
              const a = navRects[i];
              const b = navRects[j];
              if (!(a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top)) navOverlap = true;
            }}
          }}
          const logos = by('.sf-logo-img');
          const logoRects = logos.map((img) => img.getBoundingClientRect()).filter((rect) => rect.width && rect.height);
          const logoAspectOk = logoRects.every((rect) => rect.width / rect.height > 0.55 && rect.width / rect.height < 1.9);
          const h1 = h1s[0];
          return {{
            desktopLabels,
            mobileLabels,
            footerLabels,
            desktopVisibleCount: desktopVisible.length,
            bannerPresent: !!banner,
            bannerVisible: isVisible(banner),
            bannerHorizontal: bannerStyle ? bannerStyle.writingMode === 'horizontal-tb' && bannerStyle.textOrientation !== 'upright' : false,
            bannerNowrap: bannerStyle ? bannerStyle.whiteSpace === 'nowrap' || bannerStyle.flexWrap === 'nowrap' : false,
            bannerHeight: bannerRect?.height || 0,
            bannerInsideMenu: !!document.querySelector('#mobile-menu .sf-identity-banner'),
            headerVisible: isVisible(header),
            headerHeight: headerRect?.height || 0,
            headerCta: !!document.querySelector('[data-header-cta]'),
            headerCtaVisible: isVisible(document.querySelector('[data-header-cta]')),
            menuButtonVisible: isVisible(menuButton),
            menuButtonAria: !!(menuButton?.getAttribute('aria-label') || textOf(menuButton)),
            whatsappCount: by('.sf-floating-tools .sf-floating-whatsapp').length,
            accessibilityCount: by('.sf-floating-tools .sf-floating-accessibility').length,
            backTopCount: by('.sf-floating-tools .sf-back-to-top').length,
            pageOverflow: document.documentElement.scrollWidth <= window.innerWidth + 2,
            textFits,
            navOverlap,
            logoCount: logos.length,
            logosLoaded: logos.length >= 3 && logos.every((img) => img.complete && img.naturalWidth > 0),
            logoAspectOk,
            staleLogoRefs: by('img').filter((img) => /sofiati-(?:logo-primary-sage|signature-sage|monogram-sage|logo-primary-white|logo-primary-bronze|monogram-white|monogram-bronze)\\.png/.test(img.getAttribute('src') || '')).length,
            h1Count: h1s.length,
            h1Visible: isVisible(h1),
            h1Text: textOf(h1),
            heroVisible: isVisible(hero),
            heroHeight: heroRect?.height || 0,
            heroTooTall: heroRect ? heroRect.height > window.innerHeight * (window.innerWidth <= 430 ? 1.75 : window.innerWidth <= 1024 ? 1.55 : 1.35) : true,
            publicCopyLeak: /\\b(is presented with calm language|Final CTA|CTA bridge|Footer bridge|Contact bridge|concept|theme|layout|system|wireframe|debug|placeholder|website direction|design system|dark premium|portal tiles|Section\\s+\\d+|Step\\s+\\d+|should feel)\\b/i.test(bodyText),
            footerVisible: isVisible(footer),
            footerBrand: !!document.querySelector('.sf-footer-brand .sf-logo-img') && /Franciele Sofiati Biomédica/.test(textOf(document.querySelector('.sf-footer-brand'))),
            footerContact: /WhatsApp/.test(textOf(document.querySelector('.sf-footer-contact'))) && /Instagram: @fransofiati_biomedica/.test(textOf(document.querySelector('.sf-footer-contact'))) && /Londrina, PR \\/ Brazil/.test(textOf(document.querySelector('.sf-footer-contact'))),
            footerCta: !!document.querySelector('[data-footer-cta]') && /Contact the clinic/.test(textOf(document.querySelector('[data-footer-cta]'))),
            copyright: /© 2026 Franciele Sofiati Biomédica/.test(bodyText),
          }};
        }}, {{ requiredMain, requiredFooter }});
        Object.assign(record, metrics);
        const same = (a, b) => a.length === b.length && a.every((value, index) => value === b[index]);
        if (!same(metrics.desktopLabels, requiredMain)) record.failures.push('desktop nav labels/count');
        if (!same(metrics.mobileLabels, requiredMain)) record.failures.push('mobile nav labels/count');
        if (!same(metrics.footerLabels, requiredFooter)) record.failures.push('footer sitemap labels/count');
        if (!metrics.bannerPresent || !metrics.bannerVisible) record.failures.push('language banner missing/hidden');
        if (!metrics.bannerHorizontal || !metrics.bannerNowrap) record.failures.push('language banner wrapping/orientation');
        if (metrics.bannerInsideMenu) record.failures.push('language banner inside menu');
        if (!metrics.headerVisible || !metrics.headerCta || !metrics.headerCtaVisible) record.failures.push('header/consultation cta');
        if (width >= 1280 && metrics.desktopVisibleCount !== 8) record.failures.push('desktop visible nav count');
        if (width <= 1024 && (!metrics.menuButtonVisible || metrics.desktopVisibleCount !== 0)) record.failures.push('tablet/mobile header mode');
        if (!metrics.menuButtonAria) record.failures.push('menu button accessible name');
        if (metrics.whatsappCount !== 1 || metrics.accessibilityCount !== 1 || metrics.backTopCount !== 1) record.failures.push('floating action counts');
        if (!metrics.pageOverflow) record.failures.push('horizontal overflow');
        if (!metrics.textFits) record.failures.push('text clipping');
        if (metrics.navOverlap) record.failures.push('nav overlap');
        if (metrics.logoCount < 3 || !metrics.logosLoaded || !metrics.logoAspectOk || metrics.staleLogoRefs) record.failures.push('logo render/reference');
        if (metrics.h1Count !== 1 || !metrics.h1Visible || !metrics.h1Text) record.failures.push('h1');
        if (!metrics.heroVisible || metrics.heroTooTall) record.failures.push('hero sizing/visibility');
        if (metrics.publicCopyLeak) record.failures.push('public copy leak');
        if (!metrics.footerVisible || !metrics.footerBrand || !metrics.footerContact || !metrics.footerCta || !metrics.copyright) record.failures.push('footer completeness');
        if (!record.visibleImagesLoadedTop) record.failures.push('visible images not loaded');
        await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
        await page.waitForTimeout(35);
        record.visibleImagesLoadedFooter = await visibleImagesLoaded(page);
        if (!record.visibleImagesLoadedFooter) record.failures.push('footer visible images not loaded');
        const footerOverlap = await page.evaluate(() => {{
          const floating = document.querySelector('.sf-floating-tools');
          const floatingRect = floating?.getBoundingClientRect();
          if (!floatingRect) return true;
          const targets = [...document.querySelectorAll('.sf-footer-sitemap a, .sf-footer-cta, .sf-footer-close p')];
          return targets.some((target) => {{
            const rect = target.getBoundingClientRect();
            return !(floatingRect.right <= rect.left || rect.right <= floatingRect.left || floatingRect.bottom <= rect.top || rect.bottom <= floatingRect.top);
          }});
        }});
        record.footerOverlap = footerOverlap;
        if (footerOverlap) record.failures.push('floating overlaps footer');
        if (width <= 1024) {{
          await page.evaluate(() => window.scrollTo(0, 0));
          await page.click('[data-menu-toggle]');
          await page.waitForTimeout(280);
          const menuMetrics = await page.evaluate(() => {{
            const menu = document.querySelector('#mobile-menu');
            const dialog = document.querySelector('.sf-mobile-dialog');
            const rect = dialog?.getBoundingClientRect();
            const parseColor = (value) => {{
              const match = String(value || '').match(/rgba?\\(([^)]+)\\)/);
              if (!match) return null;
              const parts = match[1].split(',').map((part) => Number.parseFloat(part.trim()));
              if (parts.length < 3) return null;
              return {{ r: parts[0], g: parts[1], b: parts[2], a: parts[3] ?? 1 }};
            }};
            const luminance = (color) => {{
              const values = [color.r, color.g, color.b].map((part) => {{
                const c = part / 255;
                return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
              }});
              return values[0] * 0.2126 + values[1] * 0.7152 + values[2] * 0.0722;
            }};
            const contrast = (fg, bg) => {{
              if (!fg || !bg) return 0;
              const a = luminance(fg) + 0.05;
              const b = luminance(bg) + 0.05;
              return a > b ? a / b : b / a;
            }};
            const effectiveBackground = (el) => {{
              let node = el;
              while (node && node !== document.documentElement) {{
                const color = parseColor(getComputedStyle(node).backgroundColor);
                if (color && color.a > 0.92) return color;
                node = node.parentElement;
              }}
              return parseColor('rgb(251, 248, 240)');
            }};
            const contrastTargets = [...document.querySelectorAll('.sf-mobile-dialog a, .sf-mobile-dialog button')];
            const menuContrastOk = contrastTargets.every((el) => {{
              const style = getComputedStyle(el);
              return contrast(parseColor(style.color), effectiveBackground(el)) >= 4.5;
            }});
            const labels = [...document.querySelectorAll('.sf-mobile-nav [data-main-nav="true"]')].filter((el) => getComputedStyle(el).display !== 'none').map((el) => el.textContent.replace(/\\s+/g, ' ').replace(/^\\d{{2}}\\s*/, '').trim());
            return {{
              open: menu?.getAttribute('aria-hidden') === 'false',
              labels,
              dialogFits: rect ? rect.width <= window.innerWidth && rect.height <= window.innerHeight : false,
              menuOverflow: document.documentElement.scrollWidth > window.innerWidth + 2,
              menuContrastOk,
            }};
          }});
          Object.assign(record, menuMetrics);
          if (!menuMetrics.open) record.failures.push('mobile menu open');
          if (!same(menuMetrics.labels || [], requiredMain)) record.failures.push('mobile menu visible links');
          if (!menuMetrics.dialogFits || menuMetrics.menuOverflow) record.failures.push('mobile menu fit');
          if (!menuMetrics.menuContrastOk) record.failures.push('mobile menu contrast');
        }}
        if (failedRequests.length) record.failures.push('missing request/asset');
        if (consoleErrors.length) record.failures.push('console errors');
        record.failedRequests = failedRequests.slice(0, 5);
        record.consoleErrors = consoleErrors.slice(0, 5);
      }} catch (error) {{
        record.failures.push(String(error.message || error));
      }}
      record.status = record.failures.length ? 'FAIL' : 'PASS';
      results.push(record);
    }}
    await context.close();
  }}
  await browser.close();
  console.log(JSON.stringify(results));
}})().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
    completed = subprocess.run(
        ["node", "-e", node_script],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=True,
    )
    return json.loads(completed.stdout)


def write_report(static_results: list[StaticPageResult], rendered_results: list[dict] | None) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    static_failures = [row for row in static_results if row.failures]
    rendered_failures = [row for row in rendered_results or [] if row.get("failures")]
    failure_counter = Counter()
    for row in rendered_failures:
        failure_counter.update(row.get("failures", []))

    summary = {
        "pages": len(static_results),
        "static_failures": len(static_failures),
        "rendered_checks": len(rendered_results or []),
        "rendered_failures": len(rendered_failures),
        "viewports": VIEWPORTS if rendered_results is not None else [],
        "rendered_failure_types": dict(failure_counter),
        "static": [row.__dict__ | {"status": row.status} for row in static_results],
        "rendered": rendered_results,
    }
    json_path = DOCS_DIR / "sofiati-full-site-qa.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Sofiati Full Site QA",
        "",
        f"- Public pages audited: {len(static_results)}",
        f"- Static failures: {len(static_failures)}",
        f"- Rendered checks: {len(rendered_results or [])}",
        f"- Rendered failures: {len(rendered_failures)}",
        f"- Viewports: {', '.join(str(v) for v in (VIEWPORTS if rendered_results is not None else [])) or 'not run'}",
        "",
    ]
    if failure_counter:
        lines.extend(["## Rendered Failure Types", ""])
        for key, value in failure_counter.most_common():
            lines.append(f"- {key}: {value}")
        lines.append("")
    if static_failures:
        lines.extend(["## Static Failures", ""])
        for row in static_failures[:200]:
            lines.append(f"- {row.path}: {'; '.join(row.failures)}")
        if len(static_failures) > 200:
            lines.append(f"- ... {len(static_failures) - 200} more")
        lines.append("")
    if rendered_failures:
        lines.extend(["## Rendered Failures", ""])
        for row in rendered_failures[:300]:
            lines.append(f"- {row['page']} @ {row['width']}px: {', '.join(row.get('failures') or [])}")
        if len(rendered_failures) > 300:
            lines.append(f"- ... {len(rendered_failures) - 300} more")
    md_path = DOCS_DIR / "sofiati-full-site-qa.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Full Sofiati QA across all concept pages.")
    parser.add_argument("--render", action="store_true", help="Run rendered checks for every page and breakpoint.")
    parser.add_argument("--limit", type=int, default=0, help="Limit rendered page count for debugging.")
    parser.add_argument("--port", type=int, default=0)
    args = parser.parse_args()

    static_results = static_audit()
    rendered_results = None
    server = None
    try:
        if args.render:
            port = args.port or free_port()
            server = run_server(port)
            time.sleep(0.6)
            rendered_results = rendered_audit(port, limit=args.limit or None)
    finally:
        if server is not None:
            server.terminate()
            try:
                server.wait(timeout=4)
            except subprocess.TimeoutExpired:
                server.kill()

    write_report(static_results, rendered_results)
    failures = sum(1 for row in static_results if row.failures)
    if rendered_results is not None:
        failures += sum(1 for row in rendered_results if row.get("failures"))
    print(
        f"Sofiati full-site QA: pages={len(static_results)} "
        f"rendered={len(rendered_results or [])} failures={failures}"
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
