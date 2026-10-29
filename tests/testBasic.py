import unittest

from src.moves import apply_moves, is_goal, successors
from src.parser import parse_collection, parse_level

SMALL = ["#####", "#@$.#", "#####"]


class TestParser(unittest.TestCase):
    def test_parse_basic(self):
        lv = parse_level(SMALL)
        self.assertEqual(lv.initial.player, (1, 1))
        self.assertEqual(lv.initial.boxes, frozenset({(1, 2)}))
        self.assertEqual(lv.goals, frozenset({(1, 3)}))

    def test_collection_with_comments(self):
        text = "; 1\n#####\n#@$.#\n#####\n\n; 2\n#####\n#@*.#\n#####\n"
        # The second level is invalid (2 goals/1 box), so it should fail clearly.
        with self.assertRaises(ValueError):
            parse_collection(text)

    def test_two_levels(self):
        text = "; 1\n#####\n#@$.#\n#####\n\n; 2\n######\n#@$ .#\n######\n"
        self.assertEqual(len(parse_collection(text)), 2)


class TestMoves(unittest.TestCase):
    def test_push_legal_and_win(self):
        lv = parse_level(SMALL)
        end = apply_moves(lv, lv.initial, "R")
        self.assertTrue(is_goal(lv, end))

    def test_push_into_wall_illegal(self):
        lv = parse_level(SMALL)
        s = apply_moves(lv, lv.initial, "R")
        with self.assertRaises(ValueError):
            apply_moves(lv, s, "R")  # box against wall

    def test_box_against_box_illegal(self):
        lv = parse_level(["######", "#@$$.#", "#  . #", "######"])
        acts = [a for a, _ in successors(lv, lv.initial)]
        self.assertNotIn("R", acts)

    def test_walk_is_lowercase(self):
        lv = parse_level(["#####", "#@ $.#", "#####"])
        self.assertEqual([a for a, _ in successors(lv, lv.initial)], ["r"])


if __name__ == "__main__":
    unittest.main()