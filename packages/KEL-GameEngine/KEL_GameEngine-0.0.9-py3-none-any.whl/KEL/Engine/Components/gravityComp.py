from KEL.Engine.Core import *

class GravityComp:
    def start(self):
        self.velocity = -10
        self.isGround = False


    def update(self):
        transformComp = KELEngine.getComponent('TransformRectComp')
        


        # Increasing the increase
        if self.isGround == False:
            self.velocity += 0.98
        else:
            self.velocity = 0

        
        transformComp.yLT += self.velocity
