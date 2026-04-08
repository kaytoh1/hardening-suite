"""Validação estrita de uma linha de chave pública OpenSSH (sem opções)."""

from __future__ import annotations

import base64
import re

from app.core.exceptions import ValidationError

_MAX_LINE_LEN = 16_384

_ALLOWED_TYPES = frozenset(
    {
        "ssh-rsa",
        "ssh-dss",
        "ssh-ed25519",
        "ecdsa-sha2-nistp256",
        "ecdsa-sha2-nistp384",
        "ecdsa-sha2-nistp521",
        # Certificados de usuário/host OpenSSH (CA interna)
        "ssh-rsa-cert-v01@openssh.com",
        "ssh-dss-cert-v01@openssh.com",
        "ssh-ed25519-cert-v01@openssh.com",
        "ecdsa-sha2-nistp256-cert-v01@openssh.com",
        "ecdsa-sha2-nistp384-cert-v01@openssh.com",
        "ecdsa-sha2-nistp521-cert-v01@openssh.com",
    }
)

# Blob em Base64 (OpenSSH); comentário opcional: apenas texto imprimível sem controle.
_B64 = re.compile(r"^[A-Za-z0-9+/]+=*$")


def validate_ssh_public_key_line(raw: str) -> str:
    """
    Aceita apenas linhas no formato: <tipo> <blob_base64> [comentário]
    Rejeita prefixos de opções (command=, from=, etc.).
    """
    key = raw.strip()
    if not key:
        raise ValidationError("Chave pública vazia.")
    if len(key) > _MAX_LINE_LEN:
        raise ValidationError("Chave pública excede o tamanho máximo permitido.")
    if any(ch in key for ch in "\n\r\t\x00"):
        raise ValidationError("A chave deve ser uma única linha, sem quebras ou tabs.")

    if key.startswith(("no-", "cert-authority", "restrict", "command=", "tunnel=", "from=")):
        raise ValidationError("Linhas com opções OpenSSH não são permitidas; cole apenas a chave pública.")

    if "," in key.split()[0] if key.split() else False:
        raise ValidationError("Formato inválido: opções antes do tipo de chave não são permitidas.")

    parts = key.split()
    if len(parts) < 2:
        raise ValidationError("Formato inválido: esperado '<tipo> <dados_base64> [comentário]'.")

    key_type, blob = parts[0], parts[1]
    if key_type not in _ALLOWED_TYPES:
        raise ValidationError(f"Tipo de chave não suportado: {key_type}")

    if not _B64.fullmatch(blob):
        raise ValidationError("Dados da chave (Base64) inválidos.")

    try:
        decoded = base64.b64decode(blob, validate=True)
    except Exception as exc:  # noqa: BLE001 - entrada do usuário
        raise ValidationError("Falha ao decodificar Base64 da chave pública.") from exc

    if len(decoded) < 32:
        raise ValidationError("Chave pública muito curta ou corrompida.")

    if len(parts) > 2:
        comment = " ".join(parts[2:])
        if len(comment) > 512:
            raise ValidationError("Comentário da chave muito longo.")
        if not comment.isprintable():
            raise ValidationError("Comentário contém caracteres não permitidos.")

    return f"{key_type} {blob}" + (f" {' '.join(parts[2:])}" if len(parts) > 2 else "")
