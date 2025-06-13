from PySide6.QtWidgets import (
    QWidget, QTreeView, QPushButton,
    QHBoxLayout, QVBoxLayout, QFileSystemModel, QStyle, QAbstractItemView, QHeaderView
)
from PySide6.QtCore import QModelIndex, Qt, QDir
import os

class CustomFileSystemModel(QFileSystemModel):
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if index.column() == 2 and role == Qt.DisplayRole:  # Column 2 = "Type"
            file_path = self.filePath(index)
            if os.path.isdir(file_path):
                return "Folder"
            else:
                return os.path.splitext(file_path)[1]  # Extension like '.png'
        return super().data(index, role)


class FileExplorer(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("QTreeView with Navigation Icons")

        home_dir = QDir.currentPath()
        self.model = CustomFileSystemModel()
        self.model.setRootPath(home_dir)

        self.tree = QTreeView()
        self.tree.setModel(self.model)
        # self.tree.selectionModel().selectionChanged

        self.tree.setRootIndex(self.model.index(home_dir))
        # self.tree.setHeaderHidden(True)
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


        self.current_path = home_dir
        self.history = [home_dir]
        self.history_index = 0

        # Create buttons with icons
        style = self.style()

        self.back_btn = QPushButton()
        self.back_btn.setIcon(style.standardIcon(QStyle.SP_ArrowBack))
        self.back_btn.setToolTip("Back")

        self.forward_btn = QPushButton()
        self.forward_btn.setIcon(style.standardIcon(QStyle.SP_ArrowForward))
        self.forward_btn.setToolTip("Forward")

        self.up_btn = QPushButton()
        self.up_btn.setIcon(style.standardIcon(QStyle.SP_ArrowUp))
        self.up_btn.setToolTip("Up")

        self.back_btn.clicked.connect(self.go_back)
        self.forward_btn.clicked.connect(self.go_forward)
        self.up_btn.clicked.connect(self.go_up)

        self.update_buttons()

        nav_layout = QHBoxLayout()
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.forward_btn)
        nav_layout.addWidget(self.up_btn)

        main_layout = QVBoxLayout()
        main_layout.addLayout(nav_layout)
        main_layout.addWidget(self.tree)

        self.setLayout(main_layout)

        self.tree.doubleClicked.connect(self.on_double_click)

    def update_buttons(self):
        self.back_btn.setEnabled(self.history_index > 0)
        self.forward_btn.setEnabled(self.history_index < len(self.history) - 1)
        self.up_btn.setEnabled(self.current_path != os.path.abspath(os.sep))

    def set_path(self, path):
        if not os.path.isdir(path): return

        self.current_path = path
        self.tree.setRootIndex(self.model.index(path))

        self.history = self.history[:self.history_index + 1]
        self.history.append(path)
        self.history_index += 1

        self.update_buttons()

    def go_back(self):
        if self.history_index > 0:
            self.history_index -= 1
            path = self.history[self.history_index]
            self.current_path = path
            self.tree.setRootIndex(self.model.index(path))
            self.update_buttons()

    def go_forward(self):
        if self.history_index < len(self.history) - 1:
            self.history_index += 1
            path = self.history[self.history_index]
            self.current_path = path
            self.tree.setRootIndex(self.model.index(path))
            self.update_buttons()

    def go_up(self):
        parent = os.path.dirname(self.current_path)
        if parent and parent != self.current_path:
            self.set_path(parent)

    def on_double_click(self, index: QModelIndex):
        if not index.isValid(): return

        path = self.model.filePath(index)
        if os.path.isdir(path):
            self.set_path(path)

    def file_path(self, index) -> str:
        return self.model.filePath(index)
    
    def selection_connect(self, func) -> None:
        self.tree.selectionModel().selectionChanged.connect(func)