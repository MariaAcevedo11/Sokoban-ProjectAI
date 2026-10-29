"""A* search, with an optional dead-square pruning hook.

One implementation serves both A* variants of the proposal:
  * A* + Manhattan:         dead_squares=None
  * A* + deadlock pruning:  dead_squares=<set of squares> (see deadlock.py)
Sharing the code guarantees that the only difference between the two is the
pruning, which is what the experiment is meant to isolate.

"Expanded node" has the same meaning as in bfs.py: a state is counted when it
is popped from the frontier (stale heap entries are skipped and not counted),
before the goal test, so the goal node itself counts.
"""
import heapq
import time
from typing import FrozenSet, Optional

from .heuristic import ManhattanHeuristic
from .moves import DIRS, is_goal, successors
from .result import Result
from .state import Level, Pos


def _reconstruct(parents, state) -> str:
    actions = []
    while parents[state] is not None:
        state, action = parents[state]
        actions.append(action)
    return "".join(reversed(actions))


def astar(level: Level, node_limit: int = 1_000_000,
          max_seconds: Optional[float] = None,
          dead_squares: Optional[FrozenSet[Pos]] = None) -> Result:
    start_t = time.perf_counter()
    h = ManhattanHeuristic(level)
    start = level.initial

    # A start state with a box on a dead square can never be solved.
    if dead_squares and any(b in dead_squares for b in start.boxes):
        return Result(False, None, 0, "exhausted", time.perf_counter() - start_t)

    g_cost = {start: 0}
    parents = {start: None}          # state -> (parent, action)
    counter = 0                      # deterministic tie-break (FIFO among equals)
    # Heap entries: (f, h, counter, g, state). Lower h first on equal f means the
    # search prefers states that look closer to the goal.
    h0 = h(start.boxes)
    heap = [(h0, h0, counter, 0, start)]
    expanded = 0

    while heap:
        f, hv, _, g, state = heapq.heappop(heap)
        if g > g_cost[state]:
            continue                 # stale entry: a cheaper path was found later
        expanded += 1
        if expanded > node_limit:
            return Result(False, None, expanded - 1, "budget", time.perf_counter() - start_t)
        if max_seconds is not None and time.perf_counter() - start_t > max_seconds:
            return Result(False, None, expanded - 1, "timeout", time.perf_counter() - start_t)
        if is_goal(level, state):
            return Result(True, _reconstruct(parents, state), expanded,
                          "solved", time.perf_counter() - start_t)

        for action, nxt in successors(level, state):
            if dead_squares is not None and action.isupper():
                # An uppercase action is a push: the box landed one square
                # beyond the player's new position, in the push direction.
                dr, dc = DIRS[action]
                if (nxt.player[0] + dr, nxt.player[1] + dc) in dead_squares:
                    continue         # prune: box can never reach a goal from here
            ng = g + 1
            if ng < g_cost.get(nxt, float("inf")):
                g_cost[nxt] = ng
                parents[nxt] = (state, action)
                counter += 1
                nh = h(nxt.boxes)
                heapq.heappush(heap, (ng + nh, nh, counter, ng, nxt))

    return Result(False, None, expanded, "exhausted", time.perf_counter() - start_t)


def astar_manhattan(level: Level, node_limit: int = 1_000_000,
                    max_seconds: Optional[float] = None) -> Result:
    """A* with the Manhattan assignment heuristic and no pruning."""
    return astar(level, node_limit, max_seconds, dead_squares=None)