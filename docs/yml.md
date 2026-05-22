# OMOOSPACE.md

## 简述

项目的概述

```markdown
---
description: <简述项目>
---
```

例如

```markdown
---
description: 一个超厉害的IP项目
---
```


## 主文件夹指定

通过设置文件夹名，可以不改变原路径，又能让结构符合 Omoospace。还可以兼容其他项目的固定文件夹名，比如 Unity 中资产文件夹名为 `Assets/`，Unreal 中为 `Content/`

```markdown
---
contents_dir: <资源型文件夹名>
subspaces_dir: <制作型文件夹名>
---
```

例如

```markdown
---
contents_dir: Assets          #兼容 Unity 项目
subspaces_dir: ProjectFiles
---
```


## 忽略列表

不被当作 Subspace 的文件、文件夹

```markdown
---
ignore:
  - <忽略规则>
---
```

例如

```markdown
---
ignore:
  - Short02
  - Short03/Prop01.*
---
```


## 记录列表

```markdown
---
notes:
  <记录对象>: <记录内容>
---
```

例如

```markdown
---
notes:
  客户: 腾讯爸爸
---
```


## 主创列表

```markdown
---
makers:
  <个人/团队名>: <邮箱>
---
```

或

```markdown
---
makers:
  <个人/团队名>:
    email: <邮箱>
    website: <网站/社交账号>
---
```

例如

```markdown
---
makers:
  马南001: manan001@example.com
  马南002:
    email: manan002@example.com
  偶魔数字:
    email: studio@omoolab.xyz
    website: https://www.omoolab.xyz
---
```



## 工具列表

```markdown
---
tools:
  <工具/软件名>: <版本>
---
```

或

```markdown
---
tools:
  <工具/软件名>:
    version: <版本>
    website: <官网>
    extensions:
      - <插件>
      - <插件>
---
```

例如

```markdown
---
tools:
  Houdini: 20.0
  DaVinciResolve:
    version: 20.5
  Blender:
    version: 4.2.0
    website: https://www.blender.org
    extensions:
      - Omoospace
      - BioxelNodes
---
```


## 作品列表

```markdown
---
works:
  <作品名>: <contents文件夹的相对路径>
---
```

或

```markdown
---
works:
  <作品名>:
    description: <简述作品>
    version: "0.1.0"
    contents:
      - <contents文件夹的相对路径>
    contributions:
      <角色/做了什么>:
        - <个人/团队名>
---
```

例如

```markdown
---
works:
  超厉害道具01: models/道具01.glb
  超厉害道具02:
    - models/道具02/道具02.fbx
    - models/道具02/Textures
  超厉害短片01:
    description: 一个超厉害的IP动画短片
    version: "1.0.0"
    contents:
      - videos/动画短片01.mp4
      - images/动画短片01_封面.png
    contributions:
      模型师:
        - 马南003
      动画师: [马南002, 马南003]
      导演: 马南001
---
```