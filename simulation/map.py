import xml.etree.ElementTree as ET

from simulation.directions_finder import DirectionsFinder
from simulation.origin import Origin
from simulation.way import Way
from simulation.node import Node, TraversableNode


class Map:
    def __init__(self):
        self.node_dict = {}
        self.way_dict = {}
        self.origin_dict = {}
        self.cars = []
        self.term_list = []

        root = ET.parse('./obwodnica.osm').getroot()
        bounds = root.find('bounds')
        self.minlat = float(bounds.get('minlat'))
        self.minlon = float(bounds.get('minlon'))
        self.maxlat = float(bounds.get('maxlat'))
        self.maxlon = float(bounds.get('maxlon'))

        for node in root.findall('node'):
            node_id = int(node.get('id'))
            lat = float(node.get('lat'))
            lon = float(node.get('lon'))
            self.node_dict[node_id] = TraversableNode(node_id, lat, lon)

        for way in root.findall('way'):
            way_id = int(way.get('id'))
            nodes = way.findall('nd')
            # print(f"ELOOOO way_id = {way_id}")
            try:
                lanes = next(int(tag.get("v")) for tag in way.findall("tag") if tag.get("k") == "lanes")
            except StopIteration:
                lanes = 1

            # some ways have just one node (or none), we ignore them
            # to do: remove them from obwodnica.osm
            try:
                begining = nodes.pop(0)
                begining_id = int(begining.get('ref'))
                end = nodes.pop()
                end_id = int(end.get('ref'))
            except IndexError:
                continue

            intermediate_nodes = []
            for node in nodes:
                node_id = int(node.get('ref'))
                intermediate_nodes.append(self.node_dict[node_id])

            self.way_dict[way_id] = Way(way_id, self.node_dict[begining_id], self.node_dict[end_id], lanes,
                                        intermediate_nodes)
            self.node_dict[begining_id].add_outgoing_way(self.way_dict[way_id])

        for node in root.findall('node'):
            try:
                edge = next(tag.get("v") for tag in node.findall("tag") if tag.get("k") == "edge")
            except StopIteration:
                edge = None
            if edge is None:
                pass
            elif edge == "term":
                self.term_list.append(int(node.get('id')))
            else:
                node = self.node_dict[int(node.get('id'))]
                try:
                    origin_way = next(way for way in self.way_dict.values() if way.begin_node.node_id == node.node_id)
                except StopIteration:
                    print(f"Could not find origin way for origin with node id {node.node_id}")
                    pass
                origin = Origin(chance_of_introducing=20, origin_way=origin_way,
                                cars=self.cars)
                self.origin_dict[node.node_id] = origin

        directions_finder = DirectionsFinder(self.node_dict, self.way_dict)
        for origin in self.origin_dict.values():
            origin_directions_map = {}
            for node in self.term_list:
                directions = directions_finder.find_directions(start_node=origin.origin_way.begin_node.node_id, end_node=node)
                origin_directions_map[node] = directions
            origin.add_directions_map(origin_directions_map)

        print(len(self.way_dict))
        print(len(self.origin_dict))
        print(len(self.node_dict))

