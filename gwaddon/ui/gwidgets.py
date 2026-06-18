from dataclasses import asdict
import os.path

from PySide6.QtWidgets import (
    QToolButton,
    QMenu,
    QToolBar,
    QDockWidget,
    QMainWindow,
    QPushButton,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QCheckBox,
    QGraphicsDropShadowEffect,
    QCompleter,
)
from PySide6.QtGui import QIcon, QColor, QPalette, QCloseEvent
from PySide6.QtCore import Qt, QSettings, QAbstractAnimation, QVariantAnimation, QStringListModel

settings_folder = "C:/Users/emaag/Documents/scripts/laboratorio"  # TODO


class GToolBar(QToolBar):
    def __init__(self, title: str, *argss, **kwargs):
        super().__init__(*argss, **kwargs)
        self.setObjectName(title)

    def add_button(self, content: str, tooltip: str, connection: any):
        button = QToolButton()
        if os.path.exists(content) and os.path.isfile(content):
            button.setIcon(QIcon(content))
        else:
            button.setText(content)
        button.setToolTip(tooltip)
        self.addWidget(button)
        button.clicked.connect(connection)
        return button


class GDockWidget(QDockWidget):
    def __init__(self, title: str, *args, **kwargs):
        super().__init__(title, *args, **kwargs)
        self.setObjectName(title)
        self.setFloating(False)
        self.toggle_view_action = self.toggleViewAction()
        self.toggle_view_action.setText(title)
        self.visibilityChanged.connect(self.status)

    def status(self, value):
        self.setUpdatesEnabled(value)


class GMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setObjectName(self.title())
        self.add_shadow()

    def add_shadow(self):
        e = QGraphicsDropShadowEffect(
            offset=0,
            blurRadius=50,
            color=QColor(0, 0, 0, 160),
        )
        self.setGraphicsEffect(e)


