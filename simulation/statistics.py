class Statistics:
    def __init__(self):
        self.cars_number = 0
        self.speed_sum = 0

    def register_speed(self, speed):
        self.cars_number += 1
        self.speed_sum += speed

    def get_average_speed(self):
        if self.cars_number == 0:
            return 0
        else:
            return self.speed_sum / self.cars_number

    def reset(self):
        self.cars_number = 0
        self.speed_sum = 0
