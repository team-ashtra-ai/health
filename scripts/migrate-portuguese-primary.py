#!/usr/bin/env python3
"""Promote Brazilian Portuguese pages to canonical routes and preserve English."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from urllib.parse import urljoin

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = "https://www.francielesofiati.com"

ROUTES = {
    "home": ("index.html", "index.html", "/"),
    "not-found": ("404.html", "404.html", "/404.html"),
    "about": ("about.html", "sobre.html", "/sobre.html"),
    "care": ("care.html", "cuidados.html", "/cuidados.html"),
    "consultation": ("consultation.html", "consulta.html", "/consulta.html"),
    "contact": ("contact.html", "contato.html", "/contato.html"),
    "cookies": ("cookies.html", "cookies.html", "/cookies.html"),
    "faq": ("faq.html", "perguntas-frequentes.html", "/perguntas-frequentes.html"),
    "journal": ("journal.html", "blog.html", "/blog.html"),
    "laser": ("laser.html", "laser.html", "/laser.html"),
    "legal": ("legal.html", "legal.html", "/legal.html"),
    "mission": ("mission.html", "missao.html", "/missao.html"),
    "privacy": ("privacy.html", "privacidade.html", "/privacidade.html"),
    "results": ("results.html", "resultados.html", "/resultados.html"),
    "skin": ("skin.html", "pele.html", "/pele.html"),
    "testimonials": ("testimonials.html", "depoimentos.html", "/depoimentos.html"),
    "thank-you": ("thank-you.html", "obrigada.html", "/obrigada.html"),
    "treatments": ("treatments.html", "tratamentos.html", "/tratamentos.html"),
    "values": ("values.html", "valores.html", "/valores.html"),
}

SEO = {
    "home": ("Cuidados estéticos e laser em Londrina | Franciele Sofiati", "Cuidado estético premium em Londrina com Franciele Sofiati: pele, laser, couro cabeludo e tratamentos planejados a partir de uma consulta responsável."),
    "about": ("Sobre Franciele Sofiati | Biomédica estética em Londrina", "Conheça Franciele Sofiati, biomédica estética e cosmetologista em Londrina, com atuação cuidadosa em pele, laser e tratamentos estéticos personalizados."),
    "care": ("Cuidados estéticos personalizados | Franciele Sofiati", "Entenda como os cuidados estéticos são planejados por indicação, contexto, preparo e acompanhamento individual."),
    "consultation": ("Consulta estética em Londrina | Franciele Sofiati", "Agende uma consulta estética com Franciele Sofiati em Londrina para avaliar pele, laser, tratamentos e expectativas com clareza."),
    "contact": ("Contato | Franciele Sofiati", "Entre em contato com Franciele Sofiati em Londrina para dúvidas, agendamento de consulta estética e orientações iniciais."),
    "cookies": ("Política de cookies | Franciele Sofiati", "Saiba como o site Franciele Sofiati usa cookies e tecnologias semelhantes, e gerencie suas preferências de consentimento."),
    "faq": ("Perguntas frequentes | Franciele Sofiati", "Respostas sobre consulta, tratamentos estéticos, preparo, recuperação, segurança e acompanhamento com Franciele Sofiati."),
    "journal": ("Blog de estética, pele e laser | Franciele Sofiati", "Conteúdos sobre pele, laser, estética responsável, preparo e cuidados de acompanhamento por Franciele Sofiati."),
    "laser": ("Laser estético em Londrina | Franciele Sofiati", "Tratamentos com laser em Londrina para pele, pigmentação, pelos e textura, com avaliação de indicação, preparo e recuperação."),
    "legal": ("Legal | Franciele Sofiati", "Legal, termos de uso e orientações institucionais do site Franciele Sofiati."),
    "mission": ("Missão | Franciele Sofiati", "A missão de Franciele Sofiati: cuidado estético responsável, natural e orientado por consulta, contexto e segurança."),
    "privacy": ("Privacidade e proteção de dados | Franciele Sofiati", "Entenda como informações de contato, consulta e navegação podem ser tratadas por Franciele Sofiati segundo princípios da LGPD."),
    "results": ("Resultados e expectativas | Franciele Sofiati", "Como Franciele Sofiati aborda resultados estéticos com expectativas realistas, acompanhamento e respeito à individualidade."),
    "skin": ("Cuidados com a pele em Londrina | Franciele Sofiati", "Cuidados personalizados para acne, textura, sensibilidade, viço e saúde da pele em Londrina com Franciele Sofiati."),
    "testimonials": ("Depoimentos | Franciele Sofiati", "Experiências e depoimentos sobre o cuidado estético conduzido por Franciele Sofiati em Londrina."),
    "thank-you": ("Obrigada pelo contato | Franciele Sofiati", "Confirmação de contato enviado para Franciele Sofiati."),
    "treatments": ("Tratamentos estéticos em Londrina | Franciele Sofiati", "Conheça tratamentos estéticos para pele, laser, colágeno, couro cabeludo e cuidados corporais com Franciele Sofiati."),
    "values": ("Valores | Franciele Sofiati", "Os valores que orientam o cuidado estético de Franciele Sofiati: clareza, responsabilidade, naturalidade e acompanhamento."),
}

LABELS = {
    "index.html": "Início",
    "sobre.html": "Sobre",
    "cuidados.html": "Cuidados",
    "consulta.html": "Consulta",
    "contato.html": "Contato",
    "cookies.html": "Cookies",
    "perguntas-frequentes.html": "Perguntas frequentes",
    "blog.html": "Blog",
    "laser.html": "Laser",
    "legal.html": "Legal",
    "missao.html": "Missão",
    "privacidade.html": "Privacidade",
    "resultados.html": "Resultados",
    "pele.html": "Pele",
    "depoimentos.html": "Depoimentos",
    "obrigada.html": "Obrigada",
    "tratamentos.html": "Tratamentos",
    "valores.html": "Valores",
}


def site_url(route: str) -> str:
    return urljoin(f"{DOMAIN}/", route.lstrip("/"))


def page_url(path: str) -> str:
    if path == "index.html":
        return f"{DOMAIN}/"
    if path == "en/index.html":
        return f"{DOMAIN}/en/"
    return f"{DOMAIN}/{path}"


def rewrite_relative(value: str, mapping: dict[str, str], from_pt: bool) -> str:
    if not value or value.startswith(("#", "mailto:", "tel:", "http:", "https:", "//", "data:")):
        return value
    base = "../" if from_pt else ""
    if from_pt and value.startswith("../"):
        value = value[3:]
    if not from_pt and value.startswith("../"):
        return value
    if re.search(r"[?#]", value):
        match = re.match(r"([^?#]*)([?#].*)", value)
        clean, suffix = match.groups() if match else (value, "")
    else:
        clean, suffix = value, ""
    if clean in mapping:
        return mapping[clean] + suffix
    return value


def update_head(soup: BeautifulSoup, page_id: str, pt_path: str, en_path: str) -> None:
    title, description = SEO.get(page_id, SEO["home"])
    if soup.title:
        soup.title.string = title
    meta = soup.find("meta", attrs={"name": "description"})
    if meta:
        meta["content"] = description
    canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
    if canonical:
        canonical["href"] = page_url(pt_path)
    for tag in soup.find_all("link", rel=lambda value: value and "alternate" in value):
        lang = tag.get("hreflang")
        if lang == "pt-BR":
            tag["href"] = page_url(pt_path)
        elif lang == "en":
            tag["href"] = page_url(en_path)
        elif lang == "x-default":
            tag["href"] = page_url(pt_path)
    for prop, content in {
        ("property", "og:title"): title,
        ("property", "og:description"): description,
        ("property", "og:url"): page_url(pt_path),
        ("property", "og:site_name"): "Franciele Sofiati · Biomédica estética · Esteticista · Cosmetologista",
        ("property", "og:locale"): "pt_BR",
        ("name", "twitter:title"): title,
        ("name", "twitter:description"): description,
    }.items():
        attr, key = prop
        tag = soup.find("meta", attrs={attr: key})
        if tag:
            tag["content"] = content
    alt_locale = soup.find("meta", attrs={"property": "og:locale:alternate"})
    if alt_locale:
        alt_locale["content"] = "en_US"
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(script.string or "{}")
        except json.JSONDecodeError:
            continue
        graph = data.get("@graph", []) if isinstance(data, dict) else []
        for item in graph:
            if not isinstance(item, dict):
                continue
            if item.get("@type") == "WebSite":
                item["url"] = f"{DOMAIN}/"
                item["name"] = "Franciele Sofiati · Biomédica estética · Esteticista · Cosmetologista"
            if item.get("@type") == "HealthAndBeautyBusiness":
                item["url"] = f"{DOMAIN}/"
                item["name"] = "Franciele Sofiati · Biomédica estética · Esteticista · Cosmetologista"
            if item.get("@type") == "Person":
                item["url"] = site_url("/sobre.html")
                item["jobTitle"] = "Biomédica estética · Esteticista · Cosmetologista"
            if item.get("@type") == "WebPage":
                item["url"] = page_url(pt_path)
                item["@id"] = f"{page_url(pt_path)}#webpage"
                item["name"] = title
                item["description"] = description
                item["inLanguage"] = "pt-BR"
                item["breadcrumb"] = {"@id": f"{page_url(pt_path)}#breadcrumb"}
            if item.get("@type") == "BreadcrumbList":
                item["@id"] = f"{page_url(pt_path)}#breadcrumb"
                elements = [{"@type": "ListItem", "position": 1, "name": "Início", "item": f"{DOMAIN}/"}]
                if pt_path != "index.html":
                    elements.append({"@type": "ListItem", "position": 2, "name": LABELS.get(pt_path, title), "item": page_url(pt_path)})
                item["itemListElement"] = elements
        script.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))


def transform_page(source: Path, destination: Path, page_id: str, mapping: dict[str, str], from_pt: bool) -> None:
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    html = soup.find("html")
    if html:
        html["lang"] = "pt-BR"
        html["data-default-lang"] = "pt-BR"
    body = soup.find("body")
    if body:
        body["data-site-root"] = ""
    en_path = f"en/{ROUTES[page_id][0]}"
    update_head(soup, page_id, destination.name, en_path)
    for tag in soup.find_all(["a", "link", "script", "img", "source", "form"]):
        for attr in ("href", "src", "srcset", "action"):
            if not tag.has_attr(attr):
                continue
            if attr == "srcset":
                parts = []
                for candidate in str(tag[attr]).split(","):
                    bits = candidate.strip().split()
                    if bits:
                        bits[0] = rewrite_relative(bits[0], mapping, from_pt)
                    parts.append(" ".join(bits))
                tag[attr] = ", ".join(parts)
            else:
                tag[attr] = rewrite_relative(str(tag[attr]), mapping, from_pt)
    destination.write_text(str(soup), encoding="utf-8")


def transform_english(source: Path, destination: Path, mapping: dict[str, str], page_id: str | None = None) -> None:
    soup = BeautifulSoup(source.read_text(encoding="utf-8"), "html.parser")
    body = soup.find("body")
    if body:
        body["data-site-root"] = "../"
    if page_id:
        old, new, _ = ROUTES[page_id]
        en_path = f"en/{old}"
        pt_path = new
    else:
        en_path = destination.relative_to(ROOT).as_posix()
        pt_path = "blog.html"
    if page_id or en_path.startswith("en/"):
        canonical = soup.find("link", rel=lambda value: value and "canonical" in value)
        if canonical:
            canonical["href"] = page_url(en_path)
        for tag in soup.find_all("link", rel=lambda value: value and "alternate" in value):
            lang = tag.get("hreflang")
            if lang == "en":
                tag["href"] = page_url(en_path)
            elif lang == "pt-BR":
                tag["href"] = page_url(pt_path)
            elif lang == "x-default":
                tag["href"] = page_url(pt_path)
        og_url = soup.find("meta", attrs={"property": "og:url"})
        if og_url:
            og_url["content"] = page_url(en_path)
        for script in soup.find_all("script", type="application/ld+json"):
            try:
                data = json.loads(script.string or "{}")
            except json.JSONDecodeError:
                continue
            graph = data.get("@graph", []) if isinstance(data, dict) else []
            for item in graph:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") == "WebPage":
                    item["url"] = page_url(en_path)
                    item["@id"] = f"{page_url(en_path)}#webpage"
                    item["breadcrumb"] = {"@id": f"{page_url(en_path)}#breadcrumb"}
                if item.get("@type") == "BreadcrumbList":
                    item["@id"] = f"{page_url(en_path)}#breadcrumb"
            script.string = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    for tag in soup.find_all(["a", "link", "script", "img", "source", "form"]):
        for attr in ("href", "src", "srcset", "action"):
            if not tag.has_attr(attr):
                continue
            if attr == "srcset":
                parts = []
                for candidate in str(tag[attr]).split(","):
                    bits = candidate.strip().split()
                    if bits and not bits[0].startswith(("#", "http:", "https:", "//", "data:", "../")):
                        bits[0] = "../" + mapping.get(bits[0], bits[0])
                    parts.append(" ".join(bits))
                tag[attr] = ", ".join(parts)
            else:
                value = str(tag[attr])
                if not value.startswith(("#", "http:", "https:", "//", "data:", "../", "mailto:", "tel:")):
                    tag[attr] = "../" + mapping.get(value, value)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(str(soup), encoding="utf-8")


def redirect_page(target: str) -> str:
    absolute = site_url(target)
    return f"""<!DOCTYPE html>
