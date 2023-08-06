from KEL.Engine.Setup import *


class Events:
    def update(self):
        self.events = []

        for event in pygame.event.get():
            self.events.append(event)
