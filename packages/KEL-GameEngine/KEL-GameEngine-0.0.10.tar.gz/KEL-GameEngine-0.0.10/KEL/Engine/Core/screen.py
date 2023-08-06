from KEL.Engine.Setup import *


class Screen:
    def start(self):
        # 160 	× 	120
        self.wW = 160*6
        self.wH = 120*6
        self.wn = pygame.display.set_mode((self.wW, self.wH))


        # Frame Related
        self.clock = pygame.time.Clock()
        self.frameLimit = 60
        self.frameRate = self.clock.get_fps()


        self.color = "#ffffff"


    def updateBefore(self): # Before updating objects
        self.wn.fill(self.bgColor)

        # Clock
        self.clock.tick(self.frameLimit)
        self.frameRate = self.clock.get_fps()


    def updateAfter(self): # After updating objects
        pygame.display.update()
