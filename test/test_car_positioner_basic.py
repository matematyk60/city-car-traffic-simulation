from simulation.car import Car
from simulation.node import TraversableNode
from simulation.positioner import Positioner
from simulation.way import Way


class TestCarPositioner:
    def init(self):
        self.start_node = TraversableNode(node_id=1, lat=50.06238262767, long=19.92439693544)
        self.end_node = TraversableNode(node_id=2, lat=50.0622555, long=19.9237373)
        self.long_way = Way(1, self.start_node, self.end_node, lanes=1, intermediate_nodes=[])
        self.long_way.distance = 100
        self.way_dict = {1: self.long_way}
        self.car = Car(current_way=self.long_way, current_lane=0, directions_map={1: 1}, way_position=0, destination_node_id=123, v=0, v_max=10, acc=10)
        self.positioner = Positioner(self.way_dict)

    def test_position_doesnt_change_after_first_move(self):
        self.init()
        self.car.make_a_move(self.positioner)

        assert self.car.way_position == 0

    def test_v_changes_after_first_move(self):
        self.init()
        self.car.make_a_move(self.positioner)

        assert self.car.v == self.car.acc

    def test_position_changes_after_2nd_move(self):
        self.init()
        self.car.make_a_move(self.positioner)
        self.car.make_a_move(self.positioner)

        assert self.car.way_position == self.car.acc

    def test_v_grows_only_to_v_max_basic(self):
        self.init()
        self.car.make_a_move(self.positioner)
        self.car.make_a_move(self.positioner)

        assert self.car.v == self.car.v_max

        self.car.make_a_move(self.positioner)
        assert self.car.v == self.car.v_max

        self.car.make_a_move(self.positioner)
        assert self.car.v == self.car.v_max

    def test_v_grows_only_to_v_max_less_basic(self):
        self.init()
        self.car.v_max = 15

        self.car.make_a_move(self.positioner)
        self.car.make_a_move(self.positioner)

        assert self.car.v == 15

        self.car.make_a_move(self.positioner)
        assert self.car.v == 15

        self.car.make_a_move(self.positioner)
        assert self.car.v == 15