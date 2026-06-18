from logging import getLogger, basicConfig, DEBUG

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QSplitter,
)
from PySide6.QtCore import Qt, Signal

from ui.gwidgets import GToolBar, GDockWidget, GMenu, GApp
from ui.qtclasses.explorer import Explorer

logger = getLogger(__name__)
basicConfig(level=DEBUG)


class WorkPage(GApp):
    on_add_project = Signal(str,object)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create_widgets()
        self.create_connections()
        self.restore_layout()

    def create_widgets(self):
        self.menu_file = self.add_default_menu("&File")
        self.menu_view = self.add_default_menu("&View")
        self.menu_projects = self.add_default_menu("&Projects")
        self.menu_apps = self.add_default_menu("&Apps")
        self.menu_config = self.add_default_menu("&Config")
        self.menu_user = self.add_default_menu("&User")
        self.menu_about = self.add_default_menu("&About")
        self.action_logout = self.menu_user.addAction("Logout")
        self.action_studio_config = self.menu_config.addAction("Studio config")

        self.menu_view.addAction(
            "Print toolbar", lambda: print(self.findChildren(GToolBar))
        )
        self.menu_view.addAction(
            "Print dock", lambda: print(self.findChildren(GDockWidget))
        )
        self.menu_view.addAction("Print menu", lambda: print(self.findChildren(GMenu)))
        self.menu_view.addAction("Remove toolbars", self.remove_toolbars)
        self.menu_view.addAction("Remove docks", self.remove_docks)
        self.menu_view.addAction("Remove menus", self.remove_menus)
        self.menu_styles = self.menu_view.addMenu("Styles")
        self.menu_styles_gwaddon = self.menu_styles.addAction("gwaddon style")

        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_splitter = QSplitter()
        self.explorer = Explorer()

        self.main_splitter.setOrientation(Qt.Horizontal)
        # self.main_splitter.addWidget(self.task_view_holder)
        self.main_splitter.addWidget(QWidget())
        self.main_splitter.addWidget(self.explorer)
        self.main_splitter.setMinimumHeight(50)
        self.main_splitter.setSizes([500, 200])
        # self.main_layout.addWidget(self.notify_widdget)
        self.main_layout.addWidget(self.main_splitter)
        self.main_layout.setContentsMargins(0,0,0,0)
        self.main_layout.setSpacing(0)

        self.setCentralWidget(self.main_widget)

    def create_connections(self):
        self.on_add_project.connect(self.add_project)

    def add_project(self, project_name: str, callable: callable) -> None:
        action = self.menu_projects.addAction(project_name)
        action.triggered.connect(callable)