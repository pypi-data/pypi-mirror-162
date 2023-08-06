import warnings

from abc import ABC, abstractmethod

import numpy as np

from collections import deque
from typing import Tuple
from tt_sim.core.bike import Bike
from tt_sim.core.stage import Stage
from tt_sim.core.wind import Wind
from tt_sim.core.rider import Rider, TeamRider


def get_purmutations(riders, duration, t_step):
    time = np.arange(0, duration, t_step)
    index = [i for i in range(len(riders))]
    permutations = []
    que = deque(index)
    lead_elapsed_time = 0
    for t in time:
        permutations.append(list(que))
        if (
            lead_elapsed_time >= riders[que[0]].pull_duration
        ):  # if greater than lead rider pull duration then switch
            que.rotate(-1)
            lead_elapsed_time = 0
        else:
            lead_elapsed_time += t_step
    return time, permutations


class Environment:
    def __init__(self, gravity: float = 9.81, air_density: float = 1.225) -> None:
        self.gravity = gravity
        self.air_density = air_density


class BaseSimulation(ABC):
    @staticmethod
    def convergence_check(stage: Stage, v0: float):
        if stage.s_step / v0 > 2:
            warnings.warn(
                f"s_step={stage.s_step} is much larger than v0={v0}, please check convergence"
            )

    @staticmethod
    def drag_force(air_density: float, cda: float, v: float, vw: float):
        return 0.5 * air_density * cda * (v + vw) ** 2

    @staticmethod
    def gravity_force(mass: float, gravity: float, gradient: float):
        return mass * gravity * np.sin(np.arctan(gradient))

    @staticmethod
    def rolling_resistance_force(
        mass: float, gravity: float, gradient: float, crr: float
    ):
        return (crr * mass) * gravity * np.cos(np.arctan(gradient))

    @abstractmethod
    def solve_velocity_and_time(self, v0: float):
        pass


class Simulation(BaseSimulation):
    def __init__(
        self, rider: Rider, bike: Bike, wind: Wind, stage: Stage, power: np.array
    ) -> None:
        self.rider = rider
        self.bike = bike
        self.wind = wind
        self.stage = stage
        self.power = power
        self.max_g_long = 4
        self.max_velocity = 30  # m/s
        self.environment = Environment()
        self.mass = self.rider.mass + self.bike.mass
        self.time = np.zeros(len(self.stage.distance))
        self.velocity = np.zeros(len(self.stage.distance))

    def solve_velocity_and_time(self, v0: float = 1) -> None:
        self.convergence_check(self.stage, v0)

        self.velocity[0] = v0
        for step in range(1, len(self.stage.distance)):
            t = self.time[step - 1]
            v = self.velocity[step - 1]
            vw = self.wind.head_wind(self.stage.heading[step - 1])
            r_gradient = self.stage.gradient[step - 1]
            f_drag = self.drag_force(
                self.environment.air_density, self.rider.cda, v, vw
            )
            f_gravity = self.gravity_force(
                self.mass, self.environment.gravity, r_gradient
            )
            f_rolling = self.rolling_resistance_force(
                self.mass, self.environment.gravity, r_gradient, self.bike.crr
            )
            total_force = f_drag + f_gravity + f_rolling
            f_tyre = self.power[step - 1] / v
            g_long = min(self.max_g_long, (f_tyre - total_force) / self.mass)
            dv = (g_long / v) * self.stage.s_step
            dt = (1 / v) * self.stage.s_step
            self.time[step] = t + dt
            self.velocity[step] = min(v + dv, self.max_velocity)


class TeamSimulation(BaseSimulation):
    def __init__(
        self, riders: Tuple[TeamRider], bike: Bike, wind: Wind, stage: Stage
    ) -> None:
        self.riders = riders
        self.bike = bike
        self.wind = wind
        self.stage = stage
        self.power = [np.zeros(len(self.stage.distance)) for _ in riders]
        self.max_g_long = 4
        self.max_velocity = 30  # m/s
        self.environment = Environment()
        self.time = np.zeros(len(self.stage.distance))
        self.velocity = np.zeros(len(self.stage.distance))

    def solve_for_single_rider(self, rider):
        sim = Simulation(
            rider=rider,
            bike=self.bike,
            wind=self.wind,
            stage=self.stage,
            power=rider.cp * np.ones(len(self.stage.distance)),
        )
        sim.solve_velocity_and_time()
        return sim.time[-1]

    def solve_velocity_and_time(self, v0: float = 1, t_step: float = 1) -> None:
        self.convergence_check(self.stage, v0)

        t_guess = self.solve_for_single_rider(self.riders[0])
        time_permutations, position_permutaions = get_purmutations(
            self.riders, t_guess, t_step
        )

        self.velocity[0] = v0
        for step in range(1, len(self.stage.distance)):
            t = self.time[step - 1]
            v = self.velocity[step - 1]
            vw = self.wind.head_wind(self.stage.heading[step - 1])
            r_gradient = self.stage.gradient[step - 1]
            permutation_index = np.argmin(np.abs(time_permutations - t))
            for rider_position, rider_index in enumerate(
                position_permutaions[permutation_index]
            ):
                rider = self.riders[rider_index]
                rider.set_position(rider_position)
                mass = rider.mass + self.bike.mass
                f_drag = self.drag_force(
                    self.environment.air_density, rider.draft_cda, v, vw
                )
                f_gravity = self.gravity_force(
                    mass, self.environment.gravity, r_gradient
                )
                f_rolling = self.rolling_resistance_force(
                    mass, self.environment.gravity, r_gradient, self.bike.crr
                )
                total_force = f_drag + f_gravity + f_rolling
                if rider_position == 0: # for lead rider
                    leading_power = rider.leading_power
                    leading_force = total_force
                    f_tyre = rider.leading_power / v
                    g_long = min(self.max_g_long, (f_tyre - total_force) / mass)
                    dv = (g_long / v) * self.stage.s_step
                    dt = (1 / v) * self.stage.s_step

                    self.time[step] = t + dt
                    self.velocity[step] = min(v + dv, self.max_velocity)
                    self.power[rider_index][step] = rider.leading_power

                else:
                    if total_force < 0:
                        self.power[rider_index][step] = 0
                    else:
                        self.power[rider_index][step] = leading_power * (
                            total_force / leading_force
                        )
