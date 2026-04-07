from pathlib import Path

from app.core.models import CheckResult
from app.utils.shell import run_command


SSHD_CONFIG_PATH = Path("/etc/ssh/sshd_config")


def is_ssh_installed() -> bool:
    result = run_command(["which", "sshd"])
    return result.returncode == 0


def is_ssh_running() -> bool:
    result = run_command(["systemctl", "is-active", "ssh"])
    return result.stdout == "active"


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