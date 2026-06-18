class Addon:
    def __init__(self, config=None):
        self.config = config if config is not None else {}
                
        for key, value in self.config.items():
            setattr(self, key, value)
    
    def serialize(self):
        return {
            'config': self.config,
            'tasks': [task.serialize() for task in self.tasks.values()]
        }
    
    @staticmethod
    def deserialize(data):
        plugin = Addon(config=data['config'])
        return plugin
    
    def get_addon_info(self):
        methods = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]
        variables = [var for var in vars(self) if not callable(getattr(self, var)) and not var.startswith("__")]
        return {'methods': methods, 'variables': variables}



