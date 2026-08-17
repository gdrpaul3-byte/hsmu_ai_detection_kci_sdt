# -*- coding: utf-8 -*-
"""KCI human paper — SDT figure set (human-only; deliberately distinct from the RSOS
AI-benchmark paper's figures per the figure-boundary rules in PLAN.md).

Data: the companion public release cloned at ../ai_detection_hsmu/human_study/
Figures -> ../figures/ :
  kci_fig1_sdt_age   (a) d' by age with participant-level distribution  (b) criterion by age
  kci_fig2_dc_plane  d' x c plane, human age groups only, 95% CI crosses
  kci_fig3_generator ChatGPT-4o vs Imagen 3 detection accuracy by age (participant means, CI)
  kci_fig4_confidence self-rated detection confidence vs accuracy (level means + by-age association)
Run: python analysis/make_kci_figures.py
"""
import csv, math, os, statistics, sys
from collections import defaultdict
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm, spearmanr
z = norm.ppf
sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.normpath(os.path.join(ROOT, "..", "ai_detection_hsmu", "human_study", "data", "exp_data"))
FIGD = os.path.join(ROOT, "figures"); os.makedirs(FIGD, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 10.5, "axes.titlesize": 12, "axes.labelsize": 11,
    "xtick.labelsize": 9.5, "ytick.labelsize": 9.5, "legend.fontsize": 9.5,
    "axes.spines.top": False, "axes.spines.right": False, "legend.frameon": False,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
    "svg.fonttype": "none", "pdf.fonttype": 42,
})
ORANGE = "#E08214"; BLUE = "#2C6FAD"; GREY = "#9aa0a6"
BINS = [20, 30, 40, 50, 60]
BLAB = ["20s", "30s", "40s", "50s", "60s"]

def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(os.path.join(FIGD, f"{name}.{ext}"))
    plt.close(fig)
    print("  figure:", name)

# ---------------- load participants (same filters as the published reproduction) ----------------
CONF_ORD = {"very-not-confident": 1, "not-confident": 2, "neutral": 3, "confident": 4, "very-confident": 5}
P = []
for r in csv.DictReader(open(os.path.join(DATA, "surveys_export_deidentified.csv"), encoding="utf-8-sig")):
    try:
        age = int(float(r["age"])); ra = float(r["realAccuracy"]); aa = float(r["aiAccuracy"])
    except Exception:
        continue
    if (r.get("firstTime") or "").strip().lower() != "yes" or not (20 <= age <= 69):
        continue
    hits = round(aa / 100 * 10); fas = 10 - round(ra / 100 * 10)
    H = (hits + 0.5) / 11; F = (fas + 0.5) / 11          # log-linear (Hautus) correction
    P.append({"pid": r["participantId"], "age": age, "bin": (age // 10) * 10,
              "oa": float(r["overallAccuracy"]),
              "d": z(H) - z(F), "c": -0.5 * (z(H) + z(F)),
              "conf": CONF_ORD.get((r.get("aiConfidence") or "").strip(), None)})
print(f"participants: {len(P)}")
byb = {b: [p for p in P if p["bin"] == b] for b in BINS}

def mci(xs):
    # sample SD (n-1), matching analysis/kci_stats.py and the CIs reported in the manuscript.
    # pstdev shifted the 60s d' upper bound to 1.07 where the text reports 1.08.
    m = statistics.mean(xs); se = statistics.stdev(xs) / math.sqrt(len(xs))
    return m, 1.96 * se

# ---------------- Fig 1: d' and criterion by age ----------------
fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.2))
for ax, key, ylab, tt in [(axes[0], "d", "Sensitivity  d′", "(a)"),
                          (axes[1], "c", "Response criterion  c", "(b)")]:
    xs = np.arange(len(BINS))
    for i, b in enumerate(BINS):
        vals = [p[key] for p in byb[b]]
        jit = (np.random.RandomState(2026 + i).rand(len(vals)) - 0.5) * 0.42
        ax.scatter(xs[i] + jit, vals, s=4, color=GREY, alpha=0.25, linewidths=0, zorder=1)
    ms, es = zip(*[mci([p[key] for p in byb[b]]) for b in BINS])
    ax.errorbar(xs, ms, yerr=es, color=ORANGE, marker="D", ms=7, lw=2.2, capsize=4, zorder=3)
    for x, m in zip(xs, ms):
        # c is reported to 3 decimals in the text (means are ~0.00x); 2 decimals rendered the
        # 60s mean of -0.0030 as "-0.00", which reads as a typo in print.
        lab = f"{m:.2f}" if key == "d" else f"{m:+.3f}"
        ax.annotate(lab, (x, m), textcoords="offset points", xytext=(10, 6), fontsize=9, color=ORANGE)
    ax.set_xticks(xs); ax.set_xticklabels(BLAB); ax.set_xlabel("Age group")
    ax.set_xlim(-0.55, len(BINS) - 0.2)   # room for the 60s value label at the right edge
    ax.set_ylabel(ylab); ax.set_title(tt, loc="left")
