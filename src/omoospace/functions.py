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
    dirname: str,
    name: str = None,
    description: str = None,
    contents_dir: str = None,
    subspaces_dir: str = None,
    gitfiles: bool = False,
    reveal_in_explorer: bool = False,
) -> Omoospace:
    """Create an omoospace.

    Args:
        dirname (str): The directory name of the omoospace.
        name (str, optional): The name of the omoospace.
        description (str, optional): The description of the omoospace.
        contents_dir (str, optional): The name of the contents directory. Defaults to "contents".
        subspaces_dir (str, optional): The name of the subspaces directory. Defaults to "subspaces".
        gitfiles (bool, optional): Whether to create .gitattributes and .gitignore files. Defaults to False.
        reveal_in_explorer (bool, optional): Whether to reveal the created omoospace in file explorer. Defaults to False.

    Returns:
        Omoospace: The created omoospace.
    """

    root_dir = Opath(dirname).resolve()

    # Check if root_dir is in a omoospace
    try:
        Omoospace(root_dir)
        raise FileExistsError(f"{root_dir} already exists.")

    except FileNotFoundError:
        pass

    contents_dir = contents_dir or "contents"

    paths = [
        "OMOOSPACE.md",
        f"{contents_dir}/",
    ]

    if subspaces_dir:
        paths.append(f"{subspaces_dir}/")

    if gitfiles:
        readme_content = f"""# {name}
{description or ""}"""

        paths.append({"README.md": readme_content})
        paths.append({".gitattributes": gitattributes_content})
        paths.append({".gitignore": gitignore_content})

    make_path(
        *paths,
        under=root_dir,
    )

    if reveal_in_explorer:
        root_dir.reveal_in_explorer()

    omoospace = Omoospace(root_dir)

    if name:
        omoospace.name = name
    if description:
        omoospace.description = description
    if subspaces_dir != "subspaces" and subspaces_dir:
        omoospace.subspaces_dir = subspaces_dir
    if contents_dir != "contents":
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
        # Not in omoospace
        raise FileNotFoundError(f"Path is not in an omoospace")
    except ValueError:
        # Not a subspace
        return None


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
        # Not in omoospace
        raise FileNotFoundError(f"Path is not in an omoospace")
    except ValueError:
        # Not a subspace
        return None
