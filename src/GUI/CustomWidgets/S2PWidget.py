
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QFrame, QDialog, QMenu, QFormLayout,
    QHBoxLayout, QCheckBox, QGroupBox, QSizePolicy, QLineEdit
)

from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QAction, QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.gridspec as gridspec

import skrf as rf

import numpy as np
import os


from src.enums import SParameter, SParamPlotLines
from src.structs import AntennaMeasurement
from src.util import Logging, Path

from .Dialogs import RenameLineDialog, SaveFigureDialog, ColorDialog


class S2PWidget(QFrame):
    # Signal emitted when this plot widget wants to be removed
    remove_requested = Signal(QWidget)

    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()


        settings_layout = QHBoxLayout()
        self.settings_group = QGroupBox("S-Parameters to Display")
        for s in SParameter:
            cb = QCheckBox(s.name)
            cb.setChecked(True)
            cb.stateChanged.connect(self.update_plot)
            cb.setObjectName(s.name)
            settings_layout.addWidget(cb)


        self.freq_input_A = QLineEdit()
        self.freq_input_B = QLineEdit()
        double_validator = QDoubleValidator(bottom=0.0)
        self.freq_input_A.setValidator(double_validator)
        self.freq_input_B.setValidator(double_validator)
        self.freq_input_A.editingFinished.connect(self.update_plot)
        self.freq_input_B.editingFinished.connect(self.update_plot)

        # Layout
        form_layout = QFormLayout()
        form_layout.addRow("Marker A (GHz):", self.freq_input_A)
        form_layout.addRow("Marker B (GHz):", self.freq_input_B)

        settings_layout.addLayout(form_layout)


        self.settings_group.setLayout(settings_layout)
        self.settings_group.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)


        self.figure = Figure(figsize=(10, 6))

        self.canvas = FigureCanvas(self.figure)
        self.canvas.setMouseTracking(True)
        self.canvas.installEventFilter(self)
 
        # Create the 3 subplots using gridspec
        self.gs = gridspec.GridSpec(2, 2, width_ratios=[2, 1], figure=self.figure)
        # self.ax_mag = self.figure.add_subplot(self.gs[0, 0])
        self.ax_mag = self.figure.add_subplot(self.gs[:, :])
        # self.ax_phase = self.figure.add_subplot(self.gs[1, 0])
        # self.ax_smith = self.figure.add_subplot(self.gs[:, 1])

        # self.ax_smith.set_title('Smith Chart')

        self.ax_mag.grid()
        # self.ax_phase.grid()

        self.legend = None
        self.bbox_to_anchor = None
        self.loc = 'upper right'

        self.layout.addWidget(self.settings_group)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self.setAcceptDrops(True)
        self.plotted_files = {} # file_path: label
        self.plotted_lines = {} # file_path: dict[S11: lines, ...]
        self.marker_lines = {
            'A': {'mag': None, 'phase': None},
            'B': {'mag': None, 'phase': None}
        }

        # Enable context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.open_context_menu)

        self.tab_parent = parent

        self.update_plot()
        self.logger = Logging.get_logger('s2p Widget')


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
                if ext in ['.s2p']:
                    if self.plot_file(file_path):
                        updated = True
            if updated:
                self.tab_parent.global_update()
            event.acceptProposedAction()


    def plot_file(self, file_path) -> bool:
        if file_path in self.plotted_files:
            return False  # Already plotted

        try:
            graph = rf.Network(file_path)
            label = os.path.basename(file_path).strip('.s2p')
            plotted_lines = {}
            for s in SParameter:
                before_mag = set(self.ax_mag.get_lines())
                # before_phase = set(self.ax_phase.get_lines())
                # before_smith = set(self.ax_smith.get_lines())
                graph.plot_s_db(m=s.m, n=s.n, ax=self.ax_mag, label=f'{label}-{s.name}')
                # graph.plot_s_deg(m=s.m, n=s.n, ax=self.ax_phase)
                # graph.plot_s_smith(m=s.m, n=s.n, ax=self.ax_smith)
                mag_line = [line for line in self.ax_mag.get_lines() if line not in before_mag][0]
                # phase_line = [line for line in self.ax_phase.get_lines() if line not in before_phase][0]
                # smith_line = [line for line in self.ax_smith.get_lines() if line not in before_smith][0]
                color = mag_line.get_color()
                # plotted_lines[s] = SParamPlotLines(mag_line, phase_line, smith_line, color)
                plotted_lines[s] = SParamPlotLines(mag_line, None, None, color)

            self.plotted_lines[file_path] = plotted_lines
            self.plotted_files[file_path] = label
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


        # # Remove window
        # menu.addSeparator()
        # remove_menu = menu.addMenu("Remove Plotted File")
        # if not self.plotted_files:
        #     remove_menu.setDisabled(True)
        # else:
        #     for file_path, line in self.plotted_files.items():
        #         label_name = line.get_label()
        #         action = QAction(label_name, self)
        #         action.triggered.connect(lambda checked, fp=file_path: self.remove_file(fp))
        #         remove_menu.addAction(action)

        # remove_plot_action = QAction("Remove This Plot Window", self)
        # remove_plot_action.triggered.connect(lambda: self.remove_requested.emit(self))
        # menu.addAction(remove_plot_action)

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
        labels = self.plotted_files.values()
        dialog = RenameLineDialog(labels, self)

        if dialog.exec() != QDialog.Accepted: return

        old_label = dialog.selected_label
        new_label = dialog.new_label

        for key, label in self.plotted_files.items():
            if label != old_label: continue
            self.plotted_files[key] = new_label
            break

        self.update_plot()

    def change_color_dialog(self) -> None:

        plotted_files = {}
        for file_path, sparams in self.plotted_lines.items():
            label = self.plotted_files[file_path]
            for s, plot_lines in sparams.items():
                plotted_files[f'{label}-{s.name}'] = plot_lines.mag

        dlg = ColorDialog(plotted_files, self)
        if dlg.exec() != QDialog.Accepted: return

        new_colors = dlg.get_color_map()
        for file_path, label in self.plotted_files.items():
            for color_label, color in new_colors.items():
                if label not in color_label: continue
                s_param = None
                for s in SParameter:
                    if s.name in color_label: s_param = s
                self.plotted_lines[file_path][s_param].color = color

        self.update_plot()


    def remove_file(self, file_path):
        if file_path in self.plotted_files:
            self.plotted_files.pop(file_path)
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
        return

    def update_legend(self) -> None:
        if not self.plotted_files: return

        if self.legend:
            bbox = self.legend.get_frame().get_bbox()
            bbox_axes = bbox.transformed(self.figure.transFigure.inverted())
            self.bbox_to_anchor = bbox_axes.bounds[:2]
            self.loc = self.legend._loc
            self.legend.remove()


        handles, labels = self.ax_mag.get_legend_handles_labels()
        filtered = [(h, l) for h, l in zip(handles, labels) if h.get_visible()]
        filtered_handles, filtered_labels = zip(*filtered) if filtered else ([], [])


        if not filtered:
            self.legend = None
        else:
            sorted_pairs = sorted(zip(filtered_labels, filtered_handles), key=lambda x: x[0])
            sorted_labels, sorted_handles = zip(*sorted_pairs) if sorted_pairs else ([], [])


            self.legend = self.figure.legend(handles=sorted_handles, labels=sorted_labels,
                                            loc=self.loc, bbox_to_anchor=self.bbox_to_anchor)
            self.legend.set_draggable(True)
        
        if self.ax_mag.get_legend() is not None: self.ax_mag.get_legend().remove()
        # if self.ax_phase.get_legend() is not None: self.ax_phase.get_legend().remove()
        # if self.ax_smith.get_legend() is not None: self.ax_smith.get_legend().remove()


    def update_plot_sparams(self) -> None:
        sparams_in_use = []
        for cb in self.settings_group.findChildren(QCheckBox):
            if not cb.isChecked(): continue
            sparams_in_use.append(SParameter[cb.objectName()])

        for file_path, line_dict in self.plotted_lines.items():
            for s, plot_lines in line_dict.items():
                show = s in sparams_in_use
                plot_lines.mag.set_label(f'{self.plotted_files[file_path]}-{s.name}')
                plot_lines.mag.set_visible(show)
                plot_lines.mag.set_color(plot_lines.color)
                # plot_lines.phase.set_visible(show)
                # plot_lines.phase.set_color(plot_lines.color)
                # plot_lines.smith.set_visible(show)
                # plot_lines.smith.set_color(plot_lines.color)



    def update_marker_lines(self):
        try:
            freq_A = float(self.freq_input_A.text())  # in GHz
        except ValueError:
            freq_A = None

        try:
            freq_B = float(self.freq_input_B.text())
        except ValueError:
            freq_B = None

        for key, freq in zip(('A', 'B'), (freq_A, freq_B)):
            # for ax_key, ax in [('mag', self.ax_mag), ('phase', self.ax_phase)]:
            for ax_key, ax in [('mag', self.ax_mag)]:
                # Remove old line if it exists
                line = self.marker_lines[key][ax_key]
                if line:
                    line.remove()

                if freq is not None:
                    # Add new vertical line
                    self.marker_lines[key][ax_key] = ax.axvline(
                        x=freq*1e9, color='darkred', linestyle='--', linewidth=1.2,
                        label=f'Marker {freq} GHz'
                    )
                else:
                    self.marker_lines[key][ax_key] = None

    def update_axis(self) -> None:
        self.ax_mag.relim(visible_only=True)
        self.ax_mag.autoscale_view()

    def update_plot(self) -> None:
        self.update_plot_sparams()
        self.update_marker_lines()
        self.update_legend()

        self.update_axis()

        # self.figure.tight_layout()
        self.canvas.draw_idle()
