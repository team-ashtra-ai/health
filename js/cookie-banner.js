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

  const initCookieBanner = () => {
    const key = "sofiati-cookie-consent";
    const banner = document.querySelector("[data-cookie-banner]");
    if (!banner) return;

    const preferences = banner.querySelector("[data-cookie-preferences]");
    const customize = banner.querySelector("[data-cookie-customize]");
    const save = banner.querySelector("[data-cookie-save]");
    const preferenceInput = banner.querySelector("[data-cookie-preference='preferences']");
    const setVisible = (visible) => document.body.classList.toggle("public-cookie-visible", visible);

    const readConsent = () => {
      const raw = storage.get(key);
      if (!raw) return null;
      try {
        return JSON.parse(raw);
      } catch (_error) {
        return { status: raw };
      }
    };

    const applyConsent = (consent) => {
      const status = consent?.status || "pending";
      document.documentElement.dataset.cookieConsent = status;
      if (preferenceInput) preferenceInput.checked = Boolean(consent?.preferences?.preferences);
      banner.classList.toggle("is-hidden", status !== "pending");
      setVisible(status === "pending");
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

    banner.querySelector("[data-cookie-reject]")?.addEventListener("click", () => persist("rejected", false));
    save?.addEventListener("click", () => persist("custom", Boolean(preferenceInput?.checked)));
    banner.querySelector("[data-cookie-accept]")?.addEventListener("click", () => persist("accepted", true));
  };

  document.addEventListener("sofiati:partials-loaded", initCookieBanner);
})();
