#-------------- Imports ---------------
from matplotlib import pyplot as plt  # for advanced smith chart only
import skrf as rf
from skrf import Network
import numpy as np

#-------------- File paths and file names -------------
BASE_FOLDER = r'C:\Users\zuper\Documents\Masteroppgave\Testing'
VERTICAL_PATH = BASE_FOLDER + r'\Vertical polarization'
HORIZONTAL_PATH = BASE_FOLDER + r'\Horizontal polarization'
TAKE_2_FOLDER = r'C:\Users\zuper\Documents\Masteroppgave\Testing\S-parameters take 2'

# HORIZONTAL
L1_bottom_LNA_low_power_horizontal = HORIZONTAL_PATH + r'\L1 bottom antenna LNA low power.s2p'
L1_bottom_LNA_standard_horizontal = HORIZONTAL_PATH + r'\L1 bottom antenna LNA standard mode.s2p'
L1_bottom_LNA_off_horizontal = HORIZONTAL_PATH + r'\L1 bottom antenna LNA off.s2p'

L1_middle_LNA_low_power_horizontal = HORIZONTAL_PATH + r'\L1 middle antenna LNA low power.s2p'
L1_middle_LNA_standard_horizontal = HORIZONTAL_PATH + r'\L1 middle antenna LNA standard mode.s2p'
L1_middle_LNA_off_horizontal = HORIZONTAL_PATH + r'\L1 middle antenna LNA off.s2p'

L1_top_LNA_low_power_horizontal = HORIZONTAL_PATH + r'\L1 top antenna LNA low power mode.s2p'
L1_top_LNA_standard_horizontal = HORIZONTAL_PATH + r'\L1 top antenna LNA standard mode.s2p'
L1_top_LNA_off_horizontal = HORIZONTAL_PATH + r'\L1 top antenna LNA off.s2p'

L5_bottom_LNA_low_power_horizontal = HORIZONTAL_PATH + r'\L5 bottom antenna LNA low power.s2p'
L5_bottom_LNA_standard_horizontal = HORIZONTAL_PATH + r'\L5 bottom antenna LNA standard mode.s2p'
L5_bottom_LNA_off_horizontal = HORIZONTAL_PATH + r'\L5 bottom antenna LNA off.s2p'

L5_middle_LNA_low_power_horizontal = HORIZONTAL_PATH + r'\L5 middle antenna LNA low power.s2p'
L5_middle_LNA_standard_horizontal = HORIZONTAL_PATH + r'\L5 middle antenna LNA standard mode.s2p'
L5_middle_LNA_off_horizontal = HORIZONTAL_PATH + r'\L5 middle antenna LNA off.s2p'

L5_top_LNA_low_power_horizontal = HORIZONTAL_PATH + r'\L5 top antenna LNA low power mode.s2p'
L5_top_LNA_standard_horizontal = HORIZONTAL_PATH + r'\L5 top antenna LNA sandard mode.s2p'
L5_top_LNA_off_horizontal = HORIZONTAL_PATH + r'\L5 top antenna LNA off.s2p'

# VERTICAL

L1_bottom_vertical = VERTICAL_PATH + r'\L1 bottom antenna.s2p'
L1_middle_vertical = VERTICAL_PATH + r'\L1 middle antenna.s2p'
L1_top_vertical = VERTICAL_PATH + r'\L1 top antenna.s2p'
L5_bottom_vertical = VERTICAL_PATH + r'\L5 bottom antenna.s2p'
L5_middle_vertical = VERTICAL_PATH + r'\L5 middle antenna.s2p'
L5_top_vertical = VERTICAL_PATH + r'\L5 top antenna.s2p'

# TAKE 2

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

# PHASE MEASUREMENTS    
phase_hal1 = BASE_FOLDER + r'\Phase measurements\hcl5.s2p'



def get_measurement_name(filepath: str) -> str:
    sections = filepath.split('\\')
    filename = sections[-1].strip('.s2p')
    return filename


