
import simulation.road_object as road_object_
from typing import List


class RoadPoint:
    def __init__(self, usable: bool):
        self.usable = usable
        self.occupied = False

    def unoccupied(self):
        new_point = RoadPoint(self.usable)
        return new_point


class RoadLane:
    def __init__(self, lane_number: int, points: List[RoadPoint]):
        self.lane_number = lane_number
        self.points = points

    def empty(self):
        unoccupied_list = list(map(lambda point: point.unoccupied(), self.points))
        return RoadLane(lane_number=self.lane_number, points=unoccupied_list)


class RoadWay:
    def __init__(self, clock_wise: bool):
        self.clock_wise = clock_wise
        self.lanes = []
        self.objects: List[road_object_.RoadObject] = []

    def add_road_lane(self, lane: RoadLane):
        self.lanes.append(lane)

    def add_object(self, road_object):
        self.objects.append(road_object)

    def make_a_move(self):
        fresh_lanes = list(map(lambda lane: lane.empty(), self.lanes))
        for road_object in self.objects:
            road_object.mark_new_position(self, fresh_lanes)
        self.lanes = fresh_lanes

    def paint(self):
        for road_object in self.objects:
            road_object.paint_yourself()




