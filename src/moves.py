"""Game rules. ALL algorithms use these functions."""
from typing import List, Tuple

from .state import Level, State

# Action -> (dr, dc). Lowercase = walk only, UPPERCASE = move while pushing a box
# (standard Sokoban solution notation).
DIRS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


def successors(level: Level, state: State) -> List[Tuple[str, State]]:
    """Return [(action, new_state)] for each legal move. Cost = 1."""
    result = []
    pr, pc = state.player
    for name, (dr, dc) in DIRS.items():
        np_ = (pr + dr, pc + dc)
        if np_ in level.walls:
            continue
        if np_ in state.boxes:
            nb = (np_[0] + dr, np_[1] + dc)
            if nb in level.walls or nb in state.boxes:
                continue  # illegal push
            boxes = (state.boxes - {np_}) | {nb}
            result.append((name, State(np_, boxes)))
        else:
            result.append((name.lower(), State(np_, state.boxes)))
    return result


def is_goal(level: Level, state: State) -> bool:
    return state.boxes == level.goals


def apply_moves(level: Level, state: State, moves: str) -> State:
    """Replay an action string while validating each step (raise ValueError
    if any step is illegal). Base for the independent validator."""
    for ch in moves:
        d = DIRS.get(ch.upper())
        if d is None:
            raise ValueError(f"Uknown action: {ch!r}")
        for action, nxt in successors(level, state):
            if action.upper() == ch.upper():
                state = nxt
                break
        else:
            raise ValueError(f"Illegal move {ch!r} from {state.player}")
    return state