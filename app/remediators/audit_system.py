from pathlib import Path

from app.utils.shell import run_command
from app.core.exceptions import CommandExecutionError


# =========================
# 📊 AUDITD
# =========================

def setup_auditd():
    print("[INFO] Installing auditd...")

    run_command(
        ["bash", "-c", "DEBIAN_FRONTEND=noninteractive apt install -y auditd"],
        check=True,
        timeout=300
    )

    print("[INFO] Enabling auditd...")
    run_command(["systemctl", "enable", "--now", "auditd"], check=True)

    print("[OK] auditd active")


# =========================
# 🧠 RKHUNTER
# =========================

def setup_rkhunter():
    print("[INFO] Installing rkhunter...")

    run_command(
        ["bash", "-c", "DEBIAN_FRONTEND=noninteractive apt install -y rkhunter"],
        check=True,
        timeout=600
    )

    print("[INFO] Updating rkhunter database...")
    result = run_command(["rkhunter", "--update"], check=False)

    if result.returncode != 0:
        print("[WARNING] rkhunter update failed (non-critical)")

    print("[INFO] Running initial scan...")
    run_command(
        ["rkhunter", "--check", "--sk"],
        check=False,
        timeout=600
    )

    print("[OK] rkhunter configured")


# =========================
# 📦 AIDE
# =========================

AIDE_DB = Path("/var/lib/aide/aide.db")


def setup_aide():
    print("[INFO] Installing AIDE...")

    run_command(
        ["bash", "-c", "DEBIAN_FRONTEND=noninteractive apt install -y aide"],
        check=True,
        timeout=300
    )

    print("[INFO] Starting AIDE initialization (this may take a long time)...")

    try:
        run_command(
            ["aideinit"],
            check=False,
            timeout=120
        )
    except CommandExecutionError:
        print("[WARNING] AIDE initialization timed out (non-critical)")

    # mover DB se existir
    run_command(
        [
            "bash",
            "-c",
            "if [ -f /var/lib/aide/aide.db.new ]; then mv /var/lib/aide/aide.db.new /var/lib/aide/aide.db; fi"
        ],
        check=False
    )

    print("[OK] AIDE setup complete")


# =========================
# 🚀 EXECUÇÃO COMPLETA
# =========================

def setup_audit_system():
    setup_auditd()
    setup_rkhunter()
    setup_aide()
