import typer
from pathlib import Path
from omoospace.omoospace import (
    create_omoospace,
    Omoospace,
)
from omoospace.utils import format_name
from InquirerPy import inquirer

# 主应用
app = typer.Typer(help="Omoospace CLI", no_args_is_help=True)

# 资源子命令组
subspace_app = typer.Typer(help="Subspace operations", no_args_is_help=True)
package_app = typer.Typer(help="Package operations", no_args_is_help=True)
work_app = typer.Typer(help="Work operations", no_args_is_help=True)
software_app = typer.Typer(help="Software operations", no_args_is_help=True)
creator_app = typer.Typer(help="Creator operations", no_args_is_help=True)


def detect_omoospace_or_exit():
    try:
        return Omoospace(Path.cwd())
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


# -------------------------- 全局命令 --------------------------


@app.command()
def init():
    """
    Initialize current directory as an Omoospace.
    """
    cwd = Path.cwd()
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

    profile_path = cwd / "Omoospace.yml"

    # 3. 近似文件夹候选
    def find_candidates(names):
        return [
            p.name
            for p in cwd.iterdir()
            if p.is_dir() and p.name.lower() in [n.lower() for n in names]
        ]

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
    contents_candidates = find_candidates(
        ["Contents", "Content", "Assets", "Asset", "Resources", "Resource"]
    )
    references_candidates = find_candidates(["References", "Reference"])
    void_candidates = find_candidates(
        ["Void", "Temp", "Tmp", "Caches", "Cache", "Intermediate"]
    )

    # 4. Select or create logic (single step, English, skip if exact match)
    def select_or_create(folder_type, candidates, default):
        # If exact match exists, use it directly
        if default in candidates:
            return default
        # If there are candidates, ask user to select or create new
        if candidates:
            choices = candidates + [f"Create new '{default}'"]
            selected = inquirer.select(
                message=f"Select as {folder_type}, or create new:",
                choices=choices,
                default=choices[0],
            ).execute()
            if selected.startswith("Create new"):
                (cwd / default).mkdir(exist_ok=True)
                return default
            else:
                return selected
        # No candidates, just create new
        (cwd / default).mkdir(exist_ok=True)
        return default

    name = inquirer.text(message="Name:", default=cwd.name).execute()
    description = inquirer.text(message="Description:", default="").execute()

    subspaces_dir = select_or_create("Subspaces", subspaces_candidates, "Subspaces")
    contents_dir = select_or_create("Contents", contents_candidates, "Contents")
    references_dir = select_or_create("References", references_candidates, "References")
    void_dir = select_or_create("Void", void_candidates, "Void")

    # 5. 生成 Omoospace profile 文件
    profile = {
        "name": name,
        "description": description,
    }
    if subspaces_dir != "Subspaces":
        profile["subspaces_mapping"] = subspaces_dir
    if contents_dir != "Contents":
        profile["contents_mapping"] = contents_dir
    if references_dir != "References":
        profile["references_mapping"] = references_dir
    if void_dir != "Void":
        profile["void_mapping"] = void_dir

    import yaml

    with profile_path.open("w", encoding="utf-8") as f:
        yaml.dump(profile, f, allow_unicode=True)
    typer.secho(f"Omoospace.yml created.", fg=typer.colors.GREEN)

    # 6. Generate README.md
    readme_path = cwd / "README.md"
    if not readme_path.exists():
        readme_path.write_text(f"# {name}\n\n{description}\n", encoding="utf-8")
        typer.secho("README.md created.", fg=typer.colors.GREEN)
    else:
        typer.secho(
            "README.md already exists. Not overwritten.", fg=typer.colors.YELLOW
        )

    typer.secho("Omoospace initialization complete.", fg=typer.colors.GREEN)


@app.command()
def create(name: str = typer.Argument(..., help="Omoospace name")):
    """Create a new omoospace."""
    description = inquirer.text(message="Description:", default="").execute()
    chinese_to_pinyin = inquirer.confirm(
        message="Convert Chinese to pinyin?", default=False
    ).execute()
    try:
        omoospace = create_omoospace(
            name=name,
            description=description,
            chinese_to_pinyin=chinese_to_pinyin,
            reveal_in_explorer=True,
        )
        typer.secho(f"Omoospace created: {omoospace.root_path}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Create failed: {e}", fg=typer.colors.RED)


