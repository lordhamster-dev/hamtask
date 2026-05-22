from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from hamtask.parsing import parse_csv_setting

DEFAULT_FILTER = "status:pending"
DEFAULT_COLUMNS = [
    "id",
    "project",
    "description",
    "tags",
    "due",
    "scheduled",
    "priority",
    "urgency",
]
DEFAULT_LABELS = ["ID", "Project", "Description", "Tags", "Due", "Scheduled", "Pri", "Urg"]
DEFAULT_SORT = "urgency-"
TASKRC_PATHS = [Path.home() / ".taskrc", Path.home() / ".config" / "task" / "taskrc"]


@dataclass(frozen=True)
class HamtaskConfig:
    taskrc_path: Path
    settings: dict[str, str]
    default_filter: str
    columns: list[str]
    labels: list[str]
    sort: str


def default_taskrc_path() -> Path:
    for path in TASKRC_PATHS:
        if path.exists():
            return path
    return TASKRC_PATHS[0]


def read_taskrc(path: str | Path | None = None) -> dict[str, str]:
    taskrc_path = Path(path).expanduser() if path else default_taskrc_path()
    if not taskrc_path.exists():
        return {}

    settings: dict[str, str] = {}
    for raw_line in taskrc_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        settings[key.strip()] = value.strip()
    return settings


def load_config(path: str | Path | None = None) -> HamtaskConfig:
    taskrc_path = Path(path).expanduser() if path else default_taskrc_path()
    settings = read_taskrc(taskrc_path)
    default_filter = settings.get("report.next.filter", DEFAULT_FILTER) or DEFAULT_FILTER
    columns = parse_csv_setting(settings.get("report.next.columns")) or DEFAULT_COLUMNS
    labels = parse_csv_setting(settings.get("report.next.labels")) or DEFAULT_LABELS
    sort = settings.get("report.next.sort", DEFAULT_SORT) or DEFAULT_SORT
    if len(labels) != len(columns):
        labels = columns
    return HamtaskConfig(
        taskrc_path=taskrc_path,
        settings=settings,
        default_filter=default_filter,
        columns=columns,
        labels=labels,
        sort=sort,
    )
