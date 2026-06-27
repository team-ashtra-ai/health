import fs from "node:fs/promises";
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

export const BRAND_TOKENS = {
  "--sofiati-sage": "#A2AEA0",
  "--sofiati-sage-deep": "#485041",
  "--sofiati-ivory": "#F2EEE3",
  "--sofiati-cream": "#F8F7F2",
  "--sofiati-bronze": "#9A6B35",
  "--sofiati-gold": "#CDAA78",
  "--sofiati-ink": "#252321",
  "--sofiati-serif": "Georgia, \"Times New Roman\", serif",
  "--sofiati-sans": "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif",
  "--sofiati-label-spacing": "0.12em"
};

export const REQUIRED_PAGE_KEYS = [
  "home",
  "about",
  "care",
  "laser",
  "skin",
  "results",
  "consultation",
  "contact",
  "mission",
  "values",
  "testimonials",
  "faq",
  "journal",
  "blog",
  "legal",
  "privacy",
  "cookies",
  "accessibility",
  "sitemap",
  "404",
  "thank-you"
];

const PAGE_META = {
  home: { label: "Home", file: "index.html", imageKey: "home", support: false },
  about: { label: "About", file: "about.html", imageKey: "about", support: false },
  care: { label: "Care", file: "care.html", imageKey: "care", support: false },
  laser: { label: "Laser", file: "laser.html", imageKey: "laser", support: false },
  skin: { label: "Skin", file: "skin.html", imageKey: "skin", support: false },
  results: { label: "Results", file: "results.html", imageKey: "results", support: false },
  consultation: { label: "Consultation", file: "consultation.html", imageKey: "consultation", support: false },
  contact: { label: "Contact", file: "contact.html", imageKey: "contact", support: false },
  mission: { label: "Mission", file: "mission.html", imageKey: "mission", support: false },
  values: { label: "Values", file: "values.html", imageKey: "values", support: false },
  testimonials: { label: "Testimonials", file: "testimonials.html", imageKey: "testimonials", support: false },
  faq: { label: "FAQ", file: "faq.html", imageKey: "faq", support: false },
  journal: { label: "Journal", file: "journal.html", imageKey: "journal", support: false },
  blog: { label: "Blog", file: "blog.html", imageKey: "blog", support: false },
  legal: { label: "Legal", file: "legal.html", imageKey: "legal", support: true },
  privacy: { label: "Privacy", file: "privacy.html", imageKey: "legal", support: true },
  cookies: { label: "Cookies", file: "cookies.html", imageKey: "legal", support: true },
  accessibility: { label: "Accessibility", file: "accessibility.html", imageKey: "legal", support: true },
  sitemap: { label: "Sitemap", file: "sitemap.html", imageKey: "generated", support: true },
  "404": { label: "404", file: "404.html", imageKey: "generated", support: true },
  "thank-you": { label: "Thank You", file: "thank-you.html", imageKey: "generated", support: true }
};

const IMAGE_FILES = {
  home: "assets/images/home/sofiati-home-hero-botanical-clinical-luxury.webp",
  about: "assets/images/about/franciele-sofiati-brand-story-botanical-moodboard.webp",
  care: "assets/images/care/sofiati-care-botanical-clinical-brand-application.webp",
  laser: "assets/images/laser/sofiati-laser-botanical-precision-story-background.webp",
  skin: "assets/images/skin/sofiati-skin-care-soft-sage-story-background.webp",
  results: "assets/images/results/sofiati-results-ethical-expectations-botanical.webp",
  consultation: "assets/images/consultation/sofiati-consultation-stationery-care-pathway.webp",
  contact: "assets/images/contact/sofiati-contact-business-card-inspired-layout.webp",
  mission: "assets/images/mission/sofiati-mission-science-care-naturalness.webp",
  values: "assets/images/values/sofiati-values-care-confidence-safety-naturalness.webp",
  testimonials: "assets/images/testimonials/sofiati-testimonials-approval-first-contact-card.webp",
  faq: "assets/images/faq/sofiati-faq-brand-manual-clinical-guidance.webp",
  journal: "assets/images/journal/sofiati-journal-typography-palette-system.webp",
  blog: "assets/images/blog/sofiati-blog-palette-care-education.webp",
  legal: "assets/images/legal/sofiati-legal-monogram-pattern-sage.webp",
  generated: "assets/generated/homepage-asset-composition.svg"
};

const ICONS = {
  care: "assets/icons/care.svg",
  trust: "assets/icons/credentials.svg",
  safety: "assets/icons/safety.svg",
  naturality: "assets/icons/values.svg",
  consultation: "assets/icons/consultation.svg",
  contact: "assets/icons/contact.svg",
  journal: "assets/icons/journal.svg",
  laser: "assets/icons/laser.svg",
  skin: "assets/icons/skin.svg",
  results: "assets/icons/results.svg",
  mission: "assets/icons/mission.svg",
  whatsapp: "assets/icons/whatsapp.svg"
};

const DNA_NAMES = [
  "Sage Cutout Editorial",
  "Bronze Concierge Ledger",
  "Ivory Studio Flow",
  "Renewal Gallery Calm",
  "Elevated Botanical Salon",
  "Refined Clinical Index",
  "Glow Soft Light Story",
  "Balanced Split Narrative",
  "Radiance Magazine Arc",
  "Essence Quiet Ritual",
  "Bloom Layered Botanical",
  "Vital Direct Guidance",
  "Poise Portrait Sequence",
  "Aura Haloed Glass",
  "Clarity Precision Panels",
  "Grace Soft Column",
  "Sculpt Contour Studio",
  "Lumin Lightbox Editorial",
  "Verda Verdant Margin",
  "Halo Circular Promise",
  "Calm Slow Journal",
  "Precision Clinical Matrix",
  "Ritual Warm Sequence",
  "Signal Clear Route",
  "Align Modular Balance",
  "Vivant Living Collage",
  "Form Structured Atelier",
  "Pure Minimal Trust",
  "Solace Gentle Retreat",
  "Method Process Ledger",
  "Evolve Progressive Path",
  "Serene Quiet Grid",
  "Elan Expressive Salon",
  "Flora Botanical Field",
  "Atelier Crafted Notes",
  "Lumina Bright Gallery",
  "Vellum Paper Layer",
  "Origin Grounded Story",
  "Kindred Personal Route",
  "Noble Classic Register",
  "Vista Wide Editorial",
  "Softline Fine Contour",
  "Meridian Measured Journey",
  "Safeguard Trust Frame",
  "Silhouette Cutout Theater",
  "Curate Gallery System",
  "Proof Ethical Evidence",
  "Signature Personal Mark",
  "Wisdom Calm Archive",
  "Sovereign Monogram Court"
];

const PALETTES = [
  ["#485041", "#9A6B35", "#F2EEE3"],
  ["#6B5846", "#A2AEA0", "#F8F7F2"],
  ["#5F6E61", "#CDAA78", "#FFF9ED"],
  ["#586D73", "#9A6B35", "#F6F0E5"],
  ["#403F36", "#B88352", "#F2EEE3"],
  ["#4D5A63", "#A2AEA0", "#F8F7F2"],
  ["#735C62", "#CDAA78", "#F7EFE8"],
  ["#505E54", "#8F7955", "#F6F4EA"],
  ["#694B43", "#D1A771", "#FBF5EC"],
  ["#3F4A45", "#B7A06D", "#F8F7F2"]
];

const HERO_STRATEGIES = [
  "asymmetric portrait with small botanical proof mark",
  "concierge letter opener with compact action rail",
  "soft full-bleed photo crop with quiet text margin",
  "stacked editorial masthead with floating cutout",
  "salon-style portrait panel with bronze rule",
  "clinical index hero with trust note and image strip",
  "lightbox portrait glow with low-pressure CTAs",
  "split balance grid with rounded image bracket",
  "magazine cover crop with service route tabs",
  "minimal promise block with tactile texture"
];

const SECTION_RHYTHMS = [
  "alternating portrait, cards, and statement pauses",
  "ledger rows, narrow callouts, and concise routes",
  "large image beats followed by airy text panels",
  "gallery cards that break into statement bands",
  "botanical dividers and salon-style quote frames",
  "matrix panels with measured service notes",
  "soft glow blocks with generous negative space",
  "balanced two-column sections with offset media",
  "editorial chapter cards and magazine previews",
  "quiet text-first sections with restrained media"
];

const PARTIAL_STRATEGIES = [
  "heroPlate, valueRail, serviceDiptych, journalRibbon, footerBridge",
  "conciergeHero, routeLedger, compactCta, supportStrip, footerIndex",
  "studioHero, portraitNote, serviceCards, formFrame, footerSignature",
  "galleryHero, imagePause, cardSequence, trustBand, footerGallery",
  "salonHero, botanicalDivider, softProcess, ctaSalon, footerSalon",
  "clinicalHero, evidencePanel, routeMatrix, faqBridge, footerLedger",
  "glowHero, lightboxCard, educationArc, contactGlow, footerHalo",
  "balanceHero, splitStep, routePair, trustSplit, footerBalance",
  "magazineHero, articleFeature, serviceChapter, ctaSpread, footerMagazine",
  "minimalHero, quietStatement, measuredCards, finalNote, footerMinimal"
];

const MOBILE_STRATEGIES = [
  "portrait stays first, CTAs stack, cards become compact rows",
  "routes collapse into touch-led ledger items with clear spacing",
  "images crop to calm center points and text stays short",
  "gallery cards stack with one visual anchor per viewport",
  "botanical accents reduce opacity and never block copy",
  "matrix panels become numbered blocks with large touch targets",
  "lightbox media moves below copy and keeps buttons visible",
  "split layouts become single-flow stories with preserved order",
  "journal previews become horizontal-scannable but readable cards",
  "minimal pages remove decorative weight and keep final CTA visible"
];

const MOTION_STRATEGIES = [
  "small opacity and translate reveals only",
  "hover lifts under 4px with reduced-motion fallback",
  "soft image fade with no parallax requirement",
  "section rule draw-ins and calm focus states",
  "botanical accent sway disabled for reduced motion",
  "ledger row highlight with no flashing",
  "lightbox glow transition under 300ms",
  "split panels settle without layout shift",
  "editorial card reveal by section order",
  "minimal focus ring and button state motion"
];

const AVOID_NOTES = [
  "generic split hero, boxed footer columns, heavy card grids",
  "sales funnel pressure, loud colors, duplicated four-card rhythm",
  "text-heavy essays, fake proof, clinical coldness",
  "stock-like image darkness, oversized hero-only layout",
  "rustic beige sameness, ornamental clutter, badge overload",
  "spreadsheet feeling, unsupported equipment claims",
  "purple-blue gradients, dramatic promises, blurred backgrounds",
  "symmetry that makes every page feel identical",
  "blog-template sameness and repeated thumbnail rhythm",
  "empty minimalism that removes guidance"
];

