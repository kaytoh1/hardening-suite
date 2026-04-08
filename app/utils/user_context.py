"""Resolução segura do usuário efetivo (sudo vs root)."""

from __future__ import annotations

import os
import re
from pathlib import Path

from app.core.exceptions import ValidationError

# Nomes de usuário POSIX razoáveis (evita confiar em strings arbitrárias do ambiente).
_LINUX_USER = re.compile(r"^[a-z_][a-z0-9_-]{0,31}$")


def get_effective_user() -> tuple[str, Path]:
    """
    Retorna (username, home) do operador real.
    Com sudo: usa SUDO_USER validado contra passwd.
    Sem sudo: usa USER ou root.
    """
    import pwd  # noqa: PLC0415 — só existe em Unix; import tardio evita falha em import no Windows.

    sudo_user = os.environ.get("SUDO_USER")
    if sudo_user:
        if not _LINUX_USER.fullmatch(sudo_user):
            raise ValidationError("SUDO_USER inválido ou inseguro.")
        try:
            info = pwd.getpwnam(sudo_user)
        except KeyError as exc:
            raise ValidationError(f"Usuário SUDO_USER não existe: {sudo_user}") from exc
        return sudo_user, Path(info.pw_dir)

    user = os.environ.get("USER") or "root"
    if user != "root" and not _LINUX_USER.fullmatch(user):
        raise ValidationError("USER inválido ou inseguro.")
    try:
        info = pwd.getpwnam(user)
    except KeyError as exc:
        raise ValidationError(f"Usuário não encontrado: {user}") from exc
    return user, Path(info.pw_dir)
