from simulation.road_object import Car, StopLight
from simulation.road import RoadPoint, RoadLane, RoadWay
from simulation.node import Node, PositionNode, TraversableNode
from simulation.way import Way
from simulation.map import Map
from typing import Dict
import time
import pygame
import geopy.distance


class SimulationManager:

    def __init__(self):
        print("started")
        self.map = Map()
        pygame.init()
        self.S_WIDTH = 1080
        self.S_HEIGHT = 720
        self.screen = pygame.display.set_mode((self.S_WIDTH, self.S_HEIGHT))
        pygame.display.set_caption("Traffic simulation")

        cords_1 = (self.map.maxlat, self.map.minlon)
        cords_2 = (self.map.maxlat, self.map.maxlon)
        self.M_WIDTH = geopy.distance.vincenty(cords_1, cords_2).m
        cords_2 = (self.map.minlat, self.map.minlon)
        self.M_HEIGHT = geopy.distance.vincenty(cords_1, cords_2).m

        self.scale = self.S_HEIGHT/ self.M_HEIGHT


        # self.node_dict = {}
        # self.way = self.create_way(node_dict=self.node_dict)
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

    def convert_coords(self, coords):
        (lat, long) = coords
        if self.map.minlat < lat < self.map.maxlat or self.map.minlat < lat < self.map.maxlat:
            cords_1 = (lat, long)
            cords_2 = (lat, self.map.minlon)
            x = int(self.scale * geopy.distance.vincenty(cords_1, cords_2).m)
            cords_2 = (self.map.maxlat, long)
            y = int(self.scale * geopy.distance.vincenty(cords_1, cords_2).m)
            return (x, y)
        else:
            print(f"({lat}, {long}) is outside the map")
            return (0,0)


    def draw_way(self, way):
        node_list = []        
        node_list.append(self.convert_coords(way.begin_node.get_coords()))

        for node in way.intermediate_nodes:
            node_list.append(self.convert_coords(node.get_coords()))

        node_list.append(self.convert_coords(way.end_node.get_coords()))


        pygame.draw.lines(self.screen, (0, 0, 0), False, node_list, 5)


    def draw_map(self):
        self.screen.fill((255,255,255))

        #pygame.draw.lines(self.screen, (0, 0, 0), False, [(10, 10), (20, 30), (150, 400), (800, 700)], 10)

        for way in self.map.way_dict.values():
            self.draw_way(way)

        for node in self.map.node_dict.values():
            coords = node.get_coords()
            pygame.draw.circle(self.screen, (0,0,255), self.convert_coords(coords), 1)

        pygame.display.flip()


    def run(self):
        # print(self.node_dict[269325414])
        # print(self.node_dict[2264896423])
        # print(self.way.coords_of_distance(7))
        self.draw_map()

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
            

        pygame.quit()
        print("end")
