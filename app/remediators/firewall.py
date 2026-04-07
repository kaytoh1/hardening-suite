from app.utils.shell import run_command


def setup_ufw() -> None:
    print("[INFO] Installing UFW...")
    run_command(["apt", "update"], check=True)
    run_command(["apt", "install", "-y", "ufw"], check=True)

    print("[INFO] Configuring firewall rules...")

    # Reset
    run_command(["ufw", "--force", "reset"], check=True)

    # Default policies
    run_command(["ufw", "default", "deny", "incoming"], check=True)
    run_command(["ufw", "default", "allow", "outgoing"], check=True)

    # Allow SSH
    run_command(["ufw", "allow", "ssh"], check=True)

    print("[INFO] Enabling firewall...")
    run_command(["ufw", "--force", "enable"], check=True)

    print("[OK] UFW firewall configured")
