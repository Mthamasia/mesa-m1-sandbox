"""Synthetic mission #6 test cases."""
import unittest
from mesa_sandbox.m1demo_6 import mission_receipt


class SyntheticMissionTests(unittest.TestCase):
    def test_id(self):
        self.assertEqual(mission_receipt()["mission_id"], "M1-DEMO-6")

    def test_properties(self):
        self.assertEqual(mission_receipt()["kind"], "synthetic")
        self.assertIs(mission_receipt()["validated"], True)


if __name__ == "__main__":
    unittest.main()
