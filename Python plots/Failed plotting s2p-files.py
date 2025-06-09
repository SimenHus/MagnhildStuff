#-------------- Imports ---------------
from matplotlib import pyplot as plt  # for advanced smith chart only
import skrf as rf
from skrf import Network
import glob

#-------------- File paths and file names -------------
path_to_folder = r'C:\Users\zuper\Documents\Masteroppgave\Testing\Vertical polarization'
path = path_to_folder + r'\*.s2p'

list_of_file_paths = glob.glob(path)

# filenames = []
# file_dict = {}
# for file in list_of_files:
#     sections = file.split('\\')
#     filename = sections[-1].strip('.s2p')
#     filenames.append(filename)
#     file_dict[filename] = file



#---------- Plot magnitude in dB --------------
# Use index of file as argument to plot single file, plots all files in same plot if no argument.

# def plot_magnitude(files = None):
#     if files is None:
#         for i, file in enumerate(list_of_files):
#             graph = Network(file)
#             graph.plot_s_db(m=0,n=0, label='S11' + filenames[i])

#         plt.show()

#     else:
#         graph = Network(list_of_files[files])
#         graph.plot_s_db(m=0,n=0, label='S11' + filenames[files])
#         plt.show()

def get_measurement_name(filepath: str) -> str:
    sections = filepath.split('\\')
    filename = sections[-1].strip('.s2p')
    return filename



def simen_plot(paths: list):
    if type(paths) is not list: paths = [paths]
    for filepath in paths:
        title = get_measurement_name(filepath)
        graph = Network(filepath)
        graph.plot_s_db(m=0, n=0, label='S11 ' + title)
    
    plt.show()



# #---------- Plot in smith chart ---------------
# def plot_smith():
#     L5_top.plot_s_smith(m=0,n=0, label='S11')
#     L5_top.plot_s_smith(m=1,n=0, label='S21')
#     plt.show()


# plot_magnitude()
simen_plot(list_of_file_paths[:3])





