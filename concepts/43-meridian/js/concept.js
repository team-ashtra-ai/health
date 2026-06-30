(() => {
  "use strict";

  const profile = {
    conceptId: "43-meridian",
    partialNames: ["header", "mobile-menu", "footer", "cookie-banner", "floating-widgets"],
  };
  const cache = new Map();
  let lastMenuTrigger = null;

  const fetchPartial = async (name) => {
    if (!cache.has(name)) {
      cache.set(name, fetch(`partials/${name}.html`, { cache: "no-store" }).then((response) => {
        if (!response.ok) throw new Error(`Missing partial ${name} for ${profile.conceptId}`);
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
    panel.classList.add("is-open");
    panel.setAttribute("aria-hidden", "false");
    document.body.classList.add("public-menu-locked");
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      button.setAttribute("aria-expanded", "true");
      button.setAttribute("aria-controls", "mobile-menu");
    });
    const first = panel.querySelector("a[href], button:not([disabled])");
    if (first) first.focus({ preventScroll: true });
  };

  const closeMenu = () => {
    const panel = menu();
    if (!panel) return;
    panel.classList.remove("is-open");
    panel.setAttribute("aria-hidden", "true");
    document.body.classList.remove("public-menu-locked");
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", "mobile-menu");
    });
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

  const setLanguage = (value) => {
    const lang = value === "pt" || value === "pt-BR" ? "pt-BR" : "en";
    const short = lang === "pt-BR" ? "pt" : "en";
    document.documentElement.lang = lang;
    document.documentElement.dataset.activeLang = short;
    document.querySelectorAll("[data-lang-switch]").forEach((button) => {
      const active = (button.dataset.langSwitch || "en").toLowerCase().startsWith(short);
      button.setAttribute("aria-pressed", active ? "true" : "false");
      button.dataset.active = active ? "true" : "false";
    });
  };

  const wireLanguage = () => {
    document.addEventListener("click", (event) => {
      const button = event.target.closest("[data-lang-switch]");
      if (!button) return;
      event.preventDefault();
      setLanguage(button.dataset.langSwitch);
    });
    setLanguage(document.documentElement.lang || "en");
  };

  const wireFloatingTools = () => {
    const buttons = document.querySelectorAll("[data-back-to-top]");
    const update = () => {
      const visible = window.scrollY > Math.min(520, Math.max(220, window.innerHeight * 0.42));
      buttons.forEach((button) => {
        button.classList.toggle("is-visible", visible);
        button.setAttribute("aria-hidden", visible ? "false" : "true");
        button.tabIndex = visible ? 0 : -1;
      });
    };
    buttons.forEach((button) => {
      if (button.dataset.sofiatiTopReady === "true") return;
      button.dataset.sofiatiTopReady = "true";
      button.addEventListener("click", () => {
        const reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
      });
    });
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  };

  const markCurrentLinks = () => {
    const current = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll("a[href$='.html']").forEach((link) => {
      const href = link.getAttribute("href") || "";
      link.removeAttribute("aria-current");
      if (href === current) link.setAttribute("aria-current", "page");
    });
  };

  const init = async () => {
    await mountPartials();
    wireMenu();
    wireCookie();
    wireLanguage();
    wireFloatingTools();
    markCurrentLinks();
    document.body.dataset.partialsReady = "true";
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
