## Context

项目使用 `ruamel-yaml` 作为 YAML 解析库，同时通过 `python-frontmatter`（其内部依赖 `pyyaml`）来解析 Markdown 文件的 YAML frontmatter。`python-frontmatter` 的核心功能是：

1. 从 Markdown 文件中分离 frontmatter（`---...---` 包裹的 YAML 块）和正文
2. 使用 YAML 解析器解析 frontmatter 得到 metadata dict
3. 将 metadata 和正文组合成可序列化的对象

由于 `ruamel-yaml` 本身支持 YAML 解析，我们只需要用它替代 `pyyaml` 来实现相同的功能。

## Goals / Non-Goals

**Goals:**
- 实现基于 `ruamel-yaml` 的 Markdown frontmatter 解析
- 移除 `python-frontmatter` 和 `pyyaml` 依赖
- 保持 `Profile._read_profile` 和 `Profile._write_profile` 的行为不变

**Non-Goals:**
- 不实现完整的 `python-frontmatter` 兼容层（只需要项目中用到的功能）
- 不修改 YAML 文件的处理逻辑（继续使用现有 `yaml` 模块）
- 不改变 frontmatter 的格式规范（仍然是 `---...---` 包裹的 YAML）

## Decisions

### Decision 1: Frontmatter 模块位置

**选择**: 在 `src/omoospace/utils/frontmatter.py` 实现解析逻辑。

**原因**:
- `common.py` 中的 `Profile` 类已导入 `omoospace.utils.yaml`
- 遵循项目模块划分，工具函数放在 `utils` 包中
- frontmatter 解析是独立功能，便于后续复用

**替代方案**:
- 直接在 `common.py` 中实现（会使 `common.py` 变得更长，不推荐）
- 放在 `utils/__init__.py` 中导出（混合了不同功能）

### Decision 2: Frontmatter 解析策略

**选择**: 使用正则表达式分离 frontmatter 和正文，再用 `ruamel-yaml` 解析。

```python
import re
from io import StringIO
from ruamel.yaml import YAML

FRONTMATTER_PATTERN = re.compile(r'^---\s*\n(.*?)\n---\s*\n', re.DOTALL)

def parse(content: str) -> tuple[dict, str]:
    """Parse frontmatter from markdown content.

    Returns (metadata, content) tuple. metadata is empty dict if no frontmatter found.
    """
    match = FRONTMATTER_PATTERN.match(content)
    if not match:
        return {}, content

    yaml_content = match.group(1)
    yaml = YAML()
    yaml.preserve_quotes = True

    metadata = yaml.load(StringIO(yaml_content)) or {}
    body = content[match.end():]
    return dict(metadata), body
```

**原因**:
- `python-frontmatter` 内部也是类似实现
- 正则匹配 `---...---` 块是标准做法
- `ruamel-yaml` 的 `YAML().load()` 可直接解析字符串

**替代方案**:
- 使用 `ruamel.yaml` 的扫描器逐行解析（过度复杂）
- 使用状态机解析（需要处理嵌套边界，不值得）

### Decision 3: 写入时的处理

**选择**: 写入时手动构建 `---...---` 结构，不使用 `ruamel.yaml` 的 dump。

```python
def dump(metadata: dict, content: str = "") -> str:
    """Serialize metadata and content to markdown with frontmatter."""
    if not metadata:
        return content

    yaml = YAML()
    buf = StringIO()
    yaml.dump(dict(metadata), buf)
    frontmatter = buf.getvalue()

    return f"---\n{frontmatter}---\n{content}"
```

**原因**:
- frontmatter 格式要求 `---` 在单独一行
- `ruamel.yaml.dump()` 输出可能不符合预期格式
- 手动构建确保格式一致

## Risks / Trade-offs

[Risk] 非标准 frontmatter 格式（如使用 `...` 而非 `---`） → **Mitigation**: 暂不支持，仅处理标准 `---` 格式。如果有特殊需求再扩展。

[Risk] YAML 解析失败（语法错误） → **Mitigation**: `Profile._read_profile` 已有 try-except 保护，解析失败时返回空 dict。

[Risk] 保留引号和格式（`preserve_quotes`） → **Mitigation**: 读取时使用 `preserve_quotes = True`，但最终转换为普通 dict，写入时由 ruamel-yaml 重新处理。