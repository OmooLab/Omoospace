# CLI

## 安装 uv 和小工具

https://docs.astral.sh/uv/getting-started/installation/

```Bash
uv tool install omoospace[cli]
```

## 新建项目

```Bash
omoos create <Name>
```

## 已有项目

```Bash
cd <project folder>
omoos init
```

## init 命令

```Bash
omoos init
```

## 属性命令

打印或设置 Omoospace 属性：

```Bash
omoos subspaces-dir          # 打印 subspaces 目录路径
omoos subspaces-dir Projects # 设置 subspaces 目录为 Projects
omoos contents-dir           # 打印 contents 目录路径
omoos contents-dir Assets    # 设置 contents 目录为 Assets
omoos name                   # 打印项目名
omoos description            # 打印简介
omoos root-dir               # 打印根目录
```

## create 命令

```Bash
omoos create "动画短片01" --description "一个神秘的项目" --contents contents --subspaces subspaces
```

## Claude Code Commands

安装 init 后可使用：

```Bash
omoos:lint    # 检查命名规范、文件放置、frontmatter
omoos:setup   # 分析现有结构，提议迁移到 omoospace
```