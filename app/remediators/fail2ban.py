from pathlib import Path

from app.utils.shell import run_command

JAIL_LOCAL = Path("/etc/fail2ban/jail.local")


def setup_fail2ban() -> None:
    print("[INFO] Installing fail2ban...")
    run_command(["apt", "update"], check=True)
    run_command(["apt", "install", "-y", "fail2ban"], check=True)

    print("[INFO] Configuring fail2ban...")

    config = """
[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
maxretry = 5
bantime = 600
findtime = 600
"""

    JAIL_LOCAL.write_text(config)

    print("[INFO] Restarting fail2ban...")
    run_command(["service", "fail2ban", "restart"], check=True)

    print("[OK] fail2ban configured")
