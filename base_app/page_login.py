from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QWidget,
    QApplication,
    QStackedWidget,
    QGraphicsDropShadowEffect,
)
from PySide6.QtGui import QPalette, QColor
from PySide6.QtCore import Signal, Qt, QPointF

from widget_button import AToolButton, APushButton, RoundButton


class WidgetLogOut(QFrame):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.create_widgets()
        self.create_layout()
        self.create_style()
        self.create_connections()

    def create_widgets(self):
        self.central_layout = QVBoxLayout(self)
        self.user_label = QLabel(" Sign out? ")
        self.logout_button = AToolButton()
        self.cancel_button = AToolButton()

    def create_layout(self):
        self.central_layout.addItem(
            QSpacerItem(5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        self.central_layout.addWidget(self.user_label)
        self.central_layout.addWidget(self.logout_button)
        self.central_layout.addWidget(self.cancel_button)
        self.central_layout.addItem(
            QSpacerItem(5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def create_style(self):
        self.user_label.setStyleSheet('*{font: 50 14pt "Consolas";}')

        self.central_layout.setSpacing(40)
        self.central_layout.setContentsMargins(30, 30, 30, 30)

        self.logout_button.setText(" Log out ")
        self.logout_button.setAnimation(
            250,
            QPalette().color(QPalette.Dark).name(),
            QPalette().color(QPalette.Highlight).name(),
        )
        self.logout_button.setMinimumSize(100, 50)
        self.logout_button.setMaximumSize(1000, 50)

        self.cancel_button.setText(" Cancel ")
        self.cancel_button.setAnimation(
            250,
            QPalette().color(QPalette.Dark).name(),
            QPalette().color(QPalette.Dark).name(),
        )
        self.cancel_button.setMinimumSize(100, 50)
        self.cancel_button.setMaximumSize(1000, 50)

    def create_connections(self):
        self.logout_button.clicked.connect(self.parent.logout)
        self.cancel_button.clicked.connect(self.parent.onCancelClicked.emit)


class WidgetLogin(QFrame):
    def __init__(self, parent=None):
        super().__init__()
        self.parent = parent
        self.create_widgets()
        self.create_layout()
        self.create_style()
        self.create_connections()

    def create_widgets(self):
        self.central_layout = QVBoxLayout(self)
        self.login_label = QLabel("LOGIN")
        self.user_label = QLabel("User ")
        self.user_edit = QLineEdit()
        self.password_label = QLabel("Password ")
        self.password_edit = QLineEdit()

        self.buttons_layout = QHBoxLayout()
        self.login_button = APushButton(title=" Login ", radius=5)

    def create_layout(self):
        self.buttons_layout.addWidget(self.login_button)

        self.central_layout.addItem(
            QSpacerItem(5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )
        self.central_layout.addWidget(self.login_label)
        self.central_layout.addWidget(self.user_label)
        self.central_layout.addWidget(self.user_edit)
        self.central_layout.addWidget(self.password_label)
        self.central_layout.addWidget(self.password_edit)
        self.central_layout.addLayout(self.buttons_layout)
        self.central_layout.addItem(
            QSpacerItem(5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )

    def create_style(self):
        self.login_label.setSizePolicy(
            QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        )
        self.login_label.setStyleSheet('*{font: 50 22pt "Consolas";}')
        self.login_label.setAlignment(Qt.AlignCenter | Qt.AlignCenter)

        self.user_label.setStyleSheet('*{font: 50 12pt "Consolas";}')

        self.central_layout.setSpacing(20)
        self.central_layout.setContentsMargins(30, 30, 30, 30)

        self.user_edit.setPlaceholderText(" Username or email...")
        self.user_edit.setClearButtonEnabled(True)
        self.user_edit.setStyleSheet(
            "*{background:transparent;border:0px solid transparent;border-bottom: 1px solid palette(mid); border-radius:0px}*:hover{border:0px;border-bottom: 1px solid palette(Highlight)}*:focus{border:0px;border-bottom: 1px solid palette(Highlight)}"
        )

        self.password_label.setStyleSheet('*{font: 50 12pt "Consolas";}')

        self.password_edit.setPlaceholderText(" Insert password...")
        self.password_edit.setClearButtonEnabled(True)
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setStyleSheet(
            "*{background:transparent;border:0px solid transparent;border-bottom: 1px solid palette(mid); border-radius:0px}*:hover{border-bottom: 1px solid palette(Highlight)}*:focus{border-bottom: 1px solid palette(Highlight)}"
        )

        
        self.login_button.setAnimation(
            150,
            QPalette().color(QPalette.Dark).name(),
            QPalette().color(QPalette.Highlight).name(),
        )
        self.login_button.setMinimumSize(100, 50)
        self.login_button.setMaximumSize(1000, 50)

    def create_connections(self):
        self.login_button.clicked.connect(self.parent.login)


class PageLogin(QFrame):
    onLoginClicked = Signal()
    onLogoutClicked = Signal()
    onLoginError = Signal()
    onCancelClicked = Signal()
    def __init__(self, logout=False):

        super().__init__()
        self.create_widgets()
        self.create_layout()
        self.create_style()
        self.create_connections()
        self.menu_widget.setCurrentIndex(1)
        if logout:
            self.menu_widget.setCurrentIndex(0)

    def create_widgets(self):
        self.main_layout = QGridLayout(self)
        self.central_widget = QWidget()
        self.central_widget.setObjectName("central_widget")
        self.central_layout = QVBoxLayout(self.central_widget)

        self.title_frame = QFrame()
        self.title_layout = QGridLayout(self.title_frame)

        self.img = RoundButton(
            text="Change image",
            icon="base_app/icons/ico.png",
            size=[128, 128],
            background="palette(dark)",
        )

        self.title_layout.addWidget(self.img)
        self.log = QLabel(" ")
        self.menu_widget = QStackedWidget()
        self.module_login = WidgetLogin(self)
        self.module_logout = WidgetLogOut(self)

    def create_layout(self):
        self.main_layout.addWidget(self.central_widget, 1, 1)
        self.menu_widget.addWidget(self.module_login)
        self.menu_widget.addWidget(self.module_logout)

        self.central_layout.addWidget(self.title_frame)
        self.central_layout.addWidget(self.log)
        self.central_layout.addWidget(self.menu_widget)

    def create_style(self):
        self.title_frame.setStyleSheet(
            "QFrame{background:palette(HighLight);border-bottom-left-radius:0px;border-bottom-right-radius:0px}"
        )

        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)

        self.title_layout.setHorizontalSpacing(0)
        self.title_layout.setVerticalSpacing(0)
        self.title_layout.setContentsMargins(0, 0, 0, 0)

        self.title_frame.setMinimumSize(400, 175)
        self.title_frame.setMaximumSize(400, 175)

        self.img.setIcon("base_app/icons/ico.png")
        self.img.setActive(False)

        self.log.setAlignment(Qt.AlignCenter | Qt.AlignCenter)
        self.log.setStyleSheet('*{font: 50 10pt "Consolas";background:red}')
        self.log.setMinimumSize(400, 30)
        self.log.setMaximumSize(400, 30)
        self.log.hide()

        self.menu_widget.setMinimumSize(400, 325)
        self.menu_widget.setMaximumSize(400, 325)

        e = QGraphicsDropShadowEffect(
            self, offset=QPointF(0, 0), blurRadius=50, color=QColor(0, 0, 0, 255)
        )
        self.central_widget.setGraphicsEffect(e)
        self.central_widget.setSizePolicy(
            QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        )
        self.central_widget.setStyleSheet("border-radius:10px")

    def create_connections(self):
        pass

    def back(self):
        self.menu_widget.setCurrentIndex(0)
        self.log.hide()

    def logout(self):
        # RELLENAR FUNCION DE DESCONEXION O CONECTAR SIGNAL
        self.onLogoutClicked.emit()
        self.menu_widget.setCurrentIndex(0)

    def login(self):
        # RELLENAR FUNCION DE CONEXION O CONECTAR SIGNAL
        self.onLoginClicked.emit()
        self.menu_widget.setCurrentIndex(1)


if __name__ == "__main__":

    app = QApplication()
    app.setStyle("Fusion")

    window = PageLogin(True)
    window.show()

    app.exec()
