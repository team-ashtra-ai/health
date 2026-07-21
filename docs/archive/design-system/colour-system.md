# Colour system

The visual foundation is intentionally luminous. Warm ivory carries most pages; sage and blush create narrative rhythm; medium olive is reserved for contained authority and conversion panels. Rose-gold and antique gold are details, not paragraph colours or large metallic fields.

## Primitive palette

| Token | Value | Primary use |
|---|---|---|
| `--ivory-50` | `#fffdf7` | brightest page and elevated surface |
| `--ivory-100` | `#fbf2e7` | warm paper field |
| `--sage-50` | `#f1f5ec` | soft clinical wash |
| `--sage-100` | `#e4edda` | botanical support section |
| `--sage-200` | `#d3dfc7` | illuminated sage detail |
| `--olive-400` | `#818d6f` | scrollbar and quiet visual detail |
| `--olive-600` | `#52634b` | lighter authority gradient |
| `--olive-700` | `#3f5039` | primary authority/action colour |
| `--forest-700/800/900` | `#334734` / `#293b30` / `#1d3026` | high-contrast text and hover depth |
| `--blush-50/100/200` | `#fff4ef` / `#f8e0d8` / `#edc7bd` | human warmth and soft fields |
| `--pink-gold-300` | `#d39183` | illuminated CTA detail |
| `--rose-gold-500/600/700` | `#b96b5d` / `#9b584d` / `#7c453e` | rules, labels and accessible accent copy |
| `--champagne-100` | `#f3e1c4` | luminous warm surface |
| `--gold-200/300/500/700` | `#e8cd9c` / `#d2ad69` / `#ab7a38` / `#735024` | borders, focus and restrained trust details |
| `--ink-700` | `#46554c` | secondary body copy |

## Semantic tones

| HTML tone | Visual result | Intended role |
|---|---|---|
| `data-tone="paper"` | warm ivory | open editorial chapter |
| `data-tone="mist"` | soft cream with blush light | quiet information field |
| `data-tone="sage"` | muted botanical sage | process, trust or practical guidance |
| `data-tone="blush"` | illuminated blush/champagne | human or reassuring emphasis |
| `data-tone="forest"` | light surrounding field with a contained olive panel | authority, evidence or final action |

`forest` does not create a page-width dark slab. Its direct content panel receives the olive surface while the surrounding section remains light. A long page normally contains one or two such moments; testimonials deliberately converts two nominal forest chapters back to light blush/sage to avoid a dark-heavy rhythm.

## Contrast rules

- Primary text is `--forest-900`; secondary text is `--ink-700`.
- Ivory text is used only on `--olive-700`, `--olive-600` or darker fields.
- Gold is a border/focus/detail colour and never normal paragraph copy.
- Rose-gold body accents use `--rose-gold-700`, not pale pink-gold.
- Focus uses a two-part `--focus-ring` that remains visible on light and olive surfaces.
- Error and success states use text, borders and messages; colour is never the only signal.

Implementation authority: `css/src/foundations/tokens.css` and `css/src/layout/sections.css`.
