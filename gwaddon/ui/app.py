from logging import getLogger, basicConfig, DEBUG

from PySide6.QtWidgets import (
    QMainWindow,
    QStackedWidget,
    QMessageBox,
)
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtCore import Signal

from ui.qtclasses.login import LoginPage
from ui.qtclasses.work import WorkPage
from ui.qtclasses.config import ConfigPage

logger = getLogger(__name__)
basicConfig(level=DEBUG)

# DATABASE = r"D:\PROJECTS\Gwaddon\gwaddon\studio.json"

class Main(QMainWindow):
    on_show = Signal()
    on_close = Signal()
    on_change_page = Signal(object)
    on_error = Signal(str) 

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.stacked_pages = QStackedWidget()
        self.setCentralWidget(self.stacked_pages)
        self.login_page = LoginPage()
        self.gwaddon_page = WorkPage()
        self.config_page = ConfigPage()
        self.add_page(self.login_page)
        self.add_page(self.gwaddon_page)
        self.add_page(self.config_page)
        self.create_connections()
        self.resize(1200, 600)
        self.set_title()
        self.setWindowIcon(QIcon("./gwaddon/utils/static/icons/gwaddon.ico"))
        self.set_style("./gwaddon/utils/static/styles/gwaddon.css")

    def add_page(self, *args, **kwargs):
        self.stacked_pages.addWidget(*args, **kwargs)

    def create_connections(self):
        self.on_show.connect(self.show)
        self.gwaddon_page.menu_styles_gwaddon.triggered.connect(
            lambda: self.set_style("./gwaddon/utils/static/styles/gwaddon.css")
        )
        self.config_page.on_close.connect(self.set_gwaddon_page)
        self.on_change_page.connect(self.change_page)
        self.on_error.connect(self.error)

    def change_page(self, page):
        self.stacked_pages.setCurrentWidget(page)

    def set_login_page(self):
        self.on_change_page.emit(self.login_page)

    def set_gwaddon_page(self):
        self.on_change_page.emit(self.gwaddon_page)

    def set_config_page(self, cfg):
        print(">>>",cfg)
        self.config_page.load_config(cfg)
        self.on_change_page.emit(self.config_page)

    def set_style(self, qss: str) -> None:
        try:
            with open(qss, "r") as ftr:
                css = ftr.read()
            self.setStyleSheet(css)
        except Exception as e:
            logger.error("Error reading stylesheet")
            logger.error(str(e))

    def set_title(self, project_name: str = "") -> None:
        title = "Gwaddon (woof, woof)"
        if project_name:
            title = f"{title} - {project_name}"
        self.setWindowTitle(title)

    def error(self, error: str):
        QMessageBox.critical(self, "Failed", error)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.on_close.emit()
        return super().closeEvent(event)
