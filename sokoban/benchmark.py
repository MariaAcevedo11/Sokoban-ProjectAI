from __future__ import annotations

from dataclasses import dataclass

from .model import Level
from .solver import SearchResult, solve_astar, solve_bfs


@dataclass(frozen=True)
class BenchmarkSummary:
    solved_levels: int
    total_levels: int
    solved_percent: float
    results: list[SearchResult]


def run_algorithm(levels: list[Level], algorithm: str, max_expanded_nodes: int = 1_000_000) -> BenchmarkSummary:
    results: list[SearchResult] = []
    for level in levels:
        if algorithm == "bfs":
            result = solve_bfs(level, max_expanded_nodes=max_expanded_nodes)
        elif algorithm == "astar":
            result = solve_astar(level, max_expanded_nodes=max_expanded_nodes, deadlock_pruning=False)
        elif algorithm == "astar-deadlock":
            result = solve_astar(level, max_expanded_nodes=max_expanded_nodes, deadlock_pruning=True)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        results.append(result)

    solved_levels = sum(1 for r in results if r.solved)
    total = len(levels)
    solved_percent = 100.0 * solved_levels / total if total else 0.0
    return BenchmarkSummary(solved_levels, total, solved_percent, results)
