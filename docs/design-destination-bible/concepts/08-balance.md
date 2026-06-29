# 08-balance — Layered Magazine

## Visual Thesis

A layered editorial magazine site with alternating panels, offset content, and sophisticated visual pacing.

## Colour Thesis

Ivory base. Sage, cream, blush, and one dark editorial band create layered rhythm. Bronze dividers connect the layout.

## Systems

- Header: `layered-magazine-header`
- Mobile: `botanical-panel`
- Footer: `quiet-signature`
- Homepage anatomy: `reading-path`
- Internal page anatomy: `technical-table`
- Component strategy: shape-field with inline-route calls to action
- CTA strategy: text-link
- Image strategy: Selective full transparent portraits in sections 2, 6, and 9; object-fit contain only.

## Homepage Colour Sequence

1. Ivory layered magazine hero
2. Sage-offset trust panel
3. Cream route spread
4. Blush editorial aside
5. Dark sage statement band
6. Ivory article-row section
7. Sage results panel
8. Cream journal index
9. Bronze-line CTA layer
10. Dark/ivory magazine footer bridge

## All Other Pages

Alternate layered panels. Use one dramatic colour break per page. Preserve magazine asymmetry.

## Forbidden Patterns

- No centered card stack
- No same two-column split repeated
- No flat all-cream page.

## Colour Rhythm Contract

