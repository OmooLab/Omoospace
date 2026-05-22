## ADDED Requirements

### Requirement: Naming Semantic Check
The system SHALL check that file and folder names have correct semantics based on omoospace naming conventions. File name format: `语境前缀_核心名.修饰后缀`

#### Scenario: Perfect name with all components
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `Seq010_Sc010.high.v001.blend`
- **THEN** system reports no error (Seq010=语境前缀, Sc010=核心名, .high.修饰后缀, .v001=版本后缀)

#### Scenario: Context prefix only
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `动画短片01_场景010.blend`
- **THEN** system reports no error (动画短片01=语境前缀, 场景010=核心名)

#### Scenario: Modifier suffix only
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `角色A.high.blend`
- **THEN** system reports no error (角色A=核心名, .high=修饰后缀)

#### Scenario: Multiple modifier suffixes
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `骨骼模型.high.v001.blend`
- **THEN** system reports no error (骨骼模型=核心名, .high.修饰后缀, .v001=版本)

#### Scenario: Just core name
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `角色A.blend`
- **THEN** system reports no error (角色A=核心名，单独使用也是正确的)

#### Scenario: Valid folder name (context prefix as folder)
- **WHEN** user runs `omoos:lint`
- **AND** a folder is named `动画短片01`
- **THEN** system reports no error

#### Scenario: Valid nested path
- **WHEN** user runs `omoos:lint`
- **AND** a file path is `subspaces/动画短片01/资产/角色A.blend`
- **THEN** system reports no error

#### Scenario: Invalid name with spaces
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `my file.png`
- **THEN** system reports: "文件名包含空格: my file.png"

#### Scenario: Invalid name with special symbols
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `file@#.txt`
- **THEN** system reports: "文件名包含非法字符: file@#.txt"

### Requirement: Suffix Semantic Check
The system SHALL verify that modifier suffixes follow semantic conventions. Common suffixes:

| 后缀 | 语义 | 示例 |
|------|------|------|
| .v001, .v002 | 版本 | 骨骼模型.v001.blend |
| .low, .high | 面数 | 角色A.high.blend |
| .basecolor, .roughness | 贴图类型 | 贴图.basecolor.2k.png |
| .0001, .0002 | 帧序号（4位） | Seq010_Sc010.0001.png |
| .1001, .1002 | UDIM（4位） | 模型.1001.png |
| .bak | 备份 | 场景010.bak.blend |
| .2k, .4k, .1080p | 分辨率 | 视频.1080p.mp4 |
| .left, .right | 方位 | 通道.left.wav |
| .karma, .arnold | 渲染器 | 场景.karma.exr |
| .beauty, .clay | 渲染风格 | 渲染.beauty.0001.exr |
| .bak | 备份 | 场景010.bak.blend |

#### Scenario: Correct version suffix
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `骨骼模型.v001.blend`
- **THEN** system reports no error

#### Scenario: Correct resolution suffix
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `贴图.basecolor.2k.png`
- **THEN** system reports no error

#### Scenario: Correct frame suffix
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `Seq010_Sc010.0001.png`
- **THEN** system reports no error

#### Scenario: Correct UDIM suffix
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `模型.1001.png`
- **THEN** system reports no error

#### Scenario: Multiple correct suffixes
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `场景010.karma.high.v001.exr`
- **THEN** system reports no error (.karma=渲染器, .high=面数, .v001=版本)

#### Scenario: Incorrect suffix standalone .001
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `骨骼模型.001.blend`
- **THEN** system reports: "后缀 .001 单独使用无语义，请使用 .v001 表示版本"

#### Scenario: Correct .v001 version suffix
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `骨骼模型.v001.blend`
- **THEN** system reports no error

#### Scenario: Correct frame sequence suffix (.0001, 4 digits)
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `Seq010_Sc010.0001.png`
- **THEN** system reports no error

#### Scenario: Correct UDIM suffix (.1001, 4 digits)
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `模型.1001.png`
- **THEN** system reports no error

#### Scenario: Incorrect suffix .bak without context
- **WHEN** user runs `omoos:lint`
- **AND** a file is named `场景010.bak.blend`
- **THEN** system reports no error (.bak 作为修饰后缀是合理的)

#### Scenario: Frontmatter with notes and makers
- **WHEN** user runs `omoos:lint`
- **AND** OMOOSPACE.md contains valid frontmatter with notes and makers
- **THEN** system reports no error

### Requirement: File Placement Check
The system SHALL verify that resource-type files are not incorrectly placed in subspaces/. Uses Omoospace.subspaces_dir and Omoospace.contents_dir to get actual paths.

#### Scenario: Resource file in subspaces (violation)
- **WHEN** user runs `omoos:lint`
- **AND** a resource file is in the subspaces directory (e.g., `Assets/textures/` if subspaces_dir is root)
- **THEN** system reports: "资源型文件不应放在 subspaces_dir 目录下: ..."

#### Scenario: Valid resource file location
- **WHEN** user runs `omoos:lint`
- **AND** a resource file is in the contents directory
- **THEN** system reports no error for this file

#### Scenario: Production file in contents as reference (valid)
- **WHEN** user runs `omoos:lint`
- **AND** a production file (.blend, .psd, etc.) is in contents directory
- **THEN** system reports no error for this file (production files can be in contents as references)

#### Scenario: Production file in subspaces (valid)
- **WHEN** user runs `omoos:lint`
- **AND** a production file (.blend, .psd, etc.) is in subspaces directory
- **THEN** system reports no error for this file

### Requirement: Frontmatter Validation
The system SHALL validate OMOOSPACE.md frontmatter format. All fields are optional.

#### Scenario: Valid frontmatter (empty)
- **WHEN** user runs `omoos:lint`
- **AND** OMOOSPACE.md contains only `---` delimiters with no content
- **THEN** system reports no error

#### Scenario: Valid frontmatter with fields
- **WHEN** user runs `omoos:lint`
- **AND** OMOOSPACE.md contains valid frontmatter with any fields
- **THEN** system reports no error

#### Scenario: Invalid YAML syntax
- **WHEN** user runs `omoos:lint`
- **AND** OMOOSPACE.md frontmatter has invalid YAML
- **THEN** system reports: "OMOOSPACE.md frontmatter YAML 格式错误"