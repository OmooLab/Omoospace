## 背景

Omoospace 使用 YAML profile 文件（如 `Omoospace.yml`）存储配置。目标是扩展支持从 `Omoospace.md` 的 YAML frontmatter 读取配置，并让 MD 文件拥有更高的读取优先级。

当前实现：
- `Omoospace` 类从根目录的 `Omoospace.{lang}.yml` 读取 profile
- 不支持 Markdown 文件作为配置源
- `Objective` 类封装树节点，但不涉及配置读取

## 目标 / 非目标

**目标：**
- 支持从根目录的 `Omoospace.md` 文件读取 YAML frontmatter 配置
- 设置读取优先级：`Omoospace.md` > `Omoospace.yml`
- 当 `Omoospace.md` 存在且有有效 frontmatter 时，完全使用 MD 文件配置
- 当 `Omoospace.md` 不存在或无有效 frontmatter 时，回退到 `Omoospace.yml`
- 保持与现有 `Omoospace.yml` 配置的向后兼容

**非目标：**
- 将配置写回 `Omoospace.md`（只读）
- 支持 `Omoospace.md` 以外的其他 Markdown 文件作为配置源
- 改变 `Omoospace.yml` 的工作方式或格式

## 决策

1. **`Omoospace.md` 优先级高于 `Omoospace.yml`**
   - 当 `Omoospace.md` 存在且包含有效 frontmatter 时，完全使用 MD 文件
   - 不做合并：MD 文件存在时，完全忽略 YAML 文件
   - 原因：用户明确选择 MD 文件作为配置源，应获得完整控制权

2. **使用 `python-frontmatter` 库进行解析**
   - 成熟、维护良好的 YAML frontmatter 解析库
   - 已处理边缘情况（无 frontmatter、格式错误的 YAML 等）
   - 替代方案：手动正则解析 — 被拒绝，因为容易出错

3. **`Omoospace.md` 只读，不写入**
   - 避免文件与 profile 之间的同步问题
   - 用户可以在 MD 文件中自由编辑 frontmatter

4. **读取优先级：MD > YAML**
   - `Omoospace.md` 存在且有效 → 使用 MD
   - `Omoospace.md` 不存在或无效 → 回退到 `Omoospace.yml`
   - 与原有 profile 读取逻辑兼容

## 风险 / 权衡

- **风险**：用户同时维护 `Omoospace.md` 和 `Omoospace.yml` 导致配置冲突
  - **缓解**：明确文档说明 MD 优先，MD 存在时 YAML 完全被忽略
  - **缓解**：检测到两者同时存在时，在日志中输出警告信息

- **风险**：格式错误的 frontmatter 导致配置读取失败
  - **缓解**：frontmatter 无效时回退到 YAML 文件
  - **缓解**：格式错误返回空 dict `{}` 而不是抛出异常

- **风险**：引入新的文件导致现有工具或脚本行为改变
  - **缓解**：YAML 文件仍然是有效的配置源（作为回退）
  - **缓解**：仅当 `Omoospace.md` 存在时才改变行为