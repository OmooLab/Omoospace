# OMOOSPACE.md

## Brief

```markdown
---
description: <Project description>
---
```

## Notes

```markdown
---
notes:
  <Record name>: <Record value>
---
```

Example:

```markdown
---
notes:
  Client: Tencent
---
```

## Makers

```markdown
---
makers:
  <Name>: <Email>
---
```

or

```markdown
---
makers:
  <Name>:
    email: <Email>
    website: <Website/social>
---
```

Example:

```markdown
---
makers:
  MaNan001: manan001@example.com
  MaNan002:
    email: manan002@example.com
  OmooLab:
    email: studio@omoolab.xyz
    website: https://www.omoolab.xyz
---
```

## Tools

```markdown
---
tools:
  <Tool name>: <Version>
---
```

or

```markdown
---
tools:
  <Tool name>:
    version: <Version>
    website: <Website>
    extensions:
      - <Addon/plugin>
      - <Addon/plugin>
---
```

Example:

```markdown
---
tools:
  Houdini: 20.0
  DaVinci Resolve:
    version: 20.5
  Blender:
    version: 5.0.0
    website: https://www.blender.org
    extensions:
      - Omoospace
      - BioxelNodes
---
```

## Works

```markdown
---
works:
  <Work name>: <Relative path under contents>
---
```

or

```markdown
---
works:
  <Work name>:
    description: <Work description>
    version: <Version>
    contents:
      - <Relative path under contents>
    contributions:
      <Role/what was done>:
        - <Name>
---
```

Example:

```markdown
---
works:
  AwesomeProp01: models/Prop02.glb
  AwesomeProp02:
    - models/Prop01/Prop01.fbx
    - models/Prop01/Textures
  AwesomeShort01:
    description: An awesome animated short.
    version: 1.0.0
    contents:
      - videos/Short01.mp4
      - images/Short01_Cover.png
    contributions:
      Modeler:
        - MaNan003
      Animator: [MaNan002, MaNan003]
      Director: MaNan001
---
```