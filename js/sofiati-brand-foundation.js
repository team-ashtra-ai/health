
(() => {
  "use strict";

  document.documentElement.classList.add("sofiati-js-ready");

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  document.addEventListener("click", (event) => {
    const top = event.target.closest("[data-back-to-top]");
    if (!top) return;
    event.preventDefault();
    window.scrollTo({ top: 0, behavior: reduceMotion.matches ? "auto" : "smooth" });
  });

  document.addEventListener("click", (event) => {
    const language = event.target.closest("[data-language-option]");
    if (!language) return;
    const next = language.getAttribute("data-language-option") || "en";
    document.documentElement.lang = next;
    document.querySelectorAll("[data-language-option]").forEach((button) => {
      button.setAttribute("aria-pressed", button === language ? "true" : "false");
    });
  });

  window.SofiatiFoundation = {
    reduceMotion: () => reduceMotion.matches,
    readyAt: new Date().toISOString(),
  };

  document.dispatchEvent(new CustomEvent("sofiati:foundation-ready"));
})();
