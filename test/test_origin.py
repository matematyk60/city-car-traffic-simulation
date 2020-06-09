from simulation.car import Car
from simulation.node import TraversableNode
from simulation.positioner import Positioner
from simulation.way import Way
from simulation.origin import Origin


class TestCarPositioner:
    def init(self):
        self.start_node = TraversableNode(node_id=1, lat=50.06238262767, long=19.92439693544)
        self.end_node = TraversableNode(node_id=2, lat=50.0622555, long=19.9237373)
        self.long_way = Way(1, self.start_node, self.end_node, lanes=1, intermediate_nodes=[])
        self.way_dict = {1: self.long_way}
        self.cars = []
        self.origin = Origin(chance_of_introducing=100, origin_way=self.long_way, cars=self.cars)
        self.origin.add_directions_map({2: {1: 1}})

    def test_introduces_new_car(self):
        self.init()
        self.origin.try_creating_new_car()

        assert len(self.cars) == 1

    def test_introduces_new_car_with_correct_values(self):
        self.init()
        self.origin.try_creating_new_car()
        car = self.cars[0]

        assert car.destination_node_id == 2
        assert car.current_way == self.long_way
        assert car.current_lane == 0
        assert car.way_position == 0

    def test_doesnt_introduce_new_car_if_position_occupied(self):
        self.init()
        self.long_way.lane_occupations[0].occupations[0].occupied = True
        self.origin.try_creating_new_car()

        assert len(self.cars) == 0

    def test_introduces_new_car_if_position_is_freed(self):
        self.init()
        self.long_way.lane_occupations[0].occupations[0].occupied = True
        self.origin.try_creating_new_car()

        assert len(self.cars) == 0

        self.origin.chance_of_introducing = 0
        self.long_way.lane_occupations[0].occupations[0].occupied = False

        self.origin.try_creating_new_car()
        assert len(self.cars) == 1
