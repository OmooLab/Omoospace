# What is omoospace?

Omoospace is a scalable directory structure solution for digital creation works. Its aim are universality, flexibility, and annotation. Not only for large projects and teamwork, but also for small projects and solo works. Whether it is a 3d modeling task or a series production, it all fits 😊.

## Overview

The rules are simple:

1. Naming everything with **PascalCase**.
2. 5 main directories:

    - `SourceFiles` stores source files of the software.
    - `Contents` stores digital content in common format.
    - `ExternalData` stores data from external sources.
    - `References` stores reference resources (optional).
    - `StagedData` stores temporary data (optional).

3. Subdirectories rules:

    - SourceFiles subdirectories are set by process names.
    - Contents subdirectories are set by content types.

4. Set **Subspaces** by filename prefix or subdirectory based on creation objects.
5. Write the project profile info into **Omoospace.yml**. Such as creators, software versions, etc.

![A diagram illustrating the structure of omoospace](assets/Untitled.png)

A diagram illustrating the structure of omoospace

## Omoospace Structure

### Subspace

**Subspace** is a sub-workspace based on creation objects, which is conducive to finding, sorting and understanding. Subspace can be nested, for example, an anime series project, each episode is a creation object, and under that object, multiple secondary objects can be set based on episode’s sequences, and each secondary object can continue to be split. Each object is a sub-workspace of the main workspace. **We call those sub-workspaces as "Subspace", and they are named after their objects.**

It is conceivable that the nested subspaces can generate a tree-like graph which presents the structure of the entire project, as shown in the figure below.

![Untitled](assets/Untitled%201.png)

So how to set subspace? And what is worth noting when setting subspaces?

#### Subspace can be set by filename prefix or subdirectory

Each namespace split by `_` is a subspace, for example:

```shell
Foo # (Root)
|-- SourceFiles
|   |-- AssetA.blend # (Root) > AssetA
|   |-- EP001.blend # (Root) > EP001
|   |-- EP001.prproj # (Root) > EP001
|   |-- EP002.blend # (Root) > EP002
|   |-- EP002.prproj # (Root) > EP002
|   |-- EP002_AssetB.blend # (Root) > EP002 > AssetB
|   |-- EP002_SQ010.blend # (Root) > EP002 > SQ010
|   `-- EP002_SQ020.blend # (Root) > EP002 > SQ020
```

Notes that one subspace may have multiple files to present them. We call those files **Subspace Entity**. And their parent subspaces form a route, we call them **Subspace Route**.

You can also use subdirectories instead of filename prefix. In order to distinguish **Subspace Directory** from ordinary directories, subspace directory must contain a marker file named `Subspace.yml`.

```shell
Foo # (Root)
|-- SourceFiles
|   |-- AssetA.blend # (Root) > AssetA
|   |-- EP001 # (Root) > EP001
|   |   |-- Subspace.yml # marker
|   |   |-- EP001.blend # (Root) > EP001
|   |   `-- EP001.prproj # (Root) > EP001
|   `-- EP002 # (Root) > FilmB
|       |-- Subspace.yml # marker
|       |-- AssetB.blend # (Root) > EP002 > AssetB
|       |-- EP002.blend # (Root) > EP002
|       |-- EP002.prproj # (Root) > EP002
|       |-- SQ010.blend # (Root) > EP002 > SQ010
|       `-- SQ020.blend # (Root) > EP002 > SQ020
```

Besides as marker file, `Subspace.yml` is also for noting. You can leave any comment in it.

```yaml
# Subspace.yml
Comments to this subspace.
```

Or more formal.

```yaml
# Subspace.yml
name: Subspace's name
comments: Comments to this subspace.
```

#### Filename prefix and subspace directory can be concatenated and overlap.

The subspace route of one entity is calculated by all its parent subspace directory and name prefix.

```shell
|-- SourceFiles
|   |-- EP001 # (Root) > EP001
|   |   |-- Subspace.yml
|   |   `-- SQ010_AssetA.blend # (Root) > EP001 > SQ010 > AssetA
```

If the entity name prefix contains its parent subspace name. They should overlap each other as much as possible, for example:

```shell
|-- SourceFiles
|   |-- EP001 # (Root) > EP001
|   |   |-- Subspace.yml
|   |   `-- EP001_SQ010_AssetA.blend # (Root) > EP001 > SQ010 > AssetA
```

