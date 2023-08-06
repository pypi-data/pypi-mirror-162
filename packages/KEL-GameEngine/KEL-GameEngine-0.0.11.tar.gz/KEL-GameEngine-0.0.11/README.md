# Introduction
NOTE: This is under development and does not have many features.

This is a python Framework called KEL (Kinda Exploited Game Engine). Its build on top of pygame, thefore the name. In the future you might be able to call it a game engine but right now Its a tool i guess.
It (by the moment) does not have a UI and not many features. Of course u can excpect a lot of features in the future.

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

            self.transformComp = KEL.getComponent('TransformRectComp')


        def update(self):
            if KEL.Input(inputKey='K_d', state='Down'): self.holdRight = True # State is if the func should return true on keyup or Down. Its defaulted as down but its good practise
            elif KEL.Input(inputKey='K_d', state='Up'): self.holdRight = False

            if KEL.Input(inputKey='K_a', state='Down'): self.holdLeft = True
            elif KEL.Input(inputKey='K_a', state='Up'): self.holdLeft = False

            if self.holdRight: self.transformComp.xLT += 1 # (xLT stands for x Left Top)
            if self.holdLeft: self.transformComp.xLT -= 1


    # Creating Objects
    wallComps = [RenderRectComp(), TransformRectComp(), MyComponent()] # U can change the values of TransformRectComp but its defaulted.
    KEL.addObject(objectName='Player', components=wallComps) # There are some additional settings such as what models u should use (emptyModel is only available) or where to place the object (in the future with folders YAY)


    # Create Materials
    KEL.createMaterial(materialName='background', materialColor='#282828')
    KEL.createMaterial(materialName='player', materialColor='#d65d0e')


    # Adding Materials
    KEL.addMaterial(materialName='player', objectName='Player')
    KEL.coreModules['Screen'].bgColor = "#232323"


    run()

This code does display all of the current features but this is a very simple example and u can go a lot longer.

# Explaining the code (and more)
Now to explain whats happening here. The KEL class is the one u see being used to add objects and createMaterials and stuff. It is the core of the libary.

When u add an object u provide x parameters. Every argument is defaulted but two is neccesary for a functioning object I would say.
One parameter is the name of the object as u can see. Another one is what component the object should have. In the future u will be able to add components in a slick way to an object after declaration.
Another is the model u should use. Its defaulted as emptyModel (shown in the code above). I havnt provided any other models to use but excpect some in the future such as square or anything like that.
Another one is where the object should be located. Its defaulted as None and isnt compatible by the moment. In the future u will have the ability to add folder to ur objects dictionary
(they are stored in a dictionary).

Now lets anylise the Input.
KEL.Input(): what is that? Well its will return a bool and it takes to parameters the first one being what key u want checked. The second one is how the function should react when pressing that key
or when that key is pressed up. As u can see that function will only recognize the frame that the key was pressed down or up so we will do that manualy (maybe yull se that in the future).
There is another type of input that is not shown. RawInput(). This takes to arguments and it could look something like this.
    
    if KEL.RawInput('type', 'QUIT'): print("i want to quit the program")


This is a feature more near the core of pygame. It will do the 'pygame.' for u and the event loops for u (if ur familiar with pygame) but its basicly a glorified game loop. If u want to know what
argument this could take read a little about pygame event handleling. This is the same thing as saying (in the pygame world):

    for event in pygame.event.get():
        if event.type == pygame.QUIT: print("i want to quit the program")


so read a bit about pygames event handleling if u want to udelise this feature.

Unfortunatly KEL does not currently support mouse handleling but u can of course use the RawInput method but thats lame. This will be seen in a future update.


# Materials
Lets talk about materials.
As u saw we udelised materials to display colors. In the future materials will also support images being put on top of them. Lets now go over all the materials functions.

    KEL.createMaterial(materialName='myRandomMaterial', materialColor='#ffffff')
    KEL.addMaterial(materialName='myRandomMaterial', objectName='MyRandomObject')
    myOwnMat = KEL.getMaterial()
    myOwnMat2 = KEL.getRawMaterial(materialName='myRandomMaterial')
    myOwnMat3 = KEl.getObjectMaterial(self, objectName='myRandomObject')


The first method is when u create a material (clearly)
The second method is when u add a Material on top of a object so it can display that material on top of its
The third method returns a color(material). This is used inside of a component when trying to acces there own material (put on top of it). This is used by the RenderRectComp
The fourth method returns a color. The materials are stored in a dictionary and the function is accesing that dictionary and plopping out the name of the material u want.
The fift method returns, once again, a color. This is liked the third method but u specify the object that u want to grab the material for.

I think that was all the materials methods. There will be more in the future but this is it for now.



# Download
The procces to download this is quit simple. Just use pip.
Pip command:
pip install KEL-GameEngine                              (If u know what ur doing u can ofc use pip3)

U can also visit the page on pypi here:
https://pypi.org/project/KEL-GameEngine/


# Patron
u thought
