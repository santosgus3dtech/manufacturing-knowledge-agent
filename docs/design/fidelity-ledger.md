# Concept-to-implementation ledger

## Preserved

- Compact operations-console layout rather than a marketing landing page.
- Neutral surfaces with green, amber and red reserved for machine semantics.
- Desktop split between operational data and grounded evidence.
- Mobile machine cards, summary metrics, section tabs and fixed navigation.
- Visible retrieval scores, tool traces, deterministic quote details and evaluation metrics.

## Intentional deviations

- The implementation uses three machines because that is the complete synthetic fixture set.
- Decorative settings and recent-quote controls from the concept were omitted until they have real behavior.
- Machine details use a functional drawer; evidence rows expand inline.
- The desktop table collapses into cards based on its own container width, preventing clipped columns in the split view.
- Values come from the running API and evaluation dataset rather than static mockup text.

## Verification

- Browser QA: 1280 x 720 desktop and 390 x 844 mobile.
- Artifact captures: 1440 x 960 desktop and 390 x 844 mobile.
- No horizontal overflow or relevant console warnings/errors were observed.
