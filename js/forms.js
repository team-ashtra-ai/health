(() => {
  "use strict";

  const initForms = () => {
    document.querySelectorAll("form[data-static-form]").forEach((form) => {
      form.addEventListener("submit", (event) => {
        if (!form.checkValidity()) return;
        event.preventDefault();
        form.dataset.submitted = "true";
      });
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", initForms, { once: true });
  } else {
    initForms();
  }
})();
