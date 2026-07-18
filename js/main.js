import { closeMenu, initDelegatedEvents, markCurrentLinks, openMenu, prepareMenuInitialState } from './components/navigation.js';
import { initScrollState } from './core/scroll-state.js';
import { initHeaderScroll } from './components/header.js';
import { initFloatingTools } from './components/floating-tools.js';
import { initCookies } from './components/cookie-controls.js';
import { initForms } from './components/forms.js';
import { initTreatmentDirectory } from './components/treatments.js';
import { initFaqSearch } from './pages/faq.js';
import { initBlogSearch } from './pages/blog.js';
import { initFooter } from './components/footer.js';
import { loadPartials } from './partials.js';

let sitePromise = null;

export function initSite() {
  if (sitePromise) return sitePromise;
  sitePromise = loadPartials().then(() => {
    markCurrentLinks();
    prepareMenuInitialState();
    initDelegatedEvents();
    initScrollState();
    initHeaderScroll();
    initFloatingTools();
    initCookies();
    initFooter();
    initForms();
    initFaqSearch();
    initBlogSearch();
    initTreatmentDirectory();
  });
  return sitePromise;
}

function start() {
  initSite().catch((error) => {
    console.error('[Sofiati] Site initialisation failed.', error);
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', start, { once: true });
} else {
  start();
}

window.SofiatiSite = Object.freeze({
  init: initSite,
  openMenu,
  closeMenu,
  version: 'rebuild-foundation-2026-07-13'
});
