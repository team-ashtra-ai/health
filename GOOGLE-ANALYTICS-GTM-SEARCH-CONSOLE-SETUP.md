# Google Analytics, GTM and Search Console Setup

This guide separates what is already implemented in the repository from the Google account work that must still be completed. Analytics is **not live** while the placeholder IDs remain in the code or until the GTM container is configured and published.

## What the code already does

- Creates one sitewide `dataLayer`.
- Uses Google Tag Manager as the only delivery path for GA4.
- Defaults all optional Consent Mode v2 categories to denied.
- Keeps advertising storage, advertising user data and advertising personalisation denied.
- Uses basic consent mode: GTM is not requested until analytics permission is granted.
- Reuses the existing English and Portuguese cookie controls and saved preference.
- Pushes a non-GA4 `page_context` setup event.
- Pushes the custom events listed in `GTM-EVENT-MEASUREMENT-PLAN.csv`.
- Protects contact, consultation and accessibility form fields from value collection.
- Requires a confirmed Formspree response before `form_success` or `generate_lead`.
- Deduplicates leads with a short-lived, random, non-personal `sessionStorage` record.
- Limits JavaScript error reporting to a type, script basename and coarse line bucket.
- Keeps `thank-you.html` and `pt/thank-you.html` set to `noindex, follow`.

The relevant files are:

- `js/analytics-config.js`
- `js/consent-manager.js`
- `js/analytics.js`
- `js/components/cookie-controls.js`
- `js/components/forms.js`

Run `python3 scripts/install-analytics.py` after regenerating HTML or translations. It installs the script block and tracking attributes idempotently.

## Values that must be replaced

Open `js/analytics-config.js`.

1. Replace `GTM-REPLACE_ME` with the Web container ID from Tag Manager. A real container ID starts with `GTM-`.
2. Replace `G-REPLACE_ME` with the GA4 Web stream Measurement ID. A real Measurement ID starts with `G-`.
3. Leave `consentMode: "basic"` unchanged unless the privacy architecture is deliberately reviewed.
4. Keep `debug: false` in production. Set it temporarily to `true` in a local or preview deployment to add `debug_mode` and console diagnostics.

The GA4 ID in this file is a documented reference. The operative Google Tag is created inside GTM using the same ID. Do not paste Google's direct `gtag.js` snippet into any HTML page.

## 1. Create GA4

Google's current setup flow is documented in [Set up Analytics for a website](https://support.google.com/analytics/answer/14183469).

1. Sign in at `analytics.google.com`.
2. Create or choose the business-owned Analytics account.
3. Create one GA4 property for Franciele Sofiati.
4. Use a clear property name such as `Franciele Sofiati Website`.
5. Choose the São Paulo reporting time zone.
6. Choose Brazilian real (`BRL`) as the reporting currency.
7. Create one Web data stream for `https://www.francielesofiati.com`.
8. Copy the Measurement ID beginning with `G-`.
9. Place that ID in `ga4MeasurementId` in `js/analytics-config.js`.
10. Use the same ID when creating the GTM Google Tag below.

### Enhanced Measurement

Keep automatic page views enabled. This site performs full HTML navigations, and the GTM Google Tag should create one page view for each page load.

Open the Web stream's Enhanced Measurement settings and disable:

- Scrolls, because the code sends 25%, 50%, 75% and 90% milestones.
- Outbound clicks, because the code classifies outbound, contact and social clicks.
- File downloads, because the code sends `file_download`.
- Form interactions, because the code confirms validation, submission and success itself.

Do not create a second GTM auto-event tag for those same interactions. Other Enhanced Measurement features should remain enabled only if they correspond to real site functionality and have been tested.

### Property settings

1. In Admin, open Data collection and modification → Data retention.
2. Select 14 months for event data retention. Standard GA4 properties support up to 14 months.
3. Open Admin → Data display → Events or Key events.
4. Mark `generate_lead` as a key event after it has first appeared, or create it as a new key event if the interface offers that option.
5. Do not mark `form_submit` or `form_success` as additional lead key events; doing so would inflate conversion reporting.

### Focused custom dimensions

In Admin → Data display → Custom definitions, create these event-scoped dimensions:

| Dimension name | Event parameter |
| --- | --- |
| Page type | `page_type` |
| Content group | `content_group` |
| CTA text | `cta_text` |
| CTA location | `cta_location` |
| Contact method | `contact_method` |
| Form name | `form_name` |
| Form type | `form_type` |
| Section name | `section_name` |

Avoid registering URLs, unique tokens, errors, every question or other high-cardinality values. Google recommends using predefined dimensions when available and avoiding unnecessary high-cardinality custom dimensions.

## 2. Create Google Tag Manager

