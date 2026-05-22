import subprocess

from hamtask.config import (
    DEFAULT_COLUMNS,
    DEFAULT_FILTER,
    DEFAULT_SORT,
    default_taskrc_path,
    load_config,
    read_taskrc,
    task_show_setting,
)


def test_read_taskrc_parses_key_values(tmp_path):
    taskrc = tmp_path / "taskrc"
    taskrc.write_text(
        "# comment\nreport.next.filter=status:pending +next\nfoo = bar\n",
        encoding="utf-8",
    )

    assert read_taskrc(taskrc) == {"report.next.filter": "status:pending +next", "foo": "bar"}


def test_load_config_uses_taskrc_report_next(tmp_path):
    taskrc = tmp_path / "taskrc"
    taskrc.write_text(
        "report.next.filter=project:work\n"
        "report.next.columns=id,project,description\n"
        "report.next.labels=ID,Project,Description\n"
        "report.next.sort=due+,urgency-\n",
        encoding="utf-8",
    )

    config = load_config(taskrc)

    assert config.default_filter == "project:work"
    assert config.columns == ["id", "project", "description"]
    assert config.labels == ["ID", "Project", "Description"]
    assert config.sort == "due+,urgency-"


def test_load_config_loads_named_report(tmp_path):
    taskrc = tmp_path / "taskrc"
    taskrc.write_text(
        "report.waiting.filter=status:waiting\n"
        "report.waiting.columns=id,description,wait\n"
        "report.waiting.labels=ID,Description,Wait\n"
        "report.waiting.sort=wait+\n",
        encoding="utf-8",
    )

    config = load_config(taskrc, report="waiting")

    assert config.report.name == "waiting"
    assert config.default_filter == "status:waiting"
    assert config.columns == ["id", "description", "wait"]
    assert config.labels == ["ID", "Description", "Wait"]
    assert config.sort == "wait+"


def test_load_config_defaults_when_taskrc_missing(monkeypatch, tmp_path):
    monkeypatch.setattr("hamtask.config.task_show_setting", lambda key: None)

    config = load_config(tmp_path / "missing")

    assert config.report.name == "next"
    assert config.default_filter == DEFAULT_FILTER
    assert config.columns == DEFAULT_COLUMNS
    assert config.sort == DEFAULT_SORT


def test_load_config_next_ignores_task_show_defaults(monkeypatch, tmp_path):
    values = {
        "report.next.filter": "+READY",
        "report.next.columns": "id,description",
        "report.next.labels": "ID,Description",
        "report.next.sort": "status+,start+,due+,project+",
    }
    monkeypatch.setattr("hamtask.config.task_show_setting", values.get)

    config = load_config(tmp_path / "missing", report="next")

    assert config.default_filter == DEFAULT_FILTER
    assert config.columns == DEFAULT_COLUMNS
    assert config.sort == DEFAULT_SORT


def test_load_config_uses_task_show_for_builtin_reports(monkeypatch, tmp_path):
    values = {
        "report.completed.filter": "status:completed -WAITING",
        "report.completed.columns": "id,end,description",
        "report.completed.labels": "ID,Completed,Description",
        "report.completed.sort": "end-",
    }
    monkeypatch.setattr("hamtask.config.task_show_setting", values.get)

    config = load_config(tmp_path / "missing", report="completed")

    assert config.default_filter == "status:completed -WAITING"
    assert config.columns == ["id", "end", "description"]
    assert config.labels == ["ID", "Completed", "Description"]
    assert config.sort == "end-"


def test_task_show_setting_parses_task_output(monkeypatch):
    def fake_run(args, **kwargs):
        return subprocess.CompletedProcess(
            args,
            0,
            "\nConfig Variable         Value\n"
            "----------------------- -------------------------\n"
            "report.completed.filter status:completed -WAITING\n",
            "",
        )

    monkeypatch.setattr(subprocess, "run", fake_run)

    assert task_show_setting("report.completed.filter") == "status:completed -WAITING"


def test_default_taskrc_path_prefers_legacy_taskrc(monkeypatch, tmp_path):
    legacy = tmp_path / ".taskrc"
    xdg = tmp_path / ".config" / "task" / "taskrc"
    xdg.parent.mkdir(parents=True)
    legacy.write_text("", encoding="utf-8")
    xdg.write_text("", encoding="utf-8")

    monkeypatch.setattr("hamtask.config.TASKRC_PATHS", [legacy, xdg])

    assert default_taskrc_path() == legacy


def test_default_taskrc_path_uses_xdg_when_legacy_missing(monkeypatch, tmp_path):
    legacy = tmp_path / ".taskrc"
    xdg = tmp_path / ".config" / "task" / "taskrc"
    xdg.parent.mkdir(parents=True)
    xdg.write_text("", encoding="utf-8")

    monkeypatch.setattr("hamtask.config.TASKRC_PATHS", [legacy, xdg])

    assert default_taskrc_path() == xdg
