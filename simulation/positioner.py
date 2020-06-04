
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
    next_way: int
    next_position: int
    next_lane: int
    distance_travelled: int
    should_break: bool
    change_lane_to: Optional[bool]

def position(position_request: PositionRequest) -> PositionResponse:
    current_way = position_request.current_way
    current_position = position_request.current_position
    should_travel_to_next_way = True
    collisioned = False
    travelled_distance = 0
    while should_travel_to_next_way:
        for x in range(current_position + 1, current_way.distance):
            if travelled_distance == position_request.speed:
                should_travel_to_next_way = False
            elif current_way.occupations[x].occupied:
                should_travel_to_next_way = False
                collisioned = True
                break
            else:
                travelled_distance += 1
                current_position += 1
        next_way = position_request.directions_map[current_way.way_id]
        if travelled_distance < position_request.speed and not collisioned and not next_way.occupations[x].occupied:
            current_way = next_way
            current_position = 0
    return PositionResponse(
        next_way=current_way,
        next_position=current_position,
        next_lane=position_request.current_lane_number,
        distance_travelled=travelled_distance,
        should_break=collisioned,
        change_lane_to=None
    )




