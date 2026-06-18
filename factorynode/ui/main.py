from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QSpacerItem,
    QSizePolicy,
)
from PySide6.QtCore import Qt, QEvent

from ui.machine import BaseManchine
from ui.node_editor import NodeEditorViewer

NODE_TYPES = {"BaseMachine":BaseManchine}


class ToolBar(QWidget):
    def __init__(self, NODE_TYPES=dict(), parent=None):
        super().__init__()
        self.NODE_TYPES = NODE_TYPES
        self.create_widgets()
        self.create_layout()

    def create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setSpacing(5)
        for name, action in self.NODE_TYPES.items():
            if action == "-":
                self.main_layout.addWidget(QLabel(name))
                self.main_layout.addWidget(QLabel("____________"))
            else:
                btn = QPushButton(name)
                btn.clicked.connect(action)
                self.main_layout.addWidget(btn)

    def create_layout(self):
        self.main_layout.addItem(
            QSpacerItem(5, 1, QSizePolicy.Minimum, QSizePolicy.Expanding)
        )


class PanelContent(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.content = None
        self.create_widgets()
        self.setMinimumSize(300, 10)

    def create_widgets(self):
        self.main_layout = QVBoxLayout(self)
        self.close_button = QPushButton("X")
        self.main_layout.addWidget(self.close_button)
        self.close_button.clicked.connect(self.close)

    def setContent(self, content):
        self.show()
        if not self.content == content:
            if self.content:
                self.content.close()
            self.content = content
            self.main_layout.addWidget(content)
            content.show()


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.toolbar = ToolBar()
        self.node_editor_view = NodeEditorViewer()
        self.panel_Content = PanelContent()
        self.panel_Content.hide()

    def create_layout(self):
        self.main_layout.addWidget(self.toolbar)
        self.main_layout.addWidget(self.node_editor_view)
        self.main_layout.addWidget(self.panel_Content)

    def create_connections(self):
        self.node_editor_view.onNodeDoubleClicked.connect(self.panel_Content.setContent)

    def event(self, event):
        if not event.type() != QEvent.KeyPress:
            return False
        return super().event(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Tab:
            self.onContextMenu()
