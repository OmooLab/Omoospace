from omoospace.language import ALLOWED_LANGS, Language
from omoospace.omoospace import Omoospace, Subspace, Objective
from omoospace.utils import make_path, normalize_name, Opath, AnyPath


def create_omoospace(
    name: str,
    under: str = ".",
    brief: str = None,
    contents_dir: str = "Contents",
    subspaces_dir: str = "Subspaces",
    language: Language = None,
    readme: bool = False,
    chinese_to_pinyin: bool = False,
    reveal_in_explorer: bool = False,
) -> Omoospace:
    """Create an omoospace.

    Args:
        name (str): Omoospace name
        under (str, optional): Add omoospace to which folder. Defaults to '.'.
        brief (str, optional): Omoospace brief. Defaults to None.
        chinese_to_pinyin (bool, optional): Whether convert chinese to pinyin. Defaults to False.
        reveal_in_explorer (bool, optional): Whether open folder after or not. Defaults to True.
    Raises:
        ExistsError: Target path already exists.
        CreateFailed: Fail to create directories.

    Returns:
        Omoospace: New created omoospace.
    """

    if language and language not in ALLOWED_LANGS:
        raise ValueError(f"{language} is not a valid language.")
    language = language or "en"

    dirname = normalize_name(name, chinese_to_pinyin=chinese_to_pinyin)
    root_dir = Opath(under, dirname).resolve()

    # Check if root_dir is in a omoospace
    try:
        Omoospace(root_dir)
        raise FileExistsError(f"{root_dir} already exists.")
    
    except FileNotFoundError:
        pass

    profile_file = f"Omoospace.{language}.yml" if language != "en" else "Omoospace.yml"
    contents_dir = contents_dir or "Contents"

    paths = [profile_file, f"{contents_dir}/"]

    if subspaces_dir:
        paths.append(f"{subspaces_dir}/")

    if readme:
        readme_content = f"""# {name}
{brief or ""}"""
        paths.append({"README.md": readme_content})

    make_path(
        *paths,
        under=root_dir,
    )

    if reveal_in_explorer:
        root_dir.reveal_in_explorer()

    omoospace = Omoospace(root_dir)
    omoospace.brief = brief or name

    if subspaces_dir:
        omoospace.subspaces_dir = subspaces_dir
    if contents_dir != "Contents":
        omoospace.contents_dir = contents_dir

    return omoospace


def extract_pathname(path: AnyPath) -> str:
    """Returns the pathname of a path.

    Args:
        path (AnyPath): The giving path.

    Returns:
        ObjectivePath: Objective path.

    """

    try:
        return Subspace(path).pathname
    except FileNotFoundError:
        return None
    except ValueError:
        return ""


def extract_objective(path: AnyPath) -> Objective:
    """Returns the objective.

    Args:
        path (AnyPath): The giving path.

    Returns:
        Objective: Objective.

    """

    try:
        return Subspace(path).objective
    except FileNotFoundError:
        return None
    except ValueError:
        return None