```shell
|-- SourceFiles
|   |-- EP001_SQ010
|   |   |-- Subspace.yml
|   |   `-- EP001_SQ010_AssetA.blend # (Root) > EP001 > SQ010 > AssetA
```

!!! note

    In above example, subspace `EP001` has no entity to present itself. we call it **Phantom Subspace**

There is no strict rules of when to use concatenating or overlapping. It all up to user's decision. Creator should design the subspace name to fit the project needs.

### SourceFiles

It stores the source files of the software, or executable scripts, pipelines, etc.

`SourceFiles` stores processes, and `Contents` stores results. The former needs to be opened with specific software or executed by the program and need to be precomputed. The latter generally allows cross-software reading, and without any pre-computation.

For example, using Blender's geometry node for procedural modeling. The source file of blender should be placed in `SourceFiles`. However, in order to load the procedural model in Unity, it is necessary to export as a general format, such as .fbx, and the exported file should be placed in `Contents`.

#### Subdirectories by process name (optional)

Some optional process name:

```shell
# Film production processes
|-- SourceFiles
|   |-- PreProduction
|   |-- Production
|   `-- PostProduction
```

```shell
# Post-production subprocesses
|-- SourceFiles
|   |-- Compositing
|   |-- SoundEditing
|   `-- VideoEditing
```

```shell
# 3D modeling processes
|-- SourceFiles
|   |-- Modeling
|   |-- Texturing
|   |-- Rendering
|   `-- Shading
```

```shell
# Processes sorted by number
|-- SourceFiles
|   |-- 001-Preprocessing
|   |-- 002-Scuplting
|   |-- 003-Texturing
|   |-- 004-Animation
|   |-- 005-Lighting
|   `-- 006-Typography
```

Process directories and subspace directories can be mixed.

```shell
<SeriesTitle> # (Root)
|-- SourceFiles
|   |-- PreProduction
|   |   `-- <ModelName> # (Root) > <ModelName>
|   `-- <Episode> # (Root) > <Episode>
|       |-- Subspace.yml
|       |-- Production
|       `-- PostProduction
```

Custom process subdirectories should fit your own workflow. But be aware of the following rules:

-   Pay attention to the naming style. It should be a gerund for the process. For example, not **Models** but **Modeling**, not **Scenes** but **SceneBuilding**. In this way, the **Process** is emphasized, not the **Result**.
-   You can adjust the process subdirectories freely as the project expands.

#### Put source files without creation object under Void (optional)

Most source files have its object, such as rendering images or export a 3D model. However, some source files are not used as the main process and have no certain object, but have storage needs. We put such source files in a special subspace called **Void**, which don’t need `Subspace.yml`.

!!! note

    Any subspaces in **Void** are also **Void Subspace**.

Void subspace can be in filename prefix or as directory.

```shell
|-- SourceFiles
|   |-- BeatingHeart
|   |   `-- Void_HowToBeat.hip
|   |-- Void_RnD_MetaBall.blend
|   |-- Void
|   |   `-- MaNan.hip
```

!!! note

    Although the source files under void subspace have no creation objects, they still allow outputing. However their outputs are not rigorous and necessary, but somewhat experimental and temporary. For example, `Void/HeartBeating.blend` can still render `Void_HeartBeating.0001.png`. The prefix `Void` indicates the results are experimental.

### Contents

It stores digital content in a common format, whether it is a work result or a resource, whether it is an internal or external. All files in here are organized to rules.

#### Subdirectories by content type (optional)

Some optional content type:

```shell
# For modeling propose
|-- Contents
|   |-- Images
|   |-- Materials
|   |-- Models
|   `-- Renders
```

```shell
# For short video production propose
|-- Contents
|   |-- Audios
|   |-- Dynamics
|   |-- Images
|   |-- Materials
|   |-- Models
|   |-- Renders
|   `-- Videos
```

```shell
# For film production propose
|-- Contents
|   |-- Audios
|   |-- Dynamics
|   |-- Fonts
|   |-- HDAs # Houdini Digital Assets
|   |-- Images
|   |-- Materials
|   |-- Models
|   |   |-- Characters
|   |   |-- Nature
|   |   |-- Props
|   |   `-- ...
|   |-- Presets
|   |-- Renders
|   |-- Scenes
|   |-- ScientificData
|   |-- Scripts
|   |-- Settings
|   |-- Shaders
|   `-- Videos
```

Custom type subdirectories should fit your own workflow. But be aware of the following rules:

-   Pay attention to the naming style. Should be the plural of the content type noun.
-   To avoid confusion and misplacement, try to merge similar content types into one.
-   It is not recommended to set multi-level subdirectories, nor to adjust the type subdirectories as the project expands. Because content files, always as an IO path, need stability.

