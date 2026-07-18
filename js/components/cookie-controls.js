import { qs, qsa } from '../core/dom.js';

export function initCookies() {
  const banner = qs('[data-cookie-banner]');
  if (!banner || banner.dataset.sfCookieReady === 'true') return;
  banner.dataset.sfCookieReady = 'true';
  const key = 'sofiati_cookie_preferences_v3';
  const legacyKeys = ['sofiati_cookie_preferences_v2', 'sofiati_cookie_choice_v2'];
  const prefs = qs('[data-cookie-preferences]', banner);
  const saveButton = qs('[data-cookie-save]', banner);
  const resetButton = qs('[data-cookie-reset]', banner);
  const customizeButton = qs('[data-cookie-customize]', banner);
  const pageSettings = qs('[data-cookie-page-settings]');
  const pageStatus = qs('[data-cookie-page-status]', pageSettings || document);
  const defaultPreferences = {
    essential: true,
    preferences: false,
    analytics: false,
    externalMedia: false
  };
  let lastTrigger = null;

  const normalizePreferences = (value = {}) => ({
    essential: true,
    preferences: !!(value.preferences ?? value.functional),
    analytics: !!(value.analytics ?? value.performance),
    externalMedia: !!(value.externalMedia ?? value.external_media)
  });

  const readPreferences = () => {
    try {
      const raw = localStorage.getItem(key) || legacyKeys.map((legacyKey) => localStorage.getItem(legacyKey)).find(Boolean);
      if (raw) return normalizePreferences(JSON.parse(raw));
    } catch (_) {}
    return { ...defaultPreferences };
  };

  const syncPreferenceControls = (value = readPreferences()) => {
    const preferences = qs('input[name="preferences"]', banner);
    const analytics = qs('input[name="analytics"]', banner);
    const externalMedia = qs('input[name="external_media"]', banner);
    if (preferences) preferences.checked = !!value.preferences;
    if (analytics) analytics.checked = !!value.analytics;
    if (externalMedia) externalMedia.checked = !!value.externalMedia;
    if (pageSettings) {
      const pagePreferences = qs('input[name="preferences"]', pageSettings);
      const pageAnalytics = qs('input[name="analytics"]', pageSettings);
      const pageExternalMedia = qs('input[name="external_media"]', pageSettings);
      if (pagePreferences) pagePreferences.checked = !!value.preferences;
      if (pageAnalytics) pageAnalytics.checked = !!value.analytics;
      if (pageExternalMedia) pageExternalMedia.checked = !!value.externalMedia;
    }
  };

  const persist = (value, source = 'cookie_controls') => {
    const normalized = normalizePreferences(value);
    try {
      localStorage.setItem(key, JSON.stringify({ ...normalized, savedAt: new Date().toISOString() }));
      legacyKeys.forEach((legacyKey) => localStorage.removeItem(legacyKey));
    } catch (_) {}
    banner.hidden = true;
    banner.classList.remove('is-customizing');
    syncPreferenceControls(normalized);
    document.dispatchEvent(new CustomEvent('sofiati:consentchange', {
      detail: { ...normalized, source }
    }));
    if (lastTrigger && typeof lastTrigger.focus === 'function') lastTrigger.focus({ preventScroll: true });
    lastTrigger = null;
    return normalized;
  };

  const openPreferences = (trigger = null) => {
    lastTrigger = trigger || document.activeElement;
    banner.hidden = false;
    banner.classList.add('is-customizing');
    if (prefs) prefs.hidden = false;
    if (saveButton) saveButton.hidden = false;
    if (resetButton) resetButton.hidden = false;
    if (customizeButton) customizeButton.hidden = true;
    syncPreferenceControls();
    window.requestAnimationFrame(() => qs('input:not([disabled])', prefs || banner)?.focus({ preventScroll: true }));
  };

  const resetPreferences = (trigger = null) => {
    try {
      localStorage.removeItem(key);
      legacyKeys.forEach((legacyKey) => localStorage.removeItem(legacyKey));
    } catch (_) {}
    syncPreferenceControls(defaultPreferences);
    document.dispatchEvent(new CustomEvent('sofiati:consentchange', {
      detail: { ...defaultPreferences, source: 'reset_preferences' }
    }));
    openPreferences(trigger);
  };

  let hasChoice = false;
  try { hasChoice = !!localStorage.getItem(key) || legacyKeys.some((legacyKey) => !!localStorage.getItem(legacyKey)); } catch (_) {}
  if (!hasChoice) banner.hidden = false;

  qs('[data-cookie-accept]', banner)?.addEventListener('click', () => persist(
    { essential: true, preferences: true, analytics: true, externalMedia: true },
    'banner_accept_all'
  ));
  qsa('[data-cookie-reject], [data-cookie-decline]', banner).forEach((button) => button.addEventListener('click', () => persist(
    defaultPreferences,
    'banner_reject_optional'
  )));
  customizeButton?.addEventListener('click', () => openPreferences(customizeButton));
  saveButton?.addEventListener('click', () => persist({
    essential: true,
    preferences: !!qs('input[name="preferences"]', banner)?.checked,
    analytics: !!qs('input[name="analytics"]', banner)?.checked,
    externalMedia: !!qs('input[name="external_media"]', banner)?.checked
  }, 'banner_save'));

  if (pageSettings && pageSettings.dataset.sfCookiePageReady !== 'true') {
    pageSettings.dataset.sfCookiePageReady = 'true';
    const announce = () => {
      if (!pageStatus) return;
      pageStatus.textContent = pageStatus.dataset.savedMessage || '';
    };
    qs('[data-cookie-page-save]', pageSettings)?.addEventListener('click', () => {
      persist({
        essential: true,
        preferences: !!qs('input[name="preferences"]', pageSettings)?.checked,
        analytics: !!qs('input[name="analytics"]', pageSettings)?.checked,
        externalMedia: !!qs('input[name="external_media"]', pageSettings)?.checked
      }, 'settings_page_save');
      announce();
    });
    qs('[data-cookie-page-reject]', pageSettings)?.addEventListener('click', () => {
      persist(defaultPreferences, 'settings_page_reject_optional');
      announce();
    });
    qs('[data-cookie-page-accept]', pageSettings)?.addEventListener('click', () => {
      persist(
        { essential: true, preferences: true, analytics: true, externalMedia: true },
        'settings_page_accept_all'
      );
      announce();
    });
    syncPreferenceControls();
  }

  if (!document.documentElement.dataset.sfCookieControlsReady) {
    document.documentElement.dataset.sfCookieControlsReady = 'true';
    document.addEventListener('click', (event) => {
      const manage = event.target.closest?.('[data-cookie-manage]');
      if (manage) {
        event.preventDefault();
        openPreferences(manage);
        return;
      }
      const reset = event.target.closest?.('[data-cookie-reset]');
      if (reset) {
        event.preventDefault();
        resetPreferences(reset);
      }
    });
  }

  window.SofiatiConsent = Object.freeze({
    get: readPreferences,
    set: persist,
    open: openPreferences,
    reset: resetPreferences
  });
}
