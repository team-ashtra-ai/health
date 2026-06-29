
(() => {
  "use strict";

  const profile = {
  "conceptId": "35-atelier",
  "partialNames": [
    "header",
    "mobile-menu",
    "footer",
    "cookie-banner",
    "floating-widgets"
  ],
  "menuMode": "rule-drawer",
  "headerMode": "studio-ledger-header",
  "interactionTone": "ledger-button",
  "destinationWords": [
    "crafted",
    "studio",
    "bespoke",
    "atelier",
    "site",
    "with",
    "linework",
    "curated",
    "frames",
    "artistic",
    "section",
    "composition",
    "ivory",
    "paper",
    "base",
    "bronze",
    "sage",
    "panels",
    "blush",
    "handcrafted",
    "detail",
    "dark",
    "signature",
    "strip",
    "hero",
    "line",
    "trust",
    "route",
    "cream",
    "consultation",
    "craft",
    "note",
    "education",
    "sketches"
  ],
  "sectionRhythm": [
    "ivory",
    "bronze",
    "sage",
    "cream",
    "blush",
    "ivory",
    "sage",
    "cream",
    "bronze",
    "dark"
  ]
};
  const cache = new Map();
  let lastMenuTrigger = null;

  const applyDestinationSignature = () => {
    document.body.dataset.destinationSignature = profile.destinationWords.slice(0, 8).join("-");
    document.querySelectorAll("[data-content-section]").forEach((section, index) => {
      const word = profile.destinationWords[(index * 3) % profile.destinationWords.length] || profile.conceptId;
      const rhythm = profile.sectionRhythm[index % profile.sectionRhythm.length] || "ivory";
      section.style.setProperty("--concept-word-length", String(word.length));
      section.dataset.destinationWord = word;
      section.dataset.rhythmTone = rhythm;
    });
  };

  const fetchPartial = async (name) => {
    if (!cache.has(name)) {
      cache.set(name, fetch(`partials/${name}.html`, { cache: "no-store" }).then((response) => {
        if (!response.ok) throw new Error(`Missing partial ${name} for 35-atelier`);
        return response.text();
      }));
    }
    return cache.get(name);
  };

  const mountPartials = async () => {
    await Promise.all(profile.partialNames.map(async (name) => {
      const mount = document.querySelector(`[data-sofiati-partial="${name}"]`);
      if (!mount) return;
      mount.innerHTML = await fetchPartial(name);
      mount.dataset.partialLoaded = "true";
    }));
    document.dispatchEvent(new CustomEvent("sofiati:concept-partials-ready", { detail: profile }));
  };

  const menu = () => document.getElementById("mobile-menu");

  const openMenu = (trigger) => {
    const panel = menu();
    if (!panel) return;
    lastMenuTrigger = trigger || document.activeElement;
    panel.setAttribute("aria-hidden", "false");
    document.body.classList.add("public-menu-locked");
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => button.setAttribute("aria-expanded", "true"));
    const first = panel.querySelector("a[href], button:not([disabled])");
    if (first) first.focus({ preventScroll: true });
  };

  const closeMenu = () => {
    const panel = menu();
    if (!panel) return;
    panel.setAttribute("aria-hidden", "true");
    document.body.classList.remove("public-menu-locked");
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => button.setAttribute("aria-expanded", "false"));
    if (lastMenuTrigger && typeof lastMenuTrigger.focus === "function") {
      lastMenuTrigger.focus({ preventScroll: true });
    }
  };

  const wireMenu = () => {
    document.addEventListener("click", (event) => {
      const toggle = event.target.closest("[data-menu-toggle]");
      const close = event.target.closest("[data-menu-close]");
      const panel = menu();
      if (toggle) {
        event.preventDefault();
        if (panel?.getAttribute("aria-hidden") === "false") closeMenu();
        else openMenu(toggle);
      }
      if (close) {
        event.preventDefault();
        closeMenu();
      }
      if (panel && event.target === panel) closeMenu();
    });
    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeMenu();
    });
  };

  const wireCookie = () => {
    const key = `sofiati-cookie-${profile.conceptId}`;
    const banner = document.querySelector("[data-cookie-banner]");
    if (!banner) return;
    if (window.localStorage.getItem(key) === "accepted") banner.classList.add("is-hidden");
    banner.querySelector("[data-cookie-accept]")?.addEventListener("click", () => {
      window.localStorage.setItem(key, "accepted");
      banner.classList.add("is-hidden");
    });
  };

  const wireHeaderState = () => {
    const header = document.querySelector(".c35-header");
    if (!header) return;
    const update = () => header.toggleAttribute("data-scrolled", window.scrollY > 20);
    update();
    window.addEventListener("scroll", update, { passive: true });
  };

  const markCurrentLinks = () => {
    const current = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll('a[href$=".html"]').forEach((link) => {
      const href = link.getAttribute("href") || "";
      if (href === current) link.setAttribute("aria-current", "page");
    });
  };

  const init = async () => {
    await mountPartials();
    wireMenu();
    wireCookie();
    wireHeaderState();
    markCurrentLinks();
    applyDestinationSignature();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
