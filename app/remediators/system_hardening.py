from app.utils.shell import run_command


def update_system() -> None:
    print("[INFO] Updating system packages...")

    run_command(["apt", "update"], check=True)
    run_command(["apt", "upgrade", "-y"], check=True)

    print("[OK] System updated")


def install_security_tools() -> None:
    print("[INFO] Installing security tools...")

    tools = [
        "unattended-upgrades",
        "apt-listchanges",
        "needrestart"
    ]

    run_command(["apt", "install", "-y"] + tools, check=True)

    print("[OK] Security tools installed")


def enable_auto_updates() -> None:
    print("[INFO] Enabling automatic updates...")

    run_command(["dpkg-reconfigure", "-f", "noninteractive", "unattended-upgrades"], check=True)

    print("[OK] Automatic updates enabled")


def cleanup_system() -> None:
    print("[INFO] Cleaning system...")

    run_command(["apt", "autoremove", "-y"], check=True)
    run_command(["apt", "autoclean"], check=True)

    print("[OK] System cleaned")


def harden_system() -> None:
    update_system()
    install_security_tools()
    enable_auto_updates()
    cleanup_system()