#### The output of source file is named after its entire subspace route.

There is no subspace directory in `Contents`. but use subspace route as file namespaces.

![Untitled](assets/Untitled%202.png)

Observe their correspondence through specific examples.

```shell
BloodCellAndVessel
|-- Contents
|   |-- Models
|   |   |-- BloodCells_Platelet.fbx
|   |   |-- BloodCells_RBC.fbx
|   |   `-- BloodCells_WBC.fbx
|   |-- Images
|   |   |-- BloodCellAndVessel.png
|   |   `-- SkyHDRI.exr
|   |-- Renders
|   |   `-- BloodCellAndVessel
|   |       |-- BloodCellAndVessel.0001.png
|   |       `-- ...
|   `-- Videos
|       `-- BloodCellAndVessel.mp4
|-- SourceFiles
|   |-- BloodCellAndVessel.blend
|   |-- BloodCellAndVessel.pptx
|   `-- BloodCells.blend
```

![Untitled](assets/Untitled%203.png)

More complex example:

```shell
HowOrganWorks
|-- Contents
|   |-- Models
|   |   |-- Heart
|   |   |   |-- Heart.usd
|   |   |   `-- Textures
|   |   `-- BeatingHeart_CuttedHeart
|   |       |-- BeatingHeart_CuttedHeart.usd
|   |       `-- Textures
|   |-- Dynamics
|   |   |-- BeatingHeart_SQ010_Fog.vdb
|   |   `-- BeatingHeart_SQ010_Beating.abc
|   |-- Images
|   |   |-- BeatingHeart_SQ010_VisualEffect
|   |   |   |-- BeatingHeart_SQ010_VisualEffect.1001.png
|   |   |   `-- ...
|   |-- Renders
|   |   |-- BeatingHeart_SQ010_SH0100
|   |   |   |-- BeatingHeart_SQ010_SH0100.1001.png
|   |   |   `-- ...
|   |   `-- BeatingHeart_SQ010_SH0200
|   |       |-- BeatingHeart_SQ010_SH0200.1001.png
|   |       `-- ...
|   |-- Videos
|   |   `-- BeatingHeart.mp4
|-- SourceFiles
|   |-- Modeling
|   |   `-- Heart
|   |       |-- Subspace.yml
|   |       |-- Heart.blend
|   |       |-- Heart.spp
|   |       `-- Valves.blend
|   |-- BeatingHeart
|   |   |-- Subspace.yml
|   |   |-- CuttedHeart
|   |   |   |-- Subspace.yml
|   |   |   |-- CuttedHeart.blend
|   |   |   |-- CuttedHeart.zpr
|   |   |   `-- Valves.blend
|   |   |-- BeatingHeart.prproj
|   |   `-- SQ010
|   |       |-- Subspace.yml
|   |       |-- Beating.hip
|   |       |-- Fog.EmberGen
|   |       |-- VisualEffect.aep
|   |       `-- SQ010.blend
```

![Untitled](assets/Untitled%204.png)

### ExternalData

It stores all data files from external sources. The “external” here means that it is not generated by the creator of this Omoospace, and not produced within this Omoospace, either. The most common usage of `ExternalData` is to store resources from network. You can also put your own 3D assets' library directory into `ExternalData` as a soft link.

#### No need to follow the naming rules, do not set any type subdirectories

Just keep its original file structure and naming style. For example:

```shell
|-- ExternalData
|   |-- www.models.com_CT_Scanner
|   |   |-- CT_Scanner.fbx
|   |   `-- tex
|   |-- textures_pack-4k
|   |   |-- wood
|   |   `-- metal
|   |-- MyResources
|   |   |-- Textures
|   |   |-- Materials
|   |   `-- Models
```

!!! note

    Do not put files at root directory of `ExternalData`, always under subdirectory.

#### It is not the only repository for all external data

`Contents` and `SourceFiles` also store external data. However, compared with `ExternalData`, they are stricter, all files need to be categorized and renamed properly. Meanwhile, `ExternalData` is a storage place that allows users to shipping data freely.

For external source data, if it has been stored in `Contents` | `SourceFiles`, it has no need to be stored in `ExternalData` again. For example, a HDRI downloaded from the PolyHaven, as long as it is renamed to PascalCase style, it could be directly put under `Contents`.

!!! note

    Categorizing, renaming are not fun works, so it is recommended to store external source data directly into `ExternalData` unless you can ensure files under `Contents` | `SourceFiles` strict to the rules.