1. Sign in at `tagmanager.google.com`.
2. Create a business-owned GTM account, or use the existing business account.
3. Create a **Web** container for `www.francielesofiati.com`.
4. Copy the container ID beginning with `GTM-`.
5. Replace `GTM-REPLACE_ME` in `js/analytics-config.js`.
6. Do not install GTM again through a CMS, hosting integration, inline snippet or plugin. The repository loads it dynamically after consent.
7. Do not add an unconditional GTM `noscript` iframe. A noscript iframe cannot read the existing JavaScript consent choice and would undermine basic consent mode.

### Create the main Google Tag

1. In GTM, open Tags → New.
2. Choose **Google Tag**.
3. Enter the GA4 `G-` ID as the Tag ID.
4. Name it `Google Tag – GA4 – Franciele Sofiati`.
5. Use **Initialization – All Pages** as the trigger.
6. In Consent Settings, require `analytics_storage`.
7. Save.

Because the container itself loads only after analytics consent, the Initialization trigger occurs only after a grant. The queued Consent Mode state is processed before normal measurement events.

### Create Data Layer Variables

Create Version 2 Data Layer Variables with the Data Layer Variable Name exactly matching each parameter:

`page_name`, `page_type`, `content_group`, `page_language`, `page_path`, `cta_text`, `cta_url`, `cta_location`, `cta_purpose`, `contact_method`, `link_text`, `link_url`, `link_domain`, `link_location`, `social_network`, `form_name`, `form_type`, `lead_type`, `method`, `error_type`, `error_count`, `faq_question`, `faq_position`, `section_id`, `section_name`, `section_number`, `scroll_percent`, `engagement_seconds`, `lcp_ms`, `cls_score`, `inp_ms`, `ttfb_ms`, `dom_content_loaded_ms`, `page_load_ms`, `analytics_consent`, `preferences_consent`, `consent_source`, and `debug_mode`.

Use a consistent name such as `DLV – page_type`.

`link_url` is documented for future compatibility but is intentionally not populated by the current privacy-safe events. Do not derive it from contact destinations.

### Create the custom-event trigger

1. Open Triggers → New → Custom Event.
2. Name it `CE – Franciele measurement events`.
3. Enable regular-expression matching.
4. Use:

```text
^(cta_click|contact_click|social_click|outbound_click|file_download|language_change|form_start|form_submit|form_error|form_success|generate_lead|faq_open|section_view|scroll_depth|engagement_time|field_performance|javascript_error|consent_update)$
```

Do not include `gtm.js`, `gtm.dom`, `gtm.load` or `page_context`.

### Create the reusable GA4 Event tag

1. Open Tags → New.
2. Choose **Google Analytics: GA4 Event**.
3. Select the previously created Google Tag or enter the same `G-` Measurement ID when required by the interface.
4. Set Event Name to `{{Event}}`.
5. Add the Data Layer Variables as event parameters using their exact parameter names.
6. Add only variables relevant to the event, or use a tested reusable Event Settings Variable.
7. Require `analytics_storage` in Consent Settings.
8. Attach `CE – Franciele measurement events`.
9. Name the tag `GA4 Event – Franciele custom events`.

Do not create separate click, scroll, form or outbound listeners in GTM. The repository has already classified and deduplicated them.

### Debug and publish

1. Click Preview in GTM.
2. Connect Tag Assistant to the preview or production URL.
3. Reject optional cookies first. Confirm the GTM request is absent.
4. Grant analytics consent. Confirm the container loads once.
5. Inspect the `page_context` event and confirm the GA4 Event tag does not fire for it.
6. Inspect each measurement event and its parameters.
7. Confirm the Google Tag fires once per page.
8. Confirm the reusable GA4 Event tag fires once per listed custom event.
9. Open GA4 DebugView and verify events in order. GTM Preview normally marks preview traffic for debugging; `debug: true` can also add `debug_mode` in a controlled preview.
10. Check that no name, email, telephone, form message, treatment concern or query string appears anywhere in Tag Assistant or the data layer.
11. Click Submit → Publish and Create Version.
12. Use a clear version name, for example `GA4 consent-aware measurement launch`.
13. Describe the consent rules, tags, trigger regex and Enhanced Measurement exclusions in the version description.

