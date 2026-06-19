from typing import Type

from ayon_server.addons import BaseServerAddon

from .settings.main import LabStudiosSettings, DEFAULT_LABSTUDIO_SETTINGS


class MyAddonSettings(BaseServerAddon):
    settings_model: Type[LabStudiosSettings] = LabStudiosSettings

    async def get_default_settings(self):
        settings_model_cls = self.get_settings_model()
        return settings_model_cls(**DEFAULT_LABSTUDIO_SETTINGS)
