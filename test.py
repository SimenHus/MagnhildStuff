

from src.structs import AntennaMeasurement
from src.enums import Sign

FOLDER = 'C:/Users/zuper/Documents/Masteroppgave/Testing/Radiation_pattern/Take two radpat testing/hport'
FILENAME = 'L1_hport_vTx_XY.h5ant'
path = f'{FOLDER}/{FILENAME}'

meas = AntennaMeasurement.from_file(path)
