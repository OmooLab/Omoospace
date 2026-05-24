## ADDED Requirements

### Requirement: Parse frontmatter from markdown content
The frontmatter parser SHALL extract YAML metadata from markdown files using the pattern `---...---` delimiters.

#### Scenario: Standard frontmatter with metadata
- **WHEN** markdown content starts with `---...---` block containing valid YAML
- **THEN** parser returns metadata dict and body content (without frontmatter delimiters)

#### Scenario: No frontmatter in content
- **WHEN** markdown content has no `---` delimiters
- **THEN** parser returns empty dict and full content unchanged

#### Scenario: Empty frontmatter block
- **WHEN** markdown content has `---...---` but no YAML content
- **THEN** parser returns empty dict and content (without frontmatter delimiters)

#### Scenario: Frontmatter with YAML parse error
- **WHEN** markdown content has `---...---` block with invalid YAML syntax
- **THEN** parser raises `yaml.YAMLError` or returns empty dict (caller handles)

### Requirement: Serialize metadata to markdown with frontmatter
The frontmatter serializer SHALL create markdown content with YAML frontmatter delimiters.

#### Scenario: Serialize metadata with content
- **WHEN** metadata dict and body content are provided
- **THEN** output is formatted as `---\n<yaml>\n---\n<body>`

#### Scenario: Serialize empty metadata
- **WHEN** metadata dict is empty
- **THEN** serializer returns only body content without frontmatter delimiters

### Requirement: Preserve YAML formatting
The parser SHALL preserve quotes and formatting from the original frontmatter when possible.

#### Scenario: Preserve quoted strings
- **WHEN** frontmatter contains quoted strings like `key: "value"`
- **THEN** metadata dict preserves the quoted form when re-serialized