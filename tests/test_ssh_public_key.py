from __future__ import annotations

import base64
import os
import unittest

from app.core.exceptions import ValidationError
from app.validators.ssh_public_key import validate_ssh_public_key_line


class TestSshPublicKey(unittest.TestCase):
    def _valid_line(self, key_type: str) -> str:
        payload = os.urandom(48)
        blob = base64.b64encode(payload).decode("ascii")
        return f"{key_type} {blob}"

    def test_accepts_ed25519_and_normalizes_whitespace(self) -> None:
        line = self._valid_line("ssh-ed25519")
        normalized = validate_ssh_public_key_line(f"  {line}  ")
        self.assertEqual(normalized, line)

    def test_accepts_openssh_cert_type(self) -> None:
        line = self._valid_line("ssh-ed25519-cert-v01@openssh.com")
        self.assertEqual(validate_ssh_public_key_line(line), line)

    def test_rejects_options_prefix(self) -> None:
        line = self._valid_line("ssh-ed25519")
        with self.assertRaises(ValidationError):
            validate_ssh_public_key_line(f"command=/bin/sh {line}")

    def test_rejects_multiline(self) -> None:
        line = self._valid_line("ssh-ed25519")
        with self.assertRaises(ValidationError):
            validate_ssh_public_key_line(line + "\n" + line)

    def test_rejects_short_blob(self) -> None:
        short = base64.b64encode(b"x" * 8).decode("ascii")
        with self.assertRaises(ValidationError):
            validate_ssh_public_key_line(f"ssh-ed25519 {short}")

    def test_rejects_unknown_type(self) -> None:
        line = self._valid_line("ssh-foo")
        with self.assertRaises(ValidationError):
            validate_ssh_public_key_line(line)

    def test_optional_comment_printable(self) -> None:
        line = self._valid_line("ssh-rsa") + " user@host"
        self.assertEqual(validate_ssh_public_key_line(line), line)