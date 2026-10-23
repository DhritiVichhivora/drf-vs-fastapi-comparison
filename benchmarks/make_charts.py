"""
Draws the benchmark charts from benchmarks/results.json.

Usage (from the project root, virtual environment active):
    pip install matplotlib
    python benchmarks/make_charts.py
Output: docs/benchmark_charts.png
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

ROOT = Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "benchmarks" / "results.json").read_text(encoding="utf-8"))
settings, results = data["settings"], data["results"]

# Fixed colour per setup (colour follows the entity). Validated categorical slots 1-3.
COLORS = {"FastAPI (uvicorn)": "#2a78d6", "DRF (uvicorn)": "#eb6834", "DRF (waitress)": "#1baf7a"}
SURFACE, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#e4e3df"

names = list(results.keys())
panels = [
    ("rps", "Requests handled per second", "higher is better", "{:,.0f}"),
    ("median_ms", "Median response time (ms)", "lower is better", "{:,.0f} ms"),
    ("p95_ms", "Slowest 5% of requests: p95 (ms)", "lower is better", "{:,.0f} ms"),
]

fig, axes = plt.subplots(1, 3, figsize=(13, 4.6), dpi=200, facecolor=SURFACE)
y = list(range(len(names)))[::-1]  # first setup on top

for ax, (key, title, note, fmt) in zip(axes, panels):
    ax.set_facecolor(SURFACE)
    avgs = [results[n]["average"][key] for n in names]
    top = max(max(r[key] for r in results[n]["runs"]) for n in names)
    ax.set_xlim(0, top * 1.28)
    ax.barh(y, avgs, height=0.46, color=[COLORS[n] for n in names], zorder=3)
    for yi, n, avg in zip(y, names, avgs):
        runs = [r[key] for r in results[n]["runs"]]
        ax.scatter(runs, [yi] * len(runs), s=26, color=COLORS[n], edgecolor=SURFACE,
                   linewidth=1.5, zorder=4)
        ax.text(max(runs) + top * 0.025, yi, fmt.format(avg), va="center", ha="left",
                fontsize=10.5, color=INK, fontweight="bold", zorder=5)
    ax.set_yticks(y)
    ax.set_yticklabels(names if ax is axes[0] else [], fontsize=10.5, color=INK)
    ax.tick_params(axis="y", length=0)
    ax.tick_params(axis="x", colors=INK2, labelsize=9, length=0)
    ax.xaxis.grid(True, color=GRID, linewidth=0.8, zorder=0)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(GRID)
    ax.set_title(f"{title}\n", fontsize=11.5, color=INK, loc="left", fontweight="bold")
    ax.text(0, 1.03, note, transform=ax.transAxes, fontsize=9.5, color=INK2, va="bottom")

handles = [Patch(facecolor=COLORS[n], label=n) for n in names]
handles.append(Line2D([0], [0], marker="o", color="none", markerfacecolor=INK2,
                      markeredgecolor=SURFACE, markersize=6, label="each of the 3 runs"))
fig.legend(handles=handles, loc="lower center", ncol=4, frameon=False, fontsize=10,
           labelcolor=INK, bbox_to_anchor=(0.5, -0.01))
fig.suptitle("FastAPI vs DRF: same API, same load", x=0.012, ha="left", fontsize=14,
             color=INK, fontweight="bold", y=0.99)
fig.text(0.012, 0.915,
         f"{settings['users']} simulated users for {settings['duration_seconds']} s, "
         f"{settings['runs_per_setup']} runs per setup, one laptop, one server at a time. "
         "Bars show the average; dots show each run.",
         fontsize=9.5, color=INK2, ha="left")
fig.tight_layout(rect=(0, 0.06, 1, 0.9), w_pad=2.5)

out = ROOT / "docs" / "benchmark_charts.png"
out.parent.mkdir(exist_ok=True)
fig.savefig(out, facecolor=SURFACE, bbox_inches="tight")
print("Saved", out)
