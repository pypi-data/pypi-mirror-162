import KEL


wallComps = [KEL.TransformRectComp(), KEL.RenderRectComp(), KEL.GravityComp(), KEL.CollideComp()]
KEL.KELCORE.addObject('Wall', KEL.EmptyModel(), wallComps)


run = True
KEL.KELCORE.start()
while run:
    KEL.KELCORE.updateEngine()


    if KEL.rawInput('type', 'QUIT'):
        run = False
