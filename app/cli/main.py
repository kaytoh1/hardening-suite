from __future__ import annotations

from datetime import datetime
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from app.cli.runner import run_guarded
from app.core.constants import SUPPORTED_DISTROS
from app.core.logger import setup_logger
from app.policies.ssh.ssh_hardening import harden_ssh
from app.remediators.audit_system import setup_audit_system
from app.remediators.fail2ban import setup_fail2ban
from app.remediators.firewall import setup_ufw
from app.remediators.system_advanced import harden_system_advanced
from app.remediators.system_hardening import harden_system
from app.utils.files import ensure_state_dirs
from app.utils.system import assert_supported_distro, get_os_info

app = typer.Typer(help="Linux hardening toolkit")
console = Console()
logger = setup_logger()


def _ensure_supported_distro_for_command(ctx: typer.Context) -> None:
    """
    Valida Ubuntu/Debian antes de executar hardening.
    Fica fora do callback do grupo para que `comando --help` não dispare a checagem
    (ex.: CliRunner e ambientes sem /etc/os-release).
    """
    parent = ctx.parent
    if parent is not None and parent.params.get("skip_distro_check"):
        return
    assert_supported_distro()


@app.callback()
def main(
    ctx: typer.Context,
    skip_distro_check: bool = typer.Option(
        False,
        "--skip-distro-check",
        help="Não bloqueia se a distro não for Ubuntu/Debian (perigoso).",
    ),
) -> None:
    """Inicializa diretórios; a validação de distro corre dentro de cada comando `harden-*`."""
    ensure_state_dirs()


@app.command()
def scan() -> None:
    os_info = get_os_info()

    table = Table(title="System Information")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Distro", os_info.distro)
    table.add_row("Version", os_info.version)
    table.add_row("Pretty Name", os_info.pretty_name)
    table.add_row("Kernel", os_info.kernel)
    table.add_row("Run Time", datetime.now().isoformat(timespec="seconds"))

    console.print(table)

    if os_info.distro not in SUPPORTED_DISTROS:
        console.print(
            f"[yellow]Warning:[/yellow] distro '{os_info.distro}' is not supported."
        )
    else:
        console.print("[bold green]Supported system detected.[/bold green]")

    logger.info("System scanned: %s %s", os_info.distro, os_info.version)


@app.command(name="harden-ssh")
def harden_ssh_cmd(
    ctx: typer.Context,
    public_key_file: Path | None = typer.Option(
        None,
        "--public-key-file",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Arquivo UTF-8 com uma linha de chave pública (modo não interativo).",
    ),
    ensure_ssh: bool = typer.Option(
        False,
        "--ensure-ssh",
        help="Instala openssh-server (apt) e tenta iniciar o serviço se ainda não estiver pronto.",
    ),
) -> None:
    """Aplica hardening básico do SSH."""
    console.print("[bold yellow]Applying SSH hardening...[/bold yellow]")

    def _run() -> None:
        _ensure_supported_distro_for_command(ctx)
        key_text = (
            public_key_file.read_text(encoding="utf-8") if public_key_file is not None else None
        )
        harden_ssh(public_key=key_text, ensure_ssh_server=ensure_ssh)
        console.print("[bold green]Done.[/bold green]")

    run_guarded(console, _run)


@app.command(name="harden-network")
def harden_network(
    ctx: typer.Context,
    limit_ssh: bool = typer.Option(
        False,
        "--limit-ssh",
        help="Usa 'ufw limit' nas portas SSH (mitigação a brute force na camada de firewall).",
    ),
    ensure_ipv6: bool = typer.Option(
        True,
        "--ensure-ipv6/--no-ensure-ipv6",
        help="Define IPV6=yes em /etc/default/ufw (recomendado se você usa IPv6).",
    ),
) -> None:
    """Configura firewall (UFW) e fail2ban."""
    console.print("[bold yellow]Applying network hardening...[/bold yellow]")

    def _run() -> None:
        _ensure_supported_distro_for_command(ctx)
        setup_ufw(limit_ssh=limit_ssh, ensure_ipv6=ensure_ipv6)
        setup_fail2ban()
        console.print("[bold green]Network hardening complete.[/bold green]")

    run_guarded(console, _run)


@app.command(name="harden-system")
def harden_system_cmd(ctx: typer.Context) -> None:
    """Hardening em nível de sistema (pacotes, atualizações automáticas)."""
    console.print("[bold yellow]Applying system hardening...[/bold yellow]")

    def _run() -> None:
        _ensure_supported_distro_for_command(ctx)
        harden_system()
        console.print("[bold green]System hardening complete.[/bold green]")

    run_guarded(console, _run)


@app.command(name="harden-advanced")
def harden_advanced_cmd(ctx: typer.Context) -> None:
    """Hardening avançado (serviços, módulos, sudo, permissões)."""
    console.print("[bold yellow]Applying advanced hardening...[/bold yellow]")

    def _run() -> None:
        _ensure_supported_distro_for_command(ctx)
        harden_system_advanced()
        console.print("[bold green]Advanced hardening complete.[/bold green]")

    run_guarded(console, _run)


@app.command(name="harden-audit")
def harden_audit_cmd(ctx: typer.Context) -> None:
    """Auditoria, IDS e integridade (auditd, rkhunter, AIDE)."""
    console.print("[bold yellow]Applying audit & IDS hardening...[/bold yellow]")

    def _run() -> None:
        _ensure_supported_distro_for_command(ctx)
        setup_audit_system()
        console.print("[bold green]Audit system ready.[/bold green]")

    run_guarded(console, _run)
