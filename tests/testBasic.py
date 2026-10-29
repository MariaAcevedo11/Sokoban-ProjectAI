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
        # Level 2 is invalid (2 goals / 1 box) -> should fail with a clear error message.
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
            apply_moves(lv, s, "R")  # box againts wall

    def test_box_against_box_illegal(self):
        lv = parse_level(["######", "#@$$.#", "#  . #", "######"])
        acts = [a for a, _ in successors(lv, lv.initial)]
        self.assertNotIn("R", acts)

    def test_walk_is_lowercase(self):
        lv = parse_level(["#####", "#@ $.#", "#####"])
        self.assertEqual([a for a, _ in successors(lv, lv.initial)], ["r"])


class TestMicroban(unittest.TestCase):
    PATH = "levels/microban.xsb"

    def test_loads_155_levels(self):
        from src.parser import load_file
        levels = load_file(self.PATH)
        self.assertEqual(len(levels), 155)
        self.assertEqual(levels[0].name, "microban_1")
        self.assertEqual(levels[-1].name, "microban_155")

    def test_all_levels_consistent(self):
        from src.parser import load_file
        for lv in load_file(self.PATH):
            self.assertEqual(len(lv.initial.boxes), len(lv.goals), lv.name)

    def test_select_subset(self):
        from src.parser import load_file
        sel = load_file(self.PATH, only=[3, 1])
        self.assertEqual([l.name for l in sel], ["microban_3", "microban_1"])
        with self.assertRaises(ValueError):
            load_file(self.PATH, only=[999])


if __name__ == "__main__":
    unittest.main()