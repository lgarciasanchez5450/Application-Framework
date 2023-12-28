'''
This Example will be a Notes Application
'''
from framework import *
goodKeys = allLetters.union(miscCharacters)
def example():
    with open("Hello.txt",'w') as file:
        file.write(windowSpace.mainSpace.inputbox.text)

file = open("Hello.txt",'a')
file.close
init((500,500),0,'Notes')
windowSpace = Window_Space()
windowSpace.mainSpace = ScrollingMS()
windowSpace.addBorder('top',50,(146, 158, 190))
windowSpace.top.title = TextBox((0,0),makeFont("Arial",20),'Notes Application',(0,0,0))
windowSpace.mainSpace.button = Button((0,0),100,100,example,(0,0,255),(0,255,0),(255,0,0),None,0,0)
windowSpace.mainSpace.inputbox = InputBox((100,100),(300,300),'Notes...',(200,230,240),300,lambda x:x,goodKeys)
windowSpace.mainSpace.set_background_color((213, 224, 255))
windowSpace.first_update()
windowSpace.first_draw()
with open("Hello.txt",'r') as file:
    windowSpace.mainSpace.inputbox.text = file.read()
running = 1
while running:
    myInput = getAllInput()
    if myInput.quitEvent:
        running = False
        continue
    elif escape_unicode in myInput.KDQueue: # '\x1b' is unicode for escape button 
        running = False
    windowSpace.update(myInput)
    windowSpace.draw()
