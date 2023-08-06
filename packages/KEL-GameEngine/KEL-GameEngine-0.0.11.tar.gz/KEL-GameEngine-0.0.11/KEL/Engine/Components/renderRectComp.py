from KEL.Engine.Setup import *
from KEL.Engine.Core import *


class RenderRectComp:
    def start(self):
        self.transformComp = KEL.getComponent('TransformRectComp')

    def update(self):
        self.objectColor = KEL.getMaterial()
        lX, lY, w, h = self.transformComp.xLT, self.transformComp.yLT, self.transformComp.width, self.transformComp.height
        pygame.draw.rect(KEL.coreModules['Screen'].wn, self.objectColor, pygame.Rect((lX, lY), (w, h)))
