class ActionsManager:
    actions_map = {}

    @classmethod
    def add_handler(cls, method):
        if callable(method):
            cls.actions_map[method.__name__] = method

    @classmethod
    def choices(cls):
        return ((x, x) for x in cls.actions_map.keys())