#--------- Plot S11 magnitude in dB -----------------
def plot_dbmag_s11(paths: list, colors: list = None, thickness: float = None):
    if type(paths) is not list: paths = [paths]
    if colors is None: colors = [None]*len(paths)

    for filepath, color in zip(paths, colors):
        title = get_measurement_name(filepath)
        graph = Network(filepath)
        graph.plot_s_db(m=0, n=0, label='S11 ' + title, color=color, linewidth=thickness)
        plt.axvline(x=1.176450000000000E9, color = 'darkred', linewidth = 1)
        plt.axvline(x=1.577420000000000E9, color = 'darkred', linewidth = 1)
        plt.grid()
    
    plt.show()


#--------- Plot S21 magnitude in dB -----------------
def plot_dbmag_s21(paths: list, colors: list = None, thickness: float = None):
    if type(paths) is not list: paths = [paths]
    if colors is None: colors = [None]*len(paths)

    for filepath, color in zip(paths, colors):
        title = get_measurement_name(filepath)
        graph = Network(filepath)
        graph.plot_s_db(m=1, n=0, label='S21 ' + title, color=color, linewidth=thickness)

        plt.axvline(x=1.176450000000000E9, color = 'darkred', linewidth = 1)
        plt.axvline(x=1.577420000000000E9, color = 'darkred', linewidth = 1)
        plt.grid()
        
    plt.show()


#--------- Plot S11 phase -----------------
def plot_S11_phase(paths: list, colors: list = None, thickness: float = None):
    if type(paths) is not list: paths = [paths]
    if colors is None: colors = [None]*len(paths)

    for filepath, color in zip(paths, colors):
        title = get_measurement_name(filepath)
        graph = Network(filepath)
        graph.plot_s_deg(m=0, n=0, color=color, linewidth=thickness)
        plt.grid()

    plt.show()


#--------- Plot S21 phase -----------------
def plot_S21_phase(paths: list, colors: list = None, thickness: float = None):
    if type(paths) is not list: paths = [paths]
    if colors is None: colors = [None]*len(paths)

    for filepath, color in zip(paths, colors):
        title = get_measurement_name(filepath)
        graph = Network(filepath)
        graph.plot_s_deg(m=1, n=0, color=color, linewidth=thickness)
        plt.grid()

    plt.show()



#---------- Plot in smith chart ---------------
def plot_smith(paths: list, colors: list = None, thickness: float = None):
    if type(paths) is not list: paths = [paths]
    if colors is None: colors = [None]*len(paths)

    for filepath, color in zip(paths, colors):
        title = get_measurement_name(filepath)
        graph = Network(filepath)
        graph.plot_s_smith(m=1, n=0, color=color, linewidth=thickness)
        plt.grid()

    plt.show()


#--------------------------------------------------------------------------
#//////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------------------------


# #---------------- Plot top antenna S11 parameters-------------
files_to_plot= [hbl1]
colors = ['darkorange', 'cornflowerblue', 'darkgoldenrod', 'deepskyblue']
thickness = 0.7
plt.title('Smith chart L1 S21')
plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# #---------------- Plot middle antenna S11 parameters-------------
# files_to_plot= [L1_middle_LNA_off_horizontal, L1_middle_vertical, L5_middle_LNA_off_horizontal, L5_middle_vertical]
# colors = ['darkorange', 'cornflowerblue', 'darkgoldenrod', 'deepskyblue']
# thickness = 0.7
# plt.title('Middle antenna S11')
# plot_dbmag_s11(files_to_plot, colors=colors, thickness=thickness)

# #---------------- Plot bottom antenna S11 parameters-------------
# files_to_plot= [L1_bottom_LNA_off_horizontal, L1_bottom_vertical, L5_bottom_LNA_off_horizontal, L5_bottom_vertical]
# colors = ['darkorange', 'cornflowerblue', 'darkgoldenrod', 'deepskyblue']
# thickness = 0.7
# plt.title('Bottom antenna S11')
# plot_dbmag_s11(files_to_plot, colors=colors, thickness=thickness)


#--------------------------------------------------------------------------
#//////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------------------------


