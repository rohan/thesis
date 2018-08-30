"""Various utility classes and methods."""
import os
from typing import Set, List

import networkx as nx

from elbridge.evolution.hypotheticals import HypotheticalSet
from elbridge.types import Node, FatNode


class cd:
    # pylint: disable=invalid-name, too-few-public-methods
    """Context manager for changing the current working directory."""

    def __init__(self, new_path):
        """Point this to new_path."""
        self.new_path = os.path.expanduser(new_path)
        self.saved_path = None

    def __enter__(self):
        self.saved_path = os.getcwd()
        os.chdir(self.new_path)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.saved_path)


def _connected_components(graph: nx.Graph, vertices: List[FatNode], hypotheticals: HypotheticalSet):
    """
    Return the number of connected components in a graph. The edges of the graph are defined as E \ hypotheticals.
    :param graph:
    :param vertices:
    :param hypotheticals:
    :return:
    """
    def helper(source):
        """A fast BFS node generator"""
        _seen = set()
        next_level = {source}
        while next_level:
            this_level = next_level
            next_level = set()
            for vertex in this_level:
                if vertex not in _seen:
                    yield vertex
                    _seen.add(vertex)
                    for n in graph[vertex]:
                        if n not in _seen and (vertex, n) not in hypotheticals:
                            next_level.add(n)

    seen = set()
    if isinstance(vertices[0], tuple):
        vertices: List[Node] = list(map(lambda i: i[0], vertices))

    for v in vertices:
        if v not in seen:
            c = set(helper(v))
            yield c
            seen.update(c)


def number_connected_components(graph: nx.Graph, vertices: List[FatNode], hypotheticals: HypotheticalSet) -> int:
    return sum(1 for _ in _connected_components(graph, vertices, hypotheticals))