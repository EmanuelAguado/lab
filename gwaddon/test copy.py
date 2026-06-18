from functools import partial
from pprint import pprint
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QStackedWidget,
    QFrame,
    QLineEdit,
    QSpinBox,
    QGridLayout,
    QSpacerItem,
    QSizePolicy,
    QDoubleSpinBox,
    QCheckBox,
    QListWidget,
    QListWidgetItem,
    QComboBox,
)
from PySide6.QtCore import Qt, Signal
import sys
import json
from typing import get_args, get_origin, get_type_hints
from plugin.components import *
from ui.gwidgets import GLineEditCompleter


class ComponentsWidget(QComboBox):
    def __init__(self,components):
        super().__init__()
        self.components = components
        self.components.connect(self.refresh)
        self.refresh()

    def add_component(self, component):
        self.addItem(component.name, component)
        index = self.count() - 1
        component.connect(lambda: self.update_item(index, component))

    def update_item(self, index, component):
        self.setItemText(index, component.name)

    def refresh(self):
        current_component = self.currentData()
        self.clear()
        for component in self.components.list_components:
            print(component)
            self.add_component(component)
        if current_component:
            self.setCurrentText(current_component.name)


class Components:
    def __init__(self):
        self.list_components = list()
        self.connections: list = None

    def add_component(self,component):
        self.list_components.append(component)
        self.emit()

    def connect(self, callable: callable):
        if not self.connections:
            self.connections = list()
        self.connections.append(callable)

    def emit(self):
        if not self.connections:
            return
        for conn in self.connections:
            conn()
            
@dataclass
class Component:
    id: int
    _name: str
    _type: any
    connections: list = None
    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = value
        if self.emit:
            self.emit()
        print("NAME updated")

    @property
    def type(self) -> str:
        if self.emit:
            self.emit()
        return self._type

    @type.setter
    def type(self, value: str) -> None:
        self._type = value

    def connect(self, callable: callable):
        if not self.connections:
            self.connections = list()
        self.connections.append(callable)

    def emit(self):
        if not self.connections:
            return
        for conn in self.connections:
            conn()


def refresh():
    component2.name = "addon2 updated"
    component5 = Component(2, "addon3", "Gaddon3")
    component6 = Component(2, "plugin3", "Gplugin3")
    ADDONS.add_component(component5)
    PLUGINS.add_component(component6)
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    component = Component(1, "addon", "Gaddon")
    component2 = Component(2, "addon2", "Gaddon2")
    ADDONS = Components()
    ADDONS.add_component(component)
    ADDONS.add_component(component2)
    PLUGINS = Components()
    component3 = Component(1, "plugin", "Gplugin")
    component4 = Component(2, "plugin2", "Gplugin2")
    PLUGINS.add_component(component3)
    PLUGINS.add_component(component4)
    w = QWidget()
    l = QVBoxLayout(w)
    c = ComponentsWidget(ADDONS)
    b = QPushButton("REFRESH")
    b.clicked.connect(refresh)
    l.addWidget(c)
    l.addWidget(b)
    w.show()
    app.exec()
