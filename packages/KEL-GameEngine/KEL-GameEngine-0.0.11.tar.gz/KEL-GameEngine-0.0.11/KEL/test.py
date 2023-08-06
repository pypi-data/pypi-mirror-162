#
# This will display a square moving to the right when pressing d and moving to the left when pressing a
#

from KEL import *

class MyComponent:
    def start(self):
        self.holdRight = False
        self.holdLeft = False

        self.transformComp = KEL.getComponent('TransformRectComp')


    def update(self):
        if KEL.Input(inputKey='K_d', state='Down'): self.holdRight = True # State is if the func should return true on keyup or Down. Its defaulted as down but its good practise
        elif KEL.Input(inputKey='K_d', state='Up'): self.holdRight = False

        if KEL.Input(inputKey='K_a', state='Down'): self.holdLeft = True
        elif KEL.Input(inputKey='K_a', state='Up'): self.holdLeft = False

        if self.holdRight: self.transformComp.xLT += 1 # (xLT stands for x Left Top)
        if self.holdLeft: self.transformComp.xLT -= 1


# Creating Objects
wallComps = [RenderRectComp(), TransformRectComp(), MyComponent()]# U can change the values of TransformRectComp but its defaulted.
KEL.addObject(objectName='Player', components=wallComps) # There are some additional settings such as what models u should use (emptyModel is only available) or where to place the object (in the future with folders YAY)


# Create Materials
KEL.createMaterial(materialName='background', materialColor='#282828')
KEL.createMaterial(materialName='player', materialColor='#d65d0e')


# Adding Materials
KEL.addMaterial(materialName='player', objectName='Player')
KEL.coreModules['Screen'].bgColor = "#232323"


run()
