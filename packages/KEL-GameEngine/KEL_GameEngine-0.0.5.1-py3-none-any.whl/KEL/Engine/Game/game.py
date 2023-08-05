from KEL import *


def game():
    KELCORE.start()

    
    run = True
    while run:
        KELCORE.updateEngine()
        
        if rawInput('type', 'QUIT'):
            run = False
        


# Security
if __name__ == "__main__":
    game()
