(() => {
  "use strict";

  const WHATSAPP_URL = "https://wa.me/5543991043536";
  const WHATSAPP_LABEL = "Open WhatsApp contact with Franciele Sofiati";
  const WHATSAPP_TEXT = "Message Franciele on WhatsApp";
  const TOP_LABEL = "Return to the top of the page";
  let scrollListenerReady = false;

  const conceptCode = () => {
    const concept = document.body?.dataset.concept || "";
    const match = concept.match(/^(\d{2})-/);
    return match ? match[1] : "01";
  };

  const makeImage = (src, alt) => {
    const image = document.createElement("img");
    image.src = src;
    image.alt = alt;
    image.setAttribute("aria-hidden", "true");
    return image;
  };

  const createWhatsApp = () => {
    const link = document.createElement("a");
    link.className = `floating-whatsapp floating-whatsapp-${conceptCode()}`;
    link.href = WHATSAPP_URL;
    link.target = "_blank";
    link.rel = "noopener";
    link.setAttribute("aria-label", WHATSAPP_LABEL);
    link.appendChild(makeImage("assets/icons/whatsapp.svg", ""));

    const label = document.createElement("b");
    label.textContent = WHATSAPP_TEXT;
    link.appendChild(label);

    return link;
  };

  const createBackToTop = () => {
    const button = document.createElement("button");
    button.className = `back-to-top back-to-top-${conceptCode()}`;
    button.type = "button";
    button.dataset.backToTop = "";
    button.setAttribute("aria-label", TOP_LABEL);
    button.setAttribute("aria-hidden", "true");
    button.tabIndex = -1;
    button.appendChild(makeImage("assets/icons/back-to-top.svg", ""));
    return button;
  };

  const ensureFloatingTools = () => {
    let tools = document.querySelector("[data-floating-tools]");

    if (!tools) {
      const mount = document.querySelector('[data-partial-mount="floating-widgets"]');
      tools = document.createElement("div");
      if (mount) {
        mount.innerHTML = "";
        mount.appendChild(tools);
      } else {
        document.body.appendChild(tools);
      }
    }

    tools.classList.add("floating-tools", `floating-tools-${conceptCode()}`);
    tools.dataset.floatingTools = "";

    if (!tools.querySelector(".floating-whatsapp")) {
      tools.appendChild(createWhatsApp());
    }

    if (!tools.querySelector("[data-back-to-top]")) {
      tools.appendChild(createBackToTop());
    }

    return tools;
  };

  const updateBackToTop = () => {
    const threshold = Math.min(520, Math.max(220, window.innerHeight * 0.48));
    const visible = window.scrollY > threshold;

    document.querySelectorAll("[data-back-to-top]").forEach((button) => {
      button.classList.toggle("is-visible", visible);
      button.setAttribute("aria-hidden", visible ? "false" : "true");
      button.tabIndex = visible ? 0 : -1;
    });
  };

  const wireBackToTop = () => {
    document.querySelectorAll("[data-back-to-top]").forEach((button) => {
      button.setAttribute("aria-label", TOP_LABEL);

      if (button.dataset.sofiatiBackTopReady === "true") return;
      button.dataset.sofiatiBackTopReady = "true";

      button.addEventListener("click", () => {
        const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({ top: 0, behavior: reduceMotion ? "auto" : "smooth" });
      });
    });

    if (!scrollListenerReady) {
      scrollListenerReady = true;
      window.addEventListener("scroll", updateBackToTop, { passive: true });
      window.addEventListener("resize", updateBackToTop);
    }

    updateBackToTop();
  };

  const normalizeWhatsApp = () => {
    document.querySelectorAll(".floating-whatsapp").forEach((link) => {
      link.href = WHATSAPP_URL;
      link.target = "_blank";
      link.rel = "noopener";
      link.setAttribute("aria-label", WHATSAPP_LABEL);

      const label = link.querySelector("b");
      if (label) label.textContent = WHATSAPP_TEXT;
    });
  };

  const initFloatingWidgets = () => {
    const tools = ensureFloatingTools();
    normalizeWhatsApp();
    wireBackToTop();

    requestAnimationFrame(() => {
      tools.classList.add("is-loaded");
    });
  };

  const init = () => {
    initFloatingWidgets();
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }

  document.addEventListener("sofiati:partials-ready", init);
  window.setTimeout(init, 900);
})();
