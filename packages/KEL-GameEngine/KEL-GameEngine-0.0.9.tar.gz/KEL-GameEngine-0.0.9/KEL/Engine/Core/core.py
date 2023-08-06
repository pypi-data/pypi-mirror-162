from KEL.Engine.Setup import *
from KEL.Engine.Models.emptyModel import * 
from KEL.Engine.Core.event import *


class GameCore:
    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def __init__(self, frameLimit):
        self.clock = pygame.time.Clock()
        self.frameLimit = frameLimit
        self.framerate = 0

        self.coreModules = {'EventHandling': Events()}
        self.objects = {}
        self.currentObj = None # The current object in the update loop (yourself when ur component) 


        self.givenModules = {} # When an component calles getComponent() they get added to this list (the component). # In every frame we update the components component (from getComponent). 
        # The component is the declarer. Exe. self.giveModules = {Object: Component}

        self.inputStateDefault = 'Up'

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def startEngine(self):
        for component in self.objects:
            self.currentObj = self.objects[component]
            self.objects[component].start()


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def updateEngine(self):
        wn.fill("#ffffff")
        self.framerate = self.clock.get_fps()
        
        self.__updateGivenModules()

        
        for module in self.coreModules:
            self.coreModules[module].update()
        
        # Updating objects, thats really just updating the blueprint that then updates the components of the object
        for object in self.objects:
            # We need to get value of it so we need to pass it thru the dic
            self.currentObj = self.objects[object]
            self.objects[object].update()


        self.clock.tick(self.frameLimit)
        pygame.display.update()

    def __updateGivenModules(self) -> None:
        for callingComp in self.givenModules:
            # This component is the component that the component wanted to have acces to
            accessedComp = self.givenModules[callingComp]
            # We find the right attribute by loopoing thru them using the dir command. We filter out the python attriubutes by checking if it starts with __
            for attributeName in dir(callingComp):
                if attributeName[0] != '_' and attributeName[1] != '_':
                    if attributeName == 'renderComp':
                        attribute = getattr(callingComp, attributeName)
                        attribute = accesedComp
                        

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def addObject(self, objectName="emptyModel", objectModel=EmptyModel(), objectLocation='objects', objectColor="#000000", components=[]) -> None:
        # First get the location by getting the of my self
        location = getattr(self, objectLocation)

        # Then adding it to the attribute
        location[objectName] = objectModel 

        # Then adding the components we might want to add when we create the object
        self.objects[objectName].addComponent(components)

        # Adding the objectColor
        self.objects[objectName].objectColor = objectColor

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def getComponent(self, attribute=''):
        # If nothing is specified return the object u r using
        if attribute == '':
            return self.currentObj
        
        
        # If it doesnt have the attribute just return the AttributeError 
        try:
            returnValue = self.currentObj.components[attribute]

            # self.givenModules[componentThatIsCallingThisFunction] = theComponentThatTheComponentWantsAccesTo 
            self.givenModules[self.currentObj.currentComp] = returnValue

            return returnValue  

        except AttributeError as err:
            raise err

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def rawGetComponent(self, object:str, attribute:str=''):
        # So were basicly doing getAttribute function but we specify the object and do not use the currentObj
        if attribute == '':
            return self.objects[object]


        try:
            return object.components[attribute]

        except AttributeError as err:
            return err

    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def Input(self, inputKey, state='Down') -> bool:
        for event in self.coreModules['EventHandling'].events: # Loop thru events list
            if state == "Up":
                if event.type == pygame.KEYUP:
                    if event.key == getattr(pygame, inputKey):
                        return True
                
            elif state == "Down":
                if event.type == pygame.KEYDOWN:
                    if event.key == getattr(pygame, inputKey):
                        return True

        return False


    #-----------------------------------------------------------------------FUNC--------------------------------------------------------------
    def rawInput(self, pygameAttr, eEquals):
        for event in self.coreModules['EventHandling'].events: # Loop thru events list
            attr = getattr(event, pygameAttr)
            equals = getattr(pygame, eEquals)

            if attr == equals:
                return True

        return False


KELEngine = GameCore(frameLimit=60)
