from pathlib import Path

APP_NAME = "hardening-suite"

STATE_DIR = Path("state")
BACKUP_DIR = STATE_DIR / "backups"
RUNS_DIR = STATE_DIR / "runs"
REPORTS_DIR = STATE_DIR / "reports"

SUPPORTED_DISTROS = {"ubuntu", "debian"}

DEFAULT_ENCODING = "utf-8"
DEFAULT_TIMEOUT = 300
