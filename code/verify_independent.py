# Second implementation (pandas) + live server count; independent of build_stats.py
import pandas as pd, json, os, urllib.request, urllib.parse
PKG=os.path.normpath(os.path.join(os.path.dirname(__file__),".."))
S=json.load(open(os.path.join(PKG,"stats.json")))
df=pd.read_csv(os.path.join(PKG,"data","nashville_sidewalks_raw.csv"), dtype=str, keep_default_na=False)
def fnum(s): return pd.to_numeric(s, errors="coerce")
cond=df["Condition"].str.strip().str.upper().map(lambda s: s.title() if s in ("GOOD","FAIR","POOR") else "Unknown")
score=fnum(df["RepairScoreWalkNBike"]); cost=fnum(df["RepairConstructionCost"]); leng=fnum(df["Shape__Length"])
def single_dist(v):
    v=(v or "").strip(); parts=[p.strip() for p in v.split(",")]
    if len(parts)==1 and parts[0].isdigit() and 1<=int(parts[0])<=35: return int(parts[0])
    return None
dist=df["District"].map(single_dist)
checks=[]
def chk(name, got, want, tol=0): checks.append({"check":name,"got":got,"want":want,"pass":bool(abs((got or 0)-(want or 0))<=tol) if isinstance(got,(int,float)) and isinstance(want,(int,float)) else bool(got==want)})
chk("rows", len(df), S["rows"])
chk("server_count_live", json.load(urllib.request.urlopen("https://services2.arcgis.com/HdTo6HJqh92wn4D8/arcgis/rest/services/Sidewalks_View/FeatureServer/0/query?"+urllib.parse.urlencode({"where":"1=1","returnCountOnly":"true","f":"json"}), timeout=60))["count"], S["server_count"])
for c in ["Good","Fair","Poor","Unknown"]: chk(f"condition_{c}", int((cond==c).sum()), S["condition_counter"][c])
chk("poor_pct", round(100*(cond=="Poor").mean(),1), S["condition_pct"]["Poor"])
chk("total_length_ft", float(leng[leng>0].sum()), S["total_length_ft"], tol=1.0)
chk("poor_length_ft", float(leng[(leng>0)&(cond=="Poor")].sum()), S["length_by_condition_ft"]["Poor"], tol=1.0)
sp=score[score>0]; chk("score_positive_n", int((score>0).sum()), S["score_positive_n"]); chk("score_median", float(sp.median()), float(S["score"]["median"])); chk("score_p90_nearest_rank", float(sorted(sp)[min(len(sp)-1,int(0.9*len(sp)))]), float(S["score"]["p90"]))
cp=cost[cost>0]; chk("cost_carrying_n", int((cost>0).sum()), S["cost"]["n"]); chk("cost_sum", float(cp.sum()), S["cost"]["sum"], tol=1.0); chk("cost_median", float(cp.median()), float(S["cost"]["median"]), tol=0.01)
chk("cost_on_good_n", int(((cost>0)&(cond=="Good")).sum()), S["cost_by_condition"]["Good"]["cost_carrying_n"])
chk("score_on_poor_n", int(((score>0)&(cond=="Poor")).sum()), S["cost_by_condition"]["Poor"]["score_positive_n"])
d11=df[dist==11]; chk("district11_n", len(d11), S["by_district"]["11"]["n"]); chk("district11_poor", int((cond[dist==11]=="Poor").sum()), S["by_district"]["11"]["poor_n"])
chk("district21_poor", int((cond[dist==21]=="Poor").sum()), S["by_district"]["21"]["poor_n"])
chk("single_district_n", int(dist.notna().sum()), S["district_single_n"])
rep=pd.to_datetime(df["DateRepaired"], unit="ms", utc=True, errors="coerce")
chk("repaired_dated_n", int(rep.notna().sum()), S["control_repaired_vs_not"]["repaired_dated_n"])
chk("good_share_repaired_pct", round(100*(cond[rep.notna()]=="Good").mean(),1), S["control_repaired_vs_not"]["good_share_repaired_pct"])
res={"checks":checks,"pass":sum(1 for c in checks if c["pass"]),"total":len(checks)}
json.dump(res, open(os.path.join(PKG,"data","verify_independent_output.json"),"w"), indent=2)
print(res["pass"],"/",res["total"]); [print("FAIL",c) for c in checks if not c["pass"]]
