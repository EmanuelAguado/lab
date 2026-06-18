from pathlib import Path
from threading import Thread
import time

from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QMovie, QGuiApplication
from PySide6.QtWidgets import (
    QMainWindow,
    QSizePolicy,
    QWidget,
    QVBoxLayout,
    QApplication,
    QLabel,
)

LOADING_GIF = f"{Path(__file__).parent.parent}/icons/ufo.gif"


def thread(function):
    def wrapper(*args, **kwargs):
        worker = Thread(target=function, args=args, kwargs=kwargs)
        worker.start()
        return kwargs
    return wrapper

class Loading(QWidget):
    on_close = Signal()
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_style()
        self.show()

    def create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.loading_label = QLabel()
        self.log = QLabel()
        self.loading_gif = QMovie(LOADING_GIF)
        self.loading_label.setMovie(self.loading_gif)
        self.loading_gif.start()

    def create_layout(self):
        self.main_layout.addWidget(self.loading_label)
        self.main_layout.addWidget(self.log)

    def create_connections(self):
        self.on_close.connect(self.close)

    def create_style(self):
        self.loading_label.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.log.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.log.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(420, 512)
        self.move(
            QGuiApplication.primaryScreen().availableGeometry().center()
            - self.frameGeometry().center()
        )


class App(QMainWindow):
    on_show = Signal()
    def __init__(self):
        super().__init__()
        self.loading = Loading()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_style()
        self.initialize()
        self.resize(800,600)

    def create_widgets(self):
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.menubar = self.menuBar()
        self.user_button = self.menubar.addAction("User")

    def create_layout(self):
        ...

    def create_connections(self):
        self.on_show.connect(self.show)

    def create_style(self):
        self.main_widget.setContentsMargins(0, 0, 0, 0)

    @thread
    def initialize(self):
        time.sleep(1) #example
        self.loading.log.setText("Loading last session...")
        time.sleep(1) #example
        self.loading.log.setText("Loading core...")
        time.sleep(1) #example
        self.loading.log.setText("Initialize...")
        time.sleep(1) #example
        self.on_show.emit()
        self.loading.on_close.emit()


if __name__ == "__main__":
    app = QApplication()
    instance = App()
    app.exec()
