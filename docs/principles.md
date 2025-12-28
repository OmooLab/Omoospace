# Omoospace Principles

There are only 5 principles:

1. 2+2 Main folders

2. `Subspaces` is dynamic, organized by creation objectives

3. `Contents` is static, organized by resource types

4. Name everything clearly and plainly

5. `Omoospace.x` as workspace profile


## 1. 2+2 Main folders

- `Subspaces` Stores software project files

- `Contents` Stores imported or exported resource files (project files are also allowed)

- `References` Stores reference materials (optional)

- `Void` Stores temporary data (optional)

## 2. `Subspaces` is dynamic, organized by creation objectives

- Everything here is dynamic

  Folder structure can be adjusted arbitrarily, and files can be moved freely. Content in project files can be in a messy state: WIP, R&D, unorganized.

- Name files and folders based on creation objectives

  A creation objective refers to the purpose of the project file, such as "modeling Prop A", "rigging Character B", "editing Film Sequence 010", "testing Effect D", etc.

- Object names in creation objectives cannot be omitted

  You can omit action terms (e.g., modeling, editing), but must never omit object names (e.g., character names, sequence numbers). For example, for the objective "Rigging Skeleton", you can write `Skeleton`, but cannot only write `Rigging` (even if it is in a folder named `Skeleton`).

## 3. `Contents` is static, organized by resource types

- Everything here is static

  It is not recommended to adjust the folder structure once set. Do not move files arbitrarily. If adjustment is absolutely necessary, use copy to ensure that filepath will not be lost.

- Name folders by resource types

  e.g., `Models`, `Images`, `Videos`, for quick access to resources.

- Save a copy of the project file here when its content is to be referenced
  
  For finalized project files whose content will be referenced by other project files, save a copy to Contents. This prevents dynamic, unorganized updates from affecting dependent files.

## 4. Name everything clearly and plainly

- Use language understandable to both yourself and the team for naming

- Use universal and easy-to-understand expressions for naming, avoid abbreviations and codes

- For duplicate names, add context with prefixes (connected by `_`) and modifiers with suffixes (connected by `.`)

- Use consistent expressions to describe the same thing

- Avoid special characters and spaces

## 5. `Omoospace.x` as workspace profile

Record project profile in any format you prefer. You can use .md, .yml or any document format, but we agree that the file name must be Omoospace to ensure it can be recognized as the workspace root.

Our library supports .yml format as follows:

```YAML
name: Omoospace's name
description: Omoospace's description
creators: # All creators/creation teams
  - name: Creator/team name
    email: Creator/team email
    role: Creator/team role in the project
    website: Creator/team website
softwares: # Software used
  - name: Software name
    version: Software version
    plugins: # Plugins used
      - name: Plugin name
        version: Plugin version
works: # All final deliverables
  - name: Deliverable name
    items: 
      - Relative path of the deliverable file/folder under Contents
```