Google documents publishing and version history in [Publishing, versions, and approvals](https://support.google.com/tagmanager/answer/6107163).

## 3. Search Console

The homepage already contains the optional HTML-tag placeholder:

```text
GOOGLE_SITE_VERIFICATION_REPLACE_ME
```

Domain verification is preferred:

1. Sign in at `search.google.com/search-console`.
2. Add a **Domain property** for `francielesofiati.com`, without `https://`, `www` or a path.
3. Copy the TXT verification value supplied by Google.
4. In Cloudflare, open the domain → DNS → Records → Add record.
5. Select TXT, use the name/host Google specifies (often `@`), paste the exact value, and save.
6. Return to Search Console and verify.
7. Keep the TXT record after verification.

A Domain property covers protocols and subdomains and requires DNS verification. If HTML-tag verification is used instead, create the appropriate URL-prefix property and replace only the homepage placeholder with Google's exact token.

After deployment:

1. Submit `https://www.francielesofiati.com/sitemap.xml`.
2. Inspect `/`, `/consultation.html`, `/treatments.html`, `/skin.html` and `/laser.html`.
3. Confirm `thank-you.html` is excluded and remains `noindex`.
4. In Search Console Settings → Associations, associate the Search Console property with the GA4 property when the interface and permissions allow it.

The repository already contains `sitemap.xml`, and `robots.txt` references its production URL.

## 4. Internal traffic

Use GA4's IP-based internal traffic definition; do not send IP addresses through the site's data layer.

1. In GA4 Admin, open Data streams and select the Web stream.
2. Open the Google tag settings.
3. Choose Define internal traffic.
4. Create rules for the clinic's stable public IP address and the developer/agency's stable public IP addresses.
5. Keep the standard `traffic_type` value `internal` unless a documented alternative is needed.
6. Open Admin → Data collection and modification → Data filters.
7. Create an Internal Traffic filter that excludes `internal`.
8. Set it to **Testing**, not Active.
9. Generate test traffic from each listed IP.
10. Verify the test filter dimension in an Exploration after processing.
11. Activate only after the rule is proven.

Activated data filters permanently prevent matching future data from being processed and cannot restore it. Google's [internal traffic documentation](https://support.google.com/analytics/answer/10104470) recommends testing before activation.

## 5. Complete test checklist

### Consent

- Fresh browser: no request to `googletagmanager.com` before a choice.
- Reject: choice persists after reload and GTM remains absent.
- Accept analytics: GTM loads once.
- Revoke later: consent updates to denied and custom events stop.
- Advertising consent remains denied in every state.

### Interactions

- Hero and body CTAs produce one `cta_click`.
- WhatsApp, email and telephone produce one `contact_click`, never `outbound_click`.
- Instagram produces one `social_click`, never `outbound_click`.
- Genuine external links produce one `outbound_click`.
- English/Portuguese switching produces one `language_change` before navigation.
- Each FAQ produces one `faq_open` during the page view.
- Sections require sustained visibility and fire once.
- Scroll milestones fire once at 25%, 50%, 75% and 90%.
- Engagement pauses while the tab is hidden or unfocused.

### Forms and leads

- First meaningful field interaction produces one `form_start`.
- Native/client validation errors produce `form_error`, not `form_submit`.
- A valid request produces `form_submit`.
- A failed Formspree response produces `form_error`, not `form_success`.
- A confirmed response produces one `form_success`.
- Contact and consultation success produce one `generate_lead`.
- Accessibility feedback does not produce `generate_lead`.
- Direct visits and refreshes of the thank-you page do not create leads.
- A legitimate pending form flow can be confirmed by the thank-you fallback once.
- No field values or server response bodies appear in the data layer.

### Performance and errors

- One `field_performance` event contains finite, rounded numbers.
- A controlled error produces only `error_type`, `script_name` and `line_bucket`.
- Repeated identical errors are deduplicated and error volume is capped.
- No error message, stack trace, page HTML, query string or form value is sent.

## 6. Content Security Policy

No repository-level CSP was found. If the production host adds one, do not use broad wildcards. Test the exact directives in a staging/report-only policy first. GTM/GA4 commonly require these origins, depending on the container's tags and region:

- `script-src`: `https://www.googletagmanager.com`
- `connect-src`: `https://www.google-analytics.com`, `https://region1.google-analytics.com`, `https://www.googletagmanager.com`
- `img-src`: `https://www.google-analytics.com`, `https://www.googletagmanager.com`

Do not add Google Ads domains unless an advertising product is intentionally introduced and consent/legal requirements are reviewed.

## Privacy and operational limits

- This implementation is technical preparation, not legal advice.
- Basic consent mode intentionally sacrifices pre-consent measurement.
- GTM cannot be unloaded after it has loaded, but a later rejection updates consent to denied and the site stops pushing custom analytics events.
- Browser privacy tools, ad blockers, network failure and JavaScript-disabled visits can reduce measurement.
- Performance values are field observations from supporting browsers and may be absent or zero when a metric has no sample.
- No analytics data will be collected until real IDs are installed, the GTM Google Tag and event tag are configured, and the container is published.
