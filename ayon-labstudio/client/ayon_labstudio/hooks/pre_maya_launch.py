import os

from ayon_applications import (
    PreLaunchHook,
    LaunchTypes,
)

LABSTUDIO_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

def add_path_to_env(env, key, path):
    existing = env.get(key)
    if existing:
        env[key] = os.pathsep.join([existing, path])
    else:
        env[key] = path

class PreLaunchHostHook(PreLaunchHook):
    """
    Pre-launch hook that modifies the environment for Maya before launch.

    It ensures custom Maya hooks are added to PYTHONPATH when launching locally.
    """
    app_groups = {"maya"}
    launch_types = {LaunchTypes.local}

    def execute(self):
        add_path_to_env(env=self.launch_context.env,
                        key="PYTHONPATH",
                        path="CUSTOM_MAYA_HOOKS")