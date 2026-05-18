## ADDED Requirements

### Requirement: Support .yaml file extension

The system SHALL support `.yaml` extension as an alternative to `.yml` for configuration files. Both extensions SHALL be treated identically during file detection and loading.

#### Scenario: Detect .yaml configuration file
- **WHEN** Omoospace looks for configuration files
- **THEN** it SHALL detect files matching `Omoospace.yaml`
- **AND** treat them the same as `Omoospace.yml`

#### Scenario: .yaml file takes priority when .yml also exists
- **WHEN** both `Omoospace.yml` and `Omoospace.yaml` exist in root directory
- **AND** no `OMOOSPACE.md` is present
- **THEN** system SHALL load from `Omoospace.yml` (first in alphabetical order)
- **AND** log a warning about multiple config files

#### Scenario: New project with .yaml extension
- **WHEN** `create_omoospace` is called with default settings
- **THEN** system creates `OMOOSPACE.md` as primary config
- **AND** does not create `.yaml` or `.yml` files by default