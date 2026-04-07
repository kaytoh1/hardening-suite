import os
import pwd
from pathlib import Path
from app.utils.shell import run_command
from app.validators.ssh_validator import test_ssh_connection

SSHD_CONFIG_PATH = Path("/etc/ssh/sshd_config")


# =============================
# 🔍 CONFIG SSH
# =============================

def read_sshd_config() -> list[str]:
    return SSHD_CONFIG_PATH.read_text(encoding="utf-8").splitlines()


def write_sshd_config(lines: list[str]) -> None:
    SSHD_CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def set_config_value(lines: list[str], key: str, value: str) -> list[str]:
    new_lines = []
    found = False

    for line in lines:
        stripped = line.strip()

        if stripped.lower().startswith(key.lower()):
            new_lines.append(f"{key} {value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key} {value}")

    return new_lines


# =============================
# 👤 USER DETECTION
# =============================

def get_real_user() -> tuple[str, Path]:
    sudo_user = os.environ.get("SUDO_USER")

    if sudo_user:
        user_info = pwd.getpwnam(sudo_user)
        return sudo_user, Path(user_info.pw_dir)

    user = os.environ.get("USER")
    return user, Path.home()


# =============================
# 🔐 SSH KEY MANAGEMENT
# =============================

def add_ssh_key(public_key: str) -> None:
    user, home = get_real_user()

    ssh_dir = home / ".ssh"
    authorized_keys = ssh_dir / "authorized_keys"

    ssh_dir.mkdir(parents=True, exist_ok=True)

    if authorized_keys.exists():
        existing = authorized_keys.read_text()
        if public_key.strip() in existing:
            return

    with authorized_keys.open("a") as f:
        f.write(public_key.strip() + "\n")

    # 🔐 Permissões
    os.chmod(ssh_dir, 0o700)
    os.chmod(authorized_keys, 0o600)

    # 👤 Owner correto
    try:
        uid = pwd.getpwnam(user).pw_uid
        gid = pwd.getpwnam(user).pw_gid
        os.chown(ssh_dir, uid, gid)
        os.chown(authorized_keys, uid, gid)
    except Exception:
        pass


def restart_ssh_safe() -> None:
    print("[INFO] Testing SSH connection before restart...")

    if not test_ssh_connection():
        raise RuntimeError(
            "SSH test failed before restart. Use ssh-agent or remove passphrase."
        )

    print("[OK] SSH test successful")

    print("[INFO] Restarting SSH service...")
    run_command(["service", "ssh", "restart"], check=True)

    print("[INFO] Testing SSH after restart...")

    if not test_ssh_connection():
        raise RuntimeError("SSH failed after restart! Possible lockout.")

    print("[OK] SSH restart successful and connection verified")
