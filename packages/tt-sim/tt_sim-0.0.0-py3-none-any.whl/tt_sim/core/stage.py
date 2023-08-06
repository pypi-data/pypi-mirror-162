import os

import pandas as pd
import numpy as np

from collections import namedtuple
from scipy.signal import butter
from scipy.signal import filtfilt
from scipy.interpolate import interp1d

from geographiclib.geodesic import Geodesic

FilterConfigData = namedtuple("FilterConfigData", ["gain", "offset", "frequency"])
StageData = namedtuple(
    "StageData", ["latitude", "longitude", "elevation", "distance", "heading"]
)

def read_csv(file_path, file_name):
    data = pd.read_csv(os.path.join(file_path, file_name))
    latitude = data.latitude.values
    longitude = data.longitude.values
    heading = compute_heading(latitude, longitude)

    return StageData(latitude=latitude,
                     longitude=longitude,
                     distance=data.distance.values,
                     elevation=data.elevation.values,
                     heading=heading)

def compute_heading(latitude, longitude):
    heading = np.zeros(len(latitude))
    for i in range(len(latitude)-1):
        geodesic = Geodesic.WGS84.Inverse(latitude[i], longitude[i], latitude[i + 1], longitude[i + 1])
        if geodesic['azi1'] < 0:
            heading[i] = geodesic['azi1'] + 360
        else:
            heading[i] = geodesic['azi1']
    return heading
class Stage:
    def __init__(self, name, s_step=1, file_path=None, file_name=None):
        self.name = name
        self.s_step = s_step
        if file_name:
            if file_name.split('.')[1] == 'csv':
                stage_data = read_csv(file_path, file_name) # it is confusing having heading calculation in here
            else:
                raise NotImplementedError
        else:
            # default track
            distance = np.arange(0, 54526, s_step)
            elevation_gain = 0
            elevation = np.linspace(0, elevation_gain, len(distance))
            latitude = np.linspace(0, 0, len(distance))
            longitude = np.linspace(0, 0, len(distance))
            heading = np.linspace(0, 0, len(distance))
            stage_data = StageData(
                latitude=latitude,
                longitude=longitude,
                distance=distance,
                elevation=elevation,
                heading=heading,
            )

        self.raw_data = stage_data
        self.distance = np.arange(
            stage_data.distance[0], stage_data.distance[-1], s_step
        )
        self.elevation = self._low_pass_filter(
            stage_data.distance,
            stage_data.elevation,
            self.distance,
            s_step,
            config=FilterConfigData(gain=1, offset=0, frequency=0.005),
        )
        self.latitude = self._interpolate(
            stage_data.distance, stage_data.latitude, self.distance
        )
        self.longitude = self._interpolate(
            stage_data.distance, stage_data.longitude, self.distance
        )
        self.gradient = self._compute_gradient(self.distance, self.elevation)
        self.heading = self._interpolate(
            stage_data.distance, stage_data.heading, self.distance
        )

    @staticmethod
    def _compute_gradient(x, y):
        return np.gradient(y, x)

    @staticmethod
    def _interpolate(x, y, xi, method="cubic"):
        y_interp = interp1d(x, y, kind=method, fill_value="extrapolate")
        return y_interp(xi)

    def _low_pass_filter(self, x, y, xi, s_step, config):
        [b, a] = butter(2, 2 * config.frequency * s_step)
        yi = self._interpolate(x, y * config.gain + config.offset, xi)
        y_mod = filtfilt(b, a, yi)
        return y_mod

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name} with distance step of {self.s_step}m>"
