import xml.etree.ElementTree as ET
from simulation.way import Way
from simulation.node import Node, TraversableNode

class Map:
    def __init__(self):
        self.node_dict = {}
        self.way_dict = {}

        root = ET.parse('./obwodnica.osm').getroot()
        
        for node in root.findall('node'):
            node_id = int(node.get('id'))
            lat = float(node.get('lat'))
            lon = float(node.get('lon'))
            self.node_dict[node_id] = TraversableNode(node_id, lat, lon)

        for way in root.findall('way'):
            way_id = int(way.get('id'))
            nodes = way.findall('nd')
            begining = nodes.pop(0)
            begining_id = int(begining.get('ref'))

            #some ways have just one node, we ignore them
            #to do: remove them from obwodnica.osm
            try:
                end = nodes.pop()
                end_id = int(end.get('ref'))
            except IndexError:
                continue
            

            intermediate_nodes = []
            for node in nodes:
                node_id = int(node.get('ref'))
                intermediate_nodes.append(self.node_dict[node_id])

            self.way_dict[way_id] = Way(way_id, self.node_dict[begining_id], self.node_dict[end_id], intermediate_nodes)
            self.node_dict[begining_id].add_outgoing_way(self.way_dict[way_id])
            