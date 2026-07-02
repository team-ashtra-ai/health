(() => {
  "use strict";

  const focusableSelector = [
    "a[href]",
    "button:not([disabled])",
    "input:not([disabled])",
    "select:not([disabled])",
    "textarea:not([disabled])",
    "[tabindex]:not([tabindex='-1'])",
  ].join(",");

  let initialized = false;
  let lastTrigger = null;

  const getMenu = () => document.getElementById("mobile-menu");
  const getDialog = () => getMenu()?.querySelector(".sf-mobile-dialog");
  const isOpen = () => getMenu()?.getAttribute("aria-hidden") === "false";

  const visibleFocusable = (root) =>
    Array.from(root.querySelectorAll(focusableSelector)).filter((element) => {
      if (element.hasAttribute("hidden") || element.getAttribute("aria-hidden") === "true") return false;
      return element.offsetWidth > 0 || element.offsetHeight > 0 || element === document.activeElement;
    });

  const setToggleState = (open) => {
    document.querySelectorAll("[data-menu-toggle]").forEach((button) => {
      button.setAttribute("aria-expanded", open ? "true" : "false");
      button.setAttribute("aria-controls", "mobile-menu");
    });
  };

  const openMenu = (trigger) => {
    const menu = getMenu();
    const dialog = getDialog();
    if (!menu || !dialog || isOpen()) return;

    lastTrigger = trigger || document.activeElement;
    menu.inert = false;
    menu.removeAttribute("inert");
    menu.classList.add("is-open");
    menu.setAttribute("aria-hidden", "false");
    document.body.classList.add("public-menu-locked");
    setToggleState(true);

    requestAnimationFrame(() => {
      const first = dialog.querySelector("[data-menu-close]") || visibleFocusable(dialog)[0] || dialog;
      first.focus({ preventScroll: true });
    });
  };

  const closeMenu = ({ restoreFocus = true } = {}) => {
    const menu = getMenu();
    if (!menu || !isOpen()) return;

    menu.classList.remove("is-open");
    menu.setAttribute("aria-hidden", "true");
    menu.inert = true;
    menu.setAttribute("inert", "");
    document.body.classList.remove("public-menu-locked");
    setToggleState(false);

    if (restoreFocus) lastTrigger?.focus?.({ preventScroll: true });
    lastTrigger = null;
  };

  const keepFocusInDialog = (event) => {
    if (event.key !== "Tab" || !isOpen()) return;

    const dialog = getDialog();
    if (!dialog) return;

    const focusable = visibleFocusable(dialog);
    if (!focusable.length) {
      event.preventDefault();
      dialog.focus({ preventScroll: true });
      return;
    }

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus({ preventScroll: true });
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus({ preventScroll: true });
    }
  };

  const initMobileMenu = () => {
    if (initialized) return;
    initialized = true;
    const menu = getMenu();
    if (menu && !isOpen()) {
      menu.inert = true;
      menu.setAttribute("inert", "");
    }
    setToggleState(false);

    document.addEventListener("click", (event) => {
      const toggle = event.target.closest("[data-menu-toggle]");
      const close = event.target.closest("[data-menu-close]");
      const menu = getMenu();
      const dialog = getDialog();

      if (toggle) {
        event.preventDefault();
        isOpen() ? closeMenu() : openMenu(toggle);
        return;
      }

      if (!menu || !isOpen()) return;

      if (close) {
        event.preventDefault();
        closeMenu();
        return;
      }

      if (event.target.closest("#mobile-menu a[href]")) {
        closeMenu({ restoreFocus: false });
        return;
      }

      if (dialog && !dialog.contains(event.target)) closeMenu();
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && isOpen()) {
        closeMenu();
        return;
      }

      keepFocusInDialog(event);
    });
  };

  document.addEventListener("sofiati:partials-loaded", initMobileMenu);
  if (document.body?.dataset.partialsReady === "true") initMobileMenu();
})();
