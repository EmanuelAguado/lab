from ui.gwidgets import *
from ui.styles import *


class MainWindow():
    __gwaddon_ui = None
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.instancia_secundaria = cls
        return cls._instance

    def __init__(self, gwaddon = None) -> None:
        if self.__gwaddon_ui == None:
            self.__gwaddon_ui = gwaddon

    def add_toolbar(self,toolbar: GToolBar, position=None):
        return self.__gwaddon_ui.add_toolbar(toolbar,position)

    def add_dock(self,dock, position=Qt.LeftDockWidgetArea, visible: bool = True):
        return self.__gwaddon_ui.add_dock(dock, position, visible)

    def add_menu(self,menu):
        return self.__gwaddon_ui.add_menu(menu)

    def remove_toolbar(self,toolbar: GToolBar):
        return self.__gwaddon_ui.remove_toolbar(toolbar)

    def remove_dock(self,dock: GDockWidget):
        return self.__gwaddon_ui.remove_dock(dock)

    def remove_menu(self,menu: GMenu):
        return self.__gwaddon_ui.remove_menu(menu)

    def remove_toolbars(self):
        return self.__gwaddon_ui.remove_toolbars()

    def remove_docks(self):
        return self.__gwaddon_ui.remove_docks()

    def remove_menus(self):
        return self.__gwaddon_ui.remove_menus()

    def return_toolbars(self):
        return self.__gwaddon_ui.return_toolbars()

    def return_docks(self):
        return self.__gwaddon_ui.return_docks()

    def return_menus(self):
        return self.__gwaddon_ui.return_menus()
    
    def explorer(self):
        return self.__gwaddon_ui.explorer()
    
    def tasker(self):
        return self.__gwaddon_ui.tasker()