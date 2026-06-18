from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QSpacerItem,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QMessageBox,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMovie, QColor

import metadata


class Loading(QMainWindow):
    on_close = Signal()
    on_show = Signal()
    on_set_log = Signal(str)
    on_error = Signal(str)

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
        self.bottom_layout = QVBoxLayout()
        self.title = QLabel(metadata.PROGRAM_NAME)
        self.loading_gif = QMovie("./gwaddon/utils/static/icons/splash.gif")
        self.label_loading = QLabel()
        self.log = QLabel()
        self.version = QLabel(f"Gwaddon {metadata.PROGRAM_VERSION}")
        self.author = QLabel(metadata.AUTHORS)
        self.license = QLabel(metadata.COPYRIGHT)

        self.label_loading.setMovie(self.loading_gif)
        self.loading_gif.start()

    def create_layout(self):
        self.setCentralWidget(self.main_widget)
        self.main_layout.addWidget(self.central_widget)

        self.central_layout.addWidget(self.title)
        self.central_layout.addItem(
            QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        self.central_layout.addWidget(self.label_loading)
        self.central_layout.addWidget(self.log)
        self.central_layout.addItem(
            QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        self.central_layout.addLayout(self.bottom_layout)

        self.bottom_layout.addWidget(self.version)
        self.bottom_layout.addWidget(self.author)
        self.bottom_layout.addWidget(self.license)

    def create_connections(self):
        self.on_close.connect(self.close)
        self.on_show.connect(self.show)
        self.on_set_log.connect(self.log.setText)
        self.on_error.connect(self.error)

    def create_style(self):
        self.setStyleSheet("background-color:palette(base)")
        self.central_widget.setStyleSheet(
            "background-color:palette(mid);border-radius:5px"
        )
        self.label_loading.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.log.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.log.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed))
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.resize(512, 512)
        self.move(
            self.screen().availableGeometry().center() - self.frameGeometry().center()
        )
        self.sh = QGraphicsDropShadowEffect(self)
        self.sh.setColor(QColor(0, 0, 0, 255))
        self.sh.setBlurRadius(20)
        self.sh.setYOffset(0)
        self.sh.setXOffset(0)
        self.central_widget.setGraphicsEffect(self.sh)
        self.title.setStyleSheet('font: 75 24pt "Consolas";color:white')
        self.title.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)
        self.version.setStyleSheet(
            'font-size:12px "Consolas";color:palette(light);margin-left:10px'
        )
        self.author.setStyleSheet(
            'font-size:12px "Consolas";color:palette(light);margin-left:10px'
        )
        self.license.setStyleSheet(
            'font-size:12px "Consolas";color:palette(light);margin-left:10px'
        )
        self.version.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.author.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.license.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

    def error(self, error: str):
        QMessageBox.critical(self, "Initialize Failed", error)
        self.close()
