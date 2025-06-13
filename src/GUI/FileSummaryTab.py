from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QSizePolicy, QFrame, QGroupBox, QFormLayout, QDoubleSpinBox, QHBoxLayout
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
import os
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from src.structs import AntennaMeasurement
from src.util import Logging

class PlotPreview(QFrame):
    def __init__(self, parent):
        super().__init__()
        self.setFrameShape(QFrame.StyledPanel)
        self.layout = QVBoxLayout()
        self.figure = Figure()

        self.canvas = FigureCanvas(self.figure)

        self.ax = self.figure.add_subplot(111, projection='polar')
        self.ax.set_theta_zero_location("N")
        
        
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        self.tab_parent = parent
        self.current_line = None

    def plot(self, meas: AntennaMeasurement) -> None:
        
        if self.current_line is not None:
            self.current_line.remove()
        self.current_line, = self.ax.plot(meas.angles_rad, meas.power, color='blue')
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def clear(self) -> None:
        if self.current_line is not None:
            self.current_line.remove()
        self.current_line = None
        self.canvas.draw()
        

class FileSummaryTab(QWidget):
    description = "Summary"
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.info_label = QLabel("Select file to summarize")
        self.content = QGroupBox('File information')
        content_layout = QFormLayout()

        query_info_widget = QWidget()
        query_info_layout = QVBoxLayout()

        power_info_widget = QWidget()
        power_info_layout = QHBoxLayout()
        self.power_at_label = QLabel('None')
        self.power_at_query = QDoubleSpinBox()
        self.power_at_query.setRange(0., 360.)
        self.power_at_query.setSingleStep(0.01)
        self.power_at_query.setDecimals(2)
        self.power_at_query.valueChanged.connect(self.update_power_query)

        power_info_layout.addWidget(QLabel('Power at angle'))
        power_info_layout.addWidget(self.power_at_query)
        power_info_layout.addWidget(self.power_at_label)
        power_info_widget.setLayout(power_info_layout)

        query_info_layout.addWidget(power_info_widget)
        query_info_widget.setLayout(query_info_layout)

        self.static_info = QTextEdit()
        self.static_info.setReadOnly(True)

        content_layout.addWidget(query_info_widget)
        content_layout.addWidget(self.static_info)
        self.content.setLayout(content_layout)

        self.visual_preview = PlotPreview(self)
        self.visual_preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.layout.addWidget(self.info_label)
        self.layout.addWidget(self.content)
        self.layout.addWidget(self.visual_preview)
        self.setLayout(self.layout)

        self.logger = Logging.get_logger('Summary Tab')
        self.current_meas = None

    def update_summary(self, file_path):
        if not os.path.isfile(file_path):
            self.info_label.setText("Not a file.")
            return
        
        ext = os.path.splitext(file_path)[1].lower()

        if ext != ".h5ant":
            self.info_label.setText(f"Ignored file type: {ext}")
            return
        
        self.info_label.setText(f"Measurement file selected: {file_path}")
        try:
            meas = AntennaMeasurement.from_file(file_path)
        except Exception as e:
            self.logger.error(f'Error reading file: {e}')
            self.current_meas = None
            return
        
        self.static_info.setText(meas.summary)
        self.visual_preview.plot(meas)
        self.current_meas = meas
        self.update_power_query(self.power_at_query.value())
            

    def update_power_query(self, value: float) -> None:
        if self.current_meas is None: return
        self.power_at_label.setText(f'{self.current_meas.power_at(value)} [dbm]')
        

