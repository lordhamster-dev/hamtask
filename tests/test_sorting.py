from hamtask.models import Task
from hamtask.sorting import parse_sort_setting, sort_tasks


def test_parse_sort_setting():
    assert parse_sort_setting("due+,urgency-") == [("due", False), ("urgency", True)]


def test_sort_tasks_by_urgency_descending():
    tasks = [
        Task(uuid="low", description="Low", urgency=1.0),
        Task(uuid="high", description="High", urgency=9.0),
    ]

    sorted_tasks = sort_tasks(tasks, "urgency-")

    assert [task.uuid for task in sorted_tasks] == ["high", "low"]


def test_sort_tasks_by_due_then_urgency():
    tasks = [
        Task(uuid="later", description="Later", due="20260523T000000Z", urgency=9.0),
        Task(uuid="soon-low", description="Soon low", due="20260522T000000Z", urgency=1.0),
        Task(uuid="soon-high", description="Soon high", due="20260522T000000Z", urgency=8.0),
    ]

    sorted_tasks = sort_tasks(tasks, "due+,urgency-")

    assert [task.uuid for task in sorted_tasks] == ["soon-high", "soon-low", "later"]
