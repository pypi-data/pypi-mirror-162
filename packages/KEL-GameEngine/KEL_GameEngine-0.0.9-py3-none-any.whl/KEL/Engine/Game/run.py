from KEL.Engine.Core import *


def run(mode="standard"):
    if mode == "standard":
        KELEngine.startEngine()
        
        run = True
        while run:
            KELEngine.updateEngine()

            if KELEngine.rawInput('type', 'QUIT'):
                run = False


if __name__ == "__main__":
    run()
