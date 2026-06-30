#!/usr/bin/env python3
"""Audit Sofiati public partial systems statically and in rendered viewports."""

from __future__ import annotations

import argparse
import html
import json
import re
import socket
import subprocess
import sys
import time
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

try:
    from PIL import Image
except ImportError:  # pragma: no cover - reported as an audit failure if needed.
    Image = None


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
DOCS_DIR = ROOT / "docs" / "script-runs"
VIEWPORTS = [360, 390, 430, 768, 1024, 1280, 1440]

APPROVED_LOGO_FILES = [
    "assets/brand/sofiati-logo-primary.svg",
    "assets/brand/sofiati-logo-primary.png",
    "assets/brand/sofiati-logo-dark.svg",
    "assets/brand/sofiati-logo-light.svg",
    "assets/brand/sofiati-logo-sage.svg",
    "assets/brand/sofiati-logo-gold.svg",
    "assets/brand/sofiati-logo-monogram.svg",
    "assets/brand/sofiati-logo-monogram-light.svg",
    "assets/brand/sofiati-logo-monogram-dark.svg",
    "assets/brand/sofiati-logo-primary-transparent.png",
    "assets/brand/sofiati-logo-dark-transparent.png",
    "assets/brand/sofiati-logo-light-transparent.png",
    "assets/brand/sofiati-logo-sage-transparent.png",
    "assets/brand/sofiati-logo-gold-transparent.png",
    "assets/brand/sofiati-logo-monogram-transparent.png",
    "assets/brand/sofiati-logo-monogram-light-transparent.png",
    "assets/brand/sofiati-logo-monogram-dark-transparent.png",
]

OLD_LOGO_REFS = [
    "sofiati-logo-primary-sage.png",
    "sofiati-logo-primary-white.png",
    "sofiati-logo-primary-bronze.png",
    "sofiati-signature-sage.png",
    "sofiati-signature-white.png",
    "sofiati-monogram-sage.png",
    "sofiati-monogram-white.png",
    "sofiati-monogram-bronze.png",
]

REQUIRED_MAIN = [
    "Home",
    "About",
    "Care",
    "Laser",
    "Skin",
    "Results",
    "Journal",
    "Contact",
]

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


class TextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []
        self.skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.skip_depth += 1
            return
        attr_map = {key.lower(): value or "" for key, value in attrs}
        if tag == "img" and attr_map.get("alt"):
            self.parts.append(html.unescape(attr_map["alt"]).strip())
        if tag == "meta":
            key = attr_map.get("name") or attr_map.get("property")
            if key in {"description", "og:title", "og:description", "twitter:title", "twitter:description"}:
                content = html.unescape(attr_map.get("content", "")).strip()
                if content:
                    self.parts.append(content)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"} and self.skip_depth:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.skip_depth:
            return
        value = html.unescape(data).strip()
        if value:
            self.parts.append(value)

    @property
    def text(self) -> str:
        return " ".join(self.parts)


