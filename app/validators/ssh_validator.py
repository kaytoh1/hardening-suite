from app.core.exceptions import ValidationError
from app.utils.shell import run_command


def validate_sshd_config() -> None:
    result = run_command(["sshd", "-t"])

    if result.returncode != 0:
        raise ValidationError(f"Invalid SSH configuration:\n{result.stderr}")


from pathlib import Path
import os

from app.utils.shell import run_command


def test_ssh_connection() -> bool:
    user = os.environ.get("SUDO_USER") or os.environ.get("USER")

    key_path = Path("/home") / user / ".ssh/id_ed25519"

    result = run_command(
        [
            "ssh",
            "-o", "BatchMode=yes",
            "-o", "StrictHostKeyChecking=no",
            "-i", str(key_path),
            f"{user}@localhost",
            "echo", "ok"
        ]
    )

    return result.returncode == 0 and result.stdout.strip() == "ok"
