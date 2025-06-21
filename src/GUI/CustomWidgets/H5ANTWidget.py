
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QDialog, QMenu
)

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np
import os


from src.enums import Normalization
from src.structs import AntennaMeasurement
from src.util import Logging, Path

from .Dialogs import RenameLineDialog, SaveFigureDialog, ColorDialog

class H5ANTWidget(QFrame):
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
        self.legend = None
        
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self.setAcceptDrops(True)
        self.plotted_files = {}  # file_path: matplotlib line object
        self.plotted_meas = {} # file_path: AntennaMeasurement

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        self.tab_parent = parent
        self.peak = None
        self.floor = None

        self.logger = Logging.get_logger('h5ant Widget')


    def dragEnterEvent(self, event):
        # Accept external file drops
        if event.mimeData().hasUrls():
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
            self.logger.error(f"Failed to plot {file_path}: {e}")
            return False

    def open_context_menu(self, pos: QPoint):
        menu = QMenu(self)

        # Rename window
        rename_action = QAction('Rename line', self)
        if not self.plotted_files:
            rename_action.setDisabled(True)
        else:
            rename_action.triggered.connect(self.rename_line_dialog)
        menu.addAction(rename_action)

        color_action = QAction('Change colors', self)
        if not self.plotted_files:
            color_action.setDisabled(True)
        else:
            color_action.triggered.connect(self.change_color_dialog)
        menu.addAction(color_action)


        # Remove window
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

        # Save window
        menu.addSeparator()
        save_action = QAction('Save figure', self)
        if not self.plotted_files:
            save_action.setDisabled(True)
        else:
            save_action.triggered.connect(self.save_figure)
        menu.addAction(save_action)

        menu.exec(self.mapToGlobal(pos))

    def rename_line_dialog(self) -> None:

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

    def change_color_dialog(self) -> None:
        dlg = ColorDialog(self.plotted_files, self)
        if dlg.exec() != QDialog.Accepted: return

        new_colors = dlg.get_color_map()
        for key, color in new_colors.items():
            self.plotted_files[key].set_color(color)

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
        file = f'{filename}.{extension}'
        folder = Path.output_folder()
        path = Path.join(folder, file)
        self.figure.savefig(path, format=extension)
        self.logger.info(f'Saved figure to {path}')

    def prepare_for_update(self) -> None:
        self.determine_local_extremes()

    def update_legend(self) -> None:
        if not self.plotted_files: return
        if self.legend:
            bbox = self.legend.get_frame().get_bbox()
            bbox_axes = bbox.transformed(self.ax.transAxes.inverted())
            bbox_to_anchor = bbox_axes.bounds[:2]
            loc = self.legend._loc
            self.legend.remove()
            self.legend = self.ax.legend(loc=loc, bbox_to_anchor=bbox_to_anchor)
        else:
            self.legend = self.ax.legend()
        self.legend.set_draggable(True)

    def update_plot(self) -> None:
        self.update_legend()
        self.normalize()
        self.canvas.draw()