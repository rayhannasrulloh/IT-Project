"""Render the NL->SQL evaluation metrics as a matplotlib figure.

Reads metrics.json produced by `run_eval.py --dump metrics.json` and writes a
PNG with (1) the headline scores and (2) per-category execution accuracy.
"""
import json
import sys
import matplotlib.pyplot as plt

SRC = sys.argv[1] if len(sys.argv) > 1 else "metrics.json"
OUT = sys.argv[2] if len(sys.argv) > 2 else "eval_metrics.png"

with open(SRC) as f:
    m = json.load(f)

cats = m["categories"]
names = list(cats.keys())
accs = [cats[c]["acc"] * 100 for c in names]
# sort high -> low
order = sorted(range(len(names)), key=lambda i: accs[i], reverse=True)
names = [names[i].capitalize() for i in order]
accs = [accs[i] for i in order]

fig, (ax1, ax2) = plt.subplots(
    1, 2, figsize=(12, 5), gridspec_kw={"width_ratios": [1, 1.35]}
)
fig.suptitle("NL→SQL Agent — Execution-Accuracy Evaluation",
             fontsize=15, fontweight="bold", y=0.98)

# ---- Panel 1: headline metrics ----
labels = ["Accuracy", "Precision", "Recall", "F1-score"]
vals = [m["accuracy"], m["precision"], m["recall"], m["f1"]]
colors = ["#2a9d8f", "#457b9d", "#457b9d", "#457b9d"]
bars = ax1.barh(labels[::-1], [v * 100 for v in vals][::-1],
                color=colors[::-1], height=0.6)
ax1.set_xlim(0, 100)
ax1.set_xlabel("Score (%)")
ax1.set_title("Overall metrics", fontsize=11, pad=8)
for b, v in zip(bars, vals[::-1]):
    ax1.text(b.get_width() + 2, b.get_y() + b.get_height() / 2,
             f"{v:.2f}" if v <= 1 else f"{v:.0f}",
             va="center", fontsize=10, fontweight="bold")
ax1.grid(axis="x", alpha=0.3)
ax1.set_axisbelow(True)

# ---- Panel 2: per-category accuracy ----
bars2 = ax2.bar(names, accs, color="#2a9d8f", width=0.62)
ax2.set_ylim(0, 108)
ax2.set_ylabel("Execution accuracy (%)")
ax2.set_title("Accuracy by question category", fontsize=11, pad=8)
ax2.tick_params(axis="x", rotation=25)
for b, a, c in zip(bars2, accs, [cats[k] for k in
                                 sorted(cats, key=lambda k: cats[k]["acc"], reverse=True)]):
    ax2.text(b.get_x() + b.get_width() / 2, a + 2,
             f"{a:.0f}%\n{c['correct']}/{c['total']}",
             ha="center", va="bottom", fontsize=8.5)
ax2.grid(axis="y", alpha=0.3)
ax2.set_axisbelow(True)

foot = (f"Model: {m['model']}   |   Test set: {m['n']} gold questions   |   "
        f"Mean latency: {m['mean_latency_ms']/1000:.2f} s/query   |   "
        f"Metric: execution accuracy (generated vs gold result set, live PostgreSQL)")
fig.text(0.5, 0.005, foot, ha="center", fontsize=8.5, color="#555")

fig.tight_layout(rect=[0, 0.03, 1, 0.95])
fig.savefig(OUT, dpi=150, bbox_inches="tight")
print(f"Saved {OUT}")
