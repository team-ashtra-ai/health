#!/usr/bin/env node
/* Exercise shared and page-specific interactions without contacting live services. */

const fs = require('fs');
const http = require('http');
const path = require('path');
const { chromium } = require('playwright');

const root = path.resolve(__dirname, '..');
const port = 4176;
const base = `http://127.0.0.1:${port}`;
const englishOnly = ['1', 'true', 'yes'].includes((process.env.SOFIATI_ENGLISH_ONLY || '').toLowerCase());

const inScope = (route) => !englishOnly || !route.startsWith('pt/');

function routes() {
  const english = fs.readdirSync(root, { withFileTypes: true })
    .filter((entry) => entry.isFile() && entry.name.endsWith('.html'))
    .map((entry) => entry.name);
  const journalRoot = path.join(root, 'journal');
  const journal = fs.existsSync(journalRoot)
    ? fs.readdirSync(journalRoot, { withFileTypes: true })
      .filter((entry) => entry.isFile() && entry.name.endsWith('.html'))
      .map((entry) => `journal/${entry.name}`)
    : [];
  const portugueseRoot = path.join(root, 'pt');
  const portuguese = fs.existsSync(portugueseRoot)
    ? fs.readdirSync(portugueseRoot, { withFileTypes: true })
      .filter((entry) => entry.isFile() && entry.name.endsWith('.html'))
      .map((entry) => `pt/${entry.name}`)
    : [];
  return [...english, ...journal, ...portuguese].sort();
}

const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));

function staticServer() {
  return http.createServer((request, response) => {
    const pathname = decodeURIComponent(new URL(request.url, base).pathname);
    const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
    const filename = path.resolve(root, relative);
    if (!filename.startsWith(`${root}${path.sep}`) || !fs.existsSync(filename) || fs.statSync(filename).isDirectory()) {
      response.writeHead(404).end('Not found');
      return;
    }
    const types = { '.css': 'text/css', '.html': 'text/html', '.js': 'text/javascript', '.json': 'application/json', '.svg': 'image/svg+xml', '.webp': 'image/webp', '.png': 'image/png' };
    response.writeHead(200, {
      'Content-Type': types[path.extname(filename)] || 'application/octet-stream',
      'Cache-Control': 'public, max-age=3600',
    });
    fs.createReadStream(filename).pipe(response);
  });
}

async function open(page, route, consent = true) {
  await page.addInitScript(() => {
    window.__sfPartialEvents = 0;
    window.__sfPartialEventDetail = null;
    document.addEventListener('sf:partials-loaded', (event) => {
      window.__sfPartialEvents += 1;
      window.__sfPartialEventDetail = event.detail;
    });
  });
  if (consent) {
    await page.addInitScript(() => localStorage.setItem(
      'sofiati_cookie_preferences_v2',
      JSON.stringify({ essential: true, preferences: false, analytics: false, externalMedia: false })
    ));
  }
  await page.goto(`${base}/${route}`, { waitUntil: 'load' });
  await page.waitForSelector('#sf-header-inline');
  await page.waitForSelector('#sf-footer-inline');
}

async function fillForm(page, selector) {
  const form = page.locator(selector);
  for (const control of await form.locator('input:not([type=hidden]):not(.sf-honeypot), select, textarea').all()) {
    if (await control.isDisabled()) continue;
    const type = await control.getAttribute('type');
    if (type === 'checkbox' || type === 'radio') {
      if (!(await control.isChecked())) await control.check();
    } else if ((await control.evaluate((node) => node.tagName)) === 'SELECT') {
      const value = await control.locator('option:not([disabled])').evaluateAll((options) => {
        return options.map((option) => option.value).find(Boolean) || '';
      });
      if (value) await control.selectOption(value);
    } else if (type === 'email') await control.fill('qa@example.com');
    else if (type === 'tel') await control.fill('+55 43 99999-9999');
    else if (type === 'date') await control.fill('2026-08-15');
    else if (type === 'number') await control.fill('1');
    else await control.fill('Safe local quality-assurance test');
  }
}

