from pathlib import Path

from app.remediators.ssh_manager import get_sshd_listen_ports
from app.utils.files import backup_file
from app.utils.shell import run_command

UFW_DEFAULT = Path("/etc/default/ufw")


def _ensure_ufw_ipv6_default(*, ipv6_enabled: bool) -> None:
    """
    Ajusta IPV6=yes|no em /etc/default/ufw antes de habilitar regras.
    Com IPV6=yes, o UFW aplica regras também para IPv6 quando a pilha estiver ativa.
    """
    if not UFW_DEFAULT.is_file():
        print("[INFO] /etc/default/ufw não encontrado; mantendo padrão da distro para IPv6.")
        return

    want = "yes" if ipv6_enabled else "no"
    lines = UFW_DEFAULT.read_text(encoding="utf-8").splitlines()
    new_lines: list[str] = []
    found = False
    changed = False

    for line in lines:
        cfg = line.split("#", 1)[0].strip()
        if cfg.upper().startswith("IPV6="):
            found = True
            cur = cfg.split("=", 1)[-1].strip().lower()
            if cur != want:
                changed = True
            new_lines.append(f"IPV6={want}")
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"IPV6={want}")
        changed = True

    if changed:
        backup_file(UFW_DEFAULT)
        UFW_DEFAULT.write_text("\n".join(new_lines) + "\n", encoding="utf-8")
        print(f"[INFO] /etc/default/ufw: IPV6={want} (backup em state/backups)")


def setup_ufw(*, limit_ssh: bool = False, ensure_ipv6: bool = True) -> None:
    print("[INFO] Instalando UFW...")
    run_command(["apt", "update"], check=True)
    run_command(["apt", "install", "-y", "ufw"], check=True)

    _ensure_ufw_ipv6_default(ipv6_enabled=ensure_ipv6)

    print("[INFO] Configurando regras do firewall...")

    run_command(["ufw", "--force", "reset"], check=True)

    run_command(["ufw", "default", "deny", "incoming"], check=True)
    run_command(["ufw", "default", "allow", "outgoing"], check=True)

    ports = get_sshd_listen_ports()
    for port in ports:
        if limit_ssh:
            print(f"[INFO] SSH na porta TCP {port} com limite de taxa (ufw limit)...")
            run_command(["ufw", "limit", f"{port}/tcp"], check=True)
        else:
            print(f"[INFO] Liberando SSH na porta TCP {port} (IPv4/IPv6 se IPV6=yes)...")
            run_command(["ufw", "allow", f"{port}/tcp"], check=True)

    print("[INFO] Habilitando firewall...")
    run_command(["ufw", "--force", "enable"], check=True)

    status = run_command(["ufw", "status", "verbose"], check=False)
    if status.stdout:
        print("[INFO] Status UFW (resumo):")
        print(status.stdout[:2000] + ("..." if len(status.stdout) > 2000 else ""))

    print("[OK] UFW configurado")
