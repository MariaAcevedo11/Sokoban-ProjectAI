import unittest

from src.bfs import bfs
from src.parser import load_file
from src.xsbValidator import check_solution, read_xsb_levels

MICROBAN = "levels/microban.xsb"
ROOM = ["#######", "#@$ . #", "#######"]


class TestXsbValidator(unittest.TestCase):
    def testReadsAll155Levels(self):
        with open(MICROBAN, encoding="utf-8") as f:
            levels = read_xsb_levels(f.read())
        self.assertEqual(len(levels), 155)
        self.assertIn("1", levels)

    def testKnownSolutionLevel1(self):
        with open(MICROBAN, encoding="utf-8") as f:
            rows = read_xsb_levels(f.read())["1"]
        ok, msg, pushes = check_solution(rows, "dlUrrrdLullddrUluRuulDrddrruLdlUU")
        self.assertTrue(ok, msg)
        self.assertEqual(pushes, 8)

    def testValidSmall(self):
        self.assertTrue(check_solution(ROOM, "RR")[0])

    def testIncompleteRejected(self):
        self.assertFalse(check_solution(ROOM, "R")[0])

    def testWalkIntoWallRejected(self):
        self.assertFalse(check_solution(ROOM, "l")[0])

    def testPushIntoWallRejected(self):
        self.assertFalse(check_solution(ROOM, "RRRR")[0])

    def testPushBoxIntoBoxRejected(self):
        self.assertFalse(check_solution(["######", "#@$$.#", "######"], "R")[0])

    def testCaseMustMatchPush(self):
        self.assertFalse(check_solution(ROOM, "rr")[0])   # pushes written as walks
        self.assertFalse(check_solution(["#####", "#@  .#", "#####"], "R")[0])

    def testUnknownActionRejected(self):
        self.assertFalse(check_solution(ROOM, "X")[0])

    def testAgreesWithSolverOnBfsSolutions(self):
        with open(MICROBAN, encoding="utf-8") as f:
            raw = read_xsb_levels(f.read())
        for lv in load_file(MICROBAN, only=list(range(1, 9))):
            r = bfs(lv, 300_000)
            if r.solved:
                number = lv.name.rsplit("_", 1)[1]
                self.assertTrue(check_solution(raw[number], r.solution)[0], lv.name)


if __name__ == "__main__":
    unittest.main()