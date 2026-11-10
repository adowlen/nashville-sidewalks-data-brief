import csv, json, collections, os, statistics
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
HERE=os.path.dirname(__file__); PKG=os.path.normpath(os.path.join(HERE,"..")); DATA=os.path.join(PKG,"data")
CHI=ZoneInfo("America/Chicago")
def ld(v):
    if v in (None,""): return None
    return datetime.fromtimestamp(int(float(v))/1000, tz=timezone.utc).astimezone(CHI).date()
def num(v):
    if v in (None,""): return None
    try: return float(v)
    except: return None
rows=list(csv.DictReader(open(os.path.join(DATA,"nashville_sidewalks_raw.csv"))))
N=len(rows)
def pct(n,d): return round(100*n/d,1) if d else None
# --- Condition normalization (documented in audit + brief): trim, casefold; GOOD-family variants merge; blank/space/NA/31 -> Unknown
def norm_condition(v):
    s=(v or "").strip().upper()
    if s in ("GOOD","FAIR","POOR"): return s.title()
    return "Unknown"
cond_raw=collections.Counter((r["Condition"] if r["Condition"] is not None else "") for r in rows)
cond=collections.Counter(norm_condition(r["Condition"]) for r in rows)
# --- District normalization: exactly one district number 1-35 -> that district; comma lists -> Multi; else Unknown
def norm_district(v):
    s=(v or "").strip()
    if not s: return ("Unknown",None)
    parts=[p.strip() for p in s.split(",")]
    if len(parts)>1: return ("Multi",None)
    if parts[0].isdigit() and 1<=int(parts[0])<=35: return ("Single",int(parts[0]))
    return ("Unknown",None)
dist_class=collections.Counter(norm_district(r["District"])[0] for r in rows)
# --- Length
lens={r["OBJECTID"]: (num(r["Shape__Length"]) if (num(r["Shape__Length"]) or 0)>0 else None) for r in rows}
total_len=sum(v for v in lens.values() if v)
len_by_cond=collections.defaultdict(float); len_known_by_cond=collections.Counter()
for r in rows:
    L=lens[r["OBJECTID"]]
    if L: len_by_cond[norm_condition(r["Condition"])]+=L; len_known_by_cond[norm_condition(r["Condition"])]+=1
len_base=sum(len_by_cond.values())
# --- Score / cost (positive only = determined)
scores=[num(r["RepairScoreWalkNBike"]) for r in rows if (num(r["RepairScoreWalkNBike"]) or 0)>0]
costs=[num(r["RepairConstructionCost"]) for r in rows if (num(r["RepairConstructionCost"]) or 0)>0]
def quantiles(vals):
    s=sorted(vals)
    def q(p): return s[min(len(s)-1, int(p*len(s)))]
    return {"n":len(s),"min":s[0],"median":statistics.median(s),"mean":round(statistics.mean(s),1),"p75":q(0.75),"p90":q(0.90),"max":s[-1]}
score_stats=quantiles(scores) if scores else {}
cost_stats={"n":len(costs),"sum":round(sum(costs),2),"median":statistics.median(costs) if costs else None,"mean":round(statistics.mean(costs),2) if costs else None,"max":max(costs) if costs else None}
both_pos=sum(1 for r in rows if (num(r["RepairScoreWalkNBike"]) or 0)>0 and (num(r["RepairConstructionCost"]) or 0)>0)
fields_missing=sum(1 for r in rows if r["RepairScoreWalkNBike"] in (None,"") and r["RepairConstructionCost"] in (None,""))
# cost by condition (normalized)
cost_by_cond={}
for c in ["Good","Fair","Poor","Unknown"]:
    sub=[num(r["RepairConstructionCost"]) for r in rows if norm_condition(r["Condition"])==c and (num(r["RepairConstructionCost"]) or 0)>0]
    sc=[num(r["RepairScoreWalkNBike"]) for r in rows if norm_condition(r["Condition"])==c and (num(r["RepairScoreWalkNBike"]) or 0)>0]
    cost_by_cond[c]={"segments":cond[c],"cost_carrying_n":len(sub),"cost_sum":round(sum(sub),2) if sub else 0,"cost_median":statistics.median(sub) if sub else None,"score_positive_n":len(sc),"score_median":statistics.median(sc) if sc else None}
