# For Code Contributors

## Installation

Install Poetry  
[Poetry offical page about installation](https://python-poetry.org/docs/#installation)

Install Dependencies

```bash
poetry install
```

## Other Commands

Test Coverage

```bash
poetry run pytest --cov=omoospace tests/
```

Server Mkdocs
```bash
poetry run mkdocs serve
```

Deploy Github Pages

```bash
poetry run mike deploy --push --update-aliases 0.1.x latest
```

Publish to Pypi

```bash
poetry build
poetry publish
```