<html lang=\"pt-BR\">
<head>
<meta charset=\"utf-8\">
<meta name=\"robots\" content=\"noindex, follow\">
<meta http-equiv=\"refresh\" content=\"0; url={target}\">
<link rel=\"canonical\" href=\"{absolute}\">
<title>Redirecionando | Franciele Sofiati</title>
<script>window.location.replace({json.dumps(target)});</script>
</head>
<body>
<p>Redirecionando para <a href=\"{target}\">{absolute}</a>.</p>
</body>
</html>
"""


def main() -> int:
    old_to_pt = {old: new for _, (old, new, _) in ROUTES.items()}
    pt_mapping = {"pt/index.html": "index.html", **{f"pt/{old}": new for _, (old, new, _) in ROUTES.items()}, **old_to_pt}
    en_mapping = {old: old for _, (old, _, _) in ROUTES.items()}

    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "en" / "journal").mkdir(parents=True, exist_ok=True)
    for page_id, (old, new, _) in ROUTES.items():
        transform_english(ROOT / old, ROOT / "en" / old, en_mapping, page_id)
        transform_page(ROOT / "pt" / old, ROOT / new, page_id, pt_mapping, from_pt=True)
        if old != new and old != "index.html":
            (ROOT / old).write_text(redirect_page(new), encoding="utf-8")

    for article in (ROOT / "journal").glob("*.html"):
        transform_english(article, ROOT / "en" / "journal" / article.name, en_mapping)
        article.write_text(redirect_page("../blog.html"), encoding="utf-8")

    page_pairs = {
        "version": 2,
        "defaultLanguage": "pt-BR",
        "pages": [
            {"id": page_id, "en": f"en/{old}", "pt-BR": new}
            for page_id, (old, new, _) in ROUTES.items()
        ],
    }
    for article in sorted((ROOT / "en" / "journal").glob("*.html")):
        page_pairs["pages"].append({
            "id": f"journal-{article.stem}",
            "en": f"en/journal/{article.name}",
            "pt-BR": "blog.html",
        })
    (ROOT / "data" / "page-pairs.json").write_text(json.dumps(page_pairs, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    seo = json.loads((ROOT / "data" / "seo.json").read_text(encoding="utf-8"))
    seo["siteName"] = "Franciele Sofiati · Biomédica estética · Esteticista · Cosmetologista"
    seo["areaServed"] = "Londrina, Paraná, Brasil"
    (ROOT / "data" / "seo.json").write_text(json.dumps(seo, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
