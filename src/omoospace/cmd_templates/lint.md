# Omoos Lint

Check naming conventions, file placement, and OMOOSPACE.md frontmatter for the current Omoospace project.

## Usage

```
omoos:lint
```

## Checks

### Naming Convention

File and folder names must follow the format: `语境前缀_核心名.修饰后缀`

**Allowed characters:**
- Letters, digits, underscore `_`, dash `-`, dot `.`, Chinese characters
- **Forbidden:** spaces, special symbols (@, #, $, etc.)

**Modifier suffixes:**
| Suffix | Meaning | Example |
|--------|---------|---------|
| `.v001`, `.v002` | Version | `骨骼模型.v001.blend` |
| `.low`, `.high` | Polygon count | `角色A.high.blend` |
| `.basecolor`, `.roughness` | Texture type | `贴图.basecolor.2k.png` |
| `.0001`, `.0002` | Frame sequence (4 digits) | `Seq010_Sc010.0001.png` |
| `.1001`, `.1002` | UDIM (4 digits) | `模型.1001.png` |
| `.bak` | Backup | `场景010.bak.blend` |
| `.2k`, `.4k`, `.1080p` | Resolution | `视频.1080p.mp4` |
| `.left`, `.right` | Direction | `通道.left.wav` |
| `.karma`, `.arnold` | Renderer | `场景.karma.exr` |
| `.beauty`, `.clay` | Render style | `渲染.beauty.0001.exr` |

**Suffix rules:**
- `.001` alone is meaningless — use `.v001` for versions
- Frame sequences must be 4 digits: `.0001`, not `.1`
- UDIM tiles must be 4 digits: `.1001`, not `.001`

### File Placement

- Resource files (`.png`, `.jpg`, `.mp4`, `.wav`, `.glb`, etc.) should be in `contents/` or its subdirectories
- Resource files should NOT be in `subspaces/` (production files can be in `contents/` as references)
- Get actual paths via `Omoospace.subspaces_dir` and `Omoospace.contents_dir` from OMOOSPACE.md config

### Frontmatter Validation

- All fields in OMOOSPACE.md frontmatter are optional
- Only validates YAML syntax is correct

## Output Format

Report each issue with:
- File path
- Problem description
- Suggestion

## Examples

```bash
# Check current project
omoos:lint

# Report format
# ❌ 文件名包含空格: my file.png
# ❌ 后缀 .001 单独使用无语义，请使用 .v001 表示版本
# ⚠️ 资源型文件不应放在 subspaces/: textures/背景.png
# ❌ OMOOSPACE.md frontmatter YAML 格式错误
```