axes[1].axhline(0, color="#555", lw=1, ls="--")
axes[1].set_ylim(-2.2, 2.2)
fig.tight_layout()
save(fig, "kci_fig1_sdt_age")

# ---------------- Fig 2: d' x c plane (human-only; no model points — RSOS boundary) ----------------
fig, ax = plt.subplots(figsize=(5.6, 4.6))
for b, lab in zip(BINS, BLAB):
    dm, de = mci([p["d"] for p in byb[b]])
    cm, ce = mci([p["c"] for p in byb[b]])
    ax.errorbar(cm, dm, xerr=ce, yerr=de, color=ORANGE, marker="D", ms=8, lw=1.6, capsize=3)
    # anchor labels at the right cap of the horizontal CI so they never cross the bar;
    # small per-label vertical offsets separate the crowded 20s/30s points
    dy = {"20s": 5, "30s": -10}.get(lab, -3)
    ax.annotate(lab, (cm + ce, dm), textcoords="offset points", xytext=(5, dy), fontsize=10,
                fontweight="bold", color="#7a4a09",
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.3))
ax.axvline(0, color="#555", lw=1, ls="--")
ax.set_xlim(-0.6, 0.6)
ax.set_xlabel("Response criterion  c   (← AI-leaning · REAL-leaning →)")
ax.set_ylabel("Sensitivity  d′")
fig.tight_layout()
save(fig, "kci_fig2_dc_plane")

# ---------------- Fig 3: generator x age (from trial-level responses) ----------------
# MAIN TRIALS ONLY — practice rows (trial='Practice_N') contaminated the v1 figure
acc = defaultdict(lambda: defaultdict(lambda: [0, 0]))   # pid -> imageType -> [correct, n]
for r in csv.DictReader(open(os.path.join(DATA, "responses_export_deidentified.csv"), encoding="utf-8-sig")):
    if (r.get("trial") or "").strip().lower().startswith("practice"):
        continue
    a = acc[r["participantId"]][r["imageType"]]
    a[1] += 1; a[0] += 1 if (r["isCorrect"] or "").strip().lower() in ("true", "1") else 0
fig, ax = plt.subplots(figsize=(6.2, 4.2))
xs = np.arange(len(BINS))
for it, lab, col, mk in [("ai_chatgpt", "ChatGPT-4o", "#7B3294", "o"),
                         ("ai_gemini", "Imagen 3", "#008837", "s")]:
    ms, es = [], []
    for b in BINS:
        vals = [100 * acc[p["pid"]][it][0] / acc[p["pid"]][it][1]
                for p in byb[b] if acc.get(p["pid"], {}).get(it, [0, 0])[1] > 0]
        m, e = mci(vals); ms.append(m); es.append(e)
    ax.errorbar(xs, ms, yerr=es, label=lab, color=col, marker=mk, ms=6, lw=2, capsize=3)
    print(f"  fig3 {lab}: " + ", ".join(f"{b}s {m:.1f}" for b, m in zip(BINS, ms)))
