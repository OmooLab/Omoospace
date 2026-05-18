# Terms
## Subspace

An **objective** is the purpose of your work (obviously 😄). To achieve a big objective, you usually need many smaller objectives. But objectives are abstract—they only become real through concrete source files or folders. These files and folders are called **subspaces**.

**So the best way to name a subspace is to use its objective.**


## Pathname

```bash
├── subspaces/
│   ╰── Short01/
│       ├── Assets/
│       │   ├── CharA/
│       │   │   ├── CharA.zbr
│       │   │   ├── CharA.zbr
│       │   │   ├── CharA.spp
│       │   │   ├── CharA.blend
│       │   │   ╰── CharA.v001.blend
│       │   ╰── CharB.blend
│       ├── Sc010.blend
│       ╰── Sc020.blend
```

The folder structure clearly shows multi‑level objectives. From each file, we can see:

| Subspace         | Objective               | Path                     |
| ---------------- | ----------------------- | ------------------------ |
| Short01/         | Make short film Short01 | Short01                  |
| Assets/          | Prepare assets          | Short01 / Assets         |
| CharA/           | Prepare character CharA | Short01 / Assets / CharA |
| CharA.zbr        | Sculpt CharA            | Short01 / Assets / CharA |
| CharA.spp        | Paint CharA’s materials | Short01 / Assets / CharA |
| CharA.blend      | Rig CharA               | Short01 / Assets / CharA |
| CharA.v001.blend | Backup                  | Short01 / Assets / CharA |
| CharB.blend      | Prepare character CharB | Short01 / Assets / CharB |
| Sc010.blend      | Scene 010               | Short01 / Sc010          |
| Sc020.blend      | Scene 020               | Short01 / Sc020          |

Multi‑level objectives ordered from largest to smallest form the **subspace path**.  

A name generated from this path is called a **pathname**.

For example:

- `Short01/Sc010.blend` → pathname is `Short01_Sc010`
- `Short02/Sc010.blend` → pathname is `Short02_Sc010`

**Pathnames are used to generate meaningful, non‑conflicting export paths.**


## Objective Tree

If we combine all these paths, we get a tree structure called an **objective tree**.

You can also create the same objective tree using prefixes instead of folders:

```bash
├── subspaces
│   ├── Short01_Assets_CharA.zbr
│   ├── Short01_Assets_CharA.spp
│   ├── Short01_Assets_CharA.blend
│   ├── Short01_Assets_CharA.v001.blend
│   ├── Short01_Assets_CharB.blend
│   ├── Short01_Seq010.blend
│   ╰── Short01_Seq020.blend
```

You don’t even need prefixes like `Short01_` or `Short01_Assets_`, and you don’t need folders. You can just use `Seq010.blend` or `CharA.blend`.

**Folders and prefixes are only needed when you have naming conflicts or too many files. You can keep everything flat if you want.**