#!/usr/bin/env python3
"""Normalize production SEO across every crawlable HTML route.

Run this after either English rendering or Portuguese generation.  The script
keeps visible page copy and body structure intact while standardising metadata,
truthful schema entities and the requested post-hero navigation.  Repository
facts come from ``data/seo.json``; no address, hours, price or rating is added.
"""

from __future__ import annotations

import json
import mimetypes
import re
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup, Comment, Tag
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SEO_DATA = json.loads((ROOT / "data" / "seo.json").read_text(encoding="utf-8"))
ORIGIN = str(SEO_DATA["domain"]).rstrip("/")
SITE_NAME = str(SEO_DATA["siteName"])
EMAIL = str(SEO_DATA["email"])
TELEPHONE = str(SEO_DATA["telephone"])
REGISTRATION = str(SEO_DATA["professionalRegistration"])
INSTAGRAM = str(SEO_DATA["sameAs"][0])
LOGO_URL = f"{ORIGIN}/assets/brand/sofiati-logo-primary.png"
DEFAULT_SOCIAL_URL = f"{ORIGIN}/{SEO_DATA['defaultOgImage']}"
INDEX_ROBOTS = "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1"
NOINDEX_ROBOTS = "noindex, follow"

HEAD_RE = re.compile(r"<head\b[^>]*>.*?</head>", re.I | re.S)
EXISTING_JUMP_RE = re.compile(
    r"\s*<!-- Main-content target:.*?-->\s*"
    r"<span\b[^>]*\bid=[\"']main-content[\"'][^>]*></span>\s*"
    r"|\s*<a\b[^>]*\bclass=[\"'][^\"']*\bskip-past-hero\b[^\"']*[\"'][^>]*>.*?</a>\s*",
    re.I | re.S,
)


# These titles are intentionally shorter than the visible editorial headlines.
EN_TITLE_OVERRIDES = {
    "laser.html": "Laser Treatments in Londrina | Franciele Sofiati",
    "skin.html": "Skin Care in Londrina | Franciele Sofiati",
    "care.html": "Aesthetic Preparation and Aftercare | Franciele Sofiati",
    "journal/why-aesthetic-care-begins-with-consultation.html": "Aesthetic Consultation Before Treatment | Franciele Sofiati",
    "journal/professional-skin-cleansing-guide.html": "Professional Skin Cleansing Guide | Franciele Sofiati",
    "journal/rebuilding-an-overwhelmed-skin-barrier.html": "Repairing an Overwhelmed Skin Barrier | Franciele Sofiati",
    "journal/understanding-facial-pigmentation.html": "Facial Pigmentation: Assessment and Care | Franciele Sofiati",
    "journal/persistent-facial-redness-and-vessels.html": "Persistent Facial Redness and Visible Vessels | Franciele Sofiati",
    "journal/understanding-acne-scar-treatment.html": "Acne Scar Treatment Planning | Franciele Sofiati",
    "journal/fractional-co2-laser-recovery-and-aftercare.html": "Fractional CO₂ Laser Recovery and Aftercare | Franciele Sofiati",
    "journal/laser-hair-removal-process-and-maintenance.html": "Laser Hair Removal: Sessions and Maintenance | Franciele Sofiati",
    "journal/ultrasound-radiofrequency-collagen-treatment.html": "Ultrasound and Radiofrequency for Collagen | Franciele Sofiati",
    "journal/hair-thinning-causes-and-scalp-care.html": "Hair Thinning and Scalp Care | Franciele Sofiati",
}


