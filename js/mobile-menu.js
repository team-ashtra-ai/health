(() => {
  "use strict";

  let lastMenuTrigger = null;
  const focusableSelector = "a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex='-1'])";

  const menu = () => document.getElementById("mobile-menu");
  const isMenuOpen = () => menu()?.getAttribute("aria-hidden") === "false";
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
    focusableIn(panel)[0]?.focus({ preventScroll: true });
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
    lastMenuTrigger?.focus?.({ preventScroll: true });
  };

  const initMobileMenu = () => {
    document.addEventListener("click", (event) => {
      const toggle = event.target.closest("[data-menu-toggle]");
      const close = event.target.closest("[data-menu-close]");
      const panel = menu();

      if (toggle) {
        event.preventDefault();
        isMenuOpen() ? closeMenu() : openMenu(toggle);
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

  document.addEventListener("sofiati:partials-loaded", initMobileMenu);
})();
