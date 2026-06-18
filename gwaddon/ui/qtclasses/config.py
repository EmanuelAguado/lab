from fnmatch import fnmatch
from functools import partial
from pprint import pprint
from typing import get_args, get_origin
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
    QMessageBox,
    QLabel,
)
from PySide6.QtCore import Qt, Signal

from plugin.components import *


# TODO:
# setear ID cuando se crea
# hacer campos instanciados
# añadir sistema de limpieza/reseteo antes de cargar
# buscar el punto donde se cargan los componentes, plugins y addons
# hacer sistema de guardado de base de datos, además, añadir filtro de hash de user que valide el role y que el user es del estudio
# visualizador de cambios antes de guardar


class IDManager:
    def __init__(self):
        self.current_id = 0

    def next_id(self):
        self.current_id += 1
        return self.current_id


id_manager = IDManager()


def detect_type(value):
    args = get_args(value)
    return [get_origin(value) or value, args[0] if args else None]


def field_widget(field_name, type_):
    if fnmatch(field_name, "__*__"):
        type_ = LockedField
    type_, _ = detect_type(type_)
    if type_ == int:
        widget = QSpinBox()
        widget.value_changed = widget.valueChanged
        widget.value = widget.value
        widget.set_value = widget.setValue
    elif type_ == float:
        widget = QDoubleSpinBox()
        widget.value_changed = widget.valueChanged
        widget.value = widget.value
        widget.set_value = widget.setValue
    elif type_ == bool:
        widget = QCheckBox()
        widget.value_changed = widget.stateChanged
        widget.value = widget.isChecked
        widget.set_value = widget.setChecked
    elif type_ in COMPONENTS.keys():
        widget = ComponentsWidget(COMPONENTS[type_]["__components__"])
        widget.value_changed = widget.currentTextChanged
    elif type_ == LockedField:
        widget = LockedField()
        widget.value_changed = None
    else:
        widget = QLineEdit()
        widget.value_changed = widget.textChanged
        widget.value = widget.text
        widget.set_value = widget.setText
    return widget


def select_component(cfg, parent):
    combobox = QComboBox()
    list_components = COMPONENTS.get(cfg)
    if not list_components:
        return cfg.__name__
    list_components_by_type = list(list_components.keys())
    combobox.addItems(list_components_by_type)
    msgbox = QMessageBox(parent)
    msgbox.layout().addWidget(QLabel("Select component"))
    msgbox.layout().addWidget(combobox)
    msgbox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    msgbox.exec()
    return combobox.currentText()


class LockedField(QLabel):
    def __init__(self, text=None, parent=None):
        super().__init__("", parent)
        self.real_value = text
        if text:
            self.set_value(text)

    def set_value(self, value):
        self.real_value = value
        self.setText(str(value))

    def value(self):
        return self.real_value


class ComponentsWidget(QComboBox):
    def __init__(self, components):
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
            self.add_component(component)
        if current_component:
            self.setCurrentText(current_component.name)

    def set_value(self, id_):
        for item in range(self.count()):
            component = self.itemData(item)
            if component.id == id_:
                self.setCurrentIndex(item)

    def value(self):
        for item in range(self.count()):
            component = self.currentData()
            return component.id


class Components:
    def __init__(self):
        self.list_components = list()
        self.connections: list = None

    def add_component(self, component):
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


def find_type_component_by_class(current_class):
    if not issubclass(current_class, GComponent) or current_class == GComponent:
        return None
    main = current_class
    while current_class is not None and current_class != GComponent:
        current_class = current_class.__bases__[0]
        if current_class != GComponent:
            return current_class
    return main


COMPONENTS = dict()
dict_class = {name: obj for name, obj in locals().items() if isinstance(obj, type)}

for name, class_ in dict_class.items():
    if component_type := find_type_component_by_class(class_):
        if component_type not in COMPONENTS.keys():
            COMPONENTS[component_type] = {name: None, "__components__": Components()}
        COMPONENTS[component_type][name] = dict(class_.config_class.default().items())


class FieldWidget(QTreeWidgetItem):
    def __init__(self, field, type_, parent, widget, *args, **kwargs) -> None:
        super().__init__([field.replace("__", "")], *args, **kwargs)
        self.field = field
        self.type = type_
        self.parent = parent
        self.widget = widget

        self.setTextAlignment(0, Qt.AlignRight)
        if parent:
            if isinstance(parent, DictConfigWidget):
                parent.addTopLevelItem(self)
                parent.setItemWidget(self, 1, self.widget)
            else:
                parent.addChild(self)
                parent.treeWidget().setItemWidget(self, 1, self.widget)

    def value(self):
        return self.widget.value()

    def set_value(self, config_data):
        self.widget.set_value(config_data)


