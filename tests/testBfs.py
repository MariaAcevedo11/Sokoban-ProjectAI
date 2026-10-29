import unittest

from src.bfs import bfs
from src.parser import parse_level
from src.validator import is_valid_solution

TRIVIAL = ["#####", "#@$.#", "#####"]
SMALL = ["#######", "#.    #", "# $   #", "#   @ #", "#######"]
UNSOLVABLE = ["########", "#@$ # .#", "########"]


class TestBFS(unittest.TestCase):
    def test_trivial(self):
        lv = parse_level(TRIVIAL)
        r = bfs(lv)
        self.assertTrue(r.solved)
        self.assertEqual(r.solution, "R")
        self.assertTrue(is_valid_solution(lv, r.solution))

    def test_small_optimal_and_valid(self):
        lv = parse_level(SMALL)
        r = bfs(lv)
        self.assertTrue(r.solved)
        self.assertEqual(len(r.solution), 6)   # óptimo calculado a mano
        self.assertTrue(is_valid_solution(lv, r.solution))

    def test_unsolvable_exhausts(self):
        r = bfs(parse_level(UNSOLVABLE))
        self.assertFalse(r.solved)
        self.assertEqual(r.reason, "exhausted")

    def test_budget(self):
        r = bfs(parse_level(SMALL), node_limit=3)
        self.assertFalse(r.solved)
        self.assertEqual(r.reason, "budget")
        self.assertEqual(r.nodes_expanded, 3)

    def test_validator_rejects_bad_solutions(self):
        lv = parse_level(SMALL)
        self.assertFalse(is_valid_solution(lv, "uuuu"))   # no resuelve
        self.assertFalse(is_valid_solution(lv, "LLLL"))   # movimiento ilegal


if __name__ == "__main__":
    unittest.main()