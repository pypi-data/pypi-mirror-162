class EmptyModel:
    def __init__(self):
        self.components = {}

        # This is the currentComponent that is being updated. This is used in the core function getComponent and update given modules
        self.currentComp = None


    def addComponent(self, components):
        for component in components:
            self.components[type(component).__name__] = component

    def removeComponent(self, components):
        for component in components:
            del self.components[type(component).__name__ if type(component) != str else component]

    def start(self):
        for component in self.components:
            self.currentComp = self.components[component]
            self.components[component].start()

    def update(self):
        for component in self.components:
            self.currentComp = self.components[component]
            self.components[component].update()
