import typer
from pathlib import Path
from InquirerPy import inquirer

from omoospace.functions import create_omoospace
from omoospace.omoospace import Omoospace
from omoospace.common import yaml
from omoospace.utils import Opath, normalize_name

# 主应用
app = typer.Typer(help="Omoospace CLI", no_args_is_help=True)

# 资源子命令组
subspace_app = typer.Typer(help="Subspace operations", no_args_is_help=True)
work_app = typer.Typer(help="Work operations", no_args_is_help=True)
tool_app = typer.Typer(help="tool operations", no_args_is_help=True)
maker_app = typer.Typer(help="maker operations", no_args_is_help=True)


def detect_omoospace_or_exit():
    try:
        return Omoospace(Path.cwd())
    except Exception as err:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


# -------------------------- 全局命令 --------------------------


@app.command()
def init():
    """
    Initialize current directory as an Omoospace.
    """
    cwd = Opath.cwd()
    # 1. Check if already an Omoospace
    try:
        Omoospace(cwd)
        typer.secho(
            "Current directory is already an Omoospace. Initialization skipped.",
            fg=typer.colors.GREEN,
        )
        return
    except Exception:
        pass

    # 3. 近似文件夹候选
    def find_candidates(names):
        return [
            p.name
            for p in cwd.iterdir()
            if p.is_dir() and p.name.lower() in [n.lower() for n in names]
        ]

    contents_candidates = find_candidates(
        [
            "Contents",
            "Content",
            "Assets",
            "Asset",
            "Resources",
            "Resource",
            "res",
            "dist",
            "public",
        ]
    )

    subspaces_candidates = find_candidates(
        [
            "Subspaces",
            "Subspace",
            "SourceFiles",
            "SourceFile",
            "Source File",
            "Source Files",
            "sources",
            "source",
            "src",
            "ProjectFiles",
            "ProjectFile",
            "Project Files",
            "Project File",
        ]
    )

    # 4. Select or create logic (single step, English, skip if exact match)
    def select_or_create(folder_type, candidates, default):
        # If exact match exists, use it directly
        if default in candidates:
            return default
        # If there are candidates, ask user to select or create new
        if candidates:
            choices = candidates + [f"Create new '{folder_type}'"]
            selected = inquirer.select(
                message=f"Select as {folder_type}, or create new:",
                choices=choices,
                default=choices[0],
            ).execute()

            if not selected.startswith("Create new"):
                return selected

        return inquirer.text(message=f"{folder_type}:", default=default).execute()

    brief = inquirer.text(message="Brief:", default="").execute()

    contents_dir = select_or_create("Contents Folder", contents_candidates, "Contents")
    subspaces_dir = select_or_create(
        "Subspaces Folder", subspaces_candidates, "Subspaces"
    )

    chinese_to_pinyin = inquirer.confirm(
        message="Convert Chinese to pinyin?", default=False
    ).execute()

    readme = inquirer.confirm(message="Add README.md?", default=True).execute()

    omoospace = create_omoospace(
        name=cwd.name,
        brief=brief,
        under=cwd.parent,
        chinese_to_pinyin=chinese_to_pinyin,
        contents_dir=contents_dir,
        subspaces_dir=subspaces_dir,
        readme=readme,
        reveal_in_explorer=True,
    )
    typer.secho(f"Omoospace created: {omoospace.root_dir}", fg=typer.colors.GREEN)


@app.command()
def create(name: str = typer.Argument(..., help="Omoospace name")):
    """Create a new omoospace."""
    brief = inquirer.text(message="Brief:", default="").execute()

    contents_dir = inquirer.text(
        message="Contents Folder:", default="Contents"
    ).execute()
    subspaces_dir = inquirer.text(
        message="Subspaces Folder:", default="Subspaces"
    ).execute()

    chinese_to_pinyin = inquirer.confirm(
        message="Convert Chinese to pinyin?", default=False
    ).execute()
    readme = inquirer.confirm(message="Add README.md?", default=True).execute()

    omoospace = create_omoospace(
        name=name,
        brief=brief,
        contents_dir=contents_dir,
        subspaces_dir=subspaces_dir,
        chinese_to_pinyin=chinese_to_pinyin,
        readme=readme,
        reveal_in_explorer=True,
    )
    typer.secho(f"Omoospace created: {omoospace.root_dir}", fg=typer.colors.GREEN)


@app.command()
def tree():
    """Print objective tree"""
    omoospace = detect_omoospace_or_exit()
    try:
        print(omoospace.objective_tree.format())
    except Exception as err:
        typer.secho(f"Print tree failed: {err}", fg=typer.colors.RED)


