# Omoospace Principles

![overview](assets/overview.png)

There are only 4 rules, easy to remember:

1. Name everything in a clear, specific way
2. `Contents/` stores static resource files
3. `Subspaces/` stores dynamic source files
4. `Omoospace.*` rcords project information


## 1. Name everything in a clear, specific way

- **Avoid special characters and spaces.**  
    Only letters, numbers, underscores(`_`), periods(`.`), and hyphens(`-`) are allowed.

- **Use universal, easy-to-understand expressions for naming, avoid abbreviations and codes.**  
    Do not use incomprehensible abbreviations such as `BC`?, `TE`?.


- **Action terms can be omitted, but object names must not be.**  
    For example: `ModelProp01.blend` can be simplified to `Prop01.blend`, but never `Modeling.blend`; `TestWaterEffect.hip` cannot be `Test.hip`.


- **Use prefixes (separated by `_`) for context and suffixes (separated by `.`) for modifiers.**  
    For example: `Sc010_Anatomy_Skeleton.high.v001.blend` — `Sc010` and `Anatomy` are context prefixes; `.high` and `.v001` are modifiers. See more examples here: [How to use modifier suffixes?](how-to-add-suffixes.md)


## 2. `Contents/` stores static resource files

- **Stores referenced, imported, exported resource files and final deliverables.**   
    Examples: images, videos, audio effects, models, even source files, data files, etc.

- **Organize subfolders by resource type**

    ```bash
    ├── Contents/
    │   ├── Audios/       # Audio assets
    │   ├── Downloads/    # Files downloaded online
    │   ├── Dynamics/     # Various FX simulations
    │   ├── Images/       # Textures, image assets
    │   ├── Models/       # Models, animated models
    │   ├── Renders/      # Image sequences, rendered videos
    │   ├── Data/         # Reference data
    │   ╰── Videos/       # Final videos, video assets
    ```

    See more examples here: [How to set up folders?](how-to-setup-folders.md)

- **Do not easily adjust the folder structure or move files arbitrarily.**  
    If adjustments are necessary, use the copy method to avoid losing original references.

## 3. `Subspaces/` stores dynamic source files

- **Stores process-recorded source files and software-specific project files.**  
    For examples: .psd, .blend, .word, .ppt.

- **Organize files and subfolders by objectives**

    ```bash
    ├── Subspaces/
    │   ├── Assets/                  # (Prepare) Assets
    │   │   ├── Prop01.blend         # Latest version
    │   │   ╰── Prop01.v001.blend    # Backup version
    │   ╰── Sc010/                   # (Make) Scene 010
    │       ├── Sc010.prproj         # (Editing) Scene 010
    │       ├── Sc010.blend          # (Layout) Scene 010
    │       ╰── TestExplosion.blend  # Test Explosion Effect
    ```
    See more examples here: How to set up folders?
    > The `Subspaces/` folder is optional — source files can be placed directly in the root directory.



- **The folder structure can be adjusted arbitrarily, and files can be moved freely.**  
    Messy states are allowed here, including work-in-progress, debugging, pending verification, and unorganized files.

- **If a file needs to be referenced, save a copy to `Contents/.`**  
    Do not reference source files directly from each other to avoid dynamic, disorganized upstream changes affecting downstream files.

    ```bash
    ├── Contents/
    │   ╰── Models/
    │       ╰── **Prop01.blend**  # Referenced copy
    ├── Subspaces/
    │   ├── AssetPreparation/
    │   │   ╰── Prop01.blend      # Working file
    │   ╰── Scene010.blend        # File that needs references
    ```

    If `Scene010.blend` needs to reference `Prop01.blend`, copy `Prop01.blend` to `Contents/`. See details here: [How to back up copies?](how-to-backup.md)


## 4. `Omoospace.*` records project information

Use `Omoospace.*` to record overall project information. You can use any familiar document format (Markdown, TXT, Word, ...). 

For our tool, use `Omoospace.yml` (it can be an empty file, but it must exist — otherwise, our tool cannot recognize the workspace).

```YAML
# Omoospace.yml
brief: A great project.

notes:
  Client: A great company
  
makers:
  CreatorA: creatorA@example.com
  CreatorB: creatorB@example.com

tools:
  Blender: 4.2.0
  Houdini: 20.0.0

works:
  Work01:
    - Videos/Film01.mp4
    - Images/Film01_Cover.png
  Work02: Models/Prop01.glb
```

For more complex project information, see [Omoospace.yml](omoospace-yml.md)