#!/usr/bin/env node
import fs from "node:fs";
import net from "node:net";
import path from "node:path";
import { spawn } from "node:child_process";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const root = process.cwd();
const conceptsRoot = path.join(root, "concepts");
const docsRoot = path.join(root, "docs", "script-runs");
const viewports = [1440, 1024, 768, 360];
const mainLabels = ["Home", "About", "Care", "Laser", "Skin", "Results", "Journal", "Contact"];
const footerLabels = [
  "Home",
  "About",
  "Care",
  "Laser",
  "Skin",
  "Results",
  "Journal",
  "Contact",
  "Consultation",
  "Values",
  "Mission",
  "Testimonials",
  "FAQ",
  "Privacy",
  "Cookies",
  "Accessibility",
  "Sitemap",
];

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function conceptDirs() {
  return fs
    .readdirSync(conceptsRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && /^\d{2}-/.test(entry.name))
    .map((entry) => entry.name)
    .sort();
}

function pageList() {
  const pages = [];
  for (const concept of conceptDirs()) {
    const dir = path.join(conceptsRoot, concept);
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (entry.isFile() && entry.name.endsWith(".html") && !entry.name.includes(".bak")) {
        pages.push(`concepts/${concept}/${entry.name}`);
      }
    }
  }
  return pages.sort();
}

function freePort(start = 8120) {
  return new Promise((resolve, reject) => {
    const tryPort = (port) => {
      if (port > start + 120) {
        reject(new Error("No free local port found"));
        return;
      }
      const server = net.createServer();
      server.once("error", () => tryPort(port + 1));
      server.once("listening", () => {
        server.close(() => resolve(port));
      });
      server.listen(port, "127.0.0.1");
    };
    tryPort(start);
  });
}

async function runPool(items, workerCount, worker) {
  const results = new Array(items.length);
  let next = 0;
  async function loop() {
    while (next < items.length) {
      const index = next;
      next += 1;
      results[index] = await worker(items[index], index);
    }
  }
  await Promise.all(Array.from({ length: workerCount }, loop));
  return results;
}

function sameLabels(actual, expected) {
  return actual.length === expected.length && actual.every((label, index) => label === expected[index]);
}

