from plugin.base_plugin import GPlugin


class TestPlugin(GPlugin):
    def __init__(self, config=None):
        super().__init__(config)
        self.name = "test plugin"
        print("test plugin")
        ...