# -------------------------- Subspace 命令 --------------------------
@subspace_app.command("add")
def add_subspace(name: str = typer.Argument(..., help="Subspace name")):
    """Add a new subspace"""
    omoospace = detect_omoospace_or_exit()
    subspaces_dir = omoospace.subspaces_dir
    subdirs = [p for p in subspaces_dir.glob("**/") if p.is_dir()]
    subdirs = [str(p.relative_to(subspaces_dir)) for p in subdirs]
    if not subdirs:
        subdirs = ["."]
    parent_dir = inquirer.select(
        message="Under which directory:",
        choices=subdirs,
        default=".",
    ).execute()
    collect_children = inquirer.confirm(
        message="Auto collect related subspaces?", default=True
    ).execute()
    try:
        subs = omoospace.add_subspace(
            name=name,
            under=str(subspaces_dir / parent_dir) if parent_dir != "." else None,
            collect_children=collect_children,
            reveal_in_explorer=True,
        )
        typer.secho(f"Subspace {subs.pathname} added", fg=typer.colors.GREEN)
    except Exception as err:
        typer.secho(f"Add failed: {err}", fg=typer.colors.RED)


# -------------------------- Work 命令 --------------------------
@work_app.command("add")
def add_work(
    items: list[str] = typer.Argument(..., help="Content path(s) to Contents folder")
):
    """Add a new work"""
    omoospace = detect_omoospace_or_exit()
    contents = []

    for item in items:
        abs_path = Opath(item).resolve()
        rel_path = omoospace.contents_dir / item
        is_abs = omoospace.is_content(abs_path)
        is_rel = omoospace.is_content(rel_path)

        if not is_abs and not is_rel:
            typer.secho(f"Content not found: {item}", fg=typer.colors.RED)
            raise typer.Exit(1)

        content = str(abs_path.relative_to(omoospace.contents_dir)) if is_abs else item
        contents.append(content)

    name = inquirer.text(message="Name:", default="").execute()
    brief = inquirer.text(message="Brief:", default="").execute()
    name = name or contents[0].split("/")[-1].split(".")[0]

    work = {"name": name, "version": "0.1.0", "contents": contents}
    if brief:
        work["brief"] = brief

    work = omoospace.add_work(work)
    typer.secho(f"Work {work.name} added", fg=typer.colors.GREEN)


@work_app.command("list")
def list_work():
    """List all works in current omoospace"""
    omoospace = detect_omoospace_or_exit()
    works = omoospace.works
    if not works:
        typer.secho("No works found", fg=typer.colors.YELLOW)
        return
    typer.secho("Works:", fg=typer.colors.BLUE)

    for work in works:
        typer.echo(
            f"- {work.name}{f': v{work.version}' if work.version else ''}{f' ({work.brief})' if work.brief else ''}"
        )
        for idx, content in enumerate(work.contents, 1):
            if idx != len(work.contents):
                typer.echo(f"  ├── {content}")
            else:
                typer.echo(f"  ╰── {content}")
                typer.echo(f"")


# -------------------------- tool 命令 --------------------------
@tool_app.command("add")
def add_tool(name: str = typer.Argument(..., help="tool name")):
    """Add a new tool"""
    omoospace = detect_omoospace_or_exit()
    tool = {"name": name}
    version = inquirer.text(message="tool version:", default="").execute()
    website = inquirer.text(message="Website:", default="").execute()
    if version:
        tool["version"] = version
    if website:
        tool["website"] = website

    tool = omoospace.add_tool(tool)
    typer.secho(f"tool {tool.name} added", fg=typer.colors.GREEN)


@tool_app.command("list")
def list_tool():
    """List all tools in current omoospace"""
    omoospace = detect_omoospace_or_exit()
    tools = omoospace.tools
    if not tools:
        typer.secho("No tools found", fg=typer.colors.YELLOW)
        return
    typer.secho("Tools:", fg=typer.colors.BLUE)
    for tool in tools:
        typer.echo(
            f"- {tool.name}{f': v{tool.version}' if tool.version else ''}{f' ({tool.website})' if tool.website else ''}"
        )


# -------------------------- maker 命令 --------------------------
@maker_app.command("add")
def add_maker(
    name: str = typer.Argument(..., help="maker name"),
):
    """Add a new maker"""
    omoospace = detect_omoospace_or_exit()
    email = inquirer.text(message="Email:", default="").execute()
    website = inquirer.text(message="Website:", default="").execute()
    maker = {"name": name}
    if email:
        maker["email"] = email
    if website:
        maker["website"] = website

    maker = omoospace.add_maker(maker)
    typer.secho(f"Maker {maker.name} added", fg=typer.colors.GREEN)


@maker_app.command("list")
def list_maker():
    """List all makers in current omoospace"""
    omoospace = detect_omoospace_or_exit()
    makers = omoospace.makers
    if not makers:
        typer.secho("No makers found", fg=typer.colors.YELLOW)
        return
    typer.secho("Makers:", fg=typer.colors.BLUE)
    for maker in makers:
        typer.echo(
            f"- {maker.name}{f' <{maker.email}>' if maker.email else ''}{f' ({maker.website})' if maker.website else ''}"
        )


# 注册资源子命令组到主应用
app.add_typer(subspace_app, name="subspace")
app.add_typer(work_app, name="work")
app.add_typer(tool_app, name="tool")
app.add_typer(maker_app, name="maker")

if __name__ == "__main__":
    app()
