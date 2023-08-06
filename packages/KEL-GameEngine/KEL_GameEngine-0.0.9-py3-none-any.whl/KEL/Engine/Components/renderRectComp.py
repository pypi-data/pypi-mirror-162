from KEL.Engine.Setup import *
from KEL.Engine.Core import *


class RenderRectComp:
    def start(self):
        pass

    def update(self):
        transformComp = KELEngine.getComponent('TransformRectComp')

        lX, lY, w, h = transformComp.xLT, transformComp.yLT, transformComp.width, transformComp.height
        pygame.draw.rect(wn, "#000000", pygame.Rect((lX, lY), (w, h)))
