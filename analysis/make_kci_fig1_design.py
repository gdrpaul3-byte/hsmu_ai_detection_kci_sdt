# -*- coding: utf-8 -*-
"""KCI human paper — Figure 1 (methods): mirroring procedure + trial flow.

Panel A shows the mirroring flowchart plus ONE example identity triplet
(real / ChatGPT-4o / Imagen 3). Identity: FFHQ 01708 (figure-cleared,
unused in the companion RSOS Fig. 1A; also used as the trial-stimulus
thumbnail in panel B, so the manuscript caption credits one identity only).
Images are copied to figures/stimuli_fig1/ (read-only source:
  ../ai_detection_hsmu/human_study/stimuli/).

Run: python analysis/make_kci_fig1_design.py
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

sys.stdout.reconfigure(encoding="utf-8")

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
FIGD = os.path.join(ROOT, "figures")
IMD = os.path.join(FIGD, "stimuli_fig1")
os.makedirs(FIGD, exist_ok=True)

plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Arial", "DejaVu Sans"],
    "font.size": 10, "axes.titlesize": 12, "axes.labelsize": 11,
    "svg.fonttype": "none", "pdf.fonttype": 42,
    "figure.dpi": 150, "savefig.dpi": 300, "savefig.bbox": "tight",
})

BLUE = "#2C6FAD"
ORANGE = "#E08214"
GREEN = "#4CAF50"
RED = "#f44336"
INK = "#222"
MUTED = "#555"
LINE = "#c8ced5"
CARD = "#f7f8fa"

BASE = "01708"  # single example identity


def save(fig, name):
    for ext in ("png", "pdf", "svg"):
        fig.savefig(os.path.join(FIGD, f"{name}.{ext}"))
    plt.close(fig)
    print("  figure:", name)


def rounded(ax, x, y, w, h, fc=CARD, ec=LINE, lw=1.0, rs=0.012):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle=f"round,pad=0.003,rounding_size={rs}",
        fc=fc, ec=ec, lw=lw, mutation_aspect=1.0,
    ))


def arrow(ax, x1, y1, x2, y2, color=BLUE):
    ax.add_patch(FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>", mutation_scale=12, lw=1.4,
        color=color, shrinkA=0, shrinkB=0,
    ))


def thumb(fig, path, x, y, w, h, ec="#777", lw=0.8):
    ax = fig.add_axes([x, y, w, h])
    ax.imshow(plt.imread(path) if isinstance(path, str) else path)
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor(ec); s.set_linewidth(lw)
    return ax


def main():
    W, H = 11.6, 7.8
    fig = plt.figure(figsize=(W, H))
    bg = fig.add_axes([0, 0, 1, 1])
    bg.set_xlim(0, 1); bg.set_ylim(0, 1); bg.axis("off")

    # ── panel labels ──────────────────────────────────────────────
    bg.text(0.018, 0.978, "A", fontsize=16, fontweight="bold", va="top")
    bg.text(0.048, 0.978, "Stimuli and mirroring", fontsize=12.5,
            fontweight="bold", va="top")
    bg.plot([0.04, 0.96], [0.515, 0.515], color="#dde1e6", lw=0.8)
    bg.text(0.018, 0.498, "B", fontsize=16, fontweight="bold", va="top")
    bg.text(0.048, 0.498, "Session flow and a single trial", fontsize=12.5,
            fontweight="bold", va="top")

    # ── A: procedure as a text flow ───────────────────────────────
    box_y, box_h, box_w = 0.858, 0.087, 0.255
    boxes = [
        (0.055, "1. Source portrait", "70 real FFHQ photographs"),
        (0.372, "2. Generator writes a description", "of that portrait, by itself"),
        (0.690, "3. Same generator recreates it", "ChatGPT-4o  and  Imagen 3"),
    ]
    for x, t1, t2 in boxes:
        rounded(bg, x, box_y, box_w, box_h, fc="#eef4fa", ec=BLUE, lw=1.1)
        bg.text(x + box_w / 2, box_y + 0.056, t1, ha="center", va="center",
                fontsize=8.3, fontweight="bold", color=BLUE)
        bg.text(x + box_w / 2, box_y + 0.024, t2, ha="center", va="center",
                fontsize=7.5, color=MUTED)
    arrow(bg, 0.055 + box_w + 0.004, box_y + box_h / 2,
          0.372 - 0.004, box_y + box_h / 2)
    arrow(bg, 0.372 + box_w + 0.004, box_y + box_h / 2,
          0.690 - 0.004, box_y + box_h / 2)
    bg.text(0.50, 0.842, "Each generator does steps 2–3 independently  ·  July 2025  ·  512×512 px",
            ha="center", va="top", fontsize=7.6, color=MUTED)

    # ── A: one example identity triplet, centered ─────────────────
    tw = 0.13
    th = tw * W / H
    gap = 0.028
    grid_w = 3 * tw + 2 * gap
    gx0 = (1 - grid_w) / 2
    col_x = [gx0, gx0 + tw + gap, gx0 + 2 * (tw + gap)]
    row_y = 0.585
    headers = ["Real (FFHQ)", "ChatGPT-4o", "Imagen 3"]
    header_cols = [BLUE, ORANGE, ORANGE]
    for cx, lab, col in zip(col_x, headers, header_cols):
        bg.text(cx + tw / 2, row_y + th + 0.008, lab, ha="center",
                va="bottom", fontsize=9.4, fontweight="bold", color=col)
    suffixes = ["", "_chatgpt", "_gemini"]
    for cx, sfx in zip(col_x, suffixes):
        thumb(fig, os.path.join(IMD, f"{BASE}{sfx}.png"), cx, row_y, tw, th)
    bg.text(0.5, 0.567, "One example identity (identity-matched triplet)",
            ha="center", va="top", fontsize=7.8, color=MUTED)

    # ── B: session stage strip ────────────────────────────────────
    stages = [
        "Device\nselection",
        "Practice  4\n(feedback)",
        "Language\nselection",
        "Main  20\n(no feedback)",
        "Five-page\nsurvey",
    ]
    n = len(stages)
    sw, sh = 0.142, 0.084
    gap = 0.028
    total = n * sw + (n - 1) * gap
    sx0 = (1 - total) / 2
    sy = 0.372
    fills = ["#eef4fa", "#e8f5e9", "#eef4fa", "#fff4e5", "#eef4fa"]
    for i, lab in enumerate(stages):
        x = sx0 + i * (sw + gap)
        rounded(bg, x, sy, sw, sh, fc=fills[i], ec=LINE, lw=1.0)
        bg.text(x + sw / 2, sy + sh / 2, lab, ha="center", va="center",
                fontsize=8.0, color=INK, linespacing=1.25)
        if i < n - 1:
            arrow(bg, x + sw + 0.004, sy + sh / 2,
                  x + sw + gap - 0.004, sy + sh / 2, color="#888")

    # ── B: one-trial schematic ────────────────────────────────────
    trial_y = 0.042
    trial_h = 0.300
    screens = [
        (0.055, "Fixation", "1,000 ms"),
        (0.297, "Stimulus", "max 450 px  ·  no zoom"),
        (0.539, "Response", "untimed"),
        (0.781, "Inter-trial", "self-paced"),
    ]
    sw2, sh2 = 0.168, trial_h
    for i, (x, title, sub) in enumerate(screens):
        rounded(bg, x, trial_y, sw2, sh2, fc="white", ec=LINE, lw=1.15)
        bg.text(x + sw2 / 2, trial_y + sh2 - 0.026, title, ha="center",
                va="center", fontsize=9, fontweight="bold", color=INK)
        bg.text(x + sw2 / 2, trial_y + 0.020, sub, ha="center", va="center",
                fontsize=7.4, color=MUTED)
        if i < 3:
            arrow(bg, x + sw2 + 0.004, trial_y + sh2 / 2,
                  screens[i + 1][0] - 0.004, trial_y + sh2 / 2)

    x = screens[0][0]
    bg.text(x + sw2 / 2, trial_y + sh2 / 2 + 0.008, "+", ha="center",
            va="center", fontsize=32, color="#333")

    x = screens[1][0]
    inner_w = 0.105
    inner_h = inner_w * W / H
    ix = x + (sw2 - inner_w) / 2
    iy = trial_y + 0.072
    thumb(fig, os.path.join(IMD, f"{BASE}.png"), ix, iy, inner_w, inner_h,
          ec="#999", lw=0.6)
    bg.text(x + sw2 / 2, iy - 0.014, "white square = artefact mask",
            ha="center", va="top", fontsize=6.6, color=MUTED)

    x = screens[2][0]
    bw, bh = sw2 * 0.38, 0.043
    bx1 = x + sw2 * 0.10
    bx2 = x + sw2 * 0.52
    by = trial_y + sh2 / 2 - 0.005
    bg.add_patch(Rectangle((bx1, by), bw, bh, fc=GREEN, ec="none"))
    bg.add_patch(Rectangle((bx2, by), bw, bh, fc=RED, ec="none"))
    bg.text(bx1 + bw / 2, by + bh / 2, "REAL", ha="center", va="center",
            fontsize=8.2, color="white", fontweight="bold")
    bg.text(bx2 + bw / 2, by + bh / 2, "AI", ha="center", va="center",
            fontsize=8.2, color="white", fontweight="bold")
    bg.text(x + sw2 / 2, by + bh + 0.030, "yes–no judgment",
            ha="center", va="center", fontsize=7.6, color=MUTED)

    x = screens[3][0]
    rounded(bg, x + 0.022, trial_y + sh2 / 2 - 0.022, sw2 - 0.044, 0.048,
            fc=BLUE, ec="none", rs=0.010)
    bg.text(x + sw2 / 2, trial_y + sh2 / 2 + 0.002, "Next trial",
            ha="center", va="center", fontsize=8.2, color="white",
            fontweight="bold")

    save(fig, "kci_fig1_design")


if __name__ == "__main__":
    main()
