"""Manhattan-distance heuristic with optimal box-to-goal assignment.

h(state) = minimum total Manhattan distance over all one-to-one assignments of
boxes to goals. It ignores walls and the player, so it is a lower bound on the
number of pushes needed, and therefore on the number of actions (each push is
one action of cost 1).

"""
from typing import Dict, FrozenSet, List

from .state import Level, Pos

INF = float("inf")


def hungarian(cost: List[List[int]]) -> int:
    """Minimum-cost assignment for a square matrix (O(n^3), pure Python).

    Classic potentials-based implementation (1-indexed internally).
    """
    n = len(cost)
    if n == 0:
        return 0
    u = [0] * (n + 1)       # row potentials
    v = [0] * (n + 1)       # column potentials
    match = [0] * (n + 1)   # match[j] = row assigned to column j
    way = [0] * (n + 1)
    for i in range(1, n + 1):
        match[0] = i
        j0 = 0
        minv = [INF] * (n + 1)
        used = [False] * (n + 1)
        while True:
            used[j0] = True
            i0 = match[j0]
            delta = INF
            j1 = 0
            for j in range(1, n + 1):
                if not used[j]:
                    cur = cost[i0 - 1][j - 1] - u[i0] - v[j]
                    if cur < minv[j]:
                        minv[j] = cur
                        way[j] = j0
                    if minv[j] < delta:
                        delta = minv[j]
                        j1 = j
            for j in range(n + 1):
                if used[j]:
                    u[match[j]] += delta
                    v[j] -= delta
                else:
                    minv[j] -= delta
            j0 = j1
            if match[j0] == 0:
                break
        while j0:
            j1 = way[j0]
            match[j0] = match[j1]
            j0 = j1
    return -v[0]


class ManhattanHeuristic:
    """Callable h(boxes) bound to one level, with a cache keyed by box set.

    The cache matters: many search states share the same boxes and differ only
    in the player position, and the assignment is the expensive part.
    """

    def __init__(self, level: Level):
        self.goals: List[Pos] = sorted(level.goals)
        self._cache: Dict[FrozenSet[Pos], int] = {}

    def __call__(self, boxes: FrozenSet[Pos]) -> int:
        h = self._cache.get(boxes)
        if h is None:
            h = hungarian([[abs(br - gr) + abs(bc - gc) for (gr, gc) in self.goals]
                           for (br, bc) in sorted(boxes)])
            self._cache[boxes] = h
        return h