# 42-softline — Paper Editorial Clinic

## Visual Thesis

Vellum uses paper, editorial, tactile pacing with magazine style paper layout.

## Colour Thesis

ivory, paper, taupe, sage

## Systems

- Header: `botanical-stem-header`
- Mobile: `salon-overlay`
- Footer: `magazine-index`
- Homepage anatomy: `manifesto-line`
- Internal page anatomy: `contact-bridge`
- Component strategy: route-ledger with split-quiet calls to action
- CTA strategy: gold-mark
- Image strategy: Selective full transparent portraits in sections 2, 7, and 9; object-fit contain only.

## Homepage Colour Sequence

1. Vellum hero promise in sage
2. Vellum trust position in ivory
3. Vellum care route in bronze
4. Vellum consultation path in cream
5. Vellum treatment navigation in gold
6. Vellum human reassurance in dark
7. Vellum education preview in sage
8. Vellum responsible expectations in ivory
9. Vellum contact bridge in bronze
10. Vellum closing identity in cream

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
  "conceptId": "42-softline",
  "colourThesis": "ivory, paper, taupe, sage",
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
  "footerColour": "Vellum closing identity in cream",
  "mobileMenuColour": "Vellum consultation path in cream",
  "homepageSectionColourSequence": [
    "Vellum hero promise in sage",
    "Vellum trust position in ivory",
    "Vellum care route in bronze",
    "Vellum consultation path in cream",
    "Vellum treatment navigation in gold",
    "Vellum human reassurance in dark",
    "Vellum education preview in sage",
    "Vellum responsible expectations in ivory",
    "Vellum contact bridge in bronze",
    "Vellum closing identity in cream"
  ],
  "aboutPageColourSequence": [
    "about 1: cream rhythm from Vellum consultation path in cream",
    "about 2: gold rhythm from Vellum treatment navigation in gold",
    "about 3: dark rhythm from Vellum human reassurance in dark",
    "about 4: sage rhythm from Vellum education preview in sage",
    "about 5: ivory rhythm from Vellum responsible expectations in ivory",
    "about 6: bronze rhythm from Vellum contact bridge in bronze",
    "about 7: cream rhythm from Vellum closing identity in cream",
    "about 8: sage rhythm from Vellum hero promise in sage",
    "about 9: ivory rhythm from Vellum trust position in ivory",
    "about 10: bronze rhythm from Vellum care route in bronze"
  ],
  "carePageColourSequence": [
    "care 1: gold rhythm from Vellum treatment navigation in gold",
    "care 2: dark rhythm from Vellum human reassurance in dark",
    "care 3: sage rhythm from Vellum education preview in sage",
    "care 4: ivory rhythm from Vellum responsible expectations in ivory",
    "care 5: bronze rhythm from Vellum contact bridge in bronze",
    "care 6: cream rhythm from Vellum closing identity in cream",
    "care 7: sage rhythm from Vellum hero promise in sage",
    "care 8: ivory rhythm from Vellum trust position in ivory",
    "care 9: bronze rhythm from Vellum care route in bronze",
    "care 10: cream rhythm from Vellum consultation path in cream"
  ],
  "laserPageColourSequence": [
    "laser 1: dark rhythm from Vellum human reassurance in dark",
    "laser 2: sage rhythm from Vellum education preview in sage",
    "laser 3: ivory rhythm from Vellum responsible expectations in ivory",
    "laser 4: bronze rhythm from Vellum contact bridge in bronze",
    "laser 5: cream rhythm from Vellum closing identity in cream",
    "laser 6: sage rhythm from Vellum hero promise in sage",
    "laser 7: ivory rhythm from Vellum trust position in ivory",
    "laser 8: bronze rhythm from Vellum care route in bronze",
    "laser 9: cream rhythm from Vellum consultation path in cream",
    "laser 10: gold rhythm from Vellum treatment navigation in gold"
  ],
  "skinPageColourSequence": [
    "skin 1: sage rhythm from Vellum education preview in sage",
    "skin 2: ivory rhythm from Vellum responsible expectations in ivory",
    "skin 3: bronze rhythm from Vellum contact bridge in bronze",
    "skin 4: cream rhythm from Vellum closing identity in cream",
    "skin 5: sage rhythm from Vellum hero promise in sage",
    "skin 6: ivory rhythm from Vellum trust position in ivory",
    "skin 7: bronze rhythm from Vellum care route in bronze",
    "skin 8: cream rhythm from Vellum consultation path in cream",
    "skin 9: gold rhythm from Vellum treatment navigation in gold",
    "skin 10: dark rhythm from Vellum human reassurance in dark"
  ],
  "resultsPageColourSequence": [
    "results 1: ivory rhythm from Vellum responsible expectations in ivory",
    "results 2: bronze rhythm from Vellum contact bridge in bronze",
    "results 3: cream rhythm from Vellum closing identity in cream",
    "results 4: sage rhythm from Vellum hero promise in sage",
    "results 5: ivory rhythm from Vellum trust position in ivory",
    "results 6: bronze rhythm from Vellum care route in bronze",
    "results 7: cream rhythm from Vellum consultation path in cream",
    "results 8: gold rhythm from Vellum treatment navigation in gold",
    "results 9: dark rhythm from Vellum human reassurance in dark",
    "results 10: sage rhythm from Vellum education preview in sage"
  ],
  "journalPageColourSequence": [
    "journal 1: bronze rhythm from Vellum contact bridge in bronze",
    "journal 2: cream rhythm from Vellum closing identity in cream",
    "journal 3: sage rhythm from Vellum hero promise in sage",
    "journal 4: ivory rhythm from Vellum trust position in ivory",
    "journal 5: bronze rhythm from Vellum care route in bronze",
    "journal 6: cream rhythm from Vellum consultation path in cream",
    "journal 7: gold rhythm from Vellum treatment navigation in gold",
    "journal 8: dark rhythm from Vellum human reassurance in dark",
    "journal 9: sage rhythm from Vellum education preview in sage",
    "journal 10: ivory rhythm from Vellum responsible expectations in ivory"
  ],
  "consultationPageColourSequence": [
    "consultation 1: sage rhythm from Vellum hero promise in sage",
    "consultation 2: ivory rhythm from Vellum trust position in ivory",
    "consultation 3: bronze rhythm from Vellum care route in bronze",
    "consultation 4: cream rhythm from Vellum consultation path in cream",
    "consultation 5: gold rhythm from Vellum treatment navigation in gold",
    "consultation 6: dark rhythm from Vellum human reassurance in dark",
    "consultation 7: sage rhythm from Vellum education preview in sage",
    "consultation 8: ivory rhythm from Vellum responsible expectations in ivory",
    "consultation 9: bronze rhythm from Vellum contact bridge in bronze",
    "consultation 10: cream rhythm from Vellum closing identity in cream"
  ],
  "contactPageColourSequence": [
    "contact 1: ivory rhythm from Vellum trust position in ivory",
    "contact 2: bronze rhythm from Vellum care route in bronze",
    "contact 3: cream rhythm from Vellum consultation path in cream",
    "contact 4: gold rhythm from Vellum treatment navigation in gold",
    "contact 5: dark rhythm from Vellum human reassurance in dark",
    "contact 6: sage rhythm from Vellum education preview in sage",
    "contact 7: ivory rhythm from Vellum responsible expectations in ivory",
    "contact 8: bronze rhythm from Vellum contact bridge in bronze",
    "contact 9: cream rhythm from Vellum closing identity in cream",
    "contact 10: sage rhythm from Vellum hero promise in sage"
  ],
  "forbiddenColourPatterns": [
    "Do not flatten the site into repeated centered card stacks",
    "Do not use gray placeholders",
    "Do not invent testimonials, guarantees, prices, results, or credentials",
    "Do not let desktop collapse into a narrow mobile column"
  ]
}
```
