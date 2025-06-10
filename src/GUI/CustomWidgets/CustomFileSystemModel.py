
from PySide6.QtWidgets import (
    QFileSystemModel
)

from PySide6.QtCore import Qt, QModelIndex
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







