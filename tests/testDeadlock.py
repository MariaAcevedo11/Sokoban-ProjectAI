import unittest

from src.astar import astar_deadlock, astar_manhattan
from src.deadlock import compute_alive_squares, compute_dead_squares
from src.moves import successors
from src.parser import load_file, parse_level
from src.validator import is_valid_solution

MICROBAN = "levels/microban.xsb"
ROOM = ["#######", "#     #", "# .   #", "#@$   #", "#######"]


class TestDeadSquares(unittest.TestCase):
    def test_corners_dead_goal_alive(self):
        lv = parse_level(ROOM)
        dead = compute_dead_squares(lv)
        self.assertIn((1, 1), dead)
        self.assertIn((1, 5), dead)
        self.assertTrue(lv.goals.isdisjoint(dead))

    def test_wall_row_without_goal_is_dead(self):
        dead = compute_dead_squares(parse_level(ROOM))
        # a box on the top row can only slide along the wall and never reach row 2
        self.assertTrue(all((1, c) in dead for c in range(1, 6)))

    def test_goals_always_alive_on_all_levels(self):
        for lv in load_file(MICROBAN):
            self.assertTrue(lv.goals <= compute_alive_squares(lv), lv.name)

    def test_no_solution_box_ever_on_dead_square(self):
        # Soundness check: replay the plain A* solution and confirm no box ever
        # stands on a dead square (otherwise pruning could lose solutions).
        for lv in load_file(MICROBAN, only=list(range(1, 16))):
            r = astar_manhattan(lv, 200_000)
            if not r.solved:
                continue
            dead = compute_dead_squares(lv)
            state = lv.initial
            for ch in r.solution:
                state = next(n for a, n in successors(lv, state) if a == ch)
                self.assertTrue(state.boxes.isdisjoint(dead), lv.name)


class TestAStarDeadlock(unittest.TestCase):
    def test_same_optimal_length_valid_and_not_worse(self):
        for lv in load_file(MICROBAN, only=list(range(1, 21))):
            a = astar_manhattan(lv, 200_000)
            d = astar_deadlock(lv, 200_000)
            if a.solved:
                self.assertTrue(d.solved, lv.name)
                self.assertEqual(len(a.solution), len(d.solution), lv.name)
                self.assertLessEqual(d.nodes_expanded, a.nodes_expanded, lv.name)
            if d.solved:
                self.assertTrue(is_valid_solution(lv, d.solution), lv.name)


if __name__ == "__main__":
    unittest.main()