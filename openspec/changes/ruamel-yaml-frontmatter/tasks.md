## 1. Setup

- [x] 1.1 Create `src/omoospace/utils/frontmatter.py` module with `parse` and `dump` functions
- [x] 1.2 Add `frontmatter` to `src/omoospace/utils/__init__.py` exports

## 2. Core Implementation

- [x] 2.1 Implement `parse(content: str) -> tuple[dict, str]` using regex and ruamel-yaml
- [x] 2.2 Implement `dump(metadata: dict, content: str = "") -> str` for serialization
- [x] 2.3 Handle edge cases: no frontmatter, empty frontmatter, YAML parse errors

## 3. Integrate with Profile

- [x] 3.1 Update `src/omoospace/common.py` to import from `omoospace.utils.frontmatter`
- [x] 3.2 Replace `frontmatter.load()` calls with custom `parse()` function
- [x] 3.3 Replace `frontmatter.dumps()` calls with custom `dump()` function
- [x] 3.4 Remove `import frontmatter` from common.py

## 4. Cleanup Dependencies

- [x] 4.1 Remove `python-frontmatter` from `pyproject.toml` dependencies
- [x] 4.2 Run `uv lock` to update lock file
- [x] 4.3 Verify `uv sync` works without python-frontmatter