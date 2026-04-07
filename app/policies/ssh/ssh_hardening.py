from pathlib import Path

from app.collectors.ssh import collect_ssh_status
from app.remediators.ssh_manager import (
    read_sshd_config,
    write_sshd_config,
    set_config_value,
    add_ssh_key,
)
from app.utils.files import backup_file
from app.validators.ssh_validator import validate_sshd_config
from app.remediators.ssh_manager import restart_ssh_safe

SSHD_CONFIG_PATH = Path("/etc/ssh/sshd_config")


def harden_ssh(enforce_pubkey: bool = True, disable_password: bool = True) -> None:
    status = collect_ssh_status()

    if status.status != "pass":
        raise RuntimeError("SSH is not ready for hardening")

    # 🔐 PASSO NOVO — chave SSH
    print("\n🔑 SSH KEY SETUP")
    public_key = input("Paste your SSH public key: ").strip()

    if not public_key.startswith("ssh-"):
        raise ValueError("Invalid SSH key format")

    add_ssh_key(public_key)
    print("[OK] SSH key added")

    # 🔥 BACKUP
    backup_path = backup_file(SSHD_CONFIG_PATH)
    print(f"[INFO] Backup created at: {backup_path}")

    lines = read_sshd_config()

    # 🔐 Hardening
    if enforce_pubkey:
        lines = set_config_value(lines, "PubkeyAuthentication", "yes")

    if disable_password:
        lines = set_config_value(lines, "PasswordAuthentication", "no")

    lines = set_config_value(lines, "PermitRootLogin", "no")

    # 💾 escreve config
    write_sshd_config(lines)

    # 🧪 valida
    validate_sshd_config()

    print("[OK] SSH configuration validated successfully")
    print("[INFO] Applying SSH changes safely...")
restart_ssh_safe()
