"""Execução de comandos CLI com tratamento uniforme de erros e códigos de saída."""

from __future__ import annotations

from collections.abc import Callable

import typer
from rich.console import Console

from app.core.exceptions import (
    BackupError,
    CommandExecutionError,
    HardeningError,
    RollbackError,
    UnsupportedSystemError,
    ValidationError,
)

# 0 = sucesso; 1 = falha geral/comando; 2 = validação; 3 = rollback; 4 = backup; 5 = sistema não suportado
_EXIT_VALIDATION = 2
_EXIT_ROLLBACK = 3
_EXIT_BACKUP = 4
_EXIT_UNSUPPORTED = 5


def run_guarded(console: Console, fn: Callable[[], None]) -> None:
    """Executa `fn`; em erro imprime mensagem legível e encerra com typer.Exit."""
    try:
        fn()
    except ValidationError as exc:
        console.print(f"[red]Erro de validação:[/red] {exc}")
        raise typer.Exit(_EXIT_VALIDATION) from exc
    except RollbackError as exc:
        console.print(f"[yellow]Operação revertida ou requer atenção:[/yellow] {exc}")
        raise typer.Exit(_EXIT_ROLLBACK) from exc
    except BackupError as exc:
        console.print(f"[red]Erro de backup/restauração:[/red] {exc}")
        raise typer.Exit(_EXIT_BACKUP) from exc
    except UnsupportedSystemError as exc:
        console.print(f"[red]Sistema não suportado:[/red] {exc}")
        raise typer.Exit(_EXIT_UNSUPPORTED) from exc
    except CommandExecutionError as exc:
        console.print(f"[red]Falha ao executar comando:[/red] {exc}")
        raise typer.Exit(1) from exc
    except HardeningError as exc:
        console.print(f"[red]Erro:[/red] {exc}")
        raise typer.Exit(1) from exc
    except RuntimeError as exc:
        console.print(f"[red]Falha:[/red] {exc}")
        raise typer.Exit(1) from exc
