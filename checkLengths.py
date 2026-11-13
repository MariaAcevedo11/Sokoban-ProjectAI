import csv
from collections import defaultdict

rows = list(csv.DictReader(open("results/benchmark.csv", encoding="utf-8")))
lengths = defaultdict(dict)
for r in rows:
    if r["solved"] == "True":
        lengths[r["level"]][r["algo"]] = int(r["solution_moves"])

bad = [(lv, d) for lv, d in lengths.items() if len(set(d.values())) > 1]
print("levels compared:", sum(1 for d in lengths.values() if len(d) > 1))
print("levels with different solution lengths:", bad if bad else "none")