```json
{
  "conceptId": "08-balance",
  "colourThesis": "Ivory base. Sage, cream, blush, and one dark editorial band create layered rhythm. Bronze dividers connect the layout.",
  "dominantColourFamily": "dark",
  "secondaryColourFamily": "sage",
  "accentColourFamily": "ivory",
  "contrastTemperature": "high editorial",
  "darkUsage": "dominant structural field",
  "blushUsage": "purposeful warmth and guidance notes",
  "sageUsage": "brand structure and quiet route support",
  "creamUsage": "reading relief and calm transitions",
  "goldBronzeUsage": "rules, markers, numerals, and selected CTA detail",
  "terracottaTaupeUsage": "earth warmth only when named by the destination",
  "cardSurfaceStrategy": "axis-grid; no universal cream-card default",
  "buttonStrategy": "text-link",
  "footerColour": "Dark/ivory magazine footer bridge",
  "mobileMenuColour": "Dark/ivory magazine footer bridge",
  "homepageSectionColourSequence": [
    "Ivory layered magazine hero",
    "Sage-offset trust panel",
    "Cream route spread",
    "Blush editorial aside",
    "Dark sage statement band",
    "Ivory article-row section",
    "Sage results panel",
    "Cream journal index",
    "Bronze-line CTA layer",
    "Dark/ivory magazine footer bridge"
  ],
  "aboutPageColourSequence": [
    "about 1: dark rhythm from Dark/ivory magazine footer bridge",
    "about 2: ivory rhythm from Ivory layered magazine hero",
    "about 3: sage rhythm from Sage-offset trust panel",
    "about 4: cream rhythm from Cream route spread",
    "about 5: blush rhythm from Blush editorial aside",
    "about 6: dark rhythm from Dark sage statement band",
    "about 7: ivory rhythm from Ivory article-row section",
    "about 8: sage rhythm from Sage results panel",
    "about 9: cream rhythm from Cream journal index",
    "about 10: bronze rhythm from Bronze-line CTA layer"
  ],
  "carePageColourSequence": [
    "care 1: ivory rhythm from Ivory layered magazine hero",
    "care 2: sage rhythm from Sage-offset trust panel",
    "care 3: cream rhythm from Cream route spread",
    "care 4: blush rhythm from Blush editorial aside",
    "care 5: dark rhythm from Dark sage statement band",
    "care 6: ivory rhythm from Ivory article-row section",
    "care 7: sage rhythm from Sage results panel",
    "care 8: cream rhythm from Cream journal index",
    "care 9: bronze rhythm from Bronze-line CTA layer",
    "care 10: dark rhythm from Dark/ivory magazine footer bridge"
  ],
  "laserPageColourSequence": [
    "laser 1: sage rhythm from Sage-offset trust panel",
    "laser 2: cream rhythm from Cream route spread",
    "laser 3: blush rhythm from Blush editorial aside",
    "laser 4: dark rhythm from Dark sage statement band",
    "laser 5: ivory rhythm from Ivory article-row section",
    "laser 6: sage rhythm from Sage results panel",
    "laser 7: cream rhythm from Cream journal index",
    "laser 8: bronze rhythm from Bronze-line CTA layer",
    "laser 9: dark rhythm from Dark/ivory magazine footer bridge",
    "laser 10: ivory rhythm from Ivory layered magazine hero"
  ],
  "skinPageColourSequence": [
    "skin 1: cream rhythm from Cream route spread",
    "skin 2: blush rhythm from Blush editorial aside",
    "skin 3: dark rhythm from Dark sage statement band",
    "skin 4: ivory rhythm from Ivory article-row section",
    "skin 5: sage rhythm from Sage results panel",
    "skin 6: cream rhythm from Cream journal index",
    "skin 7: bronze rhythm from Bronze-line CTA layer",
    "skin 8: dark rhythm from Dark/ivory magazine footer bridge",
    "skin 9: ivory rhythm from Ivory layered magazine hero",
    "skin 10: sage rhythm from Sage-offset trust panel"
  ],
  "resultsPageColourSequence": [
    "results 1: blush rhythm from Blush editorial aside",
    "results 2: dark rhythm from Dark sage statement band",
    "results 3: ivory rhythm from Ivory article-row section",
    "results 4: sage rhythm from Sage results panel",
    "results 5: cream rhythm from Cream journal index",
    "results 6: bronze rhythm from Bronze-line CTA layer",
    "results 7: dark rhythm from Dark/ivory magazine footer bridge",
    "results 8: ivory rhythm from Ivory layered magazine hero",
    "results 9: sage rhythm from Sage-offset trust panel",
    "results 10: cream rhythm from Cream route spread"
  ],
  "journalPageColourSequence": [
    "journal 1: dark rhythm from Dark sage statement band",
    "journal 2: ivory rhythm from Ivory article-row section",
    "journal 3: sage rhythm from Sage results panel",
    "journal 4: cream rhythm from Cream journal index",
    "journal 5: bronze rhythm from Bronze-line CTA layer",
    "journal 6: dark rhythm from Dark/ivory magazine footer bridge",
    "journal 7: ivory rhythm from Ivory layered magazine hero",
    "journal 8: sage rhythm from Sage-offset trust panel",
    "journal 9: cream rhythm from Cream route spread",
    "journal 10: blush rhythm from Blush editorial aside"
  ],
  "consultationPageColourSequence": [
    "consultation 1: sage rhythm from Sage results panel",
    "consultation 2: cream rhythm from Cream journal index",
    "consultation 3: bronze rhythm from Bronze-line CTA layer",
    "consultation 4: dark rhythm from Dark/ivory magazine footer bridge",
    "consultation 5: ivory rhythm from Ivory layered magazine hero",
    "consultation 6: sage rhythm from Sage-offset trust panel",
    "consultation 7: cream rhythm from Cream route spread",
    "consultation 8: blush rhythm from Blush editorial aside",
    "consultation 9: dark rhythm from Dark sage statement band",
    "consultation 10: ivory rhythm from Ivory article-row section"
  ],
  "contactPageColourSequence": [
    "contact 1: cream rhythm from Cream journal index",
    "contact 2: bronze rhythm from Bronze-line CTA layer",
    "contact 3: dark rhythm from Dark/ivory magazine footer bridge",
    "contact 4: ivory rhythm from Ivory layered magazine hero",
    "contact 5: sage rhythm from Sage-offset trust panel",
    "contact 6: cream rhythm from Cream route spread",
    "contact 7: blush rhythm from Blush editorial aside",
    "contact 8: dark rhythm from Dark sage statement band",
    "contact 9: ivory rhythm from Ivory article-row section",
    "contact 10: sage rhythm from Sage results panel"
  ],
  "forbiddenColourPatterns": [
    "No centered card stack",
    "No same two-column split repeated",
    "No flat all-cream page."
  ]
}
```
