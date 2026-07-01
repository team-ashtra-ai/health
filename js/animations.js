(() => {
  "use strict";

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)");

  const initAnimations = () => {
    document.documentElement.classList.toggle("sofiati-reduce-motion", reduceMotion.matches);
  };

  reduceMotion.addEventListener?.("change", initAnimations);
  initAnimations();
})();