class GPage(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.setObjectName(self.title())


class GApp(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__default_toolbars: list[GToolBar] = list()
        self.__default_docks: list[GDockWidget] = list()
        self.__default_menu: list[GMenu] = list()
        self.toolbars: list[GToolBar] = list()
        self.docks: list[GDockWidget] = list()
        self.menu: list[GMenu] = list()

        self.menu_bar = self.menuBar()
        self.menu_bar.setNativeMenuBar(False)
        self.status_bar = self.statusBar()

    def add_default_toolbar(self, toolbar: GToolBar, name: str, position=None):
        tb = toolbar(name)
        self.__default_toolbars.append(tb)
        if position == "right":
            self.addToolBar(Qt.ToolBarArea.RightToolBarArea, tb)
        else:
            self.addToolBar(tb)

    def add_default_dock(
        self, dock, position=Qt.LeftDockWidgetArea, visible: bool = True
    ):
        self.__default_docks.append(dock)
        self.addDockWidget(position, dock)
        self.menu_view.addAction(dock.toggle_view_action)
        dock.setHidden(not visible)

    def add_default_menu(self, *args, **kwargs):
        menu = self.menu_bar.addMenu(*args, **kwargs)
        menu.setObjectName(menu.title())
        self.__default_menu.append(menu)
        return menu

    def add_toolbar(self, toolbar: GToolBar, position=None):
        self.toolbars.append(toolbar)
        if position == "right":
            self.addToolBar(Qt.ToolBarArea.RightToolBarArea, toolbar)
        else:
            self.addToolBar(toolbar)

    def add_dock(self, dock, position=Qt.LeftDockWidgetArea, visible: bool = True):
        self.docks.append(dock)
        self.addDockWidget(position, dock)
        self.menu_view.addAction(dock.toggle_view_action)
        dock.setHidden(not visible)

    def add_menu(self, menu):
        self.menu.append(menu)
        self.menu_bar.addMenu(menu)

    def remove_toolbar(self, toolbar: GToolBar):
        self.removeToolBar(toolbar)
        self.toolbars.remove(toolbar)

    def remove_dock(self, dock: GDockWidget):
        self.removeDockWidget(dock)
        self.docks.remove(dock)

    def remove_menu(self, menu: GMenu):
        self.menu_bar.removeAction(menu.menuAction())
        self.menu.remove(menu)

    def remove_toolbars(self):
        for tb in list(self.toolbars):
            self.remove_toolbar(tb)

    def remove_docks(self):
        for dk in list(self.docks):
            self.remove_dock(dk)

    def remove_menus(self):
        for mn in list(self.menu):
            self.remove_menu(mn)

    def return_toolbars(self):
        return self.findChildren(GToolBar)

    def return_docks(self):
        return self.findChildren(GDockWidget)

    def return_menus(self):
        return self.findChildren(GMenu)

    def restore_layout(self):
        settings = QSettings(f"{settings_folder}/ui.ini", QSettings.IniFormat)
        geometry = settings.value("geometry")
        state = settings.value("windowState")
        if geometry is not None:
            self.restoreGeometry(geometry)
        if state is not None:
            self.restoreState(state)

    def save_layout(self):
        settings = QSettings(f"{settings_folder}/ui.ini", QSettings.IniFormat)
        settings.setValue("geometry", self.saveGeometry())
        settings.setValue("windowState", self.saveState())
        
    def closeEvent(self, event: QCloseEvent) -> None:
        self.save_layout()
        return super().closeEvent(event)


class GConfig(GDockWidget):
    def __init__(self, title: str, *args, **kwargs):
        super().__init__(title, *args, **kwargs)

        self.instancia_clase = instancia_clase
        self.widgets = {}
        self.create_config()

    def create_config(self):
        layout = QFormLayout()
        for prop, value in asdict(self.instancia_clase).items():
            label = QLabel(f"{prop.capitalize()}:")

            if isinstance(value, int):
                widget = QSpinBox()
                widget.setValue(value)
            elif isinstance(value, bool):
                widget = QCheckBox()
                widget.setChecked(value)
            else:
                widget = QLineEdit(value)

            self.widgets[prop] = widget
            layout.addWidget(label)
            layout.addWidget(widget)

        # Botón para aplicar los cambios
        btn_aplicar = QPushButton("Aplicar")
        btn_aplicar.clicked.connect(self.aplicar_cambios)
        layout.addWidget(btn_aplicar)

        self.setLayout(layout)
        self.setWindowTitle('Configuración de MiClase')

    def aplicar_cambios(self):
        for prop, widget in self.widgets.items():
            if isinstance(widget, QLineEdit):
                setattr(self.instancia_clase, prop, widget.text())
            elif isinstance(widget, QSpinBox):
                setattr(self.instancia_clase, prop, widget.value())
            elif isinstance(widget, QCheckBox):
                setattr(self.instancia_clase, prop, widget.isChecked())

        print("Configuración actualizada:", self.instancia_clase)


class GAnimToolButton(QToolButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._animation = None

    def setAnimation(self, time=0, color_a="", color_b=""):
        self._animation = QVariantAnimation(self)
        self._animation.valueChanged.connect(self._animate)
        self._animation.setStartValue(QColor(color_a))
        self._animation.setEndValue(QColor(color_b))
        self._animation.setDuration(time)

    def _animate(self, value):
        style = (
            "*{background-color: " + value.name() + ";border:None}"
            "*::menu-button {background-color: palette(Base)}"
            "*::menu-arrow {image: url(resources/img/arrowRight)} "
            "*::menu-button:hover {background-color: 2px palette(Highlight);border-left:2px solid palette(Base);}"
            "*:checked{background-color:palette(Highlight)}"
            "*::menu-arrow:open {image: url(resources/img/arrowDown)}"
        )
        self.setStyleSheet(style)

    def enterEvent(self, event):
        if self._animation:
            self._animation.setDirection(QAbstractAnimation.Forward)
            self._animation.start()
            super().enterEvent(event)

    def leaveEvent(self, event):
        if self._animation:
            self._animation.setDirection(QAbstractAnimation.Backward)
            self._animation.start()
            super().enterEvent(event)


class GAnimPushButton(QPushButton):
    def __init__(
        self, title="", time=None, color_a=None, color_b=None, radius=0, parent=None
    ):
        super().__init__(parent)
        self._animation = None
        self._radius = radius
        self.setText(title)
        if not time and not color_a and not color_b:
            self.setAnimation(
                250,
                QPalette().color(QPalette.Mid).name(),
                QPalette().color(QPalette.Light).name(),
            )
        else:
            self.setAnimation(time, color_a, color_b)

    def setAnimation(self, time=0, color_a="", color_b=""):
        self._animation = QVariantAnimation(self)
        self._animation.valueChanged.connect(self._animate)
        self._animation.setStartValue(QColor(color_a))
        self._animation.setEndValue(QColor(color_b))
        self._animation.setDuration(time)

    def _animate(self, value):
        style = "*{{background-color: {value};border:None;padding:10px;border-radius:{radius}}}".format(
            value=value.name(), radius=self._radius
        )
        self.setStyleSheet(style)

    def enterEvent(self, event):
        if self._animation:
            self._animation.setDirection(QAbstractAnimation.Forward)
            self._animation.start()
            super().enterEvent(event)

    def leaveEvent(self, event):
        if self._animation:
            self._animation.setDirection(QAbstractAnimation.Backward)
            self._animation.start()
            super().leaveEvent(event)


class GLineEditCompleter(QLineEdit):
    def __init__(
        self, text=None, placeholder=None, auto_complete_list=list(), parent=None
    ):
        super().__init__(parent)
        self.auto_complete_list = auto_complete_list
        self._completer = QCompleter(self)
        self._model = QStringListModel()
        self._completer.setFilterMode(Qt.MatchContains)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompleter(self._completer)
        self._completer.setModel(self._model)
        self._model.setStringList(set(self.auto_complete_list))

        if text:
            self.setText(text)
        if placeholder:
            self.setPlaceholderText(placeholder)

    def refresh_auto_complete(self, data=None):
        self._model.setStringList(set(data or self.auto_complete_list))

    def mouseReleaseEvent(self, event):
        self._completer.complete()
        return super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if self.text() == "":
            self._completer.complete()