@dataclass
class StaticResult:
    concept: str
    number: str
    header_structure: str
    desktop_count: int
    mobile_structure: str
    mobile_count: int
    footer_structure: str
    footer_count: int
    banner_present: bool
    banner_separate: bool
    footer_brand: bool
    footer_description: bool
    footer_contact: bool
    footer_cta: bool
    copyright_present: bool
    header_cta: bool
    whatsapp_present: bool
    whatsapp_count: int
    accessibility_present: bool
    accessibility_count: int
    back_to_top_present: bool
    back_to_top_count: int
    approved_logo_refs: bool
    visually_distinct: bool
    stale_logo_refs: list[str] = field(default_factory=list)
    fs_text_marks: int = 0
    leaks: list[str] = field(default_factory=list)
    failures: list[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        return "PASS" if not self.failures else "FAIL"


def concept_dirs() -> list[Path]:
    return sorted(
        [p for p in CONCEPTS_DIR.iterdir() if p.is_dir() and re.match(r"^\d{2}-", p.name)],
        key=lambda p: p.name,
    )


def read(concept: Path, name: str) -> str:
    return (concept / "partials" / f"{name}.html").read_text(encoding="utf-8")


def attr(html_text: str, key: str) -> str:
    match = re.search(rf'{key}="([^"]+)"', html_text)
    return match.group(1) if match else ""


def text_of(*chunks: str) -> str:
    parser = TextExtractor()
    for chunk in chunks:
        parser.feed(chunk)
    return parser.text


def labels_from_links(chunk: str, marker: str) -> list[str]:
    labels: list[str] = []
    for match in re.finditer(rf"<a\b[^>]*{re.escape(marker)}[^>]*>(.*?)</a>", chunk, flags=re.S):
        parser = TextExtractor()
        parser.feed(match.group(1))
        label = re.sub(r"^\d{2}", "", parser.text).strip()
        labels.append(label)
    return labels


def visible_leaks(concept: Path, *chunks: str) -> list[str]:
    text = text_of(*chunks)
    slug = concept.name.split("-", 1)[1]
    title = slug.replace("-", " ").title()
    leak_terms = [title, "Destination", "Open concept", "website direction", "concept direction", concept.name]
    leaks = []
    for term in leak_terms:
        if term and re.search(rf"\b{re.escape(term)}\b", text):
            leaks.append(term)
    return sorted(set(leaks))


def html_files_for_audit(concept: Path) -> list[Path]:
    return [path for path in sorted(concept.glob("*.html")) if ".bak" not in path.name]


def public_page_leaks(concept: Path) -> list[str]:
    chunks = []
    for page in html_files_for_audit(concept):
        chunks.append(page.read_text(encoding="utf-8"))
    text = text_of(*chunks)
    slug = concept.name.split("-", 1)[1]
    title = slug.replace("-", " ").title()
    leak_terms = [
        title,
        "Destination",
        "Open concept",
        "website direction",
        "concept direction",
        "direction shapes the pacing",
        "translated into a premium",
        "luxury independent publication",
        "dark premium editorial",
    ]
    leaks = []
    for term in leak_terms:
        flags = 0 if term == title else re.I
        if term and re.search(rf"\b{re.escape(term)}\b", text, flags=flags):
            leaks.append(term)
    if re.search(r"\b(?:Section|Step)\s+\d{1,2}\b", text):
        leaks.append("Section/Step number label")
    return sorted(set(leaks))


def scan_public_files(concept: Path) -> str:
    chunks = []
    for page in html_files_for_audit(concept):
        chunks.append(page.read_text(encoding="utf-8"))
    for partial in sorted((concept / "partials").glob("*.html")):
        if ".bak" not in partial.name:
            chunks.append(partial.read_text(encoding="utf-8"))
    return "\n".join(chunks)


def stale_logo_refs(text: str) -> list[str]:
    return sorted({name for name in OLD_LOGO_REFS if name in text})


def fs_text_mark_count(text: str) -> int:
    return len(re.findall(r">\s*FS\s*<|>\s*FS\s*$|^\s*FS\s*<", text, flags=re.M))


def global_logo_asset_failures() -> list[str]:
    failures: list[str] = []
    for rel in APPROVED_LOGO_FILES:
        path = ROOT / rel
        if not path.exists():
            failures.append(f"missing approved logo asset: {rel}")
    if Image is None:
        failures.append("Pillow unavailable for transparent-logo alpha verification")
    else:
        for rel in APPROVED_LOGO_FILES:
            if not rel.endswith(".png") or "transparent" not in rel:
                continue
            path = ROOT / rel
            if not path.exists():
                continue
            image = Image.open(path).convert("RGBA")
            alpha = image.getchannel("A")
            if alpha.getextrema()[0] > 0:
                failures.append(f"transparent logo has no transparent pixels: {rel}")
    return failures


def static_audit() -> list[StaticResult]:
    results: list[StaticResult] = []
    seen_signatures: set[tuple[str, str, str]] = set()
    for concept in concept_dirs():
        number = concept.name[:2]
        header = read(concept, "header")
        mobile = read(concept, "mobile-menu")
        footer = read(concept, "footer")
        cookie = read(concept, "cookie-banner")
        floating = read(concept, "floating-widgets")
        public_files_text = scan_public_files(concept)

        desktop_labels = labels_from_links(header, 'data-main-nav="true"')
        mobile_labels = labels_from_links(mobile, 'data-main-nav="true"')
        footer_labels = labels_from_links(footer, 'data-footer-link="true"')
        signature = (
            attr(header, "data-structure"),
            attr(mobile, "class"),
            attr(footer, "class"),
        )
        visually_distinct = signature not in seen_signatures
        seen_signatures.add(signature)

        result = StaticResult(
            concept=concept.name,
            number=number,
            header_structure=attr(header, "data-structure"),
            desktop_count=len(desktop_labels),
            mobile_structure=attr(mobile, "class"),
            mobile_count=len(mobile_labels),
            footer_structure=attr(footer, "data-structure"),
            footer_count=len(footer_labels),
            banner_present="sf-identity-banner" in header,
            banner_separate="sf-identity-banner" not in mobile,
            footer_brand="Franciele Sofiati Biomédica" in footer and "sf-footer-brand" in footer,
            footer_description="Biomedicine-led skin, laser and aesthetic care" in footer,
            footer_contact="sf-footer-contact" in footer and "Londrina, PR / Brazil" in footer,
            footer_cta="data-footer-cta" in footer and "Contact the clinic" in footer,
            copyright_present="© 2026 Franciele Sofiati Biomédica. All rights reserved." in footer,
            header_cta="data-header-cta" in header and "Consultation" in header,
            whatsapp_present="sf-floating-whatsapp" in floating and "https://wa.me/5543991043536" in floating,
            whatsapp_count=floating.count("sf-floating-whatsapp"),
            accessibility_present="accessibility.html" in header and "accessibility.html" in mobile and "Accessibility" in footer and "sf-floating-accessibility" in floating,
            accessibility_count=floating.count("sf-floating-accessibility"),
            back_to_top_present="data-back-to-top" in floating,
            back_to_top_count=floating.count("data-back-to-top"),
            approved_logo_refs="sofiati-logo-primary-transparent.png" in header
            and "sofiati-logo-primary-transparent.png" in footer
            and "sofiati-logo-monogram" in header
            and "sofiati-logo-monogram" in mobile,
            visually_distinct=visually_distinct,
            stale_logo_refs=stale_logo_refs(public_files_text),
            fs_text_marks=fs_text_mark_count(header + mobile + footer + floating),
            leaks=sorted(set(visible_leaks(concept, header, mobile, footer, cookie, floating) + public_page_leaks(concept))),
        )

        checks = {
            "desktop nav links = exactly 8": result.desktop_count == 8,
            "desktop nav labels match required set": desktop_labels == REQUIRED_MAIN,
            "mobile nav links = exactly 8": result.mobile_count == 8,
            "mobile nav labels match required set": mobile_labels == REQUIRED_MAIN,
            "footer sitemap links = exactly 17": result.footer_count == 17,
            "footer labels match required set": footer_labels == REQUIRED_FOOTER,
            "top EN/PT banner present": result.banner_present,
            "top EN/PT banner separate from menu": result.banner_separate,
            "footer brand/logo present": result.footer_brand,
            "footer description present": result.footer_description,
            "footer contact details present": result.footer_contact,
            "footer secondary CTA present": result.footer_cta,
            "footer copyright present": result.copyright_present,
            "header Consultation CTA present": result.header_cta,
            "WhatsApp present": result.whatsapp_present,
            "exactly one floating WhatsApp": result.whatsapp_count == 1,
            "Accessibility present": result.accessibility_present,
            "exactly one floating accessibility control": result.accessibility_count == 1,
            "Back to top present": result.back_to_top_present,
            "exactly one back-to-top control": result.back_to_top_count == 1,
            "approved logo references present": result.approved_logo_refs,
            "no stale logo references in public pages/partials": not result.stale_logo_refs,
            "no FS text marks": result.fs_text_marks == 0,
            "visual difference from previous concept": result.visually_distinct,
            "no public-facing internal labels in pages/partials": not result.leaks,
        }
        result.failures.extend([name for name, passed in checks.items() if not passed])
        results.append(result)
    return results


def free_port(start: int = 8000) -> int:
    for port in range(start, start + 80):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            if sock.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError("No free local port found")


def rendered_audit(port: int, headed: bool) -> list[dict]:
    concepts = [p.name for p in concept_dirs()]
    node_script = f"""
const {{ chromium }} = require('playwright');
const concepts = {json.dumps(concepts)};
const widths = {json.dumps(VIEWPORTS)};
const port = {port};
const headed = {str(headed).lower()};

const waitForPartials = async (page) => {{
  await page.waitForFunction(() => {{
    const names = ['header', 'mobile-menu', 'footer', 'cookie-banner', 'floating-widgets'];
    return names.every((name) => document.querySelector(`[data-sofiati-partial="${{name}}"]`)?.dataset.partialLoaded === 'true');
  }}, null, {{ timeout: 10000 }});
}};

(async () => {{
  const browser = await chromium.launch({{ headless: !headed }});
  const results = [];
  for (const width of widths) {{
    const context = await browser.newContext({{ viewport: {{ width, height: 950 }}, deviceScaleFactor: 1 }});
    const page = await context.newPage();
    await page.route('**/*', (route) => {{
      const request = route.request();
      const url = request.url();
      if (request.resourceType() === 'image' && !/sofiati-logo|sofiati-favicon/.test(url)) {{
        route.abort();
        return;
      }}
      route.continue();
    }});
    for (const concept of concepts) {{
      const url = `http://127.0.0.1:${{port}}/concepts/${{concept}}/index.html`;
      const record = {{ concept, width, status: 'PASS', failures: [] }};
      try {{
        await page.goto(url, {{ waitUntil: 'domcontentloaded', timeout: 15000 }});
        await waitForPartials(page);
        await page.waitForFunction(() => {{
          const logos = [...document.querySelectorAll('.sf-logo-img')];
          return logos.length >= 3 && logos.every((img) => img.complete && img.naturalWidth > 0);
        }}, null, {{ timeout: 3000 }}).catch(() => {{}});
        const metrics = await page.evaluate(() => {{
          const by = (selector) => [...document.querySelectorAll(selector)];
          const visible = (el) => {{
            const style = getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return style.display !== 'none' && style.visibility !== 'hidden' && rect.width > 0 && rect.height > 0;
          }};
          const desktopLinks = by('.sf-desktop-nav [data-main-nav="true"]');
          const mobileLinks = by('.sf-mobile-nav [data-main-nav="true"]');
          const footerLinks = by('.sf-footer-sitemap [data-footer-link="true"]');
          const doc = document.documentElement;
          const viewport = window.innerWidth;
          const textFits = by('.sf-public-header a, .sf-public-header button, .sf-mobile-menu a, .sf-mobile-menu button, .sf-public-footer a, .sf-cookie-banner a, .sf-cookie-banner button').every((el) => {{
            return el.scrollWidth <= el.clientWidth + 3 || getComputedStyle(el).whiteSpace !== 'nowrap';
          }});
          const desktopRects = desktopLinks
            .filter((el) => getComputedStyle(el).display !== 'none')
            .map((el) => {{
              const rect = el.getBoundingClientRect();
              return {{ left: rect.left, top: rect.top, right: rect.right, bottom: rect.bottom }};
            }});
          let navOverlap = false;
          for (let i = 0; i < desktopRects.length; i += 1) {{
            for (let j = i + 1; j < desktopRects.length; j += 1) {{
              const a = desktopRects[i];
              const b = desktopRects[j];
              const overlaps = !(a.right <= b.left || b.right <= a.left || a.bottom <= b.top || b.bottom <= a.top);
              if (Math.abs(a.top - b.top) < 2 && overlaps) navOverlap = true;
            }}
          }}
          const pageOverflow = doc.scrollWidth <= viewport + 2;
          const menu = document.querySelector('#mobile-menu');
          const bannerInsideMenu = !!document.querySelector('#mobile-menu .sf-identity-banner');
          const floating = document.querySelector('.sf-floating-tools');
          const whatsapps = by('.sf-floating-tools .sf-floating-whatsapp');
          const accessButtons = by('.sf-floating-tools .sf-floating-accessibility');
          const backTops = by('.sf-floating-tools .sf-back-to-top');
          const whatsapp = whatsapps[0];
          const accessibility = accessButtons[0];
          const backTop = backTops[0];
          const floatingOrder = floating && whatsapp && accessibility && backTop
            ? whatsapp.getBoundingClientRect().top <= accessibility.getBoundingClientRect().top && accessibility.getBoundingClientRect().top <= backTop.getBoundingClientRect().top
            : false;
          const menuButton = document.querySelector('[data-menu-toggle]');
          const banner = document.querySelector('.sf-identity-banner');
          const logos = by('.sf-logo-img');
          const staleLogoRefs = by('img').filter((img) => /sofiati-(?:logo-primary-sage|signature-sage|monogram-sage|logo-primary-white|logo-primary-bronze|monogram-white|monogram-bronze)\\.png/.test(img.getAttribute('src') || '')).length;
          const approvedLogosLoaded = logos.length >= 3 && logos.every((img) => img.complete && img.naturalWidth > 0 && /sofiati-logo-/.test(img.getAttribute('src') || ''));
          return {{
            desktopCount: desktopLinks.length,
            desktopVisibleCount: desktopLinks.filter(visible).length,
            mobileCount: mobileLinks.length,
            footerCount: footerLinks.length,
            bannerPresent: !!document.querySelector('.sf-identity-banner'),
            bannerHeight: banner ? banner.getBoundingClientRect().height : 0,
            bannerInsideMenu,
            headerCta: !!document.querySelector('[data-header-cta]'),
            whatsappPresent: whatsapps.length === 1,
            whatsappCount: whatsapps.length,
            accessibilityPresent: accessButtons.length === 1,
            accessibilityCount: accessButtons.length,
            backTopPresent: backTops.length === 1,
            backTopCount: backTops.length,
            floatingOrder,
            approvedLogosLoaded,
            staleLogoRefs,
            menuButtonVisible: menuButton ? visible(menuButton) : false,
            pageOverflow,
            textFits,
            navOverlap,
            menuHiddenInitial: menu?.getAttribute('aria-hidden') === 'true',
          }};
        }});
        Object.assign(record, metrics);
        if (metrics.desktopCount !== 8) record.failures.push('desktop nav count');
        if (metrics.mobileCount !== 8) record.failures.push('mobile nav count');
        if (metrics.footerCount !== 17) record.failures.push('footer sitemap count');
        if (!metrics.bannerPresent) record.failures.push('banner missing');
        if (metrics.bannerInsideMenu) record.failures.push('banner inside menu');
        if (!metrics.headerCta) record.failures.push('header cta missing');
        if (!metrics.whatsappPresent) record.failures.push('whatsapp missing');
        if (metrics.whatsappCount !== 1) record.failures.push('whatsapp count');
        if (!metrics.accessibilityPresent) record.failures.push('accessibility missing');
        if (metrics.accessibilityCount !== 1) record.failures.push('accessibility count');
        if (!metrics.backTopPresent) record.failures.push('back-to-top missing');
        if (metrics.backTopCount !== 1) record.failures.push('back-to-top count');
        if (!metrics.floatingOrder) record.failures.push('floating order');
        if (!metrics.approvedLogosLoaded) record.failures.push('approved logo load');
        if (metrics.staleLogoRefs) record.failures.push('stale logo reference');
        if (!metrics.pageOverflow) record.failures.push('horizontal overflow');
        if (!metrics.textFits) record.failures.push('text clipping');
        if (metrics.navOverlap) record.failures.push('nav overlap');
        if (!metrics.menuHiddenInitial) record.failures.push('mobile menu initially visible');
        if (width >= 1280 && metrics.desktopVisibleCount !== 8) record.failures.push('desktop visible nav count');
        if (width <= 1024 && !metrics.menuButtonVisible) record.failures.push('tablet/mobile menu button hidden');
        if (width <= 1024 && metrics.desktopVisibleCount !== 0) record.failures.push('tablet/mobile desktop nav visible');
        if (width <= 430 && metrics.bannerHeight > 46) record.failures.push('mobile banner height');
        await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
        await page.waitForTimeout(80);
        const footerMetrics = await page.evaluate(() => {{
          const floating = document.querySelector('.sf-floating-tools');
          const footerTargets = [...document.querySelectorAll('.sf-footer-sitemap a, .sf-footer-cta, .sf-footer-close p')];
          const floatingRect = floating?.getBoundingClientRect();
          let footerOverlap = false;
          if (floatingRect) {{
            for (const target of footerTargets) {{
              const rect = target.getBoundingClientRect();
              const overlaps = !(floatingRect.right <= rect.left || rect.right <= floatingRect.left || floatingRect.bottom <= rect.top || rect.bottom <= floatingRect.top);
              if (overlaps) footerOverlap = true;
            }}
          }}
          return {{ footerOverlap }};
        }});
        Object.assign(record, footerMetrics);
        if (footerMetrics.footerOverlap) record.failures.push('floating overlaps footer');
        await page.evaluate(() => window.scrollTo(0, 0));
        if (width <= 1024) {{
          await page.click('[data-menu-toggle]');
          await page.waitForTimeout(120);
          const menuMetrics = await page.evaluate(() => {{
            const menu = document.querySelector('#mobile-menu');
            const dialog = document.querySelector('.sf-mobile-dialog');
            const links = [...document.querySelectorAll('.sf-mobile-nav [data-main-nav="true"]')];
            const rect = dialog?.getBoundingClientRect();
            return {{
              open: menu?.getAttribute('aria-hidden') === 'false',
              menuLinkCount: links.filter((link) => getComputedStyle(link).display !== 'none').length,
              menuOverflow: document.documentElement.scrollWidth > window.innerWidth + 2,
              dialogFits: rect ? rect.width <= window.innerWidth && rect.height <= window.innerHeight : false,
            }};
          }});
          Object.assign(record, menuMetrics);
          if (!menuMetrics.open) record.failures.push('mobile menu did not open');
          if (menuMetrics.menuLinkCount !== 8) record.failures.push('mobile menu visible link count');
          if (menuMetrics.menuOverflow) record.failures.push('mobile menu overflow');
          if (!menuMetrics.dialogFits) record.failures.push('mobile dialog fit');
        }}
      }} catch (error) {{
        record.status = 'FAIL';
        record.failures.push(String(error.message || error));
      }}
      if (record.failures.length) record.status = 'FAIL';
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
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(completed.stdout)


def run_server(port: int) -> subprocess.Popen:
    return subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"],
        cwd=ROOT,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def write_reports(static_results: list[StaticResult], rendered_results: list[dict] | None, global_failures: list[str]) -> None:
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    rendered_failures_by_concept: dict[str, list[str]] = {}
    if rendered_results is not None:
        for row in rendered_results:
            if row.get("status") == "PASS":
                continue
            rendered_failures_by_concept.setdefault(row["concept"], []).append(
                f"{row['width']}px: {', '.join(row.get('failures') or [])}"
            )

    rows = []
    for result in static_results:
        failures = list(result.failures)
        failures.extend(rendered_failures_by_concept.get(result.concept, []))
        rows.append(
            {
                "concept": result.concept,
                "concept_number": result.number,
                "desktop_header_structure": result.header_structure,
                "desktop_nav_link_count": result.desktop_count,
                "mobile_menu_structure": result.mobile_structure,
                "mobile_nav_link_count": result.mobile_count,
                "footer_sitemap_structure": result.footer_structure,
                "footer_sitemap_link_count": result.footer_count,
                "top_en_pt_banner_present": result.banner_present,
                "top_en_pt_banner_separate_from_menu": result.banner_separate,
                "footer_brand_logo_present": result.footer_brand,
                "footer_description_present": result.footer_description,
                "footer_contact_details_present": result.footer_contact,
                "footer_secondary_cta_present": result.footer_cta,
                "footer_copyright_present": result.copyright_present,
                "header_consultation_cta_present": result.header_cta,
                "whatsapp_present": result.whatsapp_present,
                "whatsapp_count": result.whatsapp_count,
                "accessibility_present": result.accessibility_present,
                "accessibility_count": result.accessibility_count,
                "back_to_top_present": result.back_to_top_present,
                "back_to_top_count": result.back_to_top_count,
                "approved_logo_refs_present": result.approved_logo_refs,
                "stale_logo_refs": result.stale_logo_refs,
                "fs_text_marks": result.fs_text_marks,
                "visual_difference_from_previous_concept": result.visually_distinct,
                "status": "PASS" if not failures else "FAIL",
                "failures": failures,
                "leaks": result.leaks,
            }
        )

    summary = {
        "static_concepts": len(static_results),
        "rendered_checks": len(rendered_results or []),
        "viewports": VIEWPORTS if rendered_results is not None else [],
        "failures": sum(1 for row in rows if row["status"] != "PASS") + len(global_failures),
        "global_failures": global_failures,
        "rows": rows,
        "rendered": rendered_results,
    }

    json_path = DOCS_DIR / "public-partials-final-audit.json"
    json_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Public Partials Final Audit",
        "",
        f"- Concepts audited: {len(static_results)}",
        f"- Rendered checks: {len(rendered_results or [])}",
        f"- Viewports: {', '.join(str(v) for v in (VIEWPORTS if rendered_results is not None else [])) or 'not run'}",
        f"- Total failing checks/concepts: {summary['failures']}",
        f"- Global failures: {len(global_failures)}",
        "",
        "| # | Header | Desktop nav | Mobile | Mobile nav | Footer | Footer links | EN/PT | Footer brand | Footer description | Footer contact | Footer CTA | Copyright | Header CTA | Logo refs | WhatsApp | A11y | Back top | Distinct | Status |",
        "|---|---|---:|---|---:|---|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            "| {concept_number} | {desktop_header_structure} | {desktop_nav_link_count} | {mobile_menu_structure} | {mobile_nav_link_count} | {footer_sitemap_structure} | {footer_sitemap_link_count} | {top_en_pt_banner_separate_from_menu} | {footer_brand_logo_present} | {footer_description_present} | {footer_contact_details_present} | {footer_secondary_cta_present} | {footer_copyright_present} | {header_consultation_cta_present} | {approved_logo_refs_present} | {whatsapp_count} | {accessibility_count} | {back_to_top_count} | {visual_difference_from_previous_concept} | {status} |".format(**row)
        )
    if global_failures:
        lines.extend(["", "## Global Failures", ""])
        for failure in global_failures:
            lines.append(f"- {failure}")
    failures = [row for row in rows if row["status"] != "PASS"]
    if failures:
        lines.extend(["", "## Failures", ""])
        for row in failures:
            lines.append(f"- {row['concept']}: {'; '.join(row['failures'])}")
    md_path = DOCS_DIR / "public-partials-final-audit.md"
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Sofiati final public partial systems.")
    parser.add_argument("--render", action="store_true", help="Run Playwright-rendered responsive checks.")
    parser.add_argument("--headed", action="store_true", help="Run Playwright in headed mode.")
    parser.add_argument("--port", type=int, default=0, help="Port for the temporary static server.")
    args = parser.parse_args()

    global_failures = global_logo_asset_failures()
    static_results = static_audit()
    rendered_results = None
    server = None
    try:
      if args.render:
          port = args.port or free_port()
          server = run_server(port)
          time.sleep(0.8)
          rendered_results = rendered_audit(port, args.headed)
    finally:
      if server is not None:
          server.terminate()
          try:
              server.wait(timeout=4)
          except subprocess.TimeoutExpired:
              server.kill()

    write_reports(static_results, rendered_results, global_failures)
    failures = len(global_failures) + sum(1 for row in static_results if row.status != "PASS")
    if rendered_results is not None:
        failures += sum(1 for row in rendered_results if row.get("status") != "PASS")
    print(f"Public partial audit: concepts={len(static_results)} rendered={len(rendered_results or [])} failures={failures}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
