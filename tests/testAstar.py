import itertools
import random
import unittest

from src.astar import astar, astar_manhattan
from src.bfs import bfs
from src.heuristic import ManhattanHeuristic, hungarian
from src.parser import load_file
from src.validator import is_valid_solution

MICROBAN = "levels/microban.xsb"


class TestHungarian(unittest.TestCase):
    def test_matches_brute_force(self):
        rng = random.Random(0)
        for n in range(1, 7):
            for _ in range(20):
                m = [[rng.randint(0, 15) for _ in range(n)] for _ in range(n)]
                best = min(sum(m[i][p[i]] for i in range(n))
                           for p in itertools.permutations(range(n)))
                self.assertEqual(hungarian(m), best)


class TestHeuristic(unittest.TestCase):
    def test_zero_at_goal_and_admissible(self):
        # h at the initial state must never exceed the optimal cost (found by BFS).
        for lv in load_file(MICROBAN, only=[1, 2, 3, 4]):
            h = ManhattanHeuristic(lv)
            r = bfs(lv, 200_000)
            self.assertTrue(r.solved)
            self.assertLessEqual(h(lv.initial.boxes), len(r.solution))
            self.assertEqual(h(lv.goals), 0)


class TestAStar(unittest.TestCase):
    def test_optimal_and_valid_vs_bfs(self):
        # Same optimal length as BFS (A* with a consistent heuristic is optimal),
        # a valid solution, and never more expansions than BFS.
        for lv in load_file(MICROBAN, only=list(range(1, 11))):
            b = bfs(lv, 300_000)
            if not b.solved:
                continue
            a = astar_manhattan(lv, 300_000)
            self.assertTrue(a.solved, lv.name)
            self.assertEqual(len(a.solution), len(b.solution), lv.name)
            self.assertTrue(is_valid_solution(lv, a.solution), lv.name)
            self.assertLessEqual(a.nodes_expanded, b.nodes_expanded, lv.name)

    def test_budget(self):
        lv = load_file(MICROBAN, only=[5])[0]
        r = astar_manhattan(lv, node_limit=10)
        self.assertFalse(r.solved)
        self.assertEqual(r.reason, "budget")
        self.assertEqual(r.nodes_expanded, 10)

    def test_deterministic(self):
        lv = load_file(MICROBAN, only=[3])[0]
        r1, r2 = astar_manhattan(lv), astar_manhattan(lv)
        self.assertEqual((r1.solution, r1.nodes_expanded), (r2.solution, r2.nodes_expanded))

    def test_dead_square_hook_prunes(self):
        # Marking every floor square dead must make pushing impossible.
        lv = load_file(MICROBAN, only=[1])[0]
        every = frozenset((r, c) for r in range(lv.height) for c in range(lv.width)
                          if lv.is_floor((r, c)))
        r = astar(lv, 100_000, dead_squares=every)
        self.assertFalse(r.solved)


if __name__ == "__main__":
    unittest.main()