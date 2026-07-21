import { qs, qsa } from '../core/dom.js';
import { currentPage } from '../core/page.js';

const FORM_ENDPOINTS = Object.freeze({
  consultation: 'https://formspree.io/f/xvzeqgba',
  contact: 'https://formspree.io/f/xvzjdyql',
  quick_contact: 'https://formspree.io/f/xvzjdyql',
  quick_question: 'https://formspree.io/f/xvzjdyql',
  newsletter: 'https://formspree.io/f/xnjeznbg',
  newsletter_signup: 'https://formspree.io/f/xnjeznbg'
});

const CAMPAIGN_KEYS = Object.freeze([
  'utm_source',
  'utm_medium',
  'utm_campaign',
  'utm_id',
  'utm_content',
  'utm_term',
  'gclid',
  'dclid',
  'gbraid',
  'wbraid',
  'fbclid',
  'msclkid',
  'ttclid',
  'twclid',
  'li_fat_id'
]);

function isPortuguese() {
  const language = (document.documentElement.lang || '').toLowerCase();
  return language === 'pt' || language === 'pt-br' || language.startsWith('pt-');
}

function thankYouPath() {
  return isPortuguese() ? 'obrigada.html' : 'en/thank-you.html';
}

function canonicalUrl() {
  return document.querySelector('link[rel~="canonical"]')?.href || window.location.href;
}

function stableStorageValue(storage, key, factory) {
  try {
    const existing = storage.getItem(key);
    if (existing) return existing;
    const next = factory();
    storage.setItem(key, next);
    return next;
  } catch {
    return factory();
  }
}

function randomId(prefix) {
  const values = new Uint32Array(3);
  window.crypto?.getRandomValues?.(values);
  const source = values.some(Boolean) ? Array.from(values).join('-') : `${Date.now()}-${Math.random()}`;
  return `${prefix}-${source.replace(/[^a-z0-9-]+/gi, '').toLowerCase()}`;
}

function initialLandingPage() {
  return stableStorageValue(window.sessionStorage, 'sofiati_landing_page', () => window.location.href);
}

function sessionIdentifier() {
  return stableStorageValue(window.sessionStorage, 'sofiati_session_id', () => randomId('session'));
}

function returningVisitor() {
  try {
    const key = 'sofiati_returning_visitor';
    const returning = window.localStorage.getItem(key) === 'true';
    window.localStorage.setItem(key, 'true');
    return returning ? 'yes' : 'no';
  } catch {
    return 'unknown';
  }
}

function parseBrowser(userAgent) {
  const rules = [
    ['Edge', /Edg\/([\d.]+)/],
    ['Chrome', /Chrome\/([\d.]+)/],
    ['Safari', /Version\/([\d.]+).*Safari/],
    ['Firefox', /Firefox\/([\d.]+)/]
  ];
  const found = rules.find(([, pattern]) => pattern.test(userAgent));
  return found ? { name: found[0], version: userAgent.match(found[1])?.[1] || '' } : { name: 'Unknown', version: '' };
}

function parseOperatingSystem(userAgent) {
  const rules = [
    ['Windows', /Windows NT ([\d.]+)/],
    ['iOS', /(?:iPhone|iPad).*OS ([\d_]+)/],
    ['Android', /Android ([\d.]+)/],
    ['macOS', /Mac OS X ([\d_]+)/],
    ['Linux', /Linux/]
  ];
  const found = rules.find(([, pattern]) => pattern.test(userAgent));
  return found ? { name: found[0], version: (userAgent.match(found[1])?.[1] || '').replaceAll('_', '.') } : { name: 'Unknown', version: '' };
}

function deviceType() {
  const width = window.innerWidth || document.documentElement.clientWidth || 0;
  const touch = navigator.maxTouchPoints > 0;
  if (touch && width < 768) return 'mobile';
  if (touch && width < 1180) return 'tablet';
  return 'desktop';
}

