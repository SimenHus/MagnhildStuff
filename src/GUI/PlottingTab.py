from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QScrollArea, QGridLayout, QGroupBox, QComboBox,
    QHBoxLayout, QLabel, QFormLayout, QSpinBox
)
from PySide6.QtCore import Qt

from src.GUI.CustomWidgets import PlotWidget
from src.enums import Normalization
from src.util import Logging
import numpy as np

class PlottingTab(QWidget):
    description = 'Plotting'
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()

        self.add_button = QPushButton("Add Plot Window")
        self.add_button.clicked.connect(self.add_plot)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.settings_group = QGroupBox('Settings')
        self.settings_layout = QFormLayout()



        self.normalization_mode_selector = QComboBox()
        modes = list(Normalization)
        for mode in modes:
            self.normalization_mode_selector.addItem(mode.name, userData=mode)
        self.normalization_mode = modes[0]
        self.normalization_mode_selector.setCurrentIndex(0)
        self.normalization_mode_selector.currentIndexChanged.connect(self.update_normalization_mode)

        normalization_widget = QWidget()
        normalization_layout = QHBoxLayout()
        normalization_layout.addWidget(QLabel('Normalization mode:'))
        normalization_layout.addWidget(self.normalization_mode_selector)
        normalization_widget.setLayout(normalization_layout)

        columns_init = 2
        self.columns_spinbox = QSpinBox()
        self.columns_spinbox.setMinimum(1)
        self.columns_spinbox.setMaximum(5)
        self.columns_spinbox.setValue(columns_init)
        self.columns_spinbox.valueChanged.connect(self.update_columns)
        self.columns = columns_init
        columns_widget = QWidget()
        columns_layout = QHBoxLayout()
        columns_layout.addWidget(QLabel('Columns:'))
        columns_layout.addWidget(self.columns_spinbox)
        columns_widget.setLayout(columns_layout)

        self.settings_layout.addWidget(normalization_widget)
        self.settings_layout.addWidget(columns_widget)
        self.settings_layout.addWidget(self.add_button)
        self.settings_group.setLayout(self.settings_layout)

        self.plot_area = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.plot_area.setLayout(self.grid_layout)

        self.scroll_area.setWidget(self.plot_area)
        self.layout.addWidget(self.settings_group)
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

        self.plot_widgets = []
        self.setAcceptDrops(True)

        self.logger = Logging.get_logger('Plot Tab')


    def add_plot(self):
        plot_widget = PlotWidget(self)
        plot_widget.setMinimumSize(400, 300)
        plot_widget.remove_requested.connect(self.remove_plot)

        position = len(self.plot_widgets)
        row = position // self.columns
        col = position % self.columns

        self.grid_layout.addWidget(plot_widget, row, col)
        self.plot_widgets.append(plot_widget)
        self.logger.info('Created new plot')


    def remove_plot(self, plot_widget):
        if plot_widget in self.plot_widgets:
            index = self.plot_widgets.index(plot_widget)
            # Remove widget from layout and list
            self.plot_widgets.pop(index)
            self.grid_layout.removeWidget(plot_widget)
            plot_widget.deleteLater()
            self.relayout_grid()
            self.logger.info('Removed plot')

    def relayout_grid(self):
        # Clear the layout and re-add widgets in correct order
        for i in reversed(range(self.grid_layout.count())):
            item = self.grid_layout.itemAt(i)
            if item:
                widget = item.widget()
                if widget:
                    self.grid_layout.removeWidget(widget)

        for idx, widget in enumerate(self.plot_widgets):
            row = idx // self.columns
            col = idx % self.columns
            self.grid_layout.addWidget(widget, row, col)

    def handle_reorder(self, source_id, target_id):
        source_index = None
        target_index = None

        # Find indexes by matching id()
        for i, widget in enumerate(self.plot_widgets):
            if id(widget) == source_id:
                source_index = i
            if id(widget) == target_id:
                target_index = i
        if source_index is None or target_index is None or source_index == target_index:
            return

        # Swap widgets in list
        self.plot_widgets[source_index], self.plot_widgets[target_index] = \
            self.plot_widgets[target_index], self.plot_widgets[source_index]

        # Update layout
        self.relayout_grid()

    def global_update(self) -> None:
        for plot in self.plot_widgets:
            plot.prepare_for_update() # Prepare for plotting (update extremes etc)

        for plot in self.plot_widgets:
            plot.update_plot() # Perform plot update

    def update_normalization_mode(self, *args, **kwargs) -> None:
        self.normalization_mode = self.normalization_mode_selector.currentData(Qt.UserRole)
        self.global_update()

    def update_columns(self, value: int) -> None:
        self.columns = value
        self.relayout_grid()

    @property
    def peak(self) -> float:
        peak = -np.inf
        for plot in self.plot_widgets:
            if plot.peak is None: continue
            if plot.peak > peak: peak = plot.peak
        return peak
    
    @property
    def floor(self) -> float:
        floor = np.inf
        for plot in self.plot_widgets:
            if plot.floor is None: continue
            if plot.floor < floor: floor = plot.floor
        return floor