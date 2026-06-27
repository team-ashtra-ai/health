#!/usr/bin/env python3
"""Build the Sofiati translation inventory and optional EN/PT runtime.

The static HTML remains English-authored as the source of truth. By default
this script only writes reports and data. Source JavaScript is changed only
when `--apply-runtime` is paired with an explicit concept or `--all-concepts`.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_DIR = ROOT / "concepts"
DATA_DIR = ROOT / "data"
FINAL_DIR = ROOT / "final"

SKIP_PARENTS = {"script", "style", "noscript", "template"}
TRANSLATABLE_ATTRS = {"alt", "aria-label", "content", "placeholder", "title"}
CONTACT_RE = re.compile(r"(@|https?://|mailto:|\bwa\.me\b|\w+@\w+)", re.I)
ALPHA_RE = re.compile(r"[A-Za-z]")
TECHNICAL_RE = re.compile(
    r"(^#|^--|{{|}}|<|>|url\(|\.(?:html|svg|png|jpe?g|webp|css|js)\b|"
    r"^width=device-width|charset=|application/ld\+json|^\d+(?:px|rem|em|%)?$)",
    re.I,
)
ENGLISH_RESIDUE_RE = re.compile(
    r"\b(and|with|through|before|after|care|skin|quality|source|partial|section|mount|"
    r"decorative|visual|concept|story|background|guidance|evaluation)\b",
    re.I,
)

CURATED_TRANSLATIONS = {
    "Home": "Inicio",
    "About": "Sobre",
    "Care": "Cuidados",
    "Laser": "Laser",
    "Skin": "Pele",
    "Results": "Resultados",
    "Consultation": "Consulta",
    "Contact": "Contato",
    "FAQ": "Perguntas",
    "Journal": "Diario",
    "Blog": "Blog",
    "Legal": "Legal",
    "Privacy": "Privacidade",
    "Cookies": "Cookies",
    "Accessibility": "Acessibilidade",
    "Mission": "Missao",
    "Values": "Valores",
    "Testimonials": "Depoimentos",
    "Sitemap": "Mapa do site",
    "Menu": "Menu",
    "Close": "Fechar",
    "Open menu": "Abrir menu",
    "Site menu": "Menu do site",
    "Site language": "Idioma do site",
    "Book consultation": "Agendar consulta",
    "Start consultation": "Comecar pela consulta",
    "Begin consultation": "Comecar consulta",
    "View laser": "Ver laser",
    "View care": "Ver cuidados",
    "View skin": "Ver pele",
    "Send request": "Enviar solicitacao",
    "Name": "Nome",
    "WhatsApp": "WhatsApp",
    "Email": "E-mail",
    "Treatment interest": "Interesse de tratamento",
    "Select one": "Selecione uma opcao",
    "Professional evaluation": "Avaliacao profissional",
    "Laser care": "Cuidados com laser",
    "Skin care": "Cuidados com a pele",
    "Results with responsibility": "Resultados com responsabilidade",
    "Message": "Mensagem",
    "Sofiati home": "Inicio Sofiati",
    "Sofiati logo": "Logo Sofiati",
    "Advanced Aesthetic Biomedicine": "Biomedicina Estetica Avancada",
    "Advanced Aesthetic Biomedicine · Londrina, PR": "Biomedicina Estetica Avancada · Londrina, PR",
    "CRBM 6277 · Londrina, PR": "CRBM 6277 · Londrina, PR",
    "Dossier 04": "Dossie 04",
    "Evaluation before protocol selection.": "Avaliacao antes da escolha do protocolo.",
    "I understand this request does not replace individual professional evaluation.": (
        "Entendo que esta solicitacao nao substitui uma avaliacao profissional individual."
    ),
    "Your message is sent through Formspree and should not include sensitive medical details.": (
        "Sua mensagem e enviada pelo Formspree e nao deve incluir detalhes medicos sensiveis."
    ),
    "Return to the top of the page": "Voltar ao topo da pagina",
    "Message Franciele on WhatsApp": "Enviar mensagem para Franciele no WhatsApp",
    "Open WhatsApp contact with Franciele Sofiati": "Abrir contato no WhatsApp com Franciele Sofiati",
}

LANGUAGE_RUNTIME = r'''
/* SOFIATI LANGUAGE RUNTIME START */
(() => {
  "use strict";

  const STORAGE_KEY = "sofiati-language";
  const DATA_URL = "../../data/translation-strings.json";
  const ATTRS = ["alt", "aria-label", "content", "placeholder", "title"];
  const SKIP_TAGS = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE"]);
  let translations = new Map();
  let activeLanguage = "en";
  let observerReady = false;
  let applyScheduled = false;
  const originalText = new WeakMap();
  const originalAttrs = new WeakMap();

  const normalize = (value) => String(value || "").replace(/\s+/g, " ").trim();
  const isPortuguese = (language) => language === "pt" || language === "pt-BR";
  const preferredLanguage = () => (isPortuguese(window.localStorage.getItem(STORAGE_KEY)) ? "pt" : "en");

  const translatedValue = (value) => {
    const source = normalize(value);
    if (!source || activeLanguage !== "pt") return source;
    return translations.get(source) || source;
  };

  const shouldSkipTextNode = (node) => {
    if (!node.parentElement || !normalize(node.textContent)) return true;
    return Boolean(node.parentElement.closest("script,style,noscript,template"));
  };

  const preserveWhitespace = (original, translated) => {
    const leading = original.match(/^\s*/)?.[0] || "";
    const trailing = original.match(/\s*$/)?.[0] || "";
    return `${leading}${translated}${trailing}`;
  };

  const applyTextNodes = () => {
    const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        return shouldSkipTextNode(node) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      },
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      if (!originalText.has(node)) originalText.set(node, node.textContent);
      const source = originalText.get(node);
      const translated = translatedValue(source);
      node.textContent = preserveWhitespace(source, translated);
    });
  };

  const originalAttributeValue = (element, attr) => {
    let store = originalAttrs.get(element);
    if (!store) {
      store = {};
      originalAttrs.set(element, store);
    }
    if (!(attr in store)) store[attr] = element.getAttribute(attr) || "";
    return store[attr];
  };

  const applyAttributes = () => {
    document.querySelectorAll("*").forEach((element) => {
      if (SKIP_TAGS.has(element.tagName)) return;
      ATTRS.forEach((attr) => {
        if (!element.hasAttribute(attr)) return;
        const source = originalAttributeValue(element, attr);
        const translated = translatedValue(source);
        if (translated) element.setAttribute(attr, translated);
      });
    });
  };

  const updateControls = () => {
    document.querySelectorAll("[data-lang-switch]").forEach((button) => {
      const selected = button.dataset.langSwitch === activeLanguage;
      button.setAttribute("aria-pressed", selected ? "true" : "false");
    });
  };

  const applyLanguage = (language = activeLanguage) => {
    activeLanguage = isPortuguese(language) ? "pt" : "en";
    document.documentElement.lang = activeLanguage === "pt" ? "pt-BR" : "en";
    document.body.dataset.currentLang = activeLanguage;
    applyTextNodes();
    applyAttributes();
    updateControls();
  };

  const setLanguage = (language) => {
    activeLanguage = isPortuguese(language) ? "pt" : "en";
    window.localStorage.setItem(STORAGE_KEY, activeLanguage);
    applyLanguage(activeLanguage);
  };

  const wireControls = () => {
    document.querySelectorAll("[data-lang-switch]").forEach((button) => {
      if (button.dataset.sofiatiLanguageReady === "true") return;
      button.dataset.sofiatiLanguageReady = "true";
      button.addEventListener("click", () => setLanguage(button.dataset.langSwitch));
    });
    updateControls();
  };

  const loadTranslations = async () => {
    try {
      const response = await fetch(DATA_URL, { cache: "no-store" });
      if (!response.ok) throw new Error(`Translation data unavailable: ${response.status}`);
      const data = await response.json();
      translations = new Map(
        (data.strings || [])
          .filter((row) => row.source && row.pt_BR && row.pt_BR !== row.source)
          .map((row) => [normalize(row.source), row.pt_BR])
      );
    } catch (error) {
      console.warn("Sofiati language runtime kept English source copy.", error);
      translations = new Map();
    }
  };

  const scheduleApply = () => {
    if (applyScheduled) return;
    applyScheduled = true;
    window.requestAnimationFrame(() => {
      applyScheduled = false;
      wireControls();
      applyLanguage(activeLanguage);
    });
  };

  const observePartials = () => {
    if (observerReady || !document.body) return;
    observerReady = true;
    const observer = new MutationObserver(scheduleApply);
    observer.observe(document.body, { childList: true, subtree: true });
  };

  const initLanguage = async () => {
    activeLanguage = preferredLanguage();
    await loadTranslations();
    wireControls();
    applyLanguage(activeLanguage);
    observePartials();
  };

  window.SofiatiLanguage = { applyLanguage, setLanguage };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLanguage, { once: true });
  } else {
    initLanguage();
  }

  document.addEventListener("sofiati:partials-ready", () => {
    window.requestAnimationFrame(scheduleApply);
  });
})();
/* SOFIATI LANGUAGE RUNTIME END */
'''.strip()

LANGUAGE_BLOCK_RE = re.compile(
    r"\n*/\* SOFIATI LANGUAGE RUNTIME START \*/[\s\S]*?/\* SOFIATI LANGUAGE RUNTIME END \*/\n*",
    re.M,
)


class VisibleStringParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.strings: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        self.stack.append(tag)
        self._collect_attrs(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._collect_attrs(tag.lower(), attrs)

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index] == tag:
                del self.stack[index:]
                return

    def handle_data(self, data: str) -> None:
        if any(parent in SKIP_PARENTS for parent in self.stack):
            return
        self._add(data)

    def _collect_attrs(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {name.lower(): value or "" for name, value in attrs}
        for name, value in attr_map.items():
            if name not in TRANSLATABLE_ATTRS:
                continue
            if name == "content" and not self._meta_content_is_copy(tag, attr_map):
                continue
            self._add(value)

    @staticmethod
    def _meta_content_is_copy(tag: str, attrs: dict[str, str]) -> bool:
        if tag != "meta":
            return True
        name = attrs.get("name", "").lower()
        prop = attrs.get("property", "").lower()
        return name in {"description", "twitter:title", "twitter:description"} or prop in {
            "og:title",
            "og:description",
            "og:site_name",
        }

    def _add(self, value: str) -> None:
        normalized = normalize_text(value)
        if should_keep(normalized):
            self.strings.append(normalized)


def normalize_text(value: str) -> str:
    return " ".join(str(value or "").split())


def should_keep(value: str) -> bool:
    value = normalize_text(value)
    if not value or len(value) < 2:
        return False
    if not ALPHA_RE.search(value):
        return False
    if CONTACT_RE.search(value):
        return False
    if TECHNICAL_RE.search(value):
        return False
    if value in {"Franciele Sofiati", "CRBM 6277", "Londrina, PR", "PT", "EN"}:
        return False
    return True


def concept_folders() -> list[Path]:
    return sorted(path for path in CONCEPTS_DIR.glob("[0-9][0-9]-*") if path.is_dir())


def concept_by_name(name: str) -> Path:
    matches = [path for path in concept_folders() if path.name == name or path.name.startswith(f"{name}-")]
    if len(matches) != 1:
        names = ", ".join(path.name for path in concept_folders())
        raise SystemExit(f"Could not identify concept {name!r}. Available concepts: {names}")
    return matches[0]


def visible_strings(path: Path) -> list[str]:
    parser = VisibleStringParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    parser.close()
    return parser.strings


def inventory_paths(concept: Path) -> list[Path]:
    paths = list(sorted(concept.glob("*.html")))
    partials = concept / "partials"
    if partials.exists():
        paths.extend(sorted(partials.glob("*.html")))
    return paths


def existing_translation_memory() -> dict[str, str]:
    path = DATA_DIR / "translation-strings.json"
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    memory: dict[str, str] = {}
    for row in data.get("strings", []):
        source = normalize_text(row.get("source", ""))
        target = normalize_text(row.get("pt_BR", ""))
        if useful_existing_translation(source, target):
            memory[source] = target
    return memory


def useful_existing_translation(source: str, target: str) -> bool:
    if not source or not target or source == target:
        return False
    if not should_keep(source):
        return False
    if TECHNICAL_RE.search(target):
        return False
    if ENGLISH_RESIDUE_RE.search(target):
        return False
    return True


def translation_map() -> dict[str, str]:
    translations = existing_translation_memory()
    translations.update(CURATED_TRANSLATIONS)
    return translations


def runtime_status(concept: Path) -> dict[str, object]:
    js = concept / "js" / "main.js"
    partials = concept / "partials"
    js_text = js.read_text(encoding="utf-8", errors="replace") if js.exists() else ""
    surface = ""
    for name in ("status-banner.html", "header.html", "mobile-menu.html"):
        path = partials / name
        if path.exists():
            surface += path.read_text(encoding="utf-8", errors="replace")
    return {
        "concept": concept.name,
        "mainJsExists": js.exists(),
        "languageRuntimeInstalled": "SOFIATI LANGUAGE RUNTIME START" in js_text,
        "languageControls": surface.count("data-lang-switch"),
        "englishDefaultPages": sum(
            1
            for path in concept.glob("*.html")
            if 'lang="en"' in path.read_text(encoding="utf-8", errors="replace")
            and 'data-default-lang="en"' in path.read_text(encoding="utf-8", errors="replace")
        ),
    }


def build_inventory() -> dict[str, object]:
    concepts = concept_folders()
    translations = translation_map()
    counter: Counter[str] = Counter()
    by_page: dict[str, list[str]] = {}
    by_concept: dict[str, dict[str, int]] = {}

    for concept in concepts:
        concept_counter: Counter[str] = Counter()
        for page in inventory_paths(concept):
            strings = visible_strings(page)
            rel = page.relative_to(ROOT).as_posix()
            unique = sorted(set(strings), key=str.lower)
            by_page[rel] = unique
            counter.update(set(strings))
            concept_counter.update(set(strings))
        covered = sum(1 for text in concept_counter if translations.get(text, text) != text)
        by_concept[concept.name] = {
            "uniqueStringCount": len(concept_counter),
            "translatedOrPhraseCovered": covered,
        }

    rows = []
    covered = 0
    for text, count in sorted(counter.items(), key=lambda item: (-item[1], item[0].lower())):
        pt = translations.get(text, text)
        if pt != text:
            covered += 1
        rows.append(
            {
                "source": text,
                "occurrences": count,
                "pt_BR": pt,
                "needsHumanTranslation": pt == text,
            }
        )

    statuses = [runtime_status(concept) for concept in concepts]
    return {
        "mode": "english-source-with-optional-pt-runtime",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "note": (
            "HTML files remain English-authored. Portuguese is applied at runtime from exact "
            "translation strings; untranslated source text stays English until human-reviewed."
        ),
        "conceptCount": len(concepts),
        "htmlFileCount": sum(1 for concept in concepts for _ in concept.glob("*.html")),
        "uniqueStringCount": len(rows),
        "translatedOrPhraseCovered": covered,
        "runtimeStatus": statuses,
        "runtimeWarnings": [
            f"{status['concept']} has language controls but no runtime"
            for status in statuses
            if status["languageControls"] and not status["languageRuntimeInstalled"]
        ],
        "byConcept": by_concept,
        "strings": rows,
        "byPage": by_page,
    }


def write_reports(inventory: dict[str, object]) -> None:
    FINAL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    (DATA_DIR / "translation-strings.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (FINAL_DIR / "translation-report.json").write_text(
        json.dumps(inventory, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    warnings = inventory["runtimeWarnings"]
    lines = [
        "# Translation Runtime Report",
        "",
        "- Mode: english-source-with-optional-pt-runtime",
        f"- Concept count: {inventory['conceptCount']}",
        f"- HTML file count: {inventory['htmlFileCount']}",
        f"- Unique source strings: {inventory['uniqueStringCount']}",
        f"- Covered by exact translations: {inventory['translatedOrPhraseCovered']}",
        f"- Runtime warnings: {len(warnings)}",
        "- HTML rewrite: no",
        "",
        "English remains the source of truth in every HTML file.",
        "Portuguese switching is runtime-only and uses exact, human-reviewable string mappings.",
        "Any untranslated medical, legal or beauty copy intentionally remains English until reviewed.",
    ]
    if warnings:
        lines.append("")
        lines.append("## Runtime Warnings")
        lines.extend(f"- {warning}" for warning in warnings)
    (FINAL_DIR / "translation-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def install_language_runtime(concept: Path) -> str:
    js = concept / "js" / "main.js"
    if not js.exists():
        raise SystemExit(f"Missing JS runtime target: {js.relative_to(ROOT)}")
    original = js.read_text(encoding="utf-8")
    cleaned = LANGUAGE_BLOCK_RE.sub("\n", original).rstrip()
    updated = f"{cleaned}\n\n{LANGUAGE_RUNTIME}\n"
    if updated != original:
        js.write_text(updated, encoding="utf-8")
        return "updated"
    return "unchanged"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--concept", action="append", default=[], help="Concept folder to modify, e.g. 04-renew.")
    parser.add_argument("--all-concepts", action="store_true", help="Allow runtime installation across all concepts.")
    parser.add_argument("--apply-runtime", action="store_true", help="Install the EN/PT runtime into selected concept JS files.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero when runtime warnings remain.")
    return parser.parse_args()


def selected_runtime_targets(args: argparse.Namespace) -> list[Path]:
    if not args.apply_runtime:
        return []
    if args.all_concepts:
        return concept_folders()
    if not args.concept:
        raise SystemExit("--apply-runtime requires --concept or --all-concepts")
    return [concept_by_name(name) for name in args.concept]


def main() -> None:
    args = parse_args()
    applied = {}
    for concept in selected_runtime_targets(args):
        applied[concept.name] = install_language_runtime(concept)

    inventory = build_inventory()
    write_reports(inventory)

    summary = {
        "mode": inventory["mode"],
        "conceptCount": inventory["conceptCount"],
        "htmlFileCount": inventory["htmlFileCount"],
        "uniqueStringCount": inventory["uniqueStringCount"],
        "translatedOrPhraseCovered": inventory["translatedOrPhraseCovered"],
        "runtimeWarningCount": len(inventory["runtimeWarnings"]),
        "runtimeApplied": applied,
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    if args.strict and inventory["runtimeWarnings"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
