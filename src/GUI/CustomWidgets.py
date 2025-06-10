
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QFrame, 
    QGridLayout, QMenu, QFileSystemModel, QApplication
)

from PySide6.QtCore import Qt, QPoint, Signal, QMimeData, QByteArray, QDataStream, QIODevice, QModelIndex, QEvent
from PySide6.QtGui import QDrag, QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os


from src.structs import AntennaMeasurement


class CustomFileSystemModel(QFileSystemModel):
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if index.column() == 2 and role == Qt.DisplayRole:  # Column 2 = "Type"
            file_path = self.filePath(index)
            if os.path.isdir(file_path):
                return "Folder"
            else:
                return os.path.splitext(file_path)[1]  # Extension like '.png'
        return super().data(index, role)




class PlotWidget(QFrame):
    # Signal emitted when this plot widget wants to be removed
    remove_requested = Signal(QWidget)

    def __init__(self, parent):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()
        self.figure = Figure()

        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMouseTracking(True)
        self.canvas.installEventFilter(self)

        self.ax = self.figure.add_subplot(111, projection='polar')
        self.ax.set_theta_zero_location("N")
        
        
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self.setAcceptDrops(True)
        self.plotted_files = {}  # file_path: matplotlib line object
        self.plotted_meas = {} # file_path: AntennaMeasurement

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        # For drag and drop reorder
        self.setMouseTracking(True)
        self.setAttribute(Qt.WA_Hover)
        self.drag_start_position = None

        self.tab_parent = parent
        self.normalized = True



    def eventFilter(self, source, event):
        if source is self.canvas:
            if event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                self.drag_start_position = event.pos()
            elif event.type() == QEvent.MouseMove and event.buttons() & Qt.LeftButton:
                if (event.pos() - self.drag_start_position).manhattanLength() >= QApplication.startDragDistance():
                    self.start_drag(event)
                    return True  # Block further handling
        return super().eventFilter(source, event)

    def dragEnterEvent(self, event):
        # Accept both external file drops and internal drag reorder
        if event.mimeData().hasUrls() or event.mimeData().hasFormat("application/x-plotwidget"):
            event.acceptProposedAction()


    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            updated = False
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                ext = os.path.splitext(file_path)[1].lower()
                if ext in ['.h5ant']:
                    if self.plot_file(file_path):
                        updated = True
            if updated: self.update_plot()
            event.acceptProposedAction()
        elif event.mimeData().hasFormat("application/x-plotwidget"):
            # Internal reorder drop
            data = event.mimeData().data("application/x-plotwidget")
            stream = QDataStream(data, QIODevice.ReadOnly)
            source_id = stream.readInt64()
            event.acceptProposedAction()
            self.tab_parent.handle_reorder(source_id, id(self))

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()

    def start_drag(self, event):
        drag = QDrag(self)
        mime_data = QMimeData()

        # Store the id of the widget being dragged so we can identify it on drop
        data = QByteArray()
        stream = QDataStream(data, QIODevice.WriteOnly)
        stream.writeInt64(id(self))
        mime_data.setData("application/x-plotwidget", data)

        drag.setMimeData(mime_data)
        drag.setPixmap(self.grab())
        drag.setHotSpot(event.pos())

        drag.exec(Qt.MoveAction)

    def normalize(self) -> None:
        if not self.normalized: return self.denormalize()
        peak = -np.inf
        for value in self.plotted_meas.values():
            if value.peak > peak: peak = value.peak
        
        for key, value in self.plotted_meas.items():
            self.plotted_files[key].set_ydata(value.power - peak)

    def denormalize(self) -> None:
        for key, value in self.plotted_meas.items():
            self.plotted_files[key].set_ydata(value.power)
    

    def plot_file(self, file_path) -> bool:
        if file_path in self.plotted_files:
            return False  # Already plotted

        try:
            meas = AntennaMeasurement.from_file(file_path)
            label = os.path.basename(file_path)
            line, = self.ax.plot(meas.angles_rad, meas.power, label=label)
            self.plotted_files[file_path] = line
            self.plotted_meas[file_path] = meas
            return True
        except Exception as e:
            print(f"Failed to plot {file_path}: {e}")
            return False

    def open_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        remove_menu = menu.addMenu("Remove Plotted File")
        if not self.plotted_files:
            remove_menu.setDisabled(True)
        else:
            for file_path in list(self.plotted_files.keys()):
                file_name = os.path.basename(file_path)
                action = QAction(file_name, self)
                action.triggered.connect(lambda checked, fp=file_path: self.remove_file(fp))
                remove_menu.addAction(action)

        menu.addSeparator()
        remove_plot_action = QAction("Remove This Plot Window", self)
        remove_plot_action.triggered.connect(lambda: self.remove_requested.emit(self))
        menu.addAction(remove_plot_action)

        menu.addSeparator()
        msg = 'Use normalization' if not self.normalized else 'Ignore normalization'
        toggle_normalized = QAction(msg, self)
        toggle_normalized.triggered.connect(self.toggle_normalization)
        menu.addAction(toggle_normalized)

        menu.exec(self.mapToGlobal(pos))

    def toggle_normalization(self) -> None:
        self.normalized = not self.normalized
        self.update_plot()

    def remove_file(self, file_path):
        if file_path in self.plotted_files:
            self.plotted_meas.pop(file_path)
            line = self.plotted_files.pop(file_path)
            line.remove()  # Remove line from axes
            self.update_plot()

    def update_plot(self) -> None:
        self.ax.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1), frameon=False)
        self.normalize()
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()
