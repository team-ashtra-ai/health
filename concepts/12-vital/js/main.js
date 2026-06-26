(() => {
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

/* SOFIATI HEADER RUNTIME START */
(() => {
  "use strict";

  const MENU_SELECTOR = "#mobile-menu";
  let lastTrigger = null;

  const menu = () => document.querySelector(MENU_SELECTOR);
  const triggers = () => document.querySelectorAll("[data-menu-toggle]");

  const setExpanded = (expanded) => {
    triggers().forEach((button) => {
      button.setAttribute("aria-expanded", expanded ? "true" : "false");
      button.setAttribute("aria-label", expanded ? "Close menu" : "Open menu");
    });
  };

  const syncMenu = () => {
    const panel = menu();
    if (!panel) return;
    const open = panel.classList.contains("is-open");
    panel.setAttribute("aria-hidden", open ? "false" : "true");
    document.body.classList.toggle("public-menu-locked", open);
    setExpanded(open);
  };

  const openMenu = (trigger) => {
    const panel = menu();
    if (!panel) return;
    lastTrigger = trigger || document.activeElement;
    panel.classList.add("is-open");
    syncMenu();
    window.requestAnimationFrame(() => panel.focus({ preventScroll: true }));
  };

  const closeMenu = ({ restoreFocus = true } = {}) => {
    const panel = menu();
    if (!panel) return;
    panel.classList.remove("is-open");
    syncMenu();
    if (restoreFocus && lastTrigger && typeof lastTrigger.focus === "function") {
      lastTrigger.focus({ preventScroll: true });
    }
  };

  const toggleMenu = (trigger) => {
    if (menu()?.classList.contains("is-open")) closeMenu();
    else openMenu(trigger);
  };

  document.addEventListener("click", (event) => {
    const toggle = event.target.closest("[data-menu-toggle]");
    if (toggle) {
      event.preventDefault();
      toggleMenu(toggle);
      return;
    }

    if (event.target.closest("[data-menu-close]")) {
      event.preventDefault();
      closeMenu();
      return;
    }

    if (event.target.closest("#mobile-menu a")) {
      closeMenu({ restoreFocus: false });
    }
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && menu()?.classList.contains("is-open")) {
      closeMenu();
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", syncMenu, { once: true });
  } else {
    syncMenu();
  }

  document.addEventListener("sofiati:partials-ready", syncMenu);
})();
/* SOFIATI HEADER RUNTIME END */
