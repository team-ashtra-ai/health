# 09-radiance — Service Route System

## Visual Thesis

A navigation-led premium route system. It should feel like a sophisticated service map.

## Colour Thesis

Cream/ivory base. Sage route panels dominate. Gold/bronze indicate active paths. Dark is reserved for route summary and footer.

## Systems

- Header: `route-map-header`
- Mobile: `studio-card`
- Footer: `warm-reassurance`
- Homepage anatomy: `contact-bridge`
- Internal page anatomy: `process-rail`
- Component strategy: atelier-frame with dark-anchor calls to action
- CTA strategy: whatsapp-strip
- Image strategy: Selective full transparent portraits in sections 1, 7, and 8; object-fit contain only.

## Homepage Colour Sequence

1. Ivory route-index hero
2. Sage route overview
3. Cream service matrix
4. Ivory consultation pathway
5. Sage safety route
6. Cream education map
7. Ivory results path
8. Sage journal route
9. Gold/bronze route CTA
10. Deep sage directory footer

## All Other Pages

Use route maps, side indices, path markers, and structured internal links.

## Forbidden Patterns

- No portrait-first design
- No generic cards
- No decorative blush sections.

## Colour Rhythm Contract

```json
{
  "conceptId": "09-radiance",
  "colourThesis": "Cream/ivory base. Sage route panels dominate. Gold/bronze indicate active paths. Dark is reserved for route summary and footer.",
  "dominantColourFamily": "dark",
  "secondaryColourFamily": "sage",
  "accentColourFamily": "ivory",
  "contrastTemperature": "high editorial",
  "darkUsage": "dominant structural field",
  "blushUsage": "rare or absent by contract",
  "sageUsage": "brand structure and quiet route support",
  "creamUsage": "reading relief and calm transitions",
  "goldBronzeUsage": "rules, markers, numerals, and selected CTA detail",
  "terracottaTaupeUsage": "earth warmth only when named by the destination",
  "cardSurfaceStrategy": "shape-field; no universal cream-card default",
  "buttonStrategy": "whatsapp-strip",
  "footerColour": "Deep sage directory footer",
  "mobileMenuColour": "Ivory route-index hero",
  "homepageSectionColourSequence": [
    "Ivory route-index hero",
    "Sage route overview",
    "Cream service matrix",
    "Ivory consultation pathway",
    "Sage safety route",
    "Cream education map",
    "Ivory results path",
    "Sage journal route",
    "Gold/bronze route CTA",
    "Deep sage directory footer"
  ],
  "aboutPageColourSequence": [
    "about 1: ivory rhythm from Ivory route-index hero",
    "about 2: sage rhythm from Sage route overview",
    "about 3: cream rhythm from Cream service matrix",
    "about 4: ivory rhythm from Ivory consultation pathway",
    "about 5: sage rhythm from Sage safety route",
    "about 6: cream rhythm from Cream education map",
    "about 7: ivory rhythm from Ivory results path",
    "about 8: sage rhythm from Sage journal route",
    "about 9: gold rhythm from Gold/bronze route CTA",
    "about 10: dark rhythm from Deep sage directory footer"
  ],
  "carePageColourSequence": [
    "care 1: sage rhythm from Sage route overview",
    "care 2: cream rhythm from Cream service matrix",
    "care 3: ivory rhythm from Ivory consultation pathway",
    "care 4: sage rhythm from Sage safety route",
    "care 5: cream rhythm from Cream education map",
    "care 6: ivory rhythm from Ivory results path",
    "care 7: sage rhythm from Sage journal route",
    "care 8: gold rhythm from Gold/bronze route CTA",
    "care 9: dark rhythm from Deep sage directory footer",
    "care 10: ivory rhythm from Ivory route-index hero"
  ],
  "laserPageColourSequence": [
    "laser 1: cream rhythm from Cream service matrix",
    "laser 2: ivory rhythm from Ivory consultation pathway",
    "laser 3: sage rhythm from Sage safety route",
    "laser 4: cream rhythm from Cream education map",
    "laser 5: ivory rhythm from Ivory results path",
    "laser 6: sage rhythm from Sage journal route",
    "laser 7: gold rhythm from Gold/bronze route CTA",
    "laser 8: dark rhythm from Deep sage directory footer",
    "laser 9: ivory rhythm from Ivory route-index hero",
    "laser 10: sage rhythm from Sage route overview"
  ],
  "skinPageColourSequence": [
    "skin 1: ivory rhythm from Ivory consultation pathway",
    "skin 2: sage rhythm from Sage safety route",
    "skin 3: cream rhythm from Cream education map",
    "skin 4: ivory rhythm from Ivory results path",
    "skin 5: sage rhythm from Sage journal route",
    "skin 6: gold rhythm from Gold/bronze route CTA",
    "skin 7: dark rhythm from Deep sage directory footer",
    "skin 8: ivory rhythm from Ivory route-index hero",
    "skin 9: sage rhythm from Sage route overview",
    "skin 10: cream rhythm from Cream service matrix"
  ],
  "resultsPageColourSequence": [
    "results 1: sage rhythm from Sage safety route",
    "results 2: cream rhythm from Cream education map",
    "results 3: ivory rhythm from Ivory results path",
    "results 4: sage rhythm from Sage journal route",
    "results 5: gold rhythm from Gold/bronze route CTA",
    "results 6: dark rhythm from Deep sage directory footer",
    "results 7: ivory rhythm from Ivory route-index hero",
    "results 8: sage rhythm from Sage route overview",
    "results 9: cream rhythm from Cream service matrix",
    "results 10: ivory rhythm from Ivory consultation pathway"
  ],
  "journalPageColourSequence": [
    "journal 1: cream rhythm from Cream education map",
    "journal 2: ivory rhythm from Ivory results path",
    "journal 3: sage rhythm from Sage journal route",
    "journal 4: gold rhythm from Gold/bronze route CTA",
    "journal 5: dark rhythm from Deep sage directory footer",
    "journal 6: ivory rhythm from Ivory route-index hero",
    "journal 7: sage rhythm from Sage route overview",
    "journal 8: cream rhythm from Cream service matrix",
    "journal 9: ivory rhythm from Ivory consultation pathway",
    "journal 10: sage rhythm from Sage safety route"
  ],
  "consultationPageColourSequence": [
    "consultation 1: sage rhythm from Sage journal route",
    "consultation 2: gold rhythm from Gold/bronze route CTA",
    "consultation 3: dark rhythm from Deep sage directory footer",
    "consultation 4: ivory rhythm from Ivory route-index hero",
    "consultation 5: sage rhythm from Sage route overview",
    "consultation 6: cream rhythm from Cream service matrix",
    "consultation 7: ivory rhythm from Ivory consultation pathway",
    "consultation 8: sage rhythm from Sage safety route",
    "consultation 9: cream rhythm from Cream education map",
    "consultation 10: ivory rhythm from Ivory results path"
  ],
  "contactPageColourSequence": [
    "contact 1: gold rhythm from Gold/bronze route CTA",
    "contact 2: dark rhythm from Deep sage directory footer",
    "contact 3: ivory rhythm from Ivory route-index hero",
    "contact 4: sage rhythm from Sage route overview",
    "contact 5: cream rhythm from Cream service matrix",
    "contact 6: ivory rhythm from Ivory consultation pathway",
    "contact 7: sage rhythm from Sage safety route",
    "contact 8: cream rhythm from Cream education map",
    "contact 9: ivory rhythm from Ivory results path",
    "contact 10: sage rhythm from Sage journal route"
  ],
  "forbiddenColourPatterns": [
    "No portrait-first design",
    "No generic cards",
    "No decorative blush sections."
  ]
}
```
