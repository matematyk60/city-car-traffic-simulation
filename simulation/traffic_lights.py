from dataclasses import dataclass
from typing import List

from simulation.node import TraversableNode
from simulation.way import Way


@dataclass
class TrafficLights:
    node: TraversableNode
    ways: List[Way]


class TrafficLightsManager:
    def make_a_move(self):
        pass


class TwoWayTrafficLightsManager(TrafficLightsManager):
    def __init__(self, x_direction_lights: List[TrafficLights], y_direction_lights: List[TrafficLights], x_duration: int, y_duration: int):
        self.x_direction_lights = x_direction_lights
        self.y_direction_lights = y_direction_lights
        self.counter = 0
        self.interval = x_duration
        self.has_break = False
        self.current_direction = 0  # 0 stands for X, 1 stands for Y
        self.x_duration = x_duration
        self.y_duration = y_duration

    def make_a_move(self):
        if self.has_break:
            if self.counter >= 10:
                self.has_break = False
                self.counter = 0
            else:
                lights = self.x_direction_lights + self.y_direction_lights
        if not self.has_break:
            if self.counter >= self.interval:
                self.counter = 0
                self.has_break = True
                self.current_direction = 1 if self.current_direction == 0 else 0
                self.interval = self.y_duration if self.current_direction == 0 else self.x_duration
            if self.current_direction == 0:
                lights = self.x_direction_lights
            else:
                lights = self.y_direction_lights
        for light in lights:
            for way in light.ways:
                way.mark_node_occupation(light.node.node_id)
        self.counter += 1


class ThreeWayTrafficLightsManager(TrafficLightsManager):
    def __init__(self, x_direction_lights: List[TrafficLights], y_direction_lights: List[TrafficLights],
                 z_direction_lights):
        self.x_direction_lights = x_direction_lights
        self.y_direction_lights = y_direction_lights
        self.z_direction_lights = z_direction_lights
        self.counter = 0
        self.interval = 60
        self.has_break = False
        self.current_direction = 0  # 0 stands for X, 1 stands for Y, 2 stands for Z

    def make_a_move(self):
        if self.has_break:
            if self.counter >= 10:
                self.has_break = False
                self.counter = 0
            else:
                green_lights = []
                lights = self.x_direction_lights + self.y_direction_lights + self.z_direction_lights
        if not self.has_break:
            if self.counter >= self.interval:
                self.counter = 0
                self.has_break = True
                if self.current_direction == 0:
                    self.current_direction = 1
                elif self.current_direction == 1:
                    self.current_direction = 2
                else:
                    self.current_direction = 0
            if self.current_direction == 0:
                green_lights = self.x_direction_lights
                lights = self.y_direction_lights + self.z_direction_lights
            elif self.current_direction == 1:
                green_lights = self.y_direction_lights
                lights = self.x_direction_lights + self.z_direction_lights
            else:
                green_lights = self.z_direction_lights
                lights = self.x_direction_lights + self.y_direction_lights
        for light in lights:
            for way in light.ways:
                should_mark_occupation = True
                for green_light in green_lights:
                    if way in green_light.ways:
                        should_mark_occupation = False
                if should_mark_occupation:
                    way.mark_node_occupation(light.node.node_id)
        self.counter += 1

    def not_in(self, should_be_not_in, lights):
        return filter(lambda l: l.node.node_id not in map(lambda l_: l_.node.node_id, should_be_not_in), lights)
