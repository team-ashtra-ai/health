/*
 * Consent-aware measurement for Franciele Sofiati.
 *
 * Only fixed, public interface text and coarse technical values are allowed.
 * Names, contact details, form values, messages, health information, URL query
 * strings and stack traces must never be pushed. Add future tracking with the
 * documented data-track/data-track-section attributes, not brittle CSS copy.
 */
(function initialiseFrancieleAnalytics(window, document) {
  "use strict";

  const config = window.FRANCIELE_ANALYTICS_CONFIG;
  const consent = window.SofiatiConsentMode;
  if (!config || !consent || window.FrancieleAnalytics) return;

  const dataLayer = window.dataLayer = window.dataLayer || [];
  const safeEvents = Object.freeze({
    cta_click: ["cta_text", "cta_url", "cta_location", "cta_purpose"],
    contact_click: ["contact_method", "link_text", "link_location"],
    social_click: ["social_network", "link_location"],
    outbound_click: ["link_domain", "link_text", "link_location"],
    file_download: ["file_name", "file_extension", "link_location"],
    language_change: ["from_language", "to_language"],
    form_start: ["form_name", "form_type"],
    form_submit: ["form_name", "form_type"],
    form_error: ["form_name", "form_type", "error_type", "error_count"],
    form_success: ["form_name", "form_type"],
    generate_lead: ["form_name", "form_type", "lead_type", "method"],
    faq_open: ["faq_question", "faq_position"],
    section_view: ["section_id", "section_name", "section_number"],
    scroll_depth: ["scroll_percent"],
    engagement_time: ["engagement_seconds"],
    field_performance: [
      "lcp_ms", "cls_score", "inp_ms", "ttfb_ms",
      "dom_content_loaded_ms", "page_load_ms"
    ],
    javascript_error: ["error_type", "script_name", "line_bucket"],
    consent_update: ["analytics_consent", "preferences_consent", "consent_source"]
  });
  const commonParameters = Object.freeze([
    "page_name", "page_type", "content_group", "page_language", "page_path"
  ]);
  const publicTextEvents = new Set(["cta_click", "outbound_click", "faq_open", "section_view"]);
  const downloadedExtensions = new Set([
    "pdf", "doc", "docx", "xls", "xlsx", "csv", "zip", "rtf", "txt"
  ]);
  const pageContext = buildPageContext();
  const trackedSections = new Set();
  const trackedScroll = new Set();
  const trackedEngagement = new Set();
  const trackedFaqItems = new WeakSet();
  const startedForms = new WeakSet();
  const errorKeys = new Set();
  let pageContextPushed = false;
  let activeSeconds = 0;
  let errorCount = 0;
  let performancePayload = null;
  let performanceSent = false;

  function debug(message, detail) {
    if (config.debug && window.console) {
      console.info(`[Franciele analytics] ${message}`, detail || "");
    }
  }

  function normalLanguage() {
    const language = (document.documentElement.lang || "en").toLowerCase();
    return language.startsWith("pt") ? "pt-BR" : "en";
  }

  function cleanPath(pathname) {
    const path = String(pathname || "/").replace(/\/{2,}/g, "/");
    return path || "/";
  }

  function buildPageContext() {
    const baseName = String(document.body?.dataset.page || "unknown")
      .toLowerCase()
      .replace(/[^a-z0-9-]/g, "");
    const path = cleanPath(window.location.pathname);
    const article = /\/journal\/[^/]+\.html$/i.test(path);
    const pageName = article
      ? path.split("/").pop().replace(/\.html$/i, "")
      : (baseName || "unknown");
    return Object.freeze({
      page_name: pageName,
      page_type: article ? "JournalArticle" : (config.pageTypes[baseName] || "ContentPage"),
      content_group: article ? "Journal" : (config.pageGroups[baseName] || "Core"),
      page_language: normalLanguage(),
      page_path: path
    });
  }

  function safeText(value, maximum = 120) {
    const text = String(value || "").replace(/\s+/g, " ").trim().slice(0, maximum);
    if (!text) return "";
    if (
      /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i.test(text) ||
      /(?:\+?\d[\d\s().-]{7,}\d)/.test(text)
    ) return "";
    return text;
  }

  function safeNumber(value) {
    const number = Number(value);
    return Number.isFinite(number) ? number : undefined;
  }

  function safeUrlPath(value) {
    try {
      const url = new URL(String(value || ""), window.location.href);
      return url.origin === window.location.origin
        ? `${url.pathname}${url.hash && !/[?&=]/.test(url.hash) ? url.hash : ""}`
        : url.hostname;
    } catch (_) {
      return "";
    }
  }

  function sanitizeParameter(eventName, key, value) {
    if (typeof value === "number") return safeNumber(value);
    if (key.endsWith("_url")) return safeUrlPath(value);
    if (key === "link_domain" || key === "script_name" || key === "file_name") {
      return safeText(value, 100).replace(/[^a-z0-9._-]/gi, "");
    }
    if (publicTextEvents.has(eventName)) return safeText(value, key === "faq_question" ? 160 : 120);
    return safeText(value, 80);
  }

  function pushPageContext() {
    if (pageContextPushed || !consent.hasAnalyticsConsent()) return;
    pageContextPushed = true;
    dataLayer.push({
      event: "page_context",
      ...pageContext,
      ...(config.debug ? { debug_mode: true } : {})
    });
    debug("Internal page context queued.", pageContext);
  }

  function track(eventName, parameters = {}) {
    if (!consent.hasAnalyticsConsent() || !safeEvents[eventName]) return false;
    pushPageContext();
    const allowed = new Set([...commonParameters, ...safeEvents[eventName]]);
    const event = {
      event: eventName,
      ...pageContext,
      ...(config.debug ? { debug_mode: true } : {})
    };
    Object.entries(parameters).forEach(([key, value]) => {
      if (!allowed.has(key) || value === null || value === undefined) return;
      const sanitized = sanitizeParameter(eventName, key, value);
      if (sanitized !== "" && sanitized !== undefined) event[key] = sanitized;
    });
    dataLayer.push(event);
    debug(`Event queued: ${eventName}`, event);
    return true;
  }

  function linkLocation(element) {
    if (element.dataset.linkLocation) return element.dataset.linkLocation;
    if (element.closest("[data-loaded-partial='footer'], footer")) return "footer";
    if (element.closest("[data-loaded-partial='topbar']")) return "topbar";
    if (element.closest("[data-loaded-partial='header'], header.sf-header")) return "header";
    if (element.closest("[data-loaded-partial='floating-widgets']")) return "floating";
    if (element.closest("[data-pattern='hero'], .sj-masthead, .sja-hero")) return "hero";
    if (element.closest("form")) return "form";
    return "body";
  }

  function visibleLinkText(link, fallback) {
    return safeText(link.dataset.trackLabel || link.getAttribute("aria-label") || link.textContent)
      || fallback;
  }

  function classifyHref(link) {
    const raw = link.getAttribute("href") || "";
    if (/^mailto:/i.test(raw)) return "email";
    if (/^tel:/i.test(raw)) return "telephone";
    try {
      const url = new URL(raw, window.location.href);
      if (/^(?:www\.)?(?:wa\.me|api\.whatsapp\.com)$/i.test(url.hostname)) return "whatsapp";
      if (/(?:^|\.)instagram\.com$/i.test(url.hostname)) return "instagram";
      const extension = url.pathname.split(".").pop().toLowerCase();
      if (downloadedExtensions.has(extension)) return "download";
      if (/^https?:$/i.test(url.protocol) && url.origin !== window.location.origin) return "outbound";
    } catch (_) {}
    return "";
  }

  function purposeForLink(link) {
    if (link.dataset.ctaPurpose) return link.dataset.ctaPurpose;
    const href = (link.getAttribute("href") || "").toLowerCase();
    const purposes = [
      ["consultation", "consultation"],
      ["contact", "contact"],
      ["treatments", "treatments"],
      ["skin", "skin"],
      ["laser", "laser"],
      ["journal", "journal"],
      ["care", "aftercare"],
      ["results", "results"]
    ];
    return purposes.find(([needle]) => href.includes(needle))?.[1] || "navigation";
  }

  function handleTrackedClick(event) {
    const link = event.target.closest?.("a[href]");
    if (!link || link.closest("[data-analytics-ignore]") || link.closest("[data-analytics-sensitive]")) return;
    const explicit = link.dataset.track || "";
    const inferred = classifyHref(link);
    const classification = explicit || inferred || (link.matches(".sf-button, .sffo-button") ? "cta" : "");
    const location = linkLocation(link);

    if (classification === "contact" || ["whatsapp", "telephone", "email"].includes(inferred)) {
      const method = link.dataset.contactMethod || inferred;
      track("contact_click", {
        contact_method: method,
        link_text: ["whatsapp", "telephone", "email"].includes(method) ? method : "contact",
        link_location: location
      });
      return;
    }
    if (classification === "social" || inferred === "instagram") {
      track("social_click", {
        social_network: link.dataset.socialNetwork || inferred || "social",
        link_location: location
      });
      return;
    }
    if (classification === "language" || link.dataset.lang) {
      const toLanguage = (link.dataset.lang || link.getAttribute("hreflang") || "").toLowerCase();
      const normalizedTarget = toLanguage.startsWith("pt") ? "pt-BR" : "en";
      if (normalizedTarget !== pageContext.page_language) {
        track("language_change", {
          from_language: pageContext.page_language,
          to_language: normalizedTarget
        });
      }
      return;
    }
    if (classification === "download" || inferred === "download") {
      const url = new URL(link.href, window.location.href);
      const fileName = decodeURIComponent(url.pathname.split("/").pop() || "download");
      track("file_download", {
        file_name: fileName,
        file_extension: fileName.split(".").pop().toLowerCase(),
        link_location: location
      });
      return;
    }
    if (classification === "outbound" || inferred === "outbound") {
      const url = new URL(link.href, window.location.href);
      track("outbound_click", {
        link_domain: url.hostname,
        link_text: visibleLinkText(link, "external link"),
        link_location: location
      });
      return;
    }
    if (classification === "cta") {
      track("cta_click", {
        cta_text: visibleLinkText(link, "call to action"),
        cta_url: link.href,
        cta_location: link.dataset.ctaLocation || location,
        cta_purpose: purposeForLink(link)
      });
    }
  }

  function decorateDynamicContent(root = document) {
    root.querySelectorAll("a[href]").forEach((link) => {
      if (link.dataset.track || link.closest("[data-analytics-ignore]")) return;
      const classification = classifyHref(link);
      if (["whatsapp", "telephone", "email"].includes(classification)) {
        link.dataset.track = "contact";
        link.dataset.contactMethod = classification;
      } else if (classification === "instagram") {
        link.dataset.track = "social";
        link.dataset.socialNetwork = "instagram";
      } else if (classification === "download") {
        link.dataset.track = "download";
      } else if (classification === "outbound") {
        link.dataset.track = "outbound";
      } else if (link.dataset.lang) {
        link.dataset.track = "language";
      } else if (link.matches(".sf-button, .sffo-button")) {
        link.dataset.track = "cta";
      }
      if (link.dataset.track && !link.dataset.linkLocation) {
        link.dataset.linkLocation = linkLocation(link);
      }
    });
  }

  function initialiseFaqTracking(root = document) {
    root.querySelectorAll("details[data-track-faq], details.sf-accordion-item").forEach((item, index) => {
      if (item.dataset.analyticsFaqReady === "true") return;
      item.dataset.analyticsFaqReady = "true";
      item.addEventListener("toggle", () => {
        if (!item.open || trackedFaqItems.has(item) || !consent.hasAnalyticsConsent()) return;
        trackedFaqItems.add(item);
        const summary = item.querySelector("summary");
        track("faq_open", {
          faq_question: item.dataset.faqQuestion || summary?.textContent || "FAQ",
          faq_position: Number(item.dataset.faqPosition || index + 1)
        });
      });
    });
  }

  function initialiseSectionTracking(root = document) {
    if (!("IntersectionObserver" in window)) return;
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        const section = entry.target;
        const key = section.id || section.dataset.sectionName;
        if (!entry.isIntersecting || !key || trackedSections.has(key)) {
          window.clearTimeout(Number(section.dataset.analyticsVisibilityTimer || 0));
          delete section.dataset.analyticsVisibilityTimer;
          return;
        }
        if (section.dataset.analyticsVisibilityTimer) return;
        section.dataset.analyticsVisibilityTimer = String(window.setTimeout(() => {
          delete section.dataset.analyticsVisibilityTimer;
          if (trackedSections.has(key) || !consent.hasAnalyticsConsent()) return;
          trackedSections.add(key);
          observer.unobserve(section);
          track("section_view", {
            section_id: section.id || "section",
            section_name: section.dataset.sectionName || section.querySelector("h2, h3")?.textContent || section.id,
            section_number: section.dataset.sectionNumber || section.dataset.section || ""
          });
        }, config.sectionMinimumVisibleMs));
      });
    }, { threshold: 0.15 });

    root.querySelectorAll("[data-track-section]").forEach((section) => {
      if (section.dataset.analyticsSectionReady === "true") return;
      section.dataset.analyticsSectionReady = "true";
      observer.observe(section);
    });
  }

  function checkScrollDepth() {
    const documentHeight = Math.max(
      document.documentElement.scrollHeight,
      document.body?.scrollHeight || 0
    );
    if (documentHeight <= 0) return;
    const percent = Math.min(100, Math.round(
      ((window.scrollY + window.innerHeight) / documentHeight) * 100
    ));
    config.scrollThresholds.forEach((threshold) => {
      if (percent >= threshold && !trackedScroll.has(threshold)) {
        if (track("scroll_depth", { scroll_percent: threshold })) {
          trackedScroll.add(threshold);
        }
      }
    });
  }

  function initialiseScrollTracking() {
    let queued = false;
    const requestCheck = () => {
      if (queued) return;
      queued = true;
      window.requestAnimationFrame(() => {
        queued = false;
        checkScrollDepth();
      });
    };
    window.addEventListener("scroll", requestCheck, { passive: true });
    window.addEventListener("resize", requestCheck, { passive: true });
    requestCheck();
  }

  function initialiseEngagementTracking() {
    window.setInterval(() => {
      if (
        !consent.hasAnalyticsConsent() ||
        document.visibilityState !== "visible" ||
        !document.hasFocus()
      ) return;
      activeSeconds += 1;
      config.engagementThresholds.forEach((threshold) => {
        if (activeSeconds >= threshold && !trackedEngagement.has(threshold)) {
          if (track("engagement_time", { engagement_seconds: threshold })) {
            trackedEngagement.add(threshold);
          }
        }
      });
    }, 1000);
  }

  function formDetails(form) {
    return {
      form_name: form.dataset.analyticsForm || form.id || "website_form",
      form_type: form.dataset.formType || "contact",
      lead_type: form.dataset.leadType || "",
      method: form.dataset.analyticsMethod || "formspree"
    };
  }

  function safeSessionRead() {
    try {
      const parsed = JSON.parse(window.sessionStorage.getItem(config.leadStorageKey) || "null");
      if (!parsed || Date.now() - Number(parsed.createdAt || 0) > config.leadLifetimeMinutes * 60000) {
        window.sessionStorage.removeItem(config.leadStorageKey);
        return null;
      }
      return parsed;
    } catch (_) {
      return null;
    }
  }

  function safeSessionWrite(record) {
    try {
      window.sessionStorage.setItem(config.leadStorageKey, JSON.stringify(record));
    } catch (_) {}
  }

  function randomToken() {
    const values = new Uint32Array(3);
    if (window.crypto?.getRandomValues) window.crypto.getRandomValues(values);
    else values.forEach((_, index) => { values[index] = Math.floor(Math.random() * 0xffffffff); });
    return Array.from(values, (value) => value.toString(36)).join("-");
  }

  function beginSubmission(form) {
    if (!consent.hasAnalyticsConsent()) return;
    const details = formDetails(form);
    safeSessionWrite({
      token: randomToken(),
      createdAt: Date.now(),
      status: "pending",
      generated: false,
      formName: details.form_name,
      formType: details.form_type,
      leadType: details.lead_type,
      method: details.method
    });
    track("form_submit", details);
  }

  function confirmSubmission(form) {
    const details = formDetails(form);
    track("form_success", details);
    if (!details.lead_type) return;
    const existing = safeSessionRead();
    if (existing?.generated) return;
    const record = existing || {
      token: randomToken(),
      createdAt: Date.now(),
      formName: details.form_name,
      formType: details.form_type,
      leadType: details.lead_type,
      method: details.method
    };
    record.status = "confirmed";
    record.generated = true;
    safeSessionWrite(record);
    track("generate_lead", details);
  }

  function confirmThankYouFallback() {
    if (document.body?.dataset.page !== "thank-you" || !consent.hasAnalyticsConsent()) return;
    const record = safeSessionRead();
    if (!record || record.generated || record.status !== "pending") return;
    record.status = "confirmed";
    record.generated = true;
    safeSessionWrite(record);
    const details = {
      form_name: record.formName,
      form_type: record.formType,
      lead_type: record.leadType,
      method: record.method
    };
    track("form_success", details);
    if (record.leadType) track("generate_lead", details);
  }

  function initialiseForms(root = document) {
    root.querySelectorAll("form[data-analytics-form]").forEach((form) => {
      if (form.dataset.analyticsReady === "true") return;
      form.dataset.analyticsReady = "true";
      const start = (event) => {
        const field = event.target;
        if (
          startedForms.has(form) ||
          !consent.hasAnalyticsConsent() ||
          !field?.matches?.("input:not([type='hidden']), select, textarea") ||
          field.closest("[data-analytics-ignore]") ||
          field.classList.contains("sf-honeypot")
        ) return;
        startedForms.add(form);
        track("form_start", formDetails(form));
      };
      form.addEventListener("focusin", start, { passive: true });
      form.addEventListener("input", start, { passive: true });
      form.addEventListener("change", start, { passive: true });
    });
  }

  function initialiseFormLifecycle() {
    document.addEventListener("sofiati:form-submit", (event) => {
      if (event.detail?.form) beginSubmission(event.detail.form);
    });
    document.addEventListener("sofiati:form-error", (event) => {
      const form = event.detail?.form;
      if (!form) return;
      track("form_error", {
        ...formDetails(form),
        error_type: event.detail.errorType || "submission_error",
        error_count: Number(event.detail.errorCount || 1)
      });
    });
    document.addEventListener("sofiati:form-success", (event) => {
      if (event.detail?.form) confirmSubmission(event.detail.form);
    });
  }

  function initialisePerformanceTracking() {
    let lcp = 0;
    let cls = 0;
    let inp = 0;
    try {
      new PerformanceObserver((list) => {
        const entries = list.getEntries();
        if (entries.length) lcp = entries[entries.length - 1].startTime;
      }).observe({ type: "largest-contentful-paint", buffered: true });
    } catch (_) {}
    try {
      new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (!entry.hadRecentInput) cls += entry.value;
        });
      }).observe({ type: "layout-shift", buffered: true });
    } catch (_) {}
    try {
      new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          if (entry.interactionId && entry.duration > inp) inp = entry.duration;
        });
      }).observe({ type: "event", buffered: true, durationThreshold: 40 });
    } catch (_) {}

    window.addEventListener("load", () => {
      window.setTimeout(() => {
        const navigation = performance.getEntriesByType("navigation")[0];
        if (!navigation) return;
        performancePayload = {
          lcp_ms: Math.round(lcp),
          cls_score: Number(cls.toFixed(3)),
          inp_ms: Math.round(inp),
          ttfb_ms: Math.round(navigation.responseStart),
          dom_content_loaded_ms: Math.round(navigation.domContentLoadedEventEnd),
          page_load_ms: Math.round(navigation.loadEventEnd)
        };
        sendPerformance();
      }, 5000);
    }, { once: true });
  }

  function sendPerformance() {
    if (performanceSent || !performancePayload || !consent.hasAnalyticsConsent()) return;
    performanceSent = track("field_performance", performancePayload);
  }

  function scriptName(source) {
    try {
      return new URL(source || "", window.location.href).pathname.split("/").pop() || "inline";
    } catch (_) {
      return "inline";
    }
  }

  function reportError(type, source, line) {
    if (errorCount >= 5) return;
    const lineBucket = Math.max(0, Math.floor(Number(line || 0) / 10) * 10);
    const key = `${type}|${scriptName(source)}|${lineBucket}`;
    if (errorKeys.has(key)) return;
    errorKeys.add(key);
    errorCount += 1;
    track("javascript_error", {
      error_type: type,
      script_name: scriptName(source),
      line_bucket: lineBucket
    });
  }

  function initialiseErrorTracking() {
    window.addEventListener("error", (event) => {
      if (event.target && event.target !== window) {
        reportError("resource_error", event.target.src || event.target.href, 0);
        return;
      }
      reportError("runtime_error", event.filename, event.lineno);
    }, true);
    window.addEventListener("unhandledrejection", () => {
      reportError("unhandled_rejection", "promise", 0);
    });
  }

  function start() {
    decorateDynamicContent();
    initialiseFaqTracking();
    initialiseSectionTracking();
    initialiseForms();
    initialiseScrollTracking();
    initialiseEngagementTracking();
    initialiseFormLifecycle();
    initialisePerformanceTracking();
    initialiseErrorTracking();
    document.addEventListener("click", handleTrackedClick);
    confirmThankYouFallback();
    if (consent.hasAnalyticsConsent()) pushPageContext();
  }

  document.addEventListener("sf:partials-loaded", () => {
    decorateDynamicContent();
    initialiseForms();
  });
  document.addEventListener("sofiati:analytics-consent", (event) => {
    if (!event.detail?.analytics) return;
    pushPageContext();
    track("consent_update", {
      analytics_consent: "granted",
      preferences_consent: event.detail.preferences ? "granted" : "denied",
      consent_source: event.detail.source || "cookie_controls"
    });
    checkScrollDepth();
    sendPerformance();
    confirmThankYouFallback();
  });

  window.FrancieleAnalytics = Object.freeze({
    pageContext,
    track,
    decorate: decorateDynamicContent,
    version: "1.0.0"
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start, { once: true });
  } else {
    start();
  }
})(window, document);
