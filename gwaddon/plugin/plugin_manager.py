import importlib
import inspect
from os import fspath
from pathlib import Path
from logging import getLogger, basicConfig, DEBUG
import traceback

from plugin.components import GPlugin

logger = getLogger(__name__)
basicConfig(level=DEBUG)


def import_module_from_path(file_path: Path) -> callable:
    """import module by file path"""
    spec = importlib.util.spec_from_file_location(file_path.name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class PluginManager:
    def __init__(self) -> None:
        logger.debug("Starting PluginManager")
        self._plugins = {}
        self.plugin = None

    @property
    def plugins(self):
        return self._plugins

    def collet(self, plugin_config: dict[str, any]) -> list[str]:
        """collet all plugins from dir"""
        logger.debug("collet plugins")
        plugin_dir = plugin_config.get("location")
        name = plugin_config.get("type")
        if not Path(plugin_dir).exists():
            raise Exception(f"Unknown location {name!r} dir: {plugin_dir}")
        logger.debug(f"find in dir: {plugin_dir}")
        for plugin_path in Path(plugin_dir).glob("plugins/*.py"):
            logger.debug(f"plugin file detected: {plugin_path}")
            if plugin_path.is_dir():
                continue
            self.register(plugin_path, plugin_config)

        return self._plugins.keys()

    def register(self, plugin_path: Path, plugin_config: dict[str, any]) -> None:
        """Register a new plugin class."""
        logger.debug("register plugin")
        try:
            module = import_module_from_path(plugin_path)
            plugin_classes = inspect.getmembers(
                module,
                lambda member: inspect.isclass(member)
                and issubclass(member, GPlugin)
                and member is not GPlugin,
            )
            for name, plugin_class in plugin_classes:
                self._plugins[name] = {"class": plugin_class, "config": plugin_config}
                logger.debug(f"Plugin {name!r} registered")
        except ImportError as e:
            logger.error(f"Error importing module {plugin_path.name!r}: {e}")

    def unregister(self, plugin_name: str) -> None:
        """Unregister a plugin class."""
        logger.debug("unregister plugin")
        self._plugins.pop(plugin_name, None)
        logger.debug(f"Plugin {plugin_name!r} unregister")

    def unload_plugin(self) -> None:
        """Unload plugin."""
        if self.plugin:
            logger.debug(f"Unloading current plugin: {self.plugin}")
            self.plugin = None

    def load_plugin(self, plugin_name: str) -> GPlugin:
        """Load plugin."""
        if isinstance(self.plugin, self._plugins.get(plugin_name).get("class")):
            logger.debug(f"Plugin {plugin_name!r} already loaded")
            return self.plugin
        self.unload_plugin()
        try:
            plugin_class = self._plugins[plugin_name]["class"]
            config = self._plugins[plugin_name]["config"].copy()
        except KeyError:
            raise ValueError(f"unknown plugin {plugin_name!r}") from None
        try:
            logger.debug(f"loading plugin {plugin_name!r}")
            plugin_instance = plugin_class(config)
            self.plugin = plugin_instance
            logger.debug(f"Plugin {plugin_name!r} loaded and initialized")
            return plugin_instance
        except Exception as error:
            traceback.print_exc()
            raise ValueError(f"Failed loading plugin {plugin_name!r}: {error}")


if __name__ == "__main__":
    import sys

    sys.path.append(r"c:\Users\emaag\Documents\scripts\laboratorio\gwaddon")
    import plugins.test_plugin
    from plugin.base_plugin import GPlugin

    p = PluginManager()
    p.load_plugins()
