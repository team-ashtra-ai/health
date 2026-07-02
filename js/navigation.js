(() => {
  "use strict";

  let initialized = false;

  const currentPage = () => {
    const page = location.pathname.split("/").pop();
    return page || "index.html";
  };

  const normalizeHref = (href) => {
    const clean = (href || "").split(/[?#]/)[0];
    if (!clean || clean === "/" || clean === "./") return "index.html";
    return clean.split("/").pop() || "index.html";
  };

  const markCurrentLinks = () => {
    const current = currentPage();
    document.querySelectorAll("a[href]").forEach((link) => {
      const normalized = normalizeHref(link.getAttribute("href"));
      link.removeAttribute("aria-current");
      if (normalized === current) link.setAttribute("aria-current", "page");
    });
  };

  const initNavigation = () => {
    if (initialized) return;
    initialized = true;

    markCurrentLinks();
  };

  document.addEventListener("sofiati:partials-loaded", initNavigation);
  if (document.body?.dataset.partialsReady === "true") initNavigation();
})();
