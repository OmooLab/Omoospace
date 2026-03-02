from omoospace.language import ALLOWED_LANGS, Language
from omoospace.omoospace import Omoospace, Subspace, Objective
from omoospace.utils import make_path, normalize_name, Opath, AnyPath

gitattributes_content = """# Define macros (only works in top-level gitattributes files)
[attr]lfs               filter=lfs diff=lfs merge=lfs -text


# 3D models
*.collada               lfs
*.dae                   lfs
*.dxf                   lfs
*.FBX                   lfs
*.fbx                   lfs
*.jas                   lfs
*.lws                   lfs
*.lxo                   lfs
*.obj                   lfs
*.ply                   lfs
*.skp                   lfs
*.stl                   lfs
*.usd                   lfs
*.usda                  lfs
*.usdc                  lfs
*.usdz                  lfs
*.glb                   lfs
*.gltf                  lfs

# Audio
*.aif                   lfs
*.aiff                  lfs
*.it                    lfs
*.mod                   lfs
*.mp3                   lfs
*.ogg                   lfs
*.s3m                   lfs
*.wav                   lfs
*.xm                    lfs

# Video
*.asf                   lfs
*.avi                   lfs
*.flv                   lfs
*.mov                   lfs
*.mp4                   lfs
*.mpeg                  lfs
*.mpg                   lfs
*.ogv                   lfs
*.wmv                   lfs

# Images
*.bmp                   lfs
*.exr                   lfs
*.gif                   lfs
*.hdr                   lfs
*.iff                   lfs
*.jpeg                  lfs
*.jpg                   lfs
*.pict                  lfs
*.png                   lfs
*.psd                   lfs
*.tga                   lfs
*.tif                   lfs
*.tiff                  lfs
*.webp                  lfs

# Compressed Archive
*.7z                    lfs
*.bz2                   lfs
*.gz                    lfs
*.rar                   lfs
*.tar                   lfs
*.zip                   lfs

# Compiled Dynamic Library
*.dll                   lfs
*.pdb                   lfs
*.so                    lfs

# Fonts
*.otf                   lfs
*.ttf                   lfs
*.woff                  lfs
*.woff2                 lfs

# Executable/Installer
*.apk                   lfs
*.exe                   lfs

# Documents
*.pdf                   lfs

# Adobe
*.psd                    lfs
*.ai                    lfs
*.aep                   lfs
*.prproj                lfs
*.spp                   lfs

# Zbrush
*.zbr                   lfs
*.zpr                   lfs
*.ztl                   lfs
*.c4d                   lfs

# Autodesk
*.max                   lfs
*.ma                    lfs
*.mb                    lfs
*.3dm                   lfs
*.3ds                   lfs

# Blender
*.blend                 lfs
*.blend1                lfs
*.c4d                   lfs

# Imaging
*.dicom                 lfs
*.dcm                   lfs
*.nii                   lfs
*.ome                   lfs
*.map                   lfs
*.mrc                   lfs
"""

gitignore_content = """
# Blender
*.blend1
blendcache_*
*.cats.txt~
"""


def create_omoospace(
    name: str,
    under: str = ".",
    brief: str = None,
    contents_dir: str = "Contents",
    subspaces_dir: str = "Subspaces",
    language: Language = None,
    readme: bool = False,
    gitfiles: bool = False,
    chinese_to_pinyin: bool = False,
    reveal_in_explorer: bool = False,
) -> Omoospace:
    """Create an omoospace.
    
    Args:
        name (str): The name of the omoospace.
        under (str, optional): The directory under which to create the omoospace. Defaults to ".".
        brief (str, optional): A brief description of the omoospace. Defaults to None.
        contents_dir (str, optional): The name of the contents directory. Defaults to "Contents".
        subspaces_dir (str, optional): The name of the subspaces directory. Defaults to "Subspaces".
        language (Language, optional): The language of the omoospace profile. Defaults to None.
        readme (bool, optional): Whether to create a README.md file. Defaults to False.
        gitfiles (bool, optional): Whether to create .gitattributes and .gitignore files. Defaults to False.
        chinese_to_pinyin (bool, optional): Whether to convert Chinese characters in the name to Pinyin. Defaults to False.
        reveal_in_explorer (bool, optional): Whether to reveal the created omoospace in file explorer. Defaults to False.

    Returns:
        Omoospace: The created omoospace.
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

    if gitfiles:
        paths.append({".gitattributes": gitattributes_content})
        paths.append({".gitignore": gitignore_content})

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
