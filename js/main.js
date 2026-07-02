(() => {
  "use strict";

  document.documentElement.classList.add("sofiati-js-ready");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  window.SofiatiFoundation = {
    reduceMotion: () => reduceMotion.matches,
    scrollToTop: () => window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" }),
    readyAt: new Date().toISOString(),
  };

  let floatingToolsReady = false;

  const initFloatingTools = () => {
    if (floatingToolsReady) return;
    const buttons = document.querySelectorAll("[data-back-to-top]");
    if (!buttons.length) return;
    floatingToolsReady = true;

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
      button.addEventListener("click", () => window.SofiatiFoundation.scrollToTop());
    });

    window.addEventListener("scroll", update, { passive: true });
    window.addEventListener("resize", update);
    update();
  };

  document.addEventListener("sofiati:partials-loaded", initFloatingTools);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initFloatingTools, { once: true });
  } else {
    initFloatingTools();
  }
  document.dispatchEvent(new CustomEvent("sofiati:foundation-ready"));
})();
