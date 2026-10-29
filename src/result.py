"""Common result type for all algorithms, allowing the benchmark to treat them uniformly."""
from typing import NamedTuple, Optional


class Result(NamedTuple):
    solved: bool
    solution: Optional[str]   # Action string (u/d/l/r and U/D/L/R); None if unsolved
    nodes_expanded: int
    reason: str               # "solved" | "budget" | "timeout" | "exhausted"
    seconds: float