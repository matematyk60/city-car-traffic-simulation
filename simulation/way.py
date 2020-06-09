import geopy.distance

from simulation.node import Node, TraversableNode
from simulation.range import Range
from typing import List
from collections import namedtuple

from dataclasses import dataclass

@dataclass
class PositionOccupation:
    position: int
    occupied: bool


@dataclass
class LaneOccupation:
    lane: int
    occupations: List[PositionOccupation]


class Way:
    def __init__(self, way_id: int, begin_node: TraversableNode, end_node: TraversableNode, lanes: int,
                 intermediate_nodes: List[Node]):
        self.way_id = way_id
        self.begin_node = begin_node
        self.end_node = end_node
        self.intermediate_nodes = intermediate_nodes
        self.lanes = lanes
        self.distance = 0
        self.ranges = []
        self.instantiate_nodes()
        self.lane_occupations = self.create_occupations()
        self.next_lane_occupations = self.create_occupations()

    def instantiate_nodes(self):
        previous_node = self.begin_node
        for intermediate_node in self.intermediate_nodes:
            cords_1 = (previous_node.lat, previous_node.long)
            cords_2 = (intermediate_node.lat, intermediate_node.long)
            distance = geopy.distance.vincenty(cords_1, cords_2).m
            self.ranges.append((Range(self.distance, self.distance + distance), (previous_node, intermediate_node)))
            self.distance += distance
            previous_node = intermediate_node
        cords_1 = (previous_node.lat, previous_node.long)
        cords_2 = (self.end_node.lat, self.end_node.long)
        distance = geopy.distance.vincenty(cords_1, cords_2).m
        self.ranges.append((Range(self.distance, self.distance + distance), (previous_node, self.end_node)))
        self.distance = int(self.distance + distance)

    def create_occupations(self) -> List[LaneOccupation]:
        lane_occupations = []
        for lane_number in range(0, self.lanes):
            lane_occupation = LaneOccupation(lane_number, [])
            for point_number in range(0, int(self.distance)):
                lane_occupation.occupations.append(PositionOccupation(position=point_number, occupied=False))
            lane_occupations.append(lane_occupation)
        return lane_occupations

    def between_nodes(self, distance: int):
        if distance > self.distance:
            print(f"Way {self.way_id} has only distance {self.distance}. I can't find coords of distance {distance}")
        else:
            range_nodepair = next(x for x in self.ranges if (x[0].__contains__(distance)))
            range = range_nodepair[0]
            percent_of_distance = (distance - range.start) / range.len()
            return range_nodepair[1]

    def coords_of_distance(self, distance: int):
        if distance > self.distance:
            print(f"Way {self.way_id} has only distance {self.distance}. I can't find coords of distance {distance}")
        else:
            range_nodepair = next(x for x in self.ranges if (x[0].__contains__(distance)))
            range = range_nodepair[0]
            percent_of_distance = (distance - range.start) / range.len()
            start_node = range_nodepair[1][0]
            end_node = range_nodepair[1][1]
            lat = (start_node.lat + ((end_node.lat - start_node.lat) * percent_of_distance))
            long = (start_node.long + ((end_node.long - start_node.long) * percent_of_distance))
            return lat, long

    def mark_next_occupation(self, lane_number: int, position: int):
        self.next_lane_occupations[lane_number].occupations[position].occupied = True

    def rewrite_occupations(self):
        self.lane_occupations = self.next_lane_occupations
        self.next_lane_occupations = self.create_occupations()
