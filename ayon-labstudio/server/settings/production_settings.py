from ayon_server.settings import (
    BaseSettingsModel,
    SettingsField
)
from ayon_server.enum import EnumItem, EnumRegistry

# Default settings values
DEFAULT_PRODUCTION_SETTINGS = {
    "StartStatusChange": {
        "enabled": True,
        "app_start_status_shortname": "wip",
        "app_startstatus_change_conditions": [],
    },
}

async def status_types_enum(project_name: str | None = None) -> list[EnumItem]:
        result = await EnumRegistry.resolve("statuses.short_name", project_name=project_name)
        result_shortnames = [
            {
                "value": item.short_name,
                "label": item.short_name,
            }
            for item in result
        ]
        return result_shortnames


class AppStartStatusChangeCondition(BaseSettingsModel):
    def _status_change_cond_enum():
        return [
            {"value": "equal", "label": "Equal"},
            {"value": "not_equal", "label": "Not equal"},
        ]
    
    
    condition: str = SettingsField(
        "equal", enum_resolver=_status_change_cond_enum, title="Condition"
    )
    short_name: list[str] = SettingsField(default_factory=list,enum_resolver=status_types_enum, title="Short name")

class AppStartStatusChange(BaseSettingsModel):
    enabled: bool = SettingsField(title="Enabled")
    app_start_status_shortname: str = SettingsField(title="App start Status shortname",enum_resolver=status_types_enum)
    app_startstatus_change_conditions: list[AppStartStatusChangeCondition] = SettingsField(
        default_factory=AppStartStatusChangeCondition, title="App start status change conditions"
    )

class ProductionSettings(BaseSettingsModel):
    StartStatusChange: AppStartStatusChange = SettingsField(
        default_factory=AppStartStatusChange,
        title="App start status change settings",
        section="Production"
    )

