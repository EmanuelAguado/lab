from logging import getLogger
from functools import wraps
import traceback

from db.db_supabase import get_studio_data, login

logger = getLogger(__name__)


def login_required(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.logged_in_user is None:
            logger.debug("No user is currently logged in.")
            raise Exception("No user is currently logged in.")
        return func(self, *args, **kwargs)

    return wrapper


class DataBase:
    def __init__(self):
        self.data = None
        self.user_info = None
        self.logged_in_user = None

    def load_data(self, studio_key):
        self.data = get_studio_data(studio_key)

    def login(self, username, password):
        try:
            self.user_info = login(username, password)
            print(self.user_info)
            logger.debug(f"User {username} logged in successfully.")
            self.load_data(self.user_info["token"])
            self.logged_in_user = self.user_info.get("id")
            return True
        except Exception as error:
            traceback.print_exc()
            logger.error("Invalid username or password.")


    @login_required
    def logout(self):
        self.logged_in_user = None
        self.user_info = None
        return "User logged out successfully."

    @login_required
    def get_component_info(self, component: str, component_id: int):
        return next(
            (
                data
                for data in self.data[component]
                if data.get("__id__", None) == component_id
            ),
            {},
        )

    @login_required
    def get_user_info(self):
        return self.user_info

    @login_required
    def get_project_info(self, project_id):
        print(self.data["Projects"], project_id)
        return self.get_component_info("Projects", project_id)

    @login_required
    def get_plugin_info(self, plugin_id):
        return self.get_component_info("Plugins", plugin_id)

    @login_required
    def get_addon_info(self, addon_id):
        return self.get_component_info("Addons", addon_id)

    @login_required
    def get_projects(self):
        projects = self.user_info.get("projects", [])
        return {
            project_id: self.get_project_info(int(project_id))
            for project_id in projects
        }

    @login_required
    def get_studio(self):
        user_info = self.get_user_info()
        studio_id = user_info.get("studio")
        return self.data["Studio"] if self.data["Studio"]["__id__"] == studio_id else {}

    @login_required
    def get_addons(self, project_id):
        project = self.get_project_info(project_id)
        if project:
            plugin_info = self.get_plugin_info(project.get("plugin"))
            plugin_dev_info = self.get_plugin_info(project.get("dev_plugin"))
            list_addons = list()
            for addon_id in plugin_info.get("addons") + plugin_dev_info.get("addons"):
                list_addons.append(self.get_addon_info(addon_id))
            return list_addons
        return []