# Portuguese metadata is maintained here because automated translation is not
# reliable enough for search-result copy.  The visible page content is not
# changed by these entries.
PT_META: dict[str, tuple[str, str]] = {
    "pt/404.html": (
        "Página Não Encontrada | Franciele Sofiati",
        "A página procurada não foi encontrada. Volte ao início ou consulte informações sobre pele, laser, tratamentos e contato.",
    ),
    "pt/index.html": (
        "Cuidados com Pele e Laser em Londrina | Franciele Sofiati",
        "Cuidados estéticos com Franciele Sofiati em Londrina: avaliação individual, pele, laser, couro cabeludo, orientações e acompanhamento.",
    ),
    "pt/about.html": (
        "Franciele Sofiati Biomédica em Londrina | Sobre",
        "Conheça Franciele Sofiati, biomédica em Londrina, e sua forma atenta de avaliar pele, laser e cuidados estéticos com clareza e respeito.",
    ),
    "pt/accessibility.html": (
        "Acessibilidade | Franciele Sofiati Biomédica",
        "Entenda os recursos e limites de acessibilidade do site de Franciele Sofiati, incluindo leitura, teclado, contraste e formas de contato.",
    ),
    "pt/blog.html": (
        "Conteúdos sobre Pele, Laser e Estética | Franciele Sofiati",
        "Leia conteúdos de Franciele Sofiati sobre pele, acne, pigmentação, laser, cuidados pós-tratamento e planejamento estético em Londrina.",
    ),
    "pt/care.html": (
        "Preparação e Cuidados Pós-Tratamento | Franciele Sofiati",
        "Orientações práticas sobre preparação, recuperação e cuidados após procedimentos estéticos, sempre adaptadas ao tratamento e à pessoa.",
    ),
    "pt/consultation.html": (
        "Consulta Estética em Londrina | Franciele Sofiati",
        "Converse com Franciele Sofiati sobre pele, laser, face, corpo ou couro cabeludo e entenda quais cuidados podem ser adequados para você.",
    ),
    "pt/contact.html": (
        "Contato em Londrina | Franciele Sofiati Biomédica",
        "Entre em contato com Franciele Sofiati em Londrina por formulário, WhatsApp, Instagram ou e-mail para tirar dúvidas ou solicitar consulta.",
    ),
    "pt/cookies.html": (
        "Política de Cookies | Franciele Sofiati Biomédica",
        "Saiba quais cookies este site pode utilizar, para que servem e como rever suas preferências de privacidade e recursos opcionais.",
    ),
    "pt/faq.html": (
        "Dúvidas sobre Tratamentos Estéticos | Franciele Sofiati",
        "Respostas claras sobre consulta estética, indicação, pele, laser, preparação, recuperação, resultados e cuidados com Franciele Sofiati.",
    ),
    "pt/journal.html": (
        "Conteúdos sobre Pele e Estética | Franciele Sofiati",
        "Artigos sobre saúde da pele, estética, laser, prevenção, recuperação e couro cabeludo escritos com clareza por Franciele Sofiati.",
    ),
    "pt/laser.html": (
        "Tratamentos a Laser em Londrina | Franciele Sofiati",
        "Entenda as finalidades do laser, critérios de indicação, preparação, contraindicações e recuperação com Franciele Sofiati em Londrina.",
    ),
    "pt/legal.html": (
        "Termos de Serviço e Cancelamento | Franciele Sofiati",
        "Consulte as condições de reserva, pagamento, cancelamento, consentimento, acompanhamento e prestação dos serviços de Franciele Sofiati.",
    ),
    "pt/mission.html": (
        "A Forma de Cuidar de Franciele Sofiati | Missão",
        "Conheça o compromisso de Franciele Sofiati com escuta, avaliação responsável, explicações honestas, respeito e acompanhamento cuidadoso.",
    ),
    "pt/privacy.html": (
        "Aviso de Privacidade | Franciele Sofiati Biomédica",
        "Saiba quais dados podem ser recebidos pelo site, por que são utilizados, como são protegidos e como exercer seus direitos de privacidade.",
    ),
    "pt/results.html": (
        "Resultados Estéticos com Contexto | Franciele Sofiati",
        "Entenda por que resultados estéticos variam, como fotografias devem ser interpretadas e de que forma a evolução pode ser acompanhada.",
    ),
    "pt/skin.html": (
        "Cuidados com a Pele em Londrina | Franciele Sofiati",
        "Informações sobre barreira da pele, acne, pigmentação, sensibilidade, textura, poros e planejamento profissional com Franciele Sofiati.",
    ),
    "pt/testimonials.html": (
        "Relatos de Pacientes | Franciele Sofiati em Londrina",
        "Leia relatos publicados sobre escuta, explicações, tratamento e acompanhamento recebidos com Franciele Sofiati em Londrina.",
    ),
    "pt/thank-you.html": (
        "Mensagem Recebida | Franciele Sofiati",
        "Sua mensagem foi recebida. Veja o que acontece a seguir e consulte informações úteis enquanto aguarda o retorno de Franciele Sofiati.",
    ),
    "pt/treatments.html": (
        "Tratamentos Estéticos em Londrina | Franciele Sofiati",
        "Consulte tratamentos estéticos confirmados para pele, face, corpo, laser e couro cabeludo, com indicação definida após avaliação individual.",
    ),
    "pt/values.html": (
        "Valores que Orientam o Cuidado | Franciele Sofiati",
        "Escuta, clareza, segurança, honestidade, respeito e responsabilidade orientam as recomendações e o cuidado oferecido por Franciele Sofiati.",
    ),
}