function upsertHidden(form, name, value) {
  let input = form.querySelector(`input[type="hidden"][name="${CSS.escape(name)}"]`);
  if (!input) {
    input = document.createElement('input');
    input.type = 'hidden';
    input.name = name;
    input.dataset.analyticsIgnore = '';
    input.dataset.analyticsSensitive = '';
    form.prepend(input);
  }
  input.value = value == null ? '' : String(value);
  return input;
}

function formName(form) {
  return form.dataset.formName || form.dataset.analyticsForm || form.id || 'website_form';
}

function formType(form) {
  return form.dataset.formType || form.dataset.leadType || formName(form);
}

function endpointFor(form) {
  const key = formType(form);
  const name = formName(form);
  const endpoint = FORM_ENDPOINTS[key] || FORM_ENDPOINTS[name] || form.getAttribute('action') || '';
  return /^https:\/\/formspree\.io\/f\/[a-z0-9]+$/i.test(endpoint) ? endpoint : '';
}

function populateMetadata(form) {
  const now = new Date();
  const params = new URLSearchParams(window.location.search);
  const browser = parseBrowser(navigator.userAgent || '');
  const os = parseOperatingSystem(navigator.userAgent || '');
  const offsetMinutes = -now.getTimezoneOffset();
  const offsetSign = offsetMinutes >= 0 ? '+' : '-';
  const offsetHours = String(Math.floor(Math.abs(offsetMinutes) / 60)).padStart(2, '0');
  const offsetRemainder = String(Math.abs(offsetMinutes) % 60).padStart(2, '0');
  const metadata = {
    website_domain: window.location.hostname,
    current_page_url: window.location.href,
    current_page_filename: window.location.pathname.split('/').pop() || 'index.html',
    current_page_title: document.title,
    current_section: form.closest('section')?.id || form.closest('section')?.dataset.sectionName || '',
    language_selected: document.documentElement.lang || '',
    website_language: document.documentElement.dataset.defaultLang || document.documentElement.lang || '',
    browser_language: navigator.language || '',
    browser_locale: navigator.languages?.join(', ') || navigator.language || '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
    utc_offset: `${offsetSign}${offsetHours}:${offsetRemainder}`,
    referrer: document.referrer,
    original_landing_page: initialLandingPage(),
    current_page_path: window.location.pathname,
    canonical_url: canonicalUrl(),
    marketing_source: params.get('utm_source') || '',
    medium: params.get('utm_medium') || '',
    campaign: params.get('utm_campaign') || '',
    content: params.get('utm_content') || '',
    term: params.get('utm_term') || '',
    screen_resolution: `${window.screen?.width || ''}x${window.screen?.height || ''}`,
    viewport_size: `${document.documentElement.clientWidth || ''}x${document.documentElement.clientHeight || ''}`,
    window_size: `${window.innerWidth || ''}x${window.innerHeight || ''}`,
    device_pixel_ratio: window.devicePixelRatio || '',
    operating_system: os.name,
    operating_system_version: os.version,
    browser: browser.name,
    browser_version: browser.version,
    rendering_engine: browser.name === 'Firefox' ? 'Gecko' : browser.name === 'Safari' ? 'WebKit' : browser.name === 'Unknown' ? '' : 'Blink',
    device_type: deviceType(),
    touch_support: navigator.maxTouchPoints > 0 ? 'yes' : 'no',
    color_scheme_preference: window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light',
    reduced_motion_preference: window.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'reduce' : 'no-preference',
    cookies_enabled: navigator.cookieEnabled ? 'yes' : 'no',
    javascript_enabled: 'yes',
    date: now.toLocaleDateString(),
    time: now.toLocaleTimeString(),
    timestamp: String(now.getTime()),
    iso_timestamp: now.toISOString(),
    user_local_time: now.toString(),
    form_name: formName(form),
    form_type: formType(form),
    site_version: window.SofiatiSite?.version || '',
    page_template: document.body?.dataset.page || currentPage(),
    current_navigation_language: isPortuguese() ? 'pt-BR' : 'en',
    session_identifier: sessionIdentifier(),
    submission_identifier: randomId('submission'),
    returning_visitor: returningVisitor()
  };
  CAMPAIGN_KEYS.forEach((key) => {
    metadata[key] = params.get(key) || '';
  });
  Object.entries(metadata).forEach(([key, value]) => upsertHidden(form, key, value));
  const redirect = new URL(thankYouPath(), window.location.origin);
  upsertHidden(form, '_next', redirect.href);
  return redirect.href;
}

