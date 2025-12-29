# For Code Contributors

## Installation

Install Poetry  
[Poetry offical page about installation](https://python-poetry.org/docs/#installation)

Install Dependencies

```bash
uv sync
```

## Other Commands

Test Coverage

```bash
uv run pytest tests/
```

Server Mkdocs
```bash
uv run mkdocs serve
```

Deploy Github Pages

```bash
uv run mike deploy --push --update-aliases 0.2.x latest
```

Publish to Pypi

```bash
uv build
uv publish
```