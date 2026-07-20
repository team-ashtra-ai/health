/*
 * Consent Mode v2 bridge and consent-gated GTM loader.
 *
 * This module reuses the site's existing cookie controls and storage record.
 * In basic mode GTM is never requested before analytics permission. Advertising
 * consent remains denied because this site does not install advertising tags.
 * There is intentionally no unconditional GTM <noscript> iframe: it could not
 * respect the JavaScript-managed consent choice.
 */
(function initialiseConsentManager(window, document) {
  "use strict";

  const config = window.FRANCIELE_ANALYTICS_CONFIG;
  if (!config || window.SofiatiConsentMode) return;

  window.dataLayer = window.dataLayer || [];
  const dataLayer = window.dataLayer;
  const defaultPreferences = Object.freeze({
    essential: true,
    preferences: false,
    analytics: false,
    externalMedia: false
  });
  let currentPreferences = { ...defaultPreferences };
  let gtmRequested = false;
  let gtmScheduled = false;
  let googlePageViewSent = false;

  function debug(message, detail) {
    if (!config.debug || !window.console) return;
    console.info(`[Franciele analytics] ${message}`, detail || "");
  }

  function googleConsentCommand() {
    dataLayer.push(arguments);
  }

  function googleTagCommand() {
    if (typeof window.gtag === "function") {
      window.gtag(...arguments);
      return;
    }
    dataLayer.push(arguments);
  }

  function normalize(value) {
    const candidate = value && typeof value === "object" ? value : {};
    return {
      essential: true,
      preferences: Boolean(candidate.preferences ?? candidate.functional),
      analytics: Boolean(candidate.analytics ?? candidate.performance),
      externalMedia: Boolean(candidate.externalMedia ?? candidate.external_media)
    };
  }

  function readStoredPreferences() {
    try {
      const raw = window.localStorage.getItem(config.consentStorageKey);
      return raw ? normalize(JSON.parse(raw)) : { ...defaultPreferences };
    } catch (_) {
      return { ...defaultPreferences };
    }
  }

  function googleState(preferences) {
    return {
      analytics_storage: preferences.analytics ? "granted" : "denied",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied",
      functionality_storage: preferences.preferences ? "granted" : "denied",
      personalization_storage: preferences.preferences ? "granted" : "denied",
      security_storage: "granted"
    };
  }

  function validContainerId() {
    return /^GTM-[A-Z0-9]+$/i.test(config.gtmContainerId)
      && !/REPLACE/i.test(config.gtmContainerId);
  }

  function loadGtm() {
    if (gtmRequested || !currentPreferences.analytics) return false;
    if (!validContainerId()) {
      debug("GTM remains inactive until GTM-REPLACE_ME is replaced.");
      document.documentElement.dataset.analyticsGtm = "placeholder";
      return false;
    }

    if (
      document.querySelector("script[data-franciele-gtm]") ||
      document.querySelector(`script[src*="googletagmanager.com/gtm.js?id=${encodeURIComponent(config.gtmContainerId)}"]`)
    ) {
      gtmRequested = true;
      return false;
    }

    gtmRequested = true;
    dataLayer.push({ "gtm.start": Date.now(), event: "gtm.js" });
    const script = document.createElement("script");
    script.async = true;
    script.dataset.francieleGtm = "consent-granted";
    script.src = `https://www.googletagmanager.com/gtm.js?id=${encodeURIComponent(config.gtmContainerId)}`;
    script.referrerPolicy = "strict-origin-when-cross-origin";
    document.head.append(script);
    document.documentElement.dataset.analyticsGtm = "requested";
    debug("GTM requested after analytics consent.");
    return true;
  }

  function scheduleGtm() {
    if (gtmScheduled || gtmRequested || !currentPreferences.analytics) return;
    gtmScheduled = true;
    window.setTimeout(() => {
      gtmScheduled = false;
      loadGtm();
    }, 0);
  }

  function recordGooglePageView() {
    if (googlePageViewSent || !currentPreferences.analytics) return;
    googlePageViewSent = true;
    const pagePath = `${window.location.pathname}${window.location.hash || ""}`;
    const payload = {
      page_title: document.title,
      page_location: window.location.href.split("#")[0],
      page_path: pagePath
    };
    googleTagCommand("config", config.ga4MeasurementId, payload);
    if (config.googleTagId) {
      googleTagCommand("config", config.googleTagId, { ...payload, send_page_view: false });
    }
    debug("Google tag page view recorded after analytics consent.", payload);
  }

  function apply(preferences, source, initial) {
    const previous = currentPreferences;
    currentPreferences = normalize(preferences);
    // A denied default is always queued first. Stored or newly selected
    // preferences therefore use an update command rather than a second default.
    googleConsentCommand("consent", "update", googleState(currentPreferences));

    document.documentElement.dataset.analyticsConsent = currentPreferences.analytics
      ? "granted"
      : "denied";

    if (!initial) {
      document.dispatchEvent(new CustomEvent("sofiati:analytics-consent", {
        detail: {
          analytics: currentPreferences.analytics,
          preferences: currentPreferences.preferences,
          source: String(source || "cookie_controls").slice(0, 40),
          previousAnalytics: previous.analytics,
          previousPreferences: previous.preferences
        }
      }));
    }

    if (currentPreferences.analytics) scheduleGtm();
    if (currentPreferences.analytics) recordGooglePageView();
    debug("Consent state applied.", currentPreferences);
    return { ...currentPreferences };
  }

  // Consent Mode v2 defaults are established before any Google container can
  // load. A stored grant is then applied, still before the deferred GTM request.
  googleConsentCommand("consent", "default", {
    analytics_storage: "denied",
    ad_storage: "denied",
    ad_user_data: "denied",
    ad_personalization: "denied",
    functionality_storage: "denied",
    personalization_storage: "denied",
    security_storage: "granted",
    wait_for_update: 500
  });
  currentPreferences = readStoredPreferences();
  apply(currentPreferences, "stored_choice", true);

  document.addEventListener("sofiati:consentchange", (event) => {
    const detail = event.detail || {};
    apply(detail, detail.source || "cookie_controls", false);
  });

  window.SofiatiConsentMode = Object.freeze({
    get: () => ({ ...currentPreferences }),
    hasAnalyticsConsent: () => currentPreferences.analytics,
    apply,
    loadGtm
  });
})(window, document);
