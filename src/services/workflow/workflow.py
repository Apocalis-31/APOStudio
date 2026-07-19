class Workflow:

    def __init__(self):

        self.enabled = []

    def is_enabled(self, module: str):

        return module in self.enabled