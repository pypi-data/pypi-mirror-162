#
# This will display a square moving to the right when pressing d and moving to the left when pressing a
#

from KEL import *



class MyComponent:
    def start(self):
        self.holdRight = False
        self.holdLeft = False

        self.transformComp = KELEngine.getComponent('TransformRectComp')


    def update(self):
        if KELEngine.Input(inputKey='K_d', state='Down'): # State is if the func should return true on keyup or Down. Its defaulted as down but its good practise
            self.holdRight = True

        elif KELEngine.Input(inputKey='K_d', state='Up'):
            self.holdRight = False

        if KELEngine.Input(inputKey='K_a', state='Down'):
            self.holdLeft = True
        elif KELEngine.Input(inputKey='K_a', state='Up'):
            self.holdLeft = False


        if self.holdRight: self.transformComp.xLT += 1 # (xLT stands for x Left Top)

        if self.holdLeft: self.transformComp.xLT -= 1




# Creating Objects
wallComps = [RenderRectComp(), TransformRectComp(), MyComponent()]# U can change the values of TransformRectComp but its defaulted.

KELEngine.addObject(objectName='Player', components=wallComps, objectColor="#232323") # There are some additional settings such as what models u should use 
# emptyModel is only available

run()
