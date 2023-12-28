from framework import *
init((500,500),0,'Color Picker')
_r = 0
_g = 0
_b = 0

def r(newVal):
    global _r
    _r = newVal
def g(newVal):
    global _g
    _g = newVal
def b(newVal):
    global _b
    _b = newVal
basic_font = makeFont('Arial',30)
window_space = Window_Space()
window_space.mainSpace = ScrollingMS()
window_space.mainSpace.set_background_color((50,50,50))
window_space.mainSpace.slider = Slider(10,300,300,10,0,256,r,(0,0,0),(255,255,255))
window_space.mainSpace.slider1 = Slider(10,350,300,10,0,256,g,(0,0,0),(255,255,255))
window_space.mainSpace.slider2 = Slider(10,400,300,10,0,256,b,(0,0,0),(255,255,255))
window_space.mainSpace.rnum = TextBox((400,300),basic_font,'',(0,0,0))
window_space.mainSpace.gnum = TextBox((400,350),basic_font,'',(0,0,0))
window_space.mainSpace.bnum = TextBox((400,400),basic_font,'',(0,0,0))
window_space.mainSpace.color = ScreenSurface((0,0),(100,100),(_r,_g,_b))
window_space.first_update()
window_space.first_draw()
while 1:
    myInput = getAllInput()
    if myInput.quitEvent:
        break
    else:
        window_space.mainSpace.color = ScreenSurface((0,0),(100,100),(_r,_g,_b))
        window_space.mainSpace.rnum = TextBox((400,300),basic_font,str(_r),(0,0,0))
        window_space.mainSpace.gnum = TextBox((400,350),basic_font,str(_g),(0,0,0))
        window_space.mainSpace.bnum = TextBox((400,400),basic_font,str(_b),(0,0,0))
        window_space.update(myInput)
        window_space.draw()
