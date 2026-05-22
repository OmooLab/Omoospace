## Context

Omoospace 项目是创意工作空间管理方法，核心心法：
1. 直白具体命名（避免缩写、特殊符号）
2. `contents/` 存静态资源型文件
3. `subspaces/` 存动态制作型文件
4. `OMOOSPACE.md` 记录项目信息

当前缺乏自动化检查和辅助创建工具。Claude Code Commands 可以无缝融入工作流，在日常对话中检查和引导用户。

## Goals / Non-Goals

**Goals:**
- 检查 subspaces/ 和 contents/ 下命名规范性（允许中文字符）
- 检查资源型文件（图片、视频、音频等）错误放置在 subspaces/
- 检查 OMOOSPACE.md frontmatter 格式规范
- 基于现有文件夹结构推测制作 objective
- 迁移旧结构到 omoospace，保持原有合理结构，通过 OMOOSPACE.md 配置映射

**Non-Goals:**
- 不修改原始文件，只报告问题和提供重组建议
- 不实现完整的文件操作，只提供指引
- 不替代 omoospace 的核心逻辑，只作为 AI 辅助层

## Decisions

### 1. 命令文件格式

**Decision**: Claude Code Command 文件放在 `.claude/commands/omoos/` 目录下，分别为 `lint.md` 和 `setup.md`

**Rationale**: Claude Code 支持子目录，按功能分组便于管理。命令名为 `omoos:lint` 和 `omoos:setup`。

### 2. omoos:lint 检查范围

**Decision**: 检查命名规范、文件放置、frontmatter 三类问题

**检查规则**:
```markdown
命名规范（格式: 语境前缀_核心名.修饰后缀）:
- 核心名必须有，语义正确
- 语境前缀用 `_` 分隔（如 `动画短片01_场景010`）
- 修饰后缀用 `.` 分隔（如 `.high.v001`）
- 前缀和后缀都可以没有
- 允许: 字母、数字、下划线`_`、连接符`-`、英文点`.`、中文字符
- 禁止: 空格、特殊符号（如 @、#、$ 等）

常见修饰后缀:
- .v001, .v002     → 版本
- .low, .high      → 面数
- .basecolor, .roughness → 贴图类型
- .001, .002       → 无语义编号 / 帧序号
- .1001, .1002     → UDIM
- .2k, .4k, .1080p → 分辨率
- .left, .right    → 方位

文件放置:
- 资源型文件（.png, .jpg, .mp4, .wav, .glb 等）→ contents/ 或其子目录
- 资源型文件不应放在 subspaces/（制作型文件可以放在 contents/ 作为引用）

frontmatter:
- 所有字段均为可选
- 只检查 YAML 格式是否有效
- notes, makers, tools, works 等字段可有可无
```

### 3. omoos:setup 无入参

**Decision**: omoos:setup 不接受命令行参数，自动分析现有结构（可能不是 omoospace 格式），并提出迁移到 omoospace 的方案

**Rationale**: 真实项目可能有各种旧的结构（assets/, source/, renders/ 等），setup 的作用是把这些旧结构迁移到 omoospace。AI 分析现有文件夹，推测项目类型和意图，提出新的文件夹结构建议，并生成迁移步骤。

**行为**:
1. 扫描项目根目录下的所有文件夹
2. 推测项目 objective（动画短片、产品设计等）
3. 检查是否已有 omoospace 结构（通过 OMOOSPACE.md 的 contents_dir/subspaces_dir 配置，或默认 subspaces/、contents/ 文件夹）
4. 如果没有合适结构，提出迁移方案：通过 OMOOSPACE.md 配置映射，而非强制创建 subspaces/、contents/ 文件夹
5. 生成文件迁移建议（移动到配置的 contents_dir/subspaces_dir）
6. 询问用户确认后展示详细迁移步骤

### 4. 所有 CLI 命令改为入参模式

**Decision**: 所有 CLI 命令从一问一答的交互模式改为入参模式，支持 agent 直接调用

**Rationale**: 用户通过 `omoos init` 安装 commands 后，在 Claude 中运行命令时需要入参模式才能被 agent 调用。交互式问答只能用于首次安装选择。

**命令入参转换**:
```bash
# init: 交互式选择安装哪些 commands
omoos init

# create: 创建 OMOOSPACE
omoos create "项目名" --brief "项目简介" [--contents "Contents"] [--subspaces "Subspaces"]

# subspace add: 创建 subspace
omoos subspace add "资产" [--parent "动画短片01"]

# work add: 添加 work
omoos work add "动画01" --contents "videos/动画01.mp4" [--brief "简介"]

# tool add: 添加 tool
omoos tool add "Blender" [--version "4.2.0"] [--website "https://blender.org"]

# maker add: 添加 maker
omoos maker add "偶魔数字" [--email "studio@omoolab.xyz"] [--website "https://omoolab.xyz"]
```

### 5. omoos init 安装流程

**Decision**: 询问 AI tool（默认 claude code），安装 `omoos/lint.md` 和 `omoos/setup.md`

**Rationale**: 用户选择 AI tool 后，将命令安装到对应的 commands 目录。

**流程**:
```bash
omoos init
# → 显示欢迎信息和 AI tool 选择（默认 claude code）
# → 按 Enter 确认，或输入其他 AI tool
# → 若要跳过，输入 "skip" 或 "跳过"
# → 创建 .claude/commands/omoos/ 目录
# → 安装 lint.md 和 setup.md
# → 完成安装
```

**安装路径**:
- claude code: `.claude/commands/omoos/lint.md`, `.claude/commands/omoos/setup.md`

## Risks / Trade-offs

[Risk] 用户已有自定义命令文件名冲突
→ Mitigation: 检查目标目录是否已有同名文件，提示用户确认覆盖

[Risk] frontmatter YAML 解析失败
→ Mitigation: 使用宽松解析，只报告格式错误，不中断检查

[Risk] 递归扫描大目录性能问题
→ Mitigation: 限制扫描深度（默认 3 层），跳过隐藏目录

## Open Questions

1. 是否需要支持自定义规则（比如额外允许的后缀）？
2. 重组操作是纯建议还是直接执行？