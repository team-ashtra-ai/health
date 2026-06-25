/* SOFIATI FOOTER COOKIE BAR START */
(() => {
  "use strict";

  const CONFIG = {"code": "25", "slug": "align", "bg": "#FBFAF6", "fg": "#252321", "muted": "rgba(37,35,33,.64)", "accent": "#9A6B35", "border": "1px dashed rgba(154,107,53,.22)", "width": "min(1220px,calc(100% - 40px))", "padding": "11px 0 10px", "fontSize": ".77rem", "align": "center", "layout": "inline", "separator": "soft-top", "marker": "none", "buttonStyle": "square", "radius": "999px", "autoDelayMs": 10400};

  if (localStorage.getItem("sofiatiFooterCookie:" + CONFIG.code)) return;

  function saveConsent(mode) {
    const payload = {
      essential: true,
      analytics: mode === "all",
      experience: mode === "all",
      mode,
      updatedAt: new Date().toISOString()
    };

    localStorage.setItem("sofiatiFooterCookie:" + CONFIG.code, JSON.stringify(payload));
    window.dispatchEvent(new CustomEvent("sofiati:cookie-consent", { detail: payload }));
  }

  function injectStyle() {
    const style = document.createElement("style");
    style.setAttribute("data-sofiati-footer-cookie-style", CONFIG.code);

    style.textContent = `
      .sf-footer-cookie-bar {
        --bar-bg: ${CONFIG.bg};
        --bar-fg: ${CONFIG.fg};
        --bar-muted: ${CONFIG.muted};
        --bar-accent: ${CONFIG.accent};
        --bar-border: ${CONFIG.border};
        --bar-width: ${CONFIG.width};
        --bar-padding: ${CONFIG.padding};
        --bar-font-size: ${CONFIG.fontSize};
        --bar-radius: ${CONFIG.radius};

        position: static;
        display: block;
        width: 100%;
        background: var(--bar-bg);
        color: var(--bar-fg);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      }

      .sf-footer-cookie-bar[data-separator="top-line"] {
        border-top: var(--bar-border);
      }

      .sf-footer-cookie-bar[data-separator="bottom-line"] {
        border-bottom: var(--bar-border);
      }

      .sf-footer-cookie-bar[data-separator="soft-top"] {
        border-top: var(--bar-border);
        box-shadow: inset 0 1px 0 color-mix(in srgb, var(--bar-accent) 10%, transparent);
      }

      .sf-footer-cookie-bar[data-separator="champagne"] {
        border-top: 1px solid color-mix(in srgb, var(--bar-accent) 34%, transparent);
      }

      .sf-footer-cookie-bar[data-separator="dashed"] {
        border-top: 1px dashed color-mix(in srgb, var(--bar-accent) 38%, transparent);
      }

      .sf-footer-cookie-bar[data-separator="motion"] {
        border-top: 1px solid color-mix(in srgb, var(--bar-accent) 18%, transparent);
        background-image: linear-gradient(90deg, color-mix(in srgb, var(--bar-accent) 7%, transparent), transparent 42%);
      }

      .sf-footer-cookie-bar[data-separator="scan"] {
        background-image: repeating-linear-gradient(180deg, color-mix(in srgb, var(--bar-accent) 8%, transparent) 0 1px, transparent 1px 8px);
      }

      .sf-footer-cookie-inner {
        width: var(--bar-width);
        margin-inline: auto;
        min-height: 38px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px 14px;
        padding: var(--bar-padding);
        text-align: ${CONFIG.align};
        font-size: var(--bar-font-size);
        line-height: 1.35;
      }

      .sf-footer-cookie-bar[data-layout="minimal"] .sf-footer-cookie-inner {
        min-height: 30px;
        justify-content: center;
      }

      .sf-footer-cookie-bar[data-layout="centered"] .sf-footer-cookie-inner {
        justify-content: center;
      }

      .sf-footer-cookie-bar[data-layout="wide"] .sf-footer-cookie-inner {
        width: min(1240px, calc(100% - 42px));
      }

      .sf-footer-cookie-bar[data-layout="ledger"] .sf-footer-cookie-inner {
        min-height: 34px;
        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        letter-spacing: -.02em;
      }

      .sf-footer-cookie-bar[data-layout="editorial"] strong {
        letter-spacing: .08em;
        text-transform: uppercase;
      }

      .sf-footer-cookie-bar[data-separator="left-rule"] .sf-footer-cookie-inner {
        border-left: 3px solid var(--bar-accent);
        padding-left: 12px;
      }

      .sf-footer-cookie-bar[data-separator="center-line"] .sf-footer-cookie-inner::before {
        content: "";
        width: 34px;
        height: 1px;
        background: var(--bar-accent);
        opacity: .72;
        flex: 0 0 auto;
      }

      .sf-footer-cookie-mark {
        width: 7px;
        height: 7px;
        flex: 0 0 auto;
        background: var(--bar-accent);
        opacity: .85;
        border-radius: 999px;
      }

      .sf-footer-cookie-bar[data-marker="none"] .sf-footer-cookie-mark {
        display: none;
      }

      .sf-footer-cookie-bar[data-marker="line"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="dash"] .sf-footer-cookie-mark {
        width: 16px;
        height: 1px;
        border-radius: 0;
      }

      .sf-footer-cookie-bar[data-marker="diamond"] .sf-footer-cookie-mark {
        width: 7px;
        height: 7px;
        border-radius: 0;
        transform: rotate(45deg);
      }

      .sf-footer-cookie-bar[data-marker="leaf"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="sprig"] .sf-footer-cookie-mark {
        width: 12px;
        height: 7px;
        border-radius: 100% 0 100% 0;
        transform: rotate(-24deg);
      }

      .sf-footer-cookie-bar[data-marker="bracket"] .sf-footer-cookie-mark {
        width: 8px;
        height: 12px;
        background: transparent;
        border-left: 1px solid var(--bar-accent);
        border-top: 1px solid var(--bar-accent);
        border-bottom: 1px solid var(--bar-accent);
        border-radius: 0;
      }

      .sf-footer-cookie-text {
        margin: 0;
        color: var(--bar-muted);
        flex: 1 1 auto;
      }

      .sf-footer-cookie-text strong {
        color: var(--bar-fg);
        font-weight: 850;
      }

      .sf-footer-cookie-actions {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 6px;
        flex: 0 0 auto;
      }

      .sf-footer-cookie-actions button,
      .sf-footer-cookie-actions a {
        min-height: 28px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 4px 9px;
        border: 1px solid color-mix(in srgb, var(--bar-accent) 32%, transparent);
        border-radius: var(--bar-radius);
        background: transparent;
        color: var(--bar-fg);
        font: inherit;
        font-size: .78rem;
        font-weight: 800;
        text-decoration: none;
        cursor: pointer;
        white-space: nowrap;
      }

      .sf-footer-cookie-actions button:first-child {
        background: var(--bar-accent);
        border-color: var(--bar-accent);
        color: #fff;
      }

      .sf-footer-cookie-bar[data-button-style="text"] .sf-footer-cookie-actions button,
      .sf-footer-cookie-bar[data-button-style="text"] .sf-footer-cookie-actions a {
        border: 0;
        padding-inline: 4px;
        text-decoration: underline;
        text-underline-offset: .25em;
        background: transparent;
        color: var(--bar-muted);
      }

      .sf-footer-cookie-bar[data-button-style="text"] .sf-footer-cookie-actions button:first-child {
        color: var(--bar-fg);
      }

      .sf-footer-cookie-actions button:focus-visible,
      .sf-footer-cookie-actions a:focus-visible {
        outline: 2px solid var(--bar-accent);
        outline-offset: 3px;
      }

      @media (max-width: 720px) {
        .sf-footer-cookie-inner {
          width: min(520px, calc(100% - 26px));
          display: grid;
          justify-items: start;
          justify-content: start;
          text-align: left;
          gap: 8px;
          padding-block: 10px;
        }

        .sf-footer-cookie-bar[data-layout="minimal"] .sf-footer-cookie-inner,
        .sf-footer-cookie-bar[data-layout="centered"] .sf-footer-cookie-inner {
          justify-items: center;
          text-align: center;
        }

        .sf-footer-cookie-actions {
          justify-content: start;
          flex-wrap: wrap;
        }

        .sf-footer-cookie-actions button,
        .sf-footer-cookie-actions a {
          min-height: 30px;
        }
      }
    `;

    document.head.appendChild(style);
  }

  function createBar() {
    injectStyle();

    const bar = document.createElement("section");
    bar.className = "sf-footer-cookie-bar";
    bar.setAttribute("data-cookie-bar", CONFIG.code);
    bar.setAttribute("data-layout", CONFIG.layout);
    bar.setAttribute("data-separator", CONFIG.separator);
    bar.setAttribute("data-marker", CONFIG.marker);
    bar.setAttribute("data-button-style", CONFIG.buttonStyle);
    bar.setAttribute("aria-label", "Cookie notice");

    bar.innerHTML = `
      <div class="sf-footer-cookie-inner">
        <span class="sf-footer-cookie-mark" aria-hidden="true"></span>
        <p class="sf-footer-cookie-text">
          <strong>Cookies:</strong> essential cookies keep this site working. Optional cookies help improve the experience.
        </p>
        <div class="sf-footer-cookie-actions">
          <button type="button" data-cookie-choice="all">Accept</button>
          <button type="button" data-cookie-choice="essential">Essential only</button>
          <a href="cookies.html">Cookies</a>
        </div>
      </div>
    `;

    bar.addEventListener("click", (event) => {
      const choice = event.target.closest("[data-cookie-choice]");
      if (!choice) return;

      const mode = choice.getAttribute("data-cookie-choice") === "all" ? "all" : "essential";
      saveConsent(mode);
      bar.remove();
    });

    const footers = Array.from(document.querySelectorAll("footer"));
    const footer = footers.length ? footers[footers.length - 1] : null;

    if (footer && footer.parentNode) {
      footer.insertAdjacentElement("afterend", bar);
    } else {
      document.body.appendChild(bar);
    }

    window.setTimeout(() => {
      if (!localStorage.getItem("sofiatiFooterCookie:" + CONFIG.code) && document.body.contains(bar)) {
        saveConsent("essential");
        bar.remove();
      }
    }, CONFIG.autoDelayMs);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createBar, { once: true });
  } else {
    createBar();
  }
})();
/* SOFIATI FOOTER COOKIE BAR END */
