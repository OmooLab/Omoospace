## Why

Omoospace 心法强调用直白具体的命名、contents/ 存资源型文件、subspaces/ 存制作型文件、OMOOSPACE.md 记录信息。但目前没有自动化工具检查这些规范的执行情况，也没有命令来辅助设计符合规范的项目结构。通过 Claude Code Commands，可以让 AI 在工作流中自动检查和引导用户遵循心法。

## What Changes

- 新增 `omoos:lint` 命令：检查 subspaces/ 和 contents/ 下的命名规范性、资源型文件错误放置在 subspaces/、OMOOSPACE.md frontmatter 格式
- 新增 `omoos:setup` 命令：分析现有项目结构（可能是任意旧格式），提出迁移到 omoospace 的方案，保持原有合理结构，通过 OMOOSPACE.md 配置映射（无入参，自动分析）
- 大改 `omoos init` 交互流程：改为选择 AI tool（默认 claude code），安装 `omoos/lint.md` 和 `omoos/setup.md`

## Capabilities

### New Capabilities

- `omoos-lint`: 检查命名规范、资源型文件错误放置、frontmatter 格式
- `omoos-setup`: 分析现有项目结构，迁移到 omoospace，保持原有结构，通过 OMOOSPACE.md 配置映射
- `omoos-init`: 交互式选择安装哪些 commands

### Modified Capabilities

（无）

## Impact

- 新增 `.claude/commands/omoos/lint.md` 和 `.claude/commands/omoos/setup.md`
- 修改 CLI 交互逻辑，从一来一回问答改为入参模式
- 依赖 Omoospace 配置结构（OMOOSPACE.md 及配置的 contents_dir/subspaces_dir，默认为 contents/、subspaces/）