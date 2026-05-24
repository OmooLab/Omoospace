# Omoospace

![overview](assets/overview.png)

Omoospace is a universal folder structure guideline for creative projects. Its goals are **universality, flexibility, and semantic clarity**. It works for complex projects and team collaboration, as well as simple projects and individual work. [Why Omoospace?](why.md)


## Getting Started

### New Project

1. Create a new folder as the project root.
2. Create `OMOOSPACE.md` in the root.
3. Create `contents/` in the root and put your resource files in it.
4. (Optional) Create `subspaces/` in the root and put your source files in it.
5. (Optional) Add other folders as needed and place the corresponding file types in them.

### Existing Project

Create and edit `OMOOSPACE.md` in the project root.

```YAML
---
contents_dir: <resource_folder_name> # e.g. assets
subspaces_dir: <source_folder_name> # e.g. sources
---

# Project Name

...

```

## Command Line Tool

### Install uv and tool

[https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

```bash
uv tool install omoospace[cli]
```

### New Project

```bash
omoos create <Name>
```

### Existing Project

```bash
cd <project folder>
omoos init
```