from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QDialog, QListWidget,
    QLineEdit, QDialogButtonBox, QPushButton, QLabel,
    QListWidgetItem, QColorDialog, QColorDialog, QSizePolicy, QWidget
)
from PySide6.QtGui import QColor
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

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

        extensions = ['pdf', 'png', 'jpg']

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



class PreviewCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure()
        super().__init__(self.fig)
        self.ax = self.fig.add_subplot(111, projection='polar')
        self.ax.set_theta_zero_location("N")

        self.lines = {}
        self.ax.set_title("Preview")
        self.fig.tight_layout()

    def plot_lines(self, lines) -> None:
        self.lines = {}
        for line in lines:
            label = line.get_label()
            color = line.get_color()
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            self.lines[label] = self.ax.plot(xdata, ydata, color=color, label=label)[0]


    def update_preview(self, colors):
        for i, (name, color) in enumerate(colors.items()):
            self.lines[name].set_color(color.name())
        self.ax.legend()
        self.draw()


class ColorDialog(QDialog):
    def __init__(self, plot_lines: dict, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Change Plot Colors")
        self.resize(1200, 400)
        self.plot_lines = plot_lines
        self.new_colors = {line.get_label(): QColor(line.get_color()) for line in self.plot_lines.values()}

        main_layout = QHBoxLayout(self)

        # Left: List of lines + color picker
        left_layout = QVBoxLayout()

        self.list_widget = QListWidget()
        for name, color in self.new_colors.items():
            item = QListWidgetItem(name)
            self.list_widget.addItem(item)

        self.list_widget.currentItemChanged.connect(self.update_color_picker)
        left_layout.addWidget(QLabel("Select Line:"))
        left_layout.addWidget(self.list_widget)

        self.color_picker = QColorDialog()
        self.color_picker.setOptions(QColorDialog.NoButtons | QColorDialog.ShowAlphaChannel)
        self.color_picker.setCurrentColor(self.new_colors[self.list_widget.item(0).text()])
        self.color_picker.currentColorChanged.connect(self.color_changed)
        left_layout.addWidget(QLabel("Pick Color:"))
        left_layout.addWidget(self.color_picker)

        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)
        left_layout.addWidget(self.ok_button)

        # Right: Plot preview
        preview_layout = QVBoxLayout()
        self.preview = PreviewCanvas()
        self.preview.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.preview.plot_lines(self.plot_lines.values())
        self.preview.update_preview(self.new_colors)
        preview_layout.addWidget(self.preview)

        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(preview_layout, 1)

    def update_color_picker(self, current, previous):
        if current:
            name = current.text()
            self.color_picker.setCurrentColor(self.new_colors[name])

    def color_changed(self, color):
        current_item = self.list_widget.currentItem()
        if current_item:
            name = current_item.text()
            self.new_colors[name] = color
            self.preview.update_preview(self.new_colors)

    def get_color_map(self) -> dict:
        result = {}
        for filename, line in self.plot_lines.items():
            label = line.get_label()
            result[filename] = self.new_colors[label].name()
        return result


