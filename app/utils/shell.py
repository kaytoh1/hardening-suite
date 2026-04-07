import subprocess

from app.core.constants import DEFAULT_TIMEOUT
from app.core.exceptions import CommandExecutionError
from app.core.models import CommandResult


def run_command(
    command: list[str],
    timeout: int = DEFAULT_TIMEOUT,
    check: bool = False,
) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise CommandExecutionError(
            f"Command timed out after {timeout}s: {' '.join(command)}"
        ) from exc
    except OSError as exc:
        raise CommandExecutionError(
            f"Failed to execute command: {' '.join(command)}"
        ) from exc

    result = CommandResult(
        command=command,
        returncode=completed.returncode,
        stdout=completed.stdout.strip(),
        stderr=completed.stderr.strip(),
    )

    if check and completed.returncode != 0:
        raise CommandExecutionError(
            f"Command failed ({completed.returncode}): {' '.join(command)}\n"
            f"stderr: {result.stderr}"
        )

    return result
