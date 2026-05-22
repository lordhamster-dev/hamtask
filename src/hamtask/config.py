from __future__ import annotations

import subprocess
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
    "recur",
    "priority",
    "urgency",
]
DEFAULT_LABELS = ["ID", "Project", "Description", "Tags", "Due", "Scheduled", "Recur", "Pri", "Urg"]
DEFAULT_SORT = "urgency-"
TASKRC_PATHS = [Path.home() / ".taskrc", Path.home() / ".config" / "task" / "taskrc"]


@dataclass(frozen=True)
class ReportConfig:
    name: str
    filter: str
    columns: list[str]
    labels: list[str]
    sort: str


@dataclass(frozen=True)
class HamtaskConfig:
    taskrc_path: Path
    settings: dict[str, str]
    report: ReportConfig

    @property
    def default_filter(self) -> str:
        return self.report.filter

    @property
    def columns(self) -> list[str]:
        return self.report.columns

    @property
    def labels(self) -> list[str]:
        return self.report.labels

    @property
    def sort(self) -> str:
        return self.report.sort


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


def task_show_setting(key: str) -> str | None:
    result = subprocess.run(
        ["task", "show", key],
        shell=False,
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )
    if result.returncode != 0:
        return None
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if stripped.startswith(key):
            return stripped.removeprefix(key).strip() or None
    return None


def report_setting(settings: dict[str, str], key: str, *, use_task_show: bool) -> str | None:
    value = settings.get(key)
    if value or not use_task_show:
        return value
    return task_show_setting(key)


def load_report(settings: dict[str, str], name: str) -> ReportConfig:
    prefix = f"report.{name}."
    use_task_show = name != "next"
    report_filter = (
        report_setting(
            settings,
            f"{prefix}filter",
            use_task_show=use_task_show,
        )
        or DEFAULT_FILTER
    )
    columns = (
        parse_csv_setting(report_setting(settings, f"{prefix}columns", use_task_show=use_task_show))
        or DEFAULT_COLUMNS
    )
    labels = (
        parse_csv_setting(report_setting(settings, f"{prefix}labels", use_task_show=use_task_show))
        or DEFAULT_LABELS
    )
    sort = report_setting(settings, f"{prefix}sort", use_task_show=use_task_show) or DEFAULT_SORT
    if len(labels) != len(columns):
        labels = columns
    return ReportConfig(name=name, filter=report_filter, columns=columns, labels=labels, sort=sort)


def load_config(path: str | Path | None = None, report: str = "next") -> HamtaskConfig:
    taskrc_path = Path(path).expanduser() if path else default_taskrc_path()
    settings = read_taskrc(taskrc_path)
    return HamtaskConfig(
        taskrc_path=taskrc_path,
        settings=settings,
        report=load_report(settings, report),
    )
