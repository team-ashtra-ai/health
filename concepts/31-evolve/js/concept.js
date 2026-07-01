(() => {
  "use strict";

  const profile = {
    conceptId: "31-evolve",
    partialNames: ["header", "mobile-menu", "footer", "cookie-banner", "floating-widgets"],
  };
  const runtimeRoot = window.SofiatiConceptRuntime = window.SofiatiConceptRuntime || {};
  if (runtimeRoot[profile.conceptId]) return;
  runtimeRoot[profile.conceptId] = true;

  const cache = new Map();
  let lastMenuTrigger = null;
  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const storage = {
    get(key) {
      try {
        return window.localStorage.getItem(key);
      } catch (_error) {
        return null;
      }
    },
    set(key, value) {
      try {
        window.localStorage.setItem(key, value);
      } catch (_error) {
        document.documentElement.dataset.storageFallback = "true";
      }
    },
  };

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
  const isMenuOpen = () => menu()?.getAttribute("aria-hidden") === "false";
  const focusableSelector = "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])";
  const focusableIn = (root) => Array.from(root.querySelectorAll(focusableSelector)).filter((item) => !item.hasAttribute("hidden") && item.offsetParent !== null);

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
    const first = focusableIn(panel)[0];
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
      if (panel?.contains(event.target) && event.target.closest(".sf-mobile-link[href]")) closeMenu();
    });
    document.addEventListener("keydown", (event) => {
      const panel = menu();
      if (event.key === "Escape") closeMenu();
      if (event.key !== "Tab" || !panel || !isMenuOpen()) return;
      const items = focusableIn(panel);
      if (!items.length) return;
      const first = items[0];
      const last = items[items.length - 1];
      if (event.shiftKey && document.activeElement === first) {
        event.preventDefault();
        last.focus({ preventScroll: true });
      } else if (!event.shiftKey && document.activeElement === last) {
        event.preventDefault();
        first.focus({ preventScroll: true });
      }
    });
  };

  const wireCookie = () => {
    const key = `sofiati-cookie-${profile.conceptId}`;
    const banner = document.querySelector("[data-cookie-banner]");
    if (!banner) return;
    const preferences = banner.querySelector("[data-cookie-preferences]");
    const customize = banner.querySelector("[data-cookie-customize]");
    const save = banner.querySelector("[data-cookie-save]");
    const preferenceInput = banner.querySelector("[data-cookie-preference='preferences']");
    const setVisible = (visible) => document.body.classList.toggle("public-cookie-visible", visible);

    const readConsent = () => {
      const raw = storage.get(key);
      if (raw === "accepted" || raw === "rejected") {
        return { status: raw, preferences: { essential: true, preferences: raw === "accepted" } };
      }
      if (!raw) return null;
      try {
        const parsed = JSON.parse(raw);
        if (parsed && typeof parsed.status === "string") return parsed;
      } catch (_error) {
        return null;
      }
      return null;
    };

    const applyConsent = (consent) => {
      const status = consent?.status || "pending";
      document.documentElement.dataset.cookieConsent = status;
      if (preferenceInput) {
        preferenceInput.checked = Boolean(consent?.preferences?.preferences);
      }
      if (status !== "pending") {
        banner.classList.add("is-hidden");
        setVisible(false);
      } else {
        banner.classList.remove("is-hidden");
        setVisible(true);
      }
    };

    const persist = (status, rememberPreferences) => {
      const consent = {
        version: 1,
        status,
        preferences: {
          essential: true,
          preferences: Boolean(rememberPreferences),
        },
        updatedAt: new Date().toISOString(),
      };
      storage.set(key, JSON.stringify(consent));
      applyConsent(consent);
    };

    applyConsent(readConsent());

    customize?.addEventListener("click", () => {
      const nextOpen = preferences?.hasAttribute("hidden") ?? false;
      if (preferences) preferences.hidden = !nextOpen;
      if (save) save.hidden = !nextOpen;
      customize.setAttribute("aria-expanded", nextOpen ? "true" : "false");
    });

    banner.querySelector("[data-cookie-reject]")?.addEventListener("click", () => {
      persist("rejected", false);
    });

    save?.addEventListener("click", () => {
      persist("custom", Boolean(preferenceInput?.checked));
    });

    banner.querySelector("[data-cookie-accept]")?.addEventListener("click", () => {
      persist("accepted", true);
    });
  };

  const equivalentHref = (langValue) => {
    const current = location.pathname.split("/").pop() || "index.html";
    const url = new URL(current, location.href);
    url.searchParams.set("lang", langValue);
    return `${current}${url.search}${location.hash}`;
  };

  const setLanguage = (value, updateUrl = false) => {
    const lang = value === "pt" || value === "pt-BR" ? "pt-BR" : "en";
    const short = lang === "pt-BR" ? "pt" : "en";
    document.documentElement.lang = lang;
    document.documentElement.dataset.activeLang = short;
    storage.set(`sofiati-language-${profile.conceptId}`, lang);
    document.querySelectorAll("[data-lang-switch]").forEach((control) => {
      const target = control.dataset.langSwitch || "en";
      const active = target.toLowerCase().startsWith(short);
      control.setAttribute("aria-pressed", active ? "true" : "false");
      control.dataset.active = active ? "true" : "false";
      control.setAttribute("href", equivalentHref(target));
    });
    if (updateUrl && window.history?.replaceState) {
      const next = new URL(location.href);
      next.searchParams.set("lang", lang);
      window.history.replaceState(null, "", next);
    }
  };

  const wireLanguage = () => {
    document.addEventListener("click", (event) => {
      const control = event.target.closest("[data-lang-switch]");
      if (!control) return;
      event.preventDefault();
      setLanguage(control.dataset.langSwitch, true);
    });
    const urlLang = new URLSearchParams(location.search).get("lang");
    setLanguage(urlLang || storage.get(`sofiati-language-${profile.conceptId}`) || document.documentElement.lang || "en");
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
        window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
      });
    });
    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  };

  const markCurrentLinks = () => {
    const current = location.pathname.split("/").pop() || "index.html";
    document.querySelectorAll("a[href$='.html'], a[href*='.html?']").forEach((link) => {
      const href = (link.getAttribute("href") || "").split(/[?#]/)[0];
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