export function initForms() {
  qsa('form.sf-form, form[data-enhanced-form], form[data-consultation-form]').forEach((form, formIndex) => {
    if (form.dataset.sfFormReady === 'true') return;
    form.dataset.sfFormReady = 'true';
    form.setAttribute('data-enhanced-form', '');
    form.noValidate = true;
    form.method = 'post';

    const page = currentPage();
    const isConsultation = page === 'consultation' || /consultation|consulta/i.test(qs('button[type="submit"]', form)?.textContent || '');

    const formId = form.id || `sf-form-${formIndex + 1}`;
    if (!form.id) form.id = formId;
    const stateNodes = qsa('[data-form-state]', form);
    const renderedStateCopy = Object.fromEntries(
      stateNodes.map((node) => [node.dataset.formState, node.textContent.trim()])
    );
    const copy = {
      required: form.dataset.messageRequired || '',
      email: form.dataset.messageEmail || '',
      review: form.dataset.messageReview || '',
      loading: renderedStateCopy.loading || '',
      success: renderedStateCopy.success || '',
      error: renderedStateCopy.error || ''
    };
    let status = qs('[data-form-status]', form);
    if (!status && !stateNodes.length) {
      status = document.createElement('p');
      status.dataset.formStatus = '';
      status.className = 'sf-form-status';
      status.id = `${formId}-status`;
      status.hidden = true;
      status.tabIndex = -1;
      form.append(status);
    }
    if (status?.id) {
      form.setAttribute('aria-describedby', [form.getAttribute('aria-describedby'), status.id].filter(Boolean).join(' '));
    }

    const clearFieldError = (field) => {
      const errorId = field.dataset.sfErrorId;
      const error = errorId ? document.getElementById(errorId) : null;
      if (error?.dataset.errorFor) {
        error.textContent = '';
        error.hidden = true;
      } else {
        error?.remove();
        const describedBy = (field.getAttribute('aria-describedby') || '').split(/\s+/).filter((id) => id && id !== errorId);
        if (describedBy.length) field.setAttribute('aria-describedby', describedBy.join(' '));
        else field.removeAttribute('aria-describedby');
      }
      delete field.dataset.sfErrorId;
      field.classList.remove('is-invalid');
      field.removeAttribute('aria-invalid');
    };

    const showFieldError = (field, message) => {
      clearFieldError(field);
      const safeName = String(field.name || field.id || 'field').replace(/[^a-z0-9_-]+/gi, '-');
      let error = qsa('[data-error-for]', form).find((node) => node.dataset.errorFor === field.id);
      if (!error) {
        error = document.createElement('p');
        error.id = `${formId}-${safeName}-runtime-error`;
        error.className = 'form-error';
        field.insertAdjacentElement('afterend', error);
      }
      error.textContent = message;
      error.hidden = false;
      field.dataset.sfErrorId = error.id;
      field.classList.add('is-invalid');
      field.setAttribute('aria-invalid', 'true');
      const describedBy = new Set((field.getAttribute('aria-describedby') || '').split(/\s+/).filter(Boolean));
      describedBy.add(error.id);
      field.setAttribute('aria-describedby', Array.from(describedBy).join(' '));
    };

    const fields = qsa('input, select, textarea', form).filter((field) => !field.classList.contains('sf-honeypot') && field.type !== 'hidden');
    fields.forEach((field) => {
      const clear = () => clearFieldError(field);
      field.addEventListener('input', clear);
      field.addEventListener('change', clear);
    });

    const validate = () => {
      let firstInvalid = null;
      let errorCount = 0;
      fields.forEach(clearFieldError);
      fields.forEach((field) => {
        if (field.disabled || field.checkValidity()) return;
        errorCount += 1;
        const message = field.validity.typeMismatch ? copy.email : copy.required;
        showFieldError(field, message);
        if (!firstInvalid) firstInvalid = field;
      });
      return { firstInvalid, errorCount };
    };

    // Analytics receives lifecycle states, never FormData or field values.
    // A successful event is emitted only after Formspree confirms the request.
    const emitLifecycle = (name, detail = {}) => {
      document.dispatchEvent(new CustomEvent(`sofiati:form-${name}`, {
        detail: { form, ...detail }
      }));
    };

    const setState = (nextState, message, role = 'status') => {
      form.dataset.formState = nextState;
      form.toggleAttribute('aria-busy', nextState === 'loading');
      if (stateNodes.length) {
        let active = null;
        stateNodes.forEach((node) => {
          const selected = node.dataset.formState === nextState;
          node.hidden = !selected;
          if (selected) active = node;
        });
        if (active) {
          active.setAttribute('role', role);
          active.setAttribute('aria-live', role === 'alert' ? 'assertive' : 'polite');
          active.tabIndex = -1;
          if (!active.textContent.trim() && message) active.textContent = message;
        }
        return active;
      }
      if (status) {
        status.hidden = !message;
        status.setAttribute('role', role);
        status.setAttribute('aria-live', role === 'alert' ? 'assertive' : 'polite');
        status.textContent = message || '';
      }
      return status;
    };

    const setSubmitting = (submitting) => {
      qsa('button[type="submit"], input[type="submit"]', form).forEach((button) => {
        if (!button.dataset.sfOriginalLabel) button.dataset.sfOriginalLabel = button.value || button.textContent || '';
        button.disabled = submitting;
        if (button.tagName === 'INPUT') button.value = submitting ? copy.loading : button.dataset.sfOriginalLabel;
        else button.textContent = submitting ? copy.loading : button.dataset.sfOriginalLabel;
      });
    };

    const configureEndpoint = () => {
      const endpoint = endpointFor(form);
      if (/^https:\/\/formspree\.io\/f\/[a-z0-9]+$/i.test(endpoint)) {
        form.action = endpoint;
        return endpoint;
      }
      return '';
    };
    configureEndpoint();

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (form.dataset.formState === 'loading') return;
      const { firstInvalid, errorCount } = validate();
      if (firstInvalid) {
        setState('error', copy.review, 'alert');
        emitLifecycle('error', {
          errorType: 'client_validation',
          errorCount
        });
        firstInvalid.focus();
        return;
      }

      const honeypot = qs('input.sf-honeypot, input[name="website"]', form);
      if (honeypot && String(honeypot.value || '').trim()) {
        form.reset();
        setState('success', copy.success)?.focus({ preventScroll: true });
        return;
      }

      const endpoint = configureEndpoint();
      if (!endpoint) {
        setState('error', copy.error, 'alert')?.focus({ preventScroll: true });
        emitLifecycle('error', {
          errorType: 'endpoint_unavailable',
          errorCount: 1
        });
        return;
      }

      emitLifecycle('submit');
      setSubmitting(true);
      setState('loading', copy.loading);
      const redirectUrl = populateMetadata(form);
      const payload = new FormData(form);
      if (!payload.get('_subject')) {
        payload.set('_subject', isConsultation ? 'Sofiati consultation request' : 'Sofiati website contact');
      }
      try {
        const response = await fetch(endpoint, {
          method: 'POST',
          body: payload,
          headers: { Accept: 'application/json' }
        });
        if (!response.ok) throw new Error(`Form submission failed (${response.status})`);
        form.reset();
        fields.forEach(clearFieldError);
        setState('success', copy.success)?.focus({ preventScroll: true });
        emitLifecycle('success');
        window.location.assign(redirectUrl);
      } catch (error) {
        setState('error', copy.error, 'alert')?.focus({ preventScroll: true });
        emitLifecycle('error', {
          errorType: 'server_submission',
          errorCount: 1
        });
      } finally {
        setSubmitting(false);
      }
    });
  });
}
