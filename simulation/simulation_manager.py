from simulation.node import Node, PositionNode, TraversableNode
from simulation.way import Way
from simulation.map import Map
from simulation.car import Car
from typing import Dict
import time
import pygame
import geopy.distance
import os


class SimulationManager:

    def __init__(self):
        print("started")
        self.map = Map()

        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        info = pygame.display.Info() # You have to call this before pygame.display.set_mode()
        self.S_WIDTH = 1080
        self.S_HEIGHT = 720
        self.screen = pygame.display.set_mode((self.S_WIDTH, self.S_HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Traffic simulation")

        cords_1 = (self.map.maxlat, self.map.minlon)
        cords_2 = (self.map.maxlat, self.map.maxlon)
        self.M_WIDTH = geopy.distance.vincenty(cords_1, cords_2).m
        cords_2 = (self.map.minlat, self.map.minlon)
        self.M_HEIGHT = geopy.distance.vincenty(cords_1, cords_2).m

        self.scale = self.S_HEIGHT/ self.M_HEIGHT
        self.map_x = 0
        self.map_y = 0

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

    def draw_node(self, surface, node):
        pygame.draw.circle(surface, (0,0,255), self.convert_coords((node.lat, node.long)), int(1.5 * self.scale))


    def draw_way(self, surface, way):
        node_list = []        
        node_list.append(self.convert_coords(way.begin_node.get_coords()))

        if node_list[0][0] + self.map_x > 2 * self.S_WIDTH or node_list[0][1] + self.map_y > 2 * self.S_HEIGHT:
            return

        for node in way.intermediate_nodes:
            node_list.append(self.convert_coords(node.get_coords()))

        node_list.append(self.convert_coords(way.end_node.get_coords()))


        pygame.draw.lines(surface, (0, 0, 0), False, node_list, int(way.lanes * 4 * self.scale))
        self.draw_node(surface, way.begin_node)
        self.draw_node(surface, way.end_node)

    def draw_car(self, surface, car):
        coords = Way.coords_of_distance(car.way_position)
        pygame.draw.circle(surface, (0,0,255), self.convert_coords(coords), int(1.5 * self.scale))


    def draw_map(self):
        self.screen.fill((255,255,255))
        
        map_surface = pygame.Surface((self.scale * self.M_WIDTH, self.scale * self.M_HEIGHT))
        map_surface.fill((255,255,255))

        for way in self.map.way_dict.values():
            self.draw_way(map_surface, way)

        # for node in self.map.node_dict.values():
        #     coords = node.get_coords()
        #     if coords[0] + self.map_x > self.S_WIDTH or coords[1] + self.map_y > self.S_HEIGHT:
        #         continue
        #     pygame.draw.circle(map_surface, (0,0,255), self.convert_coords(coords), int(2 * self.scale))


        self.screen.blit(map_surface, (self.map_x, self.map_y))
        pygame.display.flip()


    def run(self):
        self.draw_map()

        run = True
        while run:
            events = pygame.event.get()
            for event in events:        
                sth = False
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4 and self.scale < 3:
                        self.scale *= 1.5
                        (x, y) = pygame.mouse.get_pos()
                        self.map_x -= int((x - self.map_x) * 0.5)
                        self.map_y -= int((y - self.map_y) * 0.5)
                    elif event.button == 5 and self.scale > 0.07:
                        self.scale /= 1.5
                        (x, y) = pygame.mouse.get_pos()
                        self.map_x -= int((x - self.map_x) * (-1/3))
                        self.map_y -= int((y - self.map_y) * (-1/3))
                    elif event.button == 3:
                        (dx, dy) = pygame.mouse.get_rel()
                        sth = True
                    self.draw_map()
                elif event.type == pygame.MOUSEMOTION and event.buttons[2]:
                    (dx, dy) = pygame.mouse.get_rel()
                    self.map_x += dx
                    self.map_y += dy
                    self.draw_map()
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.draw_map()

            

        pygame.quit()
        print("end")
