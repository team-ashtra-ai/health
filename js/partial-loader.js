(() => {
  "use strict";

  const partialNames = ["header", "mobile-menu", "footer", "cookie-banner", "floating-widgets"];
  const cache = new Map();

  const fetchPartial = (name) => {
    if (!cache.has(name)) {
      cache.set(
        name,
        fetch(`partials/${name}.html`, { cache: "no-store" }).then((response) => {
          if (!response.ok) throw new Error(`Missing partial: ${name}`);
          return response.text();
        })
      );
    }
    return cache.get(name);
  };

  const loadPartials = async () => {
    await Promise.all(
      partialNames.map(async (name) => {
        const mount = document.querySelector(`[data-sofiati-partial="${name}"]`);
        if (!mount) return;
        mount.innerHTML = await fetchPartial(name);
        mount.dataset.partialLoaded = "true";
      })
    );

    document.body.dataset.partialsReady = "true";
    document.dispatchEvent(new CustomEvent("sofiati:partials-loaded"));
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", loadPartials, { once: true });
  } else {
    loadPartials();
  }
})();
