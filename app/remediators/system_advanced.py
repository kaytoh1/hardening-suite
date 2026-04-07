from app.utils.shell import run_command


# =========================
# 🚫 DESABILITAR SERVIÇOS PERIGOSOS
# =========================

DANGEROUS_SERVICES = [
    "telnet",
    "rsh-server",
    "rlogin",
    "rexec",
    "avahi-daemon",
    "cups",  # impressora (geralmente desnecessário em servidor)
]


def disable_unnecessary_services():
    print("[INFO] Disabling unnecessary services...")

    for service in DANGEROUS_SERVICES:
        run_command(["systemctl", "disable", "--now", service])

    print("[OK] Unnecessary services disabled")


# =========================
# 🔒 BLOQUEAR KERNEL MODULES PERIGOSOS
# =========================

def blacklist_kernel_modules():
    print("[INFO] Blacklisting dangerous kernel modules...")

    modules = [
        "cramfs",
        "freevxfs",
        "jffs2",
        "hfs",
        "hfsplus",
        "squashfs",
        "udf",
        "usb-storage"
    ]

    for module in modules:
        run_command([
            "bash", "-c",
            f"echo 'install {module} /bin/true' >> /etc/modprobe.d/hardening.conf"
        ])

    print("[OK] Kernel modules blacklisted")


# =========================
# 🔐 HARDENING DE PERMISSÕES
# =========================

def fix_permissions():
    print("[INFO] Fixing critical permissions...")

    commands = [
        ["chmod", "600", "/etc/shadow"],
        ["chmod", "644", "/etc/passwd"],
        ["chmod", "644", "/etc/group"],
        ["chmod", "600", "/etc/gshadow"],
    ]

    for cmd in commands:
        run_command(cmd)

    print("[OK] Permissions hardened")


# =========================
# 🚫 HARDENING DE ROOT / SUDO
# =========================

def harden_sudo():
    print("[INFO] Hardening sudo configuration...")

    run_command([
        "bash", "-c",
        "echo 'Defaults use_pty' >> /etc/sudoers"
    ])

    run_command([
        "bash", "-c",
        "echo 'Defaults logfile=\"/var/log/sudo.log\"' >> /etc/sudoers"
    ])

    print("[OK] Sudo hardened")


# =========================
# 🚀 EXECUÇÃO COMPLETA
# =========================

def harden_system_advanced():
    disable_unnecessary_services()
    blacklist_kernel_modules()
    fix_permissions()
    harden_sudo()
