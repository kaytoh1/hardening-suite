from __future__ import annotations

import unittest

from app.remediators.fail2ban import build_sshd_jail_local_content


class TestFail2banJail(unittest.TestCase):
    def test_ports_csv(self) -> None:
        text = build_sshd_jail_local_content([22, 2222])
        self.assertIn("port = 22,2222", text)
        self.assertIn("[sshd]", text)

    def test_empty_fallback_ssh_keyword(self) -> None:
        text = build_sshd_jail_local_content([])
        self.assertIn("port = ssh", text)