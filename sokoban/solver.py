from __future__ import annotations

import heapq
from collections import deque
from dataclasses import dataclass
from functools import lru_cache

from .deadlock import compute_dead_squares
from .model import DIRECTIONS, Level, State, apply_move


@dataclass(frozen=True)
class SearchResult:
    solved: bool
    moves: str
    expanded_nodes: int


@lru_cache(maxsize=8192)
def _assignment_cost(boxes: tuple[tuple[int, int], ...], goals: tuple[tuple[int, int], ...]) -> int:
    n_boxes = len(boxes)
    n_goals = len(goals)
    if n_boxes == 0:
        return 0
    if n_boxes > n_goals:
        return 10**9

    distances = [
        [abs(bx - gx) + abs(by - gy) for (gx, gy) in goals]
        for (bx, by) in boxes
    ]

    @lru_cache(maxsize=None)
    def dp(i: int, mask: int) -> int:
        if i == n_boxes:
            return 0
        best = 10**9
        for goal_index in range(n_goals):
            if mask & (1 << goal_index):
                continue
            best = min(best, distances[i][goal_index] + dp(i + 1, mask | (1 << goal_index)))
        return best

    return dp(0, 0)


def manhattan_assignment_heuristic(level: Level, state: State) -> int:
    boxes = tuple(sorted(state.boxes))
    goals = tuple(sorted(level.goals))
    return _assignment_cost(boxes, goals)


def solve_bfs(level: Level, max_expanded_nodes: int = 1_000_000) -> SearchResult:
    start = level.initial_state
    if level.is_goal(start):
        return SearchResult(True, "", 0)

    frontier = deque([start])
    parent: dict[State, tuple[State | None, str | None]] = {start: (None, None)}
    expanded = 0

    while frontier and expanded < max_expanded_nodes:
        current = frontier.popleft()
        expanded += 1
        if level.is_goal(current):
            return SearchResult(True, _reconstruct(parent, current), expanded)

        for action in DIRECTIONS:
            nxt = apply_move(level, current, action)
            if nxt is None or nxt in parent:
                continue
            parent[nxt] = (current, action)
            frontier.append(nxt)

    return SearchResult(False, "", expanded)


def solve_astar(
    level: Level,
    *,
    max_expanded_nodes: int = 1_000_000,
    deadlock_pruning: bool = False,
) -> SearchResult:
    start = level.initial_state
    if level.is_goal(start):
        return SearchResult(True, "", 0)

    dead_squares: set[tuple[int, int]] | None = None
    if deadlock_pruning:
        dead_squares = compute_dead_squares(level)

    parent: dict[State, tuple[State | None, str | None]] = {start: (None, None)}
    best_cost: dict[State, int] = {start: 0}

    start_h = manhattan_assignment_heuristic(level, start)
    counter = 0
    heap: list[tuple[int, int, State]] = [(start_h, counter, start)]
    expanded = 0

    while heap and expanded < max_expanded_nodes:
        _, _, current = heapq.heappop(heap)
        g = best_cost.get(current)
        if g is None:
            continue

        expanded += 1
        if level.is_goal(current):
            return SearchResult(True, _reconstruct(parent, current), expanded)

        for action in DIRECTIONS:
            nxt = apply_move(level, current, action)
            if nxt is None:
                continue

            if dead_squares is not None and any(box in dead_squares for box in nxt.boxes):
                continue

            new_g = g + 1
            old_g = best_cost.get(nxt)
            if old_g is not None and new_g >= old_g:
                continue

            best_cost[nxt] = new_g
            parent[nxt] = (current, action)
            h = manhattan_assignment_heuristic(level, nxt)
            counter += 1
            heapq.heappush(heap, (new_g + h, counter, nxt))

    return SearchResult(False, "", expanded)


def _reconstruct(parent: dict[State, tuple[State | None, str | None]], goal: State) -> str:
    actions: list[str] = []
    current: State | None = goal
    while current is not None:
        prev, action = parent[current]
        if action is not None:
            actions.append(action)
        current = prev
    actions.reverse()
    return "".join(actions)
