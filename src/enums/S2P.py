

from enum import Enum, auto
from dataclasses import dataclass

from matplotlib.pyplot import Line2D

class SParameter(Enum):
    S11 = (0, 0)
    S12 = (0, 1)
    S21 = (1, 0)
    S22 = (1, 1)

    def __init__(self, m, n) -> None:
        self.m = m
        self.n = n


@dataclass
class SParamPlotLines:
    mag: Line2D
    phase: Line2D
    smith: Line2D
    color: tuple