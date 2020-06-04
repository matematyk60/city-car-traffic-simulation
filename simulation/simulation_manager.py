from simulation.road_object import Car, StopLight
from simulation.road import RoadPoint, RoadLane, RoadWay
from simulation.node import Node, PositionNode, TraversableNode
from simulation.way import Way
from simulation.map import Map
from typing import Dict
import time


class SimulationManager:

    def __init__(self):
        print("started")
        Map()
        self.node_dict = {}
        self.way = self.create_way(node_dict=self.node_dict)
    # car = Car(lane_number=0, start_position=0, v_max = 10, acc=30)
    # stop_light = StopLight(position=40, redlight_every=1, redlight_duration=1000)
    # lane_points = []
    # for i in range(1, 10000):
    #     lane_points.append(RoadPoint(usable=True))
    # road_lane = RoadLane(1, lane_points)
    # road_way = RoadWay(clock_wise=True)
    # road_way.add_road_lane(road_lane)
    # road_way.add_object(car)
    # road_way.add_object(stop_light)
    # self.road_way = road_way

    def create_way(self, node_dict: Dict[int, Node]):
        way_id = 24787456
        begin_node_id = 269325414
        end_node_id = 2264896423
        if begin_node_id in node_dict:
            begin_node = node_dict[begin_node_id]
        else:
            begin_node = TraversableNode(node_id=begin_node_id, lat=50.07399, long=19.9460753)
            node_dict[begin_node_id] = begin_node
        if end_node_id in node_dict:
            end_node = node_dict[end_node_id]
        else:
            end_node = TraversableNode(node_id=end_node_id, lat=50.0738616, long=19.9461729)
            node_dict[end_node_id] = end_node
        way = Way(way_id=way_id, begin_node=begin_node, end_node=end_node, lanes=2, intermediate_nodes=[])
        begin_node.add_outgoing_way(way)
        return way


    def run(self):
        print(self.node_dict[269325414])
        print(self.node_dict[2264896423])
        print(self.way.coords_of_distance(7))
