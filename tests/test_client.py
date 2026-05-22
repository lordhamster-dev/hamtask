import subprocess

from hamtask.client import TaskwarriorClient


def test_export_invokes_task_with_json_array_and_filter(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, '[{"uuid":"abc","description":"Test"}]', "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    tasks = TaskwarriorClient().export(["status:pending"])

    assert tasks[0].uuid == "abc"
    assert calls[0][0] == ["task", "rc.json.array=on", "status:pending", "export"]
    assert calls[0][1]["shell"] is False


def test_modify_uses_uuid_and_shlex(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    TaskwarriorClient().modify("abc", 'project:work "new description"')

    assert calls[0] == ["task", "abc", "modify", "project:work", "new description"]


def test_edit_uses_uuid_and_interactive_subprocess(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        calls.append((args, kwargs))
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    TaskwarriorClient().edit("abc")

    assert calls[0][0] == ["task", "abc", "edit"]
    assert calls[0][1]["shell"] is False
    assert calls[0][1]["check"] is False


def test_undo_invokes_task_undo(monkeypatch):
    calls = []

    def fake_run(args, **kwargs):
        calls.append(args)
        return subprocess.CompletedProcess(args, 0, "", "")

    monkeypatch.setattr(subprocess, "run", fake_run)

    TaskwarriorClient().undo()

    assert calls[0] == ["task", "undo", "rc.confirmation=no"]
