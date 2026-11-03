from __future__ import annotations

import argparse
from pathlib import Path

from .benchmark import run_algorithm
from .model import parse_xsb, parse_xsb_collection, validate_solution


def main() -> int:
    parser = argparse.ArgumentParser(description="Sokoban solver")
    parser.add_argument("algorithm", choices=["bfs", "astar", "astar-deadlock", "benchmark"])
    parser.add_argument("level_file", help="Path to XSB level file")
    parser.add_argument("--max-expanded", type=int, default=1_000_000)
    args = parser.parse_args()

    text = Path(args.level_file).read_text(encoding="utf-8")

    if args.algorithm == "benchmark":
        levels = parse_xsb_collection(text)
        for algo in ("bfs", "astar", "astar-deadlock"):
            summary = run_algorithm(levels, algo, max_expanded_nodes=args.max_expanded)
            print(f"{algo}: solved {summary.solved_levels}/{summary.total_levels} ({summary.solved_percent:.1f}%)")
            for index, result in enumerate(summary.results, start=1):
                print(
                    f"  level {index}: solved={result.solved} expanded={result.expanded_nodes} moves={len(result.moves)}"
                )
        return 0

    level = parse_xsb(text)
    summary = run_algorithm([level], args.algorithm, max_expanded_nodes=args.max_expanded)
    result = summary.results[0]
    print(f"solved={result.solved}")
    print(f"expanded_nodes={result.expanded_nodes}")
    print(f"moves={result.moves}")
    print(f"valid_solution={validate_solution(level, result.moves) if result.solved else False}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