function esc(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function md(value) {
  return String(value ?? "").replaceAll("|", "\\|");
}

function slugify(value) {
  return String(value).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

function nowStamp() {
  return new Date().toISOString();
}

function section(name, role, heading, paragraph, options = {}) {
  return {
    name,
    role,
    heading,
    paragraph,
    bullets: options.bullets || [],
    cards: options.cards || [],
    primary: options.primary || "None",
    primaryHref: options.primaryHref || "",
    secondary: options.secondary || "None",
    secondaryHref: options.secondaryHref || "",
    asset: options.asset || "Portrait, icon, botanical divider",
    linkRole: options.linkRole || "Guides visitors to the next useful route.",
    copyDensity: options.copyDensity || "light"
  };
}

const LINKS = {
  consultation: "consultation.html",
  contact: "contact.html",
  whatsapp: "https://wa.me/5543991043536",
  about: "about.html",
  care: "care.html",
  skin: "skin.html",
  laser: "laser.html",
  results: "results.html",
  faq: "faq.html",
  journal: "journal.html",
  blog: "blog.html",
  mission: "mission.html",
  values: "values.html",
  privacy: "privacy.html",
  legal: "legal.html",
  accessibility: "accessibility.html",
  sitemap: "sitemap.html",
  home: "index.html",
  testimonials: "testimonials.html",
  cookies: "cookies.html",
  thankYou: "thank-you.html"
};

const PAGE_BLUEPRINTS = {
  home: [
    section("Hero Promise", "opening-promise", "Personalized care", "A calm, attentive approach shaped around your goals, comfort, and realistic expectations.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Franciele portrait, transparent cutout, hero background" }),
    section("Brand Values", "trust-values", "Care principles", "Every decision begins with listening, clarity, safety, and natural-looking confidence.", { cards: ["Care", "Trust", "Safety", "Naturality"], primary: "View values", primaryHref: LINKS.values, secondary: "Read mission", secondaryHref: LINKS.mission, asset: "Four custom icons and botanical divider" }),
    section("Meet Franciele", "human-trust", "Meet Franciele", "Franciele brings a careful presence to each consultation, shaped by conversation and observation.", { primary: "Meet Franciele", primaryHref: LINKS.about, secondary: "Begin consultation", secondaryHref: LINKS.consultation, asset: "Portrait crop or portrait treatment" }),
    section("Care Routes", "service-route", "Care routes", "Explore focused guidance for skin, laser, care planning, and responsible expectations.", { cards: ["Care", "Skin", "Laser", "Results"], primary: "Explore care", primaryHref: LINKS.care, secondary: "View skin", secondaryHref: LINKS.skin, asset: "Service icons or service visuals" }),
    section("Consultation Approach", "explanation-process", "How it begins", "The first step is a calm conversation about your skin, routine, goals, and comfort level.", { bullets: ["Listen", "Assess", "Plan", "Guide"], primary: "Book consultation", primaryHref: LINKS.consultation, secondary: "Read FAQ", secondaryHref: LINKS.faq, asset: "Process icons, form frame, checklist card" }),
    section("Editorial Break", "reassurance-statement", "Care with clarity", "A refined experience should feel calm, considered, and easy to understand.", { asset: "Decorative divider, texture, background asset" }),
    section("Responsible Results", "reassurance-expectations", "Realistic expectations", "Results should be discussed responsibly, with attention to individual needs and natural-looking confidence.", { primary: "Understand results", primaryHref: LINKS.results, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Results visual or trust icon" }),
    section("Journal Preview", "education-route", "Learn first", "Read calm, practical guidance before choosing your next step.", { cards: ["Skin guidance", "Laser questions", "Care planning"], primary: "Read journal", primaryHref: LINKS.journal, secondary: "View articles", secondaryHref: LINKS.blog, asset: "Journal thumbnails" }),
    section("Contact CTA", "conversion-contact", "Begin calmly", "Send your question or request an evaluation when you feel ready.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Form frame, portrait, WhatsApp icon" }),
    section("Footer Bridge", "conversion-final", "Your next route", "Continue through the site or reach out directly for guidance.", { primary: "Contact Franciele", primaryHref: LINKS.contact, secondary: "Open sitemap", secondaryHref: LINKS.sitemap, asset: "Footer detail and small decorative asset" })
  ],
  about: [
    section("Portrait Hero", "opening-portrait", "About Franciele", "A calm professional presence for aesthetic guidance, consultation, and realistic planning.", { primary: "Begin consultation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Portrait treatment" }),
    section("Professional Presence", "trust-explanation", "Careful guidance", "Her approach is attentive, clear, and guided by the person in front of her.", { bullets: ["Listen carefully", "Explain clearly", "Plan responsibly"], primary: "View care", primaryHref: LINKS.care, asset: "Icon row" }),
    section("Care Philosophy", "brand-philosophy", "Care philosophy", "Good care begins with understanding your goals, routine, and comfort before planning next steps.", { primary: "Read mission", primaryHref: LINKS.mission, secondary: "View values", secondaryHref: LINKS.values, asset: "Divider or texture" }),
    section("Values in Practice", "trust-values", "Values in practice", "Care, trust, safety, and naturality shape the client experience.", { cards: ["Care", "Trust", "Safety", "Naturality"], primary: "View values", primaryHref: LINKS.values, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Value icons" }),
    section("Human Trust", "human-trust", "A human approach", "Consultation should feel clear, respectful, and personal from the first conversation.", { primary: "Contact Franciele", primaryHref: LINKS.contact, asset: "Portrait crop or cutout" }),
    section("Editorial Pause", "reassurance-statement", "Clarity feels calm", "The best decisions are made with time, attention, and honest guidance.", { asset: "Decorative divider or statement background" }),
    section("Client Guidance", "explanation-process", "How clients start", "The journey begins with conversation, then moves into careful evaluation and planning.", { bullets: ["Ask", "Listen", "Assess", "Guide"], primary: "Book consultation", primaryHref: LINKS.consultation, secondary: "Read FAQ", secondaryHref: LINKS.faq, asset: "Process icons" }),
    section("Responsible Boundaries", "reassurance-boundary", "Responsible guidance", "Recommendations depend on individual assessment and should be discussed with realistic expectations.", { primary: "Understand results", primaryHref: LINKS.results, secondary: "Privacy", secondaryHref: LINKS.privacy, asset: "Trust icon" }),
    section("Related Routes", "internal-route", "Continue exploring", "Learn more about the approach and the care journey.", { primary: "Explore care", primaryHref: LINKS.care, secondary: "Read mission", secondaryHref: LINKS.mission, asset: "Small route icons" }),
    section("Consultation CTA", "conversion-final", "Start with clarity", "Request an evaluation or send a private message when you are ready.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Form frame or portrait accent" })
  ],
  care: [
    section("Care Hero", "opening-care", "Personalized care", "Care begins with listening, then moves toward thoughtful planning and clear next steps.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Warm portrait or care visual" }),
    section("Care Meaning", "explanation-care", "What care means", "Your goals, comfort, routine, and expectations all matter.", { bullets: ["Goals", "Comfort", "Routine", "Expectations"], primary: "Begin consultation", primaryHref: LINKS.consultation, asset: "Care icon or texture" }),
    section("Listening First", "human-trust", "Listening first", "A good plan starts with understanding what feels right, realistic, and comfortable for you.", { primary: "Book consultation", primaryHref: LINKS.consultation, secondary: "Read FAQ", secondaryHref: LINKS.faq, asset: "Portrait or consultation visual" }),
    section("Care Steps", "explanation-process", "Care steps", "A simple process makes each next step easier to understand.", { bullets: ["Assess", "Plan", "Guide", "Review"], primary: "Request evaluation", primaryHref: LINKS.consultation, asset: "Process icons" }),
    section("Related Services", "service-route", "Related care", "Explore skin guidance or laser suitability next.", { primary: "View skin", primaryHref: LINKS.skin, secondary: "Explore laser", secondaryHref: LINKS.laser, asset: "Service visuals" }),
    section("Statement Break", "reassurance-statement", "Care needs calm", "The right pace helps decisions feel clearer.", { asset: "Decorative divider or background" }),
    section("Safety Comfort", "reassurance-safety", "Feel comfortable", "Questions, limits, and expectations can all be discussed before any decision is made.", { primary: "Read FAQ", primaryHref: LINKS.faq, secondary: "Privacy", secondaryHref: LINKS.privacy, asset: "Trust icon" }),
    section("Education Preview", "education-route", "Learn before care", "Read practical guidance before choosing your next step.", { primary: "Read journal", primaryHref: LINKS.journal, secondary: "View blog", secondaryHref: LINKS.blog, asset: "Journal thumbnails" }),
    section("Prepare Consultation", "conversion-prep", "Before you start", "Bring your goals, routine, questions, and comfort level into the conversation.", { bullets: ["Your goals", "Your routine", "Your questions", "Your comfort"], primary: "Begin consultation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Form frame or checklist card" }),
    section("Final CTA", "conversion-final", "Begin with care", "Start with a conversation and choose the next step with clarity.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "CTA band" })
  ],
  laser: [
    section("Laser Hero", "opening-laser", "Laser guidance", "A suitability-led approach to laser care, expectations, and professional evaluation.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Laser service visual or portrait" }),
    section("Suitability First", "reassurance-suitability", "Suitability first", "Laser decisions depend on skin context, goals, comfort, and professional assessment.", { primary: "Begin consultation", primaryHref: LINKS.consultation, asset: "Safety icon cards" }),
    section("Guidance", "trust-guidance", "Clear guidance", "The right next step should be discussed carefully, without pressure or unrealistic promises.", { primary: "Read FAQ", primaryHref: LINKS.faq, secondary: "View results", secondaryHref: LINKS.results, asset: "Portrait or technical texture" }),
    section("Process", "explanation-process", "Care process", "Evaluation, preparation, guidance, and review keep the process understandable.", { bullets: ["Assess", "Prepare", "Guide", "Review"], primary: "Book consultation", primaryHref: LINKS.consultation, asset: "Process icons" }),
    section("Safety", "reassurance-safety", "Safe expectations", "Comfort, timing, and suitability should be clarified before moving forward.", { primary: "Read FAQ", primaryHref: LINKS.faq, secondary: "Understand results", secondaryHref: LINKS.results, asset: "Trust visual" }),
    section("Editorial Break", "reassurance-statement", "Precision needs care", "A careful process helps keep decisions clear and personal.", { asset: "Decorative divider" }),
    section("Related Routes", "service-route", "Related guidance", "Explore skin context or responsible results next.", { primary: "View skin", primaryHref: LINKS.skin, secondary: "View results", secondaryHref: LINKS.results, asset: "Service cards" }),
    section("FAQ Bridge", "education-route", "Common questions", "Find short answers before your consultation.", { primary: "Read FAQ", primaryHref: LINKS.faq, secondary: "Ask a question", secondaryHref: LINKS.contact, asset: "FAQ icon or accordion cue" }),
    section("Consultation CTA", "conversion-contact", "Check suitability", "Request an evaluation to discuss your goals and next steps.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Form frame" }),
    section("Trust Route", "conversion-final", "Need clarity", "Use the contact route or read privacy guidance before sending details.", { primary: "Contact Franciele", primaryHref: LINKS.contact, secondary: "Privacy", secondaryHref: LINKS.privacy, asset: "Trust icons" })
  ],
  skin: [
    section("Skin Hero", "opening-skin", "Skin guidance", "A refined approach to understanding skin, routine, comfort, and realistic goals.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Skin visual or portrait" }),
    section("Skin Context", "explanation-context", "Skin context", "Routine, texture, sensitivity, and goals help shape better questions.", { cards: ["Routine", "Texture", "Sensitivity", "Goals"], primary: "Begin consultation", primaryHref: LINKS.consultation, asset: "Context icons" }),
    section("Assessment", "trust-assessment", "Assessment first", "Skin guidance works best when it begins with observation, questions, and individual context.", { primary: "Book consultation", primaryHref: LINKS.consultation, secondary: "Read FAQ", secondaryHref: LINKS.faq, asset: "Portrait or detail image" }),
    section("Planning Cards", "service-route", "Planning focus", "Texture, luminosity, comfort, and routine can be discussed with care.", { cards: ["Texture", "Luminosity", "Comfort", "Routine"], primary: "View care", primaryHref: LINKS.care, asset: "Service icons" }),
    section("Texture Break", "reassurance-statement", "Less pressure", "Skin confidence should feel natural, realistic, and personal.", { asset: "Texture or decorative asset" }),
    section("Natural Confidence", "reassurance-expectations", "Natural confidence", "The goal is thoughtful guidance that respects your features and comfort.", { primary: "Understand results", primaryHref: LINKS.results, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Portrait or divider" }),
    section("Related Guidance", "internal-route", "Next guidance", "Continue with broader care planning or laser suitability.", { primary: "Explore care", primaryHref: LINKS.care, secondary: "Explore laser", secondaryHref: LINKS.laser, asset: "Service visuals" }),
    section("Journal Preview", "education-route", "Skin education", "Read simple guidance before deciding what to ask next.", { primary: "Read journal", primaryHref: LINKS.journal, secondary: "View blog", secondaryHref: LINKS.blog, asset: "Journal thumbnails" }),
    section("Consultation Path", "conversion-contact", "Clarify your goals", "A consultation helps connect your skin context with realistic next steps.", { primary: "Begin consultation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Form frame or checklist" }),
    section("Final CTA", "conversion-final", "Start with clarity", "Send your question or request an evaluation when you feel ready.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Contact Franciele", secondaryHref: LINKS.contact, asset: "CTA asset" })
  ],
  results: [
    section("Results Hero", "opening-results", "Responsible results", "A calm approach to expectations, planning, and natural-looking confidence.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Trust-led portrait or visual" }),
    section("Planning", "explanation-planning", "Results need planning", "Care outcomes depend on assessment, consistency, individual context, and realistic expectations.", { primary: "Begin consultation", primaryHref: LINKS.consultation, asset: "Process asset" }),
    section("Not Guarantees", "reassurance-boundary", "No guarantees", "This site does not promise identical results or create pressure-based expectations.", { primary: "Read FAQ", primaryHref: LINKS.faq, secondary: "Privacy", secondaryHref: LINKS.privacy, asset: "Trust icon" }),
    section("Naturality", "trust-naturality", "Natural confidence", "Guidance should support confidence without forcing a single idea of beauty.", { primary: "View care", primaryHref: LINKS.care, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Portrait or divider" }),
    section("Process", "explanation-process", "Expectation process", "Listening, assessment, planning, and review help keep expectations responsible.", { bullets: ["Listen", "Assess", "Plan", "Review"], primary: "Book consultation", primaryHref: LINKS.consultation, asset: "Process icons" }),
    section("Statement Break", "reassurance-statement", "Clarity over pressure", "The best decisions leave space for questions.", { asset: "Decorative statement asset" }),
    section("Related Care", "internal-route", "Explore context", "Read more about care planning and skin guidance.", { primary: "Explore care", primaryHref: LINKS.care, secondary: "View skin", secondaryHref: LINKS.skin, asset: "Service visuals" }),
    section("Consent Feedback", "reassurance-privacy", "Feedback matters", "Client feedback should be used with consent, privacy, and responsible context.", { primary: "Feedback guidance", primaryHref: LINKS.testimonials, secondary: "Privacy", secondaryHref: LINKS.privacy, asset: "Privacy icon" }),
    section("Consultation Path", "conversion-contact", "Discuss expectations", "A consultation helps clarify what may be realistic for your individual context.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Form frame" }),
    section("Final CTA", "conversion-final", "Ask first", "Send your question or begin with a calm evaluation.", { primary: "Contact Franciele", primaryHref: LINKS.contact, secondary: "Read FAQ", secondaryHref: LINKS.faq, asset: "CTA asset" })
  ],
  consultation: [
    section("Consultation Hero", "opening-consultation", "Begin consultation", "Start with a calm conversation about your goals, questions, comfort, and expectations.", { primary: "Fill form", primaryHref: LINKS.contact, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Warm portrait and form frame" }),
    section("What It Clarifies", "explanation-cards", "What it clarifies", "A consultation can clarify goals, questions, comfort, and expectations.", { cards: ["Goals", "Questions", "Comfort", "Expectations"], primary: "Start form", primaryHref: LINKS.contact, asset: "Icons" }),
    section("Before Consultation", "education-prep", "Before you start", "Bring simple notes about your goals, routine, questions, and comfort level.", { bullets: ["Your goals", "Your routine", "Your questions", "Your comfort"], primary: "Read FAQ", primaryHref: LINKS.faq, asset: "Checklist card" }),
    section("During Conversation", "human-trust", "During consultation", "The conversation focuses on listening, understanding, and guiding your next step clearly.", { primary: "Ask a question", primaryHref: LINKS.contact, asset: "Portrait or consultation visual" }),
    section("After Consultation", "explanation-after", "Afterwards", "You should leave with clearer options, realistic expectations, and a better sense of direction.", { primary: "View care", primaryHref: LINKS.care, secondary: "View results", secondaryHref: LINKS.results, asset: "Process icons" }),
    section("Form Break", "conversion-form", "Send your request", "Use the form or WhatsApp to begin privately.", { primary: "Submit request", primaryHref: LINKS.contact, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Form frame" }),
    section("Privacy Comfort", "reassurance-privacy", "Privacy matters", "Your message should feel safe, clear, and handled with care.", { primary: "Privacy", primaryHref: LINKS.privacy, asset: "Privacy icon" }),
    section("Related Guidance", "internal-route", "Helpful routes", "Explore care guidance or practical questions before sending your request.", { primary: "Explore care", primaryHref: LINKS.care, secondary: "View FAQ", secondaryHref: LINKS.faq, asset: "Route icons" }),
    section("Contact Options", "conversion-contact", "Prefer messaging", "Use WhatsApp or the contact page if you have a quick question.", { primary: "Message WhatsApp", primaryHref: LINKS.whatsapp, secondary: "Contact Franciele", secondaryHref: LINKS.contact, asset: "Contact icons" }),
    section("Final CTA", "conversion-final", "Start simply", "A clear first step can make the whole process easier.", { primary: "Fill form", primaryHref: LINKS.contact, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "CTA asset" })
  ],
  contact: [
    section("Contact Hero", "opening-contact", "Contact Franciele", "Send a private message or request an evaluation when you feel ready.", { primary: "Message WhatsApp", primaryHref: LINKS.whatsapp, secondary: "Fill form", secondaryHref: LINKS.contact, asset: "Warm portrait" }),
    section("Best Next Step", "guidance-route", "Best next step", "For care decisions, begin with evaluation. For questions, send a short message.", { primary: "Begin consultation", primaryHref: LINKS.consultation, secondary: "Ask a question", secondaryHref: LINKS.contact, asset: "Icon card" }),
    section("Contact Options", "conversion-contact", "Contact options", "Choose WhatsApp, email, or the form route.", { cards: ["WhatsApp", "Email", "Form"], primary: "Message WhatsApp", primaryHref: LINKS.whatsapp, secondary: "Send form", secondaryHref: LINKS.contact, asset: "Contact icons" }),
    section("Message Tips", "education-prep", "What to include", "A short note can make the first response more useful.", { bullets: ["Your goal", "Main question", "Preferred contact", "Comfort level"], primary: "Ask a question", primaryHref: LINKS.contact, asset: "Checklist icon" }),
    section("Form Section", "conversion-form", "Send a message", "Share your question and preferred contact route.", { primary: "Send message", primaryHref: LINKS.contact, secondary: "Privacy", secondaryHref: LINKS.privacy, asset: "Form frame" }),
    section("Reassurance Break", "reassurance-statement", "No pressure", "You can begin with a question before deciding anything.", { asset: "Decorative statement asset" }),
    section("FAQ Bridge", "education-route", "Have doubts", "Read common questions before sending your message.", { primary: "Read FAQ", primaryHref: LINKS.faq, secondary: "Begin consultation", secondaryHref: LINKS.consultation, asset: "FAQ icon" }),
    section("Trust Links", "reassurance-privacy", "Before sending", "Review privacy or accessibility information if helpful.", { primary: "Privacy", primaryHref: LINKS.privacy, secondary: "Accessibility", secondaryHref: LINKS.accessibility, asset: "Trust icons" }),
    section("Consultation Reminder", "conversion-contact", "Evaluation helps", "A consultation gives your questions more context and direction.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Consultation frame" }),
    section("Final Route", "conversion-final", "Keep exploring", "Return home or open the sitemap for all routes.", { primary: "Home", primaryHref: LINKS.home, secondary: "Sitemap", secondaryHref: LINKS.sitemap, asset: "Footer detail" })
  ],
  mission: [
    section("Mission Hero", "opening-mission", "Our mission", "To make aesthetic guidance feel careful, clear, and responsible.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Portrait or mission visual" }),
    section("Evaluation Leads", "trust-evaluation", "Evaluation first", "Good decisions begin with understanding the person, not rushing the answer.", { primary: "Begin consultation", primaryHref: LINKS.consultation, asset: "Evaluation icon" }),
    section("Care Philosophy", "brand-philosophy", "Careful planning", "Each step should feel considered, personal, and realistic.", { primary: "Explore care", primaryHref: LINKS.care, asset: "Care visual" }),
    section("Brand Values", "trust-values", "Guiding values", "Care, trust, safety, and naturality guide the experience.", { cards: ["Care", "Trust", "Safety", "Naturality"], primary: "View values", primaryHref: LINKS.values, secondary: "About Franciele", secondaryHref: LINKS.about, asset: "Value icons" }),
    section("Human Trust", "human-trust", "Human guidance", "The experience should feel personal, respectful, and clear.", { primary: "Meet Franciele", primaryHref: LINKS.about, asset: "Portrait crop" }),
    section("Statement Break", "reassurance-statement", "Clarity is care", "A calm process helps better choices.", { asset: "Statement background" }),
    section("Responsible Practice", "reassurance-boundary", "No pressure", "This site avoids exaggerated promises and unsupported proof.", { primary: "Understand results", primaryHref: LINKS.results, asset: "Trust icon" }),
    section("Related Pages", "internal-route", "Learn more", "Explore the values behind the experience.", { primary: "About", primaryHref: LINKS.about, secondary: "Values", secondaryHref: LINKS.values, asset: "Route icons" }),
    section("Consultation Path", "conversion-contact", "Start with questions", "A consultation can help clarify your next step.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Read FAQ", secondaryHref: LINKS.faq, asset: "Form cue" }),
    section("Final CTA", "conversion-final", "Reach out", "Send a message when you are ready.", { primary: "Contact", primaryHref: LINKS.contact, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "CTA asset" })
  ],
  values: [
    section("Values Hero", "opening-values", "Care values", "Four principles shape the Sofiati experience.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Value visual" }),
    section("Cuidado", "trust-care", "Care", "Care begins with listening closely and respecting individual context.", { primary: "Explore care", primaryHref: LINKS.care, asset: "Care icon" }),
    section("Confianca", "trust-confidence", "Trust", "Trust grows through clear explanations and calm guidance.", { primary: "Meet Franciele", primaryHref: LINKS.about, asset: "Trust icon" }),
    section("Seguranca", "reassurance-safety", "Safety", "Safety means boundaries, evaluation, and realistic expectations.", { primary: "Read FAQ", primaryHref: LINKS.faq, asset: "Safety icon" }),
    section("Naturalidade", "trust-naturality", "Naturality", "Naturality means planning that respects your features and comfort.", { primary: "Understand results", primaryHref: LINKS.results, asset: "Naturality icon" }),
    section("Visual Break", "reassurance-statement", "Values guide choices", "The experience should feel thoughtful from start to finish.", { asset: "Decorative divider" }),
    section("Values in Consultation", "conversion-prep", "In consultation", "These values shape how questions, goals, and next steps are discussed.", { primary: "Begin consultation", primaryHref: LINKS.consultation, asset: "Consultation frame" }),
    section("Related Guidance", "internal-route", "Related guidance", "Continue with care or results guidance.", { primary: "Explore care", primaryHref: LINKS.care, secondary: "Results", secondaryHref: LINKS.results, asset: "Route icons" }),
    section("About Mission Bridge", "brand-route", "Brand story", "Read more about the purpose behind the experience.", { primary: "About", primaryHref: LINKS.about, secondary: "Mission", secondaryHref: LINKS.mission, asset: "Brand mark" }),
    section("Final CTA", "conversion-final", "Begin with care", "Send a question or request an evaluation.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "CTA asset" })
  ],
  testimonials: [
    section("Feedback Hero", "opening-feedback", "Client feedback", "Feedback should be treated with consent, privacy, and realistic context.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Feedback visual" }),
    section("Consent First", "reassurance-privacy", "Consent first", "Feedback should only be shared with appropriate permission.", { primary: "Privacy", primaryHref: LINKS.privacy, asset: "Privacy icon" }),
    section("No Guarantees", "reassurance-boundary", "Not a promise", "Feedback does not guarantee the same experience or outcome.", { primary: "Results", primaryHref: LINKS.results, asset: "Trust icon" }),
    section("Experience Themes", "trust-themes", "Experience themes", "Useful feedback themes include clarity, comfort, guidance, and trust.", { cards: ["Clarity", "Comfort", "Guidance", "Trust"], primary: "Read FAQ", primaryHref: LINKS.faq, asset: "Experience icons" }),
    section("Privacy Note", "reassurance-privacy", "Privacy matters", "Personal details and feedback must be handled carefully.", { primary: "Privacy", primaryHref: LINKS.privacy, asset: "Privacy icon" }),
    section("Trust Break", "reassurance-statement", "Trust needs care", "Responsibility matters in every part of the experience.", { asset: "Statement asset" }),
    section("Results Guidance", "education-route", "Read expectations", "Understand results responsibly before making decisions.", { primary: "Results", primaryHref: LINKS.results, asset: "Results visual" }),
    section("FAQ Bridge", "education-route", "Have questions", "Read common questions before contacting.", { primary: "FAQ", primaryHref: LINKS.faq, asset: "FAQ icon" }),
    section("Consultation CTA", "conversion-contact", "Discuss your goals", "A consultation gives your questions context.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Consultation frame" }),
    section("Contact Path", "conversion-final", "Contact directly", "Send a message if you need guidance.", { primary: "Contact", primaryHref: LINKS.contact, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Contact icon" })
  ],
  faq: [
    section("FAQ Hero", "opening-faq", "Common questions", "Short answers help you choose your next step calmly.", { primary: "Ask a question", primaryHref: LINKS.contact, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "FAQ icon" }),
    section("Consultation Questions", "education-faq", "Consultation", "Bring your goals, routine, comfort level, and main questions.", { cards: ["What should I ask", "How do I prepare", "What happens next"], primary: "Begin consultation", primaryHref: LINKS.consultation, secondary: "Contact Franciele", secondaryHref: LINKS.contact, asset: "Accordion icons" }),
    section("Care Questions", "education-care", "Care", "Care depends on your goals, comfort, and evaluation.", { primary: "Explore care", primaryHref: LINKS.care, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Care icon" }),
    section("Skin Questions", "education-skin", "Skin", "Skin guidance should consider routine, sensitivity, and realistic goals.", { primary: "View skin", primaryHref: LINKS.skin, secondary: "Read journal", secondaryHref: LINKS.journal, asset: "Skin icon" }),
    section("Laser Questions", "education-laser", "Laser", "Suitability should be discussed before decisions are made.", { primary: "Explore laser", primaryHref: LINKS.laser, secondary: "Begin consultation", secondaryHref: LINKS.consultation, asset: "Laser icon" }),
    section("Results Questions", "reassurance-expectations", "Results", "Results vary and should be discussed with realistic expectations.", { primary: "Understand results", primaryHref: LINKS.results, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Results icon" }),
    section("Privacy Contact", "reassurance-privacy", "Privacy questions", "You can review privacy details before sending a message.", { primary: "Privacy", primaryHref: LINKS.privacy, secondary: "Contact", secondaryHref: LINKS.contact, asset: "Privacy icon" }),
    section("Reassurance Break", "reassurance-statement", "Questions are welcome", "You do not need to know everything before asking.", { asset: "Decorative statement asset" }),
    section("Journal Route", "education-route", "Read more", "Explore educational notes before your consultation.", { primary: "Read journal", primaryHref: LINKS.journal, secondary: "View blog", secondaryHref: LINKS.blog, asset: "Journal thumbnail" }),
    section("Consultation CTA", "conversion-final", "Still unsure", "Send your question or request an evaluation.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "CTA frame" })
  ],
  journal: [
    section("Journal Hero", "opening-journal", "Care journal", "Short guidance for better questions, calmer decisions, and clearer expectations.", { primary: "Read articles", primaryHref: LINKS.blog, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Editorial thumbnails" }),
    section("Featured Article", "education-feature", "Featured guide", "Start with the most useful topic for your current questions.", { primary: "Read guide", primaryHref: LINKS.blog, asset: "Large article thumbnail" }),
    section("Skin Category", "education-skin", "Skin guidance", "Read about routine, texture, sensitivity, and planning.", { primary: "View skin", primaryHref: LINKS.skin, secondary: "Read blog", secondaryHref: LINKS.blog, asset: "Skin thumbnail" }),
    section("Laser Category", "education-laser", "Laser questions", "Learn what to discuss before choosing laser care.", { primary: "Explore laser", primaryHref: LINKS.laser, secondary: "Read FAQ", secondaryHref: LINKS.faq, asset: "Laser thumbnail" }),
    section("Care Category", "education-care", "Care planning", "Understand how consultation supports personal decisions.", { primary: "Explore care", primaryHref: LINKS.care, secondary: "Begin consultation", secondaryHref: LINKS.consultation, asset: "Care thumbnail" }),
    section("Results Category", "reassurance-expectations", "Result expectations", "Read responsible guidance before forming expectations.", { primary: "Understand results", primaryHref: LINKS.results, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Results thumbnail" }),
    section("Editorial Break", "reassurance-statement", "Learn before deciding", "Good questions make the consultation more useful.", { asset: "Editorial divider" }),
    section("Article Grid", "education-route", "Latest notes", "Browse short educational pieces by topic.", { primary: "View blog", primaryHref: LINKS.blog, secondary: "Read FAQ", secondaryHref: LINKS.faq, asset: "Varied thumbnails" }),
    section("Consultation Bridge", "conversion-contact", "Ready to ask", "Bring your questions into a private consultation or message.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "Message WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Consultation frame" }),
    section("Blog Contact CTA", "conversion-final", "Continue reading", "Explore more articles or contact Franciele directly.", { primary: "View blog", primaryHref: LINKS.blog, secondary: "Contact Franciele", secondaryHref: LINKS.contact, asset: "Footer accent" })
  ],
  blog: [
    section("Blog Hero", "opening-blog", "Care articles", "Deeper educational notes for skin, laser, care, and expectations.", { primary: "Read articles", primaryHref: LINKS.journal, secondary: "Request evaluation", secondaryHref: LINKS.consultation, asset: "Blog editorial visual" }),
    section("Featured Guide", "education-feature", "Featured guide", "Start with the guide most relevant to your questions.", { primary: "Read guide", primaryHref: LINKS.journal, asset: "Article thumbnail" }),
    section("Article Categories", "education-route", "Browse topics", "Choose skin, laser, care, or results guidance.", { cards: ["Skin", "Laser", "Care", "Results"], primary: "Journal", primaryHref: LINKS.journal, asset: "Category cards" }),
    section("Article Grid", "education-route", "Latest articles", "Read short educational pieces by topic.", { primary: "Read more", primaryHref: LINKS.journal, asset: "Article grid thumbnails" }),
    section("Reading Path", "education-route", "Choose a path", "Follow the topic that matches your current question.", { primary: "View FAQ", primaryHref: LINKS.faq, asset: "Path icon" }),
    section("Education Break", "reassurance-statement", "Better questions", "Useful reading makes consultation clearer.", { asset: "Editorial divider" }),
    section("Popular Questions", "education-faq", "Popular doubts", "Find practical answers before your next step.", { primary: "FAQ", primaryHref: LINKS.faq, asset: "FAQ icon" }),
    section("Related Services", "service-route", "Related pages", "Connect articles to service guidance.", { primary: "Care", primaryHref: LINKS.care, secondary: "Skin", secondaryHref: LINKS.skin, asset: "Service visuals" }),
    section("Consultation CTA", "conversion-contact", "Need guidance", "Bring your questions into a consultation.", { primary: "Request evaluation", primaryHref: LINKS.consultation, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Consultation frame" }),
    section("Journal Bridge", "conversion-final", "Back to journal", "Return to the editorial guide library.", { primary: "Journal", primaryHref: LINKS.journal, secondary: "Contact", secondaryHref: LINKS.contact, asset: "Footer accent" })
  ],
  legal: supportSections("Legal", "legal", LINKS.privacy),
  privacy: supportSections("Privacy", "privacy", LINKS.cookies),
  cookies: supportSections("Cookies", "cookies", LINKS.privacy),
  accessibility: supportSections("Accessibility", "accessibility", LINKS.legal),
  sitemap: [
    section("Sitemap Hero", "opening-sitemap", "Site map", "Find every important page quickly.", { primary: "Home", primaryHref: LINKS.home, secondary: "Consultation", secondaryHref: LINKS.consultation, asset: "Route map visual" }),
    section("Core Pages", "internal-route", "Core pages", "Start with the main routes.", { primary: "Home", primaryHref: LINKS.home, secondary: "About", secondaryHref: LINKS.about, asset: "Core route icons" }),
    section("Service Pages", "service-route", "Care pages", "Explore care, skin, laser, and results.", { primary: "Care", primaryHref: LINKS.care, secondary: "Skin", secondaryHref: LINKS.skin, asset: "Service icons" }),
    section("Brand Pages", "brand-route", "Brand pages", "Learn about the mission and values.", { primary: "Mission", primaryHref: LINKS.mission, secondary: "Values", secondaryHref: LINKS.values, asset: "Brand mark" }),
    section("Education Pages", "education-route", "Education", "Read journal notes and articles.", { primary: "Journal", primaryHref: LINKS.journal, secondary: "Blog", secondaryHref: LINKS.blog, asset: "Journal icons" }),
    section("Trust Pages", "reassurance-route", "Trust pages", "Review results, feedback, and privacy.", { primary: "Results", primaryHref: LINKS.results, secondary: "Privacy", secondaryHref: LINKS.privacy, asset: "Trust icons" }),
    section("Legal Pages", "support-route", "Legal pages", "Open policy and accessibility routes.", { primary: "Legal", primaryHref: LINKS.legal, secondary: "Accessibility", secondaryHref: LINKS.accessibility, asset: "Support icons" }),
    section("Consultation Path", "conversion-contact", "Start here", "Request evaluation or send a message.", { primary: "Consultation", primaryHref: LINKS.consultation, secondary: "Contact", secondaryHref: LINKS.contact, asset: "Contact frame" }),
    section("Route Break", "reassurance-statement", "Clear routes", "A simple map helps every visitor move confidently.", { asset: "Route divider" }),
    section("Final CTA", "conversion-final", "Return home", "Go back to the beginning or start consultation.", { primary: "Home", primaryHref: LINKS.home, secondary: "Consultation", secondaryHref: LINKS.consultation, asset: "Footer bridge" })
  ],
  "404": [
    section("Error Hero", "opening-error", "Page missing", "This page could not be found, but you can continue calmly.", { primary: "Home", primaryHref: LINKS.home, secondary: "Contact", secondaryHref: LINKS.contact, asset: "Soft error visual" }),
    section("Reassurance", "reassurance-statement", "No problem", "Use one of the routes below to keep moving.", { asset: "Calm divider" }),
    section("Return Home", "internal-route", "Start again", "Return to the main page.", { primary: "Home", primaryHref: LINKS.home, asset: "Home icon" }),
    section("Consultation Path", "conversion-contact", "Need guidance", "You can still request an evaluation.", { primary: "Consultation", primaryHref: LINKS.consultation, asset: "Consultation icon" }),
    section("Service Routes", "service-route", "Care routes", "Explore care or skin guidance.", { primary: "Care", primaryHref: LINKS.care, secondary: "Skin", secondaryHref: LINKS.skin, asset: "Service icons" }),
    section("Journal Route", "education-route", "Read guidance", "Browse education while you search.", { primary: "Journal", primaryHref: LINKS.journal, secondary: "Blog", secondaryHref: LINKS.blog, asset: "Journal icon" }),
    section("FAQ Route", "education-faq", "Common questions", "Find short answers quickly.", { primary: "FAQ", primaryHref: LINKS.faq, asset: "FAQ icon" }),
    section("Contact Route", "conversion-contact", "Contact us", "Send a message if you need help.", { primary: "Contact", primaryHref: LINKS.contact, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Contact icon" }),
    section("Sitemap Route", "internal-route", "Find everything", "Open the full site map.", { primary: "Sitemap", primaryHref: LINKS.sitemap, asset: "Sitemap icon" }),
    section("Final CTA", "conversion-final", "Continue calmly", "Choose a route and keep exploring.", { primary: "Home", primaryHref: LINKS.home, secondary: "Contact", secondaryHref: LINKS.contact, asset: "Footer bridge" })
  ],
  "thank-you": [
    section("Thank You Hero", "opening-thanks", "Message received", "Thank you. Your message has been sent.", { primary: "Home", primaryHref: LINKS.home, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Thank you visual" }),
    section("What Happens Next", "explanation-next", "Next step", "Your message can now be reviewed and answered through the chosen route.", { asset: "Process icon" }),
    section("While You Wait", "education-route", "While you wait", "Read useful guidance before the next step.", { primary: "Journal", primaryHref: LINKS.journal, asset: "Journal thumbnail" }),
    section("Prepare Consultation", "education-prep", "Prepare questions", "Think about goals, routine, comfort, and expectations.", { primary: "Consultation", primaryHref: LINKS.consultation, secondary: "FAQ", secondaryHref: LINKS.faq, asset: "Checklist card" }),
    section("Care Education", "service-route", "Explore care", "Learn more about care and skin guidance.", { primary: "Care", primaryHref: LINKS.care, secondary: "Skin", secondaryHref: LINKS.skin, asset: "Service icons" }),
    section("Journal Preview", "education-route", "Read more", "Browse articles for practical education.", { primary: "Journal", primaryHref: LINKS.journal, secondary: "Blog", secondaryHref: LINKS.blog, asset: "Journal thumbnails" }),
    section("Privacy Reassurance", "reassurance-privacy", "Privacy note", "Review how contact information is handled.", { primary: "Privacy", primaryHref: LINKS.privacy, asset: "Privacy icon" }),
    section("Contact Again", "conversion-contact", "Need to add", "Send another message if needed.", { primary: "Contact", primaryHref: LINKS.contact, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Contact icon" }),
    section("Brand Reassurance", "reassurance-statement", "Calm guidance", "Every next step should feel clear and considered.", { asset: "Brand divider" }),
    section("Final Route", "conversion-final", "Return home", "Go back to the site or continue reading.", { primary: "Home", primaryHref: LINKS.home, secondary: "Journal", secondaryHref: LINKS.journal, asset: "Footer bridge" })
  ]
};

function supportSections(topic, key, relatedHref) {
  return [
    section("Page Hero", `opening-${key}`, topic, "Clear information helps visitors use this site with confidence.", { primary: "Contact", primaryHref: LINKS.contact, secondary: "Sitemap", secondaryHref: LINKS.sitemap, asset: "Support page visual" }),
    section("Main Explanation", "support-explanation", "Plain language", "This page explains the main information simply and clearly.", { asset: "Policy icon" }),
    section("Key Topic", "support-details", "Key details", "Important details should be easy to read and understand.", { asset: "Detail icon" }),
    section("User Choice", "support-choice", "Your choices", "Visitors should understand their options and contact routes.", { primary: "Contact", primaryHref: LINKS.contact, asset: "Choice icon" }),
    section("Related Route", "support-route", "Related page", "Continue to the most relevant support page.", { primary: "Related page", primaryHref: relatedHref, asset: "Route icon" }),
    section("Trust Break", "reassurance-statement", "Trust through clarity", "Clear information supports a better experience.", { asset: "Trust divider" }),
    section("Contact Route", "conversion-contact", "Need help", "Send a message if something is unclear.", { primary: "Contact", primaryHref: LINKS.contact, secondary: "WhatsApp", secondaryHref: LINKS.whatsapp, asset: "Contact icon" }),
    section("Legal Bridge", "support-route", "More information", "Review related site guidance.", { primary: "Privacy", primaryHref: LINKS.privacy, secondary: "Legal", secondaryHref: LINKS.legal, asset: "Support icons" }),
    section("Sitemap Route", "internal-route", "Find pages", "Use the sitemap to find any route.", { primary: "Sitemap", primaryHref: LINKS.sitemap, secondary: "Home", secondaryHref: LINKS.home, asset: "Sitemap icon" }),
    section("Final CTA", "conversion-final", "Contact support", "Reach out if you need help using the site.", { primary: "Contact", primaryHref: LINKS.contact, secondary: "Home", secondaryHref: LINKS.home, asset: "Footer bridge" })
  ];
}

export function normalizeAtlas(rawAtlas) {
  return rawAtlas.map((site, index) => ({
    siteId: site.id ?? site.siteId,
    siteName: site.name ?? site.siteName,
    number: (site.id ?? site.siteId).slice(0, 2),
    slug: (site.id ?? site.siteId).slice(3),
    index
  }));
}

export function siteProfile(site) {
  const index = site.index ?? Number(site.number) - 1;
  const palette = PALETTES[index % PALETTES.length];
  return {
    ...site,
    dnaName: DNA_NAMES[index],
    heroStrategy: HERO_STRATEGIES[index % HERO_STRATEGIES.length],
    sectionRhythm: SECTION_RHYTHMS[index % SECTION_RHYTHMS.length],
    partialStrategy: PARTIAL_STRATEGIES[index % PARTIAL_STRATEGIES.length],
    mobileStrategy: MOBILE_STRATEGIES[index % MOBILE_STRATEGIES.length],
    motionStrategy: MOTION_STRATEGIES[index % MOTION_STRATEGIES.length],
    avoidNote: AVOID_NOTES[index % AVOID_NOTES.length],
    primaryColor: palette[0],
    accentColor: palette[1],
    surfaceColor: palette[2],
    radius: [0, 3, 8, 14, 22, 34, 48, 64, 96, 999][index % 10],
    rhythmOffset: index % 8,
    imageRhythm: [
      "portrait, icon, wide image, statement",
      "wide image, portrait, compact icon, journal",
      "cutout, service visual, texture, form frame",
      "botanical divider, portrait, route card, footer mark",
      "journal thumbnail, portrait, service icon, texture"
    ][index % 5],
    footerStrategy: [
      "unboxed footer bridge with centered copyright",
      "thin-rule footer index with no column boxes",
      "signature footer note with open route list",
      "minimal legal route footer with botanical stamp",
      "editorial footer bridge with contact emphasis"
    ][index % 5],
    mobileMenuStrategy: [
      "sheet menu with large calm links",
      "ledger menu with service route grouping",
      "portrait-accent menu with short support routes",
      "minimal menu with strong consultation action",
      "editorial menu with journal route emphasis"
    ][index % 5]
  };
}

export function getPageMeta(key) {
  return PAGE_META[key];
}

export function pageBlueprint(key, profile) {
  const source = PAGE_BLUEPRINTS[key].map((item) => ({ ...item }));
  if (!profile) return source;
  const first = source[0];
  const last = source[source.length - 1];
  const middle = source.slice(1, -1);
  const rotation = profile.rhythmOffset % middle.length;
  const rotated = middle.slice(rotation).concat(middle.slice(0, rotation));
  return [first, ...rotated, last].map((item, index) => ({
    ...item,
    displayNumber: String(index + 1).padStart(2, "0"),
    layoutSignature: layoutSignature(profile, key, item, index)
  }));
}

function layoutSignature(profile, pageKey, item, index) {
  const base = `${profile.siteId}-${slugify(profile.dnaName)}-${slugify(pageKey)}-${slugify(item.name)}`;
  return `${base}-${String(index + 1).padStart(2, "0")}`;
}

function pageTitle(pageKey, profile) {
  const label = PAGE_META[pageKey].label;
  return `${label} | ${profile.siteName} | Franciele Sofiati`;
}

function pageDescription(pageKey, profile) {
  const section = PAGE_BLUEPRINTS[pageKey][0];
  return `${section.paragraph} ${profile.siteName} expresses this through ${profile.dnaName.toLowerCase()}.`;
}

function sectionAsset(sectionItem, pageKey, profile, index) {
  const imageKey = PAGE_META[pageKey].imageKey;
  const visual = IMAGE_FILES[imageKey] || IMAGE_FILES.generated;
  const portrait = `assets/portrait/franciele-portrait-${profile.slug}.webp`;
  const iconPool = [ICONS.care, ICONS.trust, ICONS.safety, ICONS.naturality, ICONS.consultation, ICONS.contact, ICONS.journal, ICONS.laser, ICONS.skin, ICONS.results, ICONS.mission, ICONS.whatsapp];
  if (index === 0 || sectionItem.role.includes("human") || sectionItem.role.includes("contact")) {
    return { src: portrait, alt: `Franciele Sofiati portrait for the ${profile.siteName} ${PAGE_META[pageKey].label} page`, kind: "portrait" };
  }
  if (sectionItem.role.includes("journal") || sectionItem.role.includes("education")) {
    return { src: "assets/journal/journal-thumbnail-1.svg", alt: `Editorial education asset for ${PAGE_META[pageKey].label}`, kind: "journal thumbnail" };
  }
  if (sectionItem.role.includes("service") || ["care", "skin", "laser", "results"].includes(pageKey)) {
    const serviceKey = pageKey === "laser" ? "laser" : pageKey === "skin" ? "skin" : pageKey === "results" ? "results" : "care";
    return { src: `assets/service/${serviceKey}-service-visual.svg`, alt: `${PAGE_META[pageKey].label} service visual`, kind: "service visual" };
  }
  if (sectionItem.role.includes("statement") || sectionItem.role.includes("support") || PAGE_META[pageKey].support) {
    return { src: "assets/botanical/gold-leaf-divider.svg", alt: `Decorative botanical divider for ${PAGE_META[pageKey].label}`, kind: "botanical divider" };
  }
  if (sectionItem.cards.length || sectionItem.bullets.length) {
    const src = iconPool[(profile.index + index) % iconPool.length];
    return { src, alt: `${sectionItem.name} icon for ${profile.siteName}`, kind: "icon" };
  }
  return { src: visual, alt: `${PAGE_META[pageKey].label} visual for ${profile.siteName}`, kind: "page visual" };
}

function actionHtml(label, href, style = "primary") {
  if (!label || label === "None" || !href) return "";
  const attrs = href.startsWith("http") ? ' target="_blank" rel="noopener"' : "";
  return `<a class="button atlas-button atlas-button--${style}" href="${esc(href)}"${attrs}>${esc(label)}</a>`;
}

function sectionHtml(sectionItem, pageKey, profile, index) {
  const number = sectionItem.displayNumber || String(index + 1).padStart(2, "0");
  const asset = sectionAsset(sectionItem, pageKey, profile, index);
  const headingTag = index === 0 ? "h1" : "h2";
  const actions = [actionHtml(sectionItem.primary, sectionItem.primaryHref, "primary"), actionHtml(sectionItem.secondary, sectionItem.secondaryHref, "soft")].filter(Boolean).join("\n          ");
  const cards = sectionItem.cards.length
    ? `<div class="atlas-card-row" aria-label="${esc(sectionItem.name)} cards">${sectionItem.cards.map((card) => `<article><img src="${esc(ICONS.care)}" alt="" aria-hidden="true"><h3>${esc(card)}</h3><p>${esc(shortCardText(card))}</p></article>`).join("")}</div>`
    : "";
  const bullets = sectionItem.bullets.length
    ? `<ul class="atlas-bullets">${sectionItem.bullets.map((bullet) => `<li>${esc(bullet)}</li>`).join("")}</ul>`
    : "";
  const layoutClass = [
    "atlas-layout-media-left",
    "atlas-layout-media-right",
    "atlas-layout-centered",
    "atlas-layout-ledger",
    "atlas-layout-split-card",
    "atlas-layout-statement"
  ][(profile.index + index) % 6];
  const comment = `<!--
SECTION ${number} — ${sectionItem.name}
Page: ${PAGE_META[pageKey].label}
Role: ${sectionItem.role}
Content: Heading, short paragraph${sectionItem.cards.length ? ", route cards" : ""}${sectionItem.bullets.length ? ", concise bullets" : ""}, and CTA logic.
Assets: ${sectionItem.asset}; rendered asset role: ${asset.kind}.
Links: Maximum 2 visible links/buttons.
Primary CTA: ${sectionItem.primary}
Secondary CTA: ${sectionItem.secondary}
Internal link role: ${sectionItem.linkRole}
Layout signature: ${sectionItem.layoutSignature}
Mobile note: ${profile.mobileStrategy}
QA note: Check premium spacing, short copy, asset crop, link count, and no unsupported claims.
Text: ${sectionItem.heading} / ${sectionItem.paragraph} / ${sectionItem.primary}${sectionItem.secondary !== "None" ? ` + ${sectionItem.secondary}` : ""}
-->`;
  return `${comment}
      <section
        class="story-section page-section atlas-section ${layoutClass}"
        data-section="${number}"
        data-page="${pageKey}"
        data-role="${esc(sectionItem.role)}"
        data-layout-signature="${esc(sectionItem.layoutSignature)}"
        data-max-links="2"
        data-copy-density="${esc(sectionItem.copyDensity)}"
        data-asset-role="${esc(asset.kind)}"
      >
        <div class="atlas-section__copy">
          <p class="eyebrow atlas-eyebrow">${esc(profile.siteName)} / ${esc(sectionItem.name)}</p>
          <${headingTag}>${esc(sectionItem.heading)}</${headingTag}>
          <p>${esc(sectionItem.paragraph)}</p>
          ${cards}
          ${bullets}
          ${actions ? `<div class="atlas-actions">${actions}</div>` : ""}
        </div>
        <figure class="atlas-section__media">
          <img src="${esc(asset.src)}" alt="${esc(asset.alt)}" loading="${index === 0 ? "eager" : "lazy"}" decoding="async">
          <figcaption>${esc(asset.kind)} for ${esc(sectionItem.name)}</figcaption>
        </figure>
      </section>`;
}

function shortCardText(card) {
  const text = {
    Care: "Attentive guidance.",
    Trust: "Clear explanations.",
    Safety: "Responsible boundaries.",
    Naturality: "Natural confidence.",
    Skin: "Skin context.",
    Laser: "Suitability first.",
    Results: "Realistic goals.",
    Routine: "Daily context.",
    Texture: "Refined guidance.",
    Sensitivity: "Comfort matters.",
    Goals: "Personal direction.",
    Questions: "Ask calmly.",
    Comfort: "Respect limits.",
    Expectations: "Plan responsibly."
  };
  return text[card] || "Useful route.";
}

function pageHtml(pageKey, profile) {
  const meta = PAGE_META[pageKey];
  const sections = pageBlueprint(pageKey, profile);
  const description = pageDescription(pageKey, profile);
  const canonical = `https://www.sofiati.com/concepts/${profile.siteId}/${meta.file}`;
  const bodyPage = pageKey === "home" ? "index" : pageKey;
  return `<!doctype html>
<html lang="en" data-source-lang="en" data-default-lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="${esc(description)}">
    <title>${esc(pageTitle(pageKey, profile))}</title>
    <link rel="stylesheet" href="css/style.css">
    <link rel="stylesheet" href="css/atlas-story.css">
    <link rel="canonical" href="${esc(canonical)}">
    <meta property="og:title" content="${esc(pageTitle(pageKey, profile))}">
    <meta property="og:description" content="${esc(description)}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="${esc(canonical)}">
    <meta name="twitter:card" content="summary_large_image">
  </head>
  <body class="concept concept-${esc(profile.slug)} page-${esc(bodyPage)} atlas-site atlas-site-${esc(profile.number)}" data-concept="${esc(profile.siteId)}" data-page="${esc(bodyPage)}" data-page-label="${esc(meta.label)}" data-page-title="${esc(pageTitle(pageKey, profile))}" data-page-description="${esc(description)}" data-canonical="${esc(canonical)}" data-default-lang="en" data-atlas-dna="${esc(profile.dnaName)}">
    <a class="skip-link" href="#main">Skip to main content</a>
    <div data-partial-mount="status-banner"></div>
    <div data-partial-mount="accessibility"></div>
    <div data-partial-mount="header"></div>
    <div data-partial-mount="mobile-menu"></div>
    <main id="main" class="atlas-main atlas-page-${esc(pageKey)}" data-page="${esc(pageKey)}" data-section-count="10" data-atlas-source="docs/sites/${esc(profile.siteId)}/MASTER-BRIEF.md">
${sections.map((item, index) => sectionHtml(item, pageKey, profile, index)).join("\n\n")}
    </main>
    <div data-partial-mount="cookie-banner"></div>
    <div data-partial-mount="footer"></div>
    <div data-partial-mount="floating-widgets"></div>
    <script src="js/partials.js" defer></script>
    <script src="js/main.js" defer></script>
    <script src="assets/js/sofiati-footer-cookie.js" defer data-sofiati-cookie-loader></script>
  </body>
</html>
`;
}

function atlasCss(profile) {
  const angle = 18 + (profile.index % 7) * 9;
  const gap = 28 + (profile.index % 6) * 4;
  const mediaWidth = 34 + (profile.index % 5) * 4;
  return `/* Canonical Sofiati atlas story layer for ${profile.siteId} ${profile.siteName}. */
:root {
  --sofiati-sage: #A2AEA0;
  --sofiati-sage-deep: #485041;
  --sofiati-ivory: #F2EEE3;
  --sofiati-cream: #F8F7F2;
  --sofiati-bronze: #9A6B35;
  --sofiati-gold: #CDAA78;
  --sofiati-ink: #252321;
  --sofiati-serif: Georgia, "Times New Roman", serif;
  --sofiati-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --sofiati-label-spacing: 0.12em;
}
body.atlas-site {
  --atlas-primary: ${profile.primaryColor};
  --atlas-accent: ${profile.accentColor};
  --atlas-surface: ${profile.surfaceColor};
  --atlas-radius: ${profile.radius}px;
  --atlas-gap: ${gap}px;
  --atlas-media: ${mediaWidth}%;
  background:
    linear-gradient(${angle}deg, color-mix(in srgb, var(--atlas-primary) 8%, transparent), transparent 38%),
    linear-gradient(180deg, var(--atlas-surface), var(--sofiati-cream));
  color: var(--sofiati-ink);
}
.atlas-main {
  width: min(1180px, calc(100% - 32px));
  margin: 0 auto;
  padding: clamp(30px, 5vw, 72px) 0 clamp(50px, 8vw, 110px);
}
.atlas-section {
  position: relative;
  max-width: 100%;
  min-height: clamp(420px, 72vh, 760px);
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(280px, var(--atlas-media));
  align-items: center;
  gap: var(--atlas-gap);
  padding: clamp(28px, 5vw, 76px) 0;
  border-top: 1px solid color-mix(in srgb, var(--atlas-primary) 18%, transparent);
}
.atlas-section:first-child {
  border-top: 0;
  min-height: min(760px, calc(100vh - 64px));
}
.atlas-section__copy {
  min-width: 0;
  display: grid;
  gap: 14px;
  max-width: 680px;
}
.atlas-eyebrow {
  letter-spacing: var(--sofiati-label-spacing);
  color: color-mix(in srgb, var(--atlas-primary) 76%, var(--sofiati-bronze));
}
.atlas-section h1,
.atlas-section h2,
.atlas-section h3 {
  font-family: var(--sofiati-serif);
  font-weight: 400;
  letter-spacing: 0;
  max-width: 100%;
  overflow-wrap: anywhere;
}
.atlas-section h1 {
  max-width: min(100%, 12ch);
  font-size: clamp(3rem, 8vw, 7.4rem);
  line-height: .92;
}
.atlas-section h2 {
  max-width: min(100%, 14ch);
  font-size: clamp(2rem, 5vw, 5.1rem);
  line-height: .96;
}
.atlas-section p {
  max-width: 58ch;
  color: color-mix(in srgb, var(--sofiati-ink) 70%, var(--atlas-primary));
  font-size: clamp(1rem, 1.25vw, 1.18rem);
}
.atlas-section__media {
  position: relative;
  min-width: 0;
  min-height: clamp(220px, 36vw, 520px);
  margin: 0;
  overflow: hidden;
  border-radius: var(--atlas-radius);
  background:
    radial-gradient(circle at 20% 18%, color-mix(in srgb, var(--atlas-accent) 26%, transparent), transparent 36%),
    color-mix(in srgb, var(--atlas-primary) 12%, white);
  border: 1px solid color-mix(in srgb, var(--atlas-accent) 28%, transparent);
  box-shadow: 0 22px 70px rgba(37, 35, 33, .10);
}
.atlas-section__media img {
  width: 100%;
  height: 100%;
  min-height: inherit;
  object-fit: contain;
  padding: clamp(18px, 4vw, 46px);
}
.atlas-section__media figcaption {
  position: absolute;
  left: 14px;
  right: 14px;
  bottom: 12px;
  padding: 8px 10px;
  border-radius: max(3px, calc(var(--atlas-radius) / 3));
  background: color-mix(in srgb, var(--sofiati-cream) 88%, white);
  color: color-mix(in srgb, var(--sofiati-ink) 70%, var(--atlas-primary));
  font-size: .72rem;
  letter-spacing: .06em;
  text-transform: uppercase;
}
.atlas-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 8px;
}
.atlas-button {
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid color-mix(in srgb, var(--atlas-primary) 28%, transparent);
  border-radius: max(3px, calc(var(--atlas-radius) / 2));
  padding: 10px 16px;
  text-decoration: none;
  font-weight: 800;
}
.atlas-button--primary {
  background: var(--sofiati-ink);
  color: white;
}
.atlas-button--soft {
  background: color-mix(in srgb, var(--atlas-accent) 18%, white);
  color: var(--sofiati-ink);
}
.atlas-card-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(136px, 1fr));
  gap: 10px;
  margin-top: 8px;
}
.atlas-card-row article {
  min-height: 120px;
  display: grid;
  gap: 7px;
  align-content: start;
  padding: 16px;
  border: 1px solid color-mix(in srgb, var(--atlas-primary) 18%, transparent);
  border-radius: max(3px, calc(var(--atlas-radius) / 1.5));
  background: color-mix(in srgb, white 82%, var(--atlas-surface));
}
.atlas-card-row img {
  width: 28px;
  height: 28px;
}
.atlas-card-row h3 {
  margin: 0;
  font-size: 1.2rem;
}
.atlas-card-row p {
  margin: 0;
  font-size: .9rem;
}
.atlas-bullets {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 4px 0 0;
  padding: 0;
  list-style: none;
}
.atlas-bullets li {
  padding: 8px 11px;
  border: 1px solid color-mix(in srgb, var(--atlas-primary) 20%, transparent);
  border-radius: 999px;
  background: color-mix(in srgb, var(--atlas-surface) 78%, white);
  font-weight: 800;
}
.atlas-layout-media-left .atlas-section__media {
  order: -1;
}
.atlas-layout-centered {
  grid-template-columns: 1fr;
  justify-items: center;
  text-align: center;
}
.atlas-layout-centered .atlas-section__copy,
.atlas-layout-centered .atlas-actions {
  justify-items: center;
  justify-content: center;
}
.atlas-layout-centered .atlas-section__media {
  width: min(760px, 100%);
}
.atlas-layout-ledger {
  grid-template-columns: .78fr 1fr;
  border-top-style: double;
}
.atlas-layout-ledger .atlas-section__media {
  min-height: 260px;
  border-radius: 0;
}
.atlas-layout-split-card {
  padding-left: clamp(18px, 3vw, 42px);
  padding-right: clamp(18px, 3vw, 42px);
  background: color-mix(in srgb, var(--atlas-primary) 7%, transparent);
  border-radius: var(--atlas-radius);
}
.atlas-layout-statement {
  grid-template-columns: 1fr minmax(180px, 28%);
  min-height: clamp(320px, 52vh, 560px);
}
.atlas-layout-statement .atlas-section__copy {
  max-width: 820px;
}
.atlas-page-home .atlas-section:first-child,
.atlas-page-consultation .atlas-section:first-child,
.atlas-page-contact .atlas-section:first-child {
  grid-template-columns: minmax(0, .9fr) minmax(320px, 1.1fr);
}
.atlas-section:nth-child(${(profile.index % 5) + 2}) {
  width: min(1040px, 100%);
  margin-left: auto;
}
.atlas-section:nth-child(${(profile.index % 4) + 5}) {
  width: min(1080px, 100%);
  margin-right: auto;
}
@media (max-width: 900px) {
  .atlas-main {
    width: min(100% - 26px, 720px);
    padding-top: 20px;
  }
  .atlas-section,
  .atlas-page-home .atlas-section:first-child,
  .atlas-page-consultation .atlas-section:first-child,
  .atlas-page-contact .atlas-section:first-child {
    min-height: auto;
    grid-template-columns: 1fr;
    gap: 22px;
    padding: clamp(34px, 12vw, 68px) 0;
  }
  .atlas-layout-media-left .atlas-section__media {
    order: 0;
  }
  .atlas-section h1 {
    max-width: 10ch;
    font-size: clamp(2.4rem, 14vw, 4.2rem);
  }
  .atlas-section h2 {
    max-width: 12ch;
    font-size: clamp(2rem, 10vw, 3.4rem);
  }
  .atlas-section__media {
    min-height: 220px;
  }
  .atlas-actions {
    width: 100%;
  }
  .atlas-button {
    flex: 1 1 180px;
  }
}
`;
}

function briefJson(profile) {
  const pages = REQUIRED_PAGE_KEYS.map((key) => {
    const meta = PAGE_META[key];
    const sections = pageBlueprint(key, profile).map((item) => ({
      section: item.displayNumber,
      name: item.name,
      role: item.role,
      heading: item.heading,
      paragraph: item.paragraph,
      primaryCta: item.primary,
      primaryHref: item.primaryHref,
      secondaryCta: item.secondary,
      secondaryHref: item.secondaryHref,
      asset: item.asset,
      layoutSignature: item.layoutSignature
    }));
    return { key, label: meta.label, file: meta.file, sections };
  });
  return {
    siteId: profile.siteId,
    siteName: profile.siteName,
    brandTokens: BRAND_TOKENS,
    pages: pages.map(({ key, label, file }) => ({ key, label, file })),
    pageFlow: pages.map((page) => ({ page: page.key, sequence: page.sections.map((item) => item.name) })),
    sectionBlueprint: pages,
    internalLinks: internalLinks(profile),
    assets: assetSummary(profile),
    partials: partialSummary(profile),
    ctas: { primary: "Request evaluation", secondary: "Message WhatsApp", support: ["Contact Franciele", "Read FAQ", "Open sitemap"] },
    seo: { titlePattern: "[Page] | [Site] | Franciele Sofiati", descriptionMaxWords: 24, canonicalBase: `https://www.sofiati.com/concepts/${profile.siteId}/` },
    accessibility: { headings: "One h1 per page and ordered h2 sections", altText: "Meaningful image alt text or empty decorative icons", linkLimit: "Maximum two visible links or buttons per section" },
    mobile: { strategy: profile.mobileStrategy, ctas: "Stacked, thumb-friendly, visible before final scroll" },
    qa: { sectionCount: 10, screenshotFocus: "premium spacing, distinct rhythm, no overlap, no generic filler" },
    cleanup: { obsoletePlanningFiles: "concept-level planning markdown is historical and removed from active folders", protectedAssets: "brand photos, local production assets, partials, and imported helpers" },
    humanConfirmationNeeded: ["Medical/legal compliance review", "Final photography approval", "Production contact routing"]
  };
}

function internalLinks(profile) {
  return REQUIRED_PAGE_KEYS.map((key) => {
    const sections = pageBlueprint(key, profile);
    const placements = sections
      .filter((item) => item.primaryHref || item.secondaryHref)
      .map((item) => ({
        sourcePage: key,
        section: item.displayNumber,
        anchorText: [item.primary, item.secondary].filter((label) => label && label !== "None").join(" / "),
        targets: [item.primaryHref, item.secondaryHref].filter(Boolean),
        seoReason: "Supports topical depth without bottom-only link dumps.",
        trustReason: "Places guidance near the visitor question being answered.",
        conversionReason: "Keeps consultation or contact routes near decision intent."
      }));
    return { sourcePage: key, placements };
  });
}

function assetSummary(profile) {
  return {
    icons: Object.values(ICONS),
    botanical: ["assets/botanical/gold-leaf-divider.svg", "assets/botanical/section-separator.svg", "assets/botanical/monogram-wreath.svg"],
    portrait: [`assets/portrait/franciele-portrait-${profile.slug}.webp`],
    backgrounds: ["assets/backgrounds/botanical-background.svg", "assets/backgrounds/mobile-menu-background.svg"],
    textures: ["assets/textures/soft-skin-texture.svg", "assets/textures/clinical-paper-texture.svg"],
    forms: ["assets/forms/consultation-form-frame.svg"],
    animations: ["assets/animations/motion-path.svg"],
    journal: ["assets/journal/journal-thumbnail-1.svg", "assets/journal/journal-thumbnail-2.svg", "assets/journal/journal-thumbnail-3.svg"],
    service: ["assets/service/care-service-visual.svg", "assets/service/laser-service-visual.svg", "assets/service/skin-service-visual.svg", "assets/service/results-service-visual.svg"],
    generated: ["assets/generated/homepage-asset-composition.svg"],
    treatment: profile.imageRhythm
  };
}

function partialSummary(profile) {
  const parts = profile.partialStrategy.split(",").map((item) => item.trim());
  return {
    heroPartials: parts[0],
    sectionPartials: parts[1],
    cardPartials: `${profile.dnaName} card rhythm`,
    ctaPartials: parts[2],
    journalPartials: parts[3],
    servicePartials: `${profile.dnaName} service route cards`,
    contactPartials: `${profile.siteName} contact frame`,
    footerPartials: profile.footerStrategy,
    mobileMenuPartials: profile.mobileMenuStrategy,
    legalSupportPartials: "plain-language support panels with trust routes"
  };
}

function masterBrief(profile) {
  const json = briefJson(profile);
  const pageSections = REQUIRED_PAGE_KEYS.map((key) => {
    const meta = PAGE_META[key];
    const rows = pageBlueprint(key, profile).map((item) => `| ${item.displayNumber} | ${md(item.name)} | ${md(item.role)} | ${md(item.heading)} | ${md(item.paragraph)} | ${md(item.primary)} | ${md(item.secondary)} | ${md(item.layoutSignature)} |`).join("\n");
    return `### ${meta.label} (${meta.file})
| # | Section | Role | Heading | Short text | Primary CTA | Secondary CTA | Layout signature |
|---|---|---|---|---|---|---|---|
${rows}`;
  }).join("\n\n");

  return `# ${profile.siteId} ${profile.siteName} MASTER-BRIEF

## 1. Site identity
- Site ID: ${profile.siteId}
- Site name: ${profile.siteName}
- Canonical concept number: ${profile.number}
- Public folder: concepts/${profile.siteId}
- Design DNA name: ${profile.dnaName}
- Core promise: calm aesthetic guidance, evaluation first, realistic expectations, and natural-looking confidence.

## 2. Canonical source statement
This master brief is the canonical source of truth for this site. Older page-flow, internal-link, design-DNA, design-note, asset-plan, audit, and report files are historical only and must not be used as active planning sources.

## 3. Design DNA
${profile.siteName} uses ${profile.dnaName}: ${profile.heroStrategy}. The site rhythm is ${profile.sectionRhythm}. It must feel premium, botanical, calm, personal, and distinctly different from the other 49 concepts.

## 4. Design notes
- Hero strategy: ${profile.heroStrategy}.
- Section silhouettes: ${profile.sectionRhythm}.
- Image rhythm: ${profile.imageRhythm}.
- Motion language: ${profile.motionStrategy}.
- Must not look like: ${profile.avoidNote}.

## 5. Brand foundation
Sofiati shares one ethical brand foundation: cuidado, confianca, seguranca, naturalidade, premium calm, real-photo-led storytelling, and professional guidance without pressure.

## 6. Shared colour and typography rules
\`\`\`css
:root {
  --sofiati-sage: #A2AEA0;
  --sofiati-sage-deep: #485041;
  --sofiati-ivory: #F2EEE3;
  --sofiati-cream: #F8F7F2;
  --sofiati-bronze: #9A6B35;
  --sofiati-gold: #CDAA78;
  --sofiati-ink: #252321;
  --sofiati-serif: Georgia, "Times New Roman", serif;
  --sofiati-sans: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --sofiati-label-spacing: 0.12em;
}
\`\`\`
Site-specific layer: primary ${profile.primaryColor}, accent ${profile.accentColor}, surface ${profile.surfaceColor}, radius ${profile.radius}px.

## 7. Site-specific visual rhythm
${profile.sectionRhythm}. Page sections keep one opening promise, varied middle routes, one reassurance beat, and a final CTA.

## 8. Page list
${REQUIRED_PAGE_KEYS.map((key) => `- ${PAGE_META[key].label}: concepts/${profile.siteId}/${PAGE_META[key].file}`).join("\n")}

## 9. Page flow map
${REQUIRED_PAGE_KEYS.map((key) => `- ${PAGE_META[key].label}: ${pageBlueprint(key, profile).map((item) => item.name).join(" -> ")}`).join("\n")}

## 10. Section storytelling map
Every page tells a short journey: opening promise, context, human trust, service or support guidance, reassurance, education route, contact route, and final CTA. ${profile.siteName} expresses that journey through ${profile.dnaName}.

## 11. Internal linking map
${internalLinks(profile).map((entry) => {
  const placements = entry.placements.map((item) => `  - Section ${item.section}: ${item.anchorText} -> ${item.targets.join(", ")}. SEO: ${item.seoReason} Trust: ${item.trustReason} Conversion: ${item.conversionReason}`).join("\n");
  return `- ${PAGE_META[entry.sourcePage].label}\n${placements}`;
}).join("\n")}

## 12. Asset inventory
- Icons: ${assetSummary(profile).icons.join(", ")}
- Botanical/decorative assets: ${assetSummary(profile).botanical.join(", ")}
- Portrait assets: ${assetSummary(profile).portrait.join(", ")}
- Backgrounds: ${assetSummary(profile).backgrounds.join(", ")}
- Textures: ${assetSummary(profile).textures.join(", ")}
- Forms: ${assetSummary(profile).forms.join(", ")}
- Animations: ${assetSummary(profile).animations.join(", ")}
- Journal assets: ${assetSummary(profile).journal.join(", ")}
- Service assets: ${assetSummary(profile).service.join(", ")}
- Generated assets: ${assetSummary(profile).generated.join(", ")}

## 13. Asset notes
All assets are local to concepts/${profile.siteId}/assets unless listed as shared brand tokens. Meaningful photos need descriptive alt text. Decorative icons may use empty alt text. Keep images light, crop faces safely on mobile, and replace assets only with equal-quality Sofiati brand material.

## 14. Asset plan
Hero and human-trust sections use the local Franciele portrait. Service pages use service SVGs. Education sections use journal thumbnails. Support pages use legal or generated assets. Decorative breaks use botanical dividers and textures to prevent a cloned page rhythm.

## 15. Portrait/photo usage plan
Use assets/portrait/franciele-portrait-${profile.slug}.webp on opening, human-trust, contact, and consultation moments. Keep her face visible on mobile and never darken or blur the portrait beyond recognition.

## 16. Botanical/decorative asset usage plan
Use botanical SVGs as dividers, stamps, and section accents. They support rhythm only; they must not cover text, buttons, or faces.

## 17. Background/texture usage plan
Use soft texture backgrounds behind statement and support sections. Texture opacity must stay low enough for WCAG-friendly contrast.

## 18. Form asset usage plan
Use assets/forms/consultation-form-frame.svg in consultation and contact CTA sections to frame the action without creating pressure.

## 19. Animation/motion plan
${profile.motionStrategy}. All motion must respect reduced-motion preferences.

## 20. Journal asset plan
Journal and blog sections use three thumbnail assets and present education as a premium magazine preview, not a link dump.

## 21. Service asset plan
Care, Skin, Laser, and Results use distinct service SVGs with short explanatory copy. No equipment claims are invented.

## 22. Content direction
Copy stays short, ethical, image-led, premium, feminine, calm, and conversion-focused without pressure.

## 23. Same-content rules
The meaning may match the Sofiati foundation, but ${profile.siteName} must vary layout signatures, section order, asset rhythm, CTA rhythm, partial strategy, and mobile presentation.

## 24. Page-by-page 10-section structure
${pageSections}

## 25. Actual short text for every page section
The table above is the approved short copy. Each section has one heading, one concise paragraph, optional short bullets or cards, and at most two visible links or buttons.

## 26. CTA strategy
Primary conversion language: Request evaluation, Begin consultation, Fill form, Contact Franciele. Secondary routes: Message WhatsApp, Read FAQ, View care, Open sitemap.

## 27. SEO rules
Use concise titles, unique page descriptions, canonical URLs, internal education links, short headings, and no keyword stuffing.

## 28. Accessibility rules
Use a single H1 per page, clear focus states, meaningful alt text, readable contrast, skip link, semantic sections, and no text hidden inside images.

## 29. Mobile rules
${profile.mobileStrategy}. Buttons stack, media crops safely, no text overlaps, and final CTA remains easy to reach.

## 30. Screenshot QA rules
Check desktop, tablet, and mobile for premium spacing, visible portrait, no overlapping partials, no oversized cards, and no cloned rhythm against adjacent concepts.

## 31. Implementation checklist
- MASTER-BRIEF.md exists and ends with JSON.
- scripts/sites/${profile.siteId}/implement.mjs reads this brief.
- All 21 pages exist in concepts/${profile.siteId}.
- Each page has exactly 10 sections.
- Each section has the required comment and data attributes.

## 32. Cleanup checklist
- Remove old concept-level planning markdown after this brief is active.
- Remove obsolete audit/report/doc clutter from active folders.
- Keep production partials, source photos, brand identity, package files, and imported helpers.

## 33. Final QA checklist
- Link count: maximum two visible links/buttons per section.
- Copy length: short headings and paragraphs.
- Safety: no guarantees, fake awards, fake testimonials, or unsupported claims.
- Assets: mapped, local, and intentionally used.
- Differentiation: ${profile.dnaName} remains visible in screenshots.

## 34. Human confirmation needed
- Confirm medical/legal compliance before launch.
- Confirm final photography choices.
- Confirm production contact routing and WhatsApp destination.

## 35. Machine-readable JSON summary
\`\`\`json
${JSON.stringify(json, null, 2)}
\`\`\`
`;
}

function implementationScript(profile) {
  return `#!/usr/bin/env node
import { runSingleSiteImplementation } from "../../lib/sofiati-atlas-core.mjs";

const siteProfile = ${JSON.stringify({
  siteId: profile.siteId,
  siteName: profile.siteName,
  number: profile.number,
  slug: profile.slug,
  index: profile.index,
  dnaName: profile.dnaName,
  heroStrategy: profile.heroStrategy,
  sectionRhythm: profile.sectionRhythm,
  partialStrategy: profile.partialStrategy,
  mobileStrategy: profile.mobileStrategy,
  motionStrategy: profile.motionStrategy,
  avoidNote: profile.avoidNote,
  primaryColor: profile.primaryColor,
  accentColor: profile.accentColor,
  surfaceColor: profile.surfaceColor,
  radius: profile.radius,
  rhythmOffset: profile.rhythmOffset,
  imageRhythm: profile.imageRhythm,
  footerStrategy: profile.footerStrategy,
  mobileMenuStrategy: profile.mobileMenuStrategy
}, null, 2)};

await runSingleSiteImplementation(siteProfile, {
  command: process.argv.join(" "),
  repair: !process.argv.includes("--validate-only"),
  validateOnly: process.argv.includes("--validate-only")
});
`;
}

function extractBriefJson(markdown) {
  const match = markdown.match(/```json\s*([\s\S]*?)```/);
  if (!match) return null;
  return JSON.parse(match[1]);
}

async function writeFileIfChanged(filePath, content) {
  if (existsSync(filePath)) {
    const current = readFileSync(filePath, "utf8");
    if (current === content) return false;
  }
  await fs.mkdir(path.dirname(filePath), { recursive: true });
  await fs.writeFile(filePath, content);
  return true;
}

async function removeIfExists(filePath) {
  if (!existsSync(filePath)) return false;
  await fs.rm(filePath, { force: true, recursive: true });
  return true;
}

export function sitePaths(root, profile) {
  return {
    conceptDir: path.join(root, "concepts", profile.siteId),
    docsDir: path.join(root, "docs", "sites", profile.siteId),
    scriptDir: path.join(root, "scripts", "sites", profile.siteId),
    brief: path.join(root, "docs", "sites", profile.siteId, "MASTER-BRIEF.md"),
    report: path.join(root, "docs", "sites", profile.siteId, "IMPLEMENTATION-REPORT.md"),
    script: path.join(root, "scripts", "sites", profile.siteId, "implement.mjs"),
    css: path.join(root, "concepts", profile.siteId, "css", "atlas-story.css")
  };
}

export async function ensureSite(profileInput, options = {}) {
  const root = options.root || process.cwd();
  const profile = siteProfile(profileInput);
  const paths = sitePaths(root, profile);
  const changed = [];
  const blockers = [];

  if (!existsSync(paths.conceptDir)) {
    blockers.push(`Missing concept directory: concepts/${profile.siteId}`);
  }

  if (!options.validateOnly) {
    if (await writeFileIfChanged(paths.brief, masterBrief(profile))) changed.push("MASTER-BRIEF.md");
    if (await writeFileIfChanged(paths.script, implementationScript(profile))) changed.push("implement.mjs");
    if (await writeFileIfChanged(paths.css, atlasCss(profile))) changed.push("css/atlas-story.css");
    for (const key of REQUIRED_PAGE_KEYS) {
      const meta = PAGE_META[key];
      const filePath = path.join(paths.conceptDir, meta.file);
      if (await writeFileIfChanged(filePath, pageHtml(key, profile))) changed.push(`concepts/${profile.siteId}/${meta.file}`);
    }
  }

  let validation = validateSite(root, profile);
  if (!options.validateOnly) {
    const report = implementationReport(profile, validation, changed, blockers, options.command || "direct");
    if (await writeFileIfChanged(paths.report, report)) changed.push("IMPLEMENTATION-REPORT.md");
    validation = validateSite(root, profile);
    const finalReport = implementationReport(profile, validation, changed, blockers, options.command || "direct");
    await writeFileIfChanged(paths.report, finalReport);
  }

  return { profile, changed, blockers: blockers.concat(validation.blockers), validation };
}

export async function runSingleSiteImplementation(profileInput, options = {}) {
  const result = await ensureSite(profileInput, options);
  const status = result.validation.complete ? "complete" : "incomplete";
  console.log(`${profileInput.siteId} ${profileInput.siteName}: ${status}`);
  if (result.blockers.length) {
    for (const blocker of result.blockers) console.log(`- ${blocker}`);
  }
  return result;
}

export function validateSite(root, profileInput) {
  const profile = siteProfile(profileInput);
  const paths = sitePaths(root, profile);
  const pages = [];
  const blockers = [];
  const missingPages = [];
  const pagesWithoutTenSections = [];
  const sectionsMissingComments = [];
  const sectionsMissingDataAttributes = [];
  const sectionsOverLinkLimit = [];
  const pagesMissingFormOrWhatsapp = [];
  const pagesMissingReassurance = [];
  const pagesMissingFinalCta = [];
  const missingAssets = [];

  const briefExists = existsSync(paths.brief);
  const scriptExists = existsSync(paths.script);
  const reportExists = existsSync(paths.report);
  let briefComplete = false;
  let assetsMapped = false;
  let partialsMapped = false;

  if (briefExists) {
    try {
      const brief = readFileSync(paths.brief, "utf8");
      const json = extractBriefJson(brief);
      const requiredPhrases = [
        "Site identity",
        "Canonical source statement",
        "Design DNA",
        "Design notes",
        "Page flow map",
        "Section storytelling map",
        "Internal linking map",
        "Asset inventory",
        "Asset plan",
        "Asset notes",
        "Portrait/photo usage plan",
        "Background/texture usage plan",
        "Form asset usage plan",
        "Journal asset plan",
        "Service asset plan",
        "Content direction",
        "Same-content rules",
        "Page-by-page 10-section structure",
        "Actual short text",
        "CTA strategy",
        "SEO rules",
        "Accessibility rules",
        "Mobile rules",
        "Screenshot QA rules",
        "Implementation checklist",
        "Cleanup checklist",
        "Final QA checklist",
        "Human confirmation needed",
        "Machine-readable JSON summary"
      ];
      briefComplete = Boolean(json && json.siteId === profile.siteId && requiredPhrases.every((phrase) => brief.includes(phrase)));
      assetsMapped = Boolean(json?.assets);
      partialsMapped = Boolean(json?.partials);
    } catch (error) {
      blockers.push(`Brief JSON parse failed: ${error.message}`);
    }
  }

  for (const key of REQUIRED_PAGE_KEYS) {
    const meta = PAGE_META[key];
    const filePath = path.join(paths.conceptDir, meta.file);
    if (!existsSync(filePath)) {
      missingPages.push(meta.file);
      continue;
    }
    const html = readFileSync(filePath, "utf8");
    const sections = html.match(/<section\b[\s\S]*?<\/section>/g) || [];
    const comments = html.match(/<!--\s*SECTION\s+\d{2}\s+—[\s\S]*?-->/g) || [];
    const attrsOk = sections.every((chunk) => ["data-section=", "data-page=", "data-role=", "data-layout-signature=", "data-max-links=", "data-copy-density="].every((attr) => chunk.includes(attr)));
    const copyOk = sections.every((chunk) => /<h[12]\b/.test(chunk) && /<p\b/.test(chunk));
    const linkCounts = sections.map((chunk) => (chunk.match(/<a\b/g) || []).length + (chunk.match(/<button\b/g) || []).length);
    const overLimit = linkCounts.some((count) => count > 2);
    const hasRoute = /wa\.me|consultation\.html|contact\.html|data-form-route/.test(html);
    const hasReassurance = /data-role="[^"]*(reassurance|trust|safety|privacy|boundary|expectation)/.test(html);
    const hasFinal = /data-role="conversion-final"/.test(html);
    const pageAssets = sections.map((chunk) => {
      const match = chunk.match(/<img[^>]+src="([^"]+)"/);
      return match?.[1];
    }).filter(Boolean);
    for (const asset of pageAssets) {
      const assetPath = path.join(paths.conceptDir, asset);
      if (!existsSync(assetPath)) missingAssets.push(`${meta.file}: ${asset}`);
    }
    if (sections.length !== 10) pagesWithoutTenSections.push(`${meta.file}: ${sections.length}`);
    if (comments.length !== 10) sectionsMissingComments.push(`${meta.file}: ${comments.length}`);
    if (!attrsOk) sectionsMissingDataAttributes.push(meta.file);
    if (!copyOk) blockers.push(`${meta.file}: section without actual heading or paragraph`);
    if (overLimit) sectionsOverLinkLimit.push(meta.file);
    if (!hasRoute) pagesMissingFormOrWhatsapp.push(meta.file);
    if (!hasReassurance) pagesMissingReassurance.push(meta.file);
    if (!hasFinal) pagesMissingFinalCta.push(meta.file);
    pages.push({ file: meta.file, sections: sections.length, comments: comments.length, attrsOk, copyOk, maxLinks: Math.max(0, ...linkCounts), hasRoute, hasReassurance, hasFinal });
  }

  const complete = Boolean(
    briefExists &&
    scriptExists &&
    reportExists &&
    briefComplete &&
    pages.length === REQUIRED_PAGE_KEYS.length &&
    !missingPages.length &&
    !pagesWithoutTenSections.length &&
    !sectionsMissingComments.length &&
    !sectionsMissingDataAttributes.length &&
    !sectionsOverLinkLimit.length &&
    !pagesMissingFormOrWhatsapp.length &&
    !pagesMissingReassurance.length &&
    !pagesMissingFinalCta.length &&
    !missingAssets.length &&
    !blockers.length
  );

  return {
    complete,
    briefExists,
    scriptExists,
    reportExists,
    briefComplete,
    pages,
    missingPages,
    pagesWithoutTenSections,
    sectionsMissingComments,
    sectionsMissingDataAttributes,
    sectionsOverLinkLimit,
    pagesMissingFormOrWhatsapp,
    pagesMissingReassurance,
    pagesMissingFinalCta,
    missingAssets: [...new Set(missingAssets)],
    assetsMapped,
    partialsMapped,
    blockers
  };
}

function implementationReport(profile, validation, changed, blockers, command) {
  const complete = validation.complete ? "complete" : "incomplete";
  return `# ${profile.siteId} ${profile.siteName} IMPLEMENTATION-REPORT

Run date/time: ${nowStamp()}
Command: ${command}
Status: ${complete}

## Pages checked
${validation.pages.map((page) => `- ${page.file}: ${page.sections} sections, ${page.comments} comments, max ${page.maxLinks} visible links/buttons`).join("\n")}

## Pages updated
${changed.filter((item) => item.startsWith("concepts/")).map((item) => `- ${item}`).join("\n") || "- None during this run"}

## Assets checked
- Assets mapped in master brief: ${validation.assetsMapped ? "yes" : "no"}
- Missing assets: ${validation.missingAssets.length ? validation.missingAssets.join(", ") : "none"}

## Internal links checked
- Maximum two visible links/buttons per section: ${validation.sectionsOverLinkLimit.length ? "needs repair" : "passed"}
- Pages missing form or WhatsApp route: ${validation.pagesMissingFormOrWhatsapp.length ? validation.pagesMissingFormOrWhatsapp.join(", ") : "none"}

## CTAs checked
- Pages missing final CTA: ${validation.pagesMissingFinalCta.length ? validation.pagesMissingFinalCta.join(", ") : "none"}
- Pages missing reassurance section: ${validation.pagesMissingReassurance.length ? validation.pagesMissingReassurance.join(", ") : "none"}

## Partials checked
- Strategy mapped: ${validation.partialsMapped ? "yes" : "no"}
- Site-specific partial strategy: ${profile.partialStrategy}

## Cleanup performed
- Old planning files are handled by the global cleanup command.
- This site report supersedes scattered concept planning docs.

## Unused files removed
- See docs/sites/ATLAS-CONTINUATION-REPORT.md after cleanup.

## Issues needing human confirmation
${[...new Set([...blockers, ...validation.blockers])].map((item) => `- ${item}`).join("\n") || "- Medical/legal compliance, photography approval, and production contact routing before launch."}

## Manual design review notes
- Confirm ${profile.dnaName} reads differently from adjacent concepts.
- Confirm portrait crops are visible on mobile.
- Confirm the page feels premium, botanical, calm, and not text-heavy.
`;
}

function progressEntry(profileInput, validation = null) {
  const profile = siteProfile(profileInput);
  const v = validation || {};
  const complete = Boolean(v.complete);
  return {
    siteId: profile.siteId,
    siteName: profile.siteName,
    masterBrief: v.briefExists ? (v.briefComplete ? "complete" : "partial") : "missing",
    implementationScript: v.scriptExists ? "complete" : "missing",
    implementationReport: v.reportExists ? "complete" : "missing",
    pagesChecked: Boolean(v.pages?.length === REQUIRED_PAGE_KEYS.length),
    tenSectionsPerPage: Boolean(v.pages?.length === REQUIRED_PAGE_KEYS.length && !v.pagesWithoutTenSections?.length),
    sectionComments: Boolean(v.pages?.length === REQUIRED_PAGE_KEYS.length && !v.sectionsMissingComments?.length),
    sectionAttributes: Boolean(v.pages?.length === REQUIRED_PAGE_KEYS.length && !v.sectionsMissingDataAttributes?.length),
    actualCopy: Boolean(v.pages?.every((page) => page.copyOk)),
    internalLinks: Boolean(v.pages?.length === REQUIRED_PAGE_KEYS.length && !v.sectionsOverLinkLimit?.length && !v.pagesMissingFormOrWhatsapp?.length),
    assetsMapped: Boolean(v.assetsMapped && !v.missingAssets?.length),
    partialsMapped: Boolean(v.partialsMapped),
    seoChecked: Boolean(v.briefComplete && v.pages?.length === REQUIRED_PAGE_KEYS.length),
    accessibilityChecked: Boolean(v.briefComplete && v.pages?.length === REQUIRED_PAGE_KEYS.length && !v.sectionsMissingDataAttributes?.length),
    mobileChecked: Boolean(v.briefComplete),
    cleanupChecked: complete,
    status: complete ? "complete" : (v.briefExists || v.scriptExists || v.pages?.length ? "in-progress" : "not-started"),
    blockers: [...new Set([...(v.blockers || []), ...(v.missingAssets || [])])],
    lastUpdated: nowStamp()
  };
}

export function loadProgress(root) {
  const filePath = path.join(root, "docs", "sites", "ATLAS-PROGRESS.json");
  if (!existsSync(filePath)) return null;
  return JSON.parse(readFileSync(filePath, "utf8"));
}

export async function writeProgress(root, atlas, validations = new Map()) {
  const entries = atlas.map((site) => {
    const validation = validations.get(site.siteId) || validateSite(root, siteProfile(site));
    return progressEntry(site, validation);
  });
  const payload = {
    generatedAt: nowStamp(),
    totalSites: entries.length,
    completeSites: entries.filter((entry) => entry.status === "complete").length,
    sites: entries
  };
  await writeFileIfChanged(path.join(root, "docs", "sites", "ATLAS-PROGRESS.json"), `${JSON.stringify(payload, null, 2)}\n`);
  return payload;
}

export async function writeIndex(root, atlas) {
  const rows = atlas.map((site) => `| ${site.siteId} | ${site.siteName} | [MASTER-BRIEF.md](${site.siteId}/MASTER-BRIEF.md) | ../../scripts/sites/${site.siteId}/implement.mjs | [IMPLEMENTATION-REPORT.md](${site.siteId}/IMPLEMENTATION-REPORT.md) |`).join("\n");
  const content = `# Sofiati 50-Site Atlas Index

| Site ID | Site | Master brief | Implement script | Report |
|---|---|---|---|---|
${rows}
`;
  await writeFileIfChanged(path.join(root, "docs", "sites", "INDEX.md"), content);
}

export async function writeContinuationReport(root, atlas, run) {
  const progress = loadProgress(root);
  const sites = progress?.sites || [];
  const complete = sites.filter((site) => site.status === "complete");
  const incomplete = sites.filter((site) => site.status !== "complete");
  const listBy = (predicate) => sites.filter(predicate).map((site) => site.siteId).join(", ") || "none";
  const content = `# Sofiati Atlas Continuation Report

Run date/time: ${nowStamp()}
Command used: ${run.command}
Sites complete before this run: ${run.completeBefore}
Sites completed during this run: ${run.completedDuring.join(", ") || "none"}
Sites still incomplete: ${incomplete.length}

## Current status
- Complete sites: ${complete.length} / ${atlas.length}
- Incomplete sites: ${incomplete.map((site) => site.siteId).join(", ") || "none"}

## Missing master briefs
${listBy((site) => site.masterBrief !== "complete")}

## Missing implementation scripts
${listBy((site) => site.implementationScript !== "complete")}

## Missing implementation reports
${listBy((site) => site.implementationReport !== "complete")}

## Pages without 10 sections
${listBy((site) => !site.tenSectionsPerPage)}

## Sections missing comments
${listBy((site) => !site.sectionComments)}

## Sections missing data attributes
${listBy((site) => !site.sectionAttributes)}

## Sections with more than 2 visible links/buttons
${run.sectionsOverLinkLimit.join(", ") || "none"}

## Pages missing form/WhatsApp route
${run.pagesMissingFormOrWhatsapp.join(", ") || "none"}

## Pages missing reassurance section
${run.pagesMissingReassurance.join(", ") || "none"}

## Pages missing final CTA
${run.pagesMissingFinalCta.join(", ") || "none"}

## Missing assets
${run.missingAssets.join(", ") || "none"}

## Unused files removed
${run.unusedFilesRemoved.map((item) => `- ${item}`).join("\n") || "- none"}

## Blockers needing human confirmation
${sites.flatMap((site) => site.blockers.map((blocker) => `${site.siteId}: ${blocker}`)).join("\n") || "none"}

## Exact next command to run
${incomplete.length ? "node scripts/continue-sofiati-atlas.mjs --next" : "node scripts/continue-sofiati-atlas.mjs --validate-only"}
`;
  await writeFileIfChanged(path.join(root, "docs", "sites", "ATLAS-CONTINUATION-REPORT.md"), content);
}

export async function bootstrapAtlas(root, atlas) {
  await fs.mkdir(path.join(root, "docs", "sites"), { recursive: true });
  if (!existsSync(path.join(root, "docs", "sites", "ATLAS-PROGRESS.json"))) {
    const entries = atlas.map((site) => progressEntry(site, validateSite(root, siteProfile(site))));
    const payload = { generatedAt: nowStamp(), totalSites: entries.length, completeSites: entries.filter((entry) => entry.status === "complete").length, sites: entries };
    await writeFileIfChanged(path.join(root, "docs", "sites", "ATLAS-PROGRESS.json"), `${JSON.stringify(payload, null, 2)}\n`);
  }
  if (!existsSync(path.join(root, "docs", "sites", "ATLAS-CONTINUATION-REPORT.md"))) {
    await writeFileIfChanged(path.join(root, "docs", "sites", "ATLAS-CONTINUATION-REPORT.md"), `# Sofiati Atlas Continuation Report

Run date/time: ${nowStamp()}
Command used: bootstrap
Sites complete before this run: 0
Sites completed during this run: none
Sites still incomplete: ${atlas.length}

## Exact next command to run
node scripts/continue-sofiati-atlas.mjs --status
`);
  }
}

export async function runAtlas(root, atlasInput, options = {}) {
  const atlas = normalizeAtlas(atlasInput);
  await bootstrapAtlas(root, atlas);
  const progressBefore = loadProgress(root);
  const completeBefore = progressBefore?.sites?.filter((site) => site.status === "complete").length || 0;
  const selected = selectSites(root, atlas, options);
  const validations = new Map();
  const completedDuring = [];
  const aggregate = {
    sectionsOverLinkLimit: [],
    pagesMissingFormOrWhatsapp: [],
    pagesMissingReassurance: [],
    pagesMissingFinalCta: [],
    missingAssets: [],
    unusedFilesRemoved: []
  };

  for (const site of selected) {
    const result = await ensureSite(site, { root, validateOnly: options.validateOnly, command: options.command });
    validations.set(site.siteId, result.validation);
    if (result.validation.complete) completedDuring.push(site.siteId);
    aggregate.sectionsOverLinkLimit.push(...result.validation.sectionsOverLinkLimit.map((item) => `${site.siteId}/${item}`));
    aggregate.pagesMissingFormOrWhatsapp.push(...result.validation.pagesMissingFormOrWhatsapp.map((item) => `${site.siteId}/${item}`));
    aggregate.pagesMissingReassurance.push(...result.validation.pagesMissingReassurance.map((item) => `${site.siteId}/${item}`));
    aggregate.pagesMissingFinalCta.push(...result.validation.pagesMissingFinalCta.map((item) => `${site.siteId}/${item}`));
    aggregate.missingAssets.push(...result.validation.missingAssets.map((item) => `${site.siteId}/${item}`));
    await writeProgress(root, atlas, validations);
    await writeContinuationReport(root, atlas, { command: options.command, completeBefore, completedDuring, ...aggregate });
  }

  if (options.cleanup && !options.validateOnly) {
    aggregate.unusedFilesRemoved = await cleanupAtlas(root, atlas);
  }

  for (const site of atlas) {
    if (!validations.has(site.siteId)) validations.set(site.siteId, validateSite(root, siteProfile(site)));
  }

  const progress = await writeProgress(root, atlas, validations);
  await writeIndex(root, atlas);
  await writeContinuationReport(root, atlas, { command: options.command, completeBefore, completedDuring, ...aggregate });
  return { progress, selected, completedDuring, aggregate };
}

function selectSites(root, atlas, options) {
  if (options.site) {
    const found = atlas.find((site) => site.siteId === options.site);
    return found ? [found] : [];
  }
  const incomplete = atlas.filter((site) => !validateSite(root, siteProfile(site)).complete);
  if (options.all || options.validateOnly || options.cleanup) return options.validateOnly ? atlas : incomplete;
  if (options.batch) return incomplete.slice(0, options.batch);
  if (options.next) return incomplete.slice(0, 1);
  return [];
}

export function atlasStatus(root, atlasInput) {
  const atlas = normalizeAtlas(atlasInput);
  const progress = loadProgress(root);
  const validations = atlas.map((site) => ({ site, validation: validateSite(root, siteProfile(site)) }));
  const complete = validations.filter((item) => item.validation.complete).length;
  const progressComplete = progress?.completeSites ?? 0;
  const next = validations.find((item) => !item.validation.complete)?.site.siteId || "none";
  return {
    complete,
    total: atlas.length,
    progressComplete,
    next,
    missingProgress: !progress,
    lines: [
      `Atlas status: ${complete}/${atlas.length} sites validate complete.`,
      `Progress ledger complete count: ${progressComplete}/${atlas.length}.`,
      `Next incomplete site: ${next}.`,
      progress ? "Progress ledger exists." : "Progress ledger missing."
    ]
  };
}

export async function cleanupAtlas(root, atlasInput) {
  const atlas = normalizeAtlas(atlasInput);
  const removed = [];
  const conceptPlanningNames = new Set(["design-dna.md", "design-notes.md", "page-flow-map.md", "internal-link-map.md", "asset-plan.md", "asset-notes.md"]);
  for (const site of atlas) {
    for (const name of conceptPlanningNames) {
      const filePath = path.join(root, "concepts", site.siteId, name);
      if (await removeIfExists(filePath)) removed.push(path.relative(root, filePath));
    }
  }
  const obsoletePaths = [
    "audit",
    "final",
    "docs/agent-brief-system",
    "docs/agent-system",
    "docs/audits",
    "docs/refactor-system",
    "docs/task-brief-templates",
    "docs/current-task-brief.md",
    "docs/sofiati-master-brief.md",
    "docs/sofiati-page-checklist.md",
    "docs/sofiati-task-ledger.md",
    "docs/sofiati-done-definition.md"
  ];
  for (const relative of obsoletePaths) {
    const filePath = path.join(root, relative);
    if (await removeIfExists(filePath)) removed.push(relative);
  }
  const scriptRunDir = path.join(root, "docs", "script-runs");
  if (existsSync(scriptRunDir)) {
    const entries = await fs.readdir(scriptRunDir);
    for (const entry of entries) {
      if (!entry.startsWith("continue-sofiati-atlas-")) {
        const filePath = path.join(scriptRunDir, entry);
        if (await removeIfExists(filePath)) removed.push(path.relative(root, filePath));
      }
    }
  }
  if (await removeIfExists(path.join(root, "scripts", "__pycache__"))) removed.push("scripts/__pycache__");
  return removed;
}

export { PAGE_META, PAGE_BLUEPRINTS };
