(() => {
  "use strict";

  const initLazyload = () => {
    document.querySelectorAll("img:not([loading])").forEach((image) => {
      image.loading = "lazy";
    });
    document.querySelectorAll("img:not([decoding])").forEach((image) => {
      image.decoding = "async";
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initLazyload, { once: true });
  } else {
    initLazyload();
  }
})();
