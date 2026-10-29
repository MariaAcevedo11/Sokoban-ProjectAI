"""Breadth-first search (BFS): uninformed baseline.

Definition of "expanded node" (same for BFS and A*): a state is counted
when it is removed from the frontier, before the goal test. Therefore,
the goal node is also counted. If the counter exceeds `node_limit`,
the level is abandoned.
"""
import time
from collections import deque
from typing import Optional

from .moves import is_goal, successors
from .result import Result
from .state import Level


def _reconstruct(parents, state) -> str:
    actions = []
    while parents[state] is not None:
        state, action = parents[state]
        actions.append(action)
    return "".join(reversed(actions))


def bfs(level: Level, node_limit: int = 1_000_000,
        max_seconds: Optional[float] = None) -> Result:
    start_t = time.perf_counter()
    start = level.initial
    parents = {start: None}          # state -> (parent, action); also acts like "explored"
    frontier = deque([start])
    expanded = 0

    while frontier:
        state = frontier.popleft()
        expanded += 1
        if expanded > node_limit:
            return Result(False, None, expanded - 1, "budget", time.perf_counter() - start_t)
        if max_seconds is not None and time.perf_counter() - start_t > max_seconds:
            return Result(False, None, expanded - 1, "timeout", time.perf_counter() - start_t)
        if is_goal(level, state):
            return Result(True, _reconstruct(parents, state), expanded,
                          "solved", time.perf_counter() - start_t)
        for action, nxt in successors(level, state):
            if nxt not in parents:
                parents[nxt] = (state, action)
                frontier.append(nxt)

    return Result(False, None, expanded, "exhausted", time.perf_counter() - start_t)