import xml.etree.ElementTree as ET

from simulation.directions_finder import DirectionsFinder
from simulation.origin import Origin
from simulation.traffic_lights import TrafficLights, TrafficLightsManager, TwoWayTrafficLightsManager, \
    ThreeWayTrafficLightsManager
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
            if node_id == '272305554':
                print("IM HERE")
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

            try:
                name = next(tag.get("v") for tag in way.findall("tag") if tag.get("k") == "name")
            except StopIteration:
                name = 'Brak nazwy ulicy'

            try:
                max_speed = next(int(tag.get("v")) for tag in way.findall("tag") if tag.get("k") == "maxspeed")
            except StopIteration:
                name = 'Brak nazwy ulicy'

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
                                        intermediate_nodes, name, max_speed)
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
                directions = directions_finder.find_directions(start_node=origin.origin_way.begin_node.node_id,
                                                               end_node=node)
                origin_directions_map[node] = directions
            origin.add_directions_map(origin_directions_map)
        self.traffic_lights = [
            self.create_three_way_traffic_lights(x_nodes_ids=[1798870688, 1798870692], y_nodes_ids=[272305554],
                                                 z_nodes_ids=[1798870686]),
            # R.Mogilskie
            self.create_two_way_traffic_lights(x_nodes_ids=[2070095601], y_nodes_ids=[207460778], x_duration=50,
                                               y_duration=10),
            # M. Konopnickiej
            self.create_zwierzyniecka_lights(),  # Zwierzyniecka
            self.create_three_way_traffic_lights(x_nodes_ids=[1798872942, 1798872935], y_nodes_ids=[1798872941],
                                                 z_nodes_ids=[-126734]),
            # Focha
            self.create_reymonta_lights(),
            self.create_three_way_traffic_lights(x_nodes_ids=[1798898144, 1448506739],
                                                 y_nodes_ids=[1448506737, 236160046, 1798898144],
                                                 z_nodes_ids=[-126337, 5331206462, 1448506737]),  # czarnowiejska
            self.create_two_way_traffic_lights(x_nodes_ids=[2264896425], y_nodes_ids=[269325575], x_duration=30,
                                               y_duration=30),
            # al. 29 listopada
            self.create_rakowicka_lights(),
            self.create_mogilskie_lights(),
            self.create_three_way_traffic_lights(x_nodes_ids=[311337240, 595751022],
                                                 y_nodes_ids=[595751016],
                                                 z_nodes_ids=[595751038]),  # grzegorzeckie

        ]

        print(len(self.way_dict))
        print(len(self.origin_dict))
        print(len(self.node_dict))

    def create_zwierzyniecka_lights(self):
        x_lights = [TrafficLights(self.node_dict[2419720318],
                                  [self.way_dict[277117067], self.way_dict[126106951], self.way_dict[101322354]]),
                    TrafficLights(self.node_dict[1876808668],
                                  [self.way_dict[277117076], self.way_dict[126106951], self.way_dict[255472409]]),
                    TrafficLights(self.node_dict[1169737316],
                                  [self.way_dict[372635649], self.way_dict[101322361], self.way_dict[204041393]]),
                    TrafficLights(self.node_dict[207440039],
                                  [self.way_dict[204041393], self.way_dict[126106953], self.way_dict[29325724]])]

        y_lights = [TrafficLights(self.node_dict[207440039],
                                  [self.way_dict[216987196], self.way_dict[126106953], self.way_dict[29325724]]),
                    TrafficLights(self.node_dict[2419720318],
                                  [self.way_dict[29325724], self.way_dict[101322354], self.way_dict[126106951]]),
                    TrafficLights(self.node_dict[1876808668],
                                  [self.way_dict[126106951], self.way_dict[277117076], self.way_dict[255472409]])]

        z_lights = [TrafficLights(self.node_dict[1876808668],
                                  [self.way_dict[216988890], self.way_dict[277117076], self.way_dict[255472409]]),
                    TrafficLights(self.node_dict[1169737316],
                                  [self.way_dict[255472409], self.way_dict[101322361], self.way_dict[204041393]]),
                    TrafficLights(self.node_dict[207440039],
                                  [self.way_dict[204041393], self.way_dict[126106953], self.way_dict[29325724]])]

        return ThreeWayTrafficLightsManager(x_lights, y_lights, z_lights)

    def create_reymonta_lights(self):
        x_lights = [TrafficLights(self.node_dict[262210524],
                                  [self.way_dict[431445485], self.way_dict[431516755], self.way_dict[431445483]]),
                    TrafficLights(self.node_dict[236151783],
                                  [self.way_dict[118304895], self.way_dict[277117078], self.way_dict[-107594]])]

        y_lights = [TrafficLights(self.node_dict[262210524],
                                  [self.way_dict[240869998], self.way_dict[431445483], self.way_dict[431516755]]),
                    TrafficLights(self.node_dict[236151783],
                                  [self.way_dict[431445483], self.way_dict[277117078], self.way_dict[-107594]])]

        z_lights = [TrafficLights(self.node_dict[262210524],
                                  [self.way_dict[-107594], self.way_dict[29325983], self.way_dict[431516755]]),
                    TrafficLights(self.node_dict[236151783],
                                  [self.way_dict[277117078], self.way_dict[118304895], self.way_dict[-107594]])]

        return ThreeWayTrafficLightsManager(x_lights, y_lights, z_lights)

    def create_rakowicka_lights(self):
        x_lights = [TrafficLights(self.node_dict[269325450],
                                  [self.way_dict[217178032], self.way_dict[24787452], self.way_dict[75391389]]),
                    TrafficLights(self.node_dict[251691164],
                                  [self.way_dict[114324807], self.way_dict[24787450], self.way_dict[-109284]])]

        y_lights = [TrafficLights(self.node_dict[269325450],
                                  [self.way_dict[47197017], self.way_dict[75391389], self.way_dict[24787452],
                                   self.way_dict[-109284], self.way_dict[-109319]]),
                    TrafficLights(self.node_dict[251691164],
                                  [self.way_dict[75391389], self.way_dict[138750246], self.way_dict[24787450]])]

        z_lights = [TrafficLights(self.node_dict[269325450],
                                  [self.way_dict[-109284], self.way_dict[24787452], self.way_dict[-109319]]),
                    TrafficLights(self.node_dict[251691164],
                                  [self.way_dict[-109228], self.way_dict[-109284], self.way_dict[24787450]])]

        return ThreeWayTrafficLightsManager(x_lights, y_lights, z_lights)

    def create_mogilskie_lights(self):
        x_lights = [TrafficLights(self.node_dict[226020630],
                                  [self.way_dict[242917513], self.way_dict[114324811]]),
                    TrafficLights(self.node_dict[206371898],
                                  [self.way_dict[217406135], self.way_dict[187685308], self.way_dict[19803399]]),
                    TrafficLights(self.node_dict[206371894],
                                  [self.way_dict[180640939], self.way_dict[82749515]]),
                    TrafficLights(self.node_dict[262504277],
                                  [self.way_dict[180640933], self.way_dict[217162193]]),
                    TrafficLights(self.node_dict[206371912],
                                  [self.way_dict[533275337], self.way_dict[37828460]])]

        y_lights = [TrafficLights(self.node_dict[226020630],
                                  [self.way_dict[37828459], self.way_dict[114324811]]),
                    TrafficLights(self.node_dict[206371898],
                                  [self.way_dict[217162188], self.way_dict[187685308], self.way_dict[19803399]]),
                    TrafficLights(self.node_dict[206371894],
                                  [self.way_dict[368152910], self.way_dict[82749515]]),
                    TrafficLights(self.node_dict[262504277],
                                  [self.way_dict[306884065], self.way_dict[217162193]]),
                    TrafficLights(self.node_dict[206371912],
                                  [self.way_dict[533275337], self.way_dict[37828460]])]

        z_lights = [TrafficLights(self.node_dict[226020630],
                                  [self.way_dict[242917513], self.way_dict[114324811]]),
                    TrafficLights(self.node_dict[206371898],
                                  [self.way_dict[217406135], self.way_dict[187685308], self.way_dict[19803399]]),
                    TrafficLights(self.node_dict[206371894],
                                  [self.way_dict[180640939], self.way_dict[82749515]]),
                    TrafficLights(self.node_dict[262504277],
                                  [self.way_dict[217162193]]),
                    TrafficLights(self.node_dict[206371912],
                                  [self.way_dict[368325413], self.way_dict[37828460]])]

        return ThreeWayTrafficLightsManager(x_lights, y_lights, z_lights)

    def create_two_way_traffic_lights(self, x_nodes_ids, y_nodes_ids, x_duration, y_duration):
        x_lights = []
        for node_id in x_nodes_ids:
            node = self.node_dict[node_id]
            node_ways = []
            for way in self.way_dict.values():
                if way.begin_node == node or way.end_node == node or node in way.intermediate_nodes:
                    node_ways.append(way)
            if len(node_ways) == 0:
                print(f"Could not find ways for traffic light node with id {node.node_id}")
            x_lights.append(TrafficLights(node, node_ways))

        y_lights = []
        for node_id in y_nodes_ids:
            node = self.node_dict[node_id]
            node_ways = []
            for way in self.way_dict.values():
                if way.begin_node == node or way.end_node == node or node in way.intermediate_nodes:
                    node_ways.append(way)
            if len(node_ways) == 0:
                print(f"Could not find ways for traffic light node with id {node.node_id}")
            y_lights.append(TrafficLights(node, node_ways))
        return TwoWayTrafficLightsManager(x_lights, y_lights, x_duration, y_duration)

    def create_three_way_traffic_lights(self, x_nodes_ids, y_nodes_ids, z_nodes_ids):
        x_lights = []
        for node_id in x_nodes_ids:
            node = self.node_dict[node_id]
            node_ways = []
            for way in self.way_dict.values():
                if way.begin_node == node or way.end_node == node or node in way.intermediate_nodes:
                    node_ways.append(way)
            if len(node_ways) == 0:
                print(f"Could not find ways for traffic light node with id {node.node_id}")
            x_lights.append(TrafficLights(node, node_ways))

        y_lights = []
        for node_id in y_nodes_ids:
            node = self.node_dict[node_id]
            node_ways = []
            for way in self.way_dict.values():
                if way.begin_node == node or way.end_node == node or node in way.intermediate_nodes:
                    node_ways.append(way)
            if len(node_ways) == 0:
                print(f"Could not find ways for traffic light node with id {node.node_id}")
            y_lights.append(TrafficLights(node, node_ways))

        z_lights = []
        for node_id in z_nodes_ids:
            node = self.node_dict[node_id]
            node_ways = []
            for way in self.way_dict.values():
                if way.begin_node == node or way.end_node == node or node in way.intermediate_nodes:
                    node_ways.append(way)
            if len(node_ways) == 0:
                print(f"Could not find ways for traffic light node with id {node.node_id}")
            z_lights.append(TrafficLights(node, node_ways))
        return ThreeWayTrafficLightsManager(x_lights, y_lights, z_lights)
