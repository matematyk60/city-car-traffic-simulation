import xml.etree.ElementTree as ET
from simulation.way import Way
from simulation.node import Node, TraversableNode


class Map:
    def __init__(self):
        self.node_dict = {}
        self.way_dict = {}
        self.origins = {}

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

        # print(len(self.way_dict))
