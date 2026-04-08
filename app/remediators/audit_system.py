from pathlib import Path

import shutil

from app.core.exceptions import CommandExecutionError
from app.utils.shell import run_command

_APT_ENV = {"DEBIAN_FRONTEND": "noninteractive"}

AIDE_DB_NEW = Path("/var/lib/aide/aide.db.new")
AIDE_DB = Path("/var/lib/aide/aide.db")


def setup_auditd() -> None:
    print("[INFO] Instalando auditd...")

    run_command(
        ["apt", "install", "-y", "auditd"],
        check=True,
        timeout=300,
        env=_APT_ENV,
    )

    print("[INFO] Habilitando auditd...")
    run_command(["systemctl", "enable", "--now", "auditd"], check=True)

    print("[OK] auditd ativo")


def setup_rkhunter() -> None:
    print("[INFO] Instalando rkhunter...")

    run_command(
        ["apt", "install", "-y", "rkhunter"],
        check=True,
        timeout=600,
        env=_APT_ENV,
    )

    print("[INFO] Atualizando base do rkhunter...")
    result = run_command(["rkhunter", "--update"], check=False)

    if result.returncode != 0:
        print("[WARNING] Atualização do rkhunter falhou (não crítico)")

    print("[INFO] Executando verificação inicial...")
    run_command(
        ["rkhunter", "--check", "--sk"],
        check=False,
        timeout=600,
    )

    print("[OK] rkhunter configurado")


def _finalize_aide_database() -> None:
    if AIDE_DB_NEW.is_file():
        try:
            shutil.move(str(AIDE_DB_NEW), str(AIDE_DB))
        except OSError as exc:
            print(f"[WARNING] Não foi possível mover a base AIDE: {exc}")


def setup_aide() -> None:
    print("[INFO] Instalando AIDE...")

    run_command(
        ["apt", "install", "-y", "aide"],
        check=True,
        timeout=300,
        env=_APT_ENV,
    )

    print("[INFO] Inicializando AIDE (pode demorar)...")

    try:
        run_command(
            ["aideinit"],
            check=False,
            timeout=600,
        )
    except CommandExecutionError:
        print("[WARNING] aideinit excedeu o tempo (não crítico)")

    _finalize_aide_database()

    print("[OK] AIDE configurado")


def setup_audit_system() -> None:
    setup_auditd()
    setup_rkhunter()
    setup_aide()
