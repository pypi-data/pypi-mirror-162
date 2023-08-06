from KEL.Engine.Game.pygameSetup import *
from KEL.Engine.Core.core import *

def rawInput(eAttr, eEquals):
    for event in KELCORE.coreModules['Events'].events:
        if hasattr(event, eAttr):
            if hasattr(pygame, eEquals):
                realEquals = getattr(pygame, eEquals)
                attr = getattr(event, eAttr)

                if attr == realEquals:
                    return True
