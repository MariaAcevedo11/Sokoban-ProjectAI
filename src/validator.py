"""Independent validator: replays the solution from the initial state and
checks that every step is legal and that the final state is a goal state.
This is the "solution validity" metric defined in the proposal.
"""
from .moves import apply_moves, is_goal
from .state import Level


def is_valid_solution(level: Level, moves: str) -> bool:
    try:
        return is_goal(level, apply_moves(level, level.initial, moves))
    except ValueError:
        return False