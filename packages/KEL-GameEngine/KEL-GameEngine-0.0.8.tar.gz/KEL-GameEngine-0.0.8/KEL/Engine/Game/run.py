from KEL.Engine.Core.core import *
from KEL.Engine.Core.rawInput import *


def run(mode="standard"):
    if mode == "standard":
        KELCORE.startEngine()
        
        run = True
        while run:
            KELCORE.updateEngine()

            if rawInput('type', 'QUIT'):
                run = False


if __name__ == "__main__":
    run()
