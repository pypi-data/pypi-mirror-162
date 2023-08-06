from KEL.Engine.Setup import *


class Events:
    def start(self):
        pass
    

    def updateBefore(self): # Check screen for descrition
        self.events = []

        for event in pygame.event.get():
            self.events.append(event)


    def updateAfter(self): # Check screen for descrition
        pass
