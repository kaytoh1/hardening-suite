from pathlib import Path

from app.remediators.ssh_manager import get_sshd_listen_ports
from app.utils.files import backup_file
from app.utils.shell import run_command

JAIL_LOCAL = Path("/etc/fail2ban/jail.local")


def build_sshd_jail_local_content(ports: list[int]) -> str:
    """Gera jail.local para sshd alinhado às portas reais do sshd."""
    if ports:
        port_spec = ",".join(str(p) for p in ports)
    else:
        port_spec = "ssh"
    return (
        "[sshd]\n"
        "enabled = true\n"
        f"port = {port_spec}\n"
        "logpath = /var/log/auth.log\n"
        "maxretry = 5\n"
        "bantime = 600\n"
        "findtime = 600\n"
    )


def setup_fail2ban() -> None:
    print("[INFO] Instalando fail2ban...")
    run_command(["apt", "update"], check=True)
    run_command(["apt", "install", "-y", "fail2ban"], check=True)

    print("[INFO] Configurando fail2ban (portas SSH conforme sshd_config)...")

    ports = get_sshd_listen_ports()
    config = build_sshd_jail_local_content(ports)

    if JAIL_LOCAL.is_file():
        backup_file(JAIL_LOCAL)
        print("[INFO] Backup do jail.local anterior em state/backups")

    JAIL_LOCAL.write_text(config, encoding="utf-8")

    print("[INFO] Reiniciando fail2ban...")
    run_command(["service", "fail2ban", "restart"], check=True)

    print("[OK] fail2ban configurado")
