## 1. Refactor ALL CLI Commands to Argument Mode

Convert all interactive Q&A commands to positional argument mode for agent compatibility.

- [x] 1.1 Convert `init` command to positional arguments: `omoos init [--contents "Contents"] [--subspaces "Subspaces"] [--chinese-to-pinyin] [--readme]`
- [x] 1.2 Convert `create` command to positional arguments: `omoos create "项目名" [--brief "简介"] [--contents "Contents"] [--subspaces "Subspaces"] [--chinese-to-pinyin] [--readme]`
- [x] 1.3 Convert `subspace add` command to positional arguments: `omoos subspace add "资产" [--parent "父目录"]`
- [x] 1.4 Convert `work add` command to positional arguments: `omoos work add "动画01" --contents "videos/01.mp4" [--brief "简介"]`
- [x] 1.5 Convert `tool add` command to positional arguments: `omoos tool add "Blender" [--version "4.2.0"] [--website "url"]`
- [x] 1.6 Convert `maker add` command to positional arguments: `omoos maker add "偶魔数字" [--email "email"] [--website "url"]`

## 2. Implement omoos:setup Command (无入参，自动分析)

- [x] 2.1 Scan existing folder structure and identify resource vs production files
- [x] 2.2 Detect if omoospace structure already exists (subspaces/, contents/ or OMOOSPACE.md config)
- [x] 2.3 Preserve existing type-based folders (textures/, renders/, shots/ etc.)
- [x] 2.4 Propose subspaces organized by objective (not by type)
- [x] 2.5 Generate OMOOSPACE.md config with custom contents_dir/subspaces_dir mapping if needed
- [x] 2.6 Create subspaces/ or contents/ only when no suitable existing folders exist
- [x] 2.7 Generate migration suggestions (file moves, folder mapping)

## 3. Implement omoos:lint Command

- [x] 3.1 Define resource-type file extensions (.png, .jpg, .mp4, .wav, .glb, etc.)
- [x] 3.2 Implement naming semantic check (语境前缀_核心名.修饰后缀)
- [x] 3.3 Implement suffix convention check (.v001, .high, .basecolor, etc.)
- [x] 3.4 Implement file placement check (resource-type files不应在subspaces/)
- [x] 3.5 Implement OMOOSPACE.md frontmatter validation (YAML parsing, all fields optional)
- [x] 3.6 Output formatted report with file paths and issue descriptions

## 4. Implement omoos init Installation

- [x] 4.1 Implement AI tool selection prompt (default: claude code)
- [x] 4.2 Implement skip option (user types "skip" or "跳过")
- [x] 4.3 Create `.claude/commands/omoos/` directory
- [x] 4.4 Copy lint.md and setup.md to the target AI tool's commands directory
- [x] 4.5 Implement existing file overwrite detection and confirmation

## 5. Create Claude Command Files

- [x] 5.1 Create `.claude/commands/omoos/lint.md` with description and instructions
- [x] 5.2 Create `.claude/commands/omoos/setup.md` with description and instructions

## 6. Documentation

- [x] 6.1 Update docs/cli.md with new commands usage and examples
- [x] 6.2 Add examples for `omoos:lint`, `omoos:setup`, `omoos init`