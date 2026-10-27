from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet

DIRECTIONS = {
    "U": (0, -1),
    "D": (0, 1),
    "L": (-1, 0),
    "R": (1, 0),
}


@dataclass(frozen=True)
class State:
    player: tuple[int, int]
    boxes: FrozenSet[tuple[int, int]]


@dataclass(frozen=True)
class Level:
    walls: FrozenSet[tuple[int, int]]
    floors: FrozenSet[tuple[int, int]]
    goals: FrozenSet[tuple[int, int]]
    initial_state: State

    def is_goal(self, state: State) -> bool:
        return all(box in self.goals for box in state.boxes)


def _add(a: tuple[int, int], b: tuple[int, int]) -> tuple[int, int]:
    return a[0] + b[0], a[1] + b[1]


def parse_xsb(level_text: str) -> Level:
    lines = [line.rstrip("\n") for line in level_text.splitlines() if line.strip() != ""]
    if not lines:
        raise ValueError("Empty level")

    walls: set[tuple[int, int]] = set()
    floors: set[tuple[int, int]] = set()
    goals: set[tuple[int, int]] = set()
    boxes: set[tuple[int, int]] = set()
    player: tuple[int, int] | None = None

    for y, line in enumerate(lines):
        for x, cell in enumerate(line):
            pos = (x, y)
            if cell == "#":
                walls.add(pos)
                continue

            if cell in {" ", "-", ".", "@", "+", "$", "*"}:
                floors.add(pos)

            if cell in {".", "+", "*"}:
                goals.add(pos)
            if cell in {"$", "*"}:
                boxes.add(pos)
            if cell in {"@", "+"}:
                if player is not None:
                    raise ValueError("Multiple players in level")
                player = pos

    if player is None:
        raise ValueError("Missing player in level")
    if not boxes:
        raise ValueError("Level must contain at least one box")
    if not goals:
        raise ValueError("Level must contain at least one goal")

    return Level(
        walls=frozenset(walls),
        floors=frozenset(floors),
        goals=frozenset(goals),
        initial_state=State(player=player, boxes=frozenset(boxes)),
    )


def parse_xsb_collection(text: str) -> list[Level]:
    blocks: list[str] = []
    current: list[str] = []

    for raw_line in text.splitlines():
        line = raw_line.rstrip("\n")
        if line.startswith(";"):
            continue
        if line.strip() == "":
            if current:
                blocks.append("\n".join(current))
                current = []
            continue
        current.append(line)

    if current:
        blocks.append("\n".join(current))

    return [parse_xsb(block) for block in blocks]


def apply_move(level: Level, state: State, action: str) -> State | None:
    if action not in DIRECTIONS:
        raise ValueError(f"Unknown action {action}")

    delta = DIRECTIONS[action]
    next_player = _add(state.player, delta)
    if next_player not in level.floors or next_player in level.walls:
        return None

    boxes = set(state.boxes)
    if next_player in boxes:
        next_box = _add(next_player, delta)
        if (
            next_box not in level.floors
            or next_box in level.walls
            or next_box in boxes
        ):
            return None
        boxes.remove(next_player)
        boxes.add(next_box)

    return State(player=next_player, boxes=frozenset(boxes))


def legal_actions(level: Level, state: State) -> list[str]:
    actions: list[str] = []
    for action in DIRECTIONS:
        if apply_move(level, state, action) is not None:
            actions.append(action)
    return actions


def validate_solution(level: Level, moves: str) -> bool:
    state = level.initial_state
    for action in moves:
        state = apply_move(level, state, action)
        if state is None:
            return False
    return level.is_goal(state)
