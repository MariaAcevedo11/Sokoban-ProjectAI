"""Build the report tables and figures from results/benchmark.csv.

Outputs (in results/):
  fig_nodes_per_level.pdf/.png   nodes expanded per level, log scale, 3 algorithms
  fig_solved_vs_nodes.pdf/.png   levels solved as a function of nodes expanded
  table_solved.tex               levels solved + node statistics per algorithm
  table_nodes.tex / table_nodes.md   per-level nodes expanded

Requires matplotlib (see requirements.txt).
Usage: python make_report_assets.py [csv]
"""
import csv
import statistics
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

CSV_PATH = sys.argv[1] if len(sys.argv) > 1 else "results/benchmark.csv"
OUT = "results/"
BUDGET = 1_000_000
ALGOS = ["bfs", "astar", "astar_dd"]
LABEL = {"bfs": "BFS", "astar": "A* (Manhattan)", "astar_dd": "A* + deadlock"}
SHORT = {"bfs": "BFS", "astar": "A*", "astar_dd": "A*+DD"}
COLOR = {"bfs": "#999999", "astar": "#0072B2", "astar_dd": "#E69F00"}  # colour-blind safe

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))
levels = sorted({r["level"] for r in rows}, key=lambda n: int(n.split("_")[1]))
num = lambda lv: int(lv.split("_")[1])
data = {(r["level"], r["algo"]): r for r in rows}
solved = lambda lv, a: data[(lv, a)]["solved"] == "True"
nodes = lambda lv, a: int(data[(lv, a)]["nodes_expanded"])

plt.rcParams.update({"font.size": 7, "font.family": "serif", "axes.linewidth": 0.6})

# ---------------------------------------------------------------- figure 1
fig, ax = plt.subplots(figsize=(7.16, 2.7))
w = 0.27
for k, a in enumerate(ALGOS):
    for i, lv in enumerate(levels):
        x = i + (k - 1) * w
        if solved(lv, a):
            ax.bar(x, nodes(lv, a), w, color=COLOR[a], edgecolor="black", linewidth=0.3)
        else:  # budget exhausted: dashed outline reaching the budget line
            ax.bar(x, BUDGET, w, facecolor="none", edgecolor=COLOR[a],
                   linestyle="--", linewidth=0.9)
ax.set_yscale("log")
ax.set_ylim(100, 2_000_000)
ax.axhline(BUDGET, color="black", linewidth=0.5, linestyle=":")
ax.set_xticks(range(len(levels)))
ax.set_xticklabels([num(lv) for lv in levels], fontsize=5.5)
ax.set_xlabel("Microban level")
ax.set_ylabel("Nodes expanded (log)")
handles = [Patch(facecolor=COLOR[a], edgecolor="black", linewidth=0.3, label=LABEL[a]) for a in ALGOS]
handles.append(Patch(facecolor="none", edgecolor="black", linestyle="--", label="Budget (1M) exhausted"))
ax.legend(handles=handles, ncol=4, loc="upper left", frameon=False, fontsize=6.5)
ax.set_ylim(100, 6_000_000)
fig.tight_layout()
fig.savefig(OUT + "fig_nodes_per_level.pdf")
fig.savefig(OUT + "fig_nodes_per_level.png", dpi=300)
plt.close(fig)

# ---------------------------------------------------------------- figure 2
fig, ax = plt.subplots(figsize=(3.4, 2.5))
for a in ALGOS:
    xs = sorted(nodes(lv, a) for lv in levels if solved(lv, a))
    ys = list(range(1, len(xs) + 1))
    ax.step(xs + [BUDGET], ys + [len(xs)], where="post", color=COLOR[a], linewidth=1.3, label=LABEL[a])
ax.set_xscale("log")
ax.set_xlim(100, BUDGET)
ax.set_xlabel("Nodes expanded (log)")
ax.set_ylabel("Levels solved")
ax.set_ylim(0, len(levels) + 1)
ax.grid(alpha=0.3, linewidth=0.4)
ax.legend(loc="upper left", frameon=False, fontsize=6.5)
fig.tight_layout()
fig.savefig(OUT + "fig_solved_vs_nodes.pdf")
fig.savefig(OUT + "fig_solved_vs_nodes.png", dpi=300)
plt.close(fig)

# ---------------------------------------------------------------- table: solved
common = [lv for lv in levels if all(solved(lv, a) for a in ALGOS)]
lines = [r"\begin{table}[t]", r"\centering", r"\caption{Levels solved within the 1M-node budget. "
         f"Node statistics use only the {len(common)} levels solved by all three algorithms.}}",
         r"\label{tab:solved}", r"\footnotesize", r"\begin{tabular}{lrrrr}", r"\toprule",
         r"Algorithm & Solved & Valid & Median nodes & Total nodes \\", r"\midrule"]
for a in ALGOS:
    ok = [lv for lv in levels if solved(lv, a)]
    valid = sum(1 for lv in ok if data[(lv, a)]["valid"] == "True")
    med = statistics.median(nodes(lv, a) for lv in common)
    tot = sum(nodes(lv, a) for lv in common)
    lines.append(f"{LABEL[a].replace('*', '*')} & {len(ok)}/{len(levels)} ({100 * len(ok) / len(levels):.0f}\\%) "
                 f"& {valid}/{len(ok)} & {med:,.0f} & {tot:,} \\\\".replace(",", "{,}"))
lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
open(OUT + "table_solved.tex", "w", encoding="utf-8").write("\n".join(lines) + "\n")

# ---------------------------------------------------------------- table: per level
def cell(lv, a):
    return f"{nodes(lv, a):,}" if solved(lv, a) else "$>$1M"

half = (len(levels) + 1) // 2
tex = [r"\begin{table*}[t]", r"\centering",
       r"\caption{Nodes expanded per level (``$>$1M'' = budget exhausted, level not solved).}",
       r"\label{tab:nodes}", r"\footnotesize", r"\begin{tabular}{rrrr@{\hspace{2em}}rrrr}", r"\toprule",
       r"Level & BFS & A* & A*+DD & Level & BFS & A* & A*+DD \\", r"\midrule"]
for i in range(half):
    left = levels[i]
    right = levels[i + half] if i + half < len(levels) else None
    l = f"{num(left)} & " + " & ".join(cell(left, a) for a in ALGOS)
    r_ = (f"{num(right)} & " + " & ".join(cell(right, a) for a in ALGOS)) if right else " & & & "
    tex.append((l + " & " + r_ + r" \\").replace(",", "{,}"))
tex += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
open(OUT + "table_nodes.tex", "w", encoding="utf-8").write("\n".join(tex) + "\n")

md = ["| Level | BFS | A* | A*+DD |", "|---:|---:|---:|---:|"]
for lv in levels:
    md.append(f"| {num(lv)} | " + " | ".join(cell(lv, a).replace("$>$", ">") for a in ALGOS) + " |")
open(OUT + "table_nodes.md", "w", encoding="utf-8").write("\n".join(md) + "\n")

print("Wrote figures and tables to", OUT)
print(f"Levels solved by all three: {len(common)}")