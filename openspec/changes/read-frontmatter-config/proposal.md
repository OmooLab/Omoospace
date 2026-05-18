## 背景

Omoospace 目前仅支持通过 YAML profile 文件（如 `Omoospace.yml`）管理配置。然而，许多内容创作者更倾向于使用 Markdown 文件结合 YAML frontmatter 来存储元数据。这种方式使得项目文档更加自包含，并能与 Obsidian、Notion 等工具以及静态网站生成器更好地集成。

## 变更内容

- 新增 `Omoospace.md` 支持：从带有 YAML frontmatter 的 `Omoospace.md` 文件读取配置
- 优先级调整：`Omoospace.md` 优先于 `Omoospace.yml`，前者存在时直接使用前者
- 向后兼容：当 `Omoospace.md` 不存在时，回退到现有的 `Omoospace.yml` 机制
- 支持标准 frontmatter 字段：`name`、`brief`、`tags`、`created`、`modified`、`makers`、`tools`、`works`

## 能力

### 新增能力
- `omoospace-md-config`：支持从 `Omoospace.md` 的 YAML frontmatter 读取配置，优先于 `Omoospace.yml`

### 修改的能力
- 无（这是新增能力，不改变现有 `Omoospace.yml` 的工作方式，仅添加 MD 文件作为更高优先级的配置源）

## 影响

- 受影响代码：`src/omoospace/omoospace.py`
- 新增依赖：`python-frontmatter` 或等效的 frontmatter 解析库
- 配置文件：`Omoospace.md`（优先）或 `Omoospace.yml`（回退）