PAGE_TYPES: dict[str, str | list[str]] = {
    "about.html": ["AboutPage", "ProfilePage"],
    "blog.html": ["CollectionPage", "Blog"],
    "contact.html": "ContactPage",
    "faq.html": "FAQPage",
    "journal.html": ["CollectionPage", "Blog"],
    "laser.html": ["WebPage", "MedicalWebPage"],
    "mission.html": "AboutPage",
    "skin.html": ["WebPage", "MedicalWebPage"],
    "treatments.html": "CollectionPage",
    "values.html": "AboutPage",
}


def page_paths() -> list[Path]:
    pages = list(ROOT.glob("*.html"))
    pages.extend((ROOT / "pt").glob("*.html"))
    pages.extend((ROOT / "journal").glob("*.html"))
    return sorted(pages, key=lambda path: path.relative_to(ROOT).as_posix())


def canonical_for(relative: str) -> str:
    if relative == "index.html":
        return f"{ORIGIN}/"
    if relative == "pt/index.html":
        return f"{ORIGIN}/pt/"
    return f"{ORIGIN}/{relative}"


def language_for(relative: str) -> str:
    return "pt-BR" if relative.startswith("pt/") else "en"


def local_route(relative: str, language: str) -> str:
    if language == "pt-BR":
        return relative.removeprefix("pt/")
    return relative


def meta_key(relative: str) -> str:
    return local_route(relative, language_for(relative))


def type_values(node: dict[str, Any]) -> set[str]:
    value = node.get("@type")
    if isinstance(value, list):
        return {str(item) for item in value}
    return {str(value)} if value else set()


def set_meta(soup: BeautifulSoup, attribute: str, key: str, content: str) -> Tag:
    head = soup.head
    if head is None:
        raise RuntimeError("Document has no head")
    matches = head.find_all("meta", attrs={attribute: key})
    tag = matches[0] if matches else soup.new_tag("meta")
    if not matches:
        head.append(tag)
    tag.attrs = {attribute: key, "content": content}
    for duplicate in matches[1:]:
        duplicate.decompose()
    return tag


def insert_comment_before(tag: Tag, marker: str, text: str) -> None:
    sibling = tag.previous_sibling
    while sibling is not None and isinstance(sibling, str) and not sibling.strip():
        sibling = sibling.previous_sibling
    if isinstance(sibling, Comment) and marker in str(sibling):
        return
    tag.insert_before(Comment(text))


def image_details(url: str) -> tuple[int, int, str]:
    if not url.startswith(f"{ORIGIN}/"):
        raise RuntimeError(f"Social image is outside the production origin: {url}")
    relative = url.removeprefix(f"{ORIGIN}/")
    path = ROOT / relative
    if not path.is_file():
        raise RuntimeError(f"Social image does not exist: {relative}")
    with Image.open(path) as image:
        width, height = image.size
        image_format = image.format or ""
    mime = Image.MIME.get(image_format) or mimetypes.guess_type(path.name)[0]
    if not mime:
        raise RuntimeError(f"Cannot determine social image MIME type: {relative}")
    return width, height, mime


def normalize_icon_sizes(relative: str, head: Tag) -> None:
    """Keep HTML icon declarations aligned with the dimensions on disk."""
    for link in head.find_all("link", href=True):
        rel_values = {str(value).lower() for value in link.get("rel", [])}
        if not ({"icon", "apple-touch-icon"} & rel_values):
            continue
        href = str(link["href"]).strip()
        parsed = urlsplit(href)
        if parsed.scheme or parsed.netloc or not parsed.path:
            continue
        if parsed.path.startswith("/"):
            path = ROOT / unquote(parsed.path.lstrip("/"))
        else:
            path = ROOT / Path(relative).parent / unquote(parsed.path)
        if not path.is_file():
            continue
        try:
            with Image.open(path) as image:
                width, height = image.size
        except (OSError, ValueError):
            continue
        link["sizes"] = f"{width}x{height}"


def metadata_for(relative: str, soup: BeautifulSoup) -> tuple[str, str]:
    current_title = soup.title.get_text(" ", strip=True) if soup.title else ""
    description = soup.find("meta", attrs={"name": "description"})
    current_description = str(description.get("content", "")).strip() if description else ""
    if relative in PT_META:
        return PT_META[relative]
    return EN_TITLE_OVERRIDES.get(relative, current_title), current_description


