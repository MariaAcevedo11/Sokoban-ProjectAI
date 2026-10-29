"""Solve a level from the command line.

Example:
    python -m src.solve levels/microban.xsb --index 1 --algo bfs
    python -m src.solve levels/microban.xsb --index 1 --algo astar
"""
import argparse
import sys

from .astar import astar_manhattan
from .bfs import bfs
from .parser import load_file
from .validator import is_valid_solution

ALGOS = {"bfs": bfs, "astar": astar_manhattan}  # astar_dd (deadlock pruning) coming next


def main(argv=None):
    p = argparse.ArgumentParser(description="Sokoban solver")
    p.add_argument("file", help="Path to the .xsb file")
    p.add_argument("--index", type=int, default=1, help="Level number in the file (the '; N' in the .xsb)")
    p.add_argument("--algo", choices=sorted(ALGOS), default="bfs")
    p.add_argument("--limit", type=int, default=1_000_000, help="Maximum number of expanded nodes")
    p.add_argument("--timeout", type=float, default=None, help="Maximum time in seconds (optional)")
    args = p.parse_args(argv)

    try:
        level = load_file(args.file, only=[args.index])[0]
    except ValueError as e:
        sys.exit(str(e))

    res = ALGOS[args.algo](level, args.limit, args.timeout)
    print(f"Level: {level.name}  Algorithm: {args.algo}")
    print(f"Result: {res.reason}  Nodes expanded: {res.nodes_expanded}  Time: {res.seconds:.2f}s")
    if res.solved:
        pushes = sum(ch.isupper() for ch in res.solution)
        print(f"Solution ({len(res.solution)} moves, {pushes} pushes): {res.solution}")
        print(f"Valid: {is_valid_solution(level, res.solution)}")


if __name__ == "__main__":
    main()