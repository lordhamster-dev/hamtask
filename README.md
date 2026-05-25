# hamtask

`hamtask` is a vim-style Taskwarrior TUI built with Python and Textual.

## Goals

- List-first, keyboard-only interface.
- Use Taskwarrior's native filters and raw command arguments.
- Read `report.next.filter`, `report.next.columns`, `report.next.labels`, and `report.next.sort` from `~/.taskrc` or `~/.config/task/taskrc`.
- Mutate tasks by invoking the `task` command, never by editing Taskwarrior data files directly.

## Requirements

- Python 3.11+
- Taskwarrior's `task` command must be installed and configured

## Install from PyPI

```bash
uv tool install hamtask
```

Then run:

```bash
hamtask
```

Open a specific Taskwarrior report from your taskrc:

```bash
hamtask completed
hamtask waiting
```

Update an installed PyPI version with:

```bash
uv tool upgrade hamtask
```

## Run during development

```bash
uv run hamtask
```

## Local installation

Install the current checkout as a `uv tool`:

```bash
uv tool install .
```

Then run:

```bash
hamtask
```

If your shell cannot find `hamtask`, run:

```bash
uv tool update-shell
```

Then restart your terminal or reload your shell config.

## Update local installation

After changing the local source code, reinstall with:

```bash
uv tool install . --force
```

## Uninstall

```bash
uv tool uninstall hamtask
```

## Key bindings

- `j` / `k`: move down/up
- `g`: go to top
- `G`: go to bottom
- `r`: refresh
- `q`: quit
- `enter`: toggle bottom task details
- `/`: search current list
- `f`: apply Taskwarrior filter
- `:`: command mode
- `a`: `task add ...`
- `m`: `task <uuid> modify ...`
- `e`: `task <uuid> edit`
- `A`: `task <uuid> annotate ...`
- `space`: select/unselect task
- `d`: done selected tasks, or current task when nothing is selected
- `s`: start/stop selected tasks, or current task when nothing is selected
- `u`: `task undo`
- `x`: delete with confirmation
- `?`: show all shortcuts

## Reports

By default, hamtask loads the `next` report from your taskrc:

```text
report.next.filter
report.next.columns
report.next.labels
report.next.sort
```

You can start with another report:

```bash
hamtask waiting
```

Or switch reports at runtime:

```text
:report waiting
```

hamtask will read the matching report keys, such as:

```text
report.waiting.filter
report.waiting.columns
report.waiting.labels
report.waiting.sort
```

## Command mode

Supported commands:

```text
:q
:quit
:r
:refresh
:f <filter>
:filter <filter>
:report <name>
:add <raw task args>
:mod <raw task args>
:modify <raw task args>
:done
:undo
:delete
:annotate <text>
```
