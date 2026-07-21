import { qs, qsa } from '../core/dom.js';
import { currentPage } from '../core/page.js';

const FORM_ENDPOINTS = Object.freeze({
  consultation: 'https://formspree.io/f/xzdldkjy',
  contact: 'https://formspree.io/f/xzdldkjy',
  quick_contact: 'https://formspree.io/f/xzdldkjy',
  quick_question: 'https://formspree.io/f/xzdldkjy',
  newsletter: 'https://formspree.io/f/xzdldkjy',
  newsletter_signup: 'https://formspree.io/f/xzdldkjy',
  consent_authorisation: 'https://formspree.io/f/xzdldkjy',
  consent_authorization: 'https://formspree.io/f/xzdldkjy',
  accessibility: 'https://formspree.io/f/xzdldkjy',
  accessibility_feedback: 'https://formspree.io/f/xzdldkjy'
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

const SESSION_STARTED_AT = Date.now();
let interactionCount = 0;
let lastCtaClicked = '';

document.addEventListener('click', (event) => {
  interactionCount += 1;
  const cta = event.target.closest?.('[data-track="cta"], [data-cta-purpose], a.sf-button, button.sf-button');
  if (!cta) return;
  lastCtaClicked = [
    cta.dataset.ctaPurpose,
    cta.dataset.ctaLocation || cta.dataset.linkLocation,
    cta.textContent?.trim()
  ].filter(Boolean).join(' | ').slice(0, 160);
}, { capture: true, passive: true });

document.addEventListener('input', () => {
  interactionCount += 1;
}, { capture: true, passive: true });

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

function firstVisitDate() {
  try {
    return stableStorageValue(window.localStorage, 'sofiati_first_visit', () => new Date().toISOString());
  } catch {
    return '';
  }
}

function anonymousVisitorId() {
  try {
    return stableStorageValue(window.localStorage, 'sofiati_visitor_id', () => randomId('visitor'));
  } catch {
    return randomId('visitor');
  }
}

function pageHistory() {
  try {
    const key = 'sofiati_session_pages';
    const current = `${window.location.pathname}${window.location.search}`;
    const existing = JSON.parse(window.sessionStorage.getItem(key) || '[]').filter(Boolean);
    if (existing[existing.length - 1] !== current) existing.push(current);
    const capped = existing.slice(-12);
    window.sessionStorage.setItem(key, JSON.stringify(capped));
    return capped;
  } catch {
    return [`${window.location.pathname}${window.location.search}`];
  }
}

function fieldValue(form, names) {
  const candidates = Array.isArray(names) ? names : [names];
  for (const name of candidates) {
    const field = form.elements?.[name] || qs(`[name="${CSS.escape(name)}"]`, form);
    if (!field) continue;
    if (field instanceof RadioNodeList) {
      const checked = Array.from(field).find((item) => item.checked);
      if (checked?.value) return checked.value;
      continue;
    }
    if (field.type === 'checkbox') return field.checked ? field.value || 'yes' : '';
    if (field.value) return field.value;
  }
  return '';
}

function selectedText(form, names) {
  const candidates = Array.isArray(names) ? names : [names];
  for (const name of candidates) {
    const field = form.elements?.[name] || qs(`[name="${CSS.escape(name)}"]`, form);
    if (field?.tagName === 'SELECT') return field.selectedOptions?.[0]?.textContent?.trim() || field.value || '';
  }
  return '';
}

function pageCategory() {
  return document.body?.dataset.page || document.body?.className?.match(/sf-family-([a-z-]+)/)?.[1] || currentPage();
}

function consentPreference(name) {
  try {
    const consent = window.SofiatiConsentMode?.get?.();
    if (consent && Object.prototype.hasOwnProperty.call(consent, name)) return consent[name] ? 'granted' : 'denied';
  } catch {
    return 'unknown';
  }
  return 'unknown';
}

function referrerDomain() {
  try {
    return document.referrer ? new URL(document.referrer).hostname : '';
  } catch {
    return '';
  }
}

function searchEngineSource(domain) {
  if (!domain) return '';
  if (/google\./i.test(domain)) return 'Google Search';
  if (/bing\./i.test(domain)) return 'Bing';
  if (/yahoo\./i.test(domain)) return 'Yahoo';
  if (/duckduckgo\./i.test(domain)) return 'DuckDuckGo';
  return '';
}

function socialSource(params, domain) {
  const source = params.get('utm_source') || domain || '';
  if (/instagram/i.test(source)) return 'Instagram';
  if (/facebook|fbclid/i.test(source) || params.get('fbclid')) return 'Facebook';
  if (/linkedin/i.test(source)) return 'LinkedIn';
  if (/tiktok|ttclid/i.test(source) || params.get('ttclid')) return 'TikTok';
  return '';
}

function originalSource(params, domain) {
  if (params.get('utm_source')) return params.get('utm_source');
  const search = searchEngineSource(domain);
  if (search) return search;
  const social = socialSource(params, domain);
  if (social) return social;
  return domain ? 'Referral' : 'Direct visit';
}

function viewedItems(selector, fallbackPageNames = []) {
  const values = qsa(selector)
    .map((node) => node.textContent?.trim())
    .filter(Boolean)
    .slice(0, 12);
  return values.length ? values.join(' | ') : fallbackPageNames.join(' | ');
}

function scrollDepthPercentage() {
  const doc = document.documentElement;
  const maxScroll = Math.max(1, doc.scrollHeight - window.innerHeight);
  return String(Math.min(100, Math.round((window.scrollY / maxScroll) * 100)));
}

function leadTemperature(form, serviceInterest, message) {
  const text = `${serviceInterest} ${message}`.toLowerCase();
  if (/agendar|consulta|consultation|appointment|whatsapp|telefone|phone|laser|acne|melasma|co2|ultraformer/.test(text)) return 'Warm';
  if (formType(form).includes('consultation') || formName(form).includes('contact')) return 'Warm';
  return 'Cold';
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

function setupConsentSpecificTerms(form) {
  if (!form.matches('[data-form-type="consent_authorisation"], [data-form-type="consent_authorization"]')) {
    return;
  }

  const procedureInputs = qsa('input[name="selected_procedures"]', form);
  if (!procedureInputs.length) return;

  const copy = isPortuguese()
    ? {
      selectProcedure: 'Selecione pelo menos um procedimento.',
      acceptTerm: 'Abra e aceite o termo específico do procedimento selecionado antes de enviar.'
    }
    : {
      selectProcedure: 'Select at least one procedure.',
      acceptTerm: 'Open and accept the specific term for the selected procedure before submitting.'
    };

  const matchingTermInput = (procedureInput) => {
    const raw = String(procedureInput.value || '');
    return qs(`input[name="accepted_term_${CSS.escape(raw)}"]`, form);
  };

  const procedureCard = (input) => input.closest('.sf-consent-procedure');

  const syncProcedureGroupValidity = () => {
    const selected = procedureInputs.filter((input) => input.checked);
    procedureInputs.forEach((input) => {
      input.required = false;
      input.setCustomValidity('');
    });
    if (!selected.length) {
      procedureInputs[0].required = true;
      procedureInputs[0].setCustomValidity(copy.selectProcedure);
    }
    return selected;
  };

  const syncTermRequirements = () => {
    const selected = syncProcedureGroupValidity();
    procedureInputs.forEach((procedureInput) => {
      const termInput = matchingTermInput(procedureInput);
      if (!termInput) return;
      termInput.required = procedureInput.checked;
      if (!procedureInput.checked || termInput.checked) {
        termInput.setCustomValidity('');
        return;
      }
      termInput.setCustomValidity(copy.acceptTerm);
    });
    return selected;
  };

  const openAndFocusTerm = (procedureInput, focusAcceptance = false) => {
    const card = procedureCard(procedureInput);
    const details = qs('details', card);
    const termInput = matchingTermInput(procedureInput);
    if (details) details.open = true;
    const target = focusAcceptance && termInput ? termInput : details || card || procedureInput;
    window.requestAnimationFrame(() => {
      target?.scrollIntoView?.({ behavior: 'smooth', block: 'center' });
      if (focusAcceptance && termInput) termInput.focus({ preventScroll: true });
    });
  };

  procedureInputs.forEach((procedureInput) => {
    procedureInput.addEventListener('change', () => {
      syncTermRequirements();
      if (procedureInput.checked) openAndFocusTerm(procedureInput);
    });
  });

  qsa('input[name^="accepted_term_"]', form).forEach((termInput) => {
    termInput.addEventListener('change', syncTermRequirements);
  });

  qsa('input[type="file"].sf-consent-file-input', form).forEach((fileInput) => {
    const status = fileInput.nextElementSibling?.querySelector?.('.sf-file-status');
    const emptyText = status?.textContent || '';
    fileInput.addEventListener('change', () => {
      if (!status) return;
      const files = Array.from(fileInput.files || []);
      status.textContent = files.length ? files.map((file) => file.name).join(', ') : emptyText;
    });
  });

  form.addEventListener('submit', () => {
    const selected = syncTermRequirements();
    const missingTerm = selected.find((procedureInput) => {
      const termInput = matchingTermInput(procedureInput);
      return termInput && !termInput.checked;
    });
    if (missingTerm) openAndFocusTerm(missingTerm, true);
  }, { capture: true });

  syncTermRequirements();
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

function populateMetadata(form, context = {}) {
  const now = new Date();
  const params = new URLSearchParams(window.location.search);
  const browser = parseBrowser(navigator.userAgent || '');
  const os = parseOperatingSystem(navigator.userAgent || '');
  const history = pageHistory();
  const domain = referrerDomain();
  const serviceInterest = selectedText(form, ['service_interest', 'interest', 'reason', 'treatment_interest', 'treatment'])
    || fieldValue(form, ['service_interest', 'interest', 'reason', 'treatment_interest', 'treatment'])
    || pageCategory();
  const inquiryCategory = selectedText(form, ['category', 'reason', 'subject', 'service_interest'])
    || fieldValue(form, ['category', 'reason', 'subject', 'service_interest'])
    || formType(form);
  const messageContent = fieldValue(form, ['message', 'notes', 'concern', 'question']);
  const phone = fieldValue(form, ['phone', 'telephone', 'whatsapp', 'phone_or_whatsapp']);
  const temperature = leadTemperature(form, serviceInterest, messageContent);
  const elapsed = Math.max(0, Math.round((Date.now() - (performance.timeOrigin || SESSION_STARTED_AT)) / 1000));
  const sessionDuration = Math.max(0, Math.round((Date.now() - SESSION_STARTED_AT) / 1000));
  const navigation = performance.getEntriesByType?.('navigation')?.[0];
  const loadSpeed = navigation ? Math.round(navigation.loadEventEnd || navigation.domComplete || 0) : '';
  const offsetMinutes = -now.getTimezoneOffset();
  const offsetSign = offsetMinutes >= 0 ? '+' : '-';
  const offsetHours = String(Math.floor(Math.abs(offsetMinutes) / 60)).padStart(2, '0');
  const offsetRemainder = String(Math.abs(offsetMinutes) % 60).padStart(2, '0');
  const submissionId = randomId('submission');
  const metadata = {
    lead_name: fieldValue(form, ['name', 'full_name', 'full-name']),
    lead_email: fieldValue(form, ['email', 'email_address']),
    lead_phone: phone,
    phone_number: phone,
    country: '',
    region: '',
    city: '',
    city_location: '',
    location_available: 'no',
    language_preference: document.documentElement.lang || '',
    service_interest: serviceInterest,
    inquiry_category: inquiryCategory,
    message_content: messageContent,
    website_domain: window.location.hostname,
    current_page_url: window.location.href,
    page_path: window.location.pathname,
    current_page_filename: window.location.pathname.split('/').pop() || 'index.html',
    page_filename: window.location.pathname.split('/').pop() || 'index.html',
    current_page_title: document.title,
    page_title: document.title,
    page_category: pageCategory(),
    current_section: form.closest('section')?.id || form.closest('section')?.dataset.sectionName || '',
    language_selected: document.documentElement.lang || '',
    language_version_visited: document.documentElement.lang || '',
    website_language: document.documentElement.dataset.defaultLang || document.documentElement.lang || '',
    browser_language: navigator.language || '',
    browser_locale: navigator.languages?.join(', ') || navigator.language || '',
    language: document.documentElement.lang || navigator.language || '',
    timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || '',
    utc_offset: `${offsetSign}${offsetHours}:${offsetRemainder}`,
    referrer: document.referrer,
    referrer_url: document.referrer,
    referrer_domain: domain,
    search_engine_source: searchEngineSource(domain),
    original_landing_page: initialLandingPage(),
    previous_pages_visited: history.slice(0, -1).join(' | '),
    pages_viewed_before_submission: String(Math.max(0, history.length - 1)),
    last_page_before_submission: history.length > 1 ? history[history.length - 2] : '',
    current_page_path: window.location.pathname,
    canonical_url: canonicalUrl(),
    lead_source: originalSource(params, domain),
    original_source: originalSource(params, domain),
    marketing_source: params.get('utm_source') || '',
    medium: params.get('utm_medium') || '',
    campaign: params.get('utm_campaign') || '',
    campaign_name: params.get('utm_campaign') || '',
    content: params.get('utm_content') || '',
    term: params.get('utm_term') || '',
    advertisement_id: params.get('gclid') || params.get('fbclid') || params.get('msclkid') || params.get('ttclid') || '',
    social_media_source: socialSource(params, domain),
    screen_resolution: `${window.screen?.width || ''}x${window.screen?.height || ''}`,
    viewport_size: `${document.documentElement.clientWidth || ''}x${document.documentElement.clientHeight || ''}`,
    window_size: `${window.innerWidth || ''}x${window.innerHeight || ''}`,
    device_pixel_ratio: window.devicePixelRatio || '',
    operating_system: os.name,
    operating_system_version: os.version,
    browser: browser.name,
    browser_version: browser.version,
    connection_type: navigator.connection?.effectiveType || '',
    breakpoint_used: window.innerWidth < 768 ? 'mobile' : window.innerWidth < 1180 ? 'tablet' : 'desktop',
    rendering_engine: browser.name === 'Firefox' ? 'Gecko' : browser.name === 'Safari' ? 'WebKit' : browser.name === 'Unknown' ? '' : 'Blink',
    device_type: deviceType(),
    desktop_mobile_tablet: deviceType(),
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
    form_location: form.closest('section')?.dataset.sectionName || form.closest('section')?.id || document.body?.dataset.page || '',
    form_version: form.dataset.formVersion || '2026-07-21',
    form_design_variant: form.dataset.designVariant || 'editorial-default',
    submission_id: submissionId,
    submission_timestamp: now.toISOString(),
    submission_status: context.submissionStatus || 'attempted',
    validation_status: context.validationStatus || 'passed',
    error_count: context.errorCount ?? 0,
    site_version: window.SofiatiSite?.version || '',
    page_template: document.body?.dataset.page || currentPage(),
    current_navigation_language: isPortuguese() ? 'pt-BR' : 'en',
    session_identifier: sessionIdentifier(),
    session_id: sessionIdentifier(),
    submission_identifier: submissionId,
    returning_visitor: returningVisitor(),
    first_visit_datetime: firstVisitDate(),
    anonymous_visitor_id: anonymousVisitorId(),
    time_spent_on_page_seconds: elapsed,
    total_session_duration_seconds: sessionDuration,
    scroll_depth_percentage: scrollDepthPercentage(),
    cta_clicked_before_submitting: lastCtaClicked,
    interactions_before_submission: interactionCount,
    downloaded_resources: '',
    articles_viewed: viewedItems('.sf-journal-card h3, article h2, article h3', pageCategory() === 'journal' ? [document.title] : []),
    treatments_services_viewed: viewedItems('[data-treatment-filterable] h2, .sf-content-card h3', /treat|tratamento|laser|skin|pele|care|cuidados/.test(pageCategory()) ? [document.title] : []),
    cookie_consent_status: consentPreference('analytics'),
    marketing_consent_status: 'not_requested',
    consent_timestamp: fieldValue(form, 'consent_timestamp'),
    privacy_policy_version_accepted: fieldValue(form, 'privacy_notice_version') || '2026-07',
    terms_acceptance: fieldValue(form, ['terms_acceptance', 'consultation_acknowledgement']),
    data_processing_consent: fieldValue(form, ['privacy_acknowledgement']),
    communication_preferences: fieldValue(form, ['communication_preferences', 'preferred_contact']),
    lead_score: temperature === 'Warm' ? '60' : '30',
    lead_temperature: temperature,
    priority_level: temperature === 'Warm' ? 'normal' : 'low',
    customer_stage: 'New lead',
    assigned_team_member: 'Franciele Sofiati',
    follow_up_date: '',
    crm_id: '',
    notes: '',
    tags: [formType(form), serviceInterest, document.documentElement.lang || ''].filter(Boolean).join(', '),
    ai_summary_of_inquiry: 'not_generated',
    detected_intent: serviceInterest || inquiryCategory || 'not_generated',
    service_category: serviceInterest || pageCategory(),
    urgency_level: /dor|pain|urgente|urgent|hoje|today/.test(messageContent.toLowerCase()) ? 'Medium' : 'Low',
    sentiment_analysis: 'not_generated',
    language_detection: document.documentElement.lang || '',
    suggested_reply_type: formType(form).includes('newsletter') ? 'newsletter_confirmation' : 'invite_consultation',
    recommended_next_action: formType(form).includes('newsletter') ? 'confirm_subscription' : 'review_and_reply',
    lead_quality_score: temperature === 'Warm' ? 'Medium' : 'Low',
    page_load_speed_ms: loadSpeed,
    core_web_vitals: 'not_measured_on_submission',
    failed_resources: window.SofiatiFailedResources?.join?.(' | ') || '',
    form_loading_time_ms: '',
    javascript_errors: window.SofiatiJavaScriptErrors?.join?.(' | ') || '',
    browser_compatibility_issues: '',
    spam_score: 'not_assessed',
    bot_detection_result: 'honeypot_passed',
    captcha_result: 'not_used',
    ip_risk_score: 'not_assessed',
    submission_frequency: 'not_assessed',
    duplicate_submission_detection: 'not_assessed',
    suspicious_activity_flags: ''
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
    setupConsentSpecificTerms(form);
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
      const redirectUrl = populateMetadata(form, {
        submissionStatus: 'attempted',
        validationStatus: 'passed',
        errorCount: 0
      });
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
