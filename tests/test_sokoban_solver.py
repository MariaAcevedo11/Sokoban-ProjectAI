import unittest

from sokoban.deadlock import compute_dead_squares
from sokoban.model import apply_move, parse_xsb, parse_xsb_collection, validate_solution
from sokoban.solver import solve_astar, solve_bfs


SIMPLE_LEVEL = """\
#####
#@  #
# $ #
# . #
#####
"""

UNSOLVABLE_WITH_CORNER = """\
######
#@   #
# $###
#  . #
######
"""


class SokobanSolverTests(unittest.TestCase):
    def test_parse_collection(self):
        levels = parse_xsb_collection(SIMPLE_LEVEL + "\n" + SIMPLE_LEVEL)
        self.assertEqual(2, len(levels))

    def test_apply_push_rules(self):
        level = parse_xsb(
            """\
#####
#@$.#
#####
"""
        )
        state = level.initial_state
        next_state = apply_move(level, state, "R")
        self.assertIsNotNone(next_state)
        self.assertTrue(level.is_goal(next_state))

    def test_bfs_finds_valid_solution(self):
        level = parse_xsb(SIMPLE_LEVEL)
        result = solve_bfs(level)
        self.assertTrue(result.solved)
        self.assertTrue(validate_solution(level, result.moves))

    def test_astar_finds_valid_solution(self):
        level = parse_xsb(SIMPLE_LEVEL)
        result = solve_astar(level, deadlock_pruning=False)
        self.assertTrue(result.solved)
        self.assertTrue(validate_solution(level, result.moves))

    def test_dead_square_detection_marks_corner(self):
        level = parse_xsb(UNSOLVABLE_WITH_CORNER)
        dead = compute_dead_squares(level)
        self.assertIn((1, 1), dead)
        self.assertNotIn((3, 3), dead)

    def test_deadlock_aware_astar_respects_node_limit(self):
        level = parse_xsb(UNSOLVABLE_WITH_CORNER)
        result = solve_astar(level, deadlock_pruning=True, max_expanded_nodes=5)
        self.assertFalse(result.solved)
        self.assertLessEqual(result.expanded_nodes, 5)


if __name__ == "__main__":
    unittest.main()
