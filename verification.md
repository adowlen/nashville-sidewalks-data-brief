# Verification - Nashville Sidewalks Inventory brief (2026-11-10)

## Pre-flight audit (Standards Section 10, hard gate)

Audit script: code/audit_section10.py; full output: data/audit_output.txt. Ran BEFORE stats and prose. Result: PASS on every applicable check.

- Zero/null sentinel handling: RepairScoreWalkNBike is positive on 3,720 segments, 0 on 8,859, missing on 2,359. RepairConstructionCost is positive on 1,771, 0 on 10,808, missing on 2,359. Shape__Length is positive on 14,900, missing on 38, with no zero or negative values. 0, negative, and missing values are mapped to unknown and excluded from every score, cost, and length base; the audit asserts determined + not-determined = 14,938 for each field. DateRepaired carries no sentinel dates (no year before 1990, no 1970 values, no raw 0 or negative values among the 2,182 recorded dates).
- Polarity / matched-vs-excluded for the cost filter: matched sample (first 3 segments with RepairConstructionCost > 0) and excluded sample (first 3 with cost 0 or missing) are printed in data/audit_output.txt; the audit asserts every matched row is positive and every excluded row is not. The inequality direction (positive only) was verified against both samples.
- Numerator/denominator unit agreement: condition shares divide segments by segments and length by length in two separate, labeled computations (segment shares on 14,938; length shares on the 14,900 segments with a recorded length). Cost sums and medians use only the 1,771 cost-carrying segments; score medians and means use only the 3,720 scored segments unless a base is printed otherwise. No segment count is divided by a length or the reverse.
- Counter of ALL unique values for every categorical column used: Condition (12 raw values), District (90 raw values), Side (26 raw values), SidewalkWidth (237 raw values, a text field), OnStreet (3,232 values) - full counters in data/audit_output.txt. The counters, not assumptions, drove the normalizations: Condition merges only case/spacing variants of Good, Fair, and Poor (blank, space, NA, 31, and Goo counted Unknown, 1,777 segments); District figures use only the 14,757 segments naming exactly one district number 1-35 (150 segments name two or three districts, 31 name none or an unreadable value, including one District value that reads Good).
- Physical scale (Section 10.2): total recorded length is 7,400,787.5 feet on 14,900 segments. The Shape__Length field alias in the layer metadata is "Length (ft)" and the service spatial reference is EPSG:2274 (Tennessee State Plane, feet), so the native unit is feet as served; mile figures are derived (feet / 5,280) and labeled derived wherever printed: total 1,401.7 miles; Poor 141.6 miles; Fair and Poor together 394.5 miles.
- Join hygiene: NO external join was performed. The crash-layer comparison uses published city-level figures only, because the sidewalk District field is a Metro Council district while the crash layer's published geography is precinct and ZIP code and no verified crosswalk exists in this package. The non-join is stated in the brief itself as a limitation; no district-level crash figure is claimed.
- Internal control groups (Section 10.2): (1) District totals: the District counter sums to 14,938 = the pulled row count (asserted in the audit). (2) Repaired-vs-not condition check: segments with a recorded DateRepaired are currently recorded Good at 82.1 percent (1,792 of 2,182), against 59.6 percent Good among the 12,756 segments with no repair date. The repair-date field therefore behaves the way a completed-repair record should (dated segments skew Good), which supports reading DateRepaired as a repair record rather than a random date field. (3) Length-weighted vs count shares as a cross-check: Poor is 9.7 percent by segment count and 10.1 percent by length; the two bases agree in substance, so the condition distribution is not an artifact of segment fragmentation.

Key audit lines (full file: data/audit_output.txt):
```
ROWS 14938
OBJECTID unique 14938
COUNTER Condition n_unique=12
  'GOOD': 9010
  'FAIR': 2308
  'POOR': 1454
  ' ': 992
  '': 770
  'Good': 386
  'NA': 13
NUMERIC RepairScoreWalkNBike present=12579 missing=2359 zero=8859 negative=0 positive=3720 min=0.0 max=175.0
NUMERIC RepairConstructionCost present=12579 missing=2359 zero=10808 negative=0 positive=1771 min=0.0 max=850143.79
  positive cost distinct values 765 top repeated positive costs [(55158.00029412, 34), (19698.88052632, 19), (18755.06, 18)]
NUMERIC Shape__Length present=14900 missing=38 zero=0 negative=0 positive=14900
DATES DateRepaired present=2182 missing=12756 min=1998-12-31 max=2024-06-06
PHYSICAL SCALE: total Shape__Length (positive values only) = 7400787.5 native units (feet, per the field alias and EPSG:2274)
CONTROL district totals: sum of District counter = 14938 = rows 14938 OK
```

## Methods checklist

