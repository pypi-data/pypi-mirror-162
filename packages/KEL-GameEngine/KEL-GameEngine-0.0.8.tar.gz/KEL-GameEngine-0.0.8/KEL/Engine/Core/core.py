from KEL.Engine.Core.event import *
from KEL.Engine.Game.pygameSetup import *
from KEL.Engine.Models.emptyModel import EmptyModel


class GameCore:
    def __init__(self, frameLimit):
        self.coreModules = {'Events': Events()}
        self.clock = pygame.time.Clock()
        self.frameLimit = frameLimit
        self.objects = {}

    def startEngine(self):
        for component in self.objects:
            self.objects[component].start()


    def updateEngine(self):
        wn.fill(bgColor)
        
        # Updating coreModules
        for module in self.coreModules:
            self.coreModules[module].update(self.objects)
        
        # Updating objects, thats really just updating the blueprint that then updates the components of the object
        for object in self.objects:
            # Passing all the objects except yourself
            objParameter = self.objects.copy()
            objParameter.pop(object)

            self.objects[object].update(objParameter)



        self.clock.tick(self.frameLimit)
        pygame.display.update() 
   


    def addObject(self, objectName="emptyModel", objectInstance=EmptyModel(), objectLocation='objects', components=[]) -> None:
        # First get the location by getting the of my self
        location = getattr(self, objectLocation)

        # Then adding it to the attribute
        location[objectName] = objectInstance

        # Then adding the components we might want to add when we create the object
        self.objects[objectName].addComponent(components)
    




# Declaring it here so other can use it when importing this
KELCORE = GameCore(frameLimit=30)
