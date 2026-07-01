
(() => {
  "use strict";

  document.documentElement.classList.add("sofiati-js-ready");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  window.SofiatiFoundation = {
    reduceMotion: () => reduceMotion.matches,
    scrollToTop: () => window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" }),
    readyAt: new Date().toISOString(),
  };

  document.dispatchEvent(new CustomEvent("sofiati:foundation-ready"));
})();
