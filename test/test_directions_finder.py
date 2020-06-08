from simulation.directions_finder import DirectionsFinder
from simulation.node import TraversableNode
from simulation.way import Way


class TestDirectionsFinder:
    def init(self):
        self.first_node_start = TraversableNode(node_id=1, lat=50.06238262767, long=19.92439693544)
        self.first_node_end = TraversableNode(node_id=2, lat=50.0622555, long=19.9237373)
        self.first_way = Way(1, self.first_node_start, self.first_node_end, lanes=1, intermediate_nodes=[])
        self.first_node_start.add_outgoing_way(self.first_way)
        self.second_node_end = TraversableNode(node_id=3, lat=50.06238262767, long=19.92439693544)
        self.second_way = Way(2, self.first_node_end, self.second_node_end, lanes=1, intermediate_nodes=[])
        self.first_node_end.add_outgoing_way(self.second_way)
        self.third_node_end = TraversableNode(node_id=4, lat=50.0622555, long=19.9237373)
        self.third_way = Way(3, self.second_node_end, self.third_node_end, lanes=1, intermediate_nodes=[])
        self.second_node_end.add_outgoing_way(self.third_way)
        self.fourth_node_end = TraversableNode(node_id=5, lat=50.0622555, long=19.9237373)
        self.fourth_way = Way(4, self.third_node_end, self.fourth_node_end, lanes=1, intermediate_nodes=[])
        self.third_node_end.add_outgoing_way(self.fourth_way)
        self.way_dict = {1: self.first_way, 2: self.second_way, 3: self.third_way, 4: self.fourth_way}
        self.node_dict = {1: self.first_node_start, 2: self.first_node_end, 3: self.second_node_end,
                          4: self.third_node_end, 5: self.fourth_node_end}

    def init_non_basic(self):
        self.first_node_start = TraversableNode(node_id=1, lat=50.06238262767, long=19.92439693544)
        self.first_node_end = TraversableNode(node_id=2, lat=50.0622555, long=19.9237373)
        self.first_way = Way(1, self.first_node_start, self.first_node_end, lanes=1, intermediate_nodes=[])
        self.first_node_start.add_outgoing_way(self.first_way)
        self.second_node_end = TraversableNode(node_id=3, lat=50.06238262767, long=19.92439693544)
        self.second_way = Way(2, self.first_node_end, self.second_node_end, lanes=1, intermediate_nodes=[])
        self.first_node_end.add_outgoing_way(self.second_way)
        self.third_node_end = TraversableNode(node_id=4, lat=50.0622555, long=19.9237373)
        self.third_way = Way(3, self.second_node_end, self.third_node_end, lanes=1, intermediate_nodes=[])
        self.second_node_end.add_outgoing_way(self.third_way)
        self.fourth_node_end = TraversableNode(node_id=5, lat=50.0622555, long=19.9237373)
        self.fourth_way = Way(4, self.third_node_end, self.fourth_node_end, lanes=1, intermediate_nodes=[])
        self.third_node_end.add_outgoing_way(self.fourth_way)

        self.w11_way_end = TraversableNode(node_id=12, lat=50.06238262767, long=19.92439693544)
        self.w11_way = Way(11, self.first_node_start, self.w11_way_end, lanes=1, intermediate_nodes=[])
        self.first_node_start.add_outgoing_way(self.w11_way)

        self.w12_way_end = TraversableNode(node_id=13, lat=50.06238262767, long=19.92439693544)
        self.w12_way = Way(12, self.w11_way_end, self.w12_way_end, lanes=1, intermediate_nodes=[])
        self.w11_way_end.add_outgoing_way(self.w12_way)

        self.w13_way_end = TraversableNode(node_id=14, lat=50.06238262767, long=19.92439693544)
        self.w13_way = Way(13, self.w12_way_end, self.w13_way_end, lanes=1, intermediate_nodes=[])
        self.w12_way_end.add_outgoing_way(self.w13_way)

        self.w14_way_end = TraversableNode(node_id=15, lat=50.06238262767, long=19.92439693544)
        self.w14_way = Way(14, self.w13_way_end, self.w14_way_end, lanes=1, intermediate_nodes=[])
        self.w13_way_end.add_outgoing_way(self.w14_way)

        self.w15_way_end = TraversableNode(node_id=16, lat=50.06238262767, long=19.92439693544)
        self.w15_way = Way(15, self.w14_way_end, self.w15_way_end, lanes=1, intermediate_nodes=[])
        self.w14_way_end.add_outgoing_way(self.w15_way)

        self.way_dict = {1: self.first_way, 2: self.second_way, 3: self.third_way, 4: self.fourth_way, 11: self.w11_way,
                         12: self.w12_way, 13: self.w13_way, 14: self.w14_way, 15: self.w15_way}
        self.node_dict = {1: self.first_node_start, 2: self.first_node_end, 3: self.second_node_end,
                          4: self.third_node_end, 5: self.fourth_node_end, 12: self.w11_way_end, 13: self.w12_way_end,
                          14: self.w13_way_end, 15: self.w14_way_end, 16: self.w15_way_end}

    def test_finds_basic_directions(self):
        self.init()
        finder = DirectionsFinder(self.node_dict, self.way_dict)

        result = finder.find_directions(1, 5)
        assert result == {1: 2, 2: 3, 3: 4}

    def test_finds_non_basic_directions(self):
        self.init_non_basic()
        finder = DirectionsFinder(self.node_dict, self.way_dict)

        result1 = finder.find_directions(1, 5)
        assert result1 == {1: 2, 2: 3, 3: 4}

        result2 = finder.find_directions(1, 16)
        assert result2 == {11: 12, 12: 13, 13: 14, 14: 15}


