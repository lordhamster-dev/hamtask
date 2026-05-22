from hamtask.parsing import format_task_datetime, parse_csv_setting, split_task_args


def test_split_task_args_preserves_quoted_text():
    assert split_task_args('"Buy milk" project:home +errand') == [
        "Buy milk",
        "project:home",
        "+errand",
    ]


def test_parse_csv_setting():
    assert parse_csv_setting("id, project, description") == ["id", "project", "description"]


def test_format_task_datetime():
    assert format_task_datetime("20260522T120304Z") == "2026-05-22 12:03:04"


def test_format_task_datetime_returns_unknown_format_unchanged():
    assert format_task_datetime("tomorrow") == "tomorrow"
