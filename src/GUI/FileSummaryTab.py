from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QSizePolicy
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os

from src.structs import AntennaMeasurement


class FileSummaryTab(QWidget):
    description = "Summary"
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.info_label = QLabel("Select file to summarize")
        self.content_preview = QTextEdit()
        self.content_preview.setReadOnly(True)

        self.image_preview = QLabel()
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.image_preview.setScaledContents(True)
        self.image_preview.hide()  # Hidden unless an image is selected

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.content_preview)
        self.layout.addWidget(self.image_preview)
        self.setLayout(self.layout)

    def update_summary(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()

        if not os.path.isfile(file_path):
            self.info_label.setText("Not a file.")
            self.content_preview.clear()
            self.image_preview.hide()
            return

        if ext == ".h5ant":
            self.info_label.setText(f"Measurement file selected: {file_path}")
            try:
                meas = AntennaMeasurement.from_file(file_path)
                self.content_preview.setText(meas.summary)
            except Exception as e:
                self.content_preview.setText(f"Error reading file:\n{e}")

        elif ext in [".png", ".jpg", ".jpeg"]:
            self.info_label.setText(f"Image file selected: {file_path}")
            pixmap = QPixmap(file_path)
            if pixmap.isNull():
                self.content_preview.setText("Failed to load image.")
                self.image_preview.hide()
            else:
                self.content_preview.clear()
                self.image_preview.setPixmap(pixmap)
                self.image_preview.show()

        else:
            self.info_label.setText(f"Ignored file type: {ext}")
            self.content_preview.clear()
            self.image_preview.hide()
