# Quote Model and Assumptions

## Direct costs

The quote model separates material, measured energy, machine time, labor, and packaging. Material cost uses part weight and the configured cost per gram. Machine time covers depreciation and routine maintenance rather than treating printer runtime as free.

## Failure buffer

The failure buffer applies to direct cost before margin. It represents expected rework for the specific process and should be based on measured history, not added as an unexplained markup. A new or unstable process receives a higher documented rate than a repeatable production profile.

## Margin

Margin is applied after direct cost and failure buffer. The calculator uses decimal arithmetic and rounds currency only at output boundaries. Marketplace or payment fees should be modeled explicitly when they apply instead of being hidden inside material cost.

## Review boundary

The estimate is decision support, not an accepted commercial offer. An operator must confirm quantity, geometry, material, lead time, finishing, packaging, and delivery requirements before a quote is released.