#### It stores omoospace packages

Package is an Omoospace data package designed for sharing. The loaded Package will be stored in `ExternalData`. The source file can directly reference the file here.

```shell
|-- ExternalData
|   |-- BloodCells # Package
|   |   |-- Package.yml # Package info
|   |   |-- Contents
|   |   |   `-- Models
|   |   |       `-- RedBooldCell.fbx
|   |   `-- SourceFiles
|   |       `-- RedBooldCell.blend
```

### References

It stores PureRef, Figma, Paper PDF, Storyboard. Although they will not be used directly by the source file, but still need to be saved. Put them here.

!!! tip

    If it is figma online, put the link as file.

### StagedData

It stores any software-generated data that can be rebuilt after deletion, such as temporary files, caches, software bridging files, etc. There is no need to browser `StagedData` unless necessary.

Directory structure automatically generated by software.

### Omoospace.yml

It stores profile info such as creators, software versions, etc.

<!-- prettier-ignore -->
```yaml
name: Omoospace's name
description: A brief of this Omoospace (Optional)
creators: # Creator list of this Omoospace
  - name: Creator's name
    email: Creator's email (Optional)
    role: Creator's role in this Omoospace (Optional)
    website: Creator's website (Optional)
softwares: # Software list of this Omoospace
  - name: Software's name
    version: Software's version
    plugins: # Plugins list of this Omoospace (Optional)
      - name: Plugin's name
        version: Plugin's version
works: # Work list of this Omoospace
  - name: Work's name
    path: Work's path under Contents
```

For example:

<!-- prettier-ignore -->
```yaml
name: my project
description: An Omoospace for creation works
creators:
  - name: manan
    email: icrdr2010@outlook.com
    website:
    role: Owner
softwares:
  - name: Blender
    version: 3.6.4
    plugins:
  - name: Zbrush
    version: 2023.2
    plugins:
  - name: Substance 3D Painter
    version: 9.0.0
    plugins:
works:
  - name: MyModel
    paths:
    - MyModel
```

## Omoospace Package

Inspired by Unity Package, Package is an Omoospace data package designed for sharing.

ExternalData acts like a Packages of Unity project, that storing data from other Omoospaces.

[Unity - Manual: Reusing Assets between Projects](https://docs.unity3d.com/2020.1/Documentation/Manual/HOWTO-exportpackage.html)

The internal structure of Package is part of its source Omoospace

```shell
<PackageName>
|-- Contents # (Optional)
|-- ExternalData # (Optional)
|-- References # (Optional)
|-- SourceFiles # (Optional)
|-- StagedData # (Optional)
|-- README.md
`-- Package.yml # Package info
```

<!-- prettier-ignore -->
```yaml
# Package.yml
name: Package's name
version: Package's version
description: A brief of this Package (Optional)
creators: # Creator list of this Package
  - name: Creator's name
    email: Creator's email (Optional)
    role: Creator's role in this Omoospace (Optional)
    website: Creator's website (Optional)
```

!!! note

    Once Package is exported, it has nothing to do with its source Omoospace

## Comparison with other software project structures

There are some common concepts to help understand.

| Omoospace     | Unity          | Unreal Engine                         |
| ------------- | -------------- | ------------------------------------- |
| Contents      | Assets         | Content                               |
| ExternalData  | Packages       |                                       |
| References    |                |                                       |
| SourceFiles   | Assets         | Source、Content                       |
| StagedData    | Temp           | Intermediate、Saved、DerivedDataCache |
| Omoospace.yml | PorjectSetting | Config                                |

## Q&A

-   **Q: Most directory structure solutions of CG work have no distinction between `Contents` and `SourceFiles`. Why Omoospace emphasize their differences ?**

    A: This is due to the different purposes of them. The content files, always as an IO path, need stability. So, `Contents` should be centralized, and its structure should be as flat as possible. Meanwhile, the source files, as entries of human operations, need accessible. People split their works by processes and objects, which are the best subdirectory rule of `SourceFiles`.
    Therefore, it is better to isolate the source files that store "processes" and the content files that stores "results".

-   **Q: Why `Contents` has no subspace directories?**

    The previous answer has explained the different purposes of `Contents` and `SourceFiles`. Although the `Contents` structure should be as flat as possible. But in order to avoid duplicate names, Subspace Prefixes are used. `SourceFiles`, on the other hand, sets up Subspace Directories for ease of finding.

-   **Q: Why does the Omoospace.yml field not using PascalCase style?**

    Because the official tool is written by shell. The field style should be snake_case.
