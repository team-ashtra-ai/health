# 32-serene — Sunlit Skin Studio

## Visual Thesis

Solea uses sunlit, warm, radiant pacing with sunlight inspired skin care.

## Colour Thesis

warm cream, soft gold, sage

## Systems

- Header: `botanical-stem-header`
- Mobile: `salon-overlay`
- Footer: `magazine-index`
- Homepage anatomy: `folio-stack`
- Internal page anatomy: `technical-table`
- Component strategy: route-ledger with split-quiet calls to action
- CTA strategy: gold-mark
- Image strategy: Selective full transparent portraits in sections 2, 6, and 9; object-fit contain only.

## Homepage Colour Sequence

1. Solea hero promise in gold
2. Solea trust position in ivory
3. Solea care route in dark
4. Solea consultation path in bronze
5. Solea treatment navigation in sage
6. Solea human reassurance in cream
7. Solea education preview in gold
8. Solea responsible expectations in ivory
9. Solea contact bridge in dark
10. Solea closing identity in bronze

## All Other Pages

Inner pages keep the same care voice while changing the density, introduction, navigation rhythm, and visual emphasis by page type.

## Forbidden Patterns

- Do not flatten the site into repeated centered card stacks
- Do not use gray placeholders
- Do not invent testimonials, guarantees, prices, results, or credentials
- Do not let desktop collapse into a narrow mobile column

## Colour Rhythm Contract

