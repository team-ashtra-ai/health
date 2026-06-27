/* SOFIATI ROOT COOKIE BAR START */
(() => {
  "use strict";

  const conceptCode = () => {
    const concept = document.body?.dataset.concept || "";
    const match = concept.match(/^(\d{2})-/);
    return match ? match[1] : "site";
  };

  const storageKey = () => `sofiatiFooterCookie:v3:${conceptCode()}`;

  const ensureStyle = () => {
    if (document.querySelector("[data-sofiati-root-cookie-style]")) return;
    const style = document.createElement("style");
    style.dataset.sofiatiRootCookieStyle = "";
    style.textContent = `
      [data-cookie-banner] {
        position: fixed;
        z-index: 2000;
        left: max(16px, env(safe-area-inset-left));
        right: max(16px, env(safe-area-inset-right));
        bottom: max(16px, env(safe-area-inset-bottom));
        width: min(760px, calc(100% - 32px));
        margin-inline: auto;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 14px;
        padding: 12px 14px;
        border: 1px solid color-mix(in srgb, var(--atlas-accent, #CDAA78) 34%, transparent);
        border-radius: max(6px, min(22px, var(--atlas-radius, 18px)));
        background: color-mix(in srgb, var(--sofiati-ink, #252321) 92%, var(--atlas-primary, #485041));
        color: var(--sofiati-cream, #F8F7F2);
        box-shadow: 0 18px 60px rgba(37, 35, 33, .22);
      }
      [data-cookie-banner][hidden] {
        display: none;
      }
      [data-cookie-banner] p {
        margin: 0;
        display: grid;
        gap: 2px;
        color: inherit;
        font-size: .86rem;
        line-height: 1.35;
      }
      [data-cookie-banner] span {
        color: color-mix(in srgb, currentColor 72%, transparent);
      }
      [data-cookie-banner] button {
        min-width: 52px;
        min-height: 40px;
        border: 0;
        border-radius: 999px;
        padding: 8px 16px;
        background: var(--atlas-accent, #CDAA78);
        color: var(--sofiati-ink, #252321);
        font-weight: 800;
        cursor: pointer;
      }
      @media (max-width: 640px) {
        [data-cookie-banner] {
          align-items: stretch;
          flex-direction: column;
        }
      }
    `;
    document.head.appendChild(style);
  };

  const showBanner = () => {
    if (localStorage.getItem(storageKey())) return;
    const banner = document.querySelector("[data-cookie-banner]");
    if (!banner) return;
    ensureStyle();
    banner.hidden = false;
    const button = banner.querySelector("[data-cookie-accept], button");
    if (button && button.dataset.sofiatiCookieReady !== "true") {
      button.dataset.sofiatiCookieReady = "true";
      button.addEventListener("click", () => {
        localStorage.setItem(
          storageKey(),
          JSON.stringify({
            essential: true,
            analytics: false,
            experience: true,
            updatedAt: new Date().toISOString(),
          }),
        );
        banner.hidden = true;
        window.dispatchEvent(new CustomEvent("sofiati:cookie-consent"));
      });
    }
  };

  const init = () => {
    window.setTimeout(showBanner, 450);
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
  document.addEventListener("sofiati:partials-ready", init);
})();
/* SOFIATI ROOT COOKIE BAR END */
