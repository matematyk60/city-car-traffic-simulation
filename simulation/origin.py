from simulation.way import Way
from typing import Dict, List
from simulation.car import Car
from random import randint


class Origin:

    def __init__(self, chance_of_introducing: int, origin_way: Way, destination_node_id: int,
                 directions_map: Dict[int, int], cars: List[Car]):
        self.chance_of_introducing = chance_of_introducing
        self.origin_way = origin_way
        self.destination_node_id = destination_node_id
        self.directions_map = directions_map
        self.cars = cars
        self.car_queue = []

    def try_creating_new_car(self):
        value = randint(0, 100)
        if value < self.chance_of_introducing:
            car = Car(current_way=self.origin_way, current_lane=0, directions_map=self.directions_map, way_position=0,
                      destination_node_id=self.destination_node_id, v=0, v_max=20, acc=10)
            self.car_queue.append(car)
        self.try_introducing_new_car()

    def try_introducing_new_car(self):
        if len(self.car_queue) != 0 and not self.origin_way.lane_occupations[0].occupations[0].occupied:
            car = self.car_queue.pop(0)
            self.cars.append(car)
