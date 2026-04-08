from pathlib import Path

from app.core.models import CheckResult
from app.utils.shell import run_command


SSHD_CONFIG_PATH = Path("/etc/ssh/sshd_config")


def is_ssh_installed() -> bool:
    result = run_command(["which", "sshd"])
    return result.returncode == 0


def is_ssh_running() -> bool:
    """True se o servidor SSH estiver ativo (systemd ssh/sshd, service, ou processo sshd)."""
    for unit in ("ssh", "sshd"):
        result = run_command(["systemctl", "is-active", unit], check=False, timeout=15)
        if result.stdout.strip() == "active":
            return True

    svc = run_command(["service", "ssh", "status"], check=False, timeout=15)
    out = (svc.stdout + svc.stderr).lower()
    if "running" in out or "active (running)" in out:
        return True

    pg = run_command(["pgrep", "-x", "sshd"], check=False, timeout=10)
    return pg.returncode == 0


def ssh_config_exists() -> bool:
    return SSHD_CONFIG_PATH.exists()


def collect_ssh_status() -> CheckResult:
    if not is_ssh_installed():
        return CheckResult(
            name="ssh_installed",
            status="fail",
            message="SSH is not installed",
        )

    if not ssh_config_exists():
        return CheckResult(
            name="ssh_config",
            status="fail",
            message="sshd_config not found",
        )

    running = is_ssh_running()

    return CheckResult(
        name="ssh_status",
        status="pass" if running else "fail",
        message="SSH running" if running else "SSH not running",
    )