#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONCEPTS = ROOT / "concepts"

START = "/* SOFIATI LANGUAGE TOGGLE RUNTIME START */"
END = "/* SOFIATI LANGUAGE TOGGLE RUNTIME END */"

RUNTIME = r'''/* SOFIATI LANGUAGE TOGGLE RUNTIME START */
(function () {
  function normalizeLang(value) {
    return value === "pt" || value === "pt-BR" || value === "pt-br" ? "pt-BR" : "en";
  }

  function shortLang(value) {
    return normalizeLang(value) === "pt-BR" ? "pt" : "en";
  }

  function setLanguage(nextLang) {
    const normalized = normalizeLang(nextLang);
    const short = shortLang(normalized);

    document.documentElement.lang = normalized;
    document.documentElement.setAttribute("data-active-lang", short);

    document.querySelectorAll("[data-lang-switch]").forEach((control) => {
      const controlShort = shortLang(control.getAttribute("data-lang-switch"));
      const active = controlShort === short;

      control.setAttribute("aria-pressed", active ? "true" : "false");
      control.setAttribute("data-active", active ? "true" : "false");
      control.classList.toggle("is-active", active);
      control.classList.toggle("active", active);
    });
  }

  function currentInitialLang() {
    return (
      document.documentElement.getAttribute("lang") ||
      document.body?.getAttribute("data-default-lang") ||
      document.documentElement.getAttribute("data-default-lang") ||
      "en"
    );
  }

  document.addEventListener("click", function (event) {
    const control = event.target.closest("[data-lang-switch]");
    if (!control) return;

    event.preventDefault();
    setLanguage(control.getAttribute("data-lang-switch"));
  });

  function initialiseLanguageState() {
    setLanguage(currentInitialLang());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiseLanguageState);
  } else {
    initialiseLanguageState();
  }

  window.SofiatiSetLanguage = setLanguage;
})();
 /* SOFIATI LANGUAGE TOGGLE RUNTIME END */'''

def patch(path: Path) -> bool:
    text = path.read_text(encoding="utf-8")

    if START in text and END in text:
      before = text.split(START)[0]
      after = text.split(END, 1)[1]
      new = before + RUNTIME + after
    elif "/* SOFIATI HEADER RUNTIME END */" in text:
      new = text.replace("/* SOFIATI HEADER RUNTIME END */", RUNTIME + "\n\n/* SOFIATI HEADER RUNTIME END */")
    else:
      new = text.rstrip() + "\n\n" + RUNTIME + "\n"

    if new != text:
      path.write_text(new, encoding="utf-8")
      return True

    return False

changed = []
for path in sorted(CONCEPTS.glob("*/js/main.js")):
    if patch(path):
        changed.append(path.relative_to(ROOT))

for item in changed:
    print(item)

print(f"Updated {len(changed)} concept JS files.")
