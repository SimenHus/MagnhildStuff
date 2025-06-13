
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QDialog,
    QMenu, QApplication, QListWidget,
    QLineEdit, QDialogButtonBox
)

from PySide6.QtCore import Qt, QPoint, Signal, QMimeData, QByteArray, QDataStream, QIODevice, QEvent
from PySide6.QtGui import QDrag, QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os


from src.enums import Normalization
from src.structs import AntennaMeasurement
from src.util import Logging


class RenameLineDialog(QDialog):
    def __init__(self, line_labels, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename Line")

        self.selected_label = None
        self.new_label = None

        layout = QVBoxLayout(self)

        hlayout = QHBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.addItems(line_labels)
        self.list_widget.setCurrentRow(0)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter new label...")

        hlayout.addWidget(self.list_widget)
        hlayout.addWidget(self.input_field)

        layout.addLayout(hlayout)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.list_widget.currentTextChanged.connect(self.prefill_input)

        self.prefill_input(self.list_widget.currentItem().text())

    def prefill_input(self, text):
        self.input_field.setText(text)

    def accept(self):
        self.selected_label = self.list_widget.currentItem().text()
        self.new_label = self.input_field.text()
        super().accept()


class SaveFigureDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Figure")

        self.filename = None
        self.extension = None

        extensions = ['pdf', 'png']

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget()
        self.list_widget.addItems(extensions)
        self.list_widget.setCurrentRow(0)

        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Enter filename...')

        layout.addWidget(self.list_widget)
        layout.addWidget(self.input_field)

        # Dialog buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def accept(self):
        self.extension = self.list_widget.currentItem().text()
        self.filename = self.input_field.text()
        super().accept()



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
        self.peak = None
        self.floor = None

        self.logger = Logging.get_logger('PlotWidget')



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
            if updated:
                self.tab_parent.global_update()
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


    def determine_local_extremes(self) -> None:
        peak = -np.inf
        floor = np.inf
        for value in self.plotted_meas.values():
            if value.peak > peak: peak = value.peak
            if value.floor < floor: floor = value.floor
        self.peak = peak
        self.floor = floor
        

    def normalize(self) -> None:
        norm_mode = self.tab_parent.normalization_mode
        match norm_mode:
            case Normalization.IGNORED: peak, floor = 0, 0
            case Normalization.LOCAL: peak, floor = self.peak, self.floor
            case Normalization.GLOBAL: peak, floor = self.tab_parent.peak, self.tab_parent.floor
        
        for key, value in self.plotted_meas.items():
            self.plotted_files[key].set_ydata(value.power - peak)

        if norm_mode == Normalization.GLOBAL:
            self.ax.set_ylim(ymin=floor, ymax=0, auto=False)
        else:
            self.ax.relim()
            self.ax.autoscale_view()

    def plot_file(self, file_path) -> bool:
        if file_path in self.plotted_files:
            return False  # Already plotted

        try:
            meas = AntennaMeasurement.from_file(file_path)
            label = os.path.basename(file_path).strip('.h5ant')
            line, = self.ax.plot(meas.angles_rad, meas.power, label=label)
            self.plotted_files[file_path] = line
            self.plotted_meas[file_path] = meas
            return True
        except Exception as e:
            print(f"Failed to plot {file_path}: {e}")
            return False

    def open_context_menu(self, pos: QPoint):
        menu = QMenu(self)
        
        norm_msg = {
            Normalization.IGNORED: 'Ignore normalization',
            Normalization.LOCAL: 'Local normalization',
            Normalization.GLOBAL: 'Global normalization'
        }
        normalization_menu = menu.addMenu('Normalization mode')
        for norm_mode, msg in norm_msg.items():
            action = QAction(msg, self)
            action.triggered.connect(lambda checked, mode=norm_mode: self.tab_parent.set_normalization_mode(mode))
            if norm_mode == self.tab_parent.normalization_mode: action.setDisabled(True)
            normalization_menu.addAction(action)

        rename_action = QAction('Rename line', self)
        if not self.plotted_files:
            rename_action.setDisabled(True)
        else:
            rename_action.triggered.connect(self.rename_line_dialog)
        menu.addAction(rename_action)

        menu.addSeparator()
        remove_menu = menu.addMenu("Remove Plotted File")
        if not self.plotted_files:
            remove_menu.setDisabled(True)
        else:
            for file_path, line in self.plotted_files.items():
                label_name = line.get_label()
                action = QAction(label_name, self)
                action.triggered.connect(lambda checked, fp=file_path: self.remove_file(fp))
                remove_menu.addAction(action)

        remove_plot_action = QAction("Remove This Plot Window", self)
        remove_plot_action.triggered.connect(lambda: self.remove_requested.emit(self))
        menu.addAction(remove_plot_action)

        menu.addSeparator()
        save_action = QAction('Save figure', self)
        if not self.plotted_files:
            save_action.setDisabled(True)
        else:
            save_action.triggered.connect(self.save_figure)
        menu.addAction(save_action)

        menu.exec(self.mapToGlobal(pos))

    def rename_line_dialog(self):

        # Build list of current labels
        lines = self.plotted_files.values()
        items = [line.get_label() for line in lines]
        dialog = RenameLineDialog(items, self)

        if dialog.exec() != QDialog.Accepted: return

        old_label = dialog.selected_label
        new_label = dialog.new_label

        for line in lines:
            if line.get_label() != old_label: continue
            line.set_label(new_label)
            break
        self.update_plot()


    def remove_file(self, file_path):
        if file_path in self.plotted_files:
            self.plotted_meas.pop(file_path)
            line = self.plotted_files.pop(file_path)
            line.remove()  # Remove line from axes
            self.tab_parent.global_update()


    def save_figure(self) -> None:
        
        dialog = SaveFigureDialog(self)

        if dialog.exec() != QDialog.Accepted: return

        filename = dialog.filename
        extension = dialog.extension
        path = f'./output/{filename}.{extension}'
        self.figure.savefig(path, format=extension)
        self.log(f'Saved figure to {path}')


    def update_plot(self) -> None:
        self.ax.legend(loc='upper left', bbox_to_anchor=(-0.35, 1.18), frameon=True)
        self.determine_local_extremes()
        self.normalize()
        self.canvas.draw()

    def log(self, msg) -> None:
        self.logger.info(msg)