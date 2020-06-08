from simulation.car import Car
from simulation.node import TraversableNode
from simulation.positioner import Positioner
from simulation.way import Way


class TestCarPositioner:
    def init(self):
        self.first_node_start = TraversableNode(node_id=1, lat=50.06238262767, long=19.92439693544)
        self.first_node_end = TraversableNode(node_id=2, lat=50.0622555, long=19.9237373)
        self.first_way = Way(1, self.first_node_start, self.first_node_end, lanes=1, intermediate_nodes=[])
        self.first_node_start.add_outgoing_way(self.first_way)
        self.first_way.distance = 5
        self.second_node_end = TraversableNode(node_id=3, lat=50.06238262767, long=19.92439693544)
        self.second_way = Way(2, self.first_node_end, self.second_node_end, lanes=1, intermediate_nodes=[])
        self.first_node_end.add_outgoing_way(self.second_way)
        self.second_way.distance = 2
        self.third_node_end = TraversableNode(node_id=4, lat=50.0622555, long=19.9237373)
        self.third_way = Way(3, self.second_node_end, self.third_node_end, lanes=1, intermediate_nodes=[])
        self.second_node_end.add_outgoing_way(self.third_way)
        self.way_dict = {1: self.first_way, 2: self.second_way, 3: self.third_way}
        self.directions_map = {1: 2, 2: 3, 3: 3}
        self.car = Car(current_way=self.first_way, current_lane=0, directions_map=self.directions_map, way_position=0,
                       destination_node_id=123, v=0, v_max=10, acc=10)
        self.positioner = Positioner(self.way_dict)

    def test_moves_trough_one_way(self):
        self.init()
        self.car.acc = 6
        self.car.make_a_move(self.positioner)  # do the first move (it doesnt affect position)
        self.car.make_a_move(self.positioner)

        assert self.car.current_way.way_id == self.second_way.way_id

    def test_moves_trough_one_way_and_has_correct_position(self):
        self.init()
        self.car.acc = 6
        self.car.make_a_move(self.positioner)  # do the first move (it doesnt affect position)
        self.car.make_a_move(self.positioner)

        assert self.car.current_way.way_id == self.second_way.way_id
        assert self.car.way_position == 1

    def test_moves_trough_two_ways(self):
        self.init()
        self.car.make_a_move(self.positioner)  # do the first move (it doesnt affect position)
        self.car.make_a_move(self.positioner)

        assert self.car.current_way.way_id == self.third_way.way_id

    def test_moves_trough_two_ways_and_has_correct_position(self):
        self.init()
        self.car.make_a_move(self.positioner)  # do the first move (it doesnt affect position)
        self.car.make_a_move(self.positioner)

        assert self.car.current_way.way_id == self.third_way.way_id
        assert self.car.way_position == 3

    def test_moves_trough_two_ways_and_reaches_destination(self):
        self.init()
        self.car.directions_map = {1: 2}
        self.car.make_a_move(self.positioner)  # do the first move (it doesnt affect position)

        self.car.make_a_move(self.positioner)
        assert self.car.current_way.way_id == self.second_way.way_id
        assert self.car.way_position == 1

        self.car.make_a_move(self.positioner)
        assert self.car.current_way.way_id == self.second_way.way_id
        assert self.car.way_position == 1

