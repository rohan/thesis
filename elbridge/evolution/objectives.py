"""Objective functions. These functions take a chromosome and return a value, such that better 
chromosomes have higher values."""

import statistics
from typing import List, Tuple, Dict, Any

import networkx as nx

from elbridge.evolution.hypotheticals import HypotheticalSet
from elbridge.types import FatNode
from elbridge.utils import number_connected_components
from elbridge.xceptions import KeyNotFoundException

DISTRICTS = 10


class ObjectiveFunction:
    key = None
    min_value = None
    max_value = None
    goal_value = None

    def __call__(self, *args, **kwargs):
        pass

    def call_with_data(self, *args, **kwargs):
        pass


class PopulationEquality(ObjectiveFunction):
    # pylint: disable=R0903
    """Test population equality."""

    def __init__(self, master_graph, key='pop', districts=DISTRICTS):
        self.master_graph = master_graph
        self.key = key
        self.districts = districts

        self.total_pop = sum([data.get(self.key, 0) for _, data in self.master_graph.nodes(data=True)])
        self.min_value = 0
        self.max_value = self.total_pop / self.districts

        self.goal_value = self.max_value

        self.data = {}

    def __repr__(self):
        return "Population equality"

    @profile
    def __call__(self, components: List[List[FatNode]], hypotheticals: HypotheticalSet) -> float:
        """Returns the mean absolute deviation of subgraph population."""
        score = float('inf')

        ncc = 0
        for component in components:
            component_score = 0
            for _, data in component:
                if self.key not in data:
                    raise KeyNotFoundException(self.key, data)

                component_score += data.get(self.key)

            score = min(score, component_score)
            ncc += number_connected_components(self.master_graph, component, hypotheticals)

        min_score = score

        self.data['min_score'] = score

        # punish district maps with more than d ccomps
        # this punishes disconnected districts
        score -= min_score * (ncc - self.districts)
        self.data['components'] = ncc

        # punish district maps with more or less than d districts
        score -= min_score * 10 * abs(len(components) - self.districts)
        self.data['districts'] = len(components)

        return score

    def call_with_data(self, components: List[FatNode], hypotheticals: HypotheticalSet) -> Tuple[float, Dict[str, Any]]:
        output = self.__call__(components, hypotheticals)
        return output, self.data


class SizeEquality(ObjectiveFunction):
    # pylint: disable=R0903
    """Test size equality. For testing purposes only"""

    def __init__(self, graph, districts=DISTRICTS):
        self.districts = districts
        self.total_pop = len(graph)
        self.min_value = -1 * statistics.stdev([0] * (len(graph) - 1) + [self.total_pop])
        self.max_value = 0

    def __repr__(self):
        return "Size equality"

    def __call__(self, components, graph):
        """Returns the mean absolute deviation of subgraph population."""
        goal = self.total_pop / self.districts
        score = -1 * sum([abs(len(component) - goal) for component in components])
        # punish district maps with more or less than d ccomps
        # this punishes disconnected districts
        ncc = nx.number_connected_components(graph)
        score -= 100 * abs(ncc - self.districts)

        # punish district maps with more or less than d districts
        score -= 1000 * abs(len(components) - self.districts)
        return score