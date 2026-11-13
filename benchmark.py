"""Benchmark: BFS vs A* (Manhattan) vs A* (Manhattan + dead-square pruning).

All algorithms run on the same fixed levels with the same node budget. Every
solution is re-checked by the independent validator (src/validator.py).

Level selection rule (fixed BEFORE running anything): every 5th level of
Microban (5, 10, ..., 150). Microban is ordered by increasing difficulty, so
this gives 30 levels spread across the whole difficulty range.

Usage:
    python benchmark.py                       # full run, writes results/benchmark.csv
    python benchmark.py --resume              # continue an interrupted run
    python benchmark.py --levels 1 2 3 --limit 20000 --timeout 5 --out results/smoke.csv
    python benchmark.py --summary-only        # re-print the summary from the CSV
"""
import argparse
import csv
import os
import statistics
import sys

from src.astar import astar_deadlock, astar_manhattan
from src.bfs import bfs
from src.parser import load_file
from src.validator import is_valid_solution

LEVEL_FILE = "levels/microban.xsb"
DEFAULT_LEVELS = list(range(5, 151, 5))
ALGOS = {"bfs": bfs, "astar": astar_manhattan, "astar_dd": astar_deadlock}
FIELDS = ["level", "algo", "solved", "reason", "nodes_expanded",
          "solution_moves", "solution_pushes", "valid", "seconds", "solution"]


def run_one(level, algo_name, limit, timeout):
    """Run one algorithm on one level and return a CSV row (dict)."""
    res = ALGOS[algo_name](level, limit, timeout)
    valid = ""
    moves = pushes = ""
    if res.solved:
        valid = is_valid_solution(level, res.solution)
        moves = len(res.solution)
        pushes = sum(1 for ch in res.solution if ch.isupper())
    return {"level": level.name, "algo": algo_name, "solved": res.solved,
            "reason": res.reason, "nodes_expanded": res.nodes_expanded,
            "solution_moves": moves, "solution_pushes": pushes,
            "valid": valid, "seconds": f"{res.seconds:.3f}",
            "solution": res.solution or ""}


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def summarize(path):
    """Build the summary text from the CSV (also written to results/summary.txt)."""
    rows = read_rows(path)
    algos = [a for a in ALGOS if any(r["algo"] == a for r in rows)]
    levels = sorted({r["level"] for r in rows}, key=lambda n: int(n.split("_")[1]))
    by = {(r["level"], r["algo"]): r for r in rows}
    out = []

    out.append(f"Levels: {len(levels)}\n")
    out.append("Levels solved within the budget:")
    for a in algos:
        ok = [r for r in rows if r["algo"] == a and r["solved"] == "True"]
        valid = sum(1 for r in ok if r["valid"] == "True")
        out.append(f"  {a:9s} {len(ok):3d}/{len(levels)} ({100 * len(ok) / len(levels):5.1f}%)"
                   f"   valid solutions: {valid}/{len(ok)}")

    if "astar" in algos and "astar_dd" in algos:
        common = [l for l in levels
                  if by[(l, "astar")]["solved"] == "True" and by[(l, "astar_dd")]["solved"] == "True"]
        out.append(f"\nA* vs A*+deadlock on the {len(common)} levels BOTH solved:")
        if common:
            na = [int(by[(l, "astar")]["nodes_expanded"]) for l in common]
            nd = [int(by[(l, "astar_dd")]["nodes_expanded"]) for l in common]
            out.append(f"  total nodes   A*: {sum(na):,}   A*+dd: {sum(nd):,}"
                       f"   reduction: {100 * (1 - sum(nd) / sum(na)):.1f}%")
            out.append(f"  median nodes  A*: {statistics.median(na):,.0f}   A*+dd: {statistics.median(nd):,.0f}")
            worse = [l for l, x, y in zip(common, na, nd) if y > x]
            out.append(f"  levels where A*+dd expanded MORE nodes: {len(worse)} {worse}")
            diff = [l for l in common if by[(l, 'astar')]["solution_moves"] != by[(l, 'astar_dd')]["solution_moves"]]
            out.append(f"  levels where solution length differs (should be 0): {len(diff)} {diff}")
        sa = sum(1 for l in levels if by[(l, "astar")]["solved"] == "True")
        sd = sum(1 for l in levels if by[(l, "astar_dd")]["solved"] == "True")
        fewer = bool(common) and sum(nd) < sum(na)
        out.append("\nHypothesis (proposal criterion: A*+dd solves more levels OR expands fewer nodes):")
        out.append(f"  more levels solved: {sd > sa} ({sd} vs {sa});  fewer nodes: {fewer}")
        out.append("  => " + ("SUPPORTED" if (sd > sa or fewer) else "NOT SUPPORTED"))

    out.append("\nUnsolved levels and why (budget = node limit, timeout = time cap):")
    for a in algos:
        bad = [(r["level"], r["reason"]) for r in rows if r["algo"] == a and r["solved"] != "True"]
        out.append(f"  {a:9s} {bad if bad else 'none'}")
    return "\n".join(out)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--file", default=LEVEL_FILE)
    p.add_argument("--levels", type=int, nargs="+", default=DEFAULT_LEVELS,
                   help="level numbers ('; N' in the .xsb); default: every 5th, 5..150")
    p.add_argument("--algos", nargs="+", choices=sorted(ALGOS), default=list(ALGOS))
    p.add_argument("--limit", type=int, default=1_000_000, help="expanded-node budget per level")
    p.add_argument("--timeout", type=float, default=300.0,
                   help="safety wall-clock cap in seconds per run (a limitation to report)")
    p.add_argument("--out", default="results/benchmark.csv")
    p.add_argument("--resume", action="store_true", help="skip (level, algo) pairs already in --out")
    p.add_argument("--summary-only", action="store_true")
    args = p.parse_args()

    if not args.summary_only:
        levels = load_file(args.file, only=args.levels)
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        done = set()
        if args.resume and os.path.exists(args.out):
            done = {(r["level"], r["algo"]) for r in read_rows(args.out)}
        new_file = not (args.resume and os.path.exists(args.out))
        with open(args.out, "a" if not new_file else "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=FIELDS)
            if new_file:
                w.writeheader()
            for lv in levels:
                for algo in args.algos:
                    if (lv.name, algo) in done:
                        continue
                    row = run_one(lv, algo, args.limit, args.timeout)
                    w.writerow(row)
                    f.flush()  # keep partial results if the run is interrupted
                    print(f"{lv.name:13s} {algo:9s} {row['reason']:9s} "
                          f"nodes={row['nodes_expanded']:>8} t={row['seconds']}s", flush=True)

    if not os.path.exists(args.out):
        sys.exit(f"{args.out} not found")
    text = summarize(args.out)
    print("\n" + text)
    with open(os.path.join(os.path.dirname(args.out) or ".", "summary.txt"), "w", encoding="utf-8") as f:
        f.write(text + "\n")


if __name__ == "__main__":
    main()