from datetime import datetime
from app.remediators.system_hardening import harden_system
import typer
from rich.console import Console
from rich.table import Table
from app.remediators.system_advanced import harden_system_advanced
from app.core.constants import SUPPORTED_DISTROS
from app.core.logger import setup_logger
from app.utils.files import ensure_state_dirs
from app.utils.system import get_os_info
from app.remediators.audit_system import setup_audit_system
# 👇 IMPORTANTE
from app.policies.ssh.ssh_hardening import harden_ssh
from app.remediators.firewall import setup_ufw
from app.remediators.fail2ban import setup_fail2ban

app = typer.Typer(help="Linux hardening toolkit")
console = Console()
logger = setup_logger()


@app.callback()
def main() -> None:
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


# 🔥 COMANDO QUE ESTAVA FALTANDO DIREITO
@app.command(name="harden-ssh")
def harden_ssh_cmd():
    """
    Apply basic SSH hardening
    """
    console.print("[bold yellow]Applying SSH hardening...[/bold yellow]")
    harden_ssh()
    console.print("[bold green]Done.[/bold green]")



@app.command(name="harden-network")
def harden_network() -> None:
    """
    Setup firewall and intrusion prevention
    """
    console.print("[bold yellow]Applying network hardening...[/bold yellow]")

    setup_ufw()
    setup_fail2ban()

    console.print("[bold green]Network hardening complete.[/bold green]")


@app.command(name="harden-system")
def harden_system_cmd():
    """
    System-level hardening
    """
    console.print("[bold yellow]Applying system hardening...[/bold yellow]")

    harden_system()

    console.print("[bold green]System hardening complete.[/bold green]")





@app.command(name="harden-advanced")
def harden_advanced_cmd():
    """
    Advanced system hardening
    """
    console.print("[bold yellow]Applying advanced hardening...[/bold yellow]")

    harden_system_advanced()

    console.print("[bold green]Advanced hardening complete.[/bold green]")



@app.command(name="harden-audit")
def harden_audit_cmd():
    """
    Setup auditing, IDS and integrity monitoring
    """
    console.print("[bold yellow]Applying audit & IDS hardening...[/bold yellow]")

    setup_audit_system()

    console.print("[bold green]Audit system ready.[/bold green]")
