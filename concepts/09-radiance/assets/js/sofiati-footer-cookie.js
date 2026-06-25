/* SOFIATI FOOTER COOKIE BAR START */
(() => {
  "use strict";

  const CONFIG = {"code": "09", "slug": "radiance", "bg": "#FFFDF8", "fg": "#252321", "muted": "rgba(37,35,33,.62)", "accent": "#C9A56A", "border": "1px solid rgba(201,165,106,.20)", "width": "min(1080px,calc(100% - 34px))", "padding": "10px 0", "fontSize": ".77rem", "align": "left", "layout": "fine-print", "separator": "bottom-line", "marker": "ray", "buttonStyle": "text", "radius": "4px", "autoDelayMs": 10080};
  const STORAGE_KEY = "sofiatiFooterCookie:v2:" + CONFIG.code;

  if (localStorage.getItem(STORAGE_KEY)) return;

  function saveConsent(mode) {
    const payload = {
      essential: true,
      analytics: false,
      experience: mode === "all",
      mode,
      updatedAt: new Date().toISOString()
    };

    localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
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

      .sf-footer-cookie-bar[data-separator="gold-top"],
      .sf-footer-cookie-bar[data-separator="thin-top"],
      .sf-footer-cookie-bar[data-separator="soft-top"],
      .sf-footer-cookie-bar[data-separator="top-only"] {
        border-top: var(--bar-border);
      }

      .sf-footer-cookie-bar[data-separator="bottom-line"] {
        border-bottom: var(--bar-border);
      }

      .sf-footer-cookie-bar[data-separator="champagne"] {
        border-top: 1px solid color-mix(in srgb, var(--bar-accent) 38%, transparent);
      }

      .sf-footer-cookie-bar[data-separator="dashed"] {
        border-top: 1px dashed color-mix(in srgb, var(--bar-accent) 42%, transparent);
      }

      .sf-footer-cookie-bar[data-separator="motion"] {
        border-top: 1px solid color-mix(in srgb, var(--bar-accent) 18%, transparent);
        background-image: linear-gradient(90deg, color-mix(in srgb, var(--bar-accent) 7%, transparent), transparent 44%);
      }

      .sf-footer-cookie-bar[data-separator="scan"] {
        background-image: repeating-linear-gradient(180deg, color-mix(in srgb, var(--bar-accent) 8%, transparent) 0 1px, transparent 1px 8px);
      }

      .sf-footer-cookie-inner {
        width: var(--bar-width);
        margin-inline: auto;
        min-height: 36px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px 14px;
        padding: var(--bar-padding);
        text-align: ${CONFIG.align};
        font-size: var(--bar-font-size);
        line-height: 1.35;
      }

      .sf-footer-cookie-bar[data-layout="micro"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="minimal"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="single-line"] .sf-footer-cookie-inner {
        min-height: 28px;
        justify-content: center;
      }

      .sf-footer-cookie-bar[data-layout="center"],
      .sf-footer-cookie-bar[data-layout="centered"],
      .sf-footer-cookie-bar[data-layout="balanced"] {
        text-align: center;
      }

      .sf-footer-cookie-bar[data-layout="center"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="centered"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="balanced"] .sf-footer-cookie-inner {
        justify-content: center;
      }

      .sf-footer-cookie-bar[data-layout="ledger"] .sf-footer-cookie-inner,
      .sf-footer-cookie-bar[data-layout="fine-print"] .sf-footer-cookie-inner {
        min-height: 32px;
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

      .sf-footer-cookie-bar[data-separator="center-line"] .sf-footer-cookie-inner::before,
      .sf-footer-cookie-bar[data-separator="halo"] .sf-footer-cookie-inner::before,
      .sf-footer-cookie-bar[data-separator="glow"] .sf-footer-cookie-inner::before {
        content: "";
        width: 34px;
        height: 1px;
        background: var(--bar-accent);
        opacity: .72;
        flex: 0 0 auto;
      }

      .sf-footer-cookie-bar[data-separator="diagonal"] .sf-footer-cookie-inner {
        background-image: linear-gradient(112deg, transparent 0 48%, color-mix(in srgb, var(--bar-accent) 18%, transparent) 48% 49%, transparent 49%);
      }

      .sf-footer-cookie-bar[data-separator="step"] .sf-footer-cookie-inner {
        border-top: 1px solid color-mix(in srgb, var(--bar-accent) 26%, transparent);
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
      .sf-footer-cookie-bar[data-marker="dash"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="signal"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="book"] .sf-footer-cookie-mark {
        width: 16px;
        height: 1px;
        border-radius: 0;
      }

      .sf-footer-cookie-bar[data-marker="diamond"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="check"] .sf-footer-cookie-mark {
        width: 7px;
        height: 7px;
        border-radius: 0;
        transform: rotate(45deg);
      }

      .sf-footer-cookie-bar[data-marker="leaf"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="sprig"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="curve"] .sf-footer-cookie-mark {
        width: 12px;
        height: 7px;
        border-radius: 100% 0 100% 0;
        transform: rotate(-24deg);
      }

      .sf-footer-cookie-bar[data-marker="bracket"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="signature"] .sf-footer-cookie-mark,
      .sf-footer-cookie-bar[data-marker="crest"] .sf-footer-cookie-mark {
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
        min-height: 26px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 3px 8px;
        border: 1px solid color-mix(in srgb, var(--bar-accent) 32%, transparent);
        border-radius: var(--bar-radius);
        background: transparent;
        color: var(--bar-fg);
        font: inherit;
        font-size: .75rem;
        font-weight: 800;
        text-decoration: none;
        cursor: pointer;
        white-space: nowrap;
      }

      .sf-footer-cookie-bar[data-button-style="solid-first"] .sf-footer-cookie-actions button:first-child,
      .sf-footer-cookie-bar[data-button-style="soft"] .sf-footer-cookie-actions button:first-child,
      .sf-footer-cookie-bar[data-button-style="pill-outline"] .sf-footer-cookie-actions button:first-child {
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
          padding-block: 9px;
        }

        .sf-footer-cookie-actions {
          justify-content: start;
          flex-wrap: wrap;
        }

        .sf-footer-cookie-actions button,
        .sf-footer-cookie-actions a {
          min-height: 28px;
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
          <strong>Cookies:</strong> essential storage keeps this site working. Optional preferences are only used if enabled.
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

  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", createBar, { once: true });
  } else {
    createBar();
  }
})();
/* SOFIATI FOOTER COOKIE BAR END */
