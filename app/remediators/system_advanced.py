from __future__ import annotations

import os
import re
from pathlib import Path

from app.utils.shell import run_command

# =========================
# Desabilitar serviços desnecessários
# =========================

DANGEROUS_SERVICES = [
    "telnet",
    "rsh-server",
    "rlogin",
    "rexec",
    "avahi-daemon",
    "cups",
]

_MODPROBE_LINE = re.compile(r"^install\s+([a-zA-Z0-9_-]+)\s+/bin/true\s*$")
_MODULE_NAME = re.compile(r"^[a-zA-Z0-9_-]+$")

MODPROBE_HARDENING = Path("/etc/modprobe.d/hardening.conf")
SUDO_DROPIN = Path("/etc/sudoers.d/99-hardening-suite")

SUDO_DROPIN_CONTENT = """# Gerenciado por hardening-suite — não editar manualmente sem visudo
Defaults use_pty
Defaults logfile="/var/log/sudo.log"
"""


def disable_unnecessary_services() -> None:
    print("[INFO] Desabilitando serviços desnecessários...")

    for service in DANGEROUS_SERVICES:
        run_command(["systemctl", "disable", "--now", service], check=False)

    print("[OK] Serviços desnecessários processados")


def _ensure_modprobe_install_line(module: str) -> None:
    if not _MODULE_NAME.fullmatch(module):
        raise ValueError(f"Nome de módulo inválido: {module!r}")

    line = f"install {module} /bin/true\n"
    MODPROBE_HARDENING.parent.mkdir(parents=True, exist_ok=True)

    if MODPROBE_HARDENING.is_file():
        current = MODPROBE_HARDENING.read_text(encoding="utf-8")
        if line in current:
            return
        for existing in current.splitlines():
            m = _MODPROBE_LINE.match(existing.strip())
            if m and m.group(1) == module:
                return

    with MODPROBE_HARDENING.open("a", encoding="utf-8") as f:
        f.write(line)


def blacklist_kernel_modules() -> None:
    print("[INFO] Bloqueando módulos de kernel (modprobe)...")

    modules = [
        "cramfs",
        "freevxfs",
        "jffs2",
        "hfs",
        "hfsplus",
        "squashfs",
        "udf",
        "usb-storage",
    ]

    for module in modules:
        _ensure_modprobe_install_line(module)

    print("[OK] Módulos adicionados ao blacklist (sem shell)")


def fix_permissions() -> None:
    print("[INFO] Ajustando permissões críticas...")

    commands = [
        ["chmod", "600", "/etc/shadow"],
        ["chmod", "644", "/etc/passwd"],
        ["chmod", "644", "/etc/group"],
        ["chmod", "600", "/etc/gshadow"],
    ]

    for cmd in commands:
        run_command(cmd, check=True)

    print("[OK] Permissões ajustadas")


def harden_sudo() -> None:
    print("[INFO] Endurecendo sudo via /etc/sudoers.d/...")

    if SUDO_DROPIN.is_file():
        existing = SUDO_DROPIN.read_text(encoding="utf-8")
        if existing.strip() == SUDO_DROPIN_CONTENT.strip():
            print("[OK] Drop-in sudo já aplicado")
            return

    SUDO_DROPIN.write_text(SUDO_DROPIN_CONTENT, encoding="utf-8")
    os.chmod(SUDO_DROPIN, 0o440)
    os.chown(SUDO_DROPIN, 0, 0)

    check = run_command(["visudo", "-cf", str(SUDO_DROPIN)], check=False)
    if check.returncode != 0:
        try:
            SUDO_DROPIN.unlink(missing_ok=True)
        except OSError:
            pass
        raise RuntimeError(
            f"visudo rejeitou o drop-in: {check.stderr or check.stdout}"
        )

    print("[OK] Sudo endurecido (drop-in validado por visudo)")


def harden_system_advanced() -> None:
    disable_unnecessary_services()
    blacklist_kernel_modules()
    fix_permissions()
    harden_sudo()
