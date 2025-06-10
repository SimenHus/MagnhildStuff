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


# def get_measurement_name(filepath: str) -> str:
#     sections = filepath.split('\\')
#     filename = sections[-1].strip('.s2p')
#     return filename


def plot_dbmag_s21(paths: list, colors: list = None, thickness: float = None):
    if type(paths) is not list: paths = [paths]
    if colors is None: colors = [None]*len(paths)

    for filepath, color in zip(paths, colors):
        # collect data from file
        network = Network(filepath)
        # collect S21 parameter from measurement data
        s_param = network.s[:, 1, 0]
        # Get all frequencies
        frequencies = network.f
        # convert S21 parameter to magnitude (dB)
        magnitude_db = 20 * np.log10(np.abs(s_param))

        # Locate max measurement value
        max_index = np.argmax(magnitude_db)
        # Get corresponding frequecy
        max_freq = frequencies[max_index]
        # Convert max measurement value to dB mag.
        max_value = magnitude_db[max_index]

        # Plot the magnitude
        plt.figure()
        plt.plot(frequencies, magnitude_db, color=color, label='|S21| (dB)', linewidth=2)
        plt.scatter(max_freq, max_value, color='red', label=f'Max: {max_value:.2f} dB @ {max_freq/1e9:.3f} GHz', zorder=5)
        
        # Annotate the point
        # plt.annotate(f'{max_value:.2f} dB\n@ {max_freq/1e9:.3f} GHz',
        #             xy=(max_freq / 1e9, max_value),
        #             xytext=(max_freq / 1e9 + 0.1, max_value),
        #             arrowprops=dict(facecolor='red', arrowstyle='->'),
        #             fontsize=10)

        plt.axvline(x=1.176450000000000E9, color = 'darkred', linewidth = 1)
        plt.axvline(x=1.577420000000000E9, color = 'darkred', linewidth = 1)

        # Labels and formatting
        plt.title('S21 Magnitude')
        plt.xlabel('Frequency (GHz)')
        plt.ylabel('Magnitude (dB)')
        plt.grid(True)
        plt.legend()  
    plt.show()


    # #---------------- Plot top antenna S21 parameters-------------
files_to_plot= [ hal5, hbl5, hcl5]
colors = ['darkorange', 'cornflowerblue', 'darkgoldenrod', 'deepskyblue']
thickness = 0.7
plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)