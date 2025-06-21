import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTreeView, QTabWidget, QFileDialog,
    QVBoxLayout, QSplitter, QTextEdit, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDir
import os

# === Import Tabs ===
from src.GUI import H5ANTTab, FileSummaryTab, S2PTab
from src.GUI.CustomWidgets import FileExplorer
from src.util import Logging, Path


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magnhilds Antenna Measurement Analyzer (MAMA)")
        self.setGeometry(100, 100, 1200, 800)

        # === File Explorer Setup ===
        self.file_explorer = FileExplorer()

        # === Tabs ===
        self.tabs = QTabWidget()
        self.plotting_tab = H5ANTTab()
        self.summary_tab = FileSummaryTab()
        self.s2p_tab = S2PTab()
        self.tabs.addTab(self.plotting_tab, self.plotting_tab.description)
        self.tabs.addTab(self.summary_tab, self.summary_tab.description)
        self.tabs.addTab(self.s2p_tab, self.s2p_tab.description)


        # === Bottom Output Box ===
        self.log_display = QTextEdit()
        self.log_display.setPlaceholderText("Output / Logs")
        self.log_display.setMaximumHeight(150)
        self.log_display.setReadOnly(True)
        Logging.setup_logging(self.log_display, Path.debug_folder())

        # === Right Side (Tabs + Output) ===
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.tabs)
        right_splitter.addWidget(self.log_display)
        right_splitter.setSizes([600, 150])

        # === Main Splitter ===
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.file_explorer)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([250, 950])
        self.setCentralWidget(main_splitter)

        # === Menu Bar ===
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # === Signals ===
        self.file_explorer.selection_connect(self.on_file_selected)

    def on_file_selected(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes: return

        index = indexes[0]
        file_path = self.file_explorer.file_path(index)

        # Call the tab's method to update its summary
        self.summary_tab.update_summary(file_path)


if __name__ == "__main__":
    Path.initialize()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