class ListFieldWidget(QWidget):
    def __init__(self, widget, parent) -> None:
        super().__init__()
        self.widget = widget
        self.item = QListWidgetItem()

        delete_button = QPushButton("X")
        delete_button.clicked.connect(partial(parent.remove_field, self.item))
        delete_button.setMaximumWidth(32)
        delete_button.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        layout = QHBoxLayout(self)
        layout.addWidget(self.widget)
        layout.addWidget(delete_button)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        parent.insertItem(parent.count(), self.item)
        parent.setItemWidget(self.item, self)
        self.item.setSizeHint(self.sizeHint())

    def value(self):
        return self.widget.value()

    def set_value(self, config_data):
        self.widget.set_value(config_data)

    def adjust_size(self):
        self.item.setSizeHint(self.sizeHint())


class ListConfigWidget(QListWidget):
    on_resize = Signal(int)

    def __init__(self, field, cfg, data, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.field = field
        self.cfg = cfg
        self._data = data
        self.parent = parent

        self.add_button_item = QListWidgetItem()
        self.add_button = QPushButton("+", clicked=self.add_field)
        self.insertItem(self.count(), self.add_button_item)
        self.setItemWidget(self.add_button_item, self.add_button)
        self.add_button_item.setSizeHint(self.add_button.sizeHint())
        self.setResizeMode(QListWidget.Adjust)
        FieldWidget(field, data, parent, self)

    def add_field(self, value=None, cfg=None):
        item = QListWidgetItem()
        if isinstance(self._data, list):
            data = self._data[0]
            if cfg is None:
                cfg = select_component(self.cfg, self)
            if COMPONENTS.get(self.cfg):
                if COMPONENTS.get(self.cfg).get(cfg):
                    data = COMPONENTS.get(self.cfg).get(cfg)
            widget = DictConfigWidget(self.field, cfg, data, None)
        else:
            _, item_type = detect_type(self._data)
            widget = field_widget(self.field, item_type)
        if value:
            widget.set_value(value)
        item = ListFieldWidget(widget, self)
        if hasattr(widget, "on_resize"):
            widget.on_resize.connect(item.adjust_size)

    def remove_field(self, item):
        row = self.row(item)
        self.takeItem(row)
        self.removeItemWidget(item)
        self.adjust_size()

    def set_value(self, config_data):
        for data in config_data:
            type_ = None
            if isinstance(data, dict):
                type_ = data.get("__type__")
            self.add_field(data, type_)

    def value(self):
        data = list()
        for index in range(self.count()):
            item = self.item(index)
            widget = self.itemWidget(item)
            if isinstance(widget, QPushButton):
                continue
            data.append(widget.value())
        return data

    def setItemWidget(self, item, widget):
        super().setItemWidget(item, widget)
        if not self.parent:
            return
        self.adjust_size()

    def adjust_size(self):
        height = 0
        for index in range(self.count()):
            height += self.sizeHintForRow(index)
        self.setFixedHeight(height + 4 * self.frameWidth())

    def resizeEvent(self, event):
        self.on_resize.emit(self.height())
        super().resizeEvent(event)


class DictConfigWidget(QTreeWidget):
    on_resize = Signal(int)

    def __init__(self, field, cfg, data, parent, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setColumnCount(2)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.header().hide()
        self.expandAll()
        self.field = field
        self.cfg = cfg
        self._data = data
        self.parent = parent
        self.config_widgets = dict()
        FieldWidget(field, data, parent, self)

        if isinstance(data, list):
            self.config_widgets[field] = ListConfigWidget(field, cfg, data, self)
        elif isinstance(data, dict):
            for sub_field, sub_type in self._data.items():
                type_, args_ = detect_type(sub_type)
                if type_ == list:
                    self.config_widgets[sub_field] = ListConfigWidget(
                        sub_field, args_, sub_type, self
                    )
                elif type_ == dict:
                    self.config_widgets[sub_field] = DictConfigWidget(
                        sub_field, args_, sub_type, self
                    )
                else:
                    self.config_widgets[sub_field] = FieldWidget(
                        sub_field, sub_type, self, field_widget(sub_field, sub_type)
                    )
        else:
            self.config_widgets[field] = FieldWidget(
                field, data, self, field_widget(data)
            )

    def setItemWidget(self, item, column, widget):
        super().setItemWidget(item, column, widget)
        if item.field == "__id__":
            if item.value() != 0:
                widget.set_value(id_manager.next_id())
            self.add_component()
        elif item.field == "__type__":
            cfg = self.cfg if isinstance(self.cfg, str) else self.cfg.__name__
            widget.set_value(cfg)
        elif item.field == "name":
            if widget.value_changed:
                widget.value_changed.connect(self.add_component)
        if isinstance(widget, ListConfigWidget):
            widget.on_resize.connect(
                lambda: self.itemDelegate().sizeHintChanged.emit(column)
            )
            widget.on_resize.connect(self.adjust_size)

    def value(self):
        data = dict()
        for index in range(self.topLevelItemCount()):
            item = self.topLevelItem(index)
            field = item.field
            value = self.itemWidget(item, 1).value()
            data[field] = value
        return data

    def set_value(self, config_data):
        for field, data in config_data.items():
            config_widget = self.config_widgets[field]
            if isinstance(config_widget, dict):
                for f, v in data.items():
                    config_widget[f].set_value(v)
            else:
                config_widget.set_value(data)

    def add_component(self):
        data = self.value()
        id_ = data.get("__id__")
        name = data.get("name")
        type_ = data.get("__type__")
        if not type_ in globals():
            return
        class_ = globals()[type_]
        component = [
            comp
            for comp_type in COMPONENTS.keys()
            for comp in COMPONENTS[comp_type]["__components__"].list_components
            if id_ == comp.id
        ]

        if component:
            component[0].name = name
        else:
            for comp_type in COMPONENTS.keys():
                if issubclass(class_, comp_type):
                    COMPONENTS[comp_type]["__components__"].add_component(
                        Component(id_, name, type_)
                    )

    def adjust_size(self):
        total_height = 0
        for row in range(self.topLevelItemCount()):
            total_height += self.sizeHintForRow(row)
        self.setMinimumHeight(total_height)
        self.on_resize.emit(total_height)


class ConfigPage(QMainWindow):
    on_close = Signal()

    def __init__(self):
        super().__init__()
        self.config_data = dict()
        self.config_widgets = dict()
        self.setWindowTitle("Configuración")
        self.setGeometry(300, 300, 800, 600)
        self.create_widgets()
        self.setStyleSheet(
            "DictConfigWidget::item{background:transparent;color:palette(text)};"
            "ListConfigWidget::item{background:transparent;color:palette(text)};"
        )

    def create_widgets(self):
        widget = QWidget()
        self.setCentralWidget(widget)
        main_layout = QGridLayout(widget)
        self.menu_layout = QVBoxLayout()
        bottom_layout = QHBoxLayout()
        self.stack = QStackedWidget()

        self.create_config("Studio", GStudio, dict)
        self.create_config("Projects", GProject, list)
        self.create_config("Plugins", GPlugin, list)
        self.create_config("Addons", GAddon, list)
        self.create_config("Users", GUser, list)

        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.menu_layout.addSpacerItem(spacer)
        self.apply_button = QPushButton("Apply", clicked=self.apply_changes)
        self.cancel_button = QPushButton("Cancel", clicked=self.close)
        bottom_layout.addWidget(self.cancel_button)
        bottom_layout.addWidget(self.apply_button)
        main_layout.addLayout(self.menu_layout, 0, 0, 2, 1)
        main_layout.addWidget(self.stack, 0, 1, 1, 1)
        main_layout.addLayout(bottom_layout, 1, 1, 1, 1)

    def create_config(self, name: str, cfg: GComponent, type_: type):
        data = dict(cfg.config_class.default().items())
        data = [data] if type_ == list else data
        if type_ == dict:
            tree = DictConfigWidget(name, cfg, data, None)
        else:
            tree = ListConfigWidget(name, cfg, data, None)
        self.config_widgets[name] = tree
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.addWidget(tree)
        self.stack.addWidget(frame)
        self.menu_layout.addWidget(
            QPushButton(name, clicked=lambda: self.stack.setCurrentWidget(frame))
        )

    def apply_changes(self):
        data = dict()
        for _, widget in self.config_widgets.items():
            data[widget.field] = widget.value()
        pprint(data)
        self.close()

    def load_config(self, config_data):
        self.config_data = config_data
        for config, data in self.config_data.items():
            if self.config_widgets.get(config): 
                self.config_widgets[config].set_value(data)

    def closeEvent(self, event):
        self.on_close.emit()
        super().closeEvent(event)


if __name__ == "__main__":
    import sys

    config_data = {
        "Addons": [
            {
                "__id__": 3,
                "__type__": "GAddonTest",
                "name": "TestAddon",
                "test_a": 1,
                "test_b": 2,
            }
        ],
        "Plugins": [
            {
                "__id__": 2,
                "__type__": "GPluginTest",
                "location": "D:/PROJECTS/Gwaddon/gwaddon",
                "name": "MainPlugin",
                "addons": [4],
            }
        ],
        "Projects": [
            {
                "__id__": 1,
                "__type__": "GProject",
                "name": "TestProject",
                "key": "jkhfdskjfds",
                "plugin": 3,
                "dev_plugin": 3,
            }
        ],
        "Studio": {
            "__id__": 0,
            "__type__": "GStudio",
            "key": "fgdsgfds",
            "name": "Mondo",
            "projects": [2],
        },
        "Users": [
            {
                "__id__": 10,
                "__type__": "GUser",
                "name": "e.aguado",
                "password": "1234",
                "email": "e.aguado",
                "studio": 0,
                "projects": [2],
            }
        ],
        "Roles": [
            {
                "__id__": 11,
                "__type__": "GRole",
                "name": "admin",
                "permissions": {"all": True},
            }
        ],
    }

    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = ConfigPage()
    window.show()
    app.exec()