```json
{
  "conceptId": "32-serene",
  "colourThesis": "warm cream, soft gold, sage",
  "dominantColourFamily": "dark",
  "secondaryColourFamily": "sage",
  "accentColourFamily": "ivory",
  "contrastTemperature": "high editorial",
  "darkUsage": "dominant structural field",
  "softWarmthUsage": "only through ivory, cream, champagne, and bronze from the approved identity palette",
  "sageUsage": "brand structure and quiet route support",
  "creamUsage": "reading relief and calm transitions",
  "goldBronzeUsage": "rules, markers, numerals, and selected CTA detail",
  "nonBrandColourUsage": "not allowed in generated CSS; descriptive pink, blush, rose, and terracotta words resolve to identity colours",
  "cardSurfaceStrategy": "expectation-ledger; no universal cream-card default",
  "buttonStrategy": "gold-mark",
  "footerColour": "Solea closing identity in bronze",
  "mobileMenuColour": "Solea consultation path in bronze",
  "homepageSectionColourSequence": [
    "Solea hero promise in gold",
    "Solea trust position in ivory",
    "Solea care route in dark",
    "Solea consultation path in bronze",
    "Solea treatment navigation in sage",
    "Solea human reassurance in cream",
    "Solea education preview in gold",
    "Solea responsible expectations in ivory",
    "Solea contact bridge in dark",
    "Solea closing identity in bronze"
  ],
  "aboutPageColourSequence": [
    "about 1: bronze rhythm from Solea consultation path in bronze",
    "about 2: sage rhythm from Solea treatment navigation in sage",
    "about 3: cream rhythm from Solea human reassurance in cream",
    "about 4: gold rhythm from Solea education preview in gold",
    "about 5: ivory rhythm from Solea responsible expectations in ivory",
    "about 6: dark rhythm from Solea contact bridge in dark",
    "about 7: bronze rhythm from Solea closing identity in bronze",
    "about 8: gold rhythm from Solea hero promise in gold",
    "about 9: ivory rhythm from Solea trust position in ivory",
    "about 10: dark rhythm from Solea care route in dark"
  ],
  "carePageColourSequence": [
    "care 1: sage rhythm from Solea treatment navigation in sage",
    "care 2: cream rhythm from Solea human reassurance in cream",
    "care 3: gold rhythm from Solea education preview in gold",
    "care 4: ivory rhythm from Solea responsible expectations in ivory",
    "care 5: dark rhythm from Solea contact bridge in dark",
    "care 6: bronze rhythm from Solea closing identity in bronze",
    "care 7: gold rhythm from Solea hero promise in gold",
    "care 8: ivory rhythm from Solea trust position in ivory",
    "care 9: dark rhythm from Solea care route in dark",
    "care 10: bronze rhythm from Solea consultation path in bronze"
  ],
  "laserPageColourSequence": [
    "laser 1: cream rhythm from Solea human reassurance in cream",
    "laser 2: gold rhythm from Solea education preview in gold",
    "laser 3: ivory rhythm from Solea responsible expectations in ivory",
    "laser 4: dark rhythm from Solea contact bridge in dark",
    "laser 5: bronze rhythm from Solea closing identity in bronze",
    "laser 6: gold rhythm from Solea hero promise in gold",
    "laser 7: ivory rhythm from Solea trust position in ivory",
    "laser 8: dark rhythm from Solea care route in dark",
    "laser 9: bronze rhythm from Solea consultation path in bronze",
    "laser 10: sage rhythm from Solea treatment navigation in sage"
  ],
  "skinPageColourSequence": [
    "skin 1: gold rhythm from Solea education preview in gold",
    "skin 2: ivory rhythm from Solea responsible expectations in ivory",
    "skin 3: dark rhythm from Solea contact bridge in dark",
    "skin 4: bronze rhythm from Solea closing identity in bronze",
    "skin 5: gold rhythm from Solea hero promise in gold",
    "skin 6: ivory rhythm from Solea trust position in ivory",
    "skin 7: dark rhythm from Solea care route in dark",
    "skin 8: bronze rhythm from Solea consultation path in bronze",
    "skin 9: sage rhythm from Solea treatment navigation in sage",
    "skin 10: cream rhythm from Solea human reassurance in cream"
  ],
  "resultsPageColourSequence": [
    "results 1: ivory rhythm from Solea responsible expectations in ivory",
    "results 2: dark rhythm from Solea contact bridge in dark",
    "results 3: bronze rhythm from Solea closing identity in bronze",
    "results 4: gold rhythm from Solea hero promise in gold",
    "results 5: ivory rhythm from Solea trust position in ivory",
    "results 6: dark rhythm from Solea care route in dark",
    "results 7: bronze rhythm from Solea consultation path in bronze",
    "results 8: sage rhythm from Solea treatment navigation in sage",
    "results 9: cream rhythm from Solea human reassurance in cream",
    "results 10: gold rhythm from Solea education preview in gold"
  ],
  "journalPageColourSequence": [
    "journal 1: dark rhythm from Solea contact bridge in dark",
    "journal 2: bronze rhythm from Solea closing identity in bronze",
    "journal 3: gold rhythm from Solea hero promise in gold",
    "journal 4: ivory rhythm from Solea trust position in ivory",
    "journal 5: dark rhythm from Solea care route in dark",
    "journal 6: bronze rhythm from Solea consultation path in bronze",
    "journal 7: sage rhythm from Solea treatment navigation in sage",
    "journal 8: cream rhythm from Solea human reassurance in cream",
    "journal 9: gold rhythm from Solea education preview in gold",
    "journal 10: ivory rhythm from Solea responsible expectations in ivory"
  ],
  "consultationPageColourSequence": [
    "consultation 1: gold rhythm from Solea hero promise in gold",
    "consultation 2: ivory rhythm from Solea trust position in ivory",
    "consultation 3: dark rhythm from Solea care route in dark",
    "consultation 4: bronze rhythm from Solea consultation path in bronze",
    "consultation 5: sage rhythm from Solea treatment navigation in sage",
    "consultation 6: cream rhythm from Solea human reassurance in cream",
    "consultation 7: gold rhythm from Solea education preview in gold",
    "consultation 8: ivory rhythm from Solea responsible expectations in ivory",
    "consultation 9: dark rhythm from Solea contact bridge in dark",
    "consultation 10: bronze rhythm from Solea closing identity in bronze"
  ],
  "contactPageColourSequence": [
    "contact 1: ivory rhythm from Solea trust position in ivory",
    "contact 2: dark rhythm from Solea care route in dark",
    "contact 3: bronze rhythm from Solea consultation path in bronze",
    "contact 4: sage rhythm from Solea treatment navigation in sage",
    "contact 5: cream rhythm from Solea human reassurance in cream",
    "contact 6: gold rhythm from Solea education preview in gold",
    "contact 7: ivory rhythm from Solea responsible expectations in ivory",
    "contact 8: dark rhythm from Solea contact bridge in dark",
    "contact 9: bronze rhythm from Solea closing identity in bronze",
    "contact 10: gold rhythm from Solea hero promise in gold"
  ],
  "forbiddenColourPatterns": [
    "Do not flatten the site into repeated centered card stacks",
    "Do not use gray placeholders",
    "Do not invent testimonials, guarantees, prices, results, or credentials",
    "Do not let desktop collapse into a narrow mobile column"
  ]
}
```
