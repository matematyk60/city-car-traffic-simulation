from typing import Dict

from simulation.node import Node
from simulation.way import Way


class DirectionsFinder:

    def __init__(self, node_dict: Dict[int, Node], way_dict: Dict[int, Way]):
        self.node_dict = node_dict
        self.way_dict = way_dict

    def find_directions(self, start_node: int, end_node: int):
        visited = {}
        queue = []
        directions = {}

        queue.append((start_node, None))
        visited[start_node] = False
        directions[start_node] = {}

        while queue:
            node_id, previous_way = queue.pop(0)
            if node_id == end_node:
                return directions[node_id]
            for way in self.find_outgoing_ways(node_id):
                way_end_node_id = way.end_node.node_id
                if not visited.get(way_end_node_id, False):
                    queue.append((way_end_node_id, way.way_id))
                    directions_map = directions[node_id].copy()
                    if previous_way is not None:
                        directions_map[previous_way] = way.way_id
                    directions[way_end_node_id] = directions_map
                    visited[node_id] = True


    def find_outgoing_ways(self, node: int):
        ways = []
        for way in self.node_dict[node].outgoing_ways:
            if way.begin_node.node_id == node:
                ways.append(way)
        return ways