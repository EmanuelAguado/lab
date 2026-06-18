from pathlib import Path
import time

from PySide6.QtCore import Signal, QThread, Qt
from PySide6.QtGui import QMovie, QColor, QGuiApplication
from PySide6.QtWidgets import (
    QMainWindow,
    QApplication,
    QWidget,
    QVBoxLayout,
    QLabel,
    QStackedWidget,
    QGraphicsDropShadowEffect,
    QSizePolicy,
)
from page_login import PageLogin
from page_workspace import PageWorkspace

LOADING_GIF = f"{Path(__file__).parent}/icons/ufo.gif"

class Page:
    login_page = 0
    workspace_page = 1

class Loading(QMainWindow):
    on_close = Signal()
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_style()
        self.show()

    def create_widgets(self):
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.loading_gif = QMovie(LOADING_GIF)
        self.label_loading = QLabel()
        self.log = QLabel()
        self.label_loading.setMovie(self.loading_gif)
        self.loading_gif.start()

    def create_layout(self):
        self.setCentralWidget(self.main_widget)
        self.main_layout.addWidget(self.central_widget)
        self.central_layout.addWidget(self.label_loading)
        self.central_layout.addWidget(self.log)

    def create_connections(self):
        self.on_close.connect(self.close)

    def create_style(self):
        self.setStyleSheet("background-color:rgba(30,30,30,0);color:white")
        self.central_widget.setStyleSheet("background-color:rgb(30,30,30)")
        self.label_loading.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.log.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.log.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(420, 512)
        self.move(
            QGuiApplication.primaryScreen().availableGeometry().center()
            - self.frameGeometry().center()
        )
        self.sh = QGraphicsDropShadowEffect(self)
        self.sh.setColor(QColor(0, 0, 0, 255))
        self.sh.setBlurRadius(20)
        self.sh.setYOffset(0)
        self.sh.setXOffset(0)
        self.central_widget.setGraphicsEffect(self.sh)


class Initialize(QThread):
    def __init__(self, main):
        super().__init__()
        self.main = main

    def start(self, function):
        self.function = function
        return super().start()

    def run(self):
        self.function()


class App(QMainWindow):
    on_show = Signal()
    def __init__(self):
        super().__init__()
        self.loading = Loading()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_style()
        self.setup_ui()
        self.resize(800,600)

    def create_widgets(self):
        self.main_widget = QStackedWidget()
        self.setCentralWidget(self.main_widget)
        self.page_login = PageLogin(True)
        self.page_workspace = PageWorkspace()

        self.menubar = self.menuBar()
        self.user_button = self.menubar.addAction("User")

    def create_layout(self):
        self.main_widget.addWidget(self.page_login)
        self.main_widget.addWidget(self.page_workspace)

    def create_connections(self):
        self.on_show.connect(self.show)
        self.page_login.onLoginClicked.connect(lambda:self.change_page(Page.workspace_page))
        self.page_login.onCancelClicked.connect(lambda:self.change_page(Page.workspace_page))
        self.user_button.triggered.connect(lambda:self.change_page(Page.login_page))

    def create_style(self):
        self.main_widget.setContentsMargins(0, 0, 0, 0)

    def setup_ui(self):
        self.initialize_thread = Initialize(self)
        self.initialize_thread.start(self.initialize)
    
    def initialize(self):
        time.sleep(1)
        self.loading.log.setText("Loading last session...")
        time.sleep(1)
        self.loading.log.setText("Loading core...")
        time.sleep(1)
        self.loading.log.setText("Initialize...")
        time.sleep(1)
        self.on_show.emit()
        self.loading.on_close.emit()
        
    def change_page(self, index):
        self.main_widget.setCurrentIndex(index)


if __name__ == "__main__":
    app = QApplication()
    with open(f"{Path(__file__).parent}/style.css", "r") as ftr:
        css = ftr.read()
    app.setStyleSheet(css)
    instance = App()
    app.exec()
