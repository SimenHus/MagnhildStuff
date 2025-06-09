
import h5py
import numpy as np

from dataclasses import dataclass

from src.enums import Sign

@dataclass
class AntennaMeasurement:
    angles_deg: np.ndarray
    frequency: np.ndarray
    velocities: np.ndarray
    power: np.ndarray

    def power_at(self, angle_deg):
        return self.power[self.closest_angle_index(angle_deg)]

    @property
    def angles_rad(self):
        return np.deg2rad(self.angles_deg)
    
    @property
    def peak(self):
        return np.max(self.power)
    
    @property
    def peak_index(self):
        return np.argmax(self.power)
    
    @property
    def angle_at_peak(self):
        return self.angles_deg[self.peak_index]
    
    @property
    def HPBW(self):
        return abs(self.HPBW_left - self.HPBW_right)
    
    @property
    def HPBW_left(self):
        index = self.dist_from_peak(Sign.POSITIVE, 3)
        return self.angles_deg[index]
    
    @property
    def HPBW_right(self):
        index = self.dist_from_peak(Sign.NEGATIVE, 3)
        return self.angles_deg[index]


    def dist_from_peak(self, direction: Sign, db = 3):
        current_index = self.peak_index
        while self.peak < self.power[current_index] + db:
            current_index += direction.value
            if current_index > len(self.power)-1 and direction == Sign.POSITIVE: current_index = 0
            if current_index < 0 and direction == Sign.NEGATIVE: current_index = len(self.power)-1

        return current_index


    def closest_angle_index(self, target):
        delta = (self.angles_deg - target + 180) % 360 - 180
        return np.argmin(np.abs(delta))

    @staticmethod
    def from_file(path, freq=-1):
        data={}
        with h5py.File(path, 'r') as f:
            for i in list(f.keys()): data[i]=(list(f[i]))
        
        return AntennaMeasurement(
            angles_deg = np.array(data['angles']),
            frequency = np.array(data['frequencies'])[freq],
            velocities = np.array(data['velocities']),
            power = np.array(data['powers'])[::, freq]
        )
    
    @property
    def summary(self):
        return (
            f"HPBW: {self.HPBW} [deg]\n"
            f"Peak power: {self.peak} [dbm]\n"
            f"Peak angle: {self.angle_at_peak} [deg]\n"
        )