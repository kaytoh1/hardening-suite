"""Instalação e arranque opcional do openssh-server (Ubuntu/Debian)."""

from __future__ import annotations

from app.collectors.ssh import (
    collect_ssh_status,
    is_ssh_installed,
    ssh_config_exists,
)
from app.utils.shell import run_command

_APT_ENV = {"DEBIAN_FRONTEND": "noninteractive"}


def ensure_openssh_server() -> None:
    """
    Garante pacote e serviço SSH ativos.
    Usar só com consentimento explícito (ex.: flag --ensure-ssh): implica `apt-get` e alteração do sistema.
    """
    if not is_ssh_installed() or not ssh_config_exists():
        print("[INFO] openssh-server ausente ou incompleto; instalando via apt...")
        run_command(["apt-get", "update"], check=True, timeout=180, env=_APT_ENV)
        run_command(
            ["apt-get", "install", "-y", "openssh-server"],
            check=True,
            timeout=600,
            env=_APT_ENV,
        )

    if collect_ssh_status().status == "pass":
        print("[OK] Servidor SSH já está ativo")
        return

    print("[INFO] Servidor SSH instalado mas inativo; tentando iniciar...")
    for args in (
        ["systemctl", "start", "ssh"],
        ["systemctl", "start", "sshd"],
        ["service", "ssh", "start"],
    ):
        run_command(list(args), check=False, timeout=45)

    final = collect_ssh_status()
    if final.status != "pass":
        raise RuntimeError(
            "Não foi possível deixar o SSH pronto após install/start. "
            f"Estado: {final.message}. "
            "No WSL, verifique systemd em /etc/wsl.conf ou inicie manualmente: sudo service ssh start"
        )

    print("[OK] Servidor SSH iniciado")
