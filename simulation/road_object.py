from typing import Optional
from typing import List
from simulation.road import RoadWay
from simulation.road import RoadLane


class RoadObject:
    def paint_yourself(self):
        pass

    def mark_new_position(self, road_way: RoadWay, fresh_lanes: List[RoadLane]):
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

    def mark_new_position(self, road_way: RoadWay, fresh_lanes: List[RoadLane]):
        my_lane = road_way.lanes[self.lane_number]
        distance_to_next_object = self.v
        i = 0
        while i < self.v:
            if my_lane.points[i].occupied:
                distance_to_next_object = i
                break
            else:
                i += 1
        if distance_to_next_object < self.v:
            self.v = distance_to_next_object
        elif self.v >= self.v_max:
            self.v += self.acc

        self.position += self.v

        fresh_lanes[self.lane_number].points[self.position].occupied = True


class StopLight(RoadObject):
    def __init__(self, position: int, redlight_every: int, redlight_duration: int):
        self.position = position
        self.redlight_every = redlight_every
        self.redlight_duration = redlight_duration
        self.redlight = False
        self.timer = 0

    def paint_yourself(self):
        super().paint_yourself()

    def mark_new_position(self, road_way: RoadWay, fresh_lanes: List[RoadLane]):
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