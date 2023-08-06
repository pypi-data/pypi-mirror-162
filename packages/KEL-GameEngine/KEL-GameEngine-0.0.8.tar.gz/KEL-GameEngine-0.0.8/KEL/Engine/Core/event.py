from KEL.Engine.Game.pygameSetup import *

class Events:
    def __init__(self):
        self.events = []

    def update(self, objects):
        self.events = []
        for event in pygame.event.get():
            self.events.append(event)
