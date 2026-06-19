from ayon_server.addons import BaseServerAddon
from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField
)
from .model_settings import ModelSettings, DEFAULT_MODEL_SETTINGS
from .production_settings import ProductionSettings, DEFAULT_PRODUCTION_SETTINGS

DEFAULT_LABSTUDIO_SETTINGS = {
  "enabled": True,
  "PRODUCTION": DEFAULT_PRODUCTION_SETTINGS,
  "MODEL": DEFAULT_MODEL_SETTINGS
}

# Main Settings
class LabStudiosSettings(BaseSettingsModel):
    """Lab Studios Settings. """
    enabled: bool = SettingsField(True, title="Enabled")
    PRODUCTION: ProductionSettings = SettingsField(
        default_factory=ProductionSettings, title="Production Settings")
    MODEL: ModelSettings = SettingsField(
        default_factory=ModelSettings, title="Model Settings")
