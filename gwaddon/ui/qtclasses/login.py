from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QSpacerItem,
    QSizePolicy,
    QFrame,
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QGridLayout,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QColor, QPalette, QPixmap
from PySide6.QtCore import Qt, QPointF, Signal

from ui.gwidgets import GAnimPushButton


class ModuleTitle(QFrame):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.create_style()

    def create_widgets(self):
        self.title_layout = QHBoxLayout(self)
        self.login_label = QLabel(" LOGIN")
        self.img = QLabel()
        self.img.setPixmap(QPixmap("./gwaddon/utils/static/icons/gwaddon.ico"))
        self.title_layout.addWidget(self.login_label)
        self.title_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )
        self.title_layout.addWidget(self.img)

    def create_style(self):
        self.setStyleSheet(
            "QFrame{background:palette(HighLight);border-bottom-left-radius:0px;border-bottom-right-radius:0px}"
        )
        self.title_layout.setSpacing(0)
        self.title_layout.setContentsMargins(10, 10, 10, 10)
        self.setMinimumSize(400, 100)
        self.setMaximumSize(400, 100)
        self.login_label.setSizePolicy(
            QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        )
        self.login_label.setStyleSheet('*{font: 50 22pt "Consolas";}')
        self.login_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class ModuleLogin(QFrame):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.create_layout()
        self.create_style()
        self.create_connections()

    def create_widgets(self):
        self.central_layout = QVBoxLayout(self)
        self.user_label = QLabel("User ")
        self.user_edit = QLineEdit()
        self.password_label = QLabel("Password ")
        self.password_edit = QLineEdit()

        self.buttons_layout = QHBoxLayout()
        self.login_button = GAnimPushButton(title=" Login ", radius=5)

    def create_layout(self):
        self.buttons_layout.addWidget(self.login_button)
        self.central_layout.addItem(
            QSpacerItem(5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        self.central_layout.addWidget(self.user_label)
        self.central_layout.addWidget(self.user_edit)
        self.central_layout.addWidget(self.password_label)
        self.central_layout.addWidget(self.password_edit)
        self.central_layout.addLayout(self.buttons_layout)
        self.central_layout.addItem(
            QSpacerItem(5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def create_style(self):
        self.setStyleSheet(
            "background:palette(base);border-top-left-radius:0px;border-top-right-radius:0px"
        )
        self.user_label.setStyleSheet('*{font: 50 12pt "Consolas";}')
        self.central_layout.setSpacing(20)
        self.central_layout.setContentsMargins(30, 30, 30, 30)
        self.user_edit.setPlaceholderText(" Username or email...")
        self.user_edit.setClearButtonEnabled(True)
        self.user_edit.setStyleSheet(
            "QLineEdit{background:palette(base);border-color:transparent;border-bottom: 1px solid palette(window); border-radius:0px}"
            "QLineEdit:hover{background:palette(base);border-color:transparent;border-bottom: 1px solid palette(Highlight); border-radius:0px}"
            "QLineEdit:focus{background:palette(base);border-color:transparent;border-bottom: 1px solid palette(Highlight); border-radius:0px}"
        )
        self.password_label.setStyleSheet('*{font: 50 12pt "Consolas";}')
        self.password_edit.setPlaceholderText(" Insert password")
        self.password_edit.setClearButtonEnabled(True)
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet(
            "QLineEdit{background:palette(base);border-color:transparent;border-bottom: 1px solid palette(window); border-radius:0px}"
            "QLineEdit:hover{background:palette(base);border-color:transparent;border-bottom: 1px solid palette(Highlight)}"
            "QLineEdit:focus{background:palette(base);border-color:transparent;border-bottom: 1px solid palette(Highlight)}"
        )
        self.login_button.setAnimation(
            150,
            QPalette().color(QPalette.Window).name(),
            QPalette().color(QPalette.Highlight).name(),
        )
        self.login_button.setMinimumSize(100, 50)
        self.login_button.setMaximumSize(1000, 50)

    def create_connections(self): ...


class LoginPage(QFrame):
    on_login = Signal(str, str)
    on_set_log = Signal(str)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_widgets()
        self.create_layout()
        self.create_style()
        self.create_connections()

    def create_widgets(self):
        self.main_layout = QGridLayout(self)
        self.central_widget = QWidget()
        self.central_layout = QVBoxLayout(self.central_widget)
        self.title_frame = ModuleTitle()
        self.log = QLabel(" ")
        self.module_login = ModuleLogin()

    def create_layout(self):
        self.main_layout.addWidget(self.central_widget, 1, 1)
        self.central_layout.addWidget(self.title_frame)
        self.central_layout.addWidget(self.log)
        self.central_layout.addWidget(self.module_login)

    def create_style(self):
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.log.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.log.setStyleSheet(
            '*{font: 50 10pt "Consolas";background:rgb(237,67,55);border-radius:0px}'
        )
        self.log.setMinimumSize(400, 30)
        self.log.setMaximumSize(400, 30)
        self.log.hide()
        self.central_widget.setStyleSheet("border-radius:10px")
        self.central_widget.setMinimumSize(400, 400)
        self.central_widget.setMaximumSize(400, 400)
        e = QGraphicsDropShadowEffect(
            self,
            offset=QPointF(0, 0),
            blurRadius=50,
            color=QColor(0, 0, 0, 255),
        )
        self.central_widget.setGraphicsEffect(e)
        self.central_widget.setSizePolicy(
            QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        )

    def create_connections(self):
        self.module_login.login_button.clicked.connect(
            lambda: self.on_login.emit(
                self.module_login.user_edit.text(),
                self.module_login.password_edit.text(),
            )
        )
        self.on_set_log.connect(self.set_log)

    def set_log(self, text):
        self.log.show()
        self.log.setText(text)
