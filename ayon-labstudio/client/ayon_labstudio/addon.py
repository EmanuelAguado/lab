import os
from ayon_core.addon import AYONAddon, IPluginPaths

from .version import __version__

LABSTUDIO_ADDON_ROOT = os.path.dirname(os.path.abspath(__file__))

class AyonLabStudioAddon(AYONAddon, IPluginPaths):
    """
    AYON addon for LabStudio.

    Defines plugin locations and launch hook paths for the LabStudio integration.
    Used to register publish plugins and execution hooks for the pipeline.
    """
    name = "labstudio"
    version = __version__
    host_name = "labstudio"

    def get_plugin_paths(self):
        """Implementation of IPluginPaths to get plugin paths."""
        plugins_dir = os.path.join(LABSTUDIO_ADDON_ROOT, "plugins")

        return {
            "publish": [os.path.join(plugins_dir, "publish")]
        }
    
    def get_launch_hook_paths(self, app):
        return [
            os.path.join(LABSTUDIO_ADDON_ROOT, "hooks")
        ]
    

# "\\\\lab\\generic\\resources\\maya\\scripts",
# "\\\\TANTRUM\\generic\\resources\\maya\\scripts"