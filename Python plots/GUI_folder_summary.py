import sys
import os

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QFileDialog, QLabel, QTextEdit
)
from PySide6.QtCore import Qt


from src.structs import AntennaMeasurement

class FileSummaryApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Summary Viewer")
        self.setMinimumSize(600, 400)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.select_folder_btn = QPushButton("Select Folder")
        self.select_folder_btn.clicked.connect(self.select_folder)
        self.layout.addWidget(self.select_folder_btn)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.show_file_summary)
        self.layout.addWidget(self.file_list)

        self.summary_label = QLabel("File Summary:")
        self.layout.addWidget(self.summary_label)

        self.summary_output = QTextEdit()
        self.summary_output.setReadOnly(True)
        self.layout.addWidget(self.summary_output)

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.load_files(folder)

    def load_files(self, folder_path):
        self.file_list.clear()
        self.current_folder = folder_path
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                self.file_list.addItem(file_name)

    def show_file_summary(self, item):
        file_name = item.text()
        file_path = os.path.join(self.current_folder, file_name)
        summary = self.generate_summary(file_path)
        self.summary_output.setText(summary)

    def generate_summary(self, file_path):
        try:
            return AntennaMeasurement.from_file(file_path).summary
        except Exception as e:
            return f"Error reading file: {e}"


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileSummaryApp()
    window.show()
    sys.exit(app.exec())
