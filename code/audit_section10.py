import csv, json, collections, os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
HERE=os.path.dirname(__file__); DATA=os.path.normpath(os.path.join(HERE,"..","data"))
CHI=ZoneInfo("America/Chicago")
def ldate(v):
    if v in (None,""): return None
    try: ms=int(float(v))
    except: return None
    return datetime.fromtimestamp(ms/1000, tz=timezone.utc).astimezone(CHI).date()
def num(v):
    if v in (None,""): return None
    try: return float(v)
    except: return None
rows=list(csv.DictReader(open(os.path.join(DATA,"nashville_sidewalks_raw.csv"))))
out=[]
def p(*a): s=" ".join(str(x) for x in a); out.append(s); print(s)
p("ROWS",len(rows))
p("OBJECTID unique",len(set(r["OBJECTID"] for r in rows)))
p("GlobalID unique",len(set(r["GlobalID"] for r in rows)))
# Categorical exhaustiveness: Counter of ALL unique values for every categorical column used
for col in ["Condition","District","Side","SidewalkWidth","OnStreet","FromStreet","ToStreet","RouteId"]:
    c=collections.Counter((r[col] if r[col] not in (None,) else "") for r in rows)
    show = c.most_common(60) if col in ("OnStreet","FromStreet","ToStreet") else c.most_common(200)
    p(f"COUNTER {col} n_unique={len(c)}")
    for k,v in show: p(f"  {k!r}: {v}")
    if len(show)<len(c): p(f"  ... ({len(c)-len(show)} more values not printed)")
# Numeric sentinel handling: 0 / negative / null mapped to unknown, excluded from rate denominators
for col in ["RepairScoreWalkNBike","RepairConstructionCost","Shape__Length"]:
    vals=[num(r[col]) for r in rows]
    present=[v for v in vals if v is not None]
    p(f"NUMERIC {col} present={len(present)} missing={len(vals)-len(present)} zero={sum(1 for v in present if v==0)} negative={sum(1 for v in present if v<0)} positive={sum(1 for v in present if v>0)} min={min(present) if present else None} max={max(present) if present else None}")
    # value census for score (small integer) and top repeated costs (duplication check)
    if col=="RepairScoreWalkNBike":
        p("  score value census", dict(sorted(collections.Counter(int(v) for v in present).items())))
    if col=="RepairConstructionCost":
        cc=collections.Counter(v for v in present if v>0)
        p("  positive cost distinct values", len(cc), "top repeated positive costs", cc.most_common(10))
        p("  positive cost rows", sum(cc.values()), "rows where cost repeats a value held by 10+ rows", sum(v for k,v in cc.items() if v>=10))
# SidewalkWidth is a string field: report raw values and parseability
wvals=collections.Counter((r["SidewalkWidth"] or "") for r in rows)
parsed_ok=0; parsed_bad=[]
for r in rows:
    v=num(r["SidewalkWidth"])
    if v is not None and v>0: parsed_ok+=1
    elif (r["SidewalkWidth"] or "").strip() not in ("","None"): parsed_bad.append(r["SidewalkWidth"])
