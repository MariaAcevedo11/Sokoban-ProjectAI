"""Independent solution checker.

Deliberately shares NO code with the solver: it does not import moves.py,
parser.py or state.py. It re-reads the raw XSB text and re-implements the
Sokoban rules from scratch, so a bug in the solver's rules cannot make a wrong
solution look valid.

Action notation (same as the solver's output):
  u d l r  -> walk one square
  U D L R  -> walk one square AND push the box that was there
A move whose letter case does not match whether a box was pushed is rejected.
"""
import re
from typing import Dict, List, Tuple

_LEVEL_LINE = re.compile(r"^[#@+$*. \-_]*#[#@+$*. \-_]*$")
_STEP = {"u": (-1, 0), "d": (1, 0), "l": (0, -1), "r": (0, 1)}


def read_xsb_levels(text: str) -> Dict[str, List[str]]:
    """Split a raw .xsb collection into {'N': rows}, keyed by the '; N' title."""
    levels: Dict[str, List[str]] = {}
    block: List[str] = []
    title = None
    count = 0

    def flush():
        nonlocal block, title, count
        if block:
            count += 1
            levels[title if title else str(count)] = block
        block, title = [], None

    for line in text.splitlines():
        if _LEVEL_LINE.match(line):
            block.append(line)
        else:
            flush()
            m = re.match(r"^;\s*(\S+)\s*$", line.strip())
            if m:
                title = m.group(1)
    flush()
    return levels


def check_solution(rows: List[str], moves: str) -> Tuple[bool, str, int]:
    """Replay `moves` on the level given as raw XSB rows.

    Returns (is_valid, message, number_of_pushes).
    """
    walls, goals, boxes = set(), set(), set()
    player = None
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == "#":
                walls.add((r, c))
            if ch in ".+*":
                goals.add((r, c))
            if ch in "$*":
                boxes.add((r, c))
            if ch in "@+":
                player = (r, c)
    if player is None:
        return False, "level has no player", 0
    height = len(rows)
    width = max(len(row) for row in rows)

    def blocked(p):  # outside the grid counts as wall
        return p in walls or not (0 <= p[0] < height and 0 <= p[1] < width)

    pushes = 0
    for i, ch in enumerate(moves):
        if ch.lower() not in _STEP:
            return False, f"move {i}: unknown action {ch!r}", pushes
        dr, dc = _STEP[ch.lower()]
        target = (player[0] + dr, player[1] + dc)
        if blocked(target):
            return False, f"move {i} ({ch}): walks into a wall", pushes
        if target in boxes:
            beyond = (target[0] + dr, target[1] + dc)
            if blocked(beyond):
                return False, f"move {i} ({ch}): pushes a box into a wall", pushes
            if beyond in boxes:
                return False, f"move {i} ({ch}): pushes a box into another box", pushes
            if not ch.isupper():
                return False, f"move {i} ({ch}): a push must be written in uppercase", pushes
            boxes.remove(target)
            boxes.add(beyond)
            pushes += 1
        elif ch.isupper():
            return False, f"move {i} ({ch}): uppercase move but no box was pushed", pushes
        player = target

    if boxes != goals:
        return False, f"finished with {len(goals - boxes)} goal(s) uncovered", pushes
    return True, "ok", pushes