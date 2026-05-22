from __future__ import annotations

from collections.abc import Callable

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.screen import ModalScreen
from textual.widgets import DataTable, Footer, Header, Input, Label, Static

from hamtask.client import TaskwarriorClient, TaskwarriorError
from hamtask.config import HamtaskConfig, load_config
from hamtask.models import Task
from hamtask.parsing import split_task_args
from hamtask.sorting import sort_tasks


class PromptScreen(ModalScreen[str | None]):
    def __init__(self, prompt: str, initial: str = "") -> None:
        super().__init__()
        self.prompt = prompt
        self.initial = initial

    def compose(self) -> ComposeResult:
        with Container(id="prompt-dialog"):
            yield Label(self.prompt)
            yield Input(value=self.initial, id="prompt-input")

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    @on(Input.Submitted)
    def submit(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def key_escape(self) -> None:
        self.dismiss(None)


class ConfirmScreen(ModalScreen[bool]):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        with Container(id="confirm-dialog"):
            yield Label(self.message)
            yield Label("Press y to confirm, Esc/n to cancel")

    def key_y(self) -> None:
        self.dismiss(True)

    def key_n(self) -> None:
        self.dismiss(False)

    def key_escape(self) -> None:
        self.dismiss(False)


class HelpScreen(ModalScreen[None]):
    BINDINGS = [Binding("escape,q,?", "close", "Close")]

    def compose(self) -> ComposeResult:
        yield Static(
            "\n".join(
                [
                    "hamtask shortcuts",
                    "",
                    "j / Down       move down",
                    "k / Up         move up",
                    "g              go to top",
                    "G              go to bottom",
                    "r              refresh",
                    "q              quit",
                    "Enter          toggle bottom details",
                    "/              apply Taskwarrior filter",
                    ":              command mode",
                    "a              task add ...",
                    "m              task <uuid> modify ...",
                    "e              task <uuid> edit",
                    "A              task <uuid> annotate ...",
                    "d              task <uuid> done",
                    "u              task undo",
                    "x              delete with confirmation",
                    "?              show this help",
                    "",
                    "Command mode:",
                    ":q, :quit, :r, :refresh, :f <filter>, :filter <filter>",
                    ":add <args>, :mod <args>, :modify <args>, :done, :delete",
                    ":annotate <text>",
                ]
            ),
            id="help-dialog",
        )

    def action_close(self) -> None:
        self.dismiss(None)


class HamtaskApp(App[None]):
    CSS = """
    #status { height: 1; padding: 0 1; }
    DataTable { height: 1fr; }
    #prompt-dialog, #confirm-dialog {
        width: 80%; height: auto; margin: 2 4; padding: 1 2;
        background: $surface; border: thick $primary;
    }
    #detail {
        height: 12; padding: 1 2;
        background: $surface;
        border-top: solid $primary;
    }
    #detail.hidden { display: none; }
    #help-dialog {
        width: 80%; height: auto; margin: 2 4; padding: 1 2;
        background: $surface; border: thick $primary;
    }
    """
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j,down", "cursor_down", "Down"),
        Binding("k,up", "cursor_up", "Up"),
        Binding("g", "top", "Top"),
        Binding("G", "bottom", "Bottom"),
        Binding("r", "refresh", "Refresh"),
        Binding("enter", "toggle_detail", "Detail"),
        Binding("/", "filter", "Filter"),
        Binding(":", "command", "Command"),
        Binding("a", "add", "Add"),
        Binding("m", "modify", "Modify"),
        Binding("e", "edit", "Edit"),
        Binding("A", "annotate", "Annotate"),
        Binding("d", "done", "Done"),
        Binding("u", "undo", "Undo"),
        Binding("x", "delete", "Delete"),
        Binding("?", "help", "Help"),
    ]

    def __init__(
        self,
        config: HamtaskConfig | None = None,
        client: TaskwarriorClient | None = None,
    ) -> None:
        super().__init__()
        self.config = config or load_config()
        self.client = client or TaskwarriorClient()
        self.current_filter = self.config.default_filter
        self.tasks: list[Task] = []
        self.detail_visible = True

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Static(id="status")
        yield DataTable(id="tasks")
        yield Static(id="detail")
        yield Footer()

    def on_mount(self) -> None:
        table = self.table
        for label in self.config.labels:
            table.add_column(label)
        table.cursor_type = "row"
        table.focus()
        self.refresh_tasks()

    @property
    def table(self) -> DataTable:
        return self.query_one(DataTable)

    def selected_task(self) -> Task | None:
        row = self.table.cursor_row
        if 0 <= row < len(self.tasks):
            return self.tasks[row]
        return None

    def refresh_tasks(self) -> None:
        try:
            tasks = self.client.export(split_task_args(self.current_filter))
            self.tasks = sort_tasks(tasks, self.config.sort)
        except (TaskwarriorError, ValueError) as exc:
            self.notify(str(exc), severity="error")
            self.tasks = []
        self.render_table()

    def render_table(self) -> None:
        status = self.query_one("#status", Static)
        status.update(f"filter: {self.current_filter}    count: {len(self.tasks)}")
        table = self.table
        table.clear()
        for task in self.tasks:
            table.add_row(*(self.format_value(task, column) for column in self.config.columns))
        self.update_detail()

    def format_value(self, task: Task, column: str) -> str:
        value = getattr(task, column, task.raw.get(column, ""))
        if value is None:
            return ""
        if isinstance(value, list):
            return " ".join(str(item) for item in value)
        if isinstance(value, float):
            return f"{value:.1f}"
        return str(value)

    def action_cursor_down(self) -> None:
        self.table.action_cursor_down()

    def action_cursor_up(self) -> None:
        self.table.action_cursor_up()

    def action_top(self) -> None:
        self.table.move_cursor(row=0)

    def action_bottom(self) -> None:
        self.table.move_cursor(row=max(len(self.tasks) - 1, 0))

    def action_refresh(self) -> None:
        self.refresh_tasks()

    def action_toggle_detail(self) -> None:
        self.detail_visible = not self.detail_visible
        self.update_detail()

    @on(DataTable.RowSelected)
    def toggle_selected_detail(self) -> None:
        self.action_toggle_detail()

    @on(DataTable.RowHighlighted)
    def update_highlighted_detail(self) -> None:
        if self.detail_visible:
            self.update_detail()

    def update_detail(self) -> None:
        detail = self.query_one("#detail", Static)
        detail.set_class(not self.detail_visible, "hidden")
        if not self.detail_visible:
            return
        task = self.selected_task()
        if not task:
            detail.update("No task selected")
            return
        detail.update(self.format_detail(task))

    def format_detail(self, task: Task) -> str:
        urgency = task.urgency if task.urgency is not None else ""
        lines = [
            f"Task {task.id or ''}: {task.description}",
            f"Project: {task.project or ''}    Tags: {' '.join(task.tags)}",
            f"Priority: {task.priority or ''}    Due: {task.due or ''}",
            f"Scheduled: {task.scheduled or ''}",
            f"Status: {task.status or ''}    Urgency: {urgency}",
            f"UUID: {task.uuid}",
            "Annotations:",
        ]
        if task.annotations:
            lines.extend(f"- {a.entry or ''} {a.description}" for a in task.annotations)
        else:
            lines.append("  none")
        return "\n".join(lines)

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def prompt(self, label: str, callback: Callable[[str], None], initial: str = "") -> None:
        def done(value: str | None) -> None:
            if value:
                callback(value)

        self.push_screen(PromptScreen(label, initial), done)

    def run_and_refresh(self, action: Callable[[], None]) -> None:
        try:
            action()
            self.refresh_tasks()
        except TaskwarriorError as exc:
            self.notify(str(exc), severity="error")

    def action_filter(self) -> None:
        self.prompt("filter:", self.apply_filter, self.current_filter)

    def apply_filter(self, raw_filter: str) -> None:
        self.current_filter = raw_filter
        self.refresh_tasks()

    def action_add(self) -> None:
        self.prompt("task add", lambda raw: self.run_and_refresh(lambda: self.client.add(raw)))

    def action_modify(self) -> None:
        if task := self.selected_task():
            self.prompt(
                f"task {task.uuid} modify",
                lambda raw: self.run_and_refresh(lambda: self.client.modify(task.uuid, raw)),
            )

    def action_edit(self) -> None:
        if not (task := self.selected_task()):
            return
        try:
            with self.suspend():
                self.client.edit(task.uuid)
            self.refresh_tasks()
        except TaskwarriorError as exc:
            self.notify(str(exc), severity="error")

    def action_annotate(self) -> None:
        if task := self.selected_task():
            self.prompt(
                f"task {task.uuid} annotate",
                lambda text: self.run_and_refresh(lambda: self.client.annotate(task.uuid, text)),
            )

    def action_done(self) -> None:
        if task := self.selected_task():
            self.run_and_refresh(lambda: self.client.done(task.uuid))

    def action_undo(self) -> None:
        def confirmed(ok: bool) -> None:
            if ok:
                self.run_and_refresh(self.client.undo)

        self.push_screen(ConfirmScreen("Undo last Taskwarrior operation?"), confirmed)

    def action_delete(self) -> None:
        task = self.selected_task()
        if not task:
            return

        def confirmed(ok: bool) -> None:
            if ok:
                self.run_and_refresh(lambda: self.client.delete(task.uuid))

        self.push_screen(ConfirmScreen(f"Delete task {task.id or task.uuid}?"), confirmed)

    def action_command(self) -> None:
        self.prompt(":", self.execute_command)

    def execute_command(self, command: str) -> None:
        name, _, rest = command.partition(" ")
        match name:
            case "q" | "quit":
                self.exit()
            case "r" | "refresh":
                self.refresh_tasks()
            case "f" | "filter":
                self.apply_filter(rest)
            case "add":
                self.run_and_refresh(lambda: self.client.add(rest))
            case "mod" | "modify":
                if task := self.selected_task():
                    self.run_and_refresh(lambda: self.client.modify(task.uuid, rest))
            case "done":
                self.action_done()
            case "undo":
                self.action_undo()
            case "delete":
                self.action_delete()
            case "annotate":
                if task := self.selected_task():
                    self.run_and_refresh(lambda: self.client.annotate(task.uuid, rest))
            case _:
                self.notify(f"Unknown command: {name}", severity="warning")