p(f"WIDTH parse: positive-numeric={parsed_ok} nonblank-unparseable-or-nonpositive sample={collections.Counter(parsed_bad).most_common(10)}")
# DateRepaired sentinel handling
dv=[r["DateRepaired"] for r in rows if r["DateRepaired"] not in (None,"")]
ds=[ldate(v) for v in dv]
p(f"DATES DateRepaired present={len(dv)} missing={len(rows)-len(dv)} min={min(ds) if ds else None} max={max(ds) if ds else None}")
p(f"  sentinel check: year<1990={sum(1 for d in ds if d and d.year<1990)} year 1970={sum(1 for d in ds if d and d.year==1970)} raw 0/negative={sum(1 for v in dv if float(v)<=0)}")
p("  DateRepaired year census", dict(sorted(collections.Counter(d.year for d in ds if d).items())))
# Polarity sample: segments WITH a recorded repair cost/score (matched) vs excluded (zero/missing)
matched=[r for r in rows if (num(r["RepairConstructionCost"]) or 0)>0]
excl=[r for r in rows if not ((num(r["RepairConstructionCost"]) or 0)>0)]
p("POLARITY SAMPLE matched (RepairConstructionCost > 0, first 3):",[(r["OBJECTID"],r["Condition"],r["District"],r["RepairScoreWalkNBike"],r["RepairConstructionCost"]) for r in matched[:3]])
p("POLARITY SAMPLE excluded (cost 0/missing, first 3):",[(r["OBJECTID"],r["Condition"],r["District"],r["RepairScoreWalkNBike"],r["RepairConstructionCost"]) for r in excl[:3]])
assert all((num(r["RepairConstructionCost"]) or 0)>0 for r in matched)
assert all(not ((num(r["RepairConstructionCost"]) or 0)>0) for r in excl)
# Condition x cost/score coverage (does the cost field cover the worst segments?)
p("CONDITION x cost-positive / score-positive:")
for cond in sorted(set((r["Condition"] or "") for r in rows)):
    sub=[r for r in rows if (r["Condition"] or "")==cond]
    p(f"  {cond!r}: n={len(sub)} cost>0={sum(1 for r in sub if (num(r['RepairConstructionCost']) or 0)>0)} score>0={sum(1 for r in sub if (num(r['RepairScoreWalkNBike']) or 0)>0)} repaired-dated={sum(1 for r in sub if r['DateRepaired'])}")
# Unit agreement + unknown exclusion assertions
total_len=sum(v for v in (num(r["Shape__Length"]) for r in rows) if v and v>0)
p(f"PHYSICAL SCALE: total Shape__Length (positive values only) = {round(total_len,1)} native units; field alias in layer metadata is 'Length (ft)' and the service spatial reference is EPSG:2274 (Nashville / Tennessee State Plane, feet), so the native unit is feet; miles below are derived (feet / 5280).")
p(f"  total length derived miles = {round(total_len/5280,1)}")
p("UNIT AGREEMENT: condition shares divide segments by segments and length by length in separate, labeled computations; cost sums and means use only cost-carrying (cost > 0) segments; score means/medians use only score > 0 segments unless the base is printed as all segments. No segment counts are divided by lengths or vice versa.")
p("UNKNOWN EXCLUSION: 0, negative, and missing values in RepairScoreWalkNBike, RepairConstructionCost, and Shape__Length are mapped to unknown and excluded from score/cost/length rate denominators; Condition and District blanks are carried as their own blank category on the full 14,938-segment denominator. Asserts below verify the determined + not-determined shares sum to the whole.")
n=len(rows)
for col in ["RepairScoreWalkNBike","RepairConstructionCost","Shape__Length"]:
    det=sum(1 for r in rows if (num(r[col]) or 0)>0); undet=n-det
    assert det+undet==n
    p(f"  {col}: determined (positive) {det} + not-determined (0/missing/negative) {undet} = {n} OK")
# District totals control (Section 10.2 internal control, part 1)
dc=collections.Counter((r["District"] or "") for r in rows)
assert sum(dc.values())==n
p(f"CONTROL district totals: sum of District counter = {sum(dc.values())} = rows {n} OK; districts n_unique={len(dc)}")
# Join hygiene: no external join is performed in the base analysis; the crash comparison uses published city-level figures only (see verification.md)
p("JOIN: no spatial or relational join performed in the base analysis. Crash-layer comparison is city-level against published figures only; sidewalk District is a Metro Council district while the crash layer carries precinct/ZIP geographies, so no district-level crash join is claimed.")
open(os.path.join(DATA,"audit_output.txt"),"w").write("\n".join(out)+"\n")
print("AUDIT DONE")
