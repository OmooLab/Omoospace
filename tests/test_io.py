import pytest
from omoospace import make_path, Opath
from omoospace.omoospace import Omoospace


# def test_export_package(mini_omoos_path: Path):
#     omoos = Omoospace(mini_omoos_path)
#     make_path(
#         "Heart.blend",
#         "Heart.v001.blend",
#         "Heart_Valves.blend",
#         "Liver.zpr",
#         under=omoos.subspaces_path,
#     )
#     make_path(
#         "Models/Heart/Heart.fbx",
#         "Models/Heart/Textures/Heart_BaseColor.png",
#         "Models/Liver/Liver.gltf",
#         "Models/Liver/Liver.png",
#         "Models/Liver/Liver.bin",
#         "Models/Lung.glb",
#         under=omoos.contents_dir,
#     )
#     omoos.set_creator("manan", "username@example.com")
#     assert omoos.is_content(omoos.contents_dir / "Models/Heart") == True
#     assert omoos.is_content(omoos.contents_dir / "Models/Heart001") == False
#     assert omoos.is_content(omoos.contents_dir / "Models/Heart001", False) == True

#     pkg = omoos.export_package(
#         Path(omoos.contents_dir, "Models/Heart"), name="Organs", export_dir="temp"
#     )
#     assert pkg.root_path.is_dir()
#     assert Path(pkg.root_path, "Contents/Models/Heart/Textures").is_dir()
#     assert Path(pkg.root_path, "Contents/Models/Heart/Heart.fbx").is_file()
#     assert pkg.name == "Organs"
#     assert pkg.description == None
#     assert pkg.version == "0.1.0"

#     pkg.description = "An model package of organs."
#     assert pkg.description == "An model package of organs."


# def test_import_package(mini_omoos_path: Path):
#     omoos = Omoospace(mini_omoos_path)
#     pkg_path = Path("temp", "Organs").resolve()
#     make_path("Heart.glb", "Liver.glb", under=Path(pkg_path, "Contents/Models"))
#     make_path(
#         {
#             "Package.yml": """
#         name: Organs
#         version: 0.1.0
#         description: An empty omoospace.
#         """
#         },
#         under=pkg_path,
#     )
#     omoos.import_package(pkg_path)

#     assert Path(omoos.contents_dir, "Packages", "Organs").is_dir()
