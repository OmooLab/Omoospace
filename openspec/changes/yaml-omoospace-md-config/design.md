## Context

当前 Omoospace 配置系统存在以下问题：
1. 配置文件仅支持 `.yml` 扩展名，不支持更通用的 `.yaml`
2. 默认目录名为 `Contents`/`Subspaces`（首字母大写），不符合 Unix 惯例
3. 配置文件默认为 `Omoospace.yml`，但 `OMOOSPACE.md` 仅用于读取
4. 配置键名支持多语言（`key_zh`/`key_en`），增加维护复杂度

## Goals / Non-Goals

**Goals:**
- 支持 `.yaml` 和 `.yml` 两种扩展名
- 默认目录名改为小写 `contents`/`subspaces`
- 默认生成 `OMOOSPACE.md` 作为配置文件
- 移除多语言配置键名支持
- 赋予 `OMOOSPACE.md` 完整读写能力

**Non-Goals:**
- 不修改现有已创建的项目的配置（向后兼容）
- 不支持除 `.yml`/`.yaml` 外的其他配置文件格式

## Decisions

### 1. YAML 格式扩展

**决定**：配置文件读取时同时匹配 `.yml` 和 `.yaml` 扩展名。

**理由**：很多现代项目倾向使用 `.yaml` 扩展名（Docker、GitHub Actions 等），保持一致性。

**实现**：
- `Omoospace.__init__` 中的 `candidates` glob 改为 `Omoospace.*`
- 读取时优先选择 `OMOOSPACE.md`（含 frontmatter），其次 `.yml`/`.yaml`

### 2. 小写默认目录名

**决定**：`create_omoospace` 的 `contents_dir` 和 `subspaces_dir` 默认值从 `Contents`/`Subspaces` 改为 `contents`/`subspaces`。

**理由**：Unix 系统惯例，目录名小写更简洁。

**影响范围**：
- `functions.py`：`create_omoospace` 函数默认参数
- `omoospace.py`：`subspaces_dir` 和 `contents_dir` 属性的默认值（`or "Subspaces"` → `or "subspaces"`，`or "Contents"` → `or "contents"`）

### 3. OMOOSPACE.md 替代 Omoospace.yml

**决定**：`create_omoospace` 默认生成 `OMOOSPACE.md` 而非 `Omoospace.yml`。

**理由**：`OMOOSPACE.md` 作为 Markdown 文件更直观，可直接编辑查看。

**实现**：
- `create_omoospace` 创建 `OMOOSPACE.md`（使用 frontmatter 格式）
- `Omoospace.__init__` 中 `OMOOSPACE.md` 优先级保持最高

### 4. 移除多语言配置支持

**决定**：删除 `language.py` 中的 `key_dict` 和 `ALLOWED_LANGS`，简化 `_key()` 方法。

**理由**：多语言键名功能使用率低，维护成本高。

**实现**：
- 删除 `key_dict` 和 `_key()` 方法中的多语言查询，直接使用原始键名
- `Profile.get()` 和 `Profile.set()` 直接使用 `key` 而非 `self._key(key)`
- `ProfileItem._key()` 同理简化

### 5. OMOOSPACE.md 读写等效

**决定**：修改 `_write_profile()` 方法，使其能够正确写入 `OMOOSPACE.md`。

**当前问题**：`_write_profile()` 在遇到 `.md` 文件时会切换到 `.yml` 文件。

**理由**：用户选择使用 `OMOOSPACE.md` 作为配置，应保持该选择。

**实现**：
- `_write_profile()` 保留 `.md` 文件格式，使用 `frontmatter.dumps()` 写入
- 写入时重新读取、修改、写回，而非切换文件

## Risks / Trade-offs

- **向后兼容**：现有 `.yml` 文件和旧配置仍可正常读取，但新建项目默认使用 `OMOOSPACE.md`
- **多语言迁移**：移除多语言后，原有使用多语言键名的配置需手动迁移到英文键名

## Open Questions

无