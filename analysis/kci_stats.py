# -*- coding: utf-8 -*-
"""Exact statistics for the KCI manuscript draft (single source: public surveys/responses)."""
import csv, math, os, statistics, sys
from collections import defaultdict
from scipy import stats as st
from scipy.stats import norm
z = norm.ppf
sys.stdout.reconfigure(encoding="utf-8")

def rci(r, n, kind="pearson"):
    """95% CI for a correlation via the Fisher z transform.
    Pearson: SE = 1/sqrt(n-3).  Spearman: Bonett-Wright SE = sqrt((1+r^2/2)/(n-3))."""
    se = math.sqrt((1 + r * r / 2) / (n - 3)) if kind == "spearman" else 1 / math.sqrt(n - 3)
    fz = 0.5 * math.log((1 + r) / (1 - r))
    return math.tanh(fz - 1.96 * se), math.tanh(fz + 1.96 * se)

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(HERE, "..", "..", "ai_detection_hsmu", "human_study", "data", "exp_data"))
CONF = {"very-not-confident": 1, "not-confident": 2, "neutral": 3, "confident": 4, "very-confident": 5}

P = []
n_total = n_first = 0
for r in csv.DictReader(open(os.path.join(DATA, "surveys_export_deidentified.csv"), encoding="utf-8-sig")):
    n_total += 1
    if (r.get("firstTime") or "").strip().lower() != "yes":
        continue
    n_first += 1
    try:
        age = int(float(r["age"])); ra = float(r["realAccuracy"]); aa = float(r["aiAccuracy"])
    except Exception:
        continue
    if not (20 <= age <= 69):
        continue
    hits = round(aa / 100 * 10); fas = 10 - round(ra / 100 * 10)
    H = (hits + 0.5) / 11; F = (fas + 0.5) / 11
    P.append({"pid": r["participantId"], "age": age, "bin": (age // 10) * 10, "oa": float(r["overallAccuracy"]),
              "ra": ra, "aa": aa, "d": z(H) - z(F), "c": -0.5 * (z(H) + z(F)),
              "sex": (r.get("gender") or "").strip().lower(),
              "date": (r.get("timestamp") or "")[:10],
              "conf": CONF.get((r.get("aiConfidence") or "").strip())})
ages = [p["age"] for p in P]; ds = [p["d"] for p in P]; cs = [p["c"] for p in P]
print(f"funnel: total records {n_total} -> firstTime=yes {n_first} (excl. {n_total-n_first}) "
      f"-> age 20-69 {len(P)} (excl. {n_first-len(P)})")
dts = sorted(p["date"] for p in P if p["date"])
print(f"sample date range: {dts[0]} .. {dts[-1]} (2026-02: {sum(1 for d in dts if d.startswith('2026-02'))})")
print(f"N={len(P)}, age {min(ages)}-{max(ages)}, mean {statistics.mean(ages):.1f}")
print(f"overall acc mean={statistics.mean(p['oa'] for p in P):.2f}")

N = len(P)
r, p_ = st.pearsonr(ages, ds); rs, ps = st.spearmanr(ages, ds)
print(f"age~d': pearson r={r:.3f} {rci(r, N)} p={p_:.2e} | "
      f"spearman rho={rs:.3f} {rci(rs, N, 'spearman')} p={ps:.2e}")
r2, p2 = st.pearsonr(ages, cs); rs2, ps2 = st.spearmanr(ages, cs)
print(f"age~c : pearson r={r2:.3f} {rci(r2, N)} p={p2:.3f} | "
      f"spearman rho={rs2:.3f} {rci(rs2, N, 'spearman')} p={ps2:.3f}")

BINS = [20, 30, 40, 50, 60]
groups_d = [[p["d"] for p in P if p["bin"] == b] for b in BINS]
groups_c = [[p["c"] for p in P if p["bin"] == b] for b in BINS]
F, pf = st.f_oneway(*groups_d)
print(f"d' one-way ANOVA over bins: F(4,{len(P)-5})={F:.1f} p={pf:.2e}")
Fc, pfc = st.f_oneway(*groups_c)
print(f"c  one-way ANOVA over bins: F(4,{len(P)-5})={Fc:.2f} p={pfc:.3f}")
print("one-sample t (c vs 0) per bin:")
for b, g in zip(BINS, groups_c):
    t, pv = st.ttest_1samp(g, 0)
    m = statistics.mean(g); se = statistics.stdev(g) / math.sqrt(len(g))
    print(f"  {b}s: mean c={m:+.3f} [ {m-1.96*se:+.3f}, {m+1.96*se:+.3f} ]  t({len(g)-1})={t:+.2f} p={pv:.3f}")

# hit / false-alarm rates by age bin — UNCORRECTED participant-mean percentages
# (reviewer #5 asked for hit rate, FA rate and class-wise accuracy explicitly).
# Note these are raw rates, not the log-linear-corrected proportions behind d' and c,
# so a d' computed from these bin means will not equal the participant-mean d' above.
print("\nhit / false-alarm rate by bin (participant mean, uncorrected %):")
for b in BINS:
    sub = [p for p in P if p["bin"] == b]
    h = statistics.mean(p["aa"] for p in sub); f = 100 - statistics.mean(p["ra"] for p in sub)
    print(f"  {b}s: hit={h:.1f}%  FA={f:.1f}%  (real-photo accuracy={100-f:.1f}%, n={len(sub)})")
h_all = statistics.mean(p["aa"] for p in P); f_all = 100 - statistics.mean(p["ra"] for p in P)
print(f"  all: hit={h_all:.1f}%  FA={f_all:.1f}%  (real-photo accuracy={100-f_all:.1f}%)")

# generator per participant — MAIN TRIALS ONLY (practice rows carry trial='Practice_N';
# including them contaminated v1's generator block: 81.1/89.0 -> corrected 80.4/88.9)
acc = defaultdict(lambda: defaultdict(lambda: [0, 0]))
for r_ in csv.DictReader(open(os.path.join(DATA, "responses_export_deidentified.csv"), encoding="utf-8-sig")):
    if (r_.get("trial") or "").strip().lower().startswith("practice"):
        continue
    a = acc[r_["participantId"]][r_["imageType"]]
    a[1] += 1; a[0] += 1 if (r_["isCorrect"] or "").strip().lower() in ("true", "1") else 0
pairs = []
for p_r in P:
    g = acc.get(p_r["pid"], {})
    if g.get("ai_chatgpt", [0, 0])[1] > 0 and g.get("ai_gemini", [0, 0])[1] > 0:
        cg = 100 * g["ai_chatgpt"][0] / g["ai_chatgpt"][1]
        gm = 100 * g["ai_gemini"][0] / g["ai_gemini"][1]
        pairs.append((p_r["age"], p_r["bin"], cg, gm))
cgs = [x[2] for x in pairs]; gms = [x[3] for x in pairs]
t, pv = st.ttest_rel(cgs, gms)
dif = [a - b_ for a, b_ in zip(cgs, gms)]
md = statistics.mean(dif); sed = statistics.stdev(dif) / math.sqrt(len(dif))
tcrit = st.t.ppf(0.975, len(dif) - 1)
print(f"\ngenerator (n={len(pairs)}): ChatGPT {statistics.mean(cgs):.1f}% vs Imagen {statistics.mean(gms):.1f}%  paired t={t:.1f} p={pv:.2e}")
print(f"  mean difference (ChatGPT - Imagen) = {md:.1f}%p, 95% CI [{md-tcrit*sed:.1f}, {md+tcrit*sed:.1f}]")
diffs = [g - c for _, _, c, g in pairs]
rint, pint = st.pearsonr([x[0] for x in pairs], diffs)
print(f"generator gap ~ age: r={rint:.3f} {rci(rint, len(pairs))} p={pint:.3e}")
for b in BINS:
    sub = [(c, g) for _, bb, c, g in pairs if bb == b]
    print(f"  {b}s: ChatGPT {statistics.mean(x[0] for x in sub):.1f} vs Imagen {statistics.mean(x[1] for x in sub):.1f} (n={len(sub)})")

conf_pairs = [(p_r["conf"], p_r["oa"]) for p_r in P if p_r["conf"]]
rho, pv = st.spearmanr([x for x, _ in conf_pairs], [y for _, y in conf_pairs])
print(f"\nconfidence~accuracy: rho={rho:.3f} {rci(rho, len(conf_pairs), 'spearman')} p={pv:.2e} (n={len(conf_pairs)})")
for b in BINS:
    sub = [(p_r["conf"], p_r["oa"]) for p_r in P if p_r["conf"] and p_r["bin"] == b]
    rb, pb = st.spearmanr([x for x, _ in sub], [y for _, y in sub])
    lo, hi = rci(rb, len(sub), "spearman"); plo, phi = rci(rb, len(sub))
    print(f"  {b}s: rho={rb:.3f} BW[{lo:.3f}, {hi:.3f}] plainFisher[{plo:.3f}, {phi:.3f}] p={pb:.3g} (n={len(sub)})")
rda, pda = st.spearmanr([p_r["age"] for p_r in P if p_r["conf"]], [p_r["conf"] for p_r in P if p_r["conf"]])
print(f"age~confidence: rho={rda:.3f} {rci(rda, len(conf_pairs), 'spearman')} p={pda:.2e}")

# Table 1 (sample characteristics): sex from surveys, device from per-trial deviceType
dev_of = {}
for r_ in csv.DictReader(open(os.path.join(DATA, "responses_export_deidentified.csv"), encoding="utf-8-sig")):
    pid = r_["participantId"]
    if pid not in dev_of and (r_.get("deviceType") or "").strip():
        dev_of[pid] = (r_.get("deviceType") or "").strip().lower()
print("\nTable 1 (n / female / male / prefer-not-to-say / mobile / web):")
for b in BINS:
    sub = [p_r for p_r in P if p_r["bin"] == b]
    sx = lambda k: sum(1 for p_r in sub if p_r["sex"] == k)
    dv = lambda k: sum(1 for p_r in sub if dev_of.get(p_r["pid"]) == k)
    print(f"  {b}s: {len(sub)} / {sx('female')} / {sx('male')} / {sx('prefer-not-to-say')} / {dv('mobile')} / {dv('web')}")
