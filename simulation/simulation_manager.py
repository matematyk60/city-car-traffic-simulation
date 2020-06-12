from simulation.node import Node, PositionNode, TraversableNode
from simulation.positioner import Positioner
from simulation.way import Way
from simulation.map import Map
from simulation.car import Car
from simulation.button import Button
from typing import Dict
import time
import pygame
import geopy.distance
import os
from random import randint
from math import atan2, sin, cos, pi


class SimulationManager:

    def __init__(self):
        print("started")
        self.map = Map()

        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        info = pygame.display.Info()
        self.S_WIDTH = 1080
        self.S_HEIGHT = 720
        flags = pygame.RESIZABLE | pygame.DOUBLEBUF
        self.screen = pygame.display.set_mode((self.S_WIDTH, self.S_HEIGHT), flags)
        self.screen.set_alpha(None)
        pygame.display.set_caption("Traffic simulation")
        pygame.event.set_allowed([pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION, pygame.QUIT, pygame.VIDEORESIZE])

        cords_1 = (self.map.maxlat, self.map.minlon)
        cords_2 = (self.map.maxlat, self.map.maxlon)
        self.M_WIDTH = geopy.distance.vincenty(cords_1, cords_2).m
        cords_2 = (self.map.minlat, self.map.minlon)
        self.M_HEIGHT = geopy.distance.vincenty(cords_1, cords_2).m

        self.scale = self.S_HEIGHT / self.M_HEIGHT
        self.map_x = 0
        self.map_y = 0

        self.map_surface = self.draw_map()

        self.buttons = self.create_menu()

    def run_simulation(self):
        node_dict = self.map.node_dict
        origin_dict = self.map.origin_dict
        way_dict = self.map.way_dict
        car_list = self.map.cars

        positioner = Positioner(way_dict)
        while (True):
            for origin in origin_dict.values():
                origin.try_creating_new_car()

            for car in car_list:
                car.make_a_move(positioner)
                if car.reached_destination():
                    print(f"Car [{car}] reached destination ! removing from car list...")
                    car_list.remove(car)
                else:
                    pass
                    # coords = car.get_coordinates()
                    # print(f"Car [{car} has positions [{coords}]]")

            for way in way_dict.values():
                way.rewrite_occupations()

            time.sleep(0.1)

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
            return (0, 0)

    def is_inside_screen(self, coords):
        return 0 < coords[0] + self.map_x < self.S_WIDTH and 0 < coords[1] + self.map_y < self.S_HEIGHT

    def draw_node(self, surface, node, radius):
        coords = self.convert_coords((node.lat, node.long))
        pygame.draw.circle(surface, (0, 0, 0), self.convert_coords((node.lat, node.long)), int(radius * self.scale))

    def draw_way(self, surface, way):
        prev_node = self.convert_coords(way.begin_node.get_coords())

        for node in way.intermediate_nodes:
            curr_node = self.convert_coords(node.get_coords())
            pygame.draw.line(surface, (0, 0, 0), prev_node, curr_node, int(way.lanes * 4 * self.scale))
            prev_node = curr_node

        curr_node = self.convert_coords(way.end_node.get_coords())
        pygame.draw.line(surface, (0, 0, 0), prev_node, curr_node, int(way.lanes * 4 * self.scale))

    def draw_cars(self, surface):
        for car in self.map.cars:
            coords = self.convert_coords(car.get_coordinates())
            if self.is_inside_screen(coords):
                (node_before, node_after) = car.between_nodes()

                before_coords = self.convert_coords(node_before.get_coords())
                after_coords = self.convert_coords(node_after.get_coords())

                angle = atan2(after_coords[1] - before_coords[1], after_coords[0] - before_coords[0]) + pi / 2

                lanes = car.current_lane
                way_lanes = car.current_way.lanes
                lane_distance = self.scale * (((way_lanes - 1) / 2) - (lanes - 1) - 1) * 4
                x = int(coords[0] + cos(angle) * lane_distance)
                y = int(coords[1] + sin(angle) * lane_distance)

                pygame.draw.circle(self.screen, car.color, (x + self.map_x, y + self.map_y), int(1.5 * self.scale))

    def draw_map(self):
        map_surface = pygame.Surface((self.scale * self.M_WIDTH, self.scale * self.M_HEIGHT))
        map_surface.fill((255, 255, 255))

        for way in self.map.way_dict.values():
            self.draw_way(map_surface, way)

        return map_surface

    def draw_menu(self):
        for button in self.buttons:
            button.draw(self.screen)

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.map_surface, (self.map_x, self.map_y))
        self.draw_cars(self.map_surface)
        self.draw_menu()
        pygame.display.flip()

    def create_menu(self):
        buttons = []
        buttons.append(Button(self.S_WIDTH - 310, 10, 200, 25, 'Chance of car spawning:', False))
        buttons.append(Button(self.S_WIDTH - 105, 10, 25, 25, '-', True, self.decrease_spawning_chance))
        buttons.append(Button(self.S_WIDTH - 75, 10, 35, 25, '20%', False))
        buttons.append(Button(self.S_WIDTH - 35, 10, 25, 25, '+', True, self.increase_spawning_chance))
        buttons.append(Button(self.S_WIDTH - 310, 40, 200, 25, 'Number of cars:', False))
        buttons.append(Button(self.S_WIDTH - 105, 40, 95, 25, '0', False))

        return buttons

    def handle_buttons_collisions(self, mouse_pos):
        for button in self.buttons:
            if button.clickable and button.check_collision(mouse_pos):
                button.action()

    def update_buttons(self):
        self.buttons[5].update_text(str(len(self.map.cars)))

    def increase_spawning_chance(self):
        val = int(self.buttons[2].text.replace('%', '')) + 5
        if val <= 100:
            self.buttons[2].update_text(str(val) + '%')

        for origin in self.map.origin_dict.values():
            origin.set_chance(val)

    def decrease_spawning_chance(self):
        val = int(self.buttons[2].text.replace('%', '')) - 5
        if val >= 0:
            self.buttons[2].update_text(str(val) + '%')

        for origin in self.map.origin_dict.values():
            origin.set_chance(val)

    def run(self):
        node_dict = self.map.node_dict
        origin_dict = self.map.origin_dict
        way_dict = self.map.way_dict
        car_list = self.map.cars
        traffic_lights = self.map.traffic_lights
        positioner = Positioner(way_dict)
        time_stmap = time.time()

        self.update_buttons()
        self.draw()

        run = True
        while run:
            # simulation
            if time.time() - time_stmap > 0.1:
                for origin in origin_dict.values():
                    origin.try_creating_new_car()

                for traffic_light in traffic_lights:
                    traffic_light.make_a_move()

                for car in car_list:
                    car.make_a_move(positioner)
                    if car.reached_destination():
                        # print(f"Car [{car}] reached destination ! removing from car list...")
                        car_list.remove(car)
                    else:
                        pass
                        # coords = car.get_coordinates()
                        # print(f"Car [{car} has positions [{coords}]]")

                for way in way_dict.values():
                    way.rewrite_occupations()

                self.update_buttons()

                time_stmap = time.time()

            # pygame
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4 and self.scale < 3:
                        self.scale *= 1.5
                        (x, y) = pygame.mouse.get_pos()
                        self.map_x -= int((x - self.map_x) * 0.5)
                        self.map_y -= int((y - self.map_y) * 0.5)

                        self.map_surface = self.draw_map()
                    elif event.button == 5 and self.scale > 0.07:
                        self.scale /= 1.5
                        (x, y) = pygame.mouse.get_pos()
                        self.map_x -= int((x - self.map_x) * (-1 / 3))
                        self.map_y -= int((y - self.map_y) * (-1 / 3))
                        self.map_surface = self.draw_map()
                    elif event.button == 3:
                        (dx, dy) = pygame.mouse.get_rel()
                        sth = True
                    else:
                        self.handle_buttons_collisions(pygame.mouse.get_pos())
                elif event.type == pygame.MOUSEMOTION and event.buttons[2]:
                    (dx, dy) = pygame.mouse.get_rel()
                    self.map_x += dx
                    self.map_y += dy
                elif event.type == pygame.VIDEORESIZE:
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

            self.draw()
            # time.sleep(0.1)

        pygame.quit()
        print("end")
