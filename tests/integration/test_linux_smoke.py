"""
Smoke em SO Linux real: valida leitura do sistema e subprocess sem aplicar hardening.

Em Windows os testes são ignorados (skip). No CI (ubuntu-latest) executam sempre.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

from app.utils.shell import run_command


@unittest.skipUnless(sys.platform.startswith("linux"), "requer kernel Linux")
class TestLinuxIntegrationSmoke(unittest.TestCase):
    def test_etc_os_release_exists(self) -> None:
        self.assertTrue(
            Path("/etc/os-release").is_file(),
            "Ambiente Linux deveria expor /etc/os-release",
        )

    def test_get_os_info_runs(self) -> None:
        from app.utils.system import get_os_info

        info = get_os_info()
        self.assertTrue(info.distro)
        self.assertTrue(info.kernel)

    def test_uname_is_linux(self) -> None:
        result = run_command(["uname", "-s"], check=True, timeout=10)
        self.assertEqual(result.stdout.strip(), "Linux")
