from InquirerPy import inquirer
import typer
from pathlib import Path

from omoospace.functions import create_omoospace, extract_objective, extract_pathname
from omoospace.omoospace import Omoospace
from omoospace.utils import Opath

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
        typer.secho(f"Error: {err}", fg=typer.colors.RED)
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
            "contents",
            "Contents",
            "Content",
            "assets",
            "Assets",
            "resources",
            "Resources",
            "res",
            "dist",
            "public",
        ]
    )

    subspaces_candidates = find_candidates(
        [
            "subspaces",
            "Subspaces",
            "SourceFiles",
            "Source Files",
            "sources",
            "source",
            "src",
            "ProjectFiles",
            "Project Files",
        ]
    )

    # 4. Select or create logic (single step, English, skip if exact match)
    def select_or_create(folder_type, candidates, default):
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

    contents_dir = select_or_create("Contents Folder", contents_candidates, "contents")
    subspaces_dir = select_or_create(
        "Subspaces Folder", subspaces_candidates, "subspaces"
    )

    omoospace = create_omoospace(
        dirname=".",
        contents_dir=contents_dir,
        subspaces_dir=subspaces_dir,
    )


@app.command()
def create(
    dirname: str = typer.Argument(..., help="Omoospace name"),
    name: str = typer.Option("", "--name", help="Project name"),
    description: str = typer.Option("", "--description", help="Project description"),
    contents: str = typer.Option(
        "contents", "--contents-dir", help="Contents folder name"
    ),
    subspaces: str = typer.Option(
        "subspaces", "--subspaces-dir", help="Subspaces folder name"
    ),
    gitfiles: bool = typer.Option(
        False, "--git", help="Add .gitattributes and .gitignore files"
    ),
):
    """Create a new omoospace."""
    omoospace = create_omoospace(
        dirname,
        name=name,
        description=description,
        contents_dir=contents,
        subspaces_dir=subspaces,
        gitfiles=gitfiles,
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


@app.command("subspaces-dir")
def subspaces_dir(value: str = typer.Argument(None, help="Set subspaces_dir")):
    """Print or set subspaces directory path"""
    omoospace = detect_omoospace_or_exit()
    if value is None:
        print(omoospace.subspaces_dir)
    else:
        omoospace.subspaces_dir = value


@app.command("contents-dir")
def contents_dir(value: str = typer.Argument(None, help="Set contents_dir")):
    """Print or set contents directory path"""
    omoospace = detect_omoospace_or_exit()
    if value is None:
        print(omoospace.contents_dir)
    else:
        omoospace.contents_dir = value


@app.command("name")
def name(value: str = typer.Argument(None, help="Set name")):
    """Print or set omoospace name"""
    omoospace = detect_omoospace_or_exit()
    if value is None:
        print(omoospace.name)
    else:
        omoospace.name = value


@app.command("description")
def description(value: str = typer.Argument(None, help="Set description")):
    """Print or set omoospace description"""
    omoospace = detect_omoospace_or_exit()
    if value is None:
        print(omoospace.description)
    else:
        omoospace.description = value


@app.command("root-dir")
def root_dir():
    """Print root directory path"""
    omoospace = detect_omoospace_or_exit()
    print(omoospace.root_dir)


@app.command()
def pathname(path: str = typer.Argument(..., help="Path to extract pathname")):
    """Print pathname"""
    print(extract_pathname(path))


@app.command()
def objective(path: str = typer.Argument(..., help="Path to extract objective")):
    """Print objective"""
    print(extract_objective(path))


# -------------------------- Subspace 命令 --------------------------
@subspace_app.command("add")
def add_subspace(
    name: str = typer.Argument(..., help="Subspace name"),
    parent: str = typer.Option(".", "--parent", help="Parent directory"),
    collect: bool = typer.Option(
        True, "--collect/--no-collect", help="Auto collect related subspaces"
    ),
):
    """Add a new subspace"""
    omoospace = detect_omoospace_or_exit()
    subspaces_dir = omoospace.subspaces_dir
    try:
        subs = omoospace.add_subspace(
            name=name,
            under=str(subspaces_dir / parent) if parent != "." else None,
            collect_children=collect,
            reveal_in_explorer=True,
        )
        typer.secho(f"Subspace {subs.pathname} added", fg=typer.colors.GREEN)
    except Exception as err:
        typer.secho(f"Add failed: {err}", fg=typer.colors.RED)


# -------------------------- Work 命令 --------------------------
@work_app.command("add")
def add_work(
    name: str = typer.Argument(..., help="Work name"),
    contents: str = typer.Option(
        "", "--contents", help="Content path(s) to Contents folder"
    ),
    description: str = typer.Option("", "--description", help="Work description"),
):
    """Add a new work"""
    omoospace = detect_omoospace_or_exit()

    if not contents:
        typer.secho("Error: --contents is required", fg=typer.colors.RED)
        raise typer.Exit(1)

    content_list = [c.strip() for c in contents.split(",")]
    contents_parsed = []

    for item in content_list:
        abs_path = Opath(item).resolve()
        rel_path = omoospace.contents_dir / item
        is_abs = omoospace.is_content(abs_path)
        is_rel = omoospace.is_content(rel_path)

        if not is_abs and not is_rel:
            typer.secho(f"Content not found: {item}", fg=typer.colors.RED)
            raise typer.Exit(1)

        content = str(abs_path.relative_to(omoospace.contents_dir)) if is_abs else item
        contents_parsed.append(content)

    work_name = name or contents_parsed[0].split("/")[-1].split(".")[0]

    work = {"name": work_name, "version": "0.1.0", "contents": contents_parsed}
    if description:
        work["description"] = description

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
            f"- {work.name}{f': v{work.version}' if work.version else ''}{f' ({work.description})' if work.description else ''}"
        )
        for idx, content in enumerate(work.contents, 1):
            if idx != len(work.contents):
                typer.echo(f"  ├── {content}")
            else:
                typer.echo(f"  ╰── {content}")
                typer.echo(f"")


# -------------------------- tool 命令 --------------------------
@tool_app.command("add")
def add_tool(
    name: str = typer.Argument(..., help="Tool name"),
    version: str = typer.Option("", "--version", help="Tool version"),
    website: str = typer.Option("", "--website", help="Tool website"),
):
    """Add a new tool"""
    omoospace = detect_omoospace_or_exit()
    tool = {"name": name}
    if version:
        tool["version"] = version
    if website:
        tool["website"] = website

    tool = omoospace.add_tool(tool)
    typer.secho(f"Tool {tool.name} added", fg=typer.colors.GREEN)


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
    name: str = typer.Argument(..., help="Maker name"),
    email: str = typer.Option("", "--email", help="Maker email"),
    website: str = typer.Option("", "--website", help="Maker website"),
):
    """Add a new maker"""
    omoospace = detect_omoospace_or_exit()
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
