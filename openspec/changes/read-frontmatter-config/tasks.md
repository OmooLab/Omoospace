## 1. setup 和依赖

- [x] 1.1 使用 `uv add python-frontmatter` 验证库安装正确

## 2. 核心实现

- [x] 2.1 在 `Omoospace` 类初始化逻辑中，优先检查 `Omoospace.md` 是否存在且包含有效 frontmatter
- [x] 2.2 当 `Omoospace.md` 存在且有效时，使用 frontmatter 作为配置源，跳过 `Omoospace.yml`
- [x] 2.3 当 `Omoospace.md` 不存在或无效时，回退到原有的 `Omoospace.yml` 读取逻辑

## 3. 错误处理

- [x] 3.1 处理 `Omoospace.md` 存在但 frontmatter 格式错误的情况 — 回退到 `Omoospace.yml`
- [x] 3.2 处理 `Omoospace.md` 存在但无 frontmatter 内容的情况 — 回退到 `Omoospace.yml`

## 4. 日志与警告

- [x] 4.1 当同时存在 `Omoospace.md` 和 `Omoospace.yml` 时，输出日志警告说明 MD 文件优先级更高

## 5. 测试

- [x] 5.1 添加测试：仅存在 `Omoospace.yml` 时正常读取配置
- [x] 5.2 添加测试：仅存在 `Omoospace.md` 时正常读取 frontmatter 配置
- [x] 5.3 添加测试：同时存在时，`Omoospace.md` 优先
- [x] 5.4 添加测试：`Omoospace.md` 存在但格式错误时，回退到 `Omoospace.yml`