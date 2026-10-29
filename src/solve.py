"""Solve a level from command the line.

Ex:  python -m src.solve levels/microban.xsb --index 1 --something bfs|astar
"""
import argparse
import sys

from .astar import astar_manhattan
from .bfs import bfs
from .parser import load_file
from .validator import is_valid_solution

ALGOS = {"bfs": bfs, "astar": astar_manhattan}   # astar_dd (deadlock pruning) comes next


def main(argv=None):
    p = argparse.ArgumentParser(description="Sokoban solver")
    p.add_argument("file", help="archivo .xsb")
    p.add_argument("--index", type=int, default=1, help="número del nivel en el archivo (el '; N' del .xsb)")
    p.add_argument("--algo", choices=sorted(ALGOS), default="bfs")
    p.add_argument("--limit", type=int, default=1_000_000, help="máximo de nodos expandidos")
    p.add_argument("--timeout", type=float, default=None, help="segundos máximos (opcional)")
    args = p.parse_args(argv)

    try:
        level = load_file(args.file, only=[args.index])[0]
    except ValueError as e:
        sys.exit(str(e))

    res = ALGOS[args.algo](level, args.limit, args.timeout)
    print(f"Nivel: {level.name}  Algoritmo: {args.algo}")
    print(f"Resultado: {res.reason}  Nodos expandidos: {res.nodes_expanded}  Tiempo: {res.seconds:.2f}s")
    if res.solved:
        pushes = sum(ch.isupper() for ch in res.solution)
        print(f"Solución ({len(res.solution)} movimientos, {pushes} empujes): {res.solution}")
        print(f"Válida: {is_valid_solution(level, res.solution)}")


if __name__ == "__main__":
    main()