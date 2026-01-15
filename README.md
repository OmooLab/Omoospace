[中文文档](https://wcn96x0h20lt.feishu.cn/wiki/TAduwcqV3izhJ2kM3VpcZBW0n1d)

# Omoospace
![overview](docs/assets/overview.png)

Omoospace is a set of principles for building folder structures for creative work. Its goals are **universality, flexibility, and semantic clarity**. It works for complex projects and team collaboration, as well as simple projects and individual work. [Why Omoospace?](https://omoolab.github.io/Omoospace/latest/why)


## Getting Started

### New Project

1. Create a new folder as the project root.
2. Create `Omoospace.yml` in the root.
3. Create `Contents/` in the root and put your resource files in it.
4. (Optional) Create `Subspaces/` in the root and put your source files in it.
5. (Optional) Add other folders as needed and place the corresponding file types in them.


### Existing Project

1. Create `Omoospace.yml` in the project root.
2. Edit `Omoospace.yml` and add:
    ```YAML
    contents_dir: <resource_folder_name>
    ```
    Example:
    ```YAML
    contents_dir: Assets
    ```

3. (Optional) Edit `Omoospace.yml` and add:
    ```YAML
    subspaces_dir: <source_folder_name>
    ```
    Example:
    ```YAML
    subspaces_dir: ProjectFiles
    ```


## Command Line Tool

### Install uv

[https://docs.astral.sh/uv/getting-started/installation/](https://docs.astral.sh/uv/getting-started/installation/)

### New Project

```bash
uvx omoospace create <Name>
```

### Existing Project

```bash
cd <project folder>
uvx omoospace init
```