from hamtask.parsing import parse_csv_setting, split_task_args


def test_split_task_args_preserves_quoted_text():
    assert split_task_args('"Buy milk" project:home +errand') == [
        "Buy milk",
        "project:home",
        "+errand",
    ]


def test_parse_csv_setting():
    assert parse_csv_setting("id, project, description") == ["id", "project", "description"]
