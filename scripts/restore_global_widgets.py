#!/usr/bin/env python3
"""Restore Sofiati global floating widgets and themed cookie loaders."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONCEPTS = ROOT / "concepts"

COOKIE_BLOCK = """<!-- SOFIATI FOOTER COOKIE BAR START -->
<script src="assets/js/sofiati-footer-cookie.js" defer data-sofiati-cookie-loader></script>
<!-- SOFIATI FOOTER COOKIE BAR END -->"""

MAIN_JS = r'''(() => {
  "use strict";

  const WHATSAPP_URL = "https://wa.me/5543991043536";
  const WHATSAPP_LABEL = "Open WhatsApp contact with Franciele Sofiati";
  const WHATSAPP_TEXT = "Message Franciele on WhatsApp";
  const TOP_LABEL = "Return to the top of the page";
  let scrollListenerReady = false;

  const conceptCode = () => {
    const concept = document.body?.dataset.concept || "";
    const match = concept.match(/^(\d{2})-/);
    return match ? match[1] : "01";
  };

  const makeImage = (src, alt) => {
    const image = document.createElement("img");
    image.src = src;
    image.alt = alt;
    image.setAttribute("aria-hidden", "true");
    return image;
  };

  const createWhatsApp = () => {
    const link = document.createElement("a");
    link.className = `floating-whatsapp floating-whatsapp-${conceptCode()}`;
    link.href = WHATSAPP_URL;
    link.target = "_blank";
    link.rel = "noopener";
    link.setAttribute("aria-label", WHATSAPP_LABEL);
    link.appendChild(makeImage("assets/icons/whatsapp.svg", ""));

    const label = document.createElement("b");
    label.textContent = WHATSAPP_TEXT;
    link.appendChild(label);

    return link;
  };

  const createBackToTop = () => {
    const button = document.createElement("button");
    button.className = `back-to-top back-to-top-${conceptCode()}`;
    button.type = "button";
    button.dataset.backToTop = "";
    button.setAttribute("aria-label", TOP_LABEL);
    button.setAttribute("aria-hidden", "true");
    button.tabIndex = -1;
    button.appendChild(makeImage("assets/icons/back-to-top.svg", ""));
    return button;
  };

  const ensureFloatingTools = () => {
    let tools = document.querySelector("[data-floating-tools]");

    if (!tools) {
      const mount = document.querySelector('[data-partial-mount="floating-widgets"]');
      tools = document.createElement("div");
      if (mount) {
        mount.innerHTML = "";
        mount.appendChild(tools);
      } else {
        document.body.appendChild(tools);
      }
    }

    tools.classList.add("floating-tools", `floating-tools-${conceptCode()}`);
    tools.dataset.floatingTools = "";

    if (!tools.querySelector(".floating-whatsapp")) {
      tools.appendChild(createWhatsApp());
    }

    if (!tools.querySelector("[data-back-to-top]")) {
      tools.appendChild(createBackToTop());
    }

    return tools;
  };

  const updateBackToTop = () => {
    const threshold = Math.min(520, Math.max(220, window.innerHeight * 0.48));
    const visible = window.scrollY > threshold;

    document.querySelectorAll("[data-back-to-top]").forEach((button) => {
      button.classList.toggle("is-visible", visible);
      button.setAttribute("aria-hidden", visible ? "false" : "true");
      button.tabIndex = visible ? 0 : -1;
    });
  };

  const wireBackToTop = () => {
    document.querySelectorAll("[data-back-to-top]").forEach((button) => {
      button.setAttribute("aria-label", TOP_LABEL);

      if (button.dataset.sofiatiBackTopReady === "true") return;
      button.dataset.sofiatiBackTopReady = "true";

      button.addEventListener("click", () => {
        const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      });
    });

    if (!scrollListenerReady) {
      scrollListenerReady = true;
      window.addEventListener("scroll", updateBackToTop, { passive: true });
      window.addEventListener("resize", updateBackToTop);
    }

    updateBackToTop();
  };

  const normalizeWhatsApp = () => {
    document.querySelectorAll(".floating-whatsapp").forEach((link) => {
      link.href = WHATSAPP_URL;
      link.target = "_blank";
      link.rel = "noopener";
      link.setAttribute("aria-label", WHATSAPP_LABEL);

      const label = link.querySelector("b");
      if (label) label.textContent = WHATSAPP_TEXT;
    });
  };

  const initFloatingWidgets = () => {
    const tools = ensureFloatingTools();
    normalizeWhatsApp();
    wireBackToTop();

    requestAnimationFrame(() => {
      tools.classList.add("is-loaded");
    });
  };

  const init = () => {
    initFloatingWidgets();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }

  document.addEventListener("sofiati:partials-ready", init);
  window.setTimeout(init, 900);
})();
'''


def concept_dirs() -> list[Path]:
    return sorted(
        path
        for path in CONCEPTS.iterdir()
        if path.is_dir() and re.match(r"^\d{2}-", path.name)
    )


def write_if_changed(path: Path, text: str) -> bool:
    old = path.read_text(encoding="utf-8") if path.exists() else ""
    if old == text:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return True


def restore_main_js(concept: Path) -> bool:
    return write_if_changed(concept / "js" / "main.js", MAIN_JS)


def add_cookie_loader(page: Path) -> bool:
    html = page.read_text(encoding="utf-8")
    if "sofiati-footer-cookie.js" in html:
        return False

    if re.search(r"</body\s*>", html, flags=re.I):
      updated = re.sub(r"</body\s*>", COOKIE_BLOCK + "\n</body>", html, count=1, flags=re.I)
    else:
      updated = html.rstrip() + "\n" + COOKIE_BLOCK + "\n"

    return write_if_changed(page, updated)


def restore_partial_labels(concept: Path) -> int:
    changed = 0
    whatsapp = concept / "partials" / "floating-whatsapp.html"
    if whatsapp.exists():
        text = whatsapp.read_text(encoding="utf-8")
        updated = re.sub(
            r'aria-label="[^"]*"',
            'aria-label="Open WhatsApp contact with Franciele Sofiati"',
            text,
            count=1,
        )
        updated = re.sub(
            r"<b>.*?</b>",
            "<b>Message Franciele on WhatsApp</b>",
            updated,
            count=1,
            flags=re.S,
        )
        changed += int(write_if_changed(whatsapp, updated))

    back_to_top = concept / "partials" / "back-to-top.html"
    if back_to_top.exists():
        text = back_to_top.read_text(encoding="utf-8")
        updated = re.sub(
            r'aria-label="[^"]*"',
            'aria-label="Return to the top of the page"',
            text,
            count=1,
        )
        changed += int(write_if_changed(back_to_top, updated))

    return changed


def upgrade_cookie_script(concept: Path) -> bool:
    script = concept / "assets" / "js" / "sofiati-footer-cookie.js"
    if not script.exists():
        return False

    text = script.read_text(encoding="utf-8")
    updated = text.replace(
        'const STORAGE_KEY = "sofiatiFooterCookie:" + CONFIG.code;',
        'const STORAGE_KEY = "sofiatiFooterCookie:v2:" + CONFIG.code;',
    )
    updated = updated.replace(
        "analytics: mode === \"all\",",
        "analytics: false,",
    )
    updated = updated.replace(
        "<strong>Cookies:</strong> essential cookies keep this site working. Optional cookies help improve the experience.",
        "<strong>Cookies:</strong> essential storage keeps this site working. Optional preferences are only used if enabled.",
    )
    updated = re.sub(
        r"\n    window\.setTimeout\(\(\) => \{\n"
        r"      if \(!localStorage\.getItem\(STORAGE_KEY\) && document\.body\.contains\(bar\)\) \{\n"
        r"        saveConsent\(\"essential\"\);\n"
        r"        bar\.remove\(\);\n"
        r"      \}\n"
        r"    \}, CONFIG\.autoDelayMs\);\n",
        "\n",
        updated,
    )

    return write_if_changed(script, updated)


def main() -> None:
    totals = {
        "main_js": 0,
        "html": 0,
        "partials": 0,
        "cookie_js": 0,
    }

    for concept in concept_dirs():
        totals["main_js"] += int(restore_main_js(concept))
        totals["partials"] += restore_partial_labels(concept)
        totals["cookie_js"] += int(upgrade_cookie_script(concept))

        for page in sorted(concept.glob("*.html")):
            totals["html"] += int(add_cookie_loader(page))

    print(
        "Restored widgets: "
        f"{totals['main_js']} main.js files, "
        f"{totals['html']} HTML cookie loaders, "
        f"{totals['partials']} partial labels, "
        f"{totals['cookie_js']} cookie scripts."
    )


if __name__ == "__main__":
    main()