def social_alt(relative: str, soup: BeautifulSoup, social_url: str) -> str:
    language = language_for(relative)
    if social_url == DEFAULT_SOCIAL_URL:
        if language == "pt-BR":
            return "Franciele Sofiati, biomédica, esteticista e cosmetologista em Londrina"
        return "Franciele Sofiati, biomedical practitioner, aesthetician and cosmetologist in Londrina"
    primary = soup.select_one("main img[fetchpriority='high'], main img[loading='eager']:not([alt=''])")
    if primary and primary.get("alt"):
        return str(primary["alt"]).strip().rstrip(".")
    return "Imagem editorial de Franciele Sofiati" if language == "pt-BR" else "Franciele Sofiati editorial image"


def reciprocal_urls(relative: str) -> tuple[str, str] | None:
    if relative.startswith("journal/"):
        return None
    if relative.startswith("pt/"):
        english = relative.removeprefix("pt/")
        return canonical_for(english), canonical_for(relative)
    portuguese = f"pt/{relative}"
    if (ROOT / portuguese).is_file():
        return canonical_for(relative), canonical_for(portuguese)
    return None


def normalize_head(relative: str, source: str) -> tuple[str, dict[str, Any]]:
    match = HEAD_RE.search(source)
    if not match:
        raise RuntimeError(f"{relative}: expected one head")
    soup = BeautifulSoup(match.group(0), "html.parser")
    head = soup.head
    if head is None:
        raise RuntimeError(f"{relative}: invalid head")

    title, description = metadata_for(relative, soup)
    if not title or not description:
        raise RuntimeError(f"{relative}: title and description are required")
    if soup.title:
        soup.title.string = title
    else:
        title_tag = soup.new_tag("title")
        title_tag.string = title
        head.append(title_tag)

    canonical = canonical_for(relative)
    language = language_for(relative)
    noindex = meta_key(relative) in {"404.html", "thank-you.html"}
    set_meta(soup, "name", "description", description)
    robots_tag = set_meta(
        soup,
        "name",
        "robots",
        NOINDEX_ROBOTS if noindex else INDEX_ROBOTS,
    )
    if noindex:
        insert_comment_before(
            robots_tag,
            "Indexing decision",
            " Indexing decision: confirmation and error routes intentionally use noindex, follow. ",
        )
    set_meta(soup, "name", "author", "Franciele Sofiati")
    set_meta(soup, "name", "application-name", SITE_NAME)
    set_meta(soup, "name", "theme-color", "#213128")
    set_meta(soup, "name", "color-scheme", "light")
    set_meta(soup, "name", "referrer", "strict-origin-when-cross-origin")
    set_meta(soup, "name", "format-detection", "telephone=yes, email=yes, address=no")

    canonicals = head.find_all("link", rel=lambda value: value and "canonical" in value)
    canonical_tag = canonicals[0] if canonicals else soup.new_tag("link")
    if not canonicals:
        head.append(canonical_tag)
    canonical_tag.attrs = {"rel": "canonical", "href": canonical}
    for duplicate in canonicals[1:]:
        duplicate.decompose()
    insert_comment_before(
        canonical_tag,
        "Canonical and language",
        " Canonical and language URLs: update together whenever a production route changes. ",
    )

    pair = reciprocal_urls(relative)
    expected_alternates: dict[str, str]
    if pair:
        english_url, portuguese_url = pair
        expected_alternates = {
            "en": english_url,
            "pt-BR": portuguese_url,
            "x-default": english_url,
        }
    else:
        expected_alternates = {"en": canonical, "x-default": canonical}
    existing_alternates = {
        str(tag.get("hreflang")): tag
        for tag in head.find_all("link", rel=lambda value: value and "alternate" in value)
        if tag.get("hreflang")
    }
    for code, url in expected_alternates.items():
        tag = existing_alternates.pop(code, None) or soup.new_tag("link")
        tag.attrs = {"rel": "alternate", "hreflang": code, "href": url}
        if tag.parent is None:
            canonical_tag.insert_after(tag)
    for obsolete in existing_alternates.values():
        obsolete.decompose()

    old_social = head.find("meta", attrs={"property": "og:image"})
    social_url = str(old_social.get("content", "")).strip() if old_social else DEFAULT_SOCIAL_URL
    width, height, mime = image_details(social_url)
    alt = social_alt(relative, BeautifulSoup(source, "html.parser"), social_url)
    article = relative.startswith("journal/")
    social_values = {
        "og:type": "article" if article else "website",
        "og:site_name": SITE_NAME,
        "og:locale": "pt_BR" if language == "pt-BR" else "en_US",
        "og:url": canonical,
        "og:title": title,
        "og:description": description,
        "og:image": social_url,
        "og:image:secure_url": social_url,
        "og:image:type": mime,
        "og:image:width": str(width),
        "og:image:height": str(height),
        "og:image:alt": alt,
    }
    first_social: Tag | None = None
    for key, value in social_values.items():
        tag = set_meta(soup, "property", key, value)
        first_social = first_social or tag
    if pair:
        set_meta(
            soup,
            "property",
            "og:locale:alternate",
            "en_US" if language == "pt-BR" else "pt_BR",
        )
    else:
        for tag in head.find_all("meta", attrs={"property": "og:locale:alternate"}):
            tag.decompose()
    if first_social:
        insert_comment_before(
            first_social,
            "Social sharing",
            " Social sharing metadata uses verified local assets and their real dimensions. ",
        )

    twitter_values = {
        "twitter:card": "summary_large_image",
        "twitter:title": title,
        "twitter:description": description,
        "twitter:image": social_url,
        "twitter:image:alt": alt,
    }
    for key, value in twitter_values.items():
        set_meta(soup, "name", key, value)

    # Search Console verification is intentionally a placeholder. DNS Domain
    # verification is preferred and requires no production meta token.
    for tag in head.find_all("meta", attrs={"name": "google-site-verification"}):
        tag.decompose()
    for comment in head.find_all(
        string=lambda value: isinstance(value, Comment)
        and "GOOGLE SEARCH CONSOLE" in str(value)
    ):
        comment.extract()
    if relative == "index.html":
        verification = soup.new_tag("meta")
        verification.attrs = {
            "name": "google-site-verification",
            "content": "GOOGLE_SITE_VERIFICATION_REPLACE_ME",
        }
        head.append(
            Comment(
                " GOOGLE SEARCH CONSOLE: Replace the placeholder below only "
                "for HTML-tag verification. DNS Domain verification is preferred. "
            )
        )
        head.append(verification)

    normalize_icon_sizes(relative, head)

    return source[: match.start()] + str(head) + source[match.end() :], {
        "title": title,
        "description": description,
        "canonical": canonical,
        "language": language,
        "social_url": social_url,
        "social_alt": alt,
        "social_width": width,
        "social_height": height,
        "social_mime": mime,
        "noindex": noindex,
    }


