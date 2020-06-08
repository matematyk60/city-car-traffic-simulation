from simulation.way import Way
from simulation.positioner import PositionRequest
from typing import Dict


class Car:
    def __init__(self, current_way: Way, current_lane: int, directions_map: Dict[int, int], way_position: int,
                 destination_node_id: int, v: int, v_max: int, acc: int):
        self.current_way = current_way
        self.way_position = way_position
        self.v = v
        self.v_max = v_max
        self.acc = acc
        self.current_lane = current_lane
        self.directions_map = directions_map
        self.destination_node_id = destination_node_id

    def make_a_move(self, positioner):
        position_request = PositionRequest(
            current_position=self.way_position,
            current_lane_number=self.current_lane,
            current_way=self.current_way,
            directions_map=self.directions_map,
            speed=self.v
        )
        position_response = positioner.position(position_request)
        self.current_way = position_response.next_way
        self.way_position = position_response.next_position
        # self.next_lane = ??? TODO: add lane changing logic
        self.current_way.mark_next_occupation(self.current_lane, self.way_position)
        if position_response.should_break:
            self.v = position_response.distance_travelled
        else:
            self.v = min(self.v + self.acc, self.v_max)

    def reached_destination(self):
        return self.current_way.end_node.node_id == self.destination_node_id and (
                self.current_way.distance - self.way_position < 3)
