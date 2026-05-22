## ADDED Requirements

### Requirement: AI Tool Selection
The system SHALL prompt user to select AI tool during initialization. Default is claude code.

#### Scenario: Default AI tool (claude code)
- **WHEN** user runs `omoos init`
- **AND** user presses Enter without selecting
- **THEN** system confirms: "将安装到 claude code"
- **AND** system proceeds to install commands

#### Scenario: Skip installation
- **WHEN** user runs `omoos init`
- **AND** user types "skip" or "跳过"
- **THEN** system reports: "跳过安装，可在稍后运行 omoos init 重新安装"

### Requirement: Install Commands to AI Tool Directory
The system SHALL copy commands to `.claude/commands/omoos/` directory (lint.md and setup.md).

#### Scenario: Install to claude code (default)
- **WHEN** user selects claude code (or presses Enter)
- **THEN** system creates `.claude/commands/omoos/` directory if not exists
- **AND** system copies `omoos/lint.md` and `omoos/setup.md` to `.claude/commands/omoos/`
- **AND** system confirms: "已安装 omoos/lint.md 和 omoos/setup.md 到 claude code"

### Requirement: Detect Existing Commands
The system SHALL check if command files already exist and prompt for overwrite confirmation.

#### Scenario: Commands already exist
- **WHEN** user runs `omoos init`
- **AND** `.claude/commands/omoos/lint.md` or `.claude/commands/omoos/setup.md` already exists
- **AND** user confirmed installation
- **THEN** system prompts: "omooos/lint.md 或 omoos/setup.md 已存在，是否覆盖? (y/n)"
- **AND** if user confirms, system overwrites the files
- **AND** if user declines, system skips this file