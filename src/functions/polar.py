#Function that plots a single indexed frequency in a polar plot. 

import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.structs import AntennaMeasurement

def plot_single_freq(data, freq, color, ax, label=None):
    angles = np.array(data['angles'])
    frequency = np.array(data['frequencies'])[freq]
    velocities = np.array(data['velocities'])
    power = np.array(data['powers'])[::, freq]
    theta = np.deg2rad(angles)
    if label is None:
        ax.plot(theta, power, color=color, label=f'Frequency: {frequency/(10**9)} GHz')
    else:
        ax.plot(theta, power, color=color, label=label)



def plot_normalized_batch(list_of_data: list['AntennaMeasurement'], ax, freq=-1):
    peak = -np.inf

    for data in list_of_data:
        new_peak = data.peak
        peak = new_peak if new_peak > peak else peak

    for data in list_of_data:
        power = data.power
        theta = data.angles_rad

        power_normed = power - peak
        ax.plot(theta, power_normed)