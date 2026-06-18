from pathlib import Path
import time

from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QMainWindow,
    QSplashScreen,
    QWidget,
    QApplication,
)

SPLASH_IMAGE = f"{Path(__file__).parent.parent}/icons/ufo.gif"



class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()
        self.create_splash()
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
        ...

    def create_style(self):
        self.main_widget.setContentsMargins(0, 0, 0, 0)

    def create_splash(self):
        pixmap = QPixmap(SPLASH_IMAGE)
        self.splash = QSplashScreen(pixmap)
        self.splash.show()

    def initialize(self):
        time.sleep(1) #example
        self.splash.showMessage("Loading last session...")
        QCoreApplication.processEvents()
        time.sleep(1) #example
        self.splash.showMessage("Loading core...")
        QCoreApplication.processEvents()
        time.sleep(1) #example
        self.splash.showMessage("Initialize...")
        QCoreApplication.processEvents()
        time.sleep(1) #example
        self.show()


if __name__ == "__main__":
    app = QApplication()
    instance = App()
    app.exec()
