## Why

统一配置文件格式和默认命名约定，同时简化多语言配置逻辑。OMAOSPACE.md 作为纯 Markdown 配置文件更直观易读，现需要赋予其完整的读写能力。

## What Changes

- **YAML 格式扩展**：除 `.yml` 外，支持 `.yaml` 扩展名的配置文件
- **小写默认目录名**：`create_omoospace` 的 `contents_dir` 和 `subspaces_dir` 参数默认值从 `Contents`/`Subspaces` 改为 `contents`/`subspaces`
- **OMOOSPACE.md 替代 Omoospace.yml**：新建项目默认生成 `OMOOSPACE.md` 而非 `Omoospace.yml` 作为配置文件
- **移除多语言配置支持**：配置文件中的多语言键名（如 `name_zh`、`name_en`）功能移除，仅支持英文键名
- **OMOOSPACE.md 读写等效**：赋予 `OMOOSPACE.md` 写入配置的能力，使其与 `omoospace.yml` 功能完全等价

## Capabilities

### New Capabilities

- `omoospace-md-config`：支持 OMOOSPACE.md 作为配置文件，具备完整的读写能力
- `yaml-format-support`：支持 `.yaml` 和 `.yml` 两种 YAML 文件扩展名

### Modified Capabilities

- `create-omoospace`：默认目录名和生成的配置文件类型变更
- `config-resolution`：移除多语言配置解析逻辑

## Impact

- 配置文件读取逻辑需同时支持 `.yml` 和 `.yaml`
- `create_omoospace` 函数的默认参数和生成逻辑变更
- 配置写入逻辑需适配 OMOOSPACE.md 格式
- 多语言配置解析代码可移除