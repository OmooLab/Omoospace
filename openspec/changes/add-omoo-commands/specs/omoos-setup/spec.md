## ADDED Requirements

### Requirement: Resolve Actual Directories via Omoospace API
The system SHALL use Omoospace.subspaces_dir and Omoospace.contents_dir to get the actual folder paths based on OMOOSPACE.md configuration.

#### Scenario: Unity Assets as contents
- **WHEN** user runs `omoos:setup`
- **AND** OMOOSPACE.md has `contents_dir: Assets`
- **THEN** Omoospace.contents_dir returns `Assets/` path
- **AND** Omoospace.subspaces_dir returns `Projects/` path (or root if not set)

#### Scenario: Root directory as subspaces
- **WHEN** user runs `omoos:setup`
- **AND** OMOOSPACE.md has no subspaces_dir configured
- **AND** project uses root directory for production files
- **THEN** Omoospace.subspaces_dir returns root directory path

#### Scenario: Detect subspaces/contents by checking actual folders
- **WHEN** user runs `omoos:setup`
- **AND** project has no OMOOSPACE.md
- **AND** project has `assets/`, `source/`, `shots/` folders
- **THEN** system uses Omoospace to check which folders exist and infer the configuration
- **AND** system proposes mapping based on actual folder contents

### Requirement: Analyze Existing Structure
The system SHALL analyze the existing folder structure (which may not follow omoospace conventions) and infer the project objective and current organization method.

#### Scenario: Existing structure with different naming
- **WHEN** user runs `omoos:setup`
- **AND** project has folders like `assets/`, `source/`, `renders/`
- **THEN** system displays: "检测到非 omoospace 结构: assets/, source/, renders/"
- **AND** system analyzes which folders contain production files vs resource files
- **AND** system asks: "是否要将此结构迁移到 omoospace?"

#### Scenario: Existing subspaces/contents structure (omoospace-compliant)
- **WHEN** user runs `omoos:setup`
- **AND** project has `subspaces/` and `contents/` folders
- **AND** folders are well-organized
- **THEN** system displays: "已是 omoospace 结构，无需调整"
- **AND** system suggests improvements if any

#### Scenario: Existing single-folder structure (e.g., Unity Assets)
- **WHEN** user runs `omoos:setup`
- **AND** project has only `Assets/` folder (like Unity)
- **THEN** system proposes to configure `contents_dir: Assets` in OMOOSPACE.md
- **AND** system suggests appropriate `subspaces_dir` structure

### Requirement: Preserve Existing Structure During Migration
The system SHALL keep existing folders that are already correctly organized and only create subspaces/ and contents/ when needed.

#### Scenario: Preserve type-based folders as contents
- **WHEN** user runs `omoos:setup`
- **AND** project has `textures/`, `renders/`, `audio/` folders
- **AND** these folders contain resource files
- **THEN** system suggests: "保留 textures/, renders/, audio/ 为 contents 类型文件夹"
- **AND** these folders become contents/ or stay where they are (depending on config)

#### Scenario: Preserve shots structure as subspaces
- **WHEN** user runs `omoos:setup`
- **AND** project has `shots/`, `scenes/` folders with production files
- **THEN** system suggests: "保留 shots/, scenes/ 为 subspaces 类型文件夹"
- **AND** these folders become subspaces/ or stay where they are (depending on config)

#### Scenario: No subspaces or contents folders exist
- **WHEN** user runs `omoos:setup`
- **AND** project has `Assets/` (Unity) or similar folder that acts as contents
- **THEN** system proposes OMOOSPACE.md configuration:
  ```yaml
  contents_dir: Assets
  subspaces_dir: Projects
  ```
- **AND** system does NOT create new subspaces/ or contents/ folders
- **AND** system suggests to create Projects/ folder for production files

### Requirement: Propose Omoospace Structure by Objective
The system SHALL propose subspaces organized by creative objective, not by file type. Category folders (if needed) should use English names.

#### Scenario: Propose structure for animation project
- **WHEN** user runs `omoos:setup`
- **AND** project contains `.blend` files
- **AND** inferred objective is "animation short film"
- **THEN** system proposes subspaces organized by shots/objectives:
  ```
  subspaces/
  ├── Shot010/
  ├── Shot020/
  └── Asset_CharacterA/

  contents/
  (textures/, renders/, audio/ - kept as-is or moved to contents/)
  ```

#### Scenario: Propose structure for static project
- **WHEN** user runs `omoos:setup`
- **AND** project contains `.psd`, `.ai` files
- **AND** inferred objective is "product design"
- **THEN** system proposes subspaces by objective:
  ```
  subspaces/
  ├── ConceptArt/
  └── Model_WIP/

  contents/
  (references/, outputs/ - kept as-is)
  ```

#### Scenario: Flat structure with loose files
- **WHEN** user runs `omoos:setup`
- **AND** project has loose files like `character.blend`, `scene.blend`
- **AND** no clear organization
- **THEN** system proposes subspaces by objective based on file names
- **AND** suggests creating folders like `动画短片01/` as the root subspace

### Requirement: Configure OMOOSPACE.md
The system SHALL create or update OMOOSPACE.md with the project configuration, mapping existing folders to contents_dir and subspaces_dir.

#### Scenario: Create OMOOSPACE.md with custom folder mapping
- **WHEN** user runs `omoos:setup`
- **AND** project keeps `Assets/` as contents and `Projects/` as subspaces
- **THEN** system creates OMOOSPACE.md:
  ```yaml
  ---
  brief: <inferred project name>
  contents_dir: Assets
  subspaces_dir: Projects
  ---
  ```

#### Scenario: Create subspaces/ and contents/ when needed
- **WHEN** user runs `omoos:setup`
- **AND** project has no suitable existing folders
- **AND** structure needs reorganization
- **THEN** system suggests: "创建文件夹: subspaces/, contents/"

#### Scenario: Preserve existing OMOOSPACE.md
- **WHEN** user runs `omoos:setup`
- **AND** OMOOSPACE.md already exists with valid content
- **THEN** system preserves existing configuration

### Requirement: Provide Migration Plan
The system SHALL suggest a step-by-step migration plan to reorganize files from old structure to omoospace structure.

#### Scenario: Suggest folder mapping
- **WHEN** user runs `omoos:setup`
- **AND** old structure has `textures/`, `renders/`, `shots/`
- **THEN** system suggests:
  - "移动 textures/, renders/ → contents/"
  - "移动 shots/ → subspaces/"

#### Scenario: Ask for user confirmation before presenting full plan
- **WHEN** user runs `omoos:setup`
- **AND** system has analyzed existing structure
- **THEN** system asks: "是否按上述方案重组项目?"
- **AND** if user confirms, system presents detailed migration steps
- **AND** if user declines, system exits