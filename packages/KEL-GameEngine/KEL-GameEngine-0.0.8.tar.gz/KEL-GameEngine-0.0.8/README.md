NOTE: This is under development and does not have many features.


This is a Game Engine called KEL (Kinda Exploited Libary). Its built on top of pygame since the name KEL. It doese not have many features but u can use it.
Its a libary and I wouldnt recomend cloning the repo and using it there. It is possible but kinda no good.

Example Usage of Kel:
    
    import KEL
    
    class MyOwnComp:
        def start(self, comps):
            self.moveRight = False
            self.moveLeft = False

        def update(self, comps):
            # Just moving right if pressing 


            inpD = KEL.Input('K_d')
            inpA = KEL.Input('K_a')

            if inpD == 'Down':
                self.moveRight = True
            elif inpD == 'Up':
                self.moveRight = False

            if inpA == 'Down':
                self.moveLeft = True
            elif inpA == 'Up':
                self.moveLeft = False

            if self.moveRight:
                comps['TransformRectComp'].xLT += 1 # yLT stands for x Left Top

            if self.moveLeft:
                comps['TransformRectComp'].xLT -= 1 # yLT stands for x Left Top

            return comps

    
    # Creating Object
    wallComps = [KEL.RenderRectComp(), KEL.TransformRectComp(), MyOwnComp()] # U can change the values of TransformRectComp but its defaulted.
    KEL.KELCORE.addObject(objectName='Player', ) # There are some additional settings such as what models should i use
    #(defaulted as emptyModel) and objectInstance (if u want to save it in a folder (super alpha not reliable))
    


    # Running Kel (the most reasent update)
    KEL.run()


This will just display a square that moves to the right when pressing d and move to the left when pressing a.
As I said this is steadely under development and this script in the future will look vastly different.

To install this libary just do:
pip3 install KEL-GameEngine

or go to the pypi page here: https://pypi.org/project/KEL-GameEngine/


I made this project because I wanted something to do so dont excpect a spectacular game Engine.

As u might have telled this is heavely inspired by unity. U will here not have an UI or have as much features as unity.
U also dont have to do a lot of things to get it running but all of that will be fixed more or less in the future. 
But the lack of features and the simelarities with unity might be a good thing if your starting of your journy in unity.
So it could be used as a easier to a beginner to understand (easier languages) and with it simplicity.



License: NONE (so feel free to take this but dont pls)
