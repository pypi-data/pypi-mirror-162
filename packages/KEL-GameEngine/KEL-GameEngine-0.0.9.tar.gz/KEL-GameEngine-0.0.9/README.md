NOTE: This is under development and does not have many features.

This is a python Framework called KEL (Kinda Exploited Game Engine). In the future you might be able to call it a game engine but right now Its a tool i guess.
It (by the moment) does not have a UI and not many features. Heres a list of the upcoming features u might see in the near future.

* material and color functionality (color next update)
* better overall costumizability,
* UI (very far far far away). Its a goal of mine to at least have it,
* Better inherence with how transformcomp works,
* More components such as a collider, circle collider, polygon collider, polygon renderer and much more.

It will be more features but I just cant think of any that would make a difference for the user other
than small fixes.

Anyway here is a code example of how u can use this. This is only in one file but it can of course be
in many files.

    
    #
    # This will display a square moving to the right when pressing d and moving to the left when pressing a
    #

    from KEL import *



    class MyComponent:
        def start(self):
            self.holdRight = False
            self.holdLeft = False

            self.transformComp = KELEngine.getComponent('TransformRectComp') # Here we actually define the component in the start function (super proud of this)


        def update(self):
            if KELEngine.Input(inputKey='K_d', state='Down'): # State is if the func should return true on keyup or Down. Its defaulted as down but its good practise
                self.holdRight = True

            elif KELEngine.Input(inputKey='K_d', state='Up'):
                self.holdRight = False

            if KELEngine.Input(inputKey='K_a', state='Down'):
                self.holdLeft = True
            elif KELEngine.Input(inputKey='K_a', state='Up'):
                self.holdLeft = False


            if self.holdRight: self.transformComp.xLT += 1 # (xLT stands for x Left Top)

            if self.holdLeft: self.transformComp.xLT -= 1




    # Creating Objects
    wallComps = [RenderRectComp(), TransformRectComp(), MyComponent()]# U can change the values of TransformRectComp but its defaulted.

    KELEngine.addObject(objectName='Player', components=wallComps) # There are some additional settings such as what models u should use 
    # emptyModel is only available

    run()


This code is simple and u can do a lot more with the current features. 
