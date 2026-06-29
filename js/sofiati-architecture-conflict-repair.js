/*
Sofiati Architecture Conflict Repair JS
- Deduplicates repeated navs in header.
- Keeps mobile menu closed by default.
- Provides one accessible mobile menu toggle.
- Prevents architecture JS/partials from leaving the drawer open over the hero.
- Reduces duplicated floating consultation UI when it overlaps.
*/

(function () {
  "use strict";

  const MOBILE_QUERY = "(max-width: 900px)";

  function textOf(el) {
    return (el.textContent || "").replace(/\s+/g, " ").trim().toLowerCase();
  }

  function linkSignature(nav) {
    const links = Array.from(nav.querySelectorAll("a[href]"));
    return links
      .map((a) => {
        const href = (a.getAttribute("href") || "").split("#")[0].trim().toLowerCase();
        const text = textOf(a);
        return href + "::" + text;
      })
      .filter(Boolean);
  }

  function overlapRatio(a, b) {
    if (!a.length || !b.length) return 0;
    const setA = new Set(a);
    const setB = new Set(b);
    let common = 0;
    for (const item of setA) {
      if (setB.has(item)) common += 1;
    }
    return common / Math.min(setA.size || 1, setB.size || 1);
  }

  function dedupeHeaderNavs() {
    const scopes = Array.from(
      document.querySelectorAll('[data-partial-mount="header"], header, .site-header, .sofiati-header')
    );

    for (const scope of scopes) {
      const navs = Array.from(scope.querySelectorAll("nav")).filter((nav) => {
        if (nav.closest('[data-partial-mount="mobile-menu"]')) return false;
        if (nav.dataset.sofiatiHiddenDuplicateNav === "true") return false;
        return linkSignature(nav).length >= 3;
      });

      if (navs.length < 2) continue;

      const keep = [];
      for (const nav of navs) {
        const sig = linkSignature(nav);
        const duplicateOfKept = keep.some((kept) => overlapRatio(sig, linkSignature(kept)) >= 0.72);

        if (duplicateOfKept) {
          nav.dataset.sofiatiHiddenDuplicateNav = "true";
          nav.setAttribute("aria-hidden", "true");
        } else {
          keep.push(nav);
        }
      }
    }
  }

  function ensureMobileMountHasLinks(mobileMount) {
    if (!mobileMount) return;
    if (mobileMount.querySelectorAll("a[href]").length >= 3) return;

    const header = document.querySelector('[data-partial-mount="header"], header, .site-header, .sofiati-header');
    if (!header) return;

    const nav = Array.from(header.querySelectorAll("nav"))
      .filter((n) => n.dataset.sofiatiHiddenDuplicateNav !== "true")
      .sort((a, b) => linkSignature(b).length - linkSignature(a).length)[0];

    if (!nav) return;

    const cloned = nav.cloneNode(true);
    cloned.removeAttribute("id");
    cloned.querySelectorAll("[id]").forEach((el) => el.removeAttribute("id"));
    mobileMount.appendChild(cloned);
  }

  function findMenuButtons() {
    const candidates = Array.from(document.querySelectorAll("button, a, [role='button']"));

    return candidates.filter((el) => {
      const label = [
        el.getAttribute("aria-label") || "",
        el.getAttribute("data-menu-toggle") || "",
        el.getAttribute("data-mobile-menu-toggle") || "",
        el.textContent || "",
      ].join(" ").toLowerCase();

      if (el.closest('[data-partial-mount="mobile-menu"]')) return false;

      return (
        /\bmenu\b/.test(label) ||
        label.includes("open menu") ||
        label.includes("mobile menu") ||
        el.className.toString().toLowerCase().includes("menu-toggle") ||
        el.className.toString().toLowerCase().includes("mobile-menu")
      );
    });
  }

  function closeMenu(mobileMount, buttons) {
    if (!mobileMount) return;
    mobileMount.removeAttribute("data-open");
    mobileMount.setAttribute("aria-hidden", "true");
    document.body.classList.remove("sofiati-menu-open");
    for (const button of buttons) {
      button.setAttribute("aria-expanded", "false");
    }
  }

  function openMenu(mobileMount, buttons) {
    if (!mobileMount) return;
    ensureMobileMountHasLinks(mobileMount);
    mobileMount.setAttribute("data-open", "true");
    mobileMount.setAttribute("aria-hidden", "false");
    document.body.classList.add("sofiati-menu-open");
    for (const button of buttons) {
      button.setAttribute("aria-expanded", "true");
    }

    const firstLink = mobileMount.querySelector("a[href], button");
    if (firstLink) {
      setTimeout(() => firstLink.focus({ preventScroll: true }), 50);
    }
  }

  function setupMobileMenu() {
    const mobileMount = document.querySelector('[data-partial-mount="mobile-menu"]');
    const buttons = findMenuButtons();

    if (!mobileMount) {
      for (const button of buttons) {
        button.setAttribute("aria-expanded", "false");
      }
      return;
    }

    mobileMount.setAttribute("aria-hidden", "true");
    mobileMount.removeAttribute("data-open");

    if (!mobileMount.id) {
      mobileMount.id = "sofiati-mobile-menu";
    }

    for (const button of buttons) {
      button.setAttribute("aria-controls", mobileMount.id);
      button.setAttribute("aria-expanded", "false");

      if (button.dataset.sofiatiMenuBound === "true") continue;
      button.dataset.sofiatiMenuBound = "true";

      button.addEventListener("click", function (event) {
        if (!window.matchMedia(MOBILE_QUERY).matches) return;

        event.preventDefault();
        event.stopPropagation();

        if (mobileMount.getAttribute("data-open") === "true") {
          closeMenu(mobileMount, buttons);
        } else {
          openMenu(mobileMount, buttons);
        }
      });
    }

    mobileMount.addEventListener("click", function (event) {
      const target = event.target;
      if (target && target.closest && target.closest("a[href]")) {
        closeMenu(mobileMount, buttons);
      }
    });

    document.addEventListener("keydown", function (event) {
      if (event.key === "Escape") {
        closeMenu(mobileMount, buttons);
      }
    });

    window.addEventListener("resize", function () {
      if (!window.matchMedia(MOBILE_QUERY).matches) {
        closeMenu(mobileMount, buttons);
      }
    });
  }

  function repairHeroContrast() {
    const heroSections = Array.from(
      document.querySelectorAll(
        'section[data-section="01"], section[data-role="opening-promise"]'
      )
    );

    for (const section of heroSections) {
      section.setAttribute("data-hero-contrast-repaired", "true");

      const copy = section.querySelector(".atlas-section__copy");
      if (copy) {
        copy.style.color = "var(--sofiati-ink, #252321)";
      }

      section.querySelectorAll("h1,h2,p,.eyebrow").forEach((el) => {
        el.style.textShadow = "none";
      });
    }
  }

  function dedupeFloatingConsultation() {
    const isMobile = window.matchMedia(MOBILE_QUERY).matches;
    if (!isMobile) return;

    const items = Array.from(document.querySelectorAll("a, button"))
      .filter((el) => textOf(el) === "consultation")
      .filter((el) => {
        const style = window.getComputedStyle(el);
        return style.position === "fixed" || style.position === "sticky";
      });

    if (items.length <= 1) return;

    items.slice(1).forEach((el) => {
      el.dataset.sofiatiHiddenDuplicateUi = "true";
      el.setAttribute("aria-hidden", "true");
    });
  }

  function removeOpenDrawerLeak() {
    const mobileMount = document.querySelector('[data-partial-mount="mobile-menu"]');
    if (!mobileMount) return;

    if (!document.body.classList.contains("sofiati-menu-open")) {
      mobileMount.removeAttribute("data-open");
      mobileMount.setAttribute("aria-hidden", "true");
    }
  }

  function runRepairs() {
    dedupeHeaderNavs();
    setupMobileMenu();
    repairHeroContrast();
    dedupeFloatingConsultation();
    removeOpenDrawerLeak();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", runRepairs);
  } else {
    runRepairs();
  }

  /* Partial loaders often inject after DOMContentLoaded. Re-run a few times safely. */
  [250, 750, 1500, 3000].forEach((delay) => {
    window.setTimeout(runRepairs, delay);
  });
})();
