from dataclasses import asdict, dataclass
from pathlib import Path

from plugin.components import GComponent, GConfig





if __name__ in "__main__":
    # task = Task(id=1, name="Example Task", description="This is an example task.")
    # print(task)
    {
        "users": [
            {
                "id": 1,
                "username": "e.aguado",
                "password": "1234",
                "email": "e.aguado",
                "studio": 0,
                "projects": [
                    2
                ]
            }
        ],
        "studio": {
            "key": "dhfkjsahoi",
            "projects": [
                {
                    "id": 2,
                    "name": "TestProject",
                    "key": "jkhfdskjfds",
                    "plugin": {
                        "location": "D:/PROJECTS/Gwaddon/gwaddon",
                        "type": "TestPlugin",
                        "addons": [
                            {
                                "type": "AddonA",
                                "test_a": 1,
                                "test_b": 2
                            }
                        ]
                    },
                    "dev_plugin": {
                        "location": "D:/PROJECTS/Gwaddon/dev_gwaddon",
                        "type": "DevTestPlugin",
                        "addons": [
                            {
                                "type": "AddonA",
                                "test_a": 1,
                                "test_b": 2
                            }
                        ]
                    }
                }
            ]   
        }
    }
