"""Re-check every solution stored in results/benchmark.csv with the independent
validator (src/xsb_validator.py), straight from the raw .xsb file.

Usage:  python revalidate.py [csv] [xsb]
Also cross-checks the push and move counts stored in the CSV.
"""
import csv
import sys

from src.xsbValidator import check_solution, read_xsb_levels

csv_path = sys.argv[1] if len(sys.argv) > 1 else "results/benchmark.csv"
xsb_path = sys.argv[2] if len(sys.argv) > 2 else "levels/microban.xsb"

with open(xsb_path, encoding="utf-8") as f:
    levels = read_xsb_levels(f.read())
with open(csv_path, newline="", encoding="utf-8") as f:
    rows = list(csv.DictReader(f))

if rows and "solution" not in rows[0]:
    sys.exit("The CSV has no 'solution' column: re-run benchmark.py with the updated version.")

checked, failures = 0, []
for r in rows:
    if r["solved"] != "True":
        continue
    number = r["level"].rsplit("_", 1)[1]
    ok, msg, pushes = check_solution(levels[number], r["solution"])
    checked += 1
    if ok and (pushes != int(r["solution_pushes"]) or len(r["solution"]) != int(r["solution_moves"])):
        ok, msg = False, "push/move counts differ from the CSV"
    if not ok:
        failures.append((r["level"], r["algo"], msg))

lines = [f"Independent validation: {checked - len(failures)}/{checked} solutions valid"]
lines += [f"  FAIL {lv} {algo}: {msg}" for lv, algo, msg in failures]
text = "\n".join(lines)
print(text)
with open("results/revalidation.txt", "w", encoding="utf-8") as f:
    f.write(text + "\n")
sys.exit(1 if failures else 0)