# Runtime JavaScript

`main.js` is the only module entry point. It loads shared HTML partials first,
then starts focused, idempotent feature initialisers.

| Location | Responsibility |
| --- | --- |
| `core/` | Small, dependency-free DOM, page, shared-data and scroll primitives. |
| `components/` | Shared interactive UI: navigation, cookie controls, forms, header, footer, floating tools and treatment filtering. |
| `pages/` | Page-specific search/filter behaviour. Every initializer safely does nothing when its page contract is absent. |
| `partials.js` | Loads shared page chrome and resolves locale-aware links. |
| `analytics-config.js`, `consent-manager.js`, `analytics.js` | Ordered classic scripts for consent-gated analytics. They stay outside the application module graph because consent defaults must be established before analytics can load. |

## Adding behaviour

1. Put shared DOM helpers in `core/`, a reusable interface in `components/`, or route-only behaviour in `pages/`.
2. Export one clearly named `init…` function that is safe to call more than once.
3. Add that initializer to `main.js` after `loadPartials()`.
4. Use `data-*` hooks rather than visual class names for JavaScript contracts.
5. Run `npm run validate` and the interaction audit before publishing.

Do not add a second page entry script or attach competing listeners for an
existing `data-*` hook. Extend the owning module instead.
