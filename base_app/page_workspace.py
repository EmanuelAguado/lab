
from PySide6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QSpacerItem,
    QSizePolicy,
    QHBoxLayout,
)
from PySide6.QtCore import Signal


class PageWorkspace(QFrame):
    onLogoutClicked = Signal()
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.create_layout()
        self.create_style()

    def create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.central_layout = QHBoxLayout()

    def create_layout(self):
        self.main_layout.addItem(
            QSpacerItem(
                5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding
            )
        )
        self.main_layout.addLayout(self.central_layout)
        self.main_layout.addItem(
            QSpacerItem(
                5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding
            )
        )

    def create_style(self):
        self.main_layout.setSpacing(0)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

    def set_widget(self, widget):
        self.central_layout.addWidget(widget)
