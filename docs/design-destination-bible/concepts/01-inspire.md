# 01-inspire — Editorial Botanical Atelier

## Visual Thesis

Inspire uses high-end editorial, botanical, quiet confidence pacing with asymmetric editorial spread with portrait and art panel.

## Colour Thesis

ivory, deep green, sage, muted gold

## Systems

- Header: `editorial-index-header`
- Mobile: `dark-sheet`
- Footer: `editorial-bridge`
- Homepage anatomy: `editorial-spread`
- Internal page anatomy: `process-rail`
- Component strategy: editorial-spread with single-rule calls to action
- CTA strategy: split-quiet
- Image strategy: Selective full transparent portraits in sections 1, 5, and 8; object-fit contain only.

## Homepage Colour Sequence

1. Inspire hero promise in sage
2. Inspire trust position in ivory
3. Inspire care route in gold
4. Inspire consultation path in cream
5. Inspire treatment navigation in bronze
6. Inspire human reassurance in dark
7. Inspire education preview in sage
8. Inspire responsible expectations in ivory
9. Inspire contact bridge in gold
10. Inspire closing identity in cream

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
  "conceptId": "01-inspire",
  "colourThesis": "ivory, deep green, sage, muted gold",
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
  "cardSurfaceStrategy": "route-ledger; no universal cream-card default",
  "buttonStrategy": "split-quiet",
  "footerColour": "Inspire closing identity in cream",
  "mobileMenuColour": "Inspire care route in gold",
  "homepageSectionColourSequence": [
    "Inspire hero promise in sage",
    "Inspire trust position in ivory",
    "Inspire care route in gold",
    "Inspire consultation path in cream",
    "Inspire treatment navigation in bronze",
    "Inspire human reassurance in dark",
    "Inspire education preview in sage",
    "Inspire responsible expectations in ivory",
    "Inspire contact bridge in gold",
    "Inspire closing identity in cream"
  ],
  "aboutPageColourSequence": [
    "about 1: gold rhythm from Inspire care route in gold",
    "about 2: cream rhythm from Inspire consultation path in cream",
    "about 3: bronze rhythm from Inspire treatment navigation in bronze",
    "about 4: dark rhythm from Inspire human reassurance in dark",
    "about 5: sage rhythm from Inspire education preview in sage",
    "about 6: ivory rhythm from Inspire responsible expectations in ivory",
    "about 7: gold rhythm from Inspire contact bridge in gold",
    "about 8: cream rhythm from Inspire closing identity in cream",
    "about 9: sage rhythm from Inspire hero promise in sage",
    "about 10: ivory rhythm from Inspire trust position in ivory"
  ],
  "carePageColourSequence": [
    "care 1: cream rhythm from Inspire consultation path in cream",
    "care 2: bronze rhythm from Inspire treatment navigation in bronze",
    "care 3: dark rhythm from Inspire human reassurance in dark",
    "care 4: sage rhythm from Inspire education preview in sage",
    "care 5: ivory rhythm from Inspire responsible expectations in ivory",
    "care 6: gold rhythm from Inspire contact bridge in gold",
    "care 7: cream rhythm from Inspire closing identity in cream",
    "care 8: sage rhythm from Inspire hero promise in sage",
    "care 9: ivory rhythm from Inspire trust position in ivory",
    "care 10: gold rhythm from Inspire care route in gold"
  ],
  "laserPageColourSequence": [
    "laser 1: bronze rhythm from Inspire treatment navigation in bronze",
    "laser 2: dark rhythm from Inspire human reassurance in dark",
    "laser 3: sage rhythm from Inspire education preview in sage",
    "laser 4: ivory rhythm from Inspire responsible expectations in ivory",
    "laser 5: gold rhythm from Inspire contact bridge in gold",
    "laser 6: cream rhythm from Inspire closing identity in cream",
    "laser 7: sage rhythm from Inspire hero promise in sage",
    "laser 8: ivory rhythm from Inspire trust position in ivory",
    "laser 9: gold rhythm from Inspire care route in gold",
    "laser 10: cream rhythm from Inspire consultation path in cream"
  ],
  "skinPageColourSequence": [
    "skin 1: dark rhythm from Inspire human reassurance in dark",
    "skin 2: sage rhythm from Inspire education preview in sage",
    "skin 3: ivory rhythm from Inspire responsible expectations in ivory",
    "skin 4: gold rhythm from Inspire contact bridge in gold",
    "skin 5: cream rhythm from Inspire closing identity in cream",
    "skin 6: sage rhythm from Inspire hero promise in sage",
    "skin 7: ivory rhythm from Inspire trust position in ivory",
    "skin 8: gold rhythm from Inspire care route in gold",
    "skin 9: cream rhythm from Inspire consultation path in cream",
    "skin 10: bronze rhythm from Inspire treatment navigation in bronze"
  ],
  "resultsPageColourSequence": [
    "results 1: sage rhythm from Inspire education preview in sage",
    "results 2: ivory rhythm from Inspire responsible expectations in ivory",
    "results 3: gold rhythm from Inspire contact bridge in gold",
    "results 4: cream rhythm from Inspire closing identity in cream",
    "results 5: sage rhythm from Inspire hero promise in sage",
    "results 6: ivory rhythm from Inspire trust position in ivory",
    "results 7: gold rhythm from Inspire care route in gold",
    "results 8: cream rhythm from Inspire consultation path in cream",
    "results 9: bronze rhythm from Inspire treatment navigation in bronze",
    "results 10: dark rhythm from Inspire human reassurance in dark"
  ],
  "journalPageColourSequence": [
    "journal 1: ivory rhythm from Inspire responsible expectations in ivory",
    "journal 2: gold rhythm from Inspire contact bridge in gold",
    "journal 3: cream rhythm from Inspire closing identity in cream",
    "journal 4: sage rhythm from Inspire hero promise in sage",
    "journal 5: ivory rhythm from Inspire trust position in ivory",
    "journal 6: gold rhythm from Inspire care route in gold",
    "journal 7: cream rhythm from Inspire consultation path in cream",
    "journal 8: bronze rhythm from Inspire treatment navigation in bronze",
    "journal 9: dark rhythm from Inspire human reassurance in dark",
    "journal 10: sage rhythm from Inspire education preview in sage"
  ],
  "consultationPageColourSequence": [
    "consultation 1: cream rhythm from Inspire closing identity in cream",
    "consultation 2: sage rhythm from Inspire hero promise in sage",
    "consultation 3: ivory rhythm from Inspire trust position in ivory",
    "consultation 4: gold rhythm from Inspire care route in gold",
    "consultation 5: cream rhythm from Inspire consultation path in cream",
    "consultation 6: bronze rhythm from Inspire treatment navigation in bronze",
    "consultation 7: dark rhythm from Inspire human reassurance in dark",
    "consultation 8: sage rhythm from Inspire education preview in sage",
    "consultation 9: ivory rhythm from Inspire responsible expectations in ivory",
    "consultation 10: gold rhythm from Inspire contact bridge in gold"
  ],
  "contactPageColourSequence": [
    "contact 1: sage rhythm from Inspire hero promise in sage",
    "contact 2: ivory rhythm from Inspire trust position in ivory",
    "contact 3: gold rhythm from Inspire care route in gold",
    "contact 4: cream rhythm from Inspire consultation path in cream",
    "contact 5: bronze rhythm from Inspire treatment navigation in bronze",
    "contact 6: dark rhythm from Inspire human reassurance in dark",
    "contact 7: sage rhythm from Inspire education preview in sage",
    "contact 8: ivory rhythm from Inspire responsible expectations in ivory",
    "contact 9: gold rhythm from Inspire contact bridge in gold",
    "contact 10: cream rhythm from Inspire closing identity in cream"
  ],
  "forbiddenColourPatterns": [
    "Do not flatten the site into repeated centered card stacks",
    "Do not use gray placeholders",
    "Do not invent testimonials, guarantees, prices, results, or credentials",
    "Do not let desktop collapse into a narrow mobile column"
  ]
}
```
