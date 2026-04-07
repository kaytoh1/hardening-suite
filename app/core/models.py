from typing import Literal

from pydantic import BaseModel, Field


class CommandResult(BaseModel):
    command: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""


class OSInfo(BaseModel):
    distro: str
    version: str
    pretty_name: str
    kernel: str


class ExecutionContext(BaseModel):
    dry_run: bool = False
    verbose: bool = False
    run_id: str


class CheckResult(BaseModel):
    name: str
    status: Literal["pass", "fail", "skip", "error"]
    message: str
    details: dict[str, str] = Field(default_factory=dict)
