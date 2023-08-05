This is a Game Engine called KEL (Kinda Exploited Libary). Its built on top of pygame. Note that this is not very seruis or any good. Just a project I 
thought would be fun to work with.

This is a small demo and source code. It will show a square. When you press space it will go down, when you release it will stop falling.


Now how does this work?

It works by having a Engine(core) and a while loop updateing the core. You can find this inside KEL/Engine/Game/Game.py. There you will assign objects
and add them to the Engine.objects(a dictionary).
When you add them u execute the command Engine.addObject(). There you will have to pass three parameters. The first one being the name of the object.
The second one being what model you should add (right now I only have emptyModel but things such as circle and square and other shapes will be added).
The third one being what components you should addinonay add to the object. A component is a class that make changes to the object. This will be how u
will write scripts and make changes to the object.


Now if you want to try this out u will have to clone the project.
U can go to the game file (KEL/Engine/Game/game.py) and add objects and components there.
u can see what components are available in KEL/Engine/Components directory. u can copy how I made my square and do something like it.

If u want to make a costome component u will have to make a new python file in the Components directory. Then go into the __init__.py in the Components directory
and add your file to it (just copy a line and change the last file to yours). Then in your component file copy this:

'
import KEL

class yourComponentName:

    # This is called  before the first frame
    # Used for add global variable by the self keyword
    def start(self):
        self.randomGlobalValue = "Im Global"


    # This func is called every frame
    def update(self):
        # Acces your randomGlobalValue here
        self.randomGlobalValue = "Some Thing else"


'

Now u can see what i did in the moveWallComp.py script and how i did it but I can tell u the very few fetures this engine have.
Use KEL.Input() to have an input. The parameter is a string and it is basicly the keys of pygame
For example:
print(KEL.Input('K_SPACE'))
or
prit(KEL.Input('K_a'))

this function will return a string, either "Down" or "Up"
if its down it means that the key is pressed down
if its up it means that the key is unpressed?

Theres also an raw event function
use KEL.rawInput() to have a raw event from pygame. it takes two strings and returns True or false
example
if KEL.rawInput('type', 'QUIT'):
    print("Da program is quiting")

or
if KEL.rawInput('key', 'K_SPACE'):
    print("Space is pressed")

to read about this read about pygame

I might have to refine the method I do this input in the future.


This is officially a libary but it cant yet be used as one.



I might recomed this to someone who might a thought going in the game engine industry because this is 
how almost every game engine works and its a simplified version of it so it might be helpful? This does require some basic knowlage of coding
and preferably an understanding of OOP in python(not neccesary).


AS u might have guessed this is inspired by the Unity game engine.
