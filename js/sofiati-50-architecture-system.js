(() => {
  const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)");

  const closestSection = (node) => node.closest("[data-architecture-section]");

  const markVisibleSections = () => {
    const sections = [
      ...document.querySelectorAll("[data-architecture-interaction]"),
    ];
    sections.forEach((section) => {
      if (!section.dataset.architectureState)
        section.dataset.architectureState = "waiting";
    });
    if (prefersReduced.matches || !("IntersectionObserver" in window)) {
      sections.forEach((section) => {
        section.dataset.architectureState = "visible";
      });
      return;
    }
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting)
            entry.target.dataset.architectureState = "visible";
        });
      },
      { rootMargin: "0px 0px -12% 0px", threshold: 0.18 },
    );
    sections.forEach((section) => observer.observe(section));
  };

  const enhanceSelectableRows = () => {
    document
      .querySelectorAll(
        '[data-architecture-interaction="route-selector"], [data-architecture-interaction="accordion-guidance"], [data-architecture-interaction="journal-carousel"], [data-architecture-interaction="process-stepper"]',
      )
      .forEach((section) => {
        if (section.dataset.architectureEnhanced === "true") return;
        const items = [
          ...section.querySelectorAll(
            ".atlas-card-row article, .atlas-bullets li",
          ),
        ];
        if (!items.length) return;
        section.dataset.architectureEnhanced = "true";
        items.forEach((item, index) => {
          item.tabIndex = 0;
          item.dataset.architectureItem = String(index + 1);
          if (index === 0) item.dataset.architectureActive = "true";
          item.addEventListener("click", () => activate(items, index));
          item.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
              event.preventDefault();
              activate(items, index);
            }
            if (event.key === "ArrowRight" || event.key === "ArrowDown") {
              event.preventDefault();
              const next = items[(index + 1) % items.length];
              next.focus();
              activate(items, (index + 1) % items.length);
            }
            if (event.key === "ArrowLeft" || event.key === "ArrowUp") {
              event.preventDefault();
              const previous = items[(index + items.length - 1) % items.length];
              previous.focus();
              activate(items, (index + items.length - 1) % items.length);
            }
          });
        });
      });
  };

  const activate = (items, activeIndex) => {
    items.forEach((item, index) => {
      item.dataset.architectureActive =
        index === activeIndex ? "true" : "false";
    });
  };

  const updateActiveSection = () => {
    const sections = [
      ...document.querySelectorAll("[data-architecture-section]"),
    ];
    if (!sections.length) return;
    let active = sections[0];
    for (const section of sections) {
      const rect = section.getBoundingClientRect();
      if (rect.top <= window.innerHeight * 0.4) active = section;
    }
    document.body.dataset.activeArchitectureSection =
      active.dataset.architectureSection || "";
  };

  const addStickyCta = () => {
    if (
      !document.querySelector(
        '[data-interaction="sticky-cta"], [data-architecture-interaction="sticky-cta"]',
      )
    )
      return;
    if (document.querySelector(".architecture-sticky-cta")) return;
    const link = document.createElement("a");
    link.className = "architecture-sticky-cta";
    link.href = "consultation.html";
    link.textContent = "Consultation";
    link.setAttribute("aria-label", "Request consultation");
    document.body.appendChild(link);
  };

  const init = () => {
    markVisibleSections();
    enhanceSelectableRows();
    updateActiveSection();
    addStickyCta();
  };

  document.addEventListener("scroll", updateActiveSection, { passive: true });
  document.addEventListener("sofiati:partials-ready", init);
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
