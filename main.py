import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTreeView, QTabWidget, QFileDialog,
    QVBoxLayout, QSplitter, QTextEdit, QHeaderView, QAbstractItemView
)
from PySide6.QtCore import Qt, QDir

# === Import Tabs ===
from src.GUI import PlottingTab, FileSummaryTab
from src.GUI.CustomWidgets import CustomFileSystemModel
from src.util import Logging


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Magnhilds Antenna Measurement Analyzer (MAMA)")
        self.setGeometry(100, 100, 1200, 800)

        # === File Explorer Setup ===
        self.file_model = CustomFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        # self.file_model.setReadOnly(False)

        self.tree = QTreeView()
        self.tree.setModel(self.file_model)
        self.tree.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.tree.setHeaderHidden(True)
        self.tree.setMinimumWidth(250)
        self.tree.setDragEnabled(True)
        self.tree.setDragDropMode(QAbstractItemView.DragOnly)
        columns_to_hide = [1, 2, 3] # 0 = Name, 1 = Size, 2 = Type, 3 = Date modified
        for col in columns_to_hide: 
            self.tree.hideColumn(col)

        # Control column resize behavior
        header = self.tree.header()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        # === Tabs ===
        self.tabs = QTabWidget()
        self.plotting_tab = PlottingTab()
        self.summary_tab = FileSummaryTab()
        self.tabs.addTab(self.plotting_tab, self.plotting_tab.description)
        self.tabs.addTab(self.summary_tab, self.summary_tab.description)


        # === Bottom Output Box ===
        self.log_display = QTextEdit()
        self.log_display.setPlaceholderText("Output / Logs")
        self.log_display.setMaximumHeight(150)
        self.log_display.setReadOnly(True)
        Logging.setup_logging('./debug', self.log_display)

        # === Right Side (Tabs + Output) ===
        right_splitter = QSplitter(Qt.Vertical)
        right_splitter.addWidget(self.tabs)
        right_splitter.addWidget(self.log_display)
        right_splitter.setSizes([600, 150])

        # === Main Splitter ===
        main_splitter = QSplitter(Qt.Horizontal)
        main_splitter.addWidget(self.tree)
        main_splitter.addWidget(right_splitter)
        main_splitter.setSizes([250, 950])
        self.setCentralWidget(main_splitter)

        # === Menu Bar ===
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        # === Signals ===
        change_root_action = file_menu.addAction("Change Folder...")
        change_root_action.triggered.connect(self.change_root_folder)
        self.tree.selectionModel().selectionChanged.connect(self.on_file_selected)

    def change_root_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder", QDir.currentPath())
        if folder:
            self.tree.setRootIndex(self.file_model.index(folder))

    def on_file_selected(self, selected, deselected):
        indexes = selected.indexes()
        if not indexes: return

        index = indexes[0]
        file_path = self.file_model.filePath(index)

        # Call the tab's method to update its summary
        self.summary_tab.update_summary(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
