import { assetPrefix } from './core/page.js';

const PARTIAL_FILENAMES = Object.freeze({
  topbar: 'top-bar.html',
  header: 'header.html',
  'mobile-menu': 'mobile-menu.html',
  footer: 'footer.html',
  'cookie-banner': 'cookie-banner.html',
  'floating-widgets': 'floating-widgets.html'
});

let loadPromise = null;

function localeDetails() {
  const language = (document.documentElement.lang || 'en').trim().toLowerCase();
  const portuguese = language === 'pt' || language === 'pt-br' || language.startsWith('pt-');
  const prefix = assetPrefix();
  return {
    language: portuguese ? 'pt-BR' : 'en',
    portuguese,
    baseUrl: new URL(`${prefix}${portuguese ? 'partials/pt-BR/' : 'partials/'}`, window.location.href)
  };
}

function pagePairsUrl() {
  return new URL(`${assetPrefix()}data/page-pairs.json`, window.location.href);
}

async function fetchText(name, url) {
  let response;
  try {
    response = await fetch(url, { cache: 'no-cache' });
  } catch (cause) {
    throw new Error(`Unable to load partial "${name}" from ${url.href}: network request failed.`, { cause });
  }
  if (!response.ok) {
    throw new Error(
      `Unable to load partial "${name}" from ${url.href}: HTTP ${response.status} ${response.statusText || 'Unknown status'}.`
    );
  }
  return response.text();
}

async function fetchPagePairs() {
  const url = pagePairsUrl();
  let response;
  try {
    response = await fetch(url, { cache: 'no-cache' });
  } catch (cause) {
    throw new Error(`Unable to load page-pair mapping from ${url.href}: network request failed.`, { cause });
  }
  if (!response.ok) {
    throw new Error(
      `Unable to load page-pair mapping from ${url.href}: HTTP ${response.status} ${response.statusText || 'Unknown status'}.`
    );
  }
  const payload = await response.json();
  if (!Array.isArray(payload.pages)) {
    throw new Error(`Page-pair mapping from ${url.href} does not contain a pages array.`);
  }
  return payload.pages;
}

function currentFilename() {
  const path = decodeURIComponent(window.location.pathname || '').replace(/\/+$/, '');
  if (!path || /\/(?:pt|pt-br|en)$/i.test(path)) return 'index.html';
  const filename = path.split('/').pop() || 'index.html';
  return filename.includes('.') ? filename : `${filename}.html`;
}

function pageKey(value) {
  const filename = (value || '').split('/').pop() || 'index.html';
  return filename.replace(/\.html?$/i, '') || 'index';
}

function currentPagePair(pairs, portuguese) {
  const key = pageKey(currentFilename());
  return pairs.find((pair) => {
    const candidate = portuguese ? pair['pt-BR'] : pair.en;
    return typeof candidate === 'string' && pageKey(candidate) === key;
  });
}

function siteRootPrefix(portuguese) {
  if (portuguese) return '';
  const candidate = document.body?.dataset.siteRoot || '';
  if (/^(?:\.\.\/)*$/.test(candidate)) return candidate;
  return assetPrefix();
}

function isRelativeSitePath(value) {
  return Boolean(value)
    && !value.startsWith('#')
    && !value.startsWith('/')
    && !value.startsWith('?')
    && !/^[a-z][a-z\d+.-]*:/i.test(value)
    && !value.startsWith('../');
}

function prefixNestedEnglishPaths(fragment, portuguese, rootPrefix) {
  if (portuguese || !rootPrefix) return;
  fragment.querySelectorAll('[href], [src], [action]').forEach((element) => {
    ['href', 'src', 'action'].forEach((attribute) => {
      if (!element.hasAttribute(attribute)) return;
      const value = element.getAttribute(attribute).trim();
      if (isRelativeSitePath(value)) element.setAttribute(attribute, `${rootPrefix}${value}`);
    });
  });
}

function setLanguageLinks(fragment, pairs, portuguese, rootPrefix) {
  const pair = currentPagePair(pairs, portuguese);
  if (!pair || typeof pair.en !== 'string' || typeof pair['pt-BR'] !== 'string') {
    throw new Error(`No valid English/Portuguese page-pair mapping exists for ${window.location.pathname}.`);
  }

  fragment.querySelectorAll('a[data-lang]').forEach((link) => {
    const targetLanguage = link.dataset.lang;
    if (targetLanguage === 'en') {
      link.setAttribute('href', portuguese ? `../${pair.en}` : `${rootPrefix}${pair.en}`);
    } else if (targetLanguage === 'pt' || targetLanguage === 'pt-BR') {
      link.setAttribute('href', portuguese ? pair['pt-BR'].split('/').pop() : `${rootPrefix}${pair['pt-BR']}`);
    }
  });
}

function parsePartial(name, source, pairs, portuguese, rootPrefix) {
  const parser = document.createElement('template');
  parser.innerHTML = source;
  const fragment = parser.content;
  Array.from(fragment.childNodes).forEach((node) => {
    if (
      node.nodeType === Node.ELEMENT_NODE
      && node.matches('script[data-id="five-server"][src="/fiveserver.js"]')
    ) {
      node.remove();
    }
  });
  const roots = Array.from(fragment.childNodes).filter((node) => node.nodeType === Node.ELEMENT_NODE);
  if (roots.length !== 1) {
    throw new Error(`Partial "${name}" must contain exactly one root element; found ${roots.length}.`);
  }
  roots.forEach((root) => root.setAttribute('translate', 'no'));
  prefixNestedEnglishPaths(fragment, portuguese, rootPrefix);
  if (name === 'topbar') setLanguageLinks(fragment, pairs, portuguese, rootPrefix);
  return fragment;
}

async function injectPartials() {
  const placeholders = Array.from(document.querySelectorAll('template[data-sf-partial]'));
  if (!placeholders.length) {
    const language = localeDetails().language;
    const detail = Object.freeze({ language, partials: Object.freeze([]) });
    document.dispatchEvent(new CustomEvent('sf:partials-loaded', { detail }));
    return detail;
  }
  const { language, portuguese, baseUrl } = localeDetails();
  const rootPrefix = siteRootPrefix(portuguese);
  const names = [...new Set(placeholders.map((placeholder) => placeholder.dataset.sfPartial))];

  names.forEach((name) => {
    if (!PARTIAL_FILENAMES[name]) {
      throw new Error(`Unknown partial "${name}". Add it to the explicit partial filename map.`);
    }
  });

  const requests = new Map(names.map((name) => {
    const url = new URL(PARTIAL_FILENAMES[name], baseUrl);
    return [name, fetchText(name, url)];
  }));
  const pagePairsPromise = names.includes('topbar') ? fetchPagePairs() : Promise.resolve([]);
  const [pagePairs, sources] = await Promise.all([
    pagePairsPromise,
    Promise.all([...requests.entries()].map(async ([name, request]) => [name, await request]))
  ]);
  const sourceByName = new Map(sources);

  const replacements = placeholders.map((placeholder) => {
    const name = placeholder.dataset.sfPartial;
    const fragment = parsePartial(name, sourceByName.get(name), pagePairs, portuguese, rootPrefix);
    return { placeholder, fragment };
  });
  replacements.forEach(({ placeholder, fragment }) => {
    placeholder.replaceWith(fragment);
  });

  const detail = Object.freeze({ language, partials: Object.freeze([...names]) });
  document.dispatchEvent(new CustomEvent('sf:partials-loaded', { detail }));
  return detail;
}

export function loadPartials() {
  if (!loadPromise) loadPromise = injectPartials();
  return loadPromise;
}
