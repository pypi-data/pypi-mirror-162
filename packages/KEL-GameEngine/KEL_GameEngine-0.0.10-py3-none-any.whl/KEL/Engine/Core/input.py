from KEL.Engine.Game.pygameSetup import *
from KEL.Engine.Core.core import *


def Input(eventEquals) -> str:
    # Loop thru event
    for event in KELCORE.coreModules['Events'].events:    
        
        if hasattr(event, 'key'): # Check if event has key so no errors

            pygameAttr = getattr(pygame, eventEquals) # Well do this to compare the event.key and the attr

            if event.key == pygameAttr: # Compare
                # Check if its keydown or keyup
                if event.type == pygame.KEYDOWN: 
                    return "Down"
                
                if event.type == pygame.KEYUP:
                    return "Up"
