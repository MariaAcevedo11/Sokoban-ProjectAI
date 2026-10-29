"""Common representations: Level (fixed part) and State (changing part)."""
from typing import FrozenSet, NamedTuple, Tuple

Pos = Tuple[int, int]  # (row, column)


class State(NamedTuple):
    """Search state: player position plus box positions.
    It is hashable, so it can be used directly in sets and dictionaries."""
    player: Pos
    boxes: FrozenSet[Pos]


class Level(NamedTuple):
    """Fixed part of the level: walls and goals do not change during the search."""
    width: int
    height: int
    walls: FrozenSet[Pos]
    goals: FrozenSet[Pos]
    initial: State
    name: str = ""

    def is_floor(self, pos: Pos) -> bool:
        r, c = pos
        return 0 <= r < self.height and 0 <= c < self.width and pos not in self.walls