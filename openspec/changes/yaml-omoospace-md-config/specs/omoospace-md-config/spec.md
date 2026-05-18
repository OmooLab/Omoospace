## ADDED Requirements

### Requirement: OMOOSPACE.md as primary config file

The system SHALL support `OMOOSPACE.md` as a configuration file format, using YAML frontmatter (Markdown metadata) to store configuration data. This file SHALL take priority over `Omoospace.yml` or `Omoospace.yaml` when detected.

#### Scenario: Omoospace initialized with OMOOSPACE.md
- **WHEN** user creates a new Omoospace project
- **THEN** system generates `OMOOSPACE.md` as the configuration file by default
- **AND** the file contains valid YAML frontmatter with `brief` field

#### Scenario: Existing OMOOSPACE.md is loaded
- **WHEN** Omoospace detects `OMOOSPACE.md` in root directory
- **AND** the file contains valid frontmatter with configuration data
- **THEN** system loads configuration from `OMOOSPACE.md`
- **AND** system ignores `Omoospace.yml` or `Omoospace.yaml` if present

#### Scenario: Configuration is written to OMOOSPACE.md
- **WHEN** user modifies configuration (e.g., `omoospace.brief = "new brief"`)
- **AND** the active profile file is `OMOOSPACE.md`
- **THEN** system writes changes back to `OMOOSPACE.md` using frontmatter format
- **AND** system preserves any content outside frontmatter

#### Scenario: Configuration roundtrip
- **WHEN** user reads configuration from `OMOOSPACE.md`
- **AND** modifies a value
- **AND** writes the configuration back
- **THEN** the modified value is correctly persisted
- **AND** other configuration values remain unchanged