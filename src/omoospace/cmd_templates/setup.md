# Omoos Setup

Analyze existing project structure and propose migration to omoospace format.

## Usage

```
omoos:setup
```

## Behavior

1. **Scan existing structure**: Analyze all folders in project root
2. **Detect existing omoospace**: Check if subspaces/, contents/, or OMOOSPACE.md config already exists
3. **Preserve existing folders**: Keep type-based folders (textures/, renders/, shots/, Assets/, etc.) — do not delete
4. **Propose omoospace mapping**: Configure via OMOOSPACE.md contents_dir/subspaces_dir instead of restructuring
5. **Propose subspaces by objective**: Organize subspaces based on creative objectives, not file types

## Migration Rules

### Preserve Existing Structure
- If project uses `Assets/` (Unity) or similar folder as content container, keep it
- Map existing folders via OMOOSPACE.md config:
  ```yaml
  contents_dir: Assets
  subspaces_dir: Projects
  ```

### Propose New Structure by Objective
- **Animation project**: Organize by shots (Shot010/, Shot020/, Asset_CharacterA/)
- **Product design**: Organize by concepts (ConceptArt/, Model_WIP/)
- Use Chinese names for objective folders if original names are Chinese

### Create Only When Needed
- Only create subspaces/ or contents/ if no suitable existing folders exist
- Prefer mapping existing folders over creating new ones

## Output Format

```
检测到非 omoospace 结构: assets/, source/, renders/
分析: assets/ 包含资源文件, source/ 包含制作文件

建议配置:
contents_dir: assets
subspaces_dir: source

迁移建议:
- 移动 textures/, renders/ → assets/
- 移动 shots/, scenes/ → source/
- 保持原有结构不变

是否按上述方案重组项目? (y/n)
```

## Examples

```bash
# Analyze and propose migration
omoos:setup

# Output includes:
# - Detected folder structure
# - Proposed OMOOSPACE.md config
# - Migration steps (file moves, folder mapping)
# - Confirmation prompt before proceeding
```