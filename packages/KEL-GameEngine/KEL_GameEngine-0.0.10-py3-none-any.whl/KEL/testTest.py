import KEL

wallComps = [ KEL.TransformRectComp(), KEL.RenderRectComp(), KEL.GravityComp(), KEL.CollideComp() ]
KEL.KELCORE.addObject(objectName='Wall', objectInstance=emptyComp(), objectLocation='objects', components=wallComps)


# Run the program
KEL.run()
