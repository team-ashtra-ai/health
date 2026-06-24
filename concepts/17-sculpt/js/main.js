(() => {
  const concept = "17-sculpt";
  const menuMode = "sheet";
  const observerMode = "stagger";
  document.body.dataset.jsReady = "true";

  const menu = document.querySelector("#mobile-menu");
  const open = document.querySelector("[data-menu-toggle]");
  const close = document.querySelector("[data-menu-close]");
  const setMenu = (active) => {
    if (!menu) return;
    menu.classList.toggle("is-open", active);
    menu.setAttribute("aria-hidden", String(!active));
    open?.setAttribute("aria-expanded", String(active));
    document.body.classList.toggle("menu-active-" + menuMode, active);
  };
  open?.addEventListener("click", () => setMenu(true));
  close?.addEventListener("click", () => setMenu(false));
  menu?.querySelectorAll("a").forEach((link, index) => {
    link.style.setProperty("--menu-index", index);
    link.addEventListener("click", () => setMenu(false));
  });

  const panels = [...document.querySelectorAll(".panel, .service-architecture, .responsible-note, .consultation-band")];
  if ("IntersectionObserver" in window) {
    const io = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        const delay = observerMode === "stagger" ? (panels.indexOf(entry.target) % 7) * 70 : 0;
        entry.target.style.transitionDelay = delay + "ms";
        entry.target.classList.add("is-visible");
        io.unobserve(entry.target);
      });
    }, { threshold: observerMode === "threshold" ? 0.22 : 0.12 });
    panels.forEach((panel) => io.observe(panel));
  } else {
    panels.forEach((panel) => panel.classList.add("is-visible"));
  }

  document.querySelectorAll("details").forEach((detail) => {
    detail.addEventListener("toggle", () => {
      if (detail.open && observerMode === "snap") {
        detail.scrollIntoView({ block: "nearest", behavior: "smooth" });
      }
    });
  });

  document.querySelectorAll("[data-consultation-form]").forEach((form) => {
    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const status = form.querySelector(".form-status");
      if (status) status.textContent = "Thank you. This static concept keeps requests local; WhatsApp is available for a direct consultation request.";
    });
  });

  const sticky = document.createElement("a");
  sticky.className = "sticky-contact";
  sticky.href = "consultation.html";
  sticky.textContent = concept + " consultation";
  document.body.appendChild(sticky);
  let lastY = 0;
  window.addEventListener("scroll", () => {
    const active = window.scrollY > 520 && window.scrollY >= lastY;
    sticky.style.opacity = active ? "1" : ".82";
    lastY = window.scrollY;
  }, { passive: true });
})();
