import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MplCanvas(FigureCanvas):
    def __init__(self, parent=None):
        fig = Figure()
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        self.setParent(parent)

        self.plot()

    def plot(self):
        x = [0, 1, 2, 3, 4]
        y1 = [i**2 for i in x]
        y2 = [i**1.5 for i in x]

        self.ax.plot(x, y1, label='Quadratic')
        self.ax.plot(x, y2, label='Power 1.5')

        legend = self.ax.legend()
        legend.set_draggable(True)  # This enables dragging the legend

        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Draggable Legend Example")

        canvas = MplCanvas(self)
        layout = QVBoxLayout()
        layout.addWidget(canvas)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()
