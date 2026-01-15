# Omoospace.yml

## Brief

```YAML
brief: <Project description>
```

## Notes

```YAML
notes:
  <Record name>: <Record value>
```

Example:

```YAML
notes:
  Client: Tencent
```

## Makers

```YAML
makers:
  <Name>: <Email>
```

or

```YAML
makers:
  <Name>:
    email: <Email>
    website: <Website/social>
```

Example:

```YAML
makers:
  MaNan001: manan001@example.com
  MaNan002:
    email: manan002@example.com
  OmooLab:
    email: studio@omoolab.xyz
    website: https://www.omoolab.xyz
```

## Tools

```YAML
tools:
  <Tool name>: <Version>
```

or

```YAML
tools:
  <Tool name>:
    version: <Version>
    website: <Website>
    extensions:
      - <Addon/plugin>
      - <Addon/plugin>
```

Example:

```YAML
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
```

## Works

```YAML
works:
  <Work name>:
    - <Relative path under Contents>
```

or

```YAML
works:
  <Work name>:
    brief: <Work description>
    version: <Version>
    contents:
      - <Relative path under Contents>
    contributions:
      <Role/what was done>:
        - <Name>
```

Example:

```YAML
works:
  AwesomeProp01: Models/Prop02.glb
  AwesomeProp02:
    - Models/Prop01/Prop01.fbx
    - Models/Prop01/Textures
  AwesomeShort01:
    brief: An awesome animated short.
    version: 1.0.0
    contents:
      - Videos/Short01.mp4
      - Images/Short01_Cover.png
    contributions:
      Modeler:
        - MaNan003
      Animator: [MaNan002, MaNan003]
      Director: MaNan001
```