from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from app.cli.main import app
from app.core.models import OSInfo


class TestMainCli(unittest.TestCase):
    def setUp(self) -> None:
        self.runner = CliRunner()

    @patch("app.cli.main.logger")
    @patch("app.cli.main.get_os_info")
    def test_scan_ok(self, mock_info: MagicMock, _mock_logger: MagicMock) -> None:
        mock_info.return_value = OSInfo(
            distro="ubuntu",
            version="22.04",
            pretty_name="Ubuntu 22.04",
            kernel="5.15",
        )
        result = self.runner.invoke(app, ["scan"])
        self.assertEqual(result.exit_code, 0, result.stdout)

    @patch("app.utils.system.get_os_info")
    def test_harden_system_blocked_unsupported_distro(self, mock_go: MagicMock) -> None:
        mock_go.return_value = OSInfo(
            distro="fedora",
            version="40",
            pretty_name="Fedora 40",
            kernel="6.8",
        )
        result = self.runner.invoke(app, ["harden-system"])
        self.assertEqual(result.exit_code, 5, result.stdout + result.stderr)

    @patch("app.cli.main.harden_system")
    def test_harden_system_runs_with_skip_distro_check(self, mock_harden: MagicMock) -> None:
        result = self.runner.invoke(app, ["--skip-distro-check", "harden-system"])
        self.assertEqual(result.exit_code, 0, result.stdout + result.stderr)
        mock_harden.assert_called_once()

    def test_subcommand_help_skips_distro_check(self) -> None:
        result = self.runner.invoke(app, ["harden-ssh", "--help"])
        self.assertEqual(result.exit_code, 0, result.stderr)
        self.assertIn("ensure-ssh", result.stdout)