# --- District panel (single-district rows only)
dist_rows=collections.defaultdict(list)
for r in rows:
    cls,d=norm_district(r["District"])
    if cls=="Single": dist_rows[d].append(r)
district_panel={}
for d in sorted(dist_rows):
    sub=dist_rows[d]; n=len(sub)
    poor=sum(1 for r in sub if norm_condition(r["Condition"])=="Poor")
    fair=sum(1 for r in sub if norm_condition(r["Condition"])=="Fair")
    unk=sum(1 for r in sub if norm_condition(r["Condition"])=="Unknown")
    sc=[num(r["RepairScoreWalkNBike"]) for r in sub if (num(r["RepairScoreWalkNBike"]) or 0)>0]
    co=[num(r["RepairConstructionCost"]) for r in sub if (num(r["RepairConstructionCost"]) or 0)>0]
    district_panel[str(d)]={"n":n,"poor_n":poor,"poor_pct":pct(poor,n),"fair_n":fair,"fair_poor_n":fair+poor,"fair_poor_pct":pct(fair+poor,n),"unknown_condition_n":unk,
      "score_positive_n":len(sc),"score_mean":round(statistics.mean(sc),1) if sc else None,"score_median":statistics.median(sc) if sc else None,"score_total":int(sum(sc)) if sc else 0,
      "cost_carrying_n":len(co),"cost_sum":round(sum(co),2) if co else 0,"small_base_flag": n<30}
single_n=sum(len(v) for v in dist_rows.values())
# --- DateRepaired / control group: condition among repaired-dated vs not
rep=[r for r in rows if ld(r["DateRepaired"])]
rep_years=collections.Counter(ld(r["DateRepaired"]).year for r in rep)
control={"repaired_dated_n":len(rep),
  "condition_among_repaired":dict(collections.Counter(norm_condition(r["Condition"]) for r in rep)),
  "condition_among_not_repaired":dict(collections.Counter(norm_condition(r["Condition"]) for r in rows if not ld(r["DateRepaired"]))),
  "good_share_repaired_pct":pct(sum(1 for r in rep if norm_condition(r["Condition"])=="Good"),len(rep)),
  "good_share_not_repaired_pct":pct(sum(1 for r in rows if not ld(r["DateRepaired"]) and norm_condition(r["Condition"])=="Good"), N-len(rep))}
# --- Width: single numeric values only; ranges counted separately
width_raw=collections.Counter((r["SidewalkWidth"] or "") for r in rows)
single_width=[]; range_n=0; width_blank=0
for r in rows:
    s=(r["SidewalkWidth"] or "").strip()
    if not s: width_blank+=1
    elif "-" in s: range_n+=1
    else:
        v=num(s)
        if v and v>0: single_width.append(v)
width_stats={"blank_n":width_blank,"range_string_n":range_n,"single_value_n":len(single_width),
  "single_value_counter_top":collections.Counter(single_width).most_common(8),
  "single_value_median_ft":statistics.median(single_width) if single_width else None,
  "under_5ft_n":sum(1 for v in single_width if v<5),"under_5ft_pct_of_single":pct(sum(1 for v in single_width if v<5),len(single_width))}
