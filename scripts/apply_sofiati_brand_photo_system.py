#!/usr/bin/env python3
"""Integrate the Sofiati real-photo brand system into all concept sites."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
MANIFEST_PATH = ROOT / "assets" / "brand-photos" / "image-manifest.json"
SITE_URL = "https://www.sofiati.com/"

PHOTO_CSS_START = "/* SOFIATI REAL PHOTO SYSTEM START */"
PHOTO_CSS_END = "/* SOFIATI REAL PHOTO SYSTEM END */"

VARIANTS = (
    "botanical-panel",
    "sage-editorial",
    "ivory-oval",
    "gold-clinical",
    "window-light",
    "studio-luxe",
)

PAGE_CATEGORY = {
    "index": "hero",
    "about": "about",
    "care": "care",
    "skin": "skin",
    "laser": "laser",
    "results": "results",
    "consultation": "consultation",
    "contact": "contact",
    "journal": "journal",
    "blog": "journal",
    "faq": "decorative",
    "mission": "about",
    "values": "decorative",
    "testimonials": "contact",
    "legal": "footer",
    "privacy": "footer",
    "cookies": "footer",
    "accessibility": "footer",
    "sitemap": "footer",
    "404": "footer",
}

HOME_INDEX_CATEGORY = {
    "credentials": "about",
    "philosophy": "care",
    "laser": "laser",
    "skin": "skin",
    "results": "results",
    "journal": "journal",
    "mission": "about",
    "values": "decorative",
    "faq": "consultation",
}

CATEGORY_MIXES = {
    "hero": ("hero", "about", "consultation"),
    "about": ("about", "profile", "hero"),
    "care": ("care", "consultation", "skin", "service-support"),
    "skin": ("skin", "journal", "care", "decorative"),
    "laser": ("laser", "service-support", "hero", "results"),
    "results": ("results", "about", "service-support", "laser"),
    "consultation": ("consultation", "contact", "CTA", "hero"),
    "contact": ("contact", "profile", "consultation"),
    "journal": ("journal", "decorative", "skin"),
    "decorative": ("decorative", "journal", "about"),
    "service-support": ("service-support", "laser", "care", "skin"),
    "CTA": ("CTA", "consultation", "hero"),
    "footer": ("footer", "profile", "contact"),
    "profile": ("profile", "contact", "about"),
}


@dataclass(frozen=True)
class PhotoItem:
    path: str
    entry: dict[str, object]
    category: str


def load_manifest() -> tuple[dict[str, list[PhotoItem]], dict[str, dict[str, object]]]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    entries_by_id = {entry["id"]: entry for entry in manifest["entries"]}
    pools: dict[str, list[PhotoItem]] = {}
    for category, paths in manifest["usage_pools"].items():
        category_items: list[PhotoItem] = []
        for path in paths:
            matched = None
            for entry in manifest["entries"]:
                if path in entry.get("category_files", {}).values():
                    matched = entry
                    break
            if matched is None:
                continue
            category_items.append(PhotoItem(path=path, entry=matched, category=category))
        pools[category] = category_items
    return pools, entries_by_id


POOLS, _ENTRIES_BY_ID = load_manifest()


def concept_number(concept_dir: Path) -> int:
    return int(concept_dir.name.split("-", 1)[0])


def concept_label(concept_dir: Path) -> str:
    return concept_dir.name.split("-", 1)[1].replace("-", " ").title()


def page_name(path: Path) -> str:
    return path.stem


def mixed_pool(category: str) -> list[PhotoItem]:
    categories = CATEGORY_MIXES.get(category, (category,))
    items: list[PhotoItem] = []
    seen: set[str] = set()
    for cat in categories:
        for item in POOLS.get(cat, []):
            key = f"{cat}:{item.path}"
            if key in seen:
                continue
            seen.add(key)
            items.append(item)
    if not items:
        items = POOLS["profile"]
    return items


def choose(category: str, concept_idx: int, page: str, salt: int = 0) -> PhotoItem:
    items = mixed_pool(category)
    page_salt = sum(ord(char) for char in page)
    return items[(concept_idx * 5 + page_salt + salt * 7) % len(items)]


def html_path(item: PhotoItem) -> str:
    return "../../" + item.path


def absolute_path(item: PhotoItem) -> str:
    return SITE_URL + item.path


def dims_for_html_path(path_value: str) -> tuple[int, int] | None:
    repo_rel = path_value.removeprefix("../../")
    target = ROOT / repo_rel
    if not target.exists():
        return None
    with Image.open(target) as image:
        return image.size


def set_attr(tag: str, name: str, value: str | None) -> str:
    if value is None:
        return tag
    escaped = value.replace("&", "&amp;").replace('"', "&quot;")
    pattern = re.compile(rf'\s{name}="[^"]*"')
    if pattern.search(tag):
        return pattern.sub(f' {name}="{escaped}"', tag, count=1)
    close = tag.find(">")
    if close == -1:
        return tag
    return tag[:close] + f' {name}="{escaped}"' + tag[close:]


def remove_attr(tag: str, name: str) -> str:
    return re.sub(rf'\s{name}="[^"]*"', "", tag, count=1)


def merge_class(tag: str, classes: Iterable[str]) -> str:
    wanted = [cls for cls in classes if cls]
    match = re.search(r'\sclass="([^"]*)"', tag)
    if not match:
        return set_attr(tag, "class", " ".join(wanted))
    existing = match.group(1).split()
    for cls in wanted:
        if cls not in existing:
            existing.append(cls)
    return tag[: match.start(1)] + " ".join(existing) + tag[match.end(1) :]


def remove_class_prefixes(tag: str, prefixes: tuple[str, ...]) -> str:
    match = re.search(r'\sclass="([^"]*)"', tag)
    if not match:
        return tag
    existing = [
        cls
        for cls in match.group(1).split()
        if not any(cls.startswith(prefix) for prefix in prefixes)
    ]
    return tag[: match.start(1)] + " ".join(existing) + tag[match.end(1) :]


def set_style_var(tag: str, name: str, value: str) -> str:
    match = re.search(r'\sstyle="([^"]*)"', tag)
    declaration = f"{name}: {value};"
    if not match:
        close = tag.find(">")
        if close == -1:
            return tag
        return tag[:close] + f' style="{declaration}"' + tag[close:]
    styles = [part.strip() for part in match.group(1).split(";") if part.strip()]
    styles = [part for part in styles if not part.startswith(f"{name}:")]
    styles.append(declaration.rstrip(";"))
    return tag[: match.start(1)] + "; ".join(styles) + ";" + tag[match.end(1) :]


def photo_img(
    tag: str,
    item: PhotoItem,
    *,
    role_class: str,
    alt: str | None = None,
    loading: str = "lazy",
    decorative: bool = False,
    priority: bool = False,
) -> str:
    source = html_path(item)
    tag = remove_class_prefixes(tag, ("doctor-portrait--",))
    tag = set_attr(tag, "src", source)
    tag = set_attr(tag, "alt", "" if decorative else (alt or str(item.entry["alt_text"])))
    tag = set_attr(tag, "decoding", "async")
    tag = set_attr(tag, "loading", "eager" if priority else loading)
    tag = set_attr(tag, "data-brand-photo", item.entry["id"])
    tag = set_attr(tag, "data-photo-role", item.category)
    tag = merge_class(tag, ("doctor-portrait", role_class))
    tag = set_style_var(tag, "--photo-position", str(item.entry["object_position"]))
    dims = dims_for_html_path(source)
    if dims:
        width, height = dims
        tag = set_attr(tag, "width", str(width))
        tag = set_attr(tag, "height", str(height))
    if priority:
        tag = set_attr(tag, "fetchpriority", "high")
    else:
        tag = remove_attr(tag, "fetchpriority")
    if decorative:
        tag = set_attr(tag, "aria-hidden", "true")
    return tag


def photo_figure(tag: str, variant: str, frame_class: str, item: PhotoItem) -> str:
    tag = remove_class_prefixes(tag, ("photo-frame--",))
    tag = merge_class(tag, ("photo-frame", frame_class, f"photo-frame--{variant}"))
    tag = set_attr(tag, "data-photo-frame", frame_class.removeprefix("photo-frame--"))
    tag = set_style_var(tag, "--photo-position", str(item.entry["object_position"]))
    return tag


def body_with_variant(html: str, variant: str) -> str:
    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        tag = merge_class(tag, ("sf-photo-rebuilt",))
        tag = set_attr(tag, "data-photo-variant", variant)
        return tag

    return re.sub(r"<body\b[^>]*>", replace, html, count=1)


def repair_stray_figure_attrs(html: str) -> str:
    def replace(match: re.Match[str]) -> str:
        figure = match.group(1) + ">"
        attrs = re.findall(r'(data-photo-frame|style)="([^"]*)"', match.group(2))
        for name, value in attrs:
            figure = set_attr(figure, name, value)
        return figure + match.group(3)

    return re.sub(
        r"(<figure\b[^>]*?)>\s+((?:data-photo-frame|style)=\"[^\"]+\"(?:\s+(?:data-photo-frame|style)=\"[^\"]+\")*)>(\s*<img)",
        replace,
        html,
        flags=re.S,
    )


def update_meta_images(html: str, item: PhotoItem) -> str:
    image_url = absolute_path(item)

    def upsert_meta(markup: str, key_attr: str, key_value: str) -> str:
        pattern = re.compile(rf'<meta {key_attr}="{re.escape(key_value)}" content="[^"]*">')
        tag = f'<meta {key_attr}="{key_value}" content="{image_url}">'
        if pattern.search(markup):
            return pattern.sub(tag, markup, count=1)
        anchor = re.search(r'<meta name="twitter:card" content="summary_large_image">', markup)
        if anchor:
            return markup[: anchor.end()] + "\n  " + tag + markup[anchor.end() :]
        head = re.search(r"</head>", markup)
        if head:
            return markup[: head.start()] + "  " + tag + "\n" + markup[head.start() :]
        return markup

    html = upsert_meta(html, "property", "og:image")
    html = upsert_meta(html, "name", "twitter:image")
    return html


def replace_hero(html: str, concept_idx: int, page: str, variant: str) -> str:
    category = PAGE_CATEGORY.get(page, "hero")
    item = choose(category, concept_idx, page, 0)
    alt = f"{item.entry['alt_text']} for the {page.replace('-', ' ')} page"

    def replace(match: re.Match[str]) -> str:
        figure_open, img_tag = match.group(1), match.group(2)
        figure_open = photo_figure(figure_open, variant, "photo-frame--hero", item)
        img_tag = photo_img(
            img_tag,
            item,
            role_class="doctor-portrait--hero",
            alt=alt,
            loading="eager",
            priority=True,
        )
        return figure_open + img_tag

    return re.sub(
        r'(<figure class="[^"]*\bhero-visual\b[^"]*"[^>]*>\s*)(<img\b[^>]*>)',
        replace,
        html,
        count=1,
        flags=re.S,
    )


def replace_hero_mosaic(html: str, concept_idx: int, page: str) -> str:
    def replace_block(match: re.Match[str]) -> str:
        opening, body, closing = match.group(1), match.group(2), match.group(3)
        categories = ("decorative", PAGE_CATEGORY.get(page, "journal"), "journal")

        def replace_img(img_match: re.Match[str]) -> str:
            idx = replace_img.counter
            replace_img.counter += 1
            item = choose(categories[idx % len(categories)], concept_idx, page, idx + 2)
            return photo_img(
                img_match.group(0),
                item,
                role_class="doctor-portrait--mosaic",
                decorative=True,
                loading="lazy",
            )

        replace_img.counter = 0  # type: ignore[attr-defined]
        body = re.sub(r"<img\b[^>]*>", replace_img, body)
        return opening + body + closing

    return re.sub(
        r'(<div class="[^"]*\bhero-mosaic\b[^"]*"[^>]*>)(.*?)(</div>)',
        replace_block,
        html,
        flags=re.S,
    )


def replace_doctor_presence(html: str, concept_idx: int, page: str) -> str:
    item = choose("profile", concept_idx, page, 4)

    def replace(match: re.Match[str]) -> str:
        return match.group(1) + photo_img(
            match.group(2),
            item,
            role_class="doctor-portrait--presence",
            alt="Franciele Sofiati, CRBM 6277, advanced aesthetic biomedicine specialist in Londrina, PR",
            loading="lazy",
        )

    return re.sub(
        r'(<aside class="[^"]*\bdoctor-presence\b[^"]*"[^>]*>\s*)(<img\b[^>]*>)',
        replace,
        html,
        flags=re.S,
    )


def replace_storytelling(html: str, concept_idx: int, page: str, variant: str) -> str:
    category = PAGE_CATEGORY.get(page, "journal")

    def replace(match: re.Match[str]) -> str:
        item = choose(category, concept_idx, page, 8 + replace.counter)
        replace.counter += 1
        figure_open = photo_figure(match.group(1), variant, "photo-frame--story", item)
        img_tag = photo_img(
            match.group(2),
            item,
            role_class="doctor-portrait--story",
            alt=f"{item.entry['alt_text']} supporting the {page.replace('-', ' ')} guidance section",
            loading="lazy",
        )
        return figure_open + img_tag

    replace.counter = 0  # type: ignore[attr-defined]
    return re.sub(
        r'(<figure class="[^"]*\bstorytelling-gate-visual\b[^"]*"[^>]*>\s*)(<img\b[^>]*>)',
        replace,
        html,
        flags=re.S,
    )


def replace_home_sections(html: str, concept_idx: int, page: str, variant: str) -> str:
    def replace_section(match: re.Match[str]) -> str:
        section_open, section_body = match.group(1), match.group(2)
        data_home = re.search(r'data-home-index="([^"]+)"', section_open)
        category = HOME_INDEX_CATEGORY.get(data_home.group(1) if data_home else "", "decorative")
        item = choose(category, concept_idx, page, 15 + replace_section.counter)
        replace_section.counter += 1

        def replace_img(img_match: re.Match[str]) -> str:
            figure_open = photo_figure(img_match.group(1), variant, "photo-frame--section", item)
            img_tag = photo_img(
                img_match.group(2),
                item,
                role_class="doctor-portrait--section",
                alt=f"{item.entry['alt_text']} for Sofiati {category.replace('-', ' ')} guidance",
                loading="lazy",
            )
            return figure_open + img_tag

        section_body = re.sub(
            r"(<figure\b[^>]*>\s*)(<img\b[^>]*>)",
            replace_img,
            section_body,
            count=1,
            flags=re.S,
        )
        return section_open + section_body

    replace_section.counter = 0  # type: ignore[attr-defined]
    return re.sub(
        r'(<section class="[^"]*\bhome-index-section\b[^"]*"[^>]*>)(.*?)(?=</section>)',
        replace_section,
        html,
        flags=re.S,
    )


def replace_visual_moments(html: str, concept_idx: int, page: str, variant: str) -> str:
    def replace_section(match: re.Match[str]) -> str:
        opening, body, closing = match.group(1), match.group(2), match.group(3)

        def replace_figure(match_figure: re.Match[str]) -> str:
            item = choose("journal", concept_idx, page, 24 + replace_section.counter)
            replace_section.counter += 1
            figure_open = photo_figure(match_figure.group(1), variant, "photo-frame--moment", item)
            img_tag = photo_img(
                match_figure.group(2),
                item,
                role_class="doctor-portrait--moment",
                alt=f"{item.entry['alt_text']} in a Sofiati editorial visual moment",
                loading="lazy",
            )
            return figure_open + img_tag

        body = re.sub(
            r"(<figure\b[^>]*>\s*)(<img\b[^>]*>)",
            replace_figure,
            body,
            count=1,
            flags=re.S,
        )
        return opening + body + closing

    replace_section.counter = 0  # type: ignore[attr-defined]
    html = re.sub(
        r'(<section class="[^"]*\bvisual-moment\b[^"]*"[^>]*>)(.*?)(</section>)',
        replace_section,
        html,
        flags=re.S,
    )

    def replace_detail(match: re.Match[str]) -> str:
        item = choose("decorative", concept_idx, page, 28)
        return photo_img(
            match.group(0),
            item,
            role_class="doctor-portrait--detail",
            alt=f"{item.entry['alt_text']} as a decorative Sofiati brand detail",
            loading="lazy",
        )

    return re.sub(r'<img class="[^"]*\bvisual-detail\b[^"]*"[^>]*>', replace_detail, html)


def replace_remaining_generic_images(html: str, concept_idx: int, page: str, variant: str) -> str:
    category = PAGE_CATEGORY.get(page, "decorative")

    def replace(match: re.Match[str]) -> str:
        tag = match.group(0)
        if "assets/images/" not in tag and "assets/portrait/" not in tag:
            return tag
        item = choose(category, concept_idx, page, 40 + replace.counter)
        replace.counter += 1
        return photo_img(
            tag,
            item,
            role_class="doctor-portrait--support",
            alt=f"{item.entry['alt_text']} for Franciele Sofiati's {page.replace('-', ' ')} page",
            loading="lazy",
        )

    replace.counter = 0  # type: ignore[attr-defined]
    return re.sub(r'<img\b(?=[^>]*(?:assets/images/|assets/portrait/))[^>]*>', replace, html)


def update_contact_card_partial(html: str, concept_idx: int, variant: str) -> str:
    page = "contact-card"
    item = choose("contact", concept_idx, page, 2)

    def replace(match: re.Match[str]) -> str:
        return photo_img(
            match.group(0),
            item,
            role_class="doctor-portrait--contact",
            alt="Franciele Sofiati in a warm professional contact portrait",
            loading="lazy",
        )

    html = re.sub(r'<img class="[^"]*\bcontact-card-portrait\b[^"]*"[^>]*>', replace, html, count=1)
    return html


def update_mobile_menu_partial(html: str, concept_idx: int, variant: str) -> str:
    page = "mobile-menu"
    item = choose("profile", concept_idx, page, 3)
    if "mobile-menu-avatar" in html:
        def replace(match: re.Match[str]) -> str:
            return photo_img(
                match.group(0),
                item,
                role_class="doctor-portrait--menu",
                alt="Franciele Sofiati professional portrait",
                loading="lazy",
            )

        return re.sub(r'<img class="[^"]*\bmobile-menu-avatar\b[^"]*"[^>]*>', replace, html, count=1)

    avatar = photo_img(
        '<img class="mobile-menu-avatar" src="" alt="">',
        item,
        role_class="doctor-portrait--menu",
        alt="Franciele Sofiati professional portrait",
        loading="lazy",
    )
    return re.sub(r"(\n\s*<nav class=\"mobile-menu-primary)", "\n  " + avatar + r"\1", html, count=1)


def update_head_partial(html: str, concept_idx: int) -> str:
    item = choose("hero", concept_idx, "head", 1)
    return re.sub(
        r'<meta property="og:image" content="[^"]*">',
        f'<meta property="og:image" content="{absolute_path(item)}">',
        html,
        count=1,
    )


def update_page(path: Path, concept_idx: int, variant: str) -> bool:
    html = path.read_text(encoding="utf-8")
    original = html
    page = page_name(path)
    meta_item = choose(PAGE_CATEGORY.get(page, "hero"), concept_idx, page, 1)

    html = repair_stray_figure_attrs(html)
    html = body_with_variant(html, variant)
    html = update_meta_images(html, meta_item)
    html = replace_hero(html, concept_idx, page, variant)
    html = replace_hero_mosaic(html, concept_idx, page)
    html = replace_doctor_presence(html, concept_idx, page)
    html = replace_home_sections(html, concept_idx, page, variant)
    html = replace_storytelling(html, concept_idx, page, variant)
    html = replace_visual_moments(html, concept_idx, page, variant)
    html = replace_remaining_generic_images(html, concept_idx, page, variant)

    if html != original:
        path.write_text(html, encoding="utf-8")
        return True
    return False


PHOTO_CSS = f"""{PHOTO_CSS_START}
.sf-photo-rebuilt {{
  --sf-photo-ivory: color-mix(in srgb, var(--ivory, #F3EFE5) 88%, white);
  --sf-photo-sage: color-mix(in srgb, var(--sage, #A2AE9F) 74%, white);
  --sf-photo-gold: color-mix(in srgb, var(--bronze, #9A6B35) 62%, #FDE3B0);
  --sf-photo-ink: var(--ink, #252321);
  --sf-photo-line: color-mix(in srgb, var(--bronze, #9A6B35) 24%, var(--line, rgba(37,35,33,.14)));
}}
.photo-frame {{
  position: relative;
  isolation: isolate;
  overflow: hidden;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--sf-photo-sage) 18%, transparent), transparent 62%),
    var(--sf-photo-ivory);
  border: 1px solid var(--sf-photo-line);
  box-shadow: 0 24px 70px rgba(37,35,33,.13);
}}
.photo-frame::after {{
  content: "";
  position: absolute;
  inset: auto 14px 14px auto;
  width: min(96px, 26%);
  aspect-ratio: 1;
  border-radius: 999px;
  border: 1px solid color-mix(in srgb, var(--sf-photo-gold) 55%, transparent);
  background: radial-gradient(circle, color-mix(in srgb, var(--sf-photo-gold) 22%, transparent), transparent 70%);
  opacity: .72;
  pointer-events: none;
  z-index: 2;
}}
.doctor-portrait {{
  display: block;
  max-width: 100%;
  object-fit: cover;
  object-position: var(--photo-position, 50% 34%);
  filter: saturate(1.02) contrast(1.02);
}}
.hero-visual.photo-frame--hero {{
  width: min(100%, 540px);
  min-height: clamp(380px, 53vw, 690px);
  aspect-ratio: 4 / 5;
  justify-self: center;
  align-self: center;
  border-radius: 3px 3px 72px 3px;
  background:
    linear-gradient(145deg, color-mix(in srgb, var(--sf-photo-sage) 34%, transparent), transparent 56%),
    linear-gradient(0deg, rgba(37,35,33,.08), rgba(37,35,33,0) 42%),
    var(--sf-photo-ivory);
}}
.hero-visual.photo-frame--hero::before {{
  opacity: .08;
  mix-blend-mode: soft-light;
}}
.hero-visual.photo-frame--hero img,
.hero-visual.photo-frame--hero .doctor-portrait--hero {{
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  opacity: 1;
  mix-blend-mode: normal;
}}
.hero-visual.photo-frame--hero figcaption {{
  left: 18px;
  right: 18px;
  bottom: 18px;
  border: 1px solid color-mix(in srgb, var(--sf-photo-gold) 26%, transparent);
  background: color-mix(in srgb, var(--soft-white, #F8F7F2) 88%, white);
  box-shadow: 0 16px 44px rgba(37,35,33,.12);
}}
.hero-mosaic img.doctor-portrait--mosaic,
.visual-moment img.doctor-portrait--moment,
.home-index-section img.doctor-portrait--section,
.storytelling-gate-visual img.doctor-portrait--story {{
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: var(--photo-position, 50% 34%);
  opacity: 1;
  mix-blend-mode: normal;
}}
.hero-mosaic img.doctor-portrait--mosaic {{
  border: 1px solid color-mix(in srgb, var(--sf-photo-gold) 20%, transparent);
  border-radius: 3px;
  box-shadow: 0 14px 38px rgba(37,35,33,.1);
}}
.home-index-section figure.photo-frame--section,
.storytelling-gate-visual.photo-frame--story,
.visual-moment figure.photo-frame--moment {{
  min-height: clamp(260px, 34vw, 520px);
  aspect-ratio: 5 / 4;
  border-radius: 3px 48px 3px 3px;
}}
.home-index-section:nth-of-type(even) figure.photo-frame--section,
.storytelling-gate:nth-of-type(even) .photo-frame--story {{
  border-radius: 52px 3px 3px 3px;
}}
.doctor-presence {{
  background:
    linear-gradient(145deg, color-mix(in srgb, var(--sf-photo-ivory) 92%, white), color-mix(in srgb, var(--sf-photo-sage) 18%, white));
}}
@media(min-width: 981px) {{
  .sf-photo-rebuilt .hero {{
    padding-bottom: clamp(72px, 7vw, 112px);
  }}
  .sf-photo-rebuilt .doctor-presence {{
    bottom: clamp(-84px, -4.8vw, -50px);
    width: min(168px, 17vw);
    border-radius: 28px;
  }}
}}
.doctor-presence .doctor-portrait--presence,
.contact-card-portrait.doctor-portrait--contact,
.mobile-menu-avatar.doctor-portrait--menu {{
  object-position: var(--photo-position, 50% 31%);
  border: 1px solid color-mix(in srgb, var(--sf-photo-gold) 28%, transparent);
}}
.contact-card-portrait.doctor-portrait--contact {{
  width: min(146px, 38vw);
  box-shadow: 0 18px 44px rgba(37,35,33,.13);
}}
.mobile-menu-avatar.doctor-portrait--menu {{
  background: var(--sf-photo-ivory);
}}
.visual-detail.doctor-portrait--detail {{
  border: 1px solid color-mix(in srgb, var(--sf-photo-gold) 20%, transparent);
  box-shadow: 0 16px 42px rgba(37,35,33,.1);
}}
body[data-photo-variant="sage-editorial"] .hero-visual.photo-frame--hero,
body[data-photo-variant="sage-editorial"] .home-index-section figure.photo-frame--section {{
  border-radius: 72px 3px 72px 3px;
}}
body[data-photo-variant="ivory-oval"] .hero-visual.photo-frame--hero {{
  border-radius: 999px 999px 6px 6px;
  width: min(100%, 500px);
}}
body[data-photo-variant="gold-clinical"] .hero-visual.photo-frame--hero {{
  border-radius: 3px;
  box-shadow: inset 0 0 0 10px color-mix(in srgb, var(--soft-white, #F8F7F2) 76%, transparent), 0 26px 78px rgba(37,35,33,.12);
}}
body[data-photo-variant="window-light"] .hero-visual.photo-frame--hero {{
  border-radius: 3px 110px 3px 3px;
  background: linear-gradient(135deg, rgba(255,255,255,.52), color-mix(in srgb, var(--sf-photo-sage) 18%, white));
}}
body[data-photo-variant="studio-luxe"] .hero-visual.photo-frame--hero {{
  background: linear-gradient(135deg, color-mix(in srgb, var(--deep-sage, #798A80) 72%, #252321), color-mix(in srgb, var(--sf-photo-gold) 18%, #252321));
  border-color: color-mix(in srgb, var(--sf-photo-gold) 36%, transparent);
}}
body.page-legal .hero-visual.photo-frame--hero,
body.page-privacy .hero-visual.photo-frame--hero,
body.page-cookies .hero-visual.photo-frame--hero,
body.page-accessibility .hero-visual.photo-frame--hero,
body.page-sitemap .hero-visual.photo-frame--hero {{
  width: min(100%, 420px);
  min-height: clamp(280px, 36vw, 480px);
  opacity: .92;
}}
@media(max-width: 980px) {{
  .hero-visual.photo-frame--hero {{
    width: min(100%, 480px);
    min-height: clamp(340px, 92vw, 560px);
  }}
  .home-index-section figure.photo-frame--section,
  .storytelling-gate-visual.photo-frame--story,
  .visual-moment figure.photo-frame--moment {{
    min-height: clamp(260px, 72vw, 440px);
  }}
}}
@media(max-width: 620px) {{
  .sf-photo-rebuilt .hero {{
    display: grid;
    grid-template-columns: minmax(0, 1fr) !important;
    justify-items: stretch;
    overflow: visible;
  }}
  .sf-photo-rebuilt .hero-copy,
  .sf-photo-rebuilt .hero-visual,
  .sf-photo-rebuilt .doctor-presence {{
    grid-column: 1 / -1 !important;
    max-width: 100%;
  }}
  .sf-photo-rebuilt .hero-copy {{
    order: 1;
    width: 100%;
  }}
  .hero-visual.photo-frame--hero {{
    order: -1;
    width: min(100%, 390px);
    min-height: min(520px, 116vw);
    border-radius: 3px 3px 42px 3px;
  }}
  body[data-photo-variant="ivory-oval"] .hero-visual.photo-frame--hero {{
    border-radius: 180px 180px 4px 4px;
  }}
  .hero-visual.photo-frame--hero figcaption {{
    font-size: .72rem;
    left: 12px;
    right: 12px;
    bottom: 12px;
  }}
  .hero-mosaic {{
    display: none;
  }}
  .contact-card-portrait.doctor-portrait--contact {{
    width: min(132px, 44vw);
  }}
}}
{PHOTO_CSS_END}
"""


def update_css(path: Path) -> bool:
    css = path.read_text(encoding="utf-8")
    original = css
    pattern = re.compile(
        re.escape(PHOTO_CSS_START) + r".*?" + re.escape(PHOTO_CSS_END) + r"\n?",
        flags=re.S,
    )
    css = pattern.sub("", css).rstrip() + "\n\n" + PHOTO_CSS + "\n"
    if css != original:
        path.write_text(css, encoding="utf-8")
        return True
    return False


def main() -> None:
    changed_pages = 0
    changed_partials = 0
    changed_css = 0
    concepts = sorted(path for path in CONCEPTS_DIR.iterdir() if path.is_dir())
    for concept_dir in concepts:
        idx = concept_number(concept_dir)
        variant = VARIANTS[(idx - 1) % len(VARIANTS)]

        for page_path in sorted(concept_dir.glob("*.html")):
            if update_page(page_path, idx, variant):
                changed_pages += 1

        contact_partial = concept_dir / "partials" / "contact-card.html"
        if contact_partial.exists():
            html = contact_partial.read_text(encoding="utf-8")
            updated = update_contact_card_partial(html, idx, variant)
            if updated != html:
                contact_partial.write_text(updated, encoding="utf-8")
                changed_partials += 1

        mobile_partial = concept_dir / "partials" / "mobile-menu.html"
        if mobile_partial.exists():
            html = mobile_partial.read_text(encoding="utf-8")
            updated = update_mobile_menu_partial(html, idx, variant)
            if updated != html:
                mobile_partial.write_text(updated, encoding="utf-8")
                changed_partials += 1

        head_partial = concept_dir / "partials" / "head.html"
        if head_partial.exists():
            html = head_partial.read_text(encoding="utf-8")
            updated = update_head_partial(html, idx)
            if updated != html:
                head_partial.write_text(updated, encoding="utf-8")
                changed_partials += 1

        css_path = concept_dir / "css" / "style.css"
        if css_path.exists() and update_css(css_path):
            changed_css += 1

    print(
        json.dumps(
            {
                "concepts": len(concepts),
                "pages_changed": changed_pages,
                "partials_changed": changed_partials,
                "css_changed": changed_css,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
