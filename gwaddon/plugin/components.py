from dataclasses import asdict, dataclass
from pathlib import Path

import json
from logging import getLogger, basicConfig, DEBUG

logger = getLogger(__name__)
basicConfig(level=DEBUG)


def get_all_annotations(cls):
    annotations = {}
    for base_cls in cls.mro():
        if hasattr(base_cls, "__annotations__"):
            annotations.update(base_cls.__annotations__)
    return annotations


@dataclass
class GConfig:
    __id__: int
    __type__: str
    name: str

    @classmethod
    def default(cls: "GConfig"):
        field_types = get_all_annotations(cls)
        return field_types

    @classmethod
    def serialize(cls: "GConfig", config: dict) -> "GConfig":
        logger.debug(f"Serialize config {cls!r}")
        logger.debug(f"config:\n {json.dumps(config, indent=4)}")
        if not isinstance(config, dict):
            raise ValueError(f"Expected a dictionary, got {type(config).__name__}")

        field_types = get_all_annotations(cls)
        kwargs = {}
        for key, value in config.items():
            if key not in field_types:
                continue
            field_type = field_types[key]
            logger.debug(f"{key}: field {type(value)}\n {json.dumps(value, indent=4)}")
            if isinstance(value, dict):  # and issubclass(field_type, GConfig)
                kwargs[key] = (
                    globals()
                    .get(value.get("type", "GComponent"))
                    .config_class.serialize(value)
                )
            elif (
                isinstance(value, list)
                and len(value) > 0
                and isinstance(value[0], dict)
            ):
                item_type = (
                    field_type.__args__[0] if hasattr(field_type, "__args__") else None
                )
                if isinstance(item_type, type) and issubclass(item_type, GConfig):
                    list_configs = list()
                    for item in value:
                        component_type = item.get("type", "GComponent")
                        logger.debug(f"component type {component_type!r}")
                        component_class = globals().get(component_type)
                        list_configs.append(
                            component_class.config_class.serialize(item)
                        )
                else:
                    kwargs[key] = value
            else:
                kwargs[key] = value
        return cls(**kwargs)

    def deserialize(self) -> dict[str, any]:
        result = {}
        for k, v in self.__dict__.items():
            if isinstance(v, GConfig):
                result[k] = v.deserialize()
            elif isinstance(v, list) and len(v) > 0 and isinstance(v[0], GConfig):
                result[k] = [item.deserialize() for item in v]
            else:
                result[k] = v
        return result


class GComponent:
    config_class: GConfig = GConfig

    def __init__(self, config: dict[str, any]):
        self.config = self.config_class.serialize(config)


@dataclass
class GTask:
    id: int
    name: str
    description: str

    def serialize(self):
        return {"id": self.id, "name": self.name, "description": self.description}

    def serialize(self):
        return asdict(self)

    def __str__(self):
        return f"{self.__class__.__name__}({', '.join(f'{k}: {v}' for k, v in asdict(self).items())})"


@dataclass
class GApplicationConfig(GConfig):
    executable: Path | str


class GApplication(GComponent):
    config_class: GApplicationConfig = GApplicationConfig


@dataclass
class GAddonConfig(GConfig):
    location: str


class GAddon(GComponent):
    config_class: GAddonConfig = GAddonConfig


@dataclass
class GPluginConfig(GConfig):
    location: str
    addons: list[GAddon]
    test: bool


class GPlugin(GComponent):
    config_class: GPluginConfig = GPluginConfig
    task_class: GTask = GTask

    def add_task(self, id, name, description):
        task = self.task_class(id, name, description)
        self.tasks[id] = task
        return task.serialize()

    def modify_task(self, id, name=None, description=None):
        if id in self.tasks:
            if name is not None:
                self.tasks[id].name = name
            if description is not None:
                self.tasks[id].description = description
            return self.tasks[id].serialize()
        else:
            raise ValueError("Task not found")

    def remove_task(self, id):
        if id in self.tasks:
            task = self.tasks.pop(id)
            return task.serialize()
        else:
            raise ValueError("Task not found")

    def return_task(self, id):
        if id in self.tasks:
            return self.tasks[id].serialize()
        else:
            raise ValueError("Task not found")

    def return_all_tasks(self):
        return [task.serialize() for task in self.tasks.values()]

    def serialize(self):
        return {
            "config": self.config.serialize(),
            "tasks": [task.serialize() for task in self.tasks.values()],
        }

    @staticmethod
    def deserialize(data):
        plugin = GPlugin(config=data["config"])
        plugin.tasks = {
            task_data["id"]: GTask.deserialize(task_data) for task_data in data["tasks"]
        }
        return plugin

    def get_plugin_info(self):
        methods = [
            func
            for func in dir(self)
            if callable(getattr(self, func)) and not func.startswith("__")
        ]
        variables = [
            var
            for var in vars(self)
            if not callable(getattr(self, var)) and not var.startswith("__")
        ]
        return {"methods": methods, "variables": variables}


@dataclass
class GProjectConfig(GConfig):
    key: str
    plugin: GPlugin
    dev_plugin: GPlugin


class GProject(GComponent):
    config_class: GProjectConfig = GProjectConfig


@dataclass
class GStudioConfig(GConfig):
    key: str
    projects: list[GProject]


class GStudio(GComponent):
    config_class: GStudioConfig = GStudioConfig


@dataclass
class GUserConfig(GConfig):
    email: str
    password: str
    studio: GStudio
    projects: list[GProject]


class GUser(GComponent):
    config_class: GUserConfig = GUserConfig


@dataclass
class GAddonTestConfig(GAddonConfig):
    test_a: int
    test_b: int


class GAddonTest(GAddon):
    config_class: GAddonTestConfig = GAddonTestConfig


class GPluginTest(GPlugin): ...


if __name__ in "__main__":
    DATA = {
        "plugin": {
            "type": "TestPlugin",
            "location": "D:/PROJECTS/Gwaddon/gwaddon",
            "addons": [{"type": "AddonA", "test_a": 1, "test_b": 2}],
        },
    }
    a = PluginA(DATA.get("plugin"))
    print(a.config.deserialize())
    print(a.config)
