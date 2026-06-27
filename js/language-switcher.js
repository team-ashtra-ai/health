(() => {
  const storageKey = "sofiati-language";
  const defaultLanguage = "pt";
  const maps = window.SofiatiTranslations || { enToPt: {}, ptToEn: {} };
  const blockedParents = new Set(["SCRIPT", "STYLE", "NOSCRIPT", "TEMPLATE"]);
  const attributes = [
    "alt",
    "aria-label",
    "content",
    "placeholder",
    "title",
    "value",
  ];

  function preferredLanguage() {
    const stored = localStorage.getItem(storageKey);
    return stored === "en" || stored === "pt" ? stored : defaultLanguage;
  }

  function mapFor(language) {
    return language === "en" ? maps.ptToEn || {} : maps.enToPt || {};
  }

  function translateValue(value, language) {
    if (!value || !value.trim()) return value;
    const map = mapFor(language);
    const trimmed = value.trim();
    const translated = map[trimmed];
    if (!translated || translated === trimmed) return value;
    const leading = value.match(/^\s*/)?.[0] || "";
    const trailing = value.match(/\s*$/)?.[0] || "";
    return `${leading}${translated}${trailing}`;
  }

  function shouldTranslateAttribute(element, attribute) {
    if (element.closest("[data-no-translate]")) return false;
    if (attribute !== "content") return true;
    if (element.tagName !== "META") return false;
    const key =
      element.getAttribute("name") || element.getAttribute("property") || "";
    return /description|title|image:alt|twitter/.test(key);
  }

  function translateTextNodes(root, language) {
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode(node) {
        const parent = node.parentElement;
        if (
          !parent ||
          blockedParents.has(parent.tagName) ||
          parent.closest("[data-no-translate]")
        ) {
          return NodeFilter.FILTER_REJECT;
        }
        return node.nodeValue.trim()
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_SKIP;
      },
    });
    const nodes = [];
    while (walker.nextNode()) nodes.push(walker.currentNode);
    nodes.forEach((node) => {
      node.nodeValue = translateValue(node.nodeValue, language);
    });
  }

  function translateAttributes(root, language) {
    root.querySelectorAll("*").forEach((element) => {
      attributes.forEach((attribute) => {
        if (
          !element.hasAttribute(attribute) ||
          !shouldTranslateAttribute(element, attribute)
        )
          return;
        element.setAttribute(
          attribute,
          translateValue(element.getAttribute(attribute), language),
        );
      });
    });
  }

  function updateControls(language) {
    document.querySelectorAll("[data-language-option]").forEach((button) => {
      const active = button.dataset.languageOption === language;
      button.setAttribute("aria-pressed", String(active));
    });
  }

  function applyLanguage(language) {
    document.documentElement.lang = language === "en" ? "en" : "pt-BR";
    document.body.dataset.language = language;
    document.title = translateValue(document.title, language);
    translateTextNodes(document.body, language);
    translateAttributes(document, language);
    updateControls(language);
    document.dispatchEvent(
      new CustomEvent("sofiati:language-ready", { detail: { language } }),
    );
  }

  function setLanguage(language) {
    const next = language === "en" ? "en" : "pt";
    localStorage.setItem(storageKey, next);
    applyLanguage(next);
  }

  function bindControls() {
    document.querySelectorAll("[data-language-option]").forEach((button) => {
      if (button.dataset.languageBound === "true") return;
      button.dataset.languageBound = "true";
      button.addEventListener("click", () =>
        setLanguage(button.dataset.languageOption),
      );
    });
    updateControls(preferredLanguage());
  }

  function init() {
    bindControls();
    applyLanguage(preferredLanguage());
  }

  document.addEventListener("DOMContentLoaded", init);
  document.addEventListener("sofiati:partials-ready", init);
  document.addEventListener("sofiati:content-added", init);
})();
