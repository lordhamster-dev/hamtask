# AGENTS.md

Guidance for coding agents working on `hamtask`.

## Project overview

`hamtask` is a vim-style Taskwarrior TUI built with Python and Textual.

## Development constraints

- Use `arrow` for datetime parsing, formatting, and timezone handling. Do not introduce new standard-library datetime parsing/formatting in application code unless an external API requires `datetime` objects.
- Use `typer` for command-line interfaces. Do not add new `argparse`-based CLI code.

## Development commands

Run checks before finishing code changes:

```bash
uv run ruff check .
uv run pytest
```

## Local run

```bash
uv run hamtask
```

## Publish to PyPI

Before publishing, verify the project:

```bash
uv run ruff check .
uv run pytest
uv build
```

This creates distribution files in `dist/`.

For a first test release, publish to TestPyPI:

```bash
uv publish --publish-url https://test.pypi.org/legacy/ --token <test-pypi-token>
```

Install from TestPyPI with PyPI as the fallback index for dependencies:

```bash
uv tool install \
  --index-url https://test.pypi.org/simple/ \
  --extra-index-url https://pypi.org/simple \
  hamtask
```

Publish to PyPI:

```bash
uv publish --token <pypi-token>
```

For later releases:

1. Bump `version` in `pyproject.toml`.
2. Run checks and build again.
3. Publish with `uv publish --token <pypi-token>`.
