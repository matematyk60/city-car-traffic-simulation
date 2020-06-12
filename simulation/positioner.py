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
        if current_lane > 0:
            r_current_way = position_request.current_way
            r_current_position = position_request.current_position
            r_current_lane = position_request.current_lane_number - 1
            r_speed = position_request.speed * 3
            r_should_travel_to_next_way = True
            r_collisioned = False
            r_travelled_distance = 0
            while r_should_travel_to_next_way:
                for x in range(r_current_position + 1, r_current_way.distance):
                    if r_travelled_distance == r_speed:
                        r_should_travel_to_next_way = False
                        break
                    try:
                        r_occupied = r_current_way.lane_occupations[r_current_lane].occupations[x].occupied
                    except IndexError:
                        r_occupied = True
                    if r_occupied:
                        r_should_travel_to_next_way = False
                        r_collisioned = True
                        break
                    else:
                        r_travelled_distance += 1
                        r_current_position += 1
                r_next_way_id = position_request.directions_map.get(current_way.way_id)
                if r_next_way_id is None:  # journey ended
                    break
                else:
                    r_next_way = self.way_dict[r_next_way_id]
                if r_next_way.way_id != current_way.way_id:
                    try:
                        r_first_position_in_next_way_occupied = r_next_way.lane_occupations[current_lane].occupations[
                            0].occupied
                    except IndexError:
                        r_first_position_in_next_way_occupied = True
                else:
                    r_first_position_in_next_way_occupied = False
                if r_travelled_distance == r_speed:
                    break
                if r_should_travel_to_next_way and not r_first_position_in_next_way_occupied:
                    r_current_way = r_next_way
                    r_current_position = -1
                elif r_should_travel_to_next_way and r_first_position_in_next_way_occupied:
                    r_collisioned = True
                    r_should_travel_to_next_way = False

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
                try:
                    first_position_in_next_way_occupied = next_way.lane_occupations[current_lane].occupations[
                        0].occupied
                except IndexError:
                    first_position_in_next_way_occupied = True
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
        l_collisioned = True
        l_travelled_distance = None
        if collisioned and current_way.lanes - current_lane > 1:  # try to change the line
            l_current_way = position_request.current_way
            l_current_position = position_request.current_position
            l_current_lane = position_request.current_lane_number + 1
            l_should_travel_to_next_way = True
            l_collisioned = False
            l_travelled_distance = 0
            while l_should_travel_to_next_way:
                for x in range(l_current_position + 1, l_current_way.distance):
                    if l_travelled_distance == position_request.speed:
                        l_should_travel_to_next_way = False
                        break
                    try:
                        l_occupied = l_current_way.lane_occupations[l_current_lane].occupations[x].occupied
                    except IndexError:
                        l_occupied = True
                    if l_occupied:
                        l_should_travel_to_next_way = False
                        l_collisioned = True
                        break
                    else:
                        l_travelled_distance += 1
                        l_current_position += 1
                l_next_way_id = position_request.directions_map.get(current_way.way_id)
                if l_next_way_id is None:  # journey ended
                    break
                else:
                    l_next_way = self.way_dict[l_next_way_id]
                if l_next_way.way_id != current_way.way_id:
                    try:
                        l_first_position_in_next_way_occupied = l_next_way.lane_occupations[current_lane].occupations[
                            0].occupied
                    except IndexError:
                        l_first_position_in_next_way_occupied = True
                else:
                    l_first_position_in_next_way_occupied = False
                if l_travelled_distance == position_request.speed:
                    break
                if l_should_travel_to_next_way and not l_first_position_in_next_way_occupied:
                    l_current_way = l_next_way
                    l_current_position = -1
                elif l_should_travel_to_next_way and l_first_position_in_next_way_occupied:
                    l_collisioned = True
                    l_should_travel_to_next_way = False

        if current_lane > 0 and not r_collisioned and r_travelled_distance != 0:
            return PositionResponse(
                next_way=current_way,
                next_position=current_position,
                next_lane=position_request.current_lane_number - 1,
                distance_travelled=travelled_distance,
                should_break=collisioned
            )
        elif travelled_distance == 0 and l_travelled_distance is not None and l_travelled_distance >= 1:
            return PositionResponse(
                next_way=current_way,
                next_position=current_position,
                next_lane=position_request.current_lane_number + 1,
                distance_travelled=travelled_distance,
                should_break=collisioned,
            )
        elif not l_collisioned:
            return PositionResponse(
                next_way=current_way,
                next_position=current_position,
                next_lane=position_request.current_lane_number + 1,
                distance_travelled=travelled_distance,
                should_break=collisioned
            )

        else:
            return PositionResponse(
                next_way=current_way,
                next_position=current_position,
                next_lane=position_request.current_lane_number,
                distance_travelled=travelled_distance,
                should_break=collisioned
            )
