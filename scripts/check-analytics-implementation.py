#!/usr/bin/env python3
"""Validate the consent-aware analytics implementation and write JSON results."""

from __future__ import annotations

import json
import os
import re
import socket
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
from typing import Any

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "validation" / "analytics.json"
CONFIG = ROOT / "js" / "analytics-config.js"
ANALYTICS = ROOT / "js" / "analytics.js"
CONSENT = ROOT / "js" / "consent-manager.js"
REQUIRED_SCRIPTS = (
    "analytics-config.js",
    "consent-manager.js",
    "analytics.js",
)
REQUIRED_EVENTS = (
    "cta_click",
    "contact_click",
    "social_click",
    "outbound_click",
    "file_download",
    "language_change",
    "form_start",
    "form_submit",
    "form_error",
    "form_success",
    "generate_lead",
    "faq_open",
    "section_view",
    "scroll_depth",
    "engagement_time",
    "field_performance",
    "javascript_error",
    "consent_update",
)
FORM_MAP = {
    "contact-form": ("contact_form", "contact", "contact_enquiry"),
    "consultation-request-form": (
        "consultation_request",
        "consultation",
        "consultation_request",
    ),
    "accessibility-feedback-form": ("accessibility_feedback", "accessibility", None),
}


def public_pages() -> list[Path]:
    pages = list(ROOT.glob("*.html"))
    pages.extend((ROOT / "pt").glob("*.html"))
    pages.extend((ROOT / "journal").glob("*.html"))
    return sorted(pages, key=lambda path: path.relative_to(ROOT).as_posix())


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def node_modules_path() -> str | None:
    configured = os.environ.get("NODE_PATH", "")
    for candidate in configured.split(os.pathsep):
        if candidate and (Path(candidate) / "playwright").is_dir():
            return candidate
    for candidate in Path("/home/code/.npm/_npx").glob("*/node_modules"):
        if (candidate / "playwright").is_dir():
            return str(candidate)
    return None


def syntax_check(path: Path, module: bool = False) -> tuple[bool, str]:
    command = ["node"]
    if module:
        command.extend(["--input-type=module", "--check"])
        result = subprocess.run(
            command,
            input=path.read_text(encoding="utf-8"),
            text=True,
            capture_output=True,
            cwd=ROOT,
        )
    else:
        command.extend(["--check", str(path)])
        result = subprocess.run(command, text=True, capture_output=True, cwd=ROOT)
    return result.returncode == 0, (result.stderr or result.stdout).strip()


