from PySide6.QtWidgets import (
    QLabel,
    QFrame,
    QGridLayout,
    QToolButton,
    QMenu,
)
from PySide6.QtCore import Signal


class UserWidget(QFrame):
    clicked = Signal()

    def __init__(self, project=True, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            "*:hover{background-color:palette(dark)}"
            "*:pressed{background-color:palette(dark)}"
        )
        self.project = project
        self.parent = parent
        self.create_widgets()
        self.create_layout()
        self.create_style()

        self.connection = None

    def create_widgets(self):
        self.central_grid = QGridLayout(self)
        self.label_project = QLabel("Project        ")
        self.label_user = QLabel("")
        self.label_status = QLabel("")
        self.button_img = QToolButton()
        self.button_img.setMenu(QMenu("Sub menu", parent=self))
        self.button_img.setMinimumSize(32, 32)
        self.button_img.setMaximumSize(32, 32)

    def create_layout(self):
        self.central_grid.addWidget(self.button_img, 0, 0, 3, 1)
        self.central_grid.addWidget(self.label_project, 0, 1)
        self.central_grid.addWidget(self.label_user, 1, 1)
        self.central_grid.addWidget(self.label_status, 2, 1)

    def create_style(self):
        self.label_project.setStyleSheet("background-color:transparent")
        self.label_user.setStyleSheet("background-color:transparent")
        self.label_status.setStyleSheet("background-color:transparent")
        self.button_img.setStyleSheet(
            "QToolButton{border-image: url(base_app/icons/defaultUser.png) ;border-radius: 10px;background-color: transparent}"
            "QToolButton::menu-indicator {image: url(base_app/icons/off.png)}"
        )

        if not self.project:
            self.label_project.hide()

    def user(self):
        return self.label_user.text()

    def set_name(self, user=None, user_titan=None, user_admin=None):
        if user and user != "":
            self.label_user.setText(user)
            if user_titan or user_admin:
                self.button_img.setStyleSheet(
                    "QToolButton{border-image: url(base_app/icons/defaultUser.png) ;border-radius: 10px;color: rgba(255, 255, 255, 0)}"
                    "QToolButton::menu-indicator {image: url(base_app/icons/on_titan.png)}"
                )
            else:
                self.button_img.setStyleSheet(
                    "QToolButton{border-image: url(base_app/icons/defaultUser.png) ;border-radius: 10px;color: rgba(255, 255, 255, 0)}"
                    "QToolButton::menu-indicator {image: url(base_app/icons/on.png)}"
                )

        else:
            self.button_img.setStyleSheet(
                "QToolButton{border-image: url(base_app/icons/defaultUser.png) ;border-radius: 10px;color: rgba(255, 255, 255, 0)}"
                "QToolButton::menu-indicator {image: url(base_app/icons/off.png)}"
            )

        self.label_user.setText(user)

    def set_project(self, text):
        self.label_project.setText(text)

    def set_status(self, text):
        self.label_status.setText(text)

    def mousePressEvent(self, event):
        self.clicked.emit()
