"""Dead-square detection by reverse search from the goals.

A square is ALIVE if a box standing on it could reach some goal through a
sequence of legal pushes (ignoring other boxes and the player's reachability).
Every other floor square is DEAD: a box placed there can never be solved.

Reverse transition: if a box is at p after a push in direction d, then before
the push the box was at q = p - d and the player stood at s = p - 2d. Both q
and s must be floor squares. Starting from all goals and repeating this "pull"
step gives the set of alive squares.

The method is conservative: it ignores other boxes and whether the player can
actually walk to s, so it may mark a square alive when it is not really
solvable. It never marks an alive square as dead, so pruning keeps every
valid solution (it only misses some deadlocks, e.g. freeze/corral deadlocks).
"""
from collections import deque
from typing import FrozenSet

from .moves import DIRS
from .state import Level, Pos


def compute_alive_squares(level: Level) -> FrozenSet[Pos]:
    alive = set(level.goals)
    queue = deque(level.goals)
    while queue:
        pr, pc = queue.popleft()
        for dr, dc in DIRS.values():
            box_before = (pr - dr, pc - dc)             # q = p - d
            player_before = (pr - 2 * dr, pc - 2 * dc)  # s = p - 2d
            if (box_before not in alive
                    and level.is_floor(box_before)
                    and level.is_floor(player_before)):
                alive.add(box_before)
                queue.append(box_before)
    return frozenset(alive)


def compute_dead_squares(level: Level) -> FrozenSet[Pos]:
    """Floor squares from which a box can never reach any goal."""
    alive = compute_alive_squares(level)
    return frozenset((r, c) for r in range(level.height) for c in range(level.width)
                     if level.is_floor((r, c)) and (r, c) not in alive)