(async () => {
  const server = staticServer();
  const failures = [];
  const checks = [];
  let browser;
  const record = (name, passed, detail = '') => {
    checks.push({ name, passed, detail });
    if (!passed) failures.push(`${name}${detail ? `: ${detail}` : ''}`);
  };

  try {
    await new Promise((resolve, reject) => {
      server.once('error', reject);
      server.listen(port, '127.0.0.1', resolve);
    });
    browser = await chromium.launch({
      headless: true,
      // Software-only CI/container environments can repeatedly crash Chromium's
      // Vulkan process while the route loop is opening tabs.
      args: ['--disable-dev-shm-usage', '--disable-gpu'],
    });

    const siteRoutes = routes().filter(inScope);
    for (const width of [390, 1440]) {
      const context = await browser.newContext({ viewport: { width, height: 900 } });
      for (const route of siteRoutes) {
        const page = await context.newPage();
        const errors = [];
        const partialRequests = [];
        page.on('pageerror', (error) => errors.push(error.message));
        page.on('console', (message) => { if (message.type() === 'error') errors.push(message.text()); });
        page.on('response', (response) => {
          if (response.status() >= 400) errors.push(`HTTP ${response.status()}: ${response.url()}`);
        });
        page.on('request', (request) => {
          const pathname = new URL(request.url()).pathname;
          if (pathname.includes('/partials/')) partialRequests.push(pathname);
        });
        try {
          await open(page, route);
          const audit = await page.evaluate(() => ({
            mains: document.querySelectorAll('main').length,
            h1s: document.querySelectorAll('h1').length,
            duplicateIds: [...document.querySelectorAll('[id]')]
              .map((element) => element.id)
              .filter((id, index, ids) => ids.indexOf(id) !== index),
            brokenImages: [...document.images].filter((image) => image.complete && !image.naturalWidth).map((image) => image.src),
            partialCounts: Object.fromEntries([
              'topbar', 'header', 'mobile-menu', 'footer', 'cookie-banner', 'floating-widgets',
            ].map((name) => [name, document.querySelectorAll(`[data-loaded-partial="${name}"]`).length])),
            partialOrder: [...document.querySelectorAll('[data-loaded-partial]')]
              .map((element) => element.dataset.loadedPartial),
            partialRootsAreBodyChildren: [...document.querySelectorAll('[data-loaded-partial]')]
              .every((element) => element.parentElement === document.body),
            remainingPlaceholders: document.querySelectorAll('template[data-sf-partial]').length,
            partialEvents: window.__sfPartialEvents,
            partialEventDetail: window.__sfPartialEventDetail,
            languageLinks: Object.fromEntries(
              [...document.querySelectorAll('#sf-topbar-inline a[data-lang]')]
                .map((link) => [link.dataset.lang, link.getAttribute('href')])
            ),
            activeNavigationValid: (() => {
              const pageName = document.body.dataset.page;
              const candidates = [...document.querySelectorAll(`a[data-page="${pageName}"]`)];
              return candidates.every((link) => link.getAttribute('aria-current') === 'page')
                && [...document.querySelectorAll('a[data-page][aria-current="page"]')]
                  .every((link) => link.dataset.page === pageName);
            })(),
            whatsappLinks: [...document.querySelectorAll('#sf-floating-inline a[href]')]
              .map((link) => link.getAttribute('href')),
            backToTopCount: document.querySelectorAll('#sf-floating-inline [data-scroll-top]').length,
          }));
          const filename = route.split('/').pop() || 'index.html';
          const portuguese = route.startsWith('pt/');
          const journalArticle = route.startsWith('journal/');
          const expectedLanguageLinks = journalArticle
            ? { en: `../${route}`, pt: '../pt/journal.html' }
            : {
              en: portuguese ? `../${filename}` : filename,
              pt: portuguese ? filename : `pt/${filename}`,
            };
          const expectedPartialPath = portuguese ? '/partials/pt-BR/' : '/partials/';
          const expectedPartialOrder = route.endsWith('contact.html')
            ? 'topbar,header,mobile-menu,cookie-banner,floating-widgets,footer'
            : 'topbar,header,mobile-menu,footer,cookie-banner,floating-widgets';
          const passed = audit.mains === 1
            && audit.h1s === 1
            && !audit.duplicateIds.length
            && !audit.brokenImages.length
            && Object.values(audit.partialCounts).every((count) => count === 1)
            && audit.partialOrder.join(',') === expectedPartialOrder
            && audit.partialRootsAreBodyChildren
            && audit.remainingPlaceholders === 0
            && audit.partialEvents === 1
            && audit.partialEventDetail?.partials?.length === 6
            && audit.languageLinks.en === expectedLanguageLinks.en
            && audit.languageLinks.pt === expectedLanguageLinks.pt
            && audit.activeNavigationValid
            && audit.whatsappLinks.length === 1
            && audit.whatsappLinks[0] === 'https://wa.me/5543991043536'
            && audit.backToTopCount === 1
            && partialRequests.length === 6
            && partialRequests.every((pathname) => pathname.includes(expectedPartialPath))
            && !errors.length;
          record(`${route} @ ${width}px`, passed, JSON.stringify({ ...audit, partialRequests, errors }));
        } catch (error) {
          record(`${route} @ ${width}px`, false, error.message);
        } finally {
          await page.close();
        }
      }
      await context.close();
    }

    for (const route of ['index.html', 'pt/index.html'].filter(inScope)) {
      const page = await browser.newPage({ viewport: { width: 390, height: 844 } });
      await open(page, route);
      const trigger = page.locator('[data-sf-mobile-open], .sfi-menu-button').first();
      await trigger.click();
      const menu = page.locator('#sf-mobile-menu-inline');
      const opened = await menu.getAttribute('aria-hidden') === 'false' && await trigger.getAttribute('aria-expanded') === 'true';
      const focusInside = await page.evaluate(() => !!document.activeElement?.closest('#sf-mobile-menu-inline'));
      const focusables = page.locator(
        '#sf-mobile-menu-inline [role="dialog"] a[href]:visible, '
        + '#sf-mobile-menu-inline [role="dialog"] button:not([disabled]):visible, '
        + '#sf-mobile-menu-inline [role="dialog"] [tabindex]:not([tabindex="-1"]):visible',
      );
      const firstFocusable = focusables.first();
      const lastFocusable = focusables.last();
      await firstFocusable.focus();
      await page.keyboard.press('Shift+Tab');
      const wrappedBackward = await lastFocusable.evaluate((element) => element === document.activeElement);
      await page.keyboard.press('Tab');
      const wrappedForward = await firstFocusable.evaluate((element) => element === document.activeElement);
      await page.keyboard.press('Escape');
      await page.waitForTimeout(60);
      const closed = await menu.getAttribute('aria-hidden') === 'true' && await trigger.getAttribute('aria-expanded') === 'false';
      const focusReturned = await trigger.evaluate((element) => element === document.activeElement);
      record(
        `${route} mobile menu`,
        opened && focusInside && wrappedBackward && wrappedForward && closed && focusReturned,
        JSON.stringify({ opened, focusInside, wrappedBackward, wrappedForward, closed, focusReturned }),
      );
      await page.close();
    }

    for (const route of ['index.html', 'pt/index.html'].filter(inScope)) {
      const page = await browser.newPage({ viewport: { width: 390, height: 844 }, reducedMotion: 'reduce' });
      await open(page, route);
      await page.evaluate(() => window.scrollTo(0, 900));
      await page.waitForFunction(() => document.querySelector('[data-scroll-top]')?.classList.contains('is-visible'));
      const button = page.locator('[data-scroll-top]').first();
      await button.click();
      await page.waitForFunction(() => window.scrollY < 2);
      const label = await button.getAttribute('aria-label');
      const expectedLabel = route.startsWith('pt/') ? 'Voltar ao topo' : 'Back to top';
      record(`${route} back to top`, label === expectedLabel && await page.evaluate(() => window.scrollY < 2));
      await page.close();
    }

    {
      const context = await browser.newContext({ viewport: { width: 390, height: 844 } });
      const page = await context.newPage();
      await page.goto(`${base}/index.html`, { waitUntil: 'load' });
      await page.waitForSelector('#sf-cookie-inline');
      const banner = page.locator('#sf-cookie-inline');
      const visible = await banner.isVisible();
      await banner.locator('[data-cookie-customize]').click();
      const preferencesVisible = await banner.locator('[data-cookie-preferences]').isVisible();
      await banner.locator('input[name="analytics"]').check();
      await banner.locator('[data-cookie-save]').click();
      const savedAnalytics = await page.evaluate(() => JSON.parse(localStorage.getItem('sofiati_cookie_preferences_v3')).analytics);
      await page.evaluate(() => window.SofiatiConsent.open());
      await banner.locator('[data-cookie-reject], [data-cookie-decline]').first().click();
      const rejected = await page.evaluate(() => {
        const value = JSON.parse(localStorage.getItem('sofiati_cookie_preferences_v3'));
        return value && !value.preferences && !value.analytics && !value.externalMedia;
      });
      record(
        'cookie banner customise/save/reject',
        visible && preferencesVisible && savedAnalytics && rejected && !(await banner.isVisible()),
      );
      await context.close();
    }

    for (const route of ['faq.html', 'pt/faq.html'].filter(inScope)) {
      const page = await browser.newPage();
      await open(page, route);
      const search = page.locator('[data-faq-search]');
      if (await search.count()) {
        await search.fill('zzzz-no-match');
        const hidden = await page.locator('.sf-faq-accordion details, .sf-faq-card').evaluateAll((items) => items.every((item) => item.hidden));
        record(`${route} FAQ filter`, hidden);
      } else record(`${route} FAQ filter`, false, 'search control missing');
      await page.close();
    }

    for (const route of ['blog.html', 'pt/blog.html'].filter(inScope)) {
      const page = await browser.newPage();
      await open(page, route);
      const search = page.locator('[data-blog-search] input[type=search]');
      if (await search.count()) {
        await search.fill('zzzz-no-match');
        record(`${route} blog filter`, await page.locator('[data-search-empty]').isVisible());
      } else {
        const topics = await page.locator('#browse-by-topic .sf-content-card').count();
        const linkedTopics = await page.locator('#browse-by-topic a.sf-content-card').count();
        record(`${route} curated topic gateway`, topics === 6 && linkedTopics >= 2, JSON.stringify({ topics, linkedTopics }));
      }
      await page.close();
    }

    for (const route of ['treatments.html', 'pt/treatments.html'].filter(inScope)) {
      const page = await browser.newPage();
      await open(page, route);
      const entries = page.locator('[data-treatment-entry]');
      const total = await entries.count();
      await page.locator('[data-treatment-facet="concern"]').selectOption('superficial-vessels');
      await page.locator('[data-treatment-facet="technology"]').selectOption('ultrasound-energy');
      const visibleAfterFilter = await entries.evaluateAll((items) => items.filter((item) => !item.hidden).length);
      const hiddenSections = await page.locator('[data-treatment-filterable][hidden]').count();
      await page.locator('[data-treatment-reset]').click();
      const visibleAfterReset = await entries.evaluateAll((items) => items.filter((item) => !item.hidden).length);
      const categoryNav = await page.locator('[data-treatment-category-nav] [data-treatment-category-link]').count();
      record(
        `${route} treatment facets`,
        total >= 20 && visibleAfterFilter === 0 && hiddenSections > 0 && visibleAfterReset === total && categoryNav === 8,
        JSON.stringify({ total, visibleAfterFilter, hiddenSections, visibleAfterReset, categoryNav }),
      );
      await page.close();
    }

    for (const route of [
      'accessibility.html', 'contact.html', 'consultation.html',
      'pt/accessibility.html', 'pt/contact.html', 'pt/consultation.html',
    ].filter(inScope)) {
      const page = await browser.newPage();
      await page.route('https://formspree.io/**', (request) => request.fulfill({ status: 200, contentType: 'application/json', body: '{"ok":true}' }));
      await open(page, route);
      const form = page.locator('form.sf-form, form[data-enhanced-form], form[data-consultation-form]').first();
      await form.locator('button[type=submit], input[type=submit]').click();
      record(`${route} invalid form state`, await form.locator('[aria-invalid=true]').count() > 0);
      await fillForm(page, 'form.sf-form, form[data-enhanced-form], form[data-consultation-form]');
      await form.locator('button[type=submit], input[type=submit]').click();
      await page.waitForFunction(() => document.querySelector('form[data-form-state="success"]'));
      record(`${route} intercepted success state`, await form.getAttribute('data-form-state') === 'success');
      await page.close();
    }

    const report = { generatedAt: new Date().toISOString(), routeCount: siteRoutes.length, englishOnly, checks, failures };
    fs.mkdirSync(path.join(root, 'qa'), { recursive: true });
    fs.writeFileSync(path.join(root, 'qa', 'interaction-audit.json'), JSON.stringify(report, null, 2));
    console.log(`Interaction audit: ${checks.length} checks, ${failures.length} failures.`);
    failures.slice(0, 30).forEach((failure) => console.log(`- ${failure}`));
    process.exitCode = failures.length ? 1 : 0;
  } finally {
    if (browser) await browser.close();
    await new Promise((resolve) => server.close(resolve));
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
