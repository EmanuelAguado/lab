from ayon_server.addons import BaseServerAddon
from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField
)

# Default settings values
DEFAULT_MODEL_SETTINGS = {
    "ValidateMeshTriangulated": {
        "enabled": True,
        "optional": True,
        "active": True,
    },
}


class BasicValidateModel(BaseSettingsModel):
    enabled: bool = SettingsField(title="Enabled")
    optional: bool = SettingsField(title="Optional")
    active: bool = SettingsField(title="Active")


class ModelSettings(BaseSettingsModel):
    ValidateMeshTriangulated: BasicValidateModel = SettingsField(
        default_factory=BasicValidateModel,
        title="Validate whether the mesh contains triangles",
        section="Publish"
    )
    
