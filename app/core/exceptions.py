class HardeningError(Exception):
    """Base exception for the hardening suite."""


class CommandExecutionError(HardeningError):
    """Raised when a system command fails unexpectedly."""


class ValidationError(HardeningError):
    """Raised when validation fails."""


class UnsupportedSystemError(HardeningError):
    """Raised when the current system is not supported."""


class BackupError(HardeningError):
    """Raised when backup operations fail."""


class RollbackError(HardeningError):
    """Raised when rollback operations fail."""
