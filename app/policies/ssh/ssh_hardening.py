from pathlib import Path

from app.collectors.ssh import collect_ssh_status
from app.core.exceptions import RollbackError
from app.remediators.ssh_manager import (
    add_ssh_key,
    read_sshd_config,
    restart_ssh_safe,
    set_config_value,
    write_sshd_config,
)
from app.utils.files import backup_file
from app.validators.ssh_public_key import validate_ssh_public_key_line
from app.validators.ssh_validator import validate_sshd_config

SSHD_CONFIG_PATH = Path("/etc/ssh/sshd_config")


def harden_ssh(
    enforce_pubkey: bool = True,
    disable_password: bool = True,
    public_key: str | None = None,
    ensure_ssh_server: bool = False,
) -> None:
    if ensure_ssh_server:
        from app.remediators.ssh_bootstrap import ensure_openssh_server

        ensure_openssh_server()

    status = collect_ssh_status()

    if status.status != "pass":
        raise RuntimeError(
            "SSH não está pronto para hardening. "
            f"Motivo: {status.message}. "
            "Em Ubuntu/Debian: sudo apt install -y openssh-server && sudo service ssh start "
            "(no WSL pode ser necessário ativar systemd ou usar uma VM Linux)."
        )

    print("\n🔑 CONFIGURAÇÃO DE CHAVE SSH")
    if public_key is not None:
        raw_key = public_key.strip()
    else:
        raw_key = input("Cole sua chave pública SSH (uma linha, sem opções): ").strip()

    public_key_norm = validate_ssh_public_key_line(raw_key)

    add_ssh_key(public_key_norm)
    print("[OK] Chave SSH adicionada ao authorized_keys")

    backup_path = backup_file(SSHD_CONFIG_PATH)
    print(f"[INFO] Backup de sshd_config: {backup_path}")

    lines = read_sshd_config()

    if enforce_pubkey:
        lines = set_config_value(lines, "PubkeyAuthentication", "yes")

    if disable_password:
        lines = set_config_value(lines, "PasswordAuthentication", "no")

    lines = set_config_value(lines, "PermitRootLogin", "no")

    write_sshd_config(lines)

    validate_sshd_config()

    print("[OK] sshd_config validado (sshd -t)")
    print("[INFO] Aplicando alterações com verificação de acesso...")
    try:
        restart_ssh_safe(sshd_config_backup=backup_path)
    except RollbackError as exc:
        print(f"[AVISO] {exc}")
        raise
