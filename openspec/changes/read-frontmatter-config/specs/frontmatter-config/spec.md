## 新增需求

### 需求：Omoospace 支持从 Omoospace.md 读取配置
系统 SHALL（必须）支持从根目录的 `Omoospace.md` 文件读取 YAML frontmatter 配置，并让该配置源优先于 `Omoospace.yml`。

#### 场景：Omoospace.md 存在且有效时使用 MD 配置
- **WHEN** `Omoospace.md` 文件存在于根目录且包含有效的 YAML frontmatter
- **THEN** 系统 SHALL（必须）使用该 frontmatter 作为配置源，完全忽略 `Omoospace.yml`

#### 场景：Omoospace.md 不存在时回退到 YAML
- **WHEN** `Omoospace.md` 文件不存在于根目录
- **THEN** 系统 SHALL（必须）回退到使用 `Omoospace.yml` 作为配置源

#### 场景：Omoospace.md 存在但无 frontmatter 时回退到 YAML
- **WHEN** `Omoospace.md` 文件存在但不包含有效的 YAML frontmatter（为空或仅包含无 frontmatter 的 Markdown 内容）
- **THEN** 系统 SHALL（必须）回退到使用 `Omoospace.yml` 作为配置源

#### 场景：Omoospace.md 存在但 frontmatter 格式错误时回退到 YAML
- **WHEN** `Omoospace.md` 文件存在但包含格式错误的 YAML frontmatter
- **THEN** 系统 SHALL（必须）回退到使用 `Omoospace.yml` 作为配置源，且不抛出异常

### 需求：Omoospace.md 优先于 Omoospace.yml
系统 SHALL（必须）确保当 `Omoospace.md` 存在且有效时，`Omoospace.yml` 完全被忽略。

#### 场景：同时存在 MD 和 YAML 文件时，MD 优先
- **WHEN** 根目录同时存在 `Omoospace.md`（含有效 frontmatter）和 `Omoospace.yml`
- **THEN** 系统 SHALL（必须）只读取 `Omoospace.md` 的配置，不读取 `Omoospace.yml`

### 需求：向后兼容现有 YAML 配置
系统 SHALL（必须）在没有 `Omoospace.md` 或 `Omoospace.md` 无效时，保持对 `Omoospace.yml` 的完全兼容。

#### 场景：仅有 Omoospace.yml 时正常工作
- **WHEN** 根目录仅存在 `Omoospace.yml`，不存在 `Omoospace.md`
- **THEN** 系统 SHALL（必须）正常读取 `Omoospace.yml` 中的配置

### 需求：日志警告同时存在的情况
系统 SHALL（必须）在 `Omoospace.md` 和 `Omoospace.yml` 同时存在时，输出日志警告说明 MD 文件优先级更高。

#### 场景：检测到两者同时存在时输出警告
- **WHEN** 根目录同时存在 `Omoospace.md` 和 `Omoospace.yml`
- **THEN** 系统 SHALL（必须）输出 INFO 级别日志，说明 `Omoospace.md` 优先级更高