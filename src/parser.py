"""Parser for the XSB format.

  #  wall          @  player             +  player on goal
  $  box           *  box on goal        .  goal
  ' ' (or '-', '_') empty floor
"""
import re
from typing import Iterable, List, Optional

from .state import Level, State

LEVEL_CHARS = set("#@+$*. -_")


def _is_level_line(line: str) -> bool:
    s = line.rstrip("\r\n")
    return bool(s.strip()) and set(s) <= LEVEL_CHARS and "#" in s


def parse_level(rows: List[str], name: str = "") -> Level:
    walls, goals, boxes = set(), set(), set()
    player = None
    width = max(len(r) for r in rows)
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            pos = (r, c)
            if ch == "#":
                walls.add(pos)
            elif ch == "@":
                player = pos
            elif ch == "+":
                player = pos
                goals.add(pos)
            elif ch == "$":
                boxes.add(pos)
            elif ch == "*":
                boxes.add(pos)
                goals.add(pos)
            elif ch == ".":
                goals.add(pos)
    if player is None:
        raise ValueError(f"Level '{name}': there's no player")
    if len(boxes) != len(goals):
        raise ValueError(f"Level '{name}': {len(boxes)} boxes but {len(goals)} goals")
    return Level(width, len(rows), frozenset(walls), frozenset(goals),
                 State(player, frozenset(boxes)), name)


def parse_collection(text: str, prefix: str = "level") -> List[Level]:
    """Read an .xsb file with one or more levels separated by blank lines or
    comments. If a '; N' comment appears before a level, it is named
    '<prefix>_N'; otherwise, levels are numbered in order of appearance."""
    levels, block = [], []
    pending_title = None

    def flush():
        nonlocal pending_title
        if block:
            num = pending_title if pending_title else str(len(levels) + 1)
            levels.append(parse_level(block[:], f"{prefix}_{num}"))
            block.clear()
            pending_title = None

    for line in text.splitlines():
        if _is_level_line(line):
            block.append(line.rstrip("\r\n"))
        else:
            flush()
            m = re.match(r"^;\s*(\S+)\s*$", line.strip())
            if m:
                pending_title = m.group(1)
    flush()
    return levels


def load_file(path: str, only: Optional[Iterable[int]] = None) -> List[Level]:
    """Load an .xsb file. With `only` (e.g. [1, 5, 12]), return only those
    levels, identified by their '; N' number in the file, in that order."""
    import os
    with open(path, encoding="utf-8") as f:
        levels = parse_collection(f.read(), os.path.splitext(os.path.basename(path))[0])
    if only is None:
        return levels
    by_num = {lv.name.rsplit("_", 1)[1]: lv for lv in levels}
    missing = [n for n in only if str(n) not in by_num]
    if missing:
        raise ValueError(f"Inexistent levels in {path}: {missing}")
    return [by_num[str(n)] for n in only]