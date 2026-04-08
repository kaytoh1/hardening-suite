from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app.remediators.system_advanced as system_advanced


class TestModprobeHardening(unittest.TestCase):
    def test_install_line_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "hardening.conf"
            with patch.object(system_advanced, "MODPROBE_HARDENING", target):
                system_advanced._ensure_modprobe_install_line("usb-storage")
                system_advanced._ensure_modprobe_install_line("usb-storage")
                content = target.read_text(encoding="utf-8")
                self.assertEqual(content.count("install usb-storage /bin/true"), 1)

    def test_invalid_module_name(self) -> None:
        with self.assertRaises(ValueError):
            system_advanced._ensure_modprobe_install_line("../../etc/passwd")