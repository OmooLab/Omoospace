# Why Omoospace?

Any work with even a little complexity usually involves more than one file. When there are too many files, you need folders to organize them. A good folder structure helps you revisit and understand the project later. So how should you design it?

## Points to Consider

### Common Ground Across Workflows

Files in all creative workflows can be divided into two main types:

- **Resource files**: Images, audio, video, models, and other files that are imported or referenced.
- **Source files**: Files in software-specific formats that you work on (your working files).

Additionally, all workflows can be abstracted into a cycle:

```
Resource → Production → Resource → Production → Resource → ...
```

### Software-native Solutions Are Incompatible

Most software that uses external resources has its own way to collect or pack assets, such as:

- After Effects: [Collect Files](https://helpx.adobe.com/after-effects/using/automated-rendering-network-rendering.html)
- Blender: [Pack Resources](https://docs.blender.org/manual/en/latest/files/blend/packed_data.html#pack-resources)
- Cinema 4D: [Save Project with Assets](https://help.maxon.net/c4d/en-us/#html/5595.html#PLUGIN_CMD_12255)

Some software also helps you create project folders, such as:

- Maya: [Set a Project](https://help.autodesk.com/view/MAYAUL/2024/ENU/?guid=GUID-D5CA162A-0956-49C6-9FAC-2F73DCF03409)
- Houdini: [$JOB](https://www.sidefx.com/docs/houdini/basics/project.html)

These features are useful, but each software organizes files differently. This makes it hard to collaborate across multiple tools.


### You Need a Place to Record Information

You need a place to record:

- Software versions used
- Extensions used
- Team members and their roles
- Project description, client information, etc.


### Keep It Maintainable, But Respect Laziness

Few people can maintain a very complex folder structure, and even fewer want to write lots of comments. So it’s important to make the project “self-explanatory” with minimal effort. Here are some ways to save time:

- **Use filenames as comments**  
    Not every file can have a written description, so the filename itself should be clear and plain.
- **Use prefixes and suffixes to add meaning**. For example:
    - `Sc010_` as a scene context prefix
    - `.v001` as a version suffix
    - `.480p` as a resolution suffix
    - `.low` as a low-poly suffix
- **Use consistent output paths**. For example:
    - Render outputs go to `Renders`
    - Video exports go to `Videos`
- **Accept mess for unimportant files**  
    f a file isn’t important, you don’t need to organize it strictly. But if it is important, don’t be too casual—your future self will thank you 🥲.


### The Conflict: Flexibility vs Stability

If folders are too flexible, references break. If they are too fixed, the structure becomes rigid. Consider this example:

```bash
ProjectRoot/ 
├── Prop01/ 
│   ├── Prop01.blend      # Resource file (referenced by others) 
│   ╰── Prop01.WIP.blend  # Source file (work in progress) 
```

Later, you may want to move `Prop01/` into an `Assets/` folder. But moving it will break all references to `Prop01.blend`. To avoid this, you would have to plan the final structure from the very beginning.

Is there a way to have both flexibility and stability? To start simple and grow the structure as the project expands—without breaking references?



## Omoospace Principles

No single software can cover all workflows, and workflows keep changing with new technology. We need a unified way to guide how files are stored on disk. That’s why Omoospace was created.

### Core Idea: Separate Resource Files and Source Files

To solve the flexibility/stability conflict, we ask:

- Who needs to be stable? **Resource files**
- And who needs to be flexible? **Source files**

If they are mixed together, conflicts are inevitable:

- Prioritizing stability makes the structure rigid
- Prioritizing flexibility breaks references

So they should be stored separately. This is the core idea of Omoospace.

### Omoospace Is a "Guide", Not a "Strict Rulebook"

Omoospace does not enforce a specific folder structure, and it is not a management tool (though tools can help). It is more like a set of principles that gives you a direction when you’re unsure how to organize your files.

Omoospace is simple. It has only four rules: [Omoospace Principles](principles.md).