"""Synthetic mission #4 test cases."""
import unittest
from mesa_sandbox.m1demo_4 import mission_receipt


class SyntheticMissionTests(unittest.TestCase):
    def test_id(self):
        self.assertEqual(mission_receipt()["mission_id"], "M1-DEMO-4")

    def test_properties(self):
        self.assertEqual(mission_receipt()["kind"], "synthetic")
        self.assertIs(mission_receipt()["validated"], True)


if __name__ == "__main__":
    unittest.main()
