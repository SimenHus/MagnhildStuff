#-------------- Imports ---------------
from matplotlib import pyplot as plt  # for advanced smith chart only
import skrf as rf
from skrf import Network
import numpy as np

#-------------- Files ---------------
TAKE_2_FOLDER = r'C:\Users\zuper\Documents\Masteroppgave\Testing\S-parameters take 2'

hal1 = TAKE_2_FOLDER + r'\hal1.s2p'
hal5 = TAKE_2_FOLDER + r'\hal5.s2p'
hal1po = TAKE_2_FOLDER + r'\hal1po.s2p'
hal5po = TAKE_2_FOLDER + r'\hal5po.s2p'
hal1bw = TAKE_2_FOLDER + r'\hal1bw.s2p'
hal5bw = TAKE_2_FOLDER + r'\hal5bw.s2p'
hbl1 = TAKE_2_FOLDER + r'\hbl1.s2p'
hbl5 = TAKE_2_FOLDER + r'\hbl5.s2p'
hbl1po = TAKE_2_FOLDER + r'\hbl1po.s2p'
hbl5po = TAKE_2_FOLDER + r'\hbl5po.s2p'
hbl1bw = TAKE_2_FOLDER + r'\hbl1bw.s2p'
hbl5bw = TAKE_2_FOLDER + r'\hbl5bw.s2p'
hcl1 = TAKE_2_FOLDER + r'\hcl1.s2p'
hcl5 = TAKE_2_FOLDER + r'\hcl5.s2p'
hcl1po = TAKE_2_FOLDER + r'\hcl1po.s2p'
hcl5po = TAKE_2_FOLDER + r'\hcl5po.s2p'
hcl1bw = TAKE_2_FOLDER + r'\hcl1bw.s2p'
hcl5bw = TAKE_2_FOLDER + r'\hcl5bw.s2p'


def get_measurement_name(filepath: str) -> str:
    sections = filepath.split('\\')
    filename = sections[-1].strip('.s2p')
    return filename


#---------- Plot in smith chart ---------------
def plot_smith(paths: list, colors: list = None, thickness: float = None):
    if type(paths) is not list: paths = [paths]
    if colors is None: colors = [None]*len(paths)

    for filepath, color in zip(paths, colors):
        title = get_measurement_name(filepath)
        graph = Network(filepath)
        graph.plot_s_smith(m=0, n=0, color=color, linewidth=thickness)
        plt.grid()

    plt.show()


L5_freq_point = '1.176352705410822E9'
L1_freq_point = ' 1.575150300601203E9'
frequencies = Network.f

index = np.argmin(np.abs(frequencies - L1_freq_point))
highlight_freq = frequencies[index]
highlight_s21 = s21[index]

files_to_plot= [hal1]
colors = ['darkorange', 'cornflowerblue', 'darkgoldenrod', 'deepskyblue']
thickness = 0.7
plt.title('Top antenna S11')
plot_smith(files_to_plot, colors=colors, thickness=thickness)