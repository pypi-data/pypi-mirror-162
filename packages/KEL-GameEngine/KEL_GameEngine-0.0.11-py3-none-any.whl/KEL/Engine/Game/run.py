from KEL.Engine.Core import *


def run(mode="standard", scene=None):
    if mode == "standard":
        KEL.startObjects()
        run = True
        while run:
            KEL.updateEngine()

            if KEL.rawInput('type', 'QUIT'):
                run = False



# Start engine when importing
KEL.startCoreModules()


if __name__ == "__main__":
    run()
