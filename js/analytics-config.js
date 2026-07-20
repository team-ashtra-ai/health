/*
 * Franciele Sofiati analytics configuration
 *
 * GA4 is delivered through the Google tag installed in every page head. The
 * optional GTM container remains consent-gated for future compatibility.
 *
 * Set debug to true only for local/preview validation. Consent remains required
 * in debug mode. Basic consent mode means GTM is not requested until the visitor
 * grants analytics consent.
 */
(function configureFrancieleAnalytics(window) {
  "use strict";

  window.dataLayer = window.dataLayer || [];

  const config = {
    siteName: "Franciele Sofiati · Biomedical Practitioner · Aesthetician · Cosmetologist",
    productionDomain: "www.francielesofiati.com",
    streamName: "FrancieleStream",
    streamId: "15290697519",
    gtmContainerId: "GTM-REPLACE_ME",
    ga4MeasurementId: "G-S41CQ1303W",
    googleTagId: "GT-P8Z9PB5L",
    consentMode: "basic",
    consentStorageKey: "sofiati_cookie_preferences_v3",
    leadStorageKey: "sofiati_analytics_pending_lead_v1",
    leadLifetimeMinutes: 30,
    debug: false,
    scrollThresholds: [25, 50, 75, 90],
    engagementThresholds: [30, 60, 120],
    sectionMinimumVisibleMs: 800,
    pageGroups: {
      home: "Core",
      "not-found": "Core",
      about: "Trust",
      mission: "Trust",
      values: "Trust",
      testimonials: "Trust",
      treatments: "Treatments",
      skin: "Treatments",
      laser: "Treatments",
      results: "Treatments",
      care: "Patient Care",
      faq: "Patient Care",
      blog: "Journal",
      journal: "Journal",
      consultation: "Conversion",
      contact: "Conversion",
      "thank-you": "Conversion",
      accessibility: "Legal",
      cookies: "Legal",
      legal: "Legal",
      privacy: "Legal"
    },
    pageTypes: {
      home: "HomePage",
      "not-found": "ErrorPage",
      about: "ProfilePage",
      mission: "AboutPage",
      values: "AboutPage",
      testimonials: "TrustPage",
      treatments: "TreatmentCollection",
      skin: "TreatmentGuide",
      laser: "TreatmentGuide",
      results: "ResultsGuide",
      care: "PatientCareGuide",
      faq: "FAQPage",
      blog: "BlogIndex",
      journal: "JournalIndex",
      consultation: "ConsultationPage",
      contact: "ContactPage",
      "thank-you": "ConfirmationPage",
      accessibility: "PolicyPage",
      cookies: "PolicyPage",
      legal: "PolicyPage",
      privacy: "PolicyPage"
    }
  };

  window.FRANCIELE_ANALYTICS_CONFIG = Object.freeze(config);
})(window);
