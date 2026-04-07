import platform
from pathlib import Path

from app.core.exceptions import UnsupportedSystemError
from app.core.models import OSInfo


def get_os_info() -> OSInfo:
    os_release_path = Path("/etc/os-release")

    if not os_release_path.exists():
        raise UnsupportedSystemError("Could not find /etc/os-release")

    data: dict[str, str] = {}

    for line in os_release_path.read_text(encoding="utf-8").splitlines():
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        data[key.strip()] = value.strip().strip('"')

    distro = data.get("ID", "").lower()
    version = data.get("VERSION_ID", "")
    pretty_name = data.get("PRETTY_NAME", distro or "Unknown Linux")
    kernel = platform.release()

    if not distro:
        raise UnsupportedSystemError("Could not determine Linux distribution")

    return OSInfo(
        distro=distro,
        version=version,
        pretty_name=pretty_name,
        kernel=kernel,
    )