async function checkPage(context, rel, width, port) {
  const page = await context.newPage();
  const failures = [];
  const failedRequests = [];
  const consoleErrors = [];
  page.on("requestfailed", (request) => failedRequests.push(request.url()));
  page.on("response", (response) => {
    if (response.status() >= 400) failedRequests.push(`${response.status()} ${response.url()}`);
  });
  page.on("console", (message) => {
    if (message.type() === "error") consoleErrors.push(message.text());
  });

  try {
    await page.goto(`http://127.0.0.1:${port}/${rel}`, {
      waitUntil: "domcontentloaded",
      timeout: 14000,
    });
    await page.waitForFunction(
      () => {
        const names = ["header", "mobile-menu", "footer", "cookie-banner", "floating-widgets"];
        return names.every(
          (name) => document.querySelector(`[data-sofiati-partial="${name}"]`)?.dataset.partialLoaded === "true",
        );
      },
      null,
      { timeout: 7000 },
    );
    await page.waitForTimeout(80);

    const metrics = await page.evaluate(
      ({ width, mainLabels, footerLabels }) => {
        const textOf = (el) => (el?.textContent || "").replace(/\s+/g, " ").trim();
        const visible = (el) => {
          if (!el) return false;
          const style = getComputedStyle(el);
          const rect = el.getBoundingClientRect();
          return (
            style.display !== "none" &&
            style.visibility !== "hidden" &&
            Number(style.opacity || 1) > 0.01 &&
            rect.width > 0 &&
            rect.height > 0
          );
        };
        const labels = (selector) =>
          [...document.querySelectorAll(selector)].map((el) =>
            textOf(el).replace(/^\d{2}\s*/, ""),
          );
        const images = [...document.images].filter((img) => {
          const rect = img.getBoundingClientRect();
          const style = getComputedStyle(img);
          return (
            rect.width > 4 &&
            rect.height > 4 &&
            rect.bottom >= 0 &&
            rect.top <= window.innerHeight &&
            style.display !== "none" &&
            style.visibility !== "hidden"
          );
        });
        const activeNav = [...document.querySelectorAll("a[aria-current='page']")].length > 0;
        const textFits = [
          ...document.querySelectorAll(
            ".sf-public-header a, .sf-public-header button, .sf-mobile-menu a, .sf-mobile-menu button, .sf-public-footer a, .sf-cookie-banner button, .sf-cookie-banner a",
          ),
        ].every((el) => el.scrollWidth <= el.clientWidth + 4 || getComputedStyle(el).whiteSpace !== "nowrap");
        return {
          headerMounts: document.querySelectorAll("[data-sofiati-partial='header']").length,
          footerMounts: document.querySelectorAll("[data-sofiati-partial='footer']").length,
          cookieMounts: document.querySelectorAll("[data-sofiati-partial='cookie-banner']").length,
          floatingMounts: document.querySelectorAll("[data-sofiati-partial='floating-widgets']").length,
          headerVisible: visible(document.querySelector(".sf-public-header")),
          footerVisible: visible(document.querySelector(".sf-public-footer")),
          cookieVisible: visible(document.querySelector(".sf-cookie-banner")),
          whatsappCount: document.querySelectorAll(".sf-floating-whatsapp").length,
          backTopCount: document.querySelectorAll(".sf-back-to-top").length,
          desktopLabels: labels(".sf-desktop-nav [data-main-nav='true']"),
          mobileLabels: labels(".sf-mobile-nav [data-main-nav='true']"),
          footerLabels: labels(".sf-footer-sitemap [data-footer-link='true']"),
          desktopVisibleCount: [...document.querySelectorAll(".sf-desktop-nav [data-main-nav='true']")].filter(visible)
            .length,
          menuButtonVisible: visible(document.querySelector("[data-menu-toggle]")),
          activeNav,
          languageOk:
            document.querySelector("[data-lang-switch='en']")?.getAttribute("href")?.includes("lang=en") &&
            document.querySelector("[data-lang-switch='pt-BR']")?.getAttribute("href")?.includes("lang=pt-BR"),
          cookieControls: [
            "data-cookie-accept",
            "data-cookie-reject",
            "data-cookie-customize",
            "data-cookie-save",
            "data-cookie-preferences",
          ].every((attr) => document.querySelector(`[${attr}]`)),
          overflow: document.documentElement.scrollWidth > window.innerWidth + 2,
          textFits,
          h1Count: document.querySelectorAll("main h1").length,
          h1Visible: visible(document.querySelector("main h1")),
          imagesLoaded: images.every((img) => img.complete && img.naturalWidth > 0),
          logoCount: document.querySelectorAll(".sf-logo-img").length,
          modeOk:
            width >= 1440
              ? [...document.querySelectorAll(".sf-desktop-nav [data-main-nav='true']")].filter(visible).length === 8
              : visible(document.querySelector("[data-menu-toggle]")) &&
                [...document.querySelectorAll(".sf-desktop-nav [data-main-nav='true']")].filter(visible).length === 0,
          expectedMainCount: mainLabels.length,
          expectedFooterCount: footerLabels.length,
        };
      },
      { width, mainLabels, footerLabels },
    );

    if (metrics.headerMounts !== 1) failures.push("header mount count");
    if (metrics.footerMounts !== 1) failures.push("footer mount count");
    if (metrics.cookieMounts !== 1) failures.push("cookie mount count");
    if (metrics.floatingMounts !== 1) failures.push("floating mount count");
    if (!metrics.headerVisible) failures.push("header hidden");
    if (!metrics.footerVisible) failures.push("footer hidden");
    if (!metrics.cookieVisible) failures.push("cookie hidden");
    if (metrics.whatsappCount !== 1 || metrics.backTopCount !== 1) failures.push("floating button count");
    if (!sameLabels(metrics.desktopLabels, mainLabels)) failures.push("desktop nav labels");
    if (!sameLabels(metrics.mobileLabels, mainLabels)) failures.push("mobile nav labels");
    if (!sameLabels(metrics.footerLabels, footerLabels)) failures.push("footer labels");
    if (!metrics.activeNav) failures.push("active nav");
    if (!metrics.languageOk) failures.push("language links");
    if (!metrics.cookieControls) failures.push("cookie controls");
    if (metrics.overflow) failures.push("horizontal overflow");
    if (!metrics.textFits) failures.push("text clipping");
    if (metrics.h1Count !== 1 || !metrics.h1Visible) failures.push("h1");
    if (!metrics.imagesLoaded || metrics.logoCount < 3) failures.push("visible images/logos");
    if (!metrics.modeOk) failures.push("responsive header mode");

    if (width <= 1024) {
      await page.evaluate(() => window.scrollTo(0, 0));
      await page.click("[data-menu-toggle]");
      await page.waitForTimeout(120);
      const menu = await page.evaluate(() => {
        const dialog = document.querySelector(".sf-mobile-dialog");
        const rect = dialog?.getBoundingClientRect();
        return {
          open: document.querySelector("#mobile-menu")?.getAttribute("aria-hidden") === "false",
          expanded: document.querySelector("[data-menu-toggle]")?.getAttribute("aria-expanded") === "true",
          fits: rect ? rect.width <= window.innerWidth + 2 && rect.height <= window.innerHeight + 2 : false,
          overflow: document.documentElement.scrollWidth > window.innerWidth + 2,
        };
      });
      if (!menu.open || !menu.expanded || !menu.fits || menu.overflow) failures.push("mobile menu behavior");
    }

    await page.evaluate(() => window.scrollTo(0, document.documentElement.scrollHeight));
    await page.waitForTimeout(40);
    const footerOverlap = await page.evaluate(() => {
      const floating = document.querySelector(".sf-floating-tools")?.getBoundingClientRect();
      if (!floating) return true;
      return [...document.querySelectorAll(".sf-footer-sitemap a, .sf-footer-cta, .sf-footer-close p")].some(
        (target) => {
          const rect = target.getBoundingClientRect();
          return !(
            floating.right <= rect.left ||
            rect.right <= floating.left ||
            floating.bottom <= rect.top ||
            rect.bottom <= floating.top
          );
        },
      );
    });
    if (footerOverlap) failures.push("floating overlaps footer");

    if (failedRequests.length) failures.push("failed requests");
    if (consoleErrors.length) failures.push("console errors");
  } catch (error) {
    failures.push(error.message || String(error));
  } finally {
    await page.close().catch(() => {});
  }

  return {
    page: rel,
    width,
    status: failures.length ? "FAIL" : "PASS",
    failures,
    failedRequests: failedRequests.slice(0, 5),
    consoleErrors: consoleErrors.slice(0, 5),
  };
}

