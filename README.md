# Omoospace Docs

# Omoospace

Omoospace is a scalable directory structure solution for digital creation works. In order to follow omoospace rules easily, we provide shell commands, including creating new omoospace, shipping package, adding subspace, etc.

[What is "Omoospace", how does it rule all your creation files?](https://www.notion.so/Omoospace-5eb8e068eb8445aabb7ae03b0d034724?pvs=21)

# Quick Start

### **Install Omoospace Cli**

Run the following command to install the dependencies:

```bash
pip install omoospace
```

Check if omoospace cli is installed correctly.

```bash
omoospace --help
```

### **Create New Omoospace**

For creating new omoospace, run the following command:

```bash
omoospcase create
```

Finish the setup wizard.

```bash
? Enter Omoospace name my project
? Choose a template Asset
? A brief of the Omoospace An Omoospace for creation works
╭──────────────────────── Create Omoospace Form ─────────────────────────╮
│                                                                        │
│   Name                                                                 │
│   my project (path\to\MyProject)                                       │
│                                                                        │
│   Description                                                          │
│   An Omoospace for creation works                                      │
│                                                                        │
│                                                                        │
╰────────────────────────────────────────────────────────────────────────╯

? Confirm Yes
Current working at 🛠️  my project 
(path\to\MyProject).
```

<aside>
✅ Notes that the name of your omoospace “my project” is converted to PascalCase Style.

</aside>

The new created omoospace directory structure is simple:

```python
MyProject # Omoospace root directory.
|-- Contents # Directory of all kinds of digital contents except sourece file.
|-- ExternalData # Directory of data from external sources.
|-- References # Directory of reference files.
|-- SourceFiles # Directory of sourece files that saved working process.
|   `-- Void # Void subspace for RnD, Testing, Workbench, etc.
|-- StagedData # Directory of intermediate data, temp files, etc.
`-- Omoospace.yml # Omoospace info, like its name, creators, works etc.
```

If you want more complex subdirs, you can add them manually or choose other templates.

### **Add Subspace Directory**

According to the omoospace rules, your source file of DCC should be placed in `SourceFiles/` or any subspace directory. to add a new subspace, run the following command at omoospace root directory:

```bash
omoospcase add subspace
```

Finish the setup wizard.

```bash
$ poetry run omoospace add subspace
Current working at 🛠️  my project
(path\to\MyProject).
? Enter subspace name my model
? Enter subspace dstination directory MyProject\SourceFiles

New Subspace route will be:
(Root) > MyModel

? Confirm Yes
```

It creates subspace directory named “MyModel” with `.subspace` file in it.

```python
|-- SourceFiles
|   `-- MyModel
|       `-- .subspace # The marker of subspace.
```

Now, you can save all source files that relative to “MyModel” like below:

```python
|-- SourceFiles
|   `-- MyModel
|       |-- ModelPart.blend # The complex part of model that prepared separately.
|       |-- MyModel.blend # The main file of "MyModel" for shading, riging, lookdev, etc.
|       |-- MyModel.spp # The source file of Substance 3D Painter.
|       |-- MyModel.zpr # The project file of Zbrush.
|       `-- .subspace # The marker of subspace.
```

<aside>
✅ Notes that model’s textures file is not saved here, but in Contents.

</aside>

### Export Package

An omoospace package is a data package for sharing. to export a OmooCargo, run the following command at omoospace root directory:

```python
omoospcase export
```

Finish the setup wizard.

```bash
Current working at 🛠️  my project
(C:\Users\manan\Codes\omoospace\MyProject).
? Enter the item path or path pattern MyProject\SourceFiles
╭────── Pending ──────╮    ╭──── Checked ────╮
│                     │    │                 │
│    ? SourceFiles    │ => │                 │
│                     │    │                 │
╰─────────────────────╯    ╰─────────────────╯
? Check if the items on left are wanted Yes
╭──── Pending ────╮    ╭────── Checked ──────╮
│                 │    │                     │
│                 │ => │    √ SourceFiles    │
│                 │    │                     │
╰─────────────────╯    ╰─────────────────────╯
```

```bash
? Enter the item path or path pattern MyProject
? Name this package my project
? Enter a brief description of this package An omoospace package for shar 
ing
? Enter the verison of this package 0.1.0
╭───────────────────────── Export Package Form ──────────────────────────╮
│                                                                        │
│   Name                                                                 │
│   my project                                                           │
│   (C:\Users\manan\Codes\omoospace\MyProject\StagedData\Packages\MyP…   │
│                                                                        │
│   Description                                                          │
│   An omoospace package for sharing                                     │
│                                                                        │
│   Version                                                              │
│   0.1.0                                                                │
│                                                                        │
│   Items                                                                │
│   ╭─────────────┬──────────────────────────────────────────────────╮   │
│   │ Name        │ Path                                             │   │
│   ├─────────────┼──────────────────────────────────────────────────┤   │
│   │ SourceFiles │ C:\Users\manan\Codes\omoospace\MyProject\Source… │   │
│   ╰─────────────┴──────────────────────────────────────────────────╯   │
│                                                                        │
│                                                                        │
╰────────────────────────────────────────────────────────────────────────╯
? Sure Yes

C:\Users\manan\Codes\omoospace\MyProject\SourceFiles
C:\Users\manan\Codes\omoospace\MyProject\StagedData\Packages\MyProject\Sou
rceFiles
Processing... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:00:00       
Successfully export! 📦
```

After that, a package directory will create in `StageData/Packages/`

```python
|-- StageData
|   `-- Packages
|       `-- MyAsset # The root directory of OmooCargo "MyAsset"
|           |-- Contents # Where contains the model file.
|           |-- README.md # OmooCargo's doc file.
|           `-- OmooCargo.yml # OmooCargo's info, like its name, creators, etc.
```

Now you can share the package directory any way you like, attaching to email, upload to cloud, publish to GitHub etc.

### Import Package

Importing is easy, run the following command at omoospace root directory:

```python
omoospcase import ~/Downloads/MyAsset.zip
```

After that, a package directory will create in `ExternalData/`

```python
|-- ExternalData
|   `-- MyAsset
|       |-- Contents
|       |-- README.md
|       `-- Package.yml
```

Now you can open the needed file from “MyAsset” in your software.

### Switch Omoospace

```python
omoospcase to Projects/MyProject
```

If not found in directory, choose from recent.

```bash
No omoospace detected in 'Projects/MyProject'
? Choose one from recent
❯ C:\Projects\ProjectA
  C:\Projects\ProjectB
  C:\Projects\ProjectC
```

# To Do

- Moving subspace and all its files from space structure tree node to another node.
- A more interactive and visual interface for managing omoospace.