@package_app.command("export")
def export_package(
    items: list[str] = typer.Argument(
        ..., help="Path(s) to export, relative to omoospace root, can be multiple"
    ),
    name: str = typer.Option(None, help="Package name"),
    description: str = typer.Option("", help="Package description"),
    version: str = typer.Option("0.1.0", help="Package version"),
    export_dir: str = typer.Option(".", help="Export directory"),
):
    """Export a package from omoospace"""
    omoospace = detect_omoospace_or_exit()
    abs_items = []
    for item in items:
        path = (Path(omoospace.root_path) / item).resolve()
        if not omoospace.is_omoospace_item(path):
            typer.secho(f"Invalid item: {item}", fg=typer.colors.RED)
            raise typer.Exit(1)
        abs_items.append(str(path))
    pkg_name = (
        name or inquirer.text(message="Package name:", default=omoospace.name).execute()
    )
    pkg_desc = (
        description or inquirer.text(message="Description:", default="").execute()
    )
    pkg_version = (
        version or inquirer.text(message="Version:", default="0.1.0").execute()
    )
    pkg_export_dir = (
        export_dir or inquirer.text(message="Export directory:", default=".").execute()
    )
    try:
        pkg = omoospace.export_package(
            *abs_items,
            name=pkg_name,
            description=pkg_desc,
            version=pkg_version,
            export_dir=pkg_export_dir,
            reveal_in_explorer=True,
            overwrite_existing=True,
        )
        typer.secho(f"Package exported: {pkg.root_path}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Export failed: {e}", fg=typer.colors.RED)


@package_app.command("list")
def list_package():
    """List all imported packages in current omoospace"""
    omoospace = detect_omoospace_or_exit()
    try:
        packages = omoospace.imported_packages
        if not packages:
            typer.secho("No packages found", fg=typer.colors.YELLOW)
            return
        typer.secho("Packages:", fg=typer.colors.BLUE)
        for idx, pkg in enumerate(packages, 1):
            typer.echo(
                f"{idx}. {pkg.name} v{pkg.version} - {pkg.description or 'No description'}"
            )
    except Exception as e:
        typer.secho(f"List failed: {e}", fg=typer.colors.RED)


@package_app.command("import")
def import_package(
    package_path: str = typer.Argument(..., help="Path to package directory or .zip"),
):
    """Import a package into omoospace"""
    omoospace = detect_omoospace_or_exit()
    try:
        omoospace.import_package(
            package_path=package_path,
            reveal_in_explorer=True,
            overwrite_existing=True,
        )
        typer.secho(f"Package imported: {package_path}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Import failed: {e}", fg=typer.colors.RED)


# -------------------------- Subspace 命令 --------------------------
@subspace_app.command("add")
def add_subspace(name: str = typer.Argument(..., help="Subspace name")):
    """Add a new subspace"""
    omoospace = detect_omoospace_or_exit()
    subspaces_path = omoospace.subspaces_path_path
    subdirs = [p for p in subspaces_path.glob("**/") if p.is_dir()]
    subdirs = [str(p.relative_to(subspaces_path)) for p in subdirs]
    if not subdirs:
        subdirs = ["."]
    parent_dir = inquirer.select(
        message="Select parent_dir (relative to Subspaces):",
        choices=subdirs,
        default=".",
    ).execute()
    description = inquirer.text(message="Description:", default="").execute()
    collect_entities = inquirer.confirm(
        message="Auto collect related entities?", default=True
    ).execute()
    try:
        subs = omoospace.add_subspace(
            name=name,
            parent_dir=str(subspaces_path / parent_dir) if parent_dir != "." else None,
            description=description,
            reveal_in_explorer=True,
            collect_entities=collect_entities,
        )
        typer.secho(f"Subspace added: {subs.root_path}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Add failed: {e}", fg=typer.colors.RED)


@subspace_app.command("list")
def list_subspace():
    """List all subspaces in current omoospace"""
    omoospace = detect_omoospace_or_exit()
    try:
        omoospace.print_subspace_tree()
    except Exception as e:
        typer.secho(f"List failed: {e}", fg=typer.colors.RED)