def replace_identifier(value: Any) -> Any:
    if isinstance(value, str):
        return value.replace(f"{ORIGIN}/#organization", f"{ORIGIN}/#practice")
    if isinstance(value, list):
        return [replace_identifier(item) for item in value]
    if isinstance(value, dict):
        return {key: replace_identifier(item) for key, item in value.items()}
    return value


def common_entities(language: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    portuguese = language == "pt-BR"
    website = {
        "@type": "WebSite",
        "@id": f"{ORIGIN}/#website",
        "url": f"{ORIGIN}/",
        "name": SITE_NAME,
        "inLanguage": ["en", "pt-BR"],
        "publisher": {"@id": f"{ORIGIN}/#practice"},
    }
    person = {
        "@type": "Person",
        "@id": f"{ORIGIN}/#franciele",
        "name": "Franciele Sofiati",
        "url": f"{ORIGIN}/about.html",
        "jobTitle": (
            "Biomédica, esteticista e cosmetologista"
            if portuguese
            else "Biomedical Practitioner, Aesthetician and Cosmetologist"
        ),
        "identifier": {
            "@type": "PropertyValue",
            "propertyID": "CRBM",
            "value": REGISTRATION.removeprefix("CRBM ").strip(),
        },
        "hasCredential": {
            "@type": "EducationalOccupationalCredential",
            "credentialCategory": "Professional registration",
            "name": REGISTRATION,
        },
        "email": EMAIL,
        "telephone": TELEPHONE,
        "image": {"@id": f"{DEFAULT_SOCIAL_URL}#primaryimage"},
        "worksFor": {"@id": f"{ORIGIN}/#practice"},
        "sameAs": [INSTAGRAM],
    }
    business = {
        "@type": "HealthAndBeautyBusiness",
        "@id": f"{ORIGIN}/#practice",
        "name": SITE_NAME,
        "url": f"{ORIGIN}/",
        "email": EMAIL,
        "telephone": TELEPHONE,
        "image": {"@id": f"{DEFAULT_SOCIAL_URL}#primaryimage"},
        "logo": LOGO_URL,
        "areaServed": {
            "@type": "City",
            "name": "Londrina",
            "containedInPlace": {
                "@type": "State",
                "name": "Paraná",
                "containedInPlace": {
                    "@type": "Country",
                    "name": "Brasil" if portuguese else "Brazil",
                },
            },
        },
        "founder": {"@id": f"{ORIGIN}/#franciele"},
        "sameAs": [INSTAGRAM],
    }
    return website, person, business


def page_type(relative: str) -> str | list[str]:
    return PAGE_TYPES.get(meta_key(relative), "WebPage")


def image_entity(meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "@type": "ImageObject",
        "@id": f"{meta['social_url']}#primaryimage",
        "url": meta["social_url"],
        "contentUrl": meta["social_url"],
        "encodingFormat": meta["social_mime"],
        "width": meta["social_width"],
        "height": meta["social_height"],
        "caption": meta["social_alt"],
        "representativeOfPage": True,
    }


def breadcrumb_entity(relative: str, meta: dict[str, Any], soup: BeautifulSoup) -> dict[str, Any]:
    language = meta["language"]
    home_url = f"{ORIGIN}/pt/" if language == "pt-BR" else f"{ORIGIN}/"
    items = [
        {
            "@type": "ListItem",
            "position": 1,
            "name": "Início" if language == "pt-BR" else "Home",
            "item": home_url,
        }
    ]
    if meta_key(relative) != "index.html":
        heading = soup.find("h1")
        name = heading.get_text(" ", strip=True) if heading else meta["title"].split("|")[0].strip()
        items.append(
            {
                "@type": "ListItem",
                "position": 2,
                "name": name,
                "item": meta["canonical"],
            }
        )
    return {
        "@type": "BreadcrumbList",
        "@id": f"{meta['canonical']}#breadcrumb",
        "itemListElement": items,
    }


def service_entity(relative: str, meta: dict[str, Any]) -> dict[str, Any] | None:
    key = meta_key(relative)
    names = {
        "consultation.html": ("Consulta estética personalizada", "Personalised aesthetic consultation"),
        "laser.html": ("Cuidados estéticos com laser", "Laser aesthetic care"),
        "skin.html": ("Avaliação e cuidados com a pele", "Skin assessment and aesthetic care"),
    }
    if key not in names:
        return None
    name = names[key][0 if meta["language"] == "pt-BR" else 1]
    return {
        "@type": "Service",
        "@id": f"{meta['canonical']}#service",
        "name": name,
        "serviceType": name,
        "description": meta["description"],
        "url": meta["canonical"],
        "provider": {"@id": f"{ORIGIN}/#practice"},
        "areaServed": {"@type": "City", "name": "Londrina"},
    }


def treatment_item_list(relative: str, meta: dict[str, Any], soup: BeautifulSoup) -> dict[str, Any] | None:
    if meta_key(relative) != "treatments.html":
        return None
    entries: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for card in soup.select("[data-treatment-entry]"):
        heading = card.find(["h2", "h3", "h4"])
        section = card.find_parent("section", id=True)
        if not heading or not section:
            continue
        name = heading.get_text(" ", strip=True)
        url = f"{meta['canonical']}#{section['id']}"
        if (name, url) in seen:
            continue
        seen.add((name, url))
        entries.append(
            {
                "@type": "ListItem",
                "position": len(entries) + 1,
                "item": {
                    "@type": "Service",
                    "name": name,
                    "url": url,
                    "provider": {"@id": f"{ORIGIN}/#practice"},
                    "areaServed": {"@type": "City", "name": "Londrina"},
                },
            }
        )
    return {
        "@type": "ItemList",
        "@id": f"{meta['canonical']}#treatment-list",
        "name": "Tratamentos confirmados" if meta["language"] == "pt-BR" else "Confirmed aesthetic treatments",
        "numberOfItems": len(entries),
        "itemListElement": entries,
    }


def visible_faq_entities(soup: BeautifulSoup) -> list[dict[str, Any]]:
    """Build FAQ schema only from questions and answers a visitor can read."""
    entities: list[dict[str, Any]] = []
    for details in soup.select("details.sf-accordion-item"):
        summary = details.find("summary")
        if not summary:
            continue
        question = " ".join(summary.stripped_strings).removesuffix("+").strip()
        answer = " ".join(
            paragraph.get_text(" ", strip=True)
            for paragraph in details.find_all("p")
            if paragraph.get_text(" ", strip=True)
        )
        if question and answer:
            entities.append(
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
            )
    return entities


def remove_unconfirmed_claims(value: Any) -> None:
    if isinstance(value, list):
        for item in value:
            remove_unconfirmed_claims(item)
        return
    if not isinstance(value, dict):
        return
    for key in (
        "address",
        "openingHours",
        "openingHoursSpecification",
        "priceRange",
        "aggregateRating",
        "review",
        "reviews",
        "award",
        "awards",
        "dateModified",
        "datePublished",
    ):
        value.pop(key, None)
    for item in value.values():
        remove_unconfirmed_claims(item)


def normalize_schema(relative: str, source: str, meta: dict[str, Any]) -> str:
    soup = BeautifulSoup(source, "html.parser")
    scripts = soup.select("script[type='application/ld+json']")
    if len(scripts) != 1:
        raise RuntimeError(f"{relative}: expected exactly one JSON-LD block")
    payload = replace_identifier(json.loads(scripts[0].string or scripts[0].get_text()))
    graph = payload.get("@graph", []) if isinstance(payload, dict) else []
    if not isinstance(graph, list):
        raise RuntimeError(f"{relative}: JSON-LD @graph must be an array")

    website, person, business = common_entities(meta["language"])
    common_by_id = {
        website["@id"]: website,
        person["@id"]: person,
        business["@id"]: business,
    }
    retained: list[dict[str, Any]] = []
    for raw in graph:
        if not isinstance(raw, dict):
            continue
        identifier = raw.get("@id")
        if identifier in common_by_id:
            if not any(node.get("@id") == identifier for node in retained):
                retained.append(common_by_id[identifier])
            continue
        retained.append(raw)
    for identifier, node in common_by_id.items():
        if not any(item.get("@id") == identifier for item in retained):
            retained.insert(len(retained), node)
    graph = retained

    social_id = f"{meta['social_url']}#primaryimage"
    graph = [
        node
        for node in graph
        if not (
            "ImageObject" in type_values(node)
            and (
                node.get("@id") in {social_id, f"{DEFAULT_SOCIAL_URL}#primaryimage"}
                or node.get("url") == meta["social_url"]
                or node.get("contentUrl") == meta["social_url"]
            )
        )
    ]
    graph.append(image_entity(meta))

    breadcrumb = breadcrumb_entity(relative, meta, soup)
    graph = [node for node in graph if "BreadcrumbList" not in type_values(node)]
    graph.append(breadcrumb)

    canonical = meta["canonical"]
    page_candidates = [
        node
        for node in graph
        if node.get("url") == canonical
        and type_values(node).intersection(
            {
                "WebPage",
                "AboutPage",
                "ProfilePage",
                "ContactPage",
                "CollectionPage",
                "Blog",
                "FAQPage",
                "MedicalWebPage",
            }
        )
    ]
    page = page_candidates[0] if page_candidates else {}
    if not page_candidates:
        graph.append(page)
    expected_type = page_type(relative)
    page.update(
        {
            "@type": expected_type,
            "@id": f"{canonical}#webpage",
            "url": canonical,
            "name": meta["title"],
            "description": meta["description"],
            "inLanguage": meta["language"],
            "isPartOf": {"@id": f"{ORIGIN}/#website"},
            "breadcrumb": {"@id": breadcrumb["@id"]},
            "primaryImageOfPage": {"@id": social_id},
        }
    )
    page.pop("dateModified", None)
    page.pop("datePublished", None)

    key = meta_key(relative)
    if key == "about.html":
        page["mainEntity"] = {"@id": f"{ORIGIN}/#franciele"}
        page["about"] = {"@id": f"{ORIGIN}/#franciele"}
    elif key == "contact.html":
        page["mainEntity"] = {"@id": f"{ORIGIN}/#practice"}
        page["about"] = {"@id": f"{ORIGIN}/#franciele"}
    elif key in {"consultation.html", "laser.html", "skin.html"}:
        page["about"] = {"@id": f"{canonical}#service"}
    else:
        page["about"] = {"@id": f"{ORIGIN}/#franciele"}
    if key == "faq.html":
        page["mainEntity"] = visible_faq_entities(soup)

    service = service_entity(relative, meta)
    if service:
        graph = [
            node
            for node in graph
            if not ("Service" in type_values(node) and node.get("@id") == service["@id"])
        ]
        graph.append(service)

    treatments = treatment_item_list(relative, meta, soup)
    if treatments:
        graph = [
            node
            for node in graph
            if not ("ItemList" in type_values(node) and node.get("@id") == treatments["@id"])
        ]
        graph.append(treatments)
        page["mainEntity"] = {"@id": treatments["@id"]}

    for node in graph:
        if "BlogPosting" in type_values(node):
            node["mainEntityOfPage"] = {"@id": f"{canonical}#webpage"}
            node["publisher"] = {"@id": f"{ORIGIN}/#practice"}
            node["author"] = {"@id": f"{ORIGIN}/#franciele"}

    remove_unconfirmed_claims(graph)
    scripts[0].string = json.dumps(
        {"@context": "https://schema.org", "@graph": graph},
        ensure_ascii=False,
        separators=(",", ":"),
    ).replace("</", "<\\/")
    insert_comment_before(
        scripts[0],
        "Structured data",
        " Structured data: verified entities only; do not add ratings, hours, prices or an address without client confirmation. ",
    )

    original_head = HEAD_RE.search(source)
    if not original_head or soup.head is None:
        raise RuntimeError(f"{relative}: cannot write structured data")
    return source[: original_head.start()] + str(soup.head) + source[original_head.end() :]


def matching_tag_end(source: str, start: int, tag: str) -> tuple[int, int]:
    token_re = re.compile(rf"</?{tag}\b[^>]*>", re.I)
    depth = 0
    for match in token_re.finditer(source, start):
        if match.group(0).startswith("</"):
            depth -= 1
            if depth == 0:
                return match.start(), match.end()
        elif not match.group(0).rstrip().endswith("/>"):
            depth += 1
    raise RuntimeError(f"Could not match closing {tag}")


def find_hero(source: str) -> tuple[int, int, int] | None:
    candidates = (
        (r"<section\b(?=[^>]*\bdata-pattern=[\"']hero[\"'])[^>]*>", "section"),
        (r"<header\b(?=[^>]*\bclass=[\"'][^\"']*\bsj-masthead\b)[^>]*>", "header"),
        (r"<header\b(?=[^>]*\bclass=[\"'][^\"']*\bsja-hero\b)[^>]*>", "header"),
    )
    for pattern, tag in candidates:
        match = re.search(pattern, source, re.I)
        if match:
            close_start, close_end = matching_tag_end(source, match.start(), tag)
            return close_start, close_end, match.start()
    return None


def add_main_navigation(relative: str, source: str) -> str:
    key = meta_key(relative)
    if key in {"index.html", "404.html"}:
        return EXISTING_JUMP_RE.sub("\n", source)
    source = EXISTING_JUMP_RE.sub("\n", source)
    language = language_for(relative)
    label = (
        "Pular a apresentação e continuar para o conteúdo principal"
        if language == "pt-BR"
        else "Skip the hero and continue to the main content"
    )
    text = "Continuar" if language == "pt-BR" else "Continue"
    link = (
        f'\n<a href="#main-content" class="skip-past-hero" aria-label="{label}">'
        f"{text}<span aria-hidden=\"true\">↓</span></a>\n"
    )
    target = (
        "\n<!-- Main-content target: kept immediately after the hero so fixed "
        "navigation cannot obscure the first meaningful section. -->\n"
        '<span id="main-content" class="sf-main-content-target" tabindex="-1"></span>\n'
    )
    hero = find_hero(source)
    if hero:
        _, close_end, _ = hero
        # Keep the control adjacent to, but outside, composition-specific hero
        # grids. This prevents decorative hero layers from covering the link.
        remainder = source[close_end:].lstrip()
        return source[:close_end] + link + target + "\n" + remainder

    # Contact intentionally has a compact form introduction instead of a hero.
    # Place the same navigation between that introduction and the form.
    if key == "contact.html":
        match = re.search(
            r"<header\b(?=[^>]*\bclass=[\"'][^\"']*\bsf-form-section-intro\b)[^>]*>",
            source,
            re.I,
        )
        if match:
            close_start, close_end = matching_tag_end(source, match.start(), "header")
            return source[:close_start] + link + source[close_start:close_end] + target + source[close_end:]
    raise RuntimeError(f"{relative}: no hero or compact introduction found for main-content navigation")


def process(path: Path) -> bool:
    relative = path.relative_to(ROOT).as_posix()
    original = path.read_text(encoding="utf-8")
    updated, meta = normalize_head(relative, original)
    updated = normalize_schema(relative, updated, meta)
    updated = add_main_navigation(relative, updated)
    if updated == original:
        return False
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    changed: list[str] = []
    for path in page_paths():
        if process(path):
            changed.append(path.relative_to(ROOT).as_posix())
    print(f"SEO upgrade checked {len(page_paths())} public HTML pages; updated {len(changed)}.")
    for relative in changed:
        print(f"  {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
