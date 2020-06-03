from typing import List
import simulation.road as road_
import math

class RoadObject:
    def paint_yourself(self):
        pass

    def mark_new_position(self, road_way: road_.RoadWay, fresh_lanes: List[road_.RoadLane]):
        pass


class Car(RoadObject):
    def __init__(self, lane_number: int, start_position: int, v_max: int, acc: int):
        self.v = 0
        self.v_max = v_max
        self.start_position = start_position
        self.position = start_position
        self.lane_number = lane_number
        self.acc = acc

    def paint_yourself(self):
        print(f"I have position of {self.position}, current velocity {self.v}, and lane_number {self.lane_number}")

    def mark_new_position(self, road_way: road_.RoadWay, fresh_lanes: List[road_.RoadLane]):
        my_lane = road_way.lanes[self.lane_number]
        distance_to_next_object = self.get_next_object_position(my_lane, self.v + self.acc)
        self.v = min(self.v + self.acc, self.v_max, distance_to_next_object - 1)

        self.position += self.v

        fresh_lanes[self.lane_number].points[self.position].occupied = True

    def get_next_object_position(self, my_lane, distance):
        distance_to_next_object = distance + 1
        for i in range(0, distance):
            if my_lane.points[self.position + i + 1].occupied:
                distance_to_next_object = i + 1
                break
        return distance_to_next_object



class StopLight(RoadObject):
    def __init__(self, position: int, redlight_every: int, redlight_duration: int):
        self.position = position
        self.redlight_every = redlight_every
        self.redlight_duration = redlight_duration
        self.redlight = True
        self.timer = 0

    def paint_yourself(self):
        print(f"I have position of {self.position}, and redlight {self.redlight}")

    def mark_new_position(self, road_way: road_.RoadWay, fresh_lanes: List[road_.RoadLane]):
        self.timer += 1
        if self.redlight:
            if self.timer >= self.redlight_duration :
                self.redlight = False
                self.timer = 0
            else:
                for lane in fresh_lanes:
                    lane.points[self.position].occupied = True
        else:
            if self.timer >= self.redlight_every:
                self.redlight = True
                self.timer = 0