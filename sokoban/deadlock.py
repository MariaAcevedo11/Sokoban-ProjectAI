from __future__ import annotations

from collections import deque

from .model import DIRECTIONS, Level


def compute_reachable_box_squares(level: Level) -> set[tuple[int, int]]:
    reachable: set[tuple[int, int]] = set(level.goals)
    queue = deque(level.goals)

    while queue:
        box = queue.popleft()
        for dx, dy in DIRECTIONS.values():
            prev_box = (box[0] - dx, box[1] - dy)
            player_required = (prev_box[0] - dx, prev_box[1] - dy)
            if (
                prev_box in level.floors
                and player_required in level.floors
                and prev_box not in reachable
            ):
                reachable.add(prev_box)
                queue.append(prev_box)

    return reachable


def compute_dead_squares(level: Level) -> set[tuple[int, int]]:
    return set(level.floors) - compute_reachable_box_squares(level)