# top streets by Poor count
poor_by_street=collections.Counter((r["OnStreet"] or "").strip() for r in rows if norm_condition(r["Condition"])=="Poor")
stats={
 "dataset":"Nashville Sidewalks Inventory (Sidewalks_View, layer 0)","snapshot_date":"2026-11-10","rows":N,
 "unit":"one row = one sidewalk segment as served by the view","server_count":14938,
 "condition_raw_counter":{k:v for k,v in cond_raw.most_common()},
 "condition_counter":{k:cond[k] for k in ["Good","Fair","Poor","Unknown"]},
 "condition_pct":{k:pct(cond[k],N) for k in ["Good","Fair","Poor","Unknown"]},
 "condition_determined_n":cond["Good"]+cond["Fair"]+cond["Poor"],
 "total_length_ft":round(total_len,1),"total_length_miles_derived":round(total_len/5280,1),
 "length_n":sum(1 for v in lens.values() if v),"length_missing_n":N-sum(1 for v in lens.values() if v),
 "length_by_condition_ft":{k:round(len_by_cond[k],1) for k in ["Good","Fair","Poor","Unknown"]},
 "length_share_by_condition_pct":{k:pct(len_by_cond[k],len_base) for k in ["Good","Fair","Poor","Unknown"]},
 "score":score_stats,"score_positive_n":len(scores),"score_zero_or_missing_n":N-len(scores),
 "cost":cost_stats,"cost_carrying_pct_of_all":pct(len(costs),N),"cost_zero_or_missing_n":N-len(costs),
 "score_and_cost_both_positive_n":both_pos,"score_cost_fields_both_missing_n":fields_missing,
 "cost_by_condition":cost_by_cond,
 "district_class_counter":dict(dist_class),"district_single_n":single_n,"districts_with_segments":len(district_panel),
 "by_district":district_panel,
 "daterepaired":{"dated_n":len(rep),"range":[str(min(ld(r["DateRepaired"]) for r in rep)),str(max(ld(r["DateRepaired"]) for r in rep))],"by_year":{str(k):v for k,v in sorted(rep_years.items())}},
 "control_repaired_vs_not":control,"width":width_stats,
 "top_poor_streets":[list(x) for x in poor_by_street.most_common(8)],
 "comparison_published":{"traffic_accidents_2026_11_02":{"crashes":222903,"fatalities":926,"pedestrian_fatalities":280,"pedestrian_share_of_fatalities_pct":30.2,"basis":"reported crashes Jan 1, 2019 to Oct 31, 2026, pulled Nov 2, 2026","repo":"https://github.com/adowlen/nashville-traffic-accidents-data-brief"}},
}
json.dump(stats, open(os.path.join(PKG,"stats.json"),"w"), indent=2)
with open(os.path.join(DATA,"condition_panel.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["condition_normalized","segments","pct_of_all_segments","length_ft","pct_of_total_length"])
    for k in ["Good","Fair","Poor","Unknown"]: w.writerow([k,cond[k],pct(cond[k],N),round(len_by_cond[k],1),pct(len_by_cond[k],len_base)])
with open(os.path.join(DATA,"district_panel.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["district","segments","poor_n","poor_pct","fair_poor_n","fair_poor_pct","unknown_condition_n","score_positive_n","score_mean","score_median","score_total","cost_carrying_n","cost_sum","small_base_flag"])
    for d,v in district_panel.items(): w.writerow([d,v["n"],v["poor_n"],v["poor_pct"],v["fair_poor_n"],v["fair_poor_pct"],v["unknown_condition_n"],v["score_positive_n"],v["score_mean"],v["score_median"],v["score_total"],v["cost_carrying_n"],v["cost_sum"],v["small_base_flag"]])
with open(os.path.join(DATA,"condition_raw_panel.csv"),"w",newline="") as f:
    w=csv.writer(f); w.writerow(["condition_as_recorded","segments"])
    for k,v in cond_raw.most_common(): w.writerow([k if k!="" else "(blank)",v])
print(json.dumps({"condition":stats["condition_counter"],"condition_pct":stats["condition_pct"],"miles":stats["total_length_miles_derived"],"score":score_stats,"cost":cost_stats,"cost_pct":stats["cost_carrying_pct_of_all"]},indent=1))
print("districts by poor_pct (n>=30):", sorted([(d,v["poor_pct"],v["n"],v["poor_n"]) for d,v in district_panel.items() if v["n"]>=30], key=lambda x:-x[1])[:8])
print("districts by score_total:", sorted([(d,v["score_total"],v["score_mean"],v["n"]) for d,v in district_panel.items()], key=lambda x:-x[1])[:8])
print("districts by score_mean (score n>=30):", sorted([(d,v["score_mean"],v["score_positive_n"]) for d,v in district_panel.items() if v["score_positive_n"]>=30], key=lambda x:-x[1])[:8])
print("control:",control)
print("width:",width_stats)