- Base rates and exposure: condition is reported both by segment count and by recorded length (the exposure-style check this inventory supports); the two bases are printed separately and never mixed. The inventory holds only inventoried segments: it contains no count of streets without sidewalks and no walking-volume measure, so no completeness rate and no crash rate is computed. Stated in the brief Methods and in the crash-comparison section.
- Direction of causality: no causal claim is made. In particular, no claim connects sidewalk condition to crashes; the crash comparison is city-level context with different populations, labeled as such.
- Category and definition changes over the window: the layer is a current snapshot with no condition time series, so no trend is computed. Recording-practice variation inside the snapshot is documented instead: 12 raw Condition values, 90 raw District values, and district coverage that varies sharply (District 33: 26.5 percent Unknown condition and 33 scored segments of 1,001; District 31: 12.0 percent Unknown and 13 scored of 923). The brief prints those coverage figures next to the low Poor counts for those districts.
- Exact date range: inventory snapshot pulled November 10, 2026; service data last edited November 9, 2026. DateRepaired range December 31, 1998 to June 6, 2024 (America/Chicago local dates), printed in the brief.
- Match rates: no join, so no join match rate applies. Field completeness printed instead: condition determined 88.1 percent (13,161 of 14,938), length recorded 99.7 percent, repair score positive 24.9 percent, repair cost positive 11.9 percent, repair date recorded 14.6 percent, single-district assignment 98.8 percent (14,757 of 14,938).
- Small counts: every district has at least 30 segments (smallest is District 23 with 53), so no district is flagged on the segment base; district score means are printed only with their scored-segment bases, and the brief restricts its highest-mean statement to districts with 30 or more scored segments. Poor-segment cost figures rest on 69 segments and are printed with that count.
- Official definitions: the layer metadata defines no Condition scale and no RepairScoreWalkNBike or RepairConstructionCost population rule; the layer description references a Gap field (0 = existing sidewalk, 1 = existing gap) that is not present in this view. The brief assigns no definitions the metadata does not carry and asks for them in Who can act.

## Independent verification

code/verify_independent.py (second implementation, pandas, plus a live server count) recomputed the decisive figures from the raw CSV: 23 of 23 checks PASS (data/verify_independent_output.json), including rows, live server count, all four normalized condition counts, the Poor share, total and Poor length, score count/median/90th percentile, cost count/sum/median, cost-on-Good and score-on-Poor coverage, District 11 and District 21 Poor counts, the single-district total, the repair-dated count, and the repaired-group Good share.

## Sync gate

README dependency list matches the code's actual imports (standard library; pandas in the verifier only; matplotlib in charts only). Every number in brief-draft.md was cross-checked against the final stats.json after the last build_stats.py run, including the derived figures (1,401.7 total miles; 141.6 Poor miles; 394.5 Fair-or-Poor miles; 91.6 percent of the recorded cost sum on Good segments; about 1 in 4 segments Fair or Poor). Social copy figures match stats.json. The raw CSV contains street names and segment fields only - no personal data (no names, addresses of individuals, phone numbers, or emails; OnStreet/FromStreet/ToStreet are street names) - so the raw snapshot can ship in the repository; that check is recorded here and in sources.md.

## Story Gate (Standards Section 13)

- Recorded thesis (before analysis) and its revision after the audit: see reviewer-notes.md. The brief's findings are ordered to serve the revised thesis.
- Human-scale conversion: "about 1 in 4 inventoried segments is recorded Fair or Poor" (derived from 3,762 of 14,938, 25.2 percent) and the length conversions (Poor 141.6 miles, Fair or Poor 394.5 miles, both derived), recomputed from stats.json figures.
- Cold-reader evidence: INTERNAL cold read (no external reader was available in this build run; this is recorded honestly rather than attributed to an outside person). A fresh reading of only brief-draft.md returned: (1) Point in one sentence: "About a quarter of Nashville's inventoried sidewalk segments are recorded Fair or Poor - concentrated by share in District 11 and by count in District 21 - and the inventory's cost field mostly covers Good segments, so its $59.7 million sum cannot be read as the repair backlog." This matches the revised thesis in substance. (2) Most memorable number: 4.7 percent - the share of Poor segments carrying a recorded repair cost, against 97.3 percent carrying a repair score; it is the headline finding carried in the title's second clause, the summary, and hero-headline.txt. (3) Where it got bored or lost: the width paragraph is the least load-bearing passage; it is kept short, placed after the repair sections, and no figure in it carries the thesis. Gate: PASS; no figure changed in the story pass.


## Parent QA additions (2026-11-10 morning run)

- Chart label fix: the first chart render clipped the District 11 annotation and the base footnotes on chart_condition_distribution.png, chart_condition_by_length.png, and chart_poor_share_by_district.png. code/charts.py was patched (wrapped two-line axis labels, expanded x-limits) and all charts regenerated; the parent viewed the regenerated district and condition charts and confirmed every annotation and footnote is fully inside the frame. No figure changed.
- Hero: generated illustration composited with code/hero_composite.py (headline 25.2 percent, Fair-or-Poor) and viewed by the parent - narrative scene (cracked foreground segments, survey crew, smooth segment with wheelchair and stroller users, Nashville skyline), brand palette, headline fully legible on the dark scrim field. PASS.
- Parent spot-check with a third implementation reproduced the raw Condition counter, the cost-carrying count (1,771), and the recorded cost sum ($59,743,161.85) exactly.