async function checkCookieBehavior(browser, concepts, port) {
  const results = [];
  for (const concept of concepts) {
    const context = await browser.newContext({ viewport: { width: 390, height: 900 }, deviceScaleFactor: 1 });
    const page = await context.newPage();
    const failures = [];
    try {
      await page.goto(`http://127.0.0.1:${port}/concepts/${concept}/index.html`, {
        waitUntil: "domcontentloaded",
        timeout: 14000,
      });
      await page.waitForFunction(
        () => document.querySelector("[data-sofiati-partial='cookie-banner']")?.dataset.partialLoaded === "true",
        null,
        { timeout: 7000 },
      );
      await page.evaluate((conceptId) => localStorage.removeItem(`sofiati-cookie-${conceptId}`), concept);
      await page.reload({ waitUntil: "domcontentloaded", timeout: 14000 });
      await page.waitForFunction(
        () => document.querySelector("[data-sofiati-partial='cookie-banner']")?.dataset.partialLoaded === "true",
        null,
        { timeout: 7000 },
      );
      await page.click("[data-cookie-customize]");
      const prefsOpen = await page.locator("[data-cookie-preferences]").isVisible();
      if (!prefsOpen) failures.push("preferences panel did not open");
      await page.click("[data-cookie-save]");
      const saved = await page.evaluate((conceptId) => localStorage.getItem(`sofiati-cookie-${conceptId}`), concept);
      if (!saved || !saved.includes("custom")) failures.push("custom consent not saved");
      await page.evaluate((conceptId) => localStorage.removeItem(`sofiati-cookie-${conceptId}`), concept);
      await page.reload({ waitUntil: "domcontentloaded", timeout: 14000 });
      await page.waitForFunction(
        () => document.querySelector("[data-sofiati-partial='cookie-banner']")?.dataset.partialLoaded === "true",
        null,
        { timeout: 7000 },
      );
      await page.click("[data-cookie-reject]");
      const rejected = await page.evaluate((conceptId) => localStorage.getItem(`sofiati-cookie-${conceptId}`), concept);
      if (!rejected || !rejected.includes("rejected")) failures.push("reject consent not saved");
      await page.evaluate((conceptId) => localStorage.removeItem(`sofiati-cookie-${conceptId}`), concept);
      await page.reload({ waitUntil: "domcontentloaded", timeout: 14000 });
      await page.waitForFunction(
        () => document.querySelector("[data-sofiati-partial='cookie-banner']")?.dataset.partialLoaded === "true",
        null,
        { timeout: 7000 },
      );
      await page.click("[data-cookie-accept]");
      const accepted = await page.evaluate((conceptId) => localStorage.getItem(`sofiati-cookie-${conceptId}`), concept);
      if (!accepted || !accepted.includes("accepted")) failures.push("accept consent not saved");
    } catch (error) {
      failures.push(error.message || String(error));
    } finally {
      await context.close().catch(() => {});
    }
    results.push({ concept, status: failures.length ? "FAIL" : "PASS", failures });
  }
  return results;
}

