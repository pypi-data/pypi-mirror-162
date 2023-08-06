import numpy as np


class Wind:
    def __init__(self, speed=0, direction=0):
        self.speed = speed
        self.direction = direction  # (from north=0, east=90,  south=180, west=270)

    def head_wind(self, heading: float) -> float:
        alpha = self.direction - heading
        head_wind_speed = self.speed * np.cos(np.deg2rad(alpha))
        return head_wind_speed

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'