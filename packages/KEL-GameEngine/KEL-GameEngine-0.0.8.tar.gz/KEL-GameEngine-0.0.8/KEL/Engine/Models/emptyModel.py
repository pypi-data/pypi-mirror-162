class EmptyModel:
    def __init__(self):
        self.components = {}

    def addComponent(self, components):
        for component in components:
            self.components[type(component).__name__] = component

    def removeComponent(self, components):
        for component in components:
            del self.components[type(component).__name__ if type(component) != str else component]

    def start(self):
        for component in self.components:
            self.components[component].start(self.components)

    def update(self, objects):
        for component in self.components:
            self.components = self.components[component].update(self.components, objects)
