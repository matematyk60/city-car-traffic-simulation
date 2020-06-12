from simulation.node import Node, PositionNode, TraversableNode
from simulation.positioner import Positioner
from simulation.way import Way
from simulation.map import Map
from simulation.car import Car
from simulation.button import Button
from simulation.statistics import Statistics
from typing import Dict
import time
import pygame
import geopy.distance
import os
from random import randint
from math import atan2, sin, cos, pi, sqrt


class SimulationManager:

    def __init__(self):
        print("started")
        self.map = Map()
        self.statistics = Statistics(self.map.way_dict)
        self.simulation_counter = 0

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

        self.selected = 0

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
            pygame.draw.line(surface, way.color, prev_node, curr_node, int(way.lanes * 4 * self.scale))
            prev_node = curr_node

        curr_node = self.convert_coords(way.end_node.get_coords())
        pygame.draw.line(surface, way.color, prev_node, curr_node, int(way.lanes * 4 * self.scale))

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
        for button in self.buttons.values():
            button.draw(self.screen)

    def draw_traffic_lights(self, surface):
        for traffic_lights in self.map.traffic_lights:
            greens = traffic_lights.get_green_lights()
            reds = traffic_lights.get_red_lights()

            for tl in greens:
                node = tl.node
                coords = self.convert_coords(node.get_coords())

                if self.is_inside_screen(coords):
                    way = tl.ways[0]
                    nodepair = next(x[1] for x in way.ranges if (x[1][0] == node or x[1][1] == node))
                    if nodepair[0] == node: 
                        node_before = nodepair[1] 
                    else:
                        node_before = nodepair[0]
                    before_coords = self.convert_coords(node_before.get_coords())

                    angle = atan2(coords[1] - before_coords[1], coords[0] - before_coords[0]) + pi / 2

                    distance = self.scale * 10
                    x = int(coords[0] + cos(angle) * distance)
                    y = int(coords[1] + sin(angle) * distance)

                    pygame.draw.circle(surface, (0, 255, 0), (x, y), int(4 * self.scale))

            for tl in reds:
                node = tl.node
                coords = self.convert_coords(node.get_coords())

                if self.is_inside_screen(coords):
                    way = tl.ways[0]
                    nodepair = next(x[1] for x in way.ranges if (x[1][0] == node or x[1][1] == node))
                    if nodepair[0] == node: 
                        node_before = nodepair[1] 
                    else:
                        node_before = nodepair[0]
                    before_coords = self.convert_coords(node_before.get_coords())

                    angle = atan2(coords[1] - before_coords[1], coords[0] - before_coords[0]) + pi / 2

                    distance = self.scale * 10
                    x = int(coords[0] + cos(angle) * distance)
                    y = int(coords[1] + sin(angle) * distance)

                    pygame.draw.circle(surface, (255, 0, 0), (x, y), int(4 * self.scale))

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.draw_traffic_lights(self.map_surface)
        self.screen.blit(self.map_surface, (self.map_x, self.map_y))
        self.draw_cars(self.map_surface)
        self.draw_menu()
        pygame.display.flip()

    def create_menu(self):
        buttons = {}
        buttons[0] = Button(self.S_WIDTH - 310, 10, 200, 25, 'Chance of car spawning:', False)
        buttons[1] = Button(self.S_WIDTH - 105, 10, 25, 25, '-', True, self.decrease_spawning_chance)
        buttons['spawning_chance'] = Button(self.S_WIDTH - 75, 10, 35, 25, '20%', False)
        buttons[2] = Button(self.S_WIDTH - 35, 10, 25, 25, '+', True, self.increase_spawning_chance)
        buttons[3] = Button(self.S_WIDTH - 310, 40, 200, 25, 'Number of cars:', False)
        buttons['car_number'] = Button(self.S_WIDTH - 105, 40, 95, 25, '0', False)
        buttons[4] = Button(self.S_WIDTH - 310, 70, 200, 25, 'Average speed:', False)
        buttons['average_speed'] = Button(self.S_WIDTH - 105, 70, 95, 25, '0', False)
        return buttons

    def update_menu(self):
        self.buttons[5] = Button(self.S_WIDTH - 310, 100, 200, 25, f'Number of cars on {self.selected}:', False)
        self.buttons['selection_car_number'] = Button(self.S_WIDTH - 105, 100, 95, 25, '0', False)
        self.buttons[6] = Button(self.S_WIDTH - 310, 130, 200, 25, f'Average speed of {self.selected}:', False)
        self.buttons['selection_speed'] = Button(self.S_WIDTH - 105, 130, 95, 25, '0', False)
        self.buttons[7] = Button(self.S_WIDTH - 310, 160, 200, 25, f'Flow of {self.selected}:', False)
        self.buttons['selection_flow'] = Button(self.S_WIDTH - 105, 160, 95, 25, '0', False)

    def calculate_distance(self, p, q, r):
        a = q[0] - p[0]
        b = q[1] - p[1]
        numerator = abs(b*r[0] - a*r[1] + q[0]*p[1] - q[1]*p[0])
        denominator = sqrt(a**2 + b**2)

        # print(f'{a}, {b}, {numerator} / {denominator} ', end=' ')

        return numerator / denominator

    def is_in_proximity(self, p, q, r):
        return min(p[0], q[0]) - 5 < r[0] < max(p[0], q[0]) + 5 and min(p[1], q[1]) - 5 < r[1] < max(p[1], q[1]) + 5

    def handle_way_collisions(self, mouse_pos):
        (x, y) = mouse_pos
        x -= self.map_x
        y -= self.map_y
        for way in self.map.way_dict.values():
            # if way.way_id != 25049529:
            #     continue

            prev_node = self.convert_coords(way.begin_node.get_coords())
            for node in way.intermediate_nodes:
                curr_node = self.convert_coords(node.get_coords())
                try:
                    distance = self.calculate_distance(prev_node, curr_node, (x, y))
                    if distance <= way.lanes*10 and self.is_in_proximity(prev_node, curr_node, (x, y)):
                        if self.selected != 0:
                            self.map.way_dict[self.selected].color = (0, 0, 0)
                        self.selected = way.way_id
                        self.map.way_dict[self.selected].color = (127, 127, 127)
                        self.update_menu()
                        self.map_surface = self.draw_map()
                        return
                except ZeroDivisionError:
                    pass
                prev_node = curr_node

            curr_node = self.convert_coords(way.end_node.get_coords())
            try:
                distance = self.calculate_distance(prev_node, curr_node, (x, y))
                if distance <= way.lanes*10 and self.is_in_proximity(prev_node, curr_node, (x, y)):
                    if self.selected != 0:
                        self.map.way_dict[self.selected].color = (0, 0, 0)
                    self.selected = way.way_id
                    self.map.way_dict[self.selected].color = (127, 127, 127)
                    self.update_menu()
                    self.map_surface = self.draw_map()
                    return
            except ZeroDivisionError:
                pass

    def handle_buttons_collisions(self, mouse_pos):
        for button in self.buttons.values():
            if button.check_collision(mouse_pos):
                if button.clickable:
                    button.action()
                return True
        return False

    def update_buttons(self):
        self.buttons['car_number'].update_text(str(len(self.map.cars)))
        self.buttons['average_speed'].update_text(str(round(self.statistics.get_average_speed() * 3.6, 1)) + ' km/h')
        if self.selected != 0:
            self.buttons['selection_car_number'].update_text(str(self.statistics.get_way_car_number(self.selected)))
            self.buttons['selection_speed'].update_text(str(round(self.statistics.get_way_average_speed(self.selected) * 3.6, 1)) + ' km/h')
            if self.simulation_counter == 0:
                self.buttons['selection_flow'].update_text(str(self.statistics.get_way_flow(self.selected)) + ' veh/min')

    def increase_spawning_chance(self):
        val = int(self.buttons['spawning_chance'].text.replace('%', '')) + 5
        if val <= 100:
            self.buttons['spawning_chance'].update_text(str(val) + '%')

        for origin in self.map.origin_dict.values():
            origin.set_chance(val)

    def decrease_spawning_chance(self):
        val = int(self.buttons['spawning_chance'].text.replace('%', '')) - 5
        if val >= 0:
            self.buttons['spawning_chance'].update_text(str(val) + '%')

        for origin in self.map.origin_dict.values():
            origin.set_chance(val)

    def run(self):
        node_dict = self.map.node_dict
        origin_dict = self.map.origin_dict
        way_dict = self.map.way_dict
        car_list = self.map.cars
        traffic_lights = self.map.traffic_lights
        positioner = Positioner(way_dict)
        time_stamp = time.time()

        self.update_buttons()
        self.draw()

        run = True
        while run:
            # simulation
            if time.time() - time_stamp > 0.1:
                time_stamp = time.time()

                for origin in origin_dict.values():
                    origin.try_creating_new_car()

                for traffic_light in traffic_lights:
                    traffic_light.make_a_move()

                self.statistics.reset_average_speed()
                for car in car_list:
                    car.make_a_move(positioner)
                    if car.reached_destination():
                        # print(f"Car [{car}] reached destination ! removing from car list...")
                        car_list.remove(car)
                    else:
                        pass
                        # coords = car.get_coordinates()
                        # print(f"Car [{car} has positions [{coords}]]")
                    self.statistics.register_move(car)

                for way in way_dict.values():
                    way.rewrite_occupations()

                self.update_buttons()

                if self.simulation_counter == 0:
                    self.statistics.reset_flow()

                self.simulation_counter += 1
                self.simulation_counter %= 60

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
                        elif event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            if not(self.handle_buttons_collisions(mouse_pos) or self.screen.get_at(mouse_pos) == (255,255,255)):
                                self.handle_way_collisions(mouse_pos)
                    elif event.type == pygame.MOUSEMOTION and event.buttons[2]:
                        (dx, dy) = pygame.mouse.get_rel()
                        self.map_x += dx
                        self.map_y += dy
                    elif event.type == pygame.VIDEORESIZE:
                        self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

                self.draw()

        pygame.quit()
        print("end")
