import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QMessageBox, QLabel, QListWidgetItem, QHBoxLayout, QGroupBox
)
from PySide6.QtCore import Qt

import matplotlib.pyplot as plt
import numpy as np
import h5py


def plot_polar(data, label, ax = None):
    if not ax: _, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    freq = -1 # HARDCODED CHOICE OF FREQUENCY
    angles = data['angles']
    power = data['powers'][:, freq]
    theta = np.deg2rad(angles)
    ax.plot(theta, power, label=label)


def plot_polar_normalized(data, label, ax = None):
    if not ax: _, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    freq = -1 # HARDCODED CHOICE OF FREQUENCY
    angles = data['angles']
    power = data['powers'][:, freq]
    theta = np.deg2rad(angles)

    power_normed = power - np.max(power)
    ax.plot(theta, power_normed, label=label)

def load_from_h5py(path: str):
    data = {}
    with h5py.File(path, 'r') as f:
        for key in list(f.keys()):
            data[key] = np.array(f[key])
    #The screenshots plot the angles in reverse order compared to this plot. Must reverse the order of the plots.
    #data['powers'] = np.flipud(data['powers'])
    return data

class FileSelectorPanel(QGroupBox):
    def __init__(self, title):
        super().__init__(title)
        self.current_dir = None

        self.layout = QVBoxLayout(self)

        self.label = QLabel("No directory selected")
        self.layout.addWidget(self.label)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.file_list)

        self.select_dir_btn = QPushButton("Select Directory")
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_dir_btn)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.current_dir = dir_path
            self.label.setText(f"Selected Directory: {dir_path}")
            self.populate_file_list()

    def populate_file_list(self):
        self.file_list.clear()
        for filename in os.listdir(self.current_dir):
            full_path = os.path.join(self.current_dir, filename)
            if os.path.isfile(full_path):
                self.file_list.addItem(QListWidgetItem(filename))

    def get_selected_file_paths(self):
        selected_items = self.file_list.selectedItems()
        if not self.current_dir or not selected_items:
            return []
        return [os.path.join(self.current_dir, item.text()) for item in selected_items]


class DualFileSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dual File Selector")
        self.resize(1000, 500)

        main_layout = QVBoxLayout(self)

        # Horizontal split
        file_selectors_layout = QHBoxLayout()

        self.left_panel = FileSelectorPanel("Left Directory")
        self.right_panel = FileSelectorPanel("Right Directory")

        file_selectors_layout.addWidget(self.left_panel)
        file_selectors_layout.addWidget(self.right_panel)

        main_layout.addLayout(file_selectors_layout)

        self.process_btn = QPushButton("Process Selected Files")
        self.process_btn.clicked.connect(self.process_files)
        main_layout.addWidget(self.process_btn)


    def process_files(self):
        left_files = self.left_panel.get_selected_file_paths()
        right_files = self.right_panel.get_selected_file_paths()

        fig, axs = plt.subplots(1, 2, subplot_kw={'projection': 'polar'})
        ax_left, ax_right = axs

        titles = ['L5 H-port E-plane', 'L5 H-port H-plane'] # Bestem titler her
        left_labels = ['XY-plane', 'YZ-plane'] # Bestem labels her
        right_labels = ['XY-plane', 'YZ-plane'] # Bestem labels her


        for i, file in enumerate(left_files):
            data = load_from_h5py(file)
            plot_polar_normalized(data, left_labels[i], ax_left)


        for i, file in enumerate(right_files):
            data = load_from_h5py(file)
            plot_polar_normalized(data, right_labels[i], ax_right)


        # Common settings
        for i, ax in enumerate(axs):
            ax.set_theta_zero_location("N")
            ax.grid(True)
            ax.legend()
            ax.set_title(titles[i])
            colors = ['orangered', 'mediumblue', 'seagreen']

        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DualFileSelector()
    window.show()
    sys.exit(app.exec())
