from simulation.road_object import Car,StopLight
from simulation.road import RoadPoint, RoadLane, RoadWay

import time


class SimulationManager:

    def __init__(self):
        car = Car(lane_number=0, start_position=0, v_max = 10, acc=30)
        stop_light = StopLight(position=40, redlight_every=1, redlight_duration=1000)
        lane_points = []
        for i in range(1, 10000):
            lane_points.append(RoadPoint(usable=True))
        road_lane = RoadLane(1, lane_points)
        road_way = RoadWay(clock_wise=True)
        road_way.add_road_lane(road_lane)
        road_way.add_object(car)
        road_way.add_object(stop_light)
        self.road_way = road_way


    def run(self):
        while True:
            time.sleep(1)
            self.road_way.make_a_move()
            self.road_way.paint()
