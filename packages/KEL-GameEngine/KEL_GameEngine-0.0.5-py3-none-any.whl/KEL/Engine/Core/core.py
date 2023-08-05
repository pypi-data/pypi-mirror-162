from KEL.Engine.Core.event import *
from KEL.Engine.Game.pygameSetup import *


class GameCore:
    def __init__(self, frameLimit):
        self.coreModules = {'Events': Events()}
        self.clock = pygame.time.Clock()
        self.frameLimit = frameLimit
        self.objects = {}

    def start(self):
        for component in self.objects:
            self.objects[component].start()


    def updateEngine(self):
        wn.fill(bgColor)
        
        # Updating coreModules
        for module in self.coreModules:
            self.coreModules[module].update()
        
        # Updating objects, thats really just updating the blueprint that then updates the components of the object
        for object in self.objects:
            self.objects[object].update()



        self.clock.tick(self.frameLimit)
        pygame.display.update() 
   



    def addObject(self, objectName, object, components):
        # Add object to dic
        self.objects[objectName] = object

        self.objects[objectName].addComponent(components)




KELCORE = GameCore(frameLimit=30)
