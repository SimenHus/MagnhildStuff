import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QMessageBox, QLabel, QListWidgetItem
)
from PySide6.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import h5py


def plot_3d_single_freq(data1, data2, ax, label):
    theta1 = np.deg2rad(np.array(data1['angles'])) # Liggende
    theta2 = np.deg2rad(np.array(data2['angles'])) # Stående

    min_shape = theta1.shape[0]
    if theta2.shape[0] < min_shape: min_shape = theta2.shape[0]

    theta1 = theta1[:min_shape]
    theta2 = theta2[:min_shape]

    freq = -1
    power1 = np.array(data1['powers'])[:, freq]
    power2 = np.array(data2['powers'])[:, freq]

    power1 = power1[:min_shape]
    power2 = power2[:min_shape]

    az, el = np.meshgrid(theta1, theta2)

    # R = np.maximum(az_interp, el_interp)
    # az, el = power1, power2
    R = np.outer(power1, power2)
    X = R * np.sin(el) * np.cos(az)
    Y = R * np.sin(el) * np.sin(az)
    Z = R * np.cos(el)
    ax.plot_surface(X, Y, Z, alpha=0.8, label=label)

def plot_3d_from_2d_slices(data1, data2, ax, labels):
    theta1 = np.deg2rad(np.array(data1['angles'])) # Liggende
    theta2 = np.deg2rad(np.array(data2['angles'])) # Stående

    freq = -1
    power1 = np.array(data1['powers'])[:, freq]
    power2 = np.array(data2['powers'])[:, freq]

    mag1 = 10**(power1/10)
    mag2 = 10**(power2/10)

    X1 = mag1 * np.cos(theta1)
    Y1 = mag1 * np.sin(theta1)
    Z1 = np.zeros_like(theta1)
    

    X2 = mag2 * np.cos(theta2)
    Y2 = mag2 * np.sin(theta2)
    Z2 = np.zeros_like(theta2)

    ax.plot(X1, Y1, Z1, label=labels[0])
    ax.plot(X2, Z2, Y2, label=labels[1])

class FileSelector(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Selector")
        self.resize(500, 400)

        self.layout = QVBoxLayout(self)

        self.label = QLabel("No directory selected")
        self.layout.addWidget(self.label)

        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.MultiSelection)
        self.layout.addWidget(self.file_list)

        self.select_dir_btn = QPushButton("Select Directory")
        self.select_dir_btn.clicked.connect(self.select_directory)
        self.layout.addWidget(self.select_dir_btn)

        self.process_btn = QPushButton("Process Selected Files")
        self.process_btn.clicked.connect(self.process_files)
        self.layout.addWidget(self.process_btn)

    def select_directory(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Directory")
        if dir_path:
            self.current_dir = dir_path  # Store current directory
            self.label.setText(f"Selected Directory: {dir_path}")
            self.populate_file_list(dir_path)

    def populate_file_list(self, dir_path):
        self.file_list.clear()
        for filename in os.listdir(dir_path):
            full_path = os.path.join(dir_path, filename)
            if os.path.isfile(full_path):
                self.file_list.addItem(QListWidgetItem(filename))

    def process_files(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one file.")
            return

        selected_files = [item.text() for item in selected_items]
        QMessageBox.information(self, "Processing", f"Processing files:\n" + "\n".join(selected_files))
        # Here, you can call your processing logic with full paths.
        full_paths = [os.path.join(self.current_dir, file) for file in selected_files]
        self.handle_data(full_paths)


    def handle_data(self, full_paths):
        fig, ax = plt.subplots(subplot_kw={'projection': '3d'})
        ax_scale = 1e-3
        ax.set_xlim(-ax_scale, ax_scale)
        ax.set_ylim(-ax_scale, ax_scale)
        ax.set_zlim(-ax_scale, ax_scale)
        # ax.set_theta_zero_location("N")
        # ax.grid(True)
        labels = ['L5', 'L1', '1.3 GHz']
        label = 'ligma'
        data1 = {}
        data2 = {}
        for path, data in zip(full_paths, [data1, data2]):
            with h5py.File(path, 'r') as f:
                for i in list(f.keys()): data[i]=(list(f[i]))
        # plot_3d_single_freq(data1, data2, ax, label)
        labels = ['ligma', 'balls']
        plot_3d_from_2d_slices(data1, data2, ax, labels)
        # ax.legend(loc='upper left', bbox_to_anchor=(1.1, 1.1))
        plt.show()



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSelector()
    window.show()
    sys.exit(app.exec())
