from dataclasses import dataclass
from simulation.way import Way
from typing import Dict, Optional


@dataclass
class PositionRequest:
    current_position: int
    current_lane_number: int
    current_way: Way
    directions_map: Dict[int, int]
    speed: int


@dataclass
class PositionResponse:
    next_way: Way
    next_position: int
    next_lane: int
    distance_travelled: int
    should_break: bool
    change_lane_to: Optional[bool]


class Positioner:
    def __init__(self, way_dict: Dict[int, Way]):
        self.way_dict = way_dict

    def position(self, position_request: PositionRequest) -> PositionResponse:
        current_way = position_request.current_way
        current_position = position_request.current_position
        current_lane = position_request.current_lane_number
        should_travel_to_next_way = True
        collisioned = False
        travelled_distance = 0
        while should_travel_to_next_way:
            for x in range(current_position + 1, current_way.distance):
                if travelled_distance == position_request.speed:
                    should_travel_to_next_way = False
                    break
                elif current_way.lane_occupations[current_lane].occupations[x].occupied:
                    should_travel_to_next_way = False
                    collisioned = True
                    break
                else:
                    travelled_distance += 1
                    current_position += 1
            next_way_id = position_request.directions_map.get(current_way.way_id)
            if next_way_id is None:  # journey ended
                break
            else:
                next_way = self.way_dict[next_way_id]
            if next_way.way_id != current_way.way_id:
                first_position_in_next_way_occupied = next_way.lane_occupations[current_lane].occupations[0].occupied
            else:
                first_position_in_next_way_occupied = False
            if travelled_distance == position_request.speed:
                break
            if should_travel_to_next_way and not first_position_in_next_way_occupied:
                current_way = next_way
                current_position = -1
            elif should_travel_to_next_way and first_position_in_next_way_occupied:
                collisioned = True
                should_travel_to_next_way = False

        return PositionResponse(
            next_way=current_way,
            next_position=current_position,
            next_lane=position_request.current_lane_number,
            distance_travelled=travelled_distance,
            should_break=collisioned,
            change_lane_to=None
        )
