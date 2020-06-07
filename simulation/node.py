# import simulation.way as way_

class Node:
    def __init__(self, node_id: int, lat: float, long: float):
        self.node_id = node_id
        self.lat = lat
        self.long = long

    def __str__(self):
        return f"Node(id={self.node_id}, lat={self.lat}, long={self.long})"

    def get_coords(self):
        return (self.lat, self.long)

class TraversableNode(Node):
    def __init__(self, node_id: int, lat: float, long: float):
        super().__init__(node_id, lat, long)
        self.outgoing_ways = []

    def add_outgoing_way(self, way):
        self.outgoing_ways.append(way)

    def __str__(self):
        return super().__str__()


class PositionNode(Node):
    def __init__(self, node_id: int, lat: float, long: float):
        super().__init__(node_id, lat, long)

    def __str__(self):
        return super().__str__()