# -------------------------- Work 命令 --------------------------
@work_app.command("add")
def add_work(
    items: list[str] = typer.Argument(
        ..., help="Path(s) to files or folders, can be absolute or relative"
    )
):
    """Add a new work"""
    omoospace = detect_omoospace_or_exit()
    abs_items = []

    for item in items:
        path = Path(item).resolve()
        if not path.exists():
            typer.secho(f"Path not found: {item}", fg=typer.colors.RED)
            raise typer.Exit(1)
        try:
            path.relative_to(omoospace.contents_path)
        except ValueError:
            typer.secho(
                f"Path '{item}' is not under Contents directory: {omoospace.contents_path}",
                fg=typer.colors.RED,
            )
            raise typer.Exit(1)
        abs_items.append(str(path))

    name = inquirer.text(
        message="Work name:", default=format_name(Path(abs_items[0]).stem)
    ).execute()
    description = inquirer.text(message="Description:", default="").execute()

    try:
        work = omoospace.add_work(*abs_items, name=name, description=description)
        typer.secho(f"Work added: {work.name}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Add failed: {e}", fg=typer.colors.RED)


@work_app.command("list")
def list_work():
    """List all works in current omoospace"""
    omoospace = detect_omoospace_or_exit()
    try:
        works = omoospace.works
        if not works:
            typer.secho("No works found", fg=typer.colors.YELLOW)
            return
        typer.secho("Works:", fg=typer.colors.BLUE)
        for idx, work in enumerate(works, 1):
            relpaths = [str(item) for item in getattr(work, "items", [])]
            relpaths_str = ", ".join(relpaths) if relpaths else "No files"
            typer.echo(f"{idx}. {work.name}")
            typer.echo(f"    Paths: {relpaths_str}")
    except Exception as e:
        typer.secho(f"List failed: {e}", fg=typer.colors.RED)


# -------------------------- Software 命令 --------------------------
@software_app.command("add")
def add_software(
    name: str = typer.Argument(..., help="Software name"),
    version: str = typer.Argument(..., help="Software version"),
):
    """Add a new software"""
    omoospace = detect_omoospace_or_exit()
    plugins = []
    while inquirer.confirm(message="Add plugin?", default=False).execute():
        plugin_name = inquirer.text(message="Plugin name:").execute()
        plugin_version = inquirer.text(
            message="Plugin version:", default="1.0.0"
        ).execute()
        plugins.append({"name": plugin_name, "version": plugin_version})
    try:
        sw = omoospace.add_software(name=name, version=version, plugins=plugins)
        typer.secho(f"Software added: {sw.name} {sw.version}", fg=typer.colors.GREEN)
    except Exception as e:
        typer.secho(f"Add failed: {e}", fg=typer.colors.RED)


@software_app.command("list")
def list_software():
    """List all softwares in current omoospace"""
    omoospace = detect_omoospace_or_exit()
    try:
        softwares = omoospace.softwares
        if not softwares:
            typer.secho("No softwares found", fg=typer.colors.YELLOW)
            return
        typer.secho("Softwares:", fg=typer.colors.BLUE)
        for idx, sw in enumerate(softwares, 1):
            typer.echo(f"{idx}. {sw.name} ({sw.version})")
    except Exception as e:
        typer.secho(f"List failed: {e}", fg=typer.colors.RED)


# -------------------------- Creator 命令 --------------------------
@creator_app.command("add")
def add_creator(
    name: str = typer.Argument(..., help="Creator name"),
    email: str = typer.Argument(..., help="Creator email"),
):
    """Add a new creator"""
    omoospace = detect_omoospace_or_exit()
    role = inquirer.text(message="Role:", default="").execute()
    website = inquirer.text(message="Website:", default="").execute()
    try:
        creator = omoospace.add_creator(
            name=name, email=email, website=website or None, role=role or None
        )
        typer.secho(
            f"Creator added: {creator.name} <{creator.email}>", fg=typer.colors.GREEN
        )
    except Exception as e:
        typer.secho(f"Add failed: {e}", fg=typer.colors.RED)


@creator_app.command("list")
def list_creator():
    """List all creators in current omoospace"""
    omoospace = detect_omoospace_or_exit()
    try:
        creators = omoospace.creators
        if not creators:
            typer.secho("No creators found", fg=typer.colors.YELLOW)
            return
        typer.secho("Creators:", fg=typer.colors.BLUE)
        for idx, creator in enumerate(creators, 1):
            typer.echo(
                f"{idx}. {creator.name} <{creator.email}> ({creator.role or 'No role'})"
            )
    except Exception as e:
        typer.secho(f"List failed: {e}", fg=typer.colors.RED)


# 注册资源子命令组到主应用
app.add_typer(subspace_app, name="subspace")
app.add_typer(package_app, name="package")
app.add_typer(work_app, name="work")
app.add_typer(software_app, name="software")
app.add_typer(creator_app, name="creator")

if __name__ == "__main__":
    app()