def free_port() -> int:
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def browser_audit(routes: list[str]) -> dict[str, Any]:
    node_path = node_modules_path()
    if not node_path:
        return {
            "status": "ERROR",
            "error": "Playwright module not found; browser validation did not run.",
            "tests": [],
        }

    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, format: str, *args: object) -> None:
            return

    port = free_port()
    server = ThreadingHTTPServer(("127.0.0.1", port), QuietHandler)
    Thread(target=server.serve_forever, daemon=True).start()

    runner = r'''
const { chromium } = require("playwright");
const base = process.argv[2];
const routes = JSON.parse(process.argv[3]);
const tests = [];
const failures = [];
const record = (name, passed, detail = {}) => {
  tests.push({name, passed: Boolean(passed), detail});
  if (!passed) failures.push(name);
};
const eventObjects = page => page.evaluate(() =>
  window.dataLayer.filter(value => value && typeof value === "object" && !Array.isArray(value) && value.event)
);
const countEvent = async (page, name) => (await eventObjects(page)).filter(item => item.event === name).length;
const preventNavigation = async locator => locator.evaluate(element =>
  element.addEventListener("click", event => event.preventDefault(), {once: true})
);

(async () => {
  const browser = await chromium.launch({headless: true, args: ["--disable-dev-shm-usage", "--disable-gpu"]});

  // Every route loads with denied consent and no runtime or GTM request.
  {
    const context = await browser.newContext({viewport: {width: 390, height: 844}});
    await context.addInitScript(() => localStorage.setItem(
      "sofiati_cookie_preferences_v3",
      JSON.stringify({essential: true, preferences: false, analytics: false, externalMedia: false})
    ));
    const page = await context.newPage();
    const errors = [];
    let gtmRequests = 0;
    page.on("pageerror", error => errors.push(error.message));
    page.on("request", request => {
      if (request.url().includes("googletagmanager.com/gtm.js")) gtmRequests += 1;
    });
    for (const route of routes) {
      await page.goto(`${base}/${route}`, {waitUntil: "load", timeout: 30000});
      await page.waitForTimeout(80);
    }
    record("all_pages_load_without_javascript_errors", errors.length === 0, {pages: routes.length, errors});
    record("gtm_absent_with_stored_rejection", gtmRequests === 0, {requests: gtmRequests});
    await context.close();
  }

  // Use an intercepted fake syntactically-valid container ID. No Google
  // account or live network request is used during this loader test.
  const context = await browser.newContext({viewport: {width: 1280, height: 900}});
  const page = await context.newPage();
  let fakeGtmRequests = 0;
  let formspreeShouldFail = true;
  await page.route("**/js/analytics-config.js", async route => {
    const response = await route.fetch();
    let body = await response.text();
    body = body
      .replaceAll("GTM-REPLACE_ME", "GTM-TEST123")
      .replace("engagementThresholds: [30, 60, 120]", "engagementThresholds: [1, 2, 3]");
    await route.fulfill({response, body});
  });
  await page.route("https://www.googletagmanager.com/gtm.js**", async route => {
    fakeGtmRequests += 1;
    await route.fulfill({
      status: 200,
      contentType: "application/javascript",
      body: "window.__FRANCIELE_FAKE_GTM_LOADED__ = true;"
    });
  });
  await page.route("https://formspree.io/f/**", async route => {
    if (formspreeShouldFail) {
      formspreeShouldFail = false;
      await route.fulfill({status: 500, contentType: "application/json", body: '{"ok":false}'});
      return;
    }
    await route.fulfill({status: 200, contentType: "application/json", body: '{"ok":true}'});
  });

  await page.goto(`${base}/about.html`, {waitUntil: "load"});
  await page.waitForSelector("[data-cookie-banner]");
  record("gtm_not_loaded_before_choice", fakeGtmRequests === 0, {requests: fakeGtmRequests});
  await page.locator("[data-cookie-reject]").click();
  await page.waitForTimeout(100);
  record("rejection_does_not_load_gtm", fakeGtmRequests === 0, {requests: fakeGtmRequests});
  await page.reload({waitUntil: "load"});
  await page.waitForTimeout(100);
  record("rejection_persists_after_reload", fakeGtmRequests === 0, {requests: fakeGtmRequests});

  await page.evaluate(() => window.SofiatiConsent.open());
  await page.locator("[data-cookie-accept]").click();
  await page.waitForFunction(() => window.__FRANCIELE_FAKE_GTM_LOADED__ === true);
  const consentEvents = await eventObjects(page);
  const consentIndex = consentEvents.findIndex(item => item.event === "consent_update");
  const gtmIndex = consentEvents.findIndex(item => item.event === "gtm.js");
  record("gtm_loads_once_after_grant", fakeGtmRequests === 1, {requests: fakeGtmRequests});
  record("consent_update_precedes_gtm_initialisation", consentIndex >= 0 && gtmIndex > consentIndex, {consentIndex, gtmIndex});
  const advertisingStates = await page.evaluate(() => window.dataLayer
    .filter(item => item && item[0] === "consent")
    .map(item => item[2])
    .filter(Boolean));
  record("advertising_consent_remains_denied",
    advertisingStates.length > 0 && advertisingStates.every(state =>
      state.ad_storage === "denied"
      && state.ad_user_data === "denied"
      && state.ad_personalization === "denied"
    ),
    {states: advertisingStates}
  );
  record("page_context_is_internal_and_once",
    consentEvents.filter(item => item.event === "page_context").length === 1
    && consentEvents.find(item => item.event === "page_context")?.page_name === "about",
    {events: consentEvents.filter(item => item.event === "page_context")}
  );

  const eventTests = [
    ["cta_click", "a[data-track='cta']"],
    ["contact_click", "a[data-track='contact']"],
    ["social_click", "a[data-track='social']"],
    ["outbound_click", "a[data-track='outbound']"],
    ["language_change", "a[data-track='language'][data-lang='pt']"]
  ];
  for (const [eventName, selector] of eventTests) {
    const locator = page.locator(selector).first();
    if (!(await locator.count())) {
      record(`${eventName}_classified_once`, false, {reason: `Missing ${selector}`});
      continue;
    }
    const before = await countEvent(page, eventName);
    await preventNavigation(locator);
    await locator.click();
    const after = await countEvent(page, eventName);
    record(`${eventName}_classified_once`, after - before === 1, {before, after});
  }

  const downloadBefore = await countEvent(page, "file_download");
  await page.evaluate(() => {
    const link = document.createElement("a");
    link.href = "/privacy-guide.pdf";
    link.dataset.track = "download";
    link.textContent = "Privacy guide";
    link.addEventListener("click", event => event.preventDefault(), {once: true});
    document.body.append(link);
    link.click();
    link.remove();
  });
  record("file_download_classified_once",
    await countEvent(page, "file_download") - downloadBefore === 1,
    {before: downloadBefore, after: await countEvent(page, "file_download")}
  );

  const ctaBeforeRevocation = await countEvent(page, "cta_click");
  await page.evaluate(() => window.SofiatiConsent.set(
    {essential: true, preferences: false, analytics: false, externalMedia: false},
    "validation_revoke"
  ));
  const revokedCta = page.locator("a[data-track='cta']").first();
  await preventNavigation(revokedCta);
  await revokedCta.click();
  const ctaAfterRevocation = await countEvent(page, "cta_click");
  await page.evaluate(() => window.SofiatiConsent.set(
    {essential: true, preferences: false, analytics: true, externalMedia: false},
    "validation_regrant"
  ));
  await page.waitForTimeout(100);
  record("revocation_stops_custom_events_without_reloading_gtm",
    ctaBeforeRevocation === ctaAfterRevocation && fakeGtmRequests === 1,
    {before: ctaBeforeRevocation, after: ctaAfterRevocation, gtmRequests: fakeGtmRequests}
  );

  // Engagement uses shortened validation thresholds and proves unfocused time
  // does not advance the counter. Production thresholds remain statically
  // checked at 30/60/120 seconds.
  await page.evaluate(() => { document.hasFocus = () => true; });
  await page.waitForTimeout(1150);
  const engagementOne = await countEvent(page, "engagement_time");
  await page.evaluate(() => { document.hasFocus = () => false; });
  await page.waitForTimeout(1300);
  const engagementPaused = await countEvent(page, "engagement_time");
  await page.evaluate(() => { document.hasFocus = () => true; });
  await page.waitForTimeout(1150);
  const engagementResumed = await countEvent(page, "engagement_time");
  record("engagement_counts_only_focused_visible_time",
    engagementOne === 1 && engagementPaused === 1 && engagementResumed >= 2,
    {engagementOne, engagementPaused, engagementResumed}
  );

  await page.waitForTimeout(2200);
  const performanceEvents = (await eventObjects(page)).filter(item => item.event === "field_performance");
  const performanceValid = performanceEvents.length === 1
    && ["lcp_ms", "cls_score", "inp_ms", "ttfb_ms", "dom_content_loaded_ms", "page_load_ms"]
      .every(key => Number.isFinite(performanceEvents[0][key]) && performanceEvents[0][key] >= 0);
  record("performance_event_is_consolidated_and_numeric", performanceValid, {events: performanceEvents});

  await page.evaluate(() => setTimeout(() => { throw new Error("PRIVATE_SENTINEL_MESSAGE"); }, 0));
  await page.waitForTimeout(100);
  const errorEvents = (await eventObjects(page)).filter(item => item.event === "javascript_error");
  record("javascript_error_is_privacy_safe",
    errorEvents.length === 1
    && !JSON.stringify(errorEvents).includes("PRIVATE_SENTINEL_MESSAGE")
    && Object.keys(errorEvents[0]).every(key => !["message", "stack", "url"].includes(key)),
    {events: errorEvents}
  );

  await page.goto(`${base}/faq.html`, {waitUntil: "load"});
  const firstFaq = page.locator("details[data-track-faq]").first();
  await firstFaq.evaluate(element => { element.open = true; });
  await page.waitForTimeout(50);
  await firstFaq.evaluate(element => { element.open = false; });
  await firstFaq.evaluate(element => { element.open = true; });
  await page.waitForTimeout(50);
  record("faq_open_fires_once_per_item", await countEvent(page, "faq_open") === 1, {
    count: await countEvent(page, "faq_open")
  });

  const section = page.locator("[data-track-section]").nth(1);
  const sectionId = await section.getAttribute("id");
  await section.scrollIntoViewIfNeeded();
  await page.waitForTimeout(950);
  const sectionEvents = (await eventObjects(page)).filter(item =>
    item.event === "section_view" && item.section_id === sectionId
  );
  await section.scrollIntoViewIfNeeded();
  await page.waitForTimeout(950);
  const sectionEventsAfter = (await eventObjects(page)).filter(item =>
    item.event === "section_view" && item.section_id === sectionId
  );
  record("section_view_fires_once_after_minimum_visibility",
    sectionEvents.length === 1 && sectionEventsAfter.length === 1,
    {sectionId, before: sectionEvents.length, after: sectionEventsAfter.length}
  );

  for (const ratio of [0.25, 0.5, 0.75, 0.95, 0.4, 0.95]) {
    await page.evaluate(value => {
      const height = Math.max(document.documentElement.scrollHeight, document.body.scrollHeight);
      document.documentElement.style.scrollBehavior = "auto";
      window.scrollTo(0, Math.max(0, height * value - innerHeight));
    }, ratio);
    await page.waitForTimeout(120);
  }
  const scrollValues = (await eventObjects(page))
    .filter(item => item.event === "scroll_depth")
    .map(item => item.scroll_percent);
  record("scroll_thresholds_fire_once",
    [25, 50, 75, 90].every(value => scrollValues.filter(item => item === value).length === 1),
    {scrollValues}
  );

  await page.goto(`${base}/contact.html`, {waitUntil: "load"});
  await page.waitForSelector("#contact-form[data-analytics-form]");
  const form = page.locator("#contact-form");
  await form.locator("input[name='name']").focus();
  await form.locator("input[name='email']").focus();
  record("form_start_fires_once", await countEvent(page, "form_start") === 1, {
    count: await countEvent(page, "form_start")
  });
  await form.locator("button[type='submit']").click();
  await page.waitForTimeout(100);
  record("invalid_form_has_error_without_submit",
    await countEvent(page, "form_error") === 1
    && await countEvent(page, "form_submit") === 0
    && await countEvent(page, "form_success") === 0,
    {
      error: await countEvent(page, "form_error"),
      submit: await countEvent(page, "form_submit"),
      success: await countEvent(page, "form_success")
    }
  );

  await form.locator("input[name='name']").fill("PII_SENTINEL_NAME");
  await form.locator("input[name='phone']").fill("5511999999999");
  await form.locator("input[name='email']").fill("pii_sentinel@example.com");
  const reason = form.locator("select[name='reason']");
  if (await reason.count()) {
    const value = await reason.locator("option").nth(1).getAttribute("value");
    if (value) await reason.selectOption(value);
  }
  await form.locator("textarea[name='message']").fill("SENSITIVE_HEALTH_SENTINEL test message for form validation.");
  await form.locator("input[name='privacy_acknowledgement']").check();
  await form.locator("button[type='submit']").click();
  await page.waitForFunction(() =>
    window.dataLayer.filter(item => item && item.event === "form_error").length >= 2
  );
  record("server_failure_is_not_form_success",
    await countEvent(page, "form_submit") === 1
    && await countEvent(page, "form_success") === 0
    && await countEvent(page, "generate_lead") === 0,
    {
      submit: await countEvent(page, "form_submit"),
      success: await countEvent(page, "form_success"),
      lead: await countEvent(page, "generate_lead")
    }
  );
  await form.locator("button[type='submit']").click();
  await page.waitForFunction(() =>
    window.dataLayer.some(item => item && item.event === "form_success")
  );
  const formEvents = await eventObjects(page);
  const serializedLayer = await page.evaluate(() => JSON.stringify(window.dataLayer));
  record("confirmed_form_creates_one_lead",
    formEvents.filter(item => item.event === "form_submit").length === 2
    && formEvents.filter(item => item.event === "form_success").length === 1
    && formEvents.filter(item => item.event === "generate_lead").length === 1,
    {
      submit: formEvents.filter(item => item.event === "form_submit").length,
      success: formEvents.filter(item => item.event === "form_success").length,
      lead: formEvents.filter(item => item.event === "generate_lead").length
    }
  );
  record("data_layer_contains_no_form_pii",
    !/PII_SENTINEL|pii_sentinel|5511999999999|SENSITIVE_HEALTH_SENTINEL/i.test(serializedLayer),
    {containsSentinel: /SENTINEL/i.test(serializedLayer)}
  );

  await page.goto(`${base}/thank-you.html`, {waitUntil: "load"});
  await page.waitForTimeout(100);
  const leadAfterSuccess = await countEvent(page, "generate_lead");
  await page.reload({waitUntil: "load"});
  await page.waitForTimeout(100);
  record("thank_you_does_not_duplicate_confirmed_lead",
    leadAfterSuccess === 0 && await countEvent(page, "generate_lead") === 0,
    {firstVisit: leadAfterSuccess, refresh: await countEvent(page, "generate_lead")}
  );

  await page.evaluate(() => sessionStorage.setItem(
    "sofiati_analytics_pending_lead_v1",
    JSON.stringify({
      token: "non-personal-test-token",
      createdAt: Date.now(),
      status: "pending",
      generated: false,
      formName: "contact_form",
      formType: "contact",
      leadType: "contact_enquiry",
      method: "formspree"
    })
  ));
  await page.reload({waitUntil: "load"});
  await page.waitForTimeout(100);
  const fallbackLead = await countEvent(page, "generate_lead");
  await page.reload({waitUntil: "load"});
  await page.waitForTimeout(100);
  record("pending_thank_you_fallback_is_deduplicated",
    fallbackLead === 1 && await countEvent(page, "generate_lead") === 0,
    {firstVisit: fallbackLead, refresh: await countEvent(page, "generate_lead")}
  );

  const directContext = await browser.newContext();
  await directContext.addInitScript(() => localStorage.setItem(
    "sofiati_cookie_preferences_v3",
    JSON.stringify({essential: true, preferences: false, analytics: true, externalMedia: false})
  ));
  const directPage = await directContext.newPage();
  await directPage.goto(`${base}/thank-you.html`, {waitUntil: "load"});
  await directPage.waitForTimeout(100);
  record("direct_thank_you_visit_is_not_a_lead",
    await countEvent(directPage, "generate_lead") === 0,
    {count: await countEvent(directPage, "generate_lead")}
  );
  await directContext.close();

  await context.close();
  await browser.close();
  process.stdout.write(JSON.stringify({
    status: failures.length ? "FAIL" : "PASS",
    tests,
    failures
  }));
})().catch(error => {
  process.stdout.write(JSON.stringify({
    status: "ERROR",
    error: error.stack || String(error),
    tests,
    failures: [...failures, "browser_runner_error"]
  }));
  process.exit(1);
});
'''

    with tempfile.NamedTemporaryFile("w", suffix=".cjs", dir=ROOT, delete=False) as handle:
        handle.write(runner)
        runner_path = Path(handle.name)
    environment = {**os.environ, "NODE_PATH": node_path}
    try:
        result = subprocess.run(
            [
                "node",
                str(runner_path),
                f"http://127.0.0.1:{port}",
                json.dumps(routes),
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            env=environment,
            timeout=180,
        )
    finally:
        runner_path.unlink(missing_ok=True)
        server.shutdown()
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        payload = {
            "status": "ERROR",
            "error": (result.stderr or result.stdout or "No browser output").strip(),
            "tests": [],
        }
    if result.returncode and payload.get("status") != "FAIL":
        payload["status"] = "ERROR"
        payload.setdefault("error", result.stderr.strip())
    return payload


def main() -> int:
    pages = public_pages()
    errors: list[str] = []
    warnings: list[str] = []
    script_records: list[dict[str, Any]] = []
    form_records: list[dict[str, Any]] = []
    ignored_form_records: list[dict[str, Any]] = []
    section_count = 0
    faq_count = 0

    config_source = CONFIG.read_text(encoding="utf-8")
    analytics_source = ANALYTICS.read_text(encoding="utf-8")
    consent_source = CONSENT.read_text(encoding="utf-8")

    for path in pages:
        source = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(source, "html.parser")
        scripts = [
            str(tag.get("src", ""))
            for tag in soup.find_all("script", src=True)
            if any(name in str(tag.get("src", "")) for name in REQUIRED_SCRIPTS)
        ]
        names = [Path(value).name for value in scripts]
        correct_order = names == list(REQUIRED_SCRIPTS)
        if not correct_order:
            errors.append(f"{rel(path)}: analytics scripts missing, duplicated or out of order: {names}")
        if re.search(r"googletagmanager\.com/(?:gtm|gtag)", source, re.I):
            errors.append(f"{rel(path)}: contains a direct Google tag installation")
        script_records.append({
            "page": rel(path),
            "scripts": scripts,
            "count": len(scripts),
            "correctOrder": correct_order,
        })

        for section in soup.find_all("section", id=True):
            identifier = str(section.get("id", ""))
            if (
                section.get("data-pattern") == "hero"
                or identifier.startswith("sf-")
            ):
                continue
            section_count += 1
            if not section.has_attr("data-track-section") or not section.get("data-section-name"):
                errors.append(f"{rel(path)}#{identifier}: meaningful section lacks analytics attributes")

        for index, details in enumerate(soup.find_all("details"), 1):
            if not details.find("summary"):
                continue
            faq_count += 1
            if not details.has_attr("data-track-faq") or not details.get("data-faq-question"):
                errors.append(f"{rel(path)}: FAQ item {index} lacks analytics attributes")

        for form in soup.select("form[data-analytics-form]"):
            form_id = str(form.get("id", ""))
            expected = FORM_MAP.get(form_id)
            if not expected:
                errors.append(f"{rel(path)}: unexpected tracked form {form_id}")
                continue
            name, form_type, lead_type = expected
            protected_fields = form.select("input[data-analytics-sensitive], select[data-analytics-sensitive], textarea[data-analytics-sensitive]")
            fields = form.select("input, select, textarea")
            protected = len(protected_fields) == len(fields)
            flags = (
                form.get("data-gtm-form-interact") == "false"
                and form.get("data-gtm-form-submit") == "false"
                and form.has_attr("data-analytics-sensitive")
            )
            correct = (
                form.get("data-analytics-form") == name
                and form.get("data-form-type") == form_type
                and (form.get("data-lead-type") or None) == lead_type
                and protected
                and flags
            )
            if not correct:
                errors.append(f"{rel(path)}#{form_id}: form analytics/protection attributes are incomplete")
            form_records.append({
                "page": rel(path),
                "id": form_id,
                "formName": name,
                "formType": form_type,
                "leadType": lead_type,
                "fields": len(fields),
                "sensitiveFieldsProtected": len(protected_fields),
                "gtmAutoFormDisabled": flags,
                "passed": correct,
            })

        for form in soup.select("form:not([data-analytics-form])"):
            fields = form.select("input, select, textarea")
            ignored = (
                form.has_attr("data-analytics-ignore")
                and form.has_attr("data-analytics-sensitive")
                and form.get("data-gtm-form-interact") == "false"
                and form.get("data-gtm-form-submit") == "false"
                and all(
                    field.has_attr("data-analytics-sensitive")
                    and field.has_attr("data-analytics-ignore")
                    for field in fields
                )
            )
            if not ignored:
                errors.append(
                    f"{rel(path)}#{form.get('id', 'form')}: untracked form is not explicitly protected"
                )
            ignored_form_records.append({
                "page": rel(path),
                "id": form.get("id"),
                "fields": len(fields),
                "intentionallyIgnored": ignored,
            })

        for link in soup.select("a[href^='mailto:'], a[href^='tel:'], a[href*='wa.me/']"):
            if link.get("data-track") != "contact" or not link.get("data-contact-method"):
                errors.append(f"{rel(path)}: contact link lacks explicit classification")

    for partial in (
        ROOT / "partials" / "cookie-banner.html",
        ROOT / "partials" / "pt-BR" / "cookie-banner.html",
    ):
        soup = BeautifulSoup(partial.read_text(encoding="utf-8"), "html.parser")
        categories = {
            tag.get("data-consent-category")
            for tag in soup.select("[data-consent-category]")
        }
        actions = {
            tag.get("data-consent-action")
            for tag in soup.select("[data-consent-action]")
        }
        if not {"preferences", "analytics", "external-media"} <= categories:
            errors.append(f"{rel(partial)}: consent categories are incomplete")
        if not {"accept-all", "reject-optional", "save"} <= actions:
            errors.append(f"{rel(partial)}: consent actions are incomplete")

    placeholder_status = {
        "gtm": config_source.count('"GTM-REPLACE_ME"') == 1,
        "ga4": config_source.count('"G-REPLACE_ME"') == 1,
        "searchConsole": (
            (ROOT / "index.html").read_text(encoding="utf-8").count(
                "GOOGLE_SITE_VERIFICATION_REPLACE_ME"
            ) == 1
        ),
    }
    if not all(placeholder_status.values()):
        errors.append(f"Placeholder status is incorrect: {placeholder_status}")
    if re.search(r"\bGTM-(?!REPLACE_ME\b)[A-Z0-9]{5,}\b", config_source):
        errors.append("A non-placeholder GTM ID is hard-coded")
    if re.search(r"\bG-(?!REPLACE_ME\b)[A-Z0-9]{5,}\b", config_source):
        errors.append("A non-placeholder GA4 ID is hard-coded")
    if '"basic"' not in config_source:
        errors.append("Basic consent mode is not configured")
    if "engagementThresholds: [30, 60, 120]" not in config_source:
        errors.append("Production engagement thresholds are not 30/60/120 seconds")
    if "scrollThresholds: [25, 50, 75, 90]" not in config_source:
        errors.append("Production scroll thresholds are not 25/50/75/90")

    missing_events = [event for event in REQUIRED_EVENTS if event not in analytics_source]
    if missing_events:
        errors.append(f"Missing implemented events: {missing_events}")
    if "page_context" not in analytics_source:
        errors.append("Internal page_context setup event is missing")
    if "googletagmanager.com/gtag/js" in consent_source:
        errors.append("Consent loader contains a direct GA4 gtag.js installation")

    syntax_files = [
        (ROOT / "js" / "analytics-config.js", False),
        (ROOT / "js" / "consent-manager.js", False),
        (ROOT / "js" / "analytics.js", False),
        (ROOT / "js" / "main.js", True),
        (ROOT / "js" / "components" / "cookie-controls.js", True),
        (ROOT / "js" / "components" / "forms.js", True),
    ]
    syntax_results = []
    for path, module in syntax_files:
        passed, output = syntax_check(path, module)
        syntax_results.append({"file": rel(path), "passed": passed, "output": output})
        if not passed:
            errors.append(f"{rel(path)}: JavaScript syntax failed: {output}")

    sitemap_source = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_ok = (
        "thank-you.html" not in sitemap_source
        and "pt/thank-you.html" not in sitemap_source
    )
    robots_ok = (
        "Sitemap: https://www.francielesofiati.com/sitemap.xml"
        in (ROOT / "robots.txt").read_text(encoding="utf-8")
    )
    thank_noindex = all(
        "noindex, follow" in (ROOT / route).read_text(encoding="utf-8")
        for route in ("thank-you.html", "pt/thank-you.html")
    )
    if not sitemap_ok:
        errors.append("Thank-you route appears in sitemap.xml")
    if not robots_ok:
        errors.append("robots.txt does not reference the production sitemap")
    if not thank_noindex:
        errors.append("A thank-you route is missing noindex, follow")

    installer = subprocess.run(
        [sys.executable, "scripts/install-analytics.py"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    installer_idempotent = (
        installer.returncode == 0 and "updated 0 files" in installer.stdout
    )
    if not installer_idempotent:
        errors.append(
            "Analytics installer is not idempotent: "
            + (installer.stderr or installer.stdout).strip()
        )

    browser = browser_audit([rel(path) for path in pages])
    if browser.get("status") != "PASS":
        errors.append(
            "Browser analytics audit did not pass: "
            + str(browser.get("failures") or browser.get("error"))
        )

    report = {
        "status": "PASS" if not errors else "FAIL",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "pagesChecked": len(pages),
        "scriptsPresent": {
            "required": list(REQUIRED_SCRIPTS),
            "allPagesCorrect": all(record["correctOrder"] for record in script_records),
            "records": script_records,
        },
        "placeholderIdsPresent": placeholder_status,
        "duplicateInstallations": {
            "directGtagImplementations": 0
            if not any("direct Google tag installation" in error for error in errors)
            else 1,
            "duplicateAnalyticsScriptBlocks": sum(
                1 for record in script_records if record["count"] != 3
            ),
            "gtmLoaderGuardImplemented": "gtmRequested" in consent_source
            and "data-franciele-gtm" in consent_source,
        },
        "formsChecked": {
            "count": len(form_records) + len(ignored_form_records),
            "trackedCount": len(form_records),
            "ignoredCount": len(ignored_form_records),
            "records": form_records,
            "intentionallyIgnored": ignored_form_records,
            "sensitiveFieldProtectionPassed": all(
                record["passed"] for record in form_records
            ) and all(record["intentionallyIgnored"] for record in ignored_form_records),
        },
        "trackingAttributes": {
            "meaningfulSections": section_count,
            "faqItems": faq_count,
            "installerIdempotent": installer_idempotent,
        },
        "eventsImplemented": list(REQUIRED_EVENTS),
        "internalEvents": ["page_context"],
        "consentImplementation": {
            "mode": "basic",
            "storageKey": "sofiati_cookie_preferences_v3",
            "gtmLoadsOnlyAfterAnalyticsConsent": True,
            "advertisingConsentAlwaysDenied": True,
            "unconditionalNoscriptIframe": False,
            "browserAudit": browser,
        },
        "javascriptSyntax": {
            "status": "PASS" if all(item["passed"] for item in syntax_results) else "FAIL",
            "files": syntax_results,
        },
        "searchConsolePlaceholder": placeholder_status["searchConsole"],
        "sitemapStatus": {
            "exists": (ROOT / "sitemap.xml").is_file(),
            "thankYouExcluded": sitemap_ok,
        },
        "robotsStatus": {
            "exists": (ROOT / "robots.txt").is_file(),
            "productionSitemapReferenced": robots_ok,
        },
        "thankYouNoindex": thank_noindex,
        "remainingManualSetup": [
            "Create the GA4 property and Web stream; use São Paulo time zone and BRL currency.",
            "Replace G-REPLACE_ME with the real GA4 Measurement ID reference.",
            "Create the GTM Web container and replace GTM-REPLACE_ME.",
            "Create and test the GTM Google Tag, Data Layer Variables, custom-event trigger and GA4 Event tag.",
            "Disable duplicate Enhanced Measurement scroll, outbound, download and form events.",
            "Mark generate_lead as a GA4 key event and create the focused custom dimensions.",
            "Configure internal traffic in Testing mode before activation.",
            "Verify Search Console through DNS, submit sitemap.xml and link Search Console to GA4.",
            "Publish a named GTM container version after Tag Assistant and DebugView testing.",
        ],
        "warnings": warnings,
        "errors": errors,
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(
        f"Analytics validation: {report['status']}; {len(pages)} pages, "
        f"{len(form_records) + len(ignored_form_records)} forms, "
        f"{len(errors)} errors, {len(warnings)} warnings."
    )
    print(f"Report: {REPORT}")
    for error in errors:
        print(f"ERROR: {error}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
