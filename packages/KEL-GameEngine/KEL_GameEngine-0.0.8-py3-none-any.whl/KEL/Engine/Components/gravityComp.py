import KEL

class GravityComp:
    def start(self, comps):
        self.velocity = 0
        self.isGround = False


    def update(self, comps, objects):
        # Increasing the increase
        print(self.isGround)

        if self.isGround == False:
            self.velocity += 0.98
        else:
            self.velocity = 0


        comps['TransformRectComp'].yLT += self.velocity


        return comps
