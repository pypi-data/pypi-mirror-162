from KEL.Engine.Game.pygameSetup import *
from KEL.Engine.Const import *


class RenderRectComp:
    def start(self, comps):
        try: comps['TransformRectComp']
        
        except KeyError as err: print("Component", err, "not found")


    def update(self, components, objects):
        lX, lY, w, h = components['TransformRectComp'].xLT, components['TransformRectComp'].yLT, components['TransformRectComp'].width, components['TransformRectComp'].height
        pygame.draw.rect(wn, playerColor, pygame.Rect((lX, lY), (w, h)))


        return components
