import importlib
import inspect
from os import fspath
from pathlib import Path
from logging import getLogger, basicConfig, DEBUG
import traceback

from addon.base_addon import Addon

logger = getLogger(__name__)
basicConfig(level=DEBUG)


def import_module_from_path(file_path: Path) -> callable:
    """import module by file path"""
    spec = importlib.util.spec_from_file_location(file_path.name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


class AddonManager:
    def __init__(self) -> None:
        logger.debug("Starting AddonManager")
        self._addons = {}

    @property
    def addons(self):
        return self._addons

    def collet(self, plugin_config: dict[str, any]) -> list[str]:
        """collet all addons from dir"""
        logger.debug("collet addons")
        addon_dir = Path(plugin_config.get("location"),"addons")
        if not Path(addon_dir).exists():
            return
        logger.debug(f"find in dir: {addon_dir}")
        for addon_path in Path(addon_dir).glob("*.py"):
            logger.debug(f"addon file detected: {addon_path}")
            if addon_path.is_dir():
                continue
            self.register(addon_path)

        return self._addons.keys()

    def register(self, addon_path: Path) -> None:
        """Register a new addon class."""
        logger.debug("register addon")
        try:
            module = import_module_from_path(addon_path)
            addon_classes = inspect.getmembers(
                module,
                lambda member: inspect.isclass(member)
                and issubclass(member, Addon)
                and member is not Addon,
            )
            for name, addon_class in addon_classes:
                self._addons[name] = {"class":addon_class,"instances":[]}
                logger.debug(f"addon {name!r} registered")
        except Exception as e:
            traceback.print_exc()
            logger.error(f"Error importing module {addon_path.name!r}: {e}")

    def unregister(self, addon_name: str) -> None:
        """Unregister a addon class."""
        logger.debug("unregister addon")
        self._addons.pop(addon_name, None)
        logger.debug(f"addon {addon_name!r} unregister")

    def load_addon(self, addon_name: str, arguments: dict[str, any]) -> Addon:
        """Create a addon of a specific name, given JSON data."""
        args_copy = arguments.copy()
        try:
            addon_class = self._addons[addon_name]
        except KeyError:
            raise ValueError(f"unknown addon {addon_name!r}") from None
        try:
            class_ = addon_class(**args_copy)
            self._addons[addon_name]["instances"].append(class_)
        except Exception as error:
            traceback.print_exc()
            raise ValueError(f"Failed loading addon{addon_name!r}: {error}")

        return class_
    
    def load_addons(self,):
        for addon in self._addons.keys():
            self.load_addon(addon["class"])


    def unload_addon(self) -> None:
        """Unload plugin."""
        if self.plugin:
            logger.debug(f"Unloading current plugin: {self.plugin}")
            self.plugin = None

    def unload_addons():
        ...
