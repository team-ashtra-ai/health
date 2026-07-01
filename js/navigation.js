(() => {
  "use strict";

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

  const currentPage = () => location.pathname.split("/").pop() || "index.html";

  const markCurrentLinks = () => {
    const current = currentPage();
    document.querySelectorAll("a[href$='.html'], a[href*='.html?'], a[href='./'], a[href='/']").forEach((link) => {
      const href = (link.getAttribute("href") || "").split(/[?#]/)[0];
      const normalized = href === "/" || href === "./" ? "index.html" : href.split("/").pop();
      link.removeAttribute("aria-current");
      if (normalized === current) link.setAttribute("aria-current", "page");
    });
  };

  const equivalentHref = (langValue) => {
    const current = currentPage();
    const url = new URL(current, location.href);
    url.searchParams.set("lang", langValue);
    return `${current}${url.search}${location.hash}`;
  };

  const setLanguage = (value, updateUrl = false) => {
    const lang = value === "pt" || value === "pt-BR" ? "pt-BR" : "en";
    const short = lang === "pt-BR" ? "pt" : "en";

    document.documentElement.lang = lang;
    document.documentElement.dataset.activeLang = short;
    storage.set("sofiati-language", lang);

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

  const initNavigation = () => {
    markCurrentLinks();

    document.addEventListener("click", (event) => {
      const control = event.target.closest("[data-lang-switch]");
      if (!control) return;
      event.preventDefault();
      setLanguage(control.dataset.langSwitch, true);
    });

    const urlLang = new URLSearchParams(location.search).get("lang");
    setLanguage(urlLang || storage.get("sofiati-language") || document.documentElement.lang || "en");
  };

  document.addEventListener("sofiati:partials-loaded", initNavigation);
})();
