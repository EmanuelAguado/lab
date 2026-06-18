from functools import partial
import sys
from logging import getLogger, basicConfig, DEBUG
from threading import Thread
import time
import traceback

from PySide6.QtWidgets import QApplication

from addon.addon_manager import AddonManager
from plugin.plugin_manager import PluginManager
from ui.styles import gwaddon_dark_palette
from ui.app import Main
from ui.qtclasses.loading import Loading
from db.client import DataBase
from server.server import SocketServer
from api import ui


logger = getLogger(__name__)
basicConfig(level=DEBUG)

DATABASE = r"D:\PROJECTS\Gwaddon\gwaddon\studio.json"
STUDIO_KEY = False

def thread(function: callable) -> None:
    """Decorator that calls the function within a separate thread"""

    def wrapper(*args, **kwargs):
        worker = Thread(target=function, args=args, kwargs=kwargs)
        worker.start()
        return kwargs

    return wrapper


class Application:
    def __init__(self, host, port):
        self.plugin = None
        self.__main_ui = Main()
        self.__splash = Loading()
        self.ui = self.__main_ui.gwaddon_page
        ui.MainWindow(self.ui)
        self.ui_connections()
        self.initialize(host, port)

    # def pre_init(self):
    #     global STUDIO_KEY
    #     if not STUDIO_KEY:
    #         STUDIO_KEY,ok = QInputDialog.getText(self.__main_ui,"SET STUDIO KEY","Studio KEY:")
    #     if not ok:
    #         sys.exit()
    #         return
        
    @thread
    def initialize(self, host, port):
        try:
            logger.debug("Initialize Gwaddon")
            self.__splash.on_show.emit()
            self.__splash.on_set_log.emit("Initialize Gwaddon")
            logger.debug("Initialize SocketServer")
            self.__splash.on_set_log.emit("Starting modules")
            self.api = SocketServer(host, port)
            logger.debug("Initialize PluginManager")
            self.plugin_manager = PluginManager()
            logger.debug("Initialize AddonManager")
            self.addon_manager = AddonManager()
            logger.debug("Initialize DataBase")
            self.__splash.on_set_log.emit("Connecting...")
            time.sleep(1)
            self.db = DataBase()
            self.__splash.on_set_log.emit("Login...")
            self.login("", "", initialize=True)
            self.__splash.on_set_log.emit("Preparing UI...")
            time.sleep(1)
            self.__splash.on_close.emit()
            self.__main_ui.on_show.emit()
        except Exception as error:
            traceback.print_exc()
            self.__splash.on_error.emit(str(error))
            # self.__main_ui.close()

    def ui_connections(self):
        self.__main_ui.login_page.on_login.connect(self.login)
        self.ui.action_logout.triggered.connect(self.logout)
        self.ui.action_studio_config.triggered.connect(self.config)
        self.__main_ui.on_close.connect(self.close)

    def login(self, user, password, initialize=False):
        logger.debug("Login...")
        if self.db.login(user, password):
            logger.debug("Success login")
            self.__main_ui.set_gwaddon_page()
            projects_data = self.db.get_projects()
            logger.debug("Success get projects")
            self.add_projects(projects_data)
            logger.debug("Success add projects")
            self.api.start()
            return True
        else:
            logger.debug("Failed login")
            self.__main_ui.set_login_page()
            if not initialize:
                self.__main_ui.login_page.on_set_log.emit("Failed login...")
            return False

    def logout(self):
        self.db.logout()
        self.plugin_manager.unload_plugin()
        self.api.stop()
        self.__main_ui.set_login_page()

    def config(self):
        self.__main_ui.set_config_page(self.db.data)

    def add_projects(self, projects_data: dict[str, any]):
        for project_id, config in projects_data.items():
            try:
                plugin_info = self.db.get_plugin_info(config.get("plugin"))
                self.plugin_manager.collet(plugin_info)
                self.ui.on_add_project.emit(
                    config.get("name"),
                    partial(
                        self.set_project,
                        config,
                    ),
                )
            except Exception as error:
                traceback.print_exc()
                self.__main_ui.on_error.emit(str(error))
            try:
                dev_plugin_info = self.db.get_plugin_info(config.get("dev_plugin"))
                self.plugin_manager.collet(dev_plugin_info)
                # self.ui.on_add_dev_project.emit(
                #     config.get("name"),
                #     partial(
                #         self.set_project,
                #         config.get("name"),
                #         config.get("plugin").get("type"),
                #     ),
                # )
            except Exception as error:
                traceback.print_exc()
                self.__main_ui.on_error.emit(str(error))


    def close(self):
        logger.debug("Clear UI")
        self.plugin_manager.unload_plugin()
        self.api.stop()

    def set_plugin(self, plugin_name: str):
        try:
            plugin = self.plugin_manager.load_plugin(plugin_name)
            self.api.set_plugin(plugin)
            return plugin
        except:
            traceback.print_exc()
            msg = (
                "Error loading the project plugin. "
                "Please contact technical support:,\n\n "
                f"{traceback.format_exc()}"
            )
            self.__main_ui.on_error.emit(msg)

    def set_project(self, config: dict[str,any]):
        logger.debug("Setting project")
        name = config.get("name")
        self.__main_ui.set_title(name)
        self.ui.remove_docks()
        self.ui.remove_menus()
        self.ui.remove_toolbars()
        self.addon_manager.collet(self.db.get_plugin_info(config.get("plugin")))
        # self.set_plugin(name)


# Ejemplo de uso
if __name__ == "__main__":
    sys.argv += ["-platform", "windows:darkmode=2"]
    app = QApplication(sys.argv)
    app.setPalette(gwaddon_dark_palette())
    gwaddon = Application("localhost", 9999)
    app.exec()
