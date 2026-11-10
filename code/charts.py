import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
PKG=os.path.normpath(os.path.join(os.path.dirname(__file__),"..")); S=json.load(open(os.path.join(PKG,"stats.json")))
CHAR="#232323"; AMBER="#e8a33d"; TEAL="#2a9d8f"; LIGHT="#f2f2f2"; GREY="#9a9a9a"
plt.rcParams.update({"text.color":LIGHT,"axes.edgecolor":LIGHT,"axes.labelcolor":LIGHT,"xtick.color":LIGHT,"ytick.color":LIGHT,"figure.facecolor":CHAR,"axes.facecolor":CHAR,"savefig.facecolor":CHAR})
os.makedirs(os.path.join(PKG,"charts"),exist_ok=True)
def save(fig,n): fig.tight_layout(); fig.savefig(os.path.join(PKG,"charts",n),dpi=200); plt.close(fig)
# 1. Condition distribution by segment count (full denominator printed)
labels=["Good","Fair","Poor","Unknown"]; vals=[S["condition_counter"][k] for k in labels]
cols=[TEAL,AMBER,"#d95f4b",GREY]
fig,ax=plt.subplots(figsize=(8,4.6)); ax.barh(labels[::-1],vals[::-1],color=cols[::-1])
for i,v in enumerate(vals[::-1]): ax.text(v+180,i,f"{v:,} ({S['condition_pct'][labels[::-1][i]]}%)",va="center",fontsize=10)
ax.set_xlim(0,12000)
ax.set_xlabel("Segments (share of all 14,938 inventoried segments)\nCondition normalized: case/space variants merged, blank/NA counted Unknown", fontsize=9)
ax.set_title("Sidewalk condition as recorded - Nashville Sidewalks Inventory, Nov 10, 2026"); save(fig,"chart_condition_distribution.png")
# 2. Condition by length (separate basis, labeled)
lvals=[S["length_by_condition_ft"][k]/5280 for k in labels]
fig,ax=plt.subplots(figsize=(8,4.6)); ax.barh(labels[::-1],lvals[::-1],color=cols[::-1])
for i,v in enumerate(lvals[::-1]): ax.text(v+18,i,f"{v:,.1f} mi ({S['length_share_by_condition_pct'][labels[::-1][i]]}%)",va="center",fontsize=10)
ax.set_xlim(0,1100)
ax.set_xlabel("Length in miles (derived: Shape__Length feet / 5,280)\nBase = 14,900 segments with a recorded length, 1,401.7 miles total", fontsize=9)
ax.set_title("Condition by length - a different base than segment counts; do not compare directly"); save(fig,"chart_condition_by_length.png")
# 3. Worst districts by Poor share (single-district rows, n>=30 all districts qualify)
items=sorted([(d,v) for d,v in S["by_district"].items() if v["n"]>=30], key=lambda x: x[1]["poor_pct"])[-8:]
fig,ax=plt.subplots(figsize=(8,4.8)); ax.barh([f"District {d}" for d,_ in items],[v["poor_pct"] for _,v in items],color="#d95f4b")
for i,(d,v) in enumerate(items): ax.text(v["poor_pct"]+0.6,i,f"{v['poor_pct']}%  ({v['poor_n']} of {v['n']:,})",va="center",fontsize=9)
ax.set_xlim(0,44)
ax.set_xlabel("Share of the district's inventoried segments recorded Poor\n(single-district segments only; 14,757 of 14,938)", fontsize=9)
ax.set_title("Highest Poor shares by council district"); save(fig,"chart_poor_share_by_district.png")
# 4. The two repair fields cover different segments (bases printed on the graphic)
cats=["Repair score > 0\n(of 14,938 segments)","Repair cost > 0\n(of 14,938 segments)","Score > 0 among Poor\n(of 1,454 Poor)","Cost > 0 among Poor\n(of 1,454 Poor)","Cost > 0 among Good\n(of 9,399 Good)"]
vals2=[100*S["score_positive_n"]/S["rows"],100*S["cost"]["n"]/S["rows"],100*S["cost_by_condition"]["Poor"]["score_positive_n"]/S["condition_counter"]["Poor"],100*S["cost_by_condition"]["Poor"]["cost_carrying_n"]/S["condition_counter"]["Poor"],100*S["cost_by_condition"]["Good"]["cost_carrying_n"]/S["condition_counter"]["Good"]]
fig,ax=plt.subplots(figsize=(8,5.0)); ax.barh(cats[::-1],vals2[::-1],color=AMBER)
for i,v in enumerate(vals2[::-1]): ax.text(v+1.5,i,f"{v:.1f}%",va="center",fontsize=10)
ax.set_xlim(0,112)
ax.set_xlabel("Percent of the base printed in each row label (each bar has its own base)")
ax.set_title("The inventory's two repair fields cover different segments"); save(fig,"chart_repair_field_coverage.png")
print("charts done")
