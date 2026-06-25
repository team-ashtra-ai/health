(() => {
  const concept = {"folder": "13-poise", "number": "13", "name": "Poise", "archetype": "composed editorial authority", "positioning": "Laser, skin and advanced aesthetic care in Londrina, PR", "credential": "CRBM 6277", "location": "Londrina, PR", "domain": "https://www.sofiati.com", "email": "sofiatimendonca@gmail.com", "whatsapp": "(43) 9 9104-3536", "whatsappUrl": "https://wa.me/5543991043536", "instagram": "@fransofiati_biomedica", "instagramUrl": "https://www.instagram.com/fransofiati_biomedica/"};
  const cache = new Map();
  const partialPath = (name) => `partials/${name}.html`;
  const pageFile = () => {
    const key = document.body.dataset.page || "index";
    return key === "index" ? "index.html" : `${key}.html`;
  };
  const pageMeta = () => ({
    page: document.body.dataset.page || "index",
    label: document.body.dataset.pageLabel || "Home",
    title: document.body.dataset.pageTitle || "Franciele Sofiati",
    description: document.body.dataset.pageDescription || concept.positioning,
    canonical: document.body.dataset.canonical || `${concept.domain}/concepts/${concept.folder}/${pageFile()}`,
  });
  const getPartial = async (name) => {
    if (!cache.has(name)) {
      cache.set(name, fetch(partialPath(name), { cache: "no-store" }).then((response) => {
        if (!response.ok) throw new Error(`Missing partial: ${name}`);
        return response.text();
      }));
    }
    return cache.get(name);
  };
  const interpolate = (html) => {
    const meta = pageMeta();
    return html
      .replaceAll("{{TITLE}}", meta.title)
      .replaceAll("{{DESCRIPTION}}", meta.description)
      .replaceAll("{{CANONICAL}}", meta.canonical)
      .replaceAll("{{SCHEMA_JSON}}", JSON.stringify(buildSchema(meta), null, 2));
  };
  const fragmentFrom = (html) => {
    const template = document.createElement("template");
    template.innerHTML = interpolate(html).trim();
    const innerTemplate = template.content.querySelector("template");
    if (innerTemplate) {
      const inner = document.createElement("template");
      inner.innerHTML = innerTemplate.innerHTML.trim();
      return inner.content;
    }
    return template.content;
  };
  const injectHeadPartial = async (name) => {
    const html = await getPartial(name);
    const fragment = fragmentFrom(html);
    [...document.head.querySelectorAll(`[data-dynamic-partial="${name}"]`)].forEach((node) => node.remove());
    if (name === "head") {
      document.head.querySelectorAll('title,meta[name="description"],link[rel="canonical"],meta[property^="og:"],meta[name="theme-color"],link[rel="icon"],link[rel="apple-touch-icon"]').forEach((node) => node.remove());
    }
    [...fragment.children].forEach((node) => {
      node.dataset.dynamicPartial = name;
      document.head.appendChild(node);
    });
  };
  const injectMounts = async (name) => {
    const html = await getPartial(name);
    document.querySelectorAll(`[data-partial-mount="${name}"]`).forEach((mount) => {
      mount.innerHTML = interpolate(html);
      mount.dataset.partialLoaded = "true";
    });
  };
  const applyNavigation = async () => {
    const html = await getPartial("navigation");
    const source = document.createElement("template");
    source.innerHTML = html;
    document.querySelectorAll("[data-navigation-slot]").forEach((slot) => {
      const mode = slot.dataset.navigationSlot || "primary";
      const template = source.content.querySelector(`[data-navigation-template="${mode}"]`) || source.content.querySelector('[data-navigation-template="primary"]');
      slot.innerHTML = template ? template.innerHTML : "";
    });
    const current = pageFile();
    document.querySelectorAll("nav a").forEach((link) => {
      const href = link.getAttribute("href") || "";
      link.removeAttribute("aria-current");
      if (href === current) link.setAttribute("aria-current", "page");
    });
  };
  const buildSchema = (meta) => {
    const url = meta.canonical;
    const base = [
      {
        "@type": "WebSite",
        "@id": `${concept.domain}/#website`,
        "url": concept.domain,
        "name": "Sofiati",
        "inLanguage": "en"
      },
      {
        "@type": "Person",
        "@id": `${concept.domain}/#franciele-sofiati`,
        "name": "Franciele Sofiati",
        "jobTitle": "Advanced Aesthetic Biomedicine",
        "identifier": concept.credential,
        "email": concept.email,
        "sameAs": [concept.instagramUrl],
        "address": {"@type": "PostalAddress", "addressLocality": "Londrina", "addressRegion": "PR", "addressCountry": "BR"}
      },
      {
        "@type": "ProfessionalService",
        "@id": `${concept.domain}/#professional-service`,
        "name": "Franciele Sofiati Advanced Aesthetic Biomedicine",
        "description": "Laser, skin and advanced aesthetic care in Londrina, PR",
        "areaServed": "Londrina, PR",
        "url": concept.domain,
        "telephone": "+5543991043536",
        "email": concept.email,
        "address": {"@type": "PostalAddress", "addressLocality": "Londrina", "addressRegion": "PR", "addressCountry": "BR"}
      },
      {
        "@type": "WebPage",
        "@id": `${url}#webpage`,
        "url": url,
        "name": meta.title,
        "description": meta.description,
        "isPartOf": {"@id": `${concept.domain}/#website`},
        "about": {"@id": `${concept.domain}/#professional-service`},
        "inLanguage": "en"
      },
      {
        "@type": "BreadcrumbList",
        "@id": `${url}#breadcrumb`,
        "itemListElement": [
          {"@type": "ListItem", "position": 1, "name": "Home", "item": `${concept.domain}/concepts/${concept.folder}/index.html`},
          {"@type": "ListItem", "position": 2, "name": meta.label, "item": url}
        ]
      }
    ];
    if (meta.page === "faq") {
      base.push({
        "@type": "FAQPage",
        "@id": `${url}#faq`,
        "mainEntity": [
          {"@type": "Question", "name": "Do results vary?", "acceptedAnswer": {"@type": "Answer", "text": "Results vary according to individual characteristics, evaluation, indication, protocol, sessions and aftercare."}},
          {"@type": "Question", "name": "Can I choose a laser directly?", "acceptedAnswer": {"@type": "Answer", "text": "Laser suitability should be discussed through professional evaluation before treatment selection."}}
        ]
      });
    }
    if (["journal", "blog"].includes(meta.page)) {
      base.push({
        "@type": meta.page === "blog" ? "BlogPosting" : "Article",
        "@id": `${url}#article`,
        "headline": meta.title,
        "description": meta.description,
        "author": {"@id": `${concept.domain}/#franciele-sofiati`},
        "publisher": {"@id": `${concept.domain}/#professional-service`},
        "mainEntityOfPage": {"@id": `${url}#webpage`}
      });
    }
    return {"@context": "https://schema.org", "@graph": base};
  };
  const load = async () => {
    await Promise.all([injectHeadPartial("head"), injectHeadPartial("schema")]);
    await Promise.all([
      injectMounts("status-banner"),
      injectMounts("accessibility"),
      injectMounts("header"),
      injectMounts("mobile-menu"),
      injectMounts("cookie-banner"),
      injectMounts("footer"),
      injectMounts("floating-widgets"),
      injectMounts("consultation-form"),
      injectMounts("contact-card")
    ]);
    await Promise.all([injectMounts("floating-whatsapp"), injectMounts("back-to-top")]);
    await applyNavigation();
    document.body.dataset.partialsReady = "true";
    document.dispatchEvent(new CustomEvent("sofiati:partials-ready", { detail: { concept: concept.folder } }));
  };
  window.SofiatiPartialsReady = load().catch((error) => {
    console.error(error);
    document.body.dataset.partialsReady = "error";
  });
})();
