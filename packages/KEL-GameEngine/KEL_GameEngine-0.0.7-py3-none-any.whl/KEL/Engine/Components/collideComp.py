import KEL


class CollideComp:
    def start(self, comps):
        pass

    def update(self, comps):
        if comps['TransformRectComp'].yLT > KEL.wH - comps['TransformRectComp'].height:
            comps['GravityComp'].isGround = True
            comps['TransformRectComp'].yLT = KEL.wH - comps['TransformRectComp'].height



        return comps
