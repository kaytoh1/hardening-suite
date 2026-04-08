from __future__ import annotations

import unittest

from app.remediators.ssh_manager import set_config_value


class TestSshdGlobalParser(unittest.TestCase):
    def test_only_changes_global_before_first_match(self) -> None:
        lines = [
            "Port 22",
            "Match User git",
            "PasswordAuthentication yes",
            "",
        ]
        out = set_config_value(lines, "PasswordAuthentication", "no")
        self.assertEqual(out[0], "Port 22")
        self.assertEqual(out[1], "PasswordAuthentication no")
        self.assertEqual(out[2], "Match User git")
        self.assertEqual(out[3], "PasswordAuthentication yes")

    def test_no_match_entire_file_is_global(self) -> None:
        lines = ["Port 22", "PasswordAuthentication yes"]
        out = set_config_value(lines, "PasswordAuthentication", "no")
        self.assertTrue(any(x.strip() == "PasswordAuthentication no" for x in out))
        self.assertEqual(len([x for x in out if "PasswordAuthentication" in x]), 1)

    def test_preserves_comments_in_global(self) -> None:
        lines = ["# old", "PasswordAuthentication yes"]
        out = set_config_value(lines, "PasswordAuthentication", "no")
        self.assertIn("# old", out)