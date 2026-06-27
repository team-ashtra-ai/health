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
    link.appendChild(makeImage("../../assets/generated/concept-20/icons/sofiati-concept-20-whatsapp-cta-icon.svg", ""));

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
    button.appendChild(makeImage("../../assets/generated/concept-20/icons/sofiati-concept-20-back-to-top-icon.svg", ""));
    return button;
  };

  const ensureFloatingTools = () => {
    let tools = document.querySelector("[data-floating-tools]");

    if (!tools) {
      const mount = document.querySelector(
        '[data-partial-mount="floating-widgets"]',
      );
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
        const reduceMotion = window.matchMedia(
          "(prefers-reduced-motion: reduce)",
        ).matches;
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

/* SOFIATI LANGUAGE TOGGLE RUNTIME START */
(function () {
  function normalizeLang(value) {
    return value === "pt" || value === "pt-BR" || value === "pt-br"
      ? "pt-BR"
      : "en";
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

  document.addEventListener("click", function (event) {
    const control = event.target.closest("[data-lang-switch]");
    if (!control) return;
    event.preventDefault();
    setLanguage(control.getAttribute("data-lang-switch"));
  });

  function initialiseLanguageState() {
    setLanguage(
      document.documentElement.getAttribute("lang") ||
        document.body?.getAttribute("data-default-lang") ||
        document.documentElement.getAttribute("data-default-lang") ||
        "en",
    );
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initialiseLanguageState);
  } else {
    initialiseLanguageState();
  }

  window.SofiatiSetLanguage = setLanguage;
})();
/* SOFIATI LANGUAGE TOGGLE RUNTIME END */

/* SOFIATI MOBILE MENU RUNTIME START */
(function () {
  const MENU_SELECTOR = "#mobile-menu";
  const LOCK_CLASS = "public-menu-locked";
  let lastTrigger = null;

  function getMenu() {
    return document.querySelector(MENU_SELECTOR);
  }

  function openMenu(trigger) {
    const menu = getMenu();
    if (!menu) return;

    lastTrigger = trigger || document.activeElement;
    menu.classList.add("is-open");
    menu.setAttribute("aria-hidden", "false");
    document.body.classList.add(LOCK_CLASS);

    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      button.setAttribute("aria-expanded", "true");
      button.setAttribute("aria-controls", "mobile-menu");
    });

    const firstFocusable = menu.querySelector(
      "a[href], button:not([disabled]), [tabindex]:not([tabindex='-1'])",
    );
    if (firstFocusable) firstFocusable.focus({ preventScroll: true });
  }

  function closeMenu() {
    const menu = getMenu();
    if (!menu) return;

    menu.classList.remove("is-open");
    menu.setAttribute("aria-hidden", "true");
    document.body.classList.remove(LOCK_CLASS);

    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", "mobile-menu");
    });

    if (lastTrigger && typeof lastTrigger.focus === "function") {
      lastTrigger.focus({ preventScroll: true });
    }
  }

  document.addEventListener("click", function (event) {
    const toggle = event.target.closest("[data-menu-toggle]");
    const close = event.target.closest("[data-menu-close]");
    const menu = getMenu();

    if (toggle) {
      event.preventDefault();
      if (menu?.classList.contains("is-open")) closeMenu();
      else openMenu(toggle);
      return;
    }

    if (close) {
      event.preventDefault();
      closeMenu();
      return;
    }

    if (menu?.classList.contains("is-open") && event.target === menu) {
      closeMenu();
    }
  });

  document.addEventListener("keydown", function (event) {
    if (event.key === "Escape") closeMenu();
  });

  document.addEventListener("DOMContentLoaded", function () {
    const menu = getMenu();
    if (menu && !menu.hasAttribute("aria-hidden")) {
      menu.setAttribute("aria-hidden", "true");
    }

    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      if (!button.hasAttribute("aria-expanded"))
        button.setAttribute("aria-expanded", "false");
      if (!button.hasAttribute("aria-controls"))
        button.setAttribute("aria-controls", "mobile-menu");
    });
  });
})();
/* SOFIATI MOBILE MENU RUNTIME END */