async function main() {
  fs.mkdirSync(docsRoot, { recursive: true });
  const concepts = conceptDirs();
  const pages = pageList();
  const port = await freePort();
  const server = spawn("python3", ["-m", "http.server", String(port), "--bind", "127.0.0.1"], {
    cwd: root,
    stdio: "ignore",
  });
  await sleep(700);
  const browser = await chromium.launch({ headless: true });
  const rendered = [];
  try {
    for (const width of viewports) {
      const context = await browser.newContext({ viewport: { width, height: 980 }, deviceScaleFactor: 1 });
      const rows = await runPool(pages, 8, (rel) => checkPage(context, rel, width, port));
      await context.close();
      rendered.push(...rows);
    }
    const cookies = await checkCookieBehavior(browser, concepts, port);
    const renderedFailures = rendered.filter((row) => row.failures.length);
    const cookieFailures = cookies.filter((row) => row.failures.length);
    const summary = {
      generatedAt: new Date().toISOString(),
      pages: pages.length,
      viewports,
      renderedChecks: rendered.length,
      renderedFailures: renderedFailures.length,
      cookieConceptChecks: cookies.length,
      cookieFailures: cookieFailures.length,
      failures: renderedFailures,
      cookieResults: cookies,
    };
    fs.writeFileSync(
      path.join(docsRoot, "sofiati-render-matrix.json"),
      `${JSON.stringify(summary, null, 2)}\n`,
    );
    const lines = [
      "# Sofiati Render Matrix",
      "",
      `- Pages: ${pages.length}`,
      `- Viewports: ${viewports.join(", ")}`,
      `- Rendered checks: ${rendered.length}`,
      `- Rendered failures: ${renderedFailures.length}`,
      `- Cookie concept checks: ${cookies.length}`,
      `- Cookie failures: ${cookieFailures.length}`,
      "",
    ];
    if (renderedFailures.length) {
      lines.push("## Rendered Failures", "");
      for (const row of renderedFailures.slice(0, 200)) {
        lines.push(`- ${row.page} @ ${row.width}px: ${row.failures.join("; ")}`);
      }
      if (renderedFailures.length > 200) lines.push(`- ... ${renderedFailures.length - 200} more`);
      lines.push("");
    }
    if (cookieFailures.length) {
      lines.push("## Cookie Failures", "");
      for (const row of cookieFailures) {
        lines.push(`- ${row.concept}: ${row.failures.join("; ")}`);
      }
      lines.push("");
    }
    fs.writeFileSync(path.join(docsRoot, "sofiati-render-matrix.md"), `${lines.join("\n").trim()}\n`);
    console.log(
      `Sofiati render matrix: pages=${pages.length} rendered=${rendered.length} rendered_failures=${renderedFailures.length} cookie_failures=${cookieFailures.length}`,
    );
    process.exitCode = renderedFailures.length || cookieFailures.length ? 1 : 0;
  } finally {
    await browser.close().catch(() => {});
    server.kill();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
