# Define SharedConfig first
class SharedConfig:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SharedConfig, cls).__new__(cls)
            cls._instance.func_dict = {}  # Initialize the func_dict
        return cls._instance

    def update_func_dict(self, new_dict):
        self.func_dict.update(new_dict)

    def get_func_dict(self):
        return self.func_dict