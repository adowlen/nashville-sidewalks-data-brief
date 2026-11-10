# Reviewer notes - Nashville Sidewalks Inventory brief (2026-11-10)

## Thesis recorded before analysis (Standards Section 13.1)
"Nashville's inventoried sidewalk network is mostly in serviceable condition, but poor-condition segments and the highest repair scores concentrate in a small number of council districts, and the recorded repair-cost field covers only part of the network, so its sum understates the full backlog."

## Thesis revision (after the audit, before drafting)
The concentration and partial-coverage clauses held: Poor segments concentrate by share in District 11 (30.7 percent, 175 of 570) and by count in District 21 (212), and the cost field covers only 1,771 of 14,938 segments (11.9 percent). The audit added a sharper finding the original thesis did not predict: the two repair fields cover different subpopulations. The score field covers Fair and Poor segments almost completely (98.6 and 97.3 percent) and Good segments almost not at all (0.3 percent), while the cost field sits mostly on Good segments (1,520 of its 1,771 carriers; $54,700,748.26 of its $59,743,161.85 sum). Only 263 segments carry both. Revised thesis, which the findings are ordered to serve: "About 1 in 4 of Nashville's inventoried sidewalk segments is recorded Fair or Poor, with Poor segments concentrated in Districts 11, 18, 17, and 21 - but the inventory's two repair fields describe different segments, so the recorded $59.7 million cost sum, which sits mostly on Good segments, cannot be read as the cost of repairing the Fair and Poor network."

## Claims most likely to be challenged
- The cost-field reading (91.6 percent of the recorded sum on Good segments): a reader may hold documentation showing RepairConstructionCost records something other than segment repair cost (for example associated construction value). The brief claims only where the recorded values sit, prints the coverage bases, and asks NDOT for the field definition in Who can act. It never calls the sum a backlog figure.
- The condition normalization: the raw field holds 12 values, and a reader could dispute merging Good (386) into Good or counting Goo as Unknown. The rule is printed in Methods, the full raw counter ships in data/condition_raw_panel.csv, and the affected counts are small (merges move 389 segments; Goo is 1 segment).
- District rankings: District is a messy field (90 raw values; zero-padded and unpadded duplicates, multi-district strings, one value reading Good). District figures use only the 14,757 single-district segments and the rule is printed. Districts 31 and 33 combine low Poor counts with low coverage (Unknown condition 12.0 and 26.5 percent; scored segments 13 and 33); the brief prints the coverage beside the counts and does not rank those districts as best-condition.
- Length basis: miles rest on the Shape__Length alias "Length (ft)" and EPSG:2274. Both are cited in Methods and sources.md; feet are the as-served unit and every mile figure is labeled derived.

## Incomplete checks
- No official definitions exist in the layer metadata for Condition, RepairScoreWalkNBike, or RepairConstructionCost, and the metadata description references a Gap field that is not present in this view; none could be checked beyond the metadata archived in the package. Recorded as an incomplete check; the brief restricts each field to its printed base accordingly.
- No district-level crash comparison could be performed: the crash layer's published geography is precinct and ZIP, the sidewalk District field is a council district, and no verified crosswalk exists in this package. The brief states this limitation in its own comparison section rather than implying a join.
- SidewalkWidth is a text field with range strings on 1,771 segments; no single width distribution over the full network can be computed without an assumption about ranges, so width is reported in three counted groups only.

## Surprises
- The cost field's placement: 91.6 percent of the recorded cost sum sits on Good segments, and only 69 of 1,454 Poor segments carry any recorded cost, while 97.3 percent of Poor segments carry a repair score.
- Repair dates stop at June 6, 2024 in a layer whose data was last edited November 9, 2026; 2,182 segments carry a repair date and 82.1 percent of them are currently recorded Good.
- Repeated cost values: 1,771 positive costs hold only 765 distinct values and the top value repeats on 34 segments, a pattern consistent with formula-generated estimates.
- Condition recording quality: 1,777 segments (11.9 percent) carry no usable condition value, including 992 segments whose Condition is a single space.

## Blocking defects
None. Hero image is intentionally not in this package: the parent generates the illustration and composites the headline (hero-headline.txt carries the approved headline). That is the standing build split, not a package defect.
