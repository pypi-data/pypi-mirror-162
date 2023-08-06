class Bike:
    def __init__(self, name, mass, crr=0.003):
        self.name = name
        self.mass = mass
        self.crr = crr  # tyre rolling resistance coefficient

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.name}>'

