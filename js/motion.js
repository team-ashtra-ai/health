(() => {
  const items = document.querySelectorAll(".component-section");
  items.forEach((i) => i.classList.add("reveal"));
  if (!("IntersectionObserver" in window)) {
    items.forEach((i) => i.classList.add("is-visible"));
    return;
  }
  const o = new IntersectionObserver(
    (es) =>
      es.forEach((e) => {
        if (e.isIntersecting) {
          e.target.classList.add("is-visible");
          o.unobserve(e.target);
        }
      }),
    { threshold: 0.12 },
  );
  items.forEach((i) => o.observe(i));
})();