ax.set_xticks(xs); ax.set_xticklabels(BLAB)
ax.set_xlabel("Age group"); ax.set_ylabel("Hit rate (%)")
ax.legend(loc="lower left")
fig.tight_layout()
save(fig, "kci_fig3_generator")

# ---------------- Fig 4: self-rated confidence vs accuracy ----------------
fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.0))
lv = [1, 2, 3, 4, 5]
ms, es, ns = [], [], []
for l in lv:
    vals = [p["oa"] for p in P if p["conf"] == l]
    ns.append(len(vals))
    m, e = (mci(vals) if len(vals) > 1 else (float("nan"), 0))
    ms.append(m); es.append(e)
axes[0].errorbar(lv, ms, yerr=es, color=ORANGE, marker="D", ms=7, lw=2, capsize=4)
for x, m, n in zip(lv, ms, ns):
    # horizontal offset keeps the n-label clear of the vertical error bar
    axes[0].annotate(f"n={n}", (x, m), textcoords="offset points", xytext=(8, -14), fontsize=8,
                     ha="left", color="#666")
axes[0].set_xticks(lv)
axes[0].set_xticklabels(["very not\nconfident", "not\nconfident", "neutral", "confident", "very\nconfident"], fontsize=9)
axes[0].set_xlabel("Self-rated detection confidence")
axes[0].set_ylabel("Overall accuracy (%)")
axes[0].set_title("(a)", loc="left")
rhos, los, his = [], [], []
for b in BINS:
    pares = [(p["conf"], p["oa"]) for p in byb[b] if p["conf"] is not None]
    r, _ = spearmanr([x for x, _ in pares], [y for _, y in pares])
    n = len(pares)
    # Bonett-Wright (2000) SE for the Fisher z interval of a Spearman rho; the plain
    # Pearson SE 1/sqrt(n-3) is slightly too narrow for rank correlations.
    se = math.sqrt((1 + r * r / 2) / (n - 3))
    fz = 0.5 * math.log((1 + r) / (1 - r))
    lo, hi = (math.tanh(fz - 1.96 * se), math.tanh(fz + 1.96 * se))
    print(f"  fig4b {b}s: rho={r:.3f} 95% CI [{lo:.3f}, {hi:.3f}] (n={n})")
    rhos.append(r); los.append(r - lo); his.append(hi - r)
axes[1].errorbar(np.arange(len(BINS)), rhos, yerr=[los, his], color=ORANGE, marker="D", ms=7, lw=2, capsize=4)
axes[1].axhline(0, color="#555", lw=1, ls="--")
axes[1].set_xticks(np.arange(len(BINS))); axes[1].set_xticklabels(BLAB)
axes[1].set_xlabel("Age group"); axes[1].set_ylabel("Spearman ρ (confidence, accuracy)")
axes[1].set_title("(b)", loc="left")
fig.tight_layout()
save(fig, "kci_fig4_confidence")

# ---------------- console summary ----------------
print("\nSDT by age (participant-mean, log-linear):")
for b, lab in zip(BINS, BLAB):
    dm, de = mci([p["d"] for p in byb[b]]); cm, ce = mci([p["c"] for p in byb[b]])
    print(f"  {lab}: n={len(byb[b]):4d}  d'={dm:.2f}±{de:.2f}  c={cm:+.3f}±{ce:.3f}")
pares = [(p["conf"], p["oa"]) for p in P if p["conf"] is not None]
r, pv = spearmanr([x for x, _ in pares], [y for _, y in pares])
print(f"confidence-accuracy: rho={r:.3f} (n={len(pares)}, p={pv:.2e})")
