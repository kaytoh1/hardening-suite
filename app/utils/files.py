from pathlib import Path
import shutil
from datetime import datetime

from app.core.constants import BACKUP_DIR, REPORTS_DIR, RUNS_DIR


def ensure_state_dirs() -> None:
    for directory in (BACKUP_DIR, REPORTS_DIR, RUNS_DIR):
        directory.mkdir(parents=True, exist_ok=True)


def write_text_file(path: Path, content: str, encoding: str = "utf-8") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding=encoding)


def backup_file(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{path.name}.{timestamp}.bak"
    backup_path = BACKUP_DIR / backup_name

    shutil.copy2(path, backup_path)

    return backup_path
