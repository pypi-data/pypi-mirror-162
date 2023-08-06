import logging
from typing import Dict, List

import networkx as nx
from attrs import define
from treelib import Tree

from .scan import BuildGraph

log = logging.getLogger(__name__)

@define
class TreeView:

    good = logging.DEBUG
    good_color = 'green'

    _trees: List[Tree]

    @classmethod
    def from_build_graph(cls, build: BuildGraph) -> List[Tree]:
        reversed_build = nx.reverse_view(build)
        trees = []
        for leaf in build.leaves:
            tree = Tree()
            subgraph = nx.bfs_tree(reversed_build, leaf)
            for n in subgraph.nodes():
                # skip printing deps the tree if we've already described it elsewhere
                if any(t.get_node(n) for t in trees):
                    continue

                # create the root node if there's nothing in the tree
                if not tree.get_node(n):
                    tree.create_node(n, n)

                n_out = [e[1] for e in reversed_build.out_edges(n)]
                for o in n_out:
                    # deal with duplicate nodes so we can still show the dependency
                    if tree.get_node(o):
                        tree.create_node(o, parent=n)
                    else:
                        tree.create_node(o, o, parent=n)

            trees.append(tree)

        return cls(trees)

    def annotate(self, annotations: Dict[str, str]):
        # iterate through and replace the specified tags
        for tree in self._trees:
            for node_name in tree.nodes:
                node = tree.get_node(node_name)
                if node.tag in annotations:
                    node.tag = annotations[node.tag]

    def show(self):
        for tree in self._trees:
            tree.show()