# #---------------- Plot top antenna S21 parameters-------------
# files_to_plot= [L1_top_LNA_off_horizontal, L1_top_vertical, L5_top_LNA_off_horizontal, L5_top_vertical]
# colors = ['darkorange', 'cornflowerblue', 'darkgoldenrod', 'deepskyblue']
# thickness = 0.7
# plt.title('Top antenna S21')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# #---------------- Plot middle antenna S21 parameters-------------
# files_to_plot= [L1_middle_LNA_off_horizontal, L1_middle_vertical, L5_middle_LNA_off_horizontal, L5_middle_vertical]
# colors = ['darkorange', 'cornflowerblue', 'darkgoldenrod', 'deepskyblue']
# thickness = 0.7
# plt.title('Middle antenna S21')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# #---------------- Plot bottom antenna S21 parameters-------------
# files_to_plot= [L1_bottom_LNA_off_horizontal, L1_bottom_vertical, L5_bottom_LNA_off_horizontal, L5_bottom_vertical]
# colors = ['darkorange', 'cornflowerblue', 'darkgoldenrod', 'deepskyblue']
# thickness = 0.7
# plt.title('Bottom antenna S21')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)


#--------------------------------------------------------------------------
#//////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------------------------


# #--------------- Plot S21 for all vertical polarizations ---------------
# files_to_plot= [L1_bottom_vertical, L1_middle_vertical, L1_top_vertical, L5_bottom_vertical, L5_middle_vertical, L5_top_vertical]
# colors = ['tomato', 'chartreuse', 'mediumblue', 'tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('All vertical S21')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# #-------------- Plot S21 for horizontal polarization with LNA turned off ---------------------
# files_to_plot=[L1_bottom_LNA_off_horizontal, L1_middle_LNA_off_horizontal, L1_top_LNA_off_horizontal, L5_bottom_LNA_off_horizontal, L5_middle_LNA_off_horizontal, L5_top_LNA_off_horizontal]
# colors = ['tomato', 'chartreuse', 'mediumblue', 'tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('All horizontal S21 with LNA off')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# #-------------- Plot S21 for LNA in low power mode ---------------------
# files_to_plot=[L1_bottom_LNA_low_power_horizontal, L1_middle_LNA_low_power_horizontal, L1_top_LNA_low_power_horizontal, L5_bottom_LNA_low_power_horizontal, L5_middle_LNA_low_power_horizontal, L5_top_LNA_low_power_horizontal]
# colors = ['tomato', 'chartreuse', 'mediumblue', 'tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('All horizontal S21 with LNA in low power mode')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# #-------------- Plot S21 for LNA in standard mode ---------------------
# files_to_plot=[L1_bottom_LNA_standard_horizontal, L1_middle_LNA_standard_horizontal, L1_top_LNA_standard_horizontal, L5_bottom_LNA_standard_horizontal, L5_middle_LNA_standard_horizontal, L5_top_LNA_standard_horizontal]
# colors = ['tomato', 'chartreuse', 'mediumblue', 'tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('All horizontal S21 with LNA in standard mode')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)



#--------------------------------------------------------------------------
#//////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------------------------


# #-------------- Plot all S21 measurements for L5 frequencies ---------------------
# files_to_plot=[ L5_bottom_vertical, L5_middle_vertical, L5_top_vertical, L5_bottom_LNA_off_horizontal, L5_middle_LNA_off_horizontal, L5_top_LNA_off_horizontal]
# colors = ['tomato', 'chartreuse', 'mediumblue', 'tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('S21 for L5 frequencies both polarizations')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# #-------------- Plot all S21 measurements for L1 frequencies ---------------------
# files_to_plot=[ L1_bottom_vertical, L1_middle_vertical, L1_top_vertical, L1_bottom_LNA_off_horizontal, L1_middle_LNA_off_horizontal, L1_top_LNA_off_horizontal]
# colors = ['tomato', 'chartreuse', 'mediumblue', 'tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('S21 for L1 frequencies both polarizations')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)


#--------------------------------------------------------------------------
#//////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------------------------


# #------------------- Plot phase between vertical S11 antenna measurements with L5 frequencies --------------------
# files_to_plot = [L5_bottom_vertical, L5_middle_vertical, L5_top_vertical]
# thickness = 0.7
# plt.title('S11 phase for vertical L5 frequencies')
# plot_S11_phase(files_to_plot, thickness=thickness)

