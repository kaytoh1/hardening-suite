from __future__ import annotations

import os
from pathlib import Path

from app.core.exceptions import ValidationError
from app.utils.shell import run_command
from app.utils.user_context import get_effective_user


def validate_sshd_config() -> None:
    result = run_command(["sshd", "-t"])

    if result.returncode != 0:
        raise ValidationError(f"Configuração SSH inválida:\n{result.stderr}")


def _discover_private_key_paths(ssh_dir: Path) -> list[Path]:
    candidates = [
        ssh_dir / "id_ed25519",
        ssh_dir / "id_ecdsa",
        ssh_dir / "id_rsa",
    ]
    return [p for p in candidates if p.is_file()]


def test_ssh_connection() -> bool:
    """
    Testa login em localhost com BatchMode (sem prompt).
    Tenta chaves privadas comuns no ~/.ssh do usuário efetivo.
    """
    try:
        user, home = get_effective_user()
    except ValidationError:
        return False

    ssh_dir = home / ".ssh"
    keys = _discover_private_key_paths(ssh_dir)
    if not keys:
        return False

    env = os.environ.copy()
    env.pop("SSH_AUTH_SOCK", None)

    for key_path in keys:
        result = run_command(
            [
                "ssh",
                "-o",
                "BatchMode=yes",
                "-o",
                "StrictHostKeyChecking=accept-new",
                "-o",
                "UserKnownHostsFile=" + str(ssh_dir / "known_hosts"),
                "-i",
                str(key_path),
                f"{user}@127.0.0.1",
                "echo",
                "ok",
            ],
            env=env,
        )
        if result.returncode == 0 and result.stdout.strip() == "ok":
            return True

    return False
