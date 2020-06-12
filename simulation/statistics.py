class Statistics:
    def __init__(self, way_dict):
        self.car_number = 0
        self.speed_sum = 0
        self.way_statistics_dict = {way_id: WayStatistics() for way_id in way_dict}

    def register_move(self, car):
        self.car_number += 1
        self.speed_sum += car.v
        self.way_statistics_dict[car.old_way_id].register_move(car)

    def get_average_speed(self):
        if self.car_number == 0:
            return 0
        else:
            return self.speed_sum / self.car_number
    
    def get_way_average_speed(self, way_id):
        return self.way_statistics_dict[way_id].get_average_speed()

    def get_way_flow(self, way_id):
        return self.way_statistics_dict[way_id].get_flow()

    def get_way_car_number(self, way_id):
        return self.way_statistics_dict[way_id].car_number

    def reset_average_speed(self):
        self.car_number = 0
        self.speed_sum = 0

        for way in self.way_statistics_dict.values():
            way.reset_average_speed()

    def reset_flow(self):
        for way in self.way_statistics_dict.values():
            way.reset_flow()

class WayStatistics:
    def __init__(self):
        self.car_number = 0
        self.speed_sum = 0
        self.flow = 0

    def register_move(self, car):
        self.car_number += 1
        self.speed_sum += car.v

        if car.old_way_id != car.current_way.way_id:
            self.flow += 1

    def get_average_speed(self):
        if self.car_number == 0:
            return 0
        else:
            return self.speed_sum / self.car_number

    def get_flow(self):
        return self.flow

    def reset_average_speed(self):
        self.car_number = 0
        self.speed_sum = 0

    def reset_flow(self):
        self.flow = 0
