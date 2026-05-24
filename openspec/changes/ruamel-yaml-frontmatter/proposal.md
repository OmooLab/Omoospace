## Why

项目目前依赖 `python-frontmatter`（其内部依赖 `pyyaml`）来解析 Markdown 文件的 YAML frontmatter。然而 `pyyaml` 和 `ruamel-yaml` 功能重叠，而项目中已使用 `ruamel-yaml`。通过基于 `ruamel-yaml` 自己实现 frontmatter 读取，可以移除 `python-frontmatter` 及 `pyyaml` 依赖，简化依赖结构。

## What Changes

- 新增 `omoospace.utils.frontmatter` 模块，实现基于 `ruamel-yaml` 的 frontmatter 读取
- 修改 `src/omoospace/common.py`，将 `import frontmatter` 替换为使用新的 frontmatter 工具模块
- 从 `pyproject.toml` 中移除 `python-frontmatter` 依赖

## Capabilities

### New Capabilities

- `frontmatter-parser`: 基于 `ruamel-yaml` 实现 Markdown 文件的 YAML frontmatter 解析，提取 metadata 和 content

### Modified Capabilities

- `profile-management`: 修改 `Profile._read_profile` 和 `Profile._write_profile` 的实现方式，不再依赖 `python-frontmatter`

## Impact

- 移除 `python-frontmatter` 依赖，减少一层依赖链
- `src/omoospace/common.py` 中 Markdown profile 的读写逻辑需要调整
- 需要处理边界情况：文件无 frontmatter、frontmatter 格式错误等