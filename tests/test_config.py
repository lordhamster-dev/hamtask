from hamtask.config import (
    DEFAULT_COLUMNS,
    DEFAULT_FILTER,
    DEFAULT_SORT,
    default_taskrc_path,
    load_config,
    read_taskrc,
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


def test_load_config_defaults_when_taskrc_missing(tmp_path):
    config = load_config(tmp_path / "missing")

    assert config.default_filter == DEFAULT_FILTER
    assert config.columns == DEFAULT_COLUMNS
    assert config.sort == DEFAULT_SORT


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
