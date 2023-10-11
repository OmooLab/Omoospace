
from pathlib import Path
import networkx as nx
from pyvis.network import Network

from omoospace.utils import PathLike, reveal_in_explorer


def draw_graph(
    node_dict: dict,
    output_dir: PathLike = ".",
    bgcolor: str = "#ffffff",
    font_color: bool = False,
    reveal_when_success: bool = True
):
    G = nx.Graph()
    for key, node in node_dict.items():
        G.add_node(
            key,
            label=node.get('name'),
            title=node.get('content'),
            level=node.get('level'),
            size=node.get('size'),
            color=node.get('color'),
            borderWidth=node.get('border_width')
        )
        if (node.get('parent')):
            G.add_edge(
                node.get('parent'),
                key,
                weight=node.get('edge_width'),
                color=node.get('edge_color')
            )
    net = Network(
        "100vh",
        notebook=True,
        bgcolor=bgcolor,
        font_color=font_color,
        cdn_resources='remote'
    )
    net.from_nx(G)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    structure_filepath = Path(output_path, "Structure.html").resolve()
    net.show(str(structure_filepath))

    if reveal_when_success:
        reveal_in_explorer(structure_filepath)
