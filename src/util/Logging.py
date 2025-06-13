

import logging
from PySide6.QtWidgets import QTextEdit
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QTextCursor

class QTextEditHandler(logging.Handler, QObject):
    log_signal = Signal(str)  # thread-safe signal to update QTextEdit

    def __init__(self, widget: QTextEdit):
        QObject.__init__(self)
        logging.Handler.__init__(self)
        self.widget = widget
        self.log_signal.connect(self.append_log)

    def emit(self, record):
        log_entry = self.format(record)
        self.log_signal.emit(log_entry)

    def append_log(self, msg):
        self.widget.append(msg)
        self.widget.moveCursor(QTextCursor.End)


def setup_logging(log_folder = '.', textedit = None) -> None:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] [%(name)s]: %(message)s',
        handlers=[
            logging.FileHandler(f'{log_folder}/app.log'),
            logging.StreamHandler(),
            QTextEditHandler(textedit)
        ]
    )

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)