from __future__ import annotations

import io
import unittest

import typer
from rich.console import Console

from app.cli.runner import run_guarded
from app.core.exceptions import (
    BackupError,
    CommandExecutionError,
    RollbackError,
    UnsupportedSystemError,
    ValidationError,
)


class TestRunGuarded(unittest.TestCase):
    def setUp(self) -> None:
        self.console = Console(file=io.StringIO(), width=120, force_terminal=False)

    def test_success_no_exit(self) -> None:
        called: list[int] = []

        def ok() -> None:
            called.append(1)

        run_guarded(self.console, ok)
        self.assertEqual(called, [1])

    def test_validation_exits_2(self) -> None:
        def bad() -> None:
            raise ValidationError("inválido")

        with self.assertRaises(typer.Exit) as ctx:
            run_guarded(self.console, bad)
        self.assertEqual(ctx.exception.exit_code, 2)

    def test_rollback_exits_3(self) -> None:
        def bad() -> None:
            raise RollbackError("revertido")

        with self.assertRaises(typer.Exit) as ctx:
            run_guarded(self.console, bad)
        self.assertEqual(ctx.exception.exit_code, 3)

    def test_backup_exits_4(self) -> None:
        def bad() -> None:
            raise BackupError("falha backup")

        with self.assertRaises(typer.Exit) as ctx:
            run_guarded(self.console, bad)
        self.assertEqual(ctx.exception.exit_code, 4)

    def test_unsupported_exits_5(self) -> None:
        def bad() -> None:
            raise UnsupportedSystemError("fedora")

        with self.assertRaises(typer.Exit) as ctx:
            run_guarded(self.console, bad)
        self.assertEqual(ctx.exception.exit_code, 5)

    def test_command_execution_exits_1(self) -> None:
        def bad() -> None:
            raise CommandExecutionError("apt falhou")

        with self.assertRaises(typer.Exit) as ctx:
            run_guarded(self.console, bad)
        self.assertEqual(ctx.exception.exit_code, 1)

    def test_runtime_error_exits_1(self) -> None:
        def bad() -> None:
            raise RuntimeError("ssh down")

        with self.assertRaises(typer.Exit) as ctx:
            run_guarded(self.console, bad)
        self.assertEqual(ctx.exception.exit_code, 1)