# #------------------- Plot phase between vertical S11 antenna measurements with L1 frequencies --------------------
# files_to_plot = [L1_bottom_LNA_off_horizontal, L1_middle_LNA_off_horizontal, L1_top_LNA_off_horizontal]
# thickness = 0.7
# plt.title('S11 phase for vertical L1 frequencies')
# plot_S11_phase(files_to_plot, thickness=thickness)

# #------------------- Plot phase between vertical S21 antenna measurements with L1 frequencies --------------------
# files_to_plot = [L1_bottom_LNA_off_horizontal, L1_middle_LNA_off_horizontal, L1_top_LNA_off_horizontal]
# thickness = 0.7
# plt.title('S21 phase for vertical L1 frequencies')
# plot_S21_phase(files_to_plot, thickness=thickness)


# #------------------- Plot phase between horizontal S11 antenna measurements with L5 frequencies --------------------
# files_to_plot = [L5_bottom_LNA_off_horizontal, L5_middle_LNA_off_horizontal, L5_top_LNA_off_horizontal]
# thickness = 0.7
# plt.title('S11 phase for horizontal L5 frequencies')
# plot_S11_phase(files_to_plot, thickness=thickness)



#--------------------------------------------------------------------------
#//////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------------------------


# #----------------- Smith chart S11 vertical L1 --------------------
# files_to_plot = [L1_bottom_vertical, L1_middle_vertical, L1_top_vertical]
# thickness = 0.7
# plt.title('Smith chart S11 vertical L1 frequencies')
# plot_smith(files_to_plot, thickness=thickness)



# #----------------- Smith chart S11 horizontal L1 --------------------
# files_to_plot = [hal1, hbl1, hcl1]
# thickness = 0.7
# plt.title('Smith chart S11 horizontal L1 frequencies')
# plot_smith(files_to_plot, thickness=thickness)



# #----------------- Smith chart S11 horizontal L5 --------------------
# files_to_plot = [hal5, hbl5, hcl5]
# thickness = 0.7
# plt.title('Smith chart S11 horizontal L5 frequencies')
# plot_smith(files_to_plot, thickness=thickness)


#--------------------------------------------------------------------------
#//////////////////////////////////////////////////////////////////////////
#--------------------------------------------------------------------------

# files_to_plot= [hal1, hbl1, hcl1]
# colors = ['tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('S11 for L1 frequencies, LNA low power mode, horizontal polarization')
# plot_dbmag_s11(files_to_plot, colors=colors, thickness=thickness)

# files_to_plot= [hal5, hbl5, hcl5]
# colors = ['tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('S11 for L5 frequencies, LNA low power mode, horizontal polarization')
# plot_dbmag_s11(files_to_plot, colors=colors, thickness=thickness)

# files_to_plot= [hal1, hbl1, hcl1]
# colors = ['tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('S21 for L1 frequencies, LNA low power mode, horizontal polarization')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# files_to_plot= [hal5, hbl5, hcl5]
# colors = ['tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('S21 for L5 frequencies, LNA low power mode, horizontal polarization')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# files_to_plot= [hal1bw, hbl1bw, hcl1bw]
# colors = ['tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('S21 for L1 frequencies, LNA low power mode, horizontal polarization')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# files_to_plot= [hal5bw, hbl5bw, hcl5bw]
# colors = ['tomato', 'chartreuse', 'mediumblue']
# thickness = 0.7
# plt.title('S21 for L5 frequencies, LNA low power mode, horizontal polarization')
# plot_dbmag_s21(files_to_plot, colors=colors, thickness=thickness)

# files_to_plot = [hal1po, hbl1po, hcl1po]
# thickness = 0.7
# plt.title('S21 phase for L1 frequencies with embedded phase offset')
# plot_S21_phase(files_to_plot, thickness=thickness)


# files_to_plot = [hal5po, hbl5po, hcl5po]
# thickness = 0.7
# plt.title('S21 phase for L5 frequencies with embedded phase offset')
# plot_S21_phase(files_to_plot, thickness=thickness)

# files_to_plot = [phase_hal1]
# thickness = 0.7
# plt.title('S21 phase for L5 frequencies with embedded phase offset')
# plot_S21_phase(files_to_plot, thickness=thickness)
