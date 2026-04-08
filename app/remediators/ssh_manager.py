import os
from pathlib import Path

from app.core.exceptions import RollbackError, ValidationError
from app.utils.files import restore_file_from_backup
from app.utils.shell import run_command
from app.utils.user_context import get_effective_user
from app.validators.ssh_public_key import validate_ssh_public_key_line
from app.validators.ssh_validator import test_ssh_connection

SSHD_CONFIG_PATH = Path("/etc/ssh/sshd_config")


def read_sshd_config() -> list[str]:
    return SSHD_CONFIG_PATH.read_text(encoding="utf-8").splitlines()


def write_sshd_config(lines: list[str]) -> None:
    SSHD_CONFIG_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _global_section_and_match_tail(lines: list[str]) -> tuple[list[str], list[str]]:
    """
    Separa a seção global (antes do primeiro bloco `Match`) do restante.

    No OpenSSH, diretivas após um `Match` pertencem a esse bloco até o próximo
    `Match`. Não alteramos linhas dentro de blocos Match para evitar surpresas.
    """
    for i, raw in enumerate(lines):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.lower().startswith("match "):
            return lines[:i], lines[i:]
    return lines, []


def _set_config_value_in_global_lines(lines: list[str], key: str, value: str) -> list[str]:
    new_lines: list[str] = []
    found = False
    key_l = key.lower()

    for line in lines:
        stripped = line.strip()
        if stripped.startswith("#"):
            new_lines.append(line)
            continue
        if stripped.lower().startswith(key_l):
            new_lines.append(f"{key} {value}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        new_lines.append(f"{key} {value}")

    return new_lines


def set_config_value(lines: list[str], key: str, value: str) -> list[str]:
    """Define diretiva na seção global (antes do primeiro `Match`), sem tocar em blocos Match."""
    head, tail = _global_section_and_match_tail(lines)
    new_head = _set_config_value_in_global_lines(head, key, value)
    return new_head + tail


def restart_sshd_service() -> None:
    """Reinicia SSH via systemd (ssh ou sshd) ou fallback para service(8)."""
    for unit in ("ssh", "sshd"):
        exists = run_command(["systemctl", "cat", unit], check=False, timeout=30)
        if exists.returncode == 0:
            run_command(["systemctl", "restart", unit], check=True)
            return
    run_command(["service", "ssh", "restart"], check=True)


def get_sshd_listen_ports() -> list[int]:
    """Portas TCP declaradas em sshd_config (padrão 22 se nenhuma explícita)."""
    if not SSHD_CONFIG_PATH.is_file():
        return [22]
    ports: list[int] = []
    for line in read_sshd_config():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not stripped.lower().startswith("port"):
            continue
        parts = stripped.split()
        if len(parts) < 2:
            continue
        try:
            p = int(parts[1])
        except ValueError:
            continue
        if 1 <= p <= 65535 and p not in ports:
            ports.append(p)
    return ports if ports else [22]


def add_ssh_key(public_key: str) -> None:
    normalized = validate_ssh_public_key_line(public_key)
    user, home = get_effective_user()

    ssh_dir = (home / ".ssh").resolve()
    authorized_keys = (ssh_dir / "authorized_keys").resolve()

    try:
        home_resolved = home.resolve()
    except OSError as exc:
        raise ValidationError("Não foi possível resolver o diretório home do usuário.") from exc

    if not str(ssh_dir).startswith(str(home_resolved)):
        raise ValidationError("Caminho .ssh inválido (possível path traversal).")

    ssh_dir.mkdir(parents=True, exist_ok=True)

    if authorized_keys.exists():
        existing = authorized_keys.read_text(encoding="utf-8")
        if normalized in existing.splitlines():
            return

    with authorized_keys.open("a", encoding="utf-8") as f:
        f.write(normalized + "\n")

    os.chmod(ssh_dir, 0o700)
    os.chmod(authorized_keys, 0o600)

    import pwd  # noqa: PLC0415 — Unix apenas; import tardio para testes em Windows.

    try:
        pw = pwd.getpwnam(user)
        os.chown(ssh_dir, pw.pw_uid, pw.pw_gid)
        os.chown(authorized_keys, pw.pw_uid, pw.pw_gid)
    except OSError as exc:
        raise RollbackError(
            "Falha ao ajustar dono/permissões de ~/.ssh; corrija manualmente antes de desabilitar senha."
        ) from exc


def restart_ssh_safe(sshd_config_backup: Path | None = None) -> None:
    print("[INFO] Testando conexão SSH antes do reinício...")

    if not test_ssh_connection():
        raise RuntimeError(
            "Teste SSH falhou antes do reinício. Use ssh-agent ou chave sem passphrase, "
            "e confira se a chave privada corresponde à pública adicionada."
        )

    print("[OK] Teste SSH antes do reinício bem-sucedido")

    print("[INFO] Reiniciando serviço SSH...")
    restart_sshd_service()

    print("[INFO] Testando SSH após reinício...")

    if test_ssh_connection():
        print("[OK] SSH reiniciado e conexão verificada")
        return

    if sshd_config_backup is not None and sshd_config_backup.is_file():
        print("[CRITICAL] Conexão falhou após reinício; restaurando sshd_config do backup...")
        try:
            restore_file_from_backup(sshd_config_backup, SSHD_CONFIG_PATH)
            restart_sshd_service()
        except OSError as exc:
            raise RollbackError(
                "Falha ao restaurar sshd_config após lockout. Restaure manualmente o backup em state/backups."
            ) from exc

        if test_ssh_connection():
            raise RollbackError(
                "Configuração SSH foi revertida para o backup porque o acesso falhou após o reinício. "
                "Revise sshd_config e tente novamente."
            )

    raise RuntimeError(
        "SSH inacessível após reinício e rollback não resolveu. Verifique console, backup e rede."
    )
