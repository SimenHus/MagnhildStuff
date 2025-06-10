import sys
import os
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QListWidget,
    QFileDialog, QMessageBox, QLabel, QListWidgetItem
)
from PySide6.QtCore import Qt
import numpy as np
import matplotlib.pyplot as plt
import h5py

from src.functions import polar
from src.structs import AntennaMeasurement

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

        fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
        ax.set_theta_zero_location("N")
        ax.grid(True)
        # colors = ['orangered', 'mediumblue', 'seagreen', 'magenta']
        # labels = ['Take 1', 'Take 2', 'Take 3', 'Take 4']

        list_of_data = []
        for path in full_paths:
            list_of_data.append(AntennaMeasurement.from_file(path))
        polar.plot_normalized_batch(list_of_data, ax)

        ax.legend(loc='upper left', bbox_to_anchor=(1.1, 1.1))
        plt.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSelector()
    window.show()
    sys.exit(app.exec())
