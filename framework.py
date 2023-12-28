import threading
import time
from pygame import gfxdraw
from math import sqrt
from pygame import mixer
from pygame import Surface
from pygame import font
from pygame import init as pginit
from pygame import display
from pygame import image
from pygame import draw
from pygame import Rect
from pygame import event as events
from pygame.constants import *
from pygame import mouse
from pygame import scrap
from os.path import dirname, realpath
from pygame import error as PygameEngineError
 

'''
Random facts about the time module
**mil = million**

time.perf_counter()
Very precise, changes at least 10mil times in 2.53 seconds
Very expensive, takes 2.53 seconds to call 10mil times
*Changes very quickly, should not be used for game clocks, but for performance measurements, dont call regularly in loop


time.monotonic()
Low precise, changes about 108 times in 1.67 seconds
Very fast, takes about 1.67 seconds to call 10mil times
*Changes slower than every second, should be called to measure time longer than .1 seconds, regularly faster to call than time.time() but only by a tiny bit

time.time()
Medium precise, changes about 1712 time in 1.71 seconds
Very fast, takes about 1.71 seconds to call 10mil times
*Changes about every thousandth of a second, anything closer than that and its not useful anymore

time.process_time()
DONT USE THIS, IT IS WACKY AND DOES NOT GIVE THE TIME YOU NORMALLY WANT
the others will be sufficient, only use if you know what you're doing!
'''
'''
Optimization Checklist
#####converting lists and tuples#####
tuple to tuple is the fastest by far
list to tuple is the 2nd fastest
tuple to list is 3rd fastest
list to list is just behind tuple to list

#####adding is faster than subtracting#####
#if you have a statement like
if x - y > z:
  dostuff()
#change it to
if x > y + z:
  dostuff()

#### if statements are faster than min(max(x,_min),_max) ###
if you are using min/max statements to check if a single number is out of bounds then
use if statements
'''
'''
Unicode Thingies for Special Chars:
tab = '\t'
backSpace = '\x08'
delete = '\x7f'
enter = '\r'
escape = '\x1b'
'''

def filePath():
  #might be able to optimize if i just use str manipulation on __file__ instead of os functions
  #but i dont know if it would continue to be portable across different os's
  return dirname(realpath(__file__))
tab_unicode = '\t'
back_unicode = '\x08'
enter_unicode = '\r'
delete_unicode = '\x7f'
escape_unicode = '\x1b'
paste_unicode = '\x16'
copy_unicode = '\x03'
WHEEL_SENSITIVITY = 7
lowerCaseLetters = {'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z'}
upperCaseLetters = {'A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z'}
allLetters = lowerCaseLetters.union(upperCaseLetters)
numbers = {'1','2','3','4','5','6','7','8','9','0'}
miscCharacters = {'\x08',' '}
symbolCharacters = {',','`','~','!','@','#','$','%','^','&','*','(',')','_','+','-','=','{','}','[',']','|','\\',';',':','"','<','>','.','?','/','`',"'"}
fileNameFriendlyCharactes = allLetters.union(numbers).union(miscCharacters).union(symbolCharacters).difference({'<','>','|','/','\\','*',':','?','"'})
preInitiated = 0
mixer.music.paused = 0
WIDTH, HEIGHT = (0,0)
minScreenX,minScreenY = 0,0
inputBoxSelected = False
keysThatIgnoreBoxSelected = set()
PATH = filePath()
MUSIC_END = USEREVENT + 1
mixer.music.set_endevent(MUSIC_END)
currentSoundName = ''
def addKeysThatIgnore(newKey):
  keysThatIgnoreBoxSelected.add(newKey)
class SoundError(BaseException):
  '''Error with pygame.mixer.music module'''
  def __init__(self,*args):
    pass
class function:
  '''A function of method'''
  #Just a class to increase readability
  pass
class Input:
  '''
  A way to dump all the input gathered by getAllInput() so that it can be directly put into
  update methods so that they can smartly pick what they need to update things.'''
  def __init__(self,mState,KDQueue,Events):
    self.mState = mState
    self.KDQueue = KDQueue
    try:
      self.Events = set(Events)
      self.mpos  =  mState[0]
      self.mousex  = mState[0][0]
      self.mousey  = mState[0][1]
      self.mb1  =  mState[1][0]
      self.mb2  =  mState[1][1]
      self.mb3  =  mState[1][2]
      self.wheel  = mState[2]
      self.mb1down  =  mState[3][0]
      self.mb2down  =  mState[3][1]
      self.mb3down  =  mState[3][2]
      self.mb1up = mState[4][0]
      self.mb2up = mState[4][1]
      self.mb3up = mState[4][2]
      self.quitEvent = False
    except TypeError:
      self.quitEvent = True

  def __getattr__(self, __name: str):
    return self.__dict__[__name]

class TitleScreen:
  def __init__(self,screen_time:int = -1):
    self._background_color = (0,0,0)
    self._rect = Rect(0,0,WIDTH,HEIGHT)
    self._defaults = None
    self._screen_time = screen_time if screen_time != -1 else 99999999999999999999
    self._start_time = None
    ###self._defaults setter should go last
    self._defaults = {name for name in self.__dict__}

  @property
  def background_color(self):
    self._background_color
  @background_color.setter
  def background_color(self,newColor):
    if not isinstance(newColor,tuple): raise TypeError("Has to be a tuple!")
    if len(newColor) != 3: raise TypeError("Color assignment is (R,G,B) (no A)!")
    for color in newColor:
        if not (0<= color <= 255): raise TypeError("Color range is not within bounds!")
    self._background_color = newColor
  
  #__setattr__ is unecesary cause there is not offsetPos to set for each draw_obj
  def start(self):
    thread = threading.Thread(target=self._start)
    thread.start()

  def _start(self):
    self._start_time = time.monotonic()
    while 1:
      if time.monotonic() - self._start_time > self._screen_time: #time has run out
        break
      else:
        self.draw()
        display.flip()

  def ChangeObjsOffset(self,newOffset,newSize) -> None:
    raise RuntimeError('Is not supported yet!!! :(')
    self._offset = tuple(newOffset)
    self._size = tuple(newSize)
    for obj in self.__dict__:
      if obj not in self._defaults:
        self.__dict__[obj].offSetPos = tuple(newOffset)
    self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])

  def update(self,myInput:Input):
    for object in self.__dict__:
      if object not in self._defaults:
        objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
        self.__dict__[object].update(objInput)

  def draw(self):
    draw.rect(screen,self._background_color,self._rect)
    for drawThing in self.__dict__:
      if drawThing not in self._defaults:
        self.__dict__[drawThing].draw()


class Image:
  @classmethod
  def accepts(self) -> tuple:
    return ()
  
  def __init__(self,pos:tuple,image:Surface):
    self._pos = tuple(pos)
    self.image = image
    self.offSetPos = (0,0)
    self.pos = tuple(pos)

  @property
  def pos(self):
    return self._pos

  @pos.setter
  def pos(self,newVal):
    self._pos = newVal
    self._offSetPos = (0,0)
    self.tpos = (self.offSetPos[0]+newVal[0],self.offSetPos[1]+newVal[1])

  @property
  def offSetPos(self):
    return self._offSetPos
  
  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self.tpos = (self.pos[0]+newVal[0],self.pos[1]+newVal[1])
  def update(self,_):
    pass

  def draw(self):
    screen.blit(self.image,self.tpos)
  
class ScreenSurface:
  @classmethod
  def accepts(self) -> tuple:
    return ()
  def __init__(self,pos,size,color = (0,0,0)):
    self.pos = pos
    self.size = size
    self.color = color
    self.surf = Rect(pos[0],pos[1],size[0],size[1])
  @property
  def offSetPos(self):
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self.surf = Rect(self.pos[0]+newVal[0],self.pos[1]+newVal[1],self.size[0],self.size[1])

  def update(self,*_):
    pass
  def draw(self):
    draw.rect(screen,self.color,self.surf)

class Debug:
  @classmethod
  def accepts(self) -> tuple:
    return ()
  def __init__(self,measureFunc = time.perf_counter,performanceImpact = 30):
    self.frameCount = 0
    self.frameTimes = [measureFunc(),]
    self.measureFunc = measureFunc
    self.drawEvery = performanceImpact

  def update(self):
    self.frameCount += 1
    if self.frameCount % self.drawEvery == 0:
      self.frameTimes.append(self.measureFunc())
      print(int(self.drawEvery/(self.frameTimes[-1]-self.frameTimes[-2])))

  def draw(self):
    return
    if self.frameCount % self.drawEvery == 0:
      print(int(self.drawEvery/(self.frameTimes[-1]-self.frameTimes[-2])))

  def onQuit(self):
    FPSlist = [self.drawEvery/(self.frameTimes[x+1]-self.frameTimes[x]) for x in range(len(self.frameTimes)-1)]
    FPSlist.sort()
    sum = 0
    for fps in FPSlist:
      sum += fps
    sum /= len(FPSlist)
    print(f'Avg FPS: {round(sum,2)}')
    print(f'Min FPS: {round(FPSlist[0],2)}')
    print(f'Max FPS: {round(FPSlist[-1],2)}')
    print(f'Total Frames Updated: {self.frameCount}')

class TextBox:
  @classmethod
  def accepts(self) -> tuple:
    return ()

  def __init__(self,pos,font,text,words_color):
    self.pos = pos
    self.font = font
    self.text = text
    self.words_color = words_color
    self.textsurface = self.font.render(self.text, True, self.words_color)
    self.offSetPos = (0,0)

  def update_text(self) -> None:
    '''
    Update the rendered text to match self.text
    '''
    self.textsurface = self.font.render(self.text,True,self.words_color)
  
  def setText(self,newText):
    self.text = newText
    self.textsurface = self.font.render(self.text,True,self.words_color)

  def update(self,_):
    pass

  def draw(self):
    screen.blit(self.textsurface,(self.pos[0] + self.offSetPos[0],self.pos[1] + self.offSetPos[1]))

class Options: #In Development
  def __init__(self,pos):
    self.options = dict()
    self.pos = pos
    self.font = font.SysFont("Courier New",20)

  def update(self):
    for num,option in enumerate(self.options):
      draw.rect(screen,(10,10,10),Rect(self.pos[0],self.pos[1]+num*30,70,30))
      screen.blit(self.font.render(option,1,(255,255,255)),(self.pos[0],self.pos[1]+num*30))

class Slider:

  @classmethod
  def accepts(self) -> tuple:
    return ('mpos','mb1down','mb1up')
  def __init__(self,x,y,xlen,ylen,min,max,save_function,slider_color,ball_color,acceptsInput:bool = True,type:int = 1,passed_color = None):
    self.x = x
    self.y = y
    self.xlen = xlen
    self.ylen = ylen
    self.sliderx = 0
    self.min = min
    self.max = max
    self.value = 0
    self.save_function = save_function
    self.countperpixel = (max-min)/xlen
    self.offSetPos = (0,0)
    self._rect = Rect(self.x-1,self.y-1,self.xlen+2,self.ylen+2)
    self.collider = Rect(self.x,self.y,self.xlen,self.ylen)
    self.acceptsInput = acceptsInput
    self.slider_color = slider_color
    self.ball_color = ball_color
    self.ball_pos = (self.x+self._offSetPos[0],self.y+self.ylen/2+self._offSetPos[1])
    self.active = 0
    self.pactive = 0
    self.type = type
    self.passed_color = passed_color
    self.passed_rect = Rect(0,0,0,0)
    self.mouse_active = 0

  def changeSliderLimits(self,newMin:int = None,newMax:int = None):
    if newMin is not None:
      self.min = newMin
    if newMax is not None:
      self.max = newMax
    self.countperpixel = (self.max-self.min)/self.xlen
    self.set_value(self.value)# recalculate ball, and passed_rect

  def onActivate(self):
    pass

  def onDeactivate(self):
    pass

  @property
  def offSetPos(self) -> tuple[int,int]:
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newVal) -> None:
    self._rect = Rect(self.x + newVal[0]-1,self.y+newVal[1]-1,self.xlen+2,self.ylen+2)
    self.collider = Rect(self.x + newVal[0],self.y+newVal[1],self.xlen,self.ylen)
    self._offSetPos = newVal
    self.ball_pos = (self.x+self._offSetPos[0],self.y+self.ylen/2+self._offSetPos[1])


  def update(self,things):
    if not self.acceptsInput: return 
    mpos,mb1down,mb1up = things
    if self.collider.collidepoint(mpos):
      self.mouse_active = 1
      if mb1down:
        self.active = 1
      elif mb1up:
        self.active = 0
    elif mb1down or mb1up: # if not colliding and mb1down or mb1up dont update
      self.mouse_active = 0
      self.active = 0
    else:
      self.mouse_active = 0
    
    if self.active and not self.pactive:
      self.onActivate()
    elif not self.active and self.pactive:
      self.onDeactivate()
    if self.active:
      self.sliderx = mpos[0] - self.x - self._offSetPos[0]
      newVal = int(self.sliderx*self.countperpixel)+self.min
      if newVal<0: newVal = 0
      elif newVal>self.max-1: newVal = self.max-1
      if self.value != newVal:
        self.value = newVal
        self.ball_pos = (self.sliderx+self.x+self._offSetPos[0],self.y+self.ylen/2+self._offSetPos[1])
        self.passed_rect = Rect(self.x+self._offSetPos[0],self.y+self._offSetPos[1],self.sliderx,self.ylen)
        self.save_function(self.value)
    self.pactive = self.active

  def draw(self):
    draw.rect(screen,self.slider_color,self._rect,0,2)
    if self.type == 1: #always show ball
      draw.circle(screen,self.ball_color,self.ball_pos,self.ylen)
    else:
      draw.rect(screen,self.passed_color,self.passed_rect,0,2)
      if self.mouse_active: #show ball when mouse hovering
        draw.circle(screen,self.ball_color,self.ball_pos,self.ylen)
      


  def set_value(self,newValue):
    '''set the value of slider, if slider is currently active(being controlled) then does not work''' 
    if self.active: return
    if newValue > self.max - 1: newValue = self.max - 1
    elif newValue < 0: newValue = 0
    self.value = newValue
    self.sliderx = int(newValue/self.countperpixel)
    self.ball_pos = (self.sliderx+self.x+self._offSetPos[0],self.y+self.ylen/2+self._offSetPos[1])
    self.passed_rect = Rect(self.x+self._offSetPos[0],self.y+self._offSetPos[1],self.sliderx,self.ylen)

class Dropdown:
  #TODO: make a slider go up and down next to dropdown
  @classmethod
  def accepts(self) -> tuple:
    return ('mpos','mb1down','wheel','mb3down')

  def __init__(self,pos,size,up_color,down_color,text_color,captions,outPutCommand,maxy,rightClickCommand = None,tpos = (0,0)):
    self.pos = list(pos)
    self.size = tuple(size)
    self.up_color = up_color
    self.down_color = down_color
    self.text_color = text_color
    self.captions_command = captions
    self.empty_list = list()
    self.captions = list(captions())
    self.mpos = [0,0]
    self.new_captions = list()
    self.outPutCommand = outPutCommand
    self.font = font.SysFont('Courier New', 20)
    self.yscroll = 0
    self.maxy = maxy
    self.tpos = tpos
    self.rightClickCommand = rightClickCommand if rightClickCommand else None
    for caption in self.captions:
      self.new_captions.append(self.font.render(caption, True, self.text_color))
    self.buttons = [Button((pos[0],pos[1]+count*size[1]),size[0],size[1],self.command,down_color,up_color,(min(up_color[0]+25,255),min(up_color[1]+25,255),min(up_color[2]+25,255)),caption,self.tpos[0],self.tpos[1],self.rightCommand,accepts_mb3=True if self.rightClickCommand else False) for count,caption in enumerate(self.new_captions)]
    self.offSetPos = (0,0)
    self.lenButtons = len(self.buttons)
    self._rect = Rect(self.pos[0],self.pos[1],self.size[0],self.maxy)
    self.mhover = 0
    self.pmhover = 0
  @property
  def offSetPos(self) -> tuple:
    return self._offSetPos

  def setAllToUp(self):
    for button in self.buttons:
      button.setToUp()

  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self._rect = Rect(self.pos[0]+newVal[0],self.pos[1]+newVal[1],self.size[0],self.maxy)
    for button in self.buttons:
      button.offSetPos = newVal

  def command(self):
    num = int((self.mpos[1]-self.pos[1]+self.yscroll-self.offSetPos[1])/self.size[1])
    self.outPutCommand(num)

  def onMouseEnter(self):
    pass
  def onMouseExit(self):
    pass

  def rightCommand(self):
    num = int((self.mpos[1]-self.pos[1]+self.yscroll-self.offSetPos[1])/self.size[1])
    self.rightClickCommand(num)

  def recalculate_options(self):
    self.captions = list(self.captions_command())
    self.new_captions = list()
    for caption in self.captions:
      self.new_captions.append(self.font.render(caption,1,self.text_color))
    self.buttons = [Button((self.pos[0],self.pos[1]+count*self.size[1]),self.size[0],self.size[1],self.command,self.down_color,self.up_color,(min(self.up_color[0]+25,255),min(self.up_color[1]+25,255),min(self.up_color[2]+25,255)),caption,self.tpos[0],self.tpos[1],self.rightCommand,accepts_mb3=True if self.rightClickCommand else False) for count,caption in enumerate(self.new_captions)]
    for button in self.buttons:
      button.offSetPos = self.offSetPos
    self.lenButtons = len(self.buttons)

  def update(self,things):
    '''mpos,mb1down,wheelState,mb3down'''
    mpos,mb1down,wheelState,mb3down = things
    if self._rect.collidepoint(mpos):  
      self.mhover = 1
      self.mpos = tuple(mpos)
      if self.size[1]*self.lenButtons > self.maxy and wheelState: #if scrolling is needed
        if self.size[1]*self.lenButtons >= self.maxy + self.yscroll: # if scrolling is possible
          self.yscroll = self.yscroll + wheelState * WHEEL_SENSITIVITY
          if self.yscroll + wheelState * WHEEL_SENSITIVITY > self.size[1]*self.lenButtons-self.maxy:
            self.yscroll = self.size[1]*self.lenButtons-self.maxy
          if self.yscroll < 0:
            self.yscroll = 0
          for button in self.buttons:
            button.offsetY = self.yscroll
      for button in self.buttons:
        button.update((mpos,mb1down,mb3down,self.empty_list))
    else:
      self.mhover = 0
    if self.mhover and not self.pmhover:
      self.onMouseEnter()
    elif not self.mhover and self.pmhover:
      self.onMouseExit()
      for button in self.buttons:
        button.setToUp()
    self.pmhover = self.mhover

  def draw(self):
    for button in self.buttons:
      #check if needs to be drawn
      if self.pos[1] +self.offSetPos[1] > button.y+button._offSetPos[1]-button.offsetY+button.ylen:
        continue
      if self.pos[1] + self.offSetPos[1]+self.maxy < button.y+button.offSetPos[1]-button.offsetY:
        continue
      button.draw()

  def __str__(self) -> str:
    return self.captions_command()
    
class LoadingBar:
  @classmethod
  def accepts(self):
    return ()
  def __init__(self,pos,size,background_color,bar_color,border_color):
    self.pos = pos
    self.size = size
    self.background_color = background_color
    self.bar_color = bar_color
    self.border_color = border_color
    self.fullRect = Rect(pos[0]-2,pos[1]-1,size[0]+4,size[1]+2)
    self.max = 100
    self.position = 0
    self.loadedRect = Rect(pos[0],pos[1],self.position*self.size[0]/self.max,self.size[1])
    self.offSetPos = (0,0)


  @property
  def offSetPos(self):
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self.fullRect = Rect(self.pos[0]+newVal[0]-2,self.pos[1]+newVal[1]-1,self.size[0]+4,self.size[1]+2)
    self.loadedRect = Rect(self.pos[0],self.pos[1],self.position*self.size[0]/self.max,self.size[1])


  def update(self,*_):
    pass

  def setPosition(self,newVal):
    if not isinstance(newVal,int):
      raise TypeError("Must be 'int' type")
    if newVal > 100:
      raise TypeError("Must not be greater than 100")
    if newVal < 0:
      raise TypeError("Must not be less than 0")
    self.position = newVal
    self.loadedRect = Rect(self.pos[0]+self.offSetPos[0],self.pos[1]+self.offSetPos[1],self.position*self.size[0]/self.max,self.size[1])

  def draw(self):
    draw.rect(screen,self.background_color,self.fullRect,0,2)
    draw.rect(screen,self.bar_color,self.loadedRect,0,2)
class InputBox:
  @classmethod
  def accepts(self) -> tuple:
    return ('mpos','mb1down','KDQueue')
  def __init__(self,pos,size,caption = '',box_color = (100,100,100),max_chars=500,save_function = lambda x:x,restrict_input = None):
    self.pos = pos
    self.size = size
    self.font = font.SysFont('Courier New', 21)
    self.active = False
    self.caption = caption
    self.box_color = box_color
    self.max_chars = max_chars
    self.chars = 0
    self.text = ''
    self.textsurface = self.font.render(self.text, True, (0, 0, 0))
    self.textRect = Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    self.max_chars_per_line = self.size[0]//12
    self.save_function = save_function
    self.restrict_input = restrict_input
    self.offSetPos = (0,0)
    self.timeactive = 0
    self.cursor_rect = Rect(0,0,50,10)
  @property
  def offSetPos(self):
    return self._offSetPos

  @offSetPos.setter
  def offSetPos(self,newPos):
    self._offSetPos = newPos
    self.textRect = Rect(self.pos[0]+self.offSetPos[0],self.pos[1]+self.offSetPos[1],self.size[0],self.size[1])

  def set_text(self,new_text):
    self.text = new_text

  def check_keys(self,key):
    if self.restrict_input and key not in self.restrict_input:
      return
    if self.active:
      if key == '\x08':
        if len(self.text) > 0:    
          self.text = self.text[:-1]
          self.chars -= 1
          if self.save_function:
            self.save_function(self.text)
          return
      elif self.chars != self.max_chars:
        if key == '\r':
          self.text += '\n'
        else:
          self.text +=key
        self.chars = len(self.text)
        self.save_function(self.text)

  def update(self,things):
    mpos,mb1down,keys = things
    if self.textRect.collidepoint(mpos):
      if mb1down:
        self.active = True
        self.timeactive = time.monotonic()
    else:
      if mb1down:
        self.active = False
    global inputBoxSelected
    if self.active:
      thingy = self.text
      inputBoxSelected = True
      for key in keys:
        self.check_keys(key)
      if thingy != self.text: #if text has been updated
        self.timeactive = time.monotonic()
        self.cursor_rect = Rect(self.pos[0]+ (len(self.text)%self.max_chars_per_line)*12 + self.offSetPos[0]+2,self.pos[1]+(len(self.text)//self.max_chars_per_line)*20 + self.offSetPos[1]+2,3,18)
    else:
      inputBoxSelected = False
      
  def draw(self): 
    if not self.text:
      if self.box_color:
        draw.rect(screen,self.box_color,self.textRect)
      self.textsurface = self.font.render(self.caption, True, (100, 100, 100))
      screen.blit(self.textsurface,(self.offSetPos[0]+self.pos[0],self.pos[1]+self.offSetPos[1]))
      if self.active and not int(time.monotonic()-self.timeactive) % 2:
        draw.rect(screen,(0,0,0),self.cursor_rect)
    else:
      letters = [letter for letter in self.text]
      if self.box_color:
        draw.rect(screen,self.box_color,self.textRect)
      for char_num, letter in enumerate(letters):
        self.textsurface = self.font.render(letter, True, (0, 0, 0))
        letterx = self.pos[0]+(char_num%self.max_chars_per_line)*12
        screen.blit(self.textsurface,(letterx+self.offSetPos[0],self.pos[1]+((char_num//self.max_chars_per_line)*20)+self.offSetPos[1]))
      if self.active and not int(time.monotonic()-self.timeactive) % 2:
        draw.rect(screen,(0,0,0),self.cursor_rect)

class RoundButton:
    @classmethod
    def accepts(self) -> tuple:
      return ('mpos','mb1','mb3down','KDQueue')
    def __init__(self,pos,radius,OnDownCommand,down_color,up_color,idle_color,surface = Surface((0,0)),textx = 0,texty = 0,rightClickCommand = None,key = None,accepts_mb3:bool = False, downCommand = None, OnUpCommand = None,keyCommand = 'OnDownCommand'):
      self.pos = pos
      self.radius = radius
      self.OnDownCommand = OnDownCommand
      self.downCommand = downCommand if downCommand else lambda:0
      self.OnUpCommand = OnUpCommand if OnUpCommand else lambda:0
      self.down_color = down_color
      self.up_color = up_color
      self.down = False
      self.previous_state = False
      self.idle_color = idle_color
      self.text = surface
      self.textx = textx
      self.texty = texty
      self.idle = False
      self.state = False
      self.offsetY = 0
      self.key = key
      self.accepts_mb3 = accepts_mb3
      self.rightClickCommand = self.exampleRightClick if rightClickCommand == None else rightClickCommand
      self.keyCommand = keyCommand
      self.offSetPos = (0,0)

    def exampleRightClick(self):
      print("you right clicked a button!!! :)")

    def SetDown(self):
      if self.down:
        self.downCommand()
        return
      self.down = True
      self.OnDownCommand()  

    def SetUp(self):
      if not self.down:
        return    
      self.down = False
      self.OnUpCommand()

    def draw(self):
        if self.down:
            gfxdraw.aacircle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius, self.down_color)
            gfxdraw.filled_circle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius, self.down_color)
        elif self.idle:
            gfxdraw.aacircle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius+1, self.idle_color)
            gfxdraw.filled_circle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius+1, self.idle_color)
        else:
            gfxdraw.aacircle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius, self.up_color)
            gfxdraw.filled_circle(screen, self.pos[0]+self.offSetPos[0], self.pos[1]+self.offSetPos[1], self.radius, self.up_color)
        if self.text:
            screen.blit(self.text,(self.pos[0]+self.textx+self.offSetPos[0],self.pos[1]+self.texty+self.offSetPos[1]))

    def update(self,things):
      mpos,mb1,mb3,keyQueue = things
      if self.key in keyQueue and ((not inputBoxSelected) or self.key in keysThatIgnoreBoxSelected):
        self.__dict__[self.keyCommand]()
      if sqrt((mpos[0]-self.pos[0]-self.offSetPos[0])**2+(mpos[1]-self.pos[1]-self.offSetPos[1])**2) > self.radius:
        self.idle = False
      else:
        self.idle = True
        if mb1:
          self.SetDown()
        else:
          self.SetUp()
        if self.accepts_mb3:
          if mb3:
            self.rightClickCommand()  

class ButtonSwitch:
  @classmethod
  def accepts(self) -> tuple:
    return ('mpos','mb1down')
  def __init__(self,pos,size,start_state,state_pics):
    self.pos = pos
    self.size = size
    self.state = start_state
    self.state_pics = state_pics
    

  def update(self,things):
    mpos,mb1 = things
    if mpos[0] > self.pos[0] and mpos[0] < self.pos[0] + self.size[0]:
      if mpos[1] > self.pos[1] and mpos[1] < self.pos[1] + self.size[1]:  
        if mb1:
          self.state = (self.state + 1) % len(self.state_pics)

  def draw(self):
    screen.blit(self.state_pics[self.state],self.pos)

class Button:
  font.init()
  default_font = font.SysFont("Arial",20)
  @classmethod
  def accepts(self) -> tuple:
    return ('mpos','mb1','mb3down','KDQueue')
  def __init__(self,pos,xlen,ylen,OnDownCommand,down_color,up_color,idle_color,text = Surface((0,0)),textx = 0,texty = 0,rightClickCommand = None,key = None,accepts_mb3:bool = False, downCommand = None, OnUpCommand = None,keyCommand = 'OnDownCommand'):
    self.x = pos[0]
    self.y = pos[1]
    self.xlen = xlen
    self.ylen = ylen
    self.OnDownCommand = OnDownCommand
    self.downCommand = downCommand if downCommand else lambda:0
    self.OnUpCommand = OnUpCommand if OnUpCommand else lambda:0
    self.down_color = down_color
    self.up_color = up_color
    self.down = False
    self.previous_state = False
    self.idle_color = idle_color
    self.text = text
    self.textx = textx
    self.texty = texty
    self.idle = False
    self.state = False
    self.key = key
    self.accepts_mb3 = accepts_mb3
    self.rightClickCommand = self.exampleRightClick if rightClickCommand == None else rightClickCommand
    self.keyCommand = keyCommand
    self._offSetPos = (0,0)
    self._offsetY = 0
    self.offSetPos = (0,0)
    self.offsetY = 0
    self._rect = Rect(self.x,self.y,self.xlen,self.ylen)
    if not isinstance(self.text,Surface):
      self.text = self.default_font.render(self.text,1,(0,0,0))
    self.pidle = 0
  @property
  def offSetPos(self):
    return self._offSetPos
  
  @property
  def offsetY(self):
    return self._offsetY
  
  @offsetY.setter
  def offsetY(self,newVal):
    self._offsetY = newVal
    self._rect = Rect(self.x+self.offSetPos[0],self.y+self.offSetPos[1]-self.offsetY,self.xlen,self.ylen)
    self.textPos = (self.x+self.textx + self.offSetPos[0],self.y + self.texty + self.offSetPos[1] - self.offsetY)

  @offSetPos.setter
  def offSetPos(self,newVal):
    self._offSetPos = newVal
    self._rect = Rect(self.x+newVal[0],self.y+newVal[1]-self.offsetY,self.xlen,self.ylen)
    self.textPos = (self.x+self.textx + self.offSetPos[0],self.y + self.texty + self.offSetPos[1] - self.offsetY)

  def onMouseEnter(self):
    #function to be overwritten for extra functionality
    pass
  def onMouseExit(self):
    #function to be overwritten for extra functionality
    pass

  def SetDown(self):
    if self.down:
      self.downCommand()
      return
    self.down = True
    self.OnDownCommand()  

  def SetUp(self):
    if not self.down:
      return    
    self.down = False
    self.OnUpCommand()
  def exampleRightClick(self) -> None:
    print("mid click!!")

  def draw(self) -> None:
    global screen
    if self.down:
      draw.rect(screen, self.down_color, self._rect)
    elif self.idle:
      draw.rect(screen, self.idle_color, self._rect)
    else:
      draw.rect(screen, self.up_color, self._rect)
    screen.blit(self.text,self.textPos)
  
  def setToUp(self) -> None:
    self.idle = False
    self.down = False

  def update(self,things) -> None:
    '''mpos,mb1,mbXdown,KDQueue'''
    mpos,mstate, mb3,keyQueue = things
    if keyQueue and self.key:
      if self.key in keyQueue and ((not inputBoxSelected) or self.key in keysThatIgnoreBoxSelected):
        self.__dict__[self.keyCommand]()
    
    if self._rect.collidepoint(mpos):
      self.idle = True
      if mstate:
        self.SetDown()
      elif self.down:
        self.SetUp()
      if self.accepts_mb3 and mb3:
        self.rightClickCommand()
    else:
      self.idle = False
    if self.idle and not self.pidle:
      self.onMouseEnter()
    elif not self.idle and self.pidle:
      self.onMouseExit()
      self.setToUp()
    self.pidle = self.idle

class MiniWindow:
  def __init__(self,name,pos,size,color =(70,70,70),exit_command:function = lambda:1):
    self._offset = tuple(pos)
    self._size = tuple(size)
    if self._size[1] < 200: raise TypeError("Cannot Make A MiniWindow that small")
    self._background_color = color
    self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])
    self._top_rect = Rect(self._offset[0],self._offset[1],self._size[0],25) 
    self.window_caption = TextBox((5,5),font.SysFont('Arial',15),name,(0,0,0))
    self.exit_button = Button((size[0]-30,0),30,25,lambda:1,(255,100,100),(210,210,210),(255,10,10),'',7,4,OnUpCommand=exit_command)

  def __setattr__(self, __name: str, __value) -> None:
    if __name not in {'_offset','_background_color','_size','_rect','_top_rect'}:
      self.__dict__[__name] = __value
      self.__dict__[__name].offSetPos = self._offset
    else:
      self.__dict__[__name] = __value
    
  def ChangeObjsOffset(self,newOffset,newSize) -> None:
    self._offset = tuple(newOffset)
    self._size = tuple(newSize)
    for obj in self.__dict__:
      if obj not in {'_offset','_background_color','_size','_rect','_top_rect'}:
        self.__dict__[obj].offSetPos = tuple(newOffset)
    self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])

  def update(self,myInput:Input):
    for object in self.__dict__:
      if object not in {'_offset','_background_color','_size','_rect','_top_rect'}:
        objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
        self.__dict__[object].update(objInput)

  def draw(self):
    draw.rect(screen,self._background_color,self._rect)
    draw.rect(screen,(210,210,210),self._top_rect)
    top_x = (self._offset[0]+self._size[0]-23)
    top_y = (self._offset[1]+5)
    bottom_x = (self._offset[0]+self._size[0]-8)
    bottom_y = (self._offset[1]+20)
    for drawThing in self.__dict__:
      if drawThing not in ('_offset','_background_color','_size','_rect','_top_rect'):
        self.__dict__[drawThing].draw()
    draw.line(screen,(0,0,0),(top_x,top_y),(bottom_x,bottom_y),2)
    draw.line(screen,(0,0,0),(top_x,bottom_y),(bottom_x,top_y),2)
    display.update(self._rect)

class Empty:
  @classmethod
  def accepts(self) -> tuple:
    return ()
  def __init__(self):
    pass

  def update(self,_):
    pass

  def draw(self,_):
    pass

class Stopwatch:
  def __init__(self,function = time.time):
    self.startTime = None
    self.extraTime = 0
    self.paused = False
    self.measurement = function

  def running(self):
    if self.startTime:
      return True
    else:
      return False
    
  def start(self):
    self.startTime = self.measurement()

  def stop(self):
    time = self.timeElapsed()
    self.paused = 0
    self.startTime = None
    self.extraTime = 0
    return time

  def timeElapsed(self):
    if not self.paused:
      return self.measurement() - self.startTime + self.extraTime
    elif self.paused:
      return self.extraTime
    
  def setTime(self,newVal):
    if not self.paused:
      self.startTime = self.measurement() - newVal
      self.extraTime = 0
    elif self.paused:
      self.extraTime = newVal

  def pause(self):
    if not self.paused:
      self.extraTime += self.measurement() - self.startTime
      self.paused = True

  def unpause(self):
    if self.paused:
      self.startTime = self.measurement()
      self.paused = False
  
  def reset(self):
    self.startTime, self.extraTime = self.measurement(), 0
  time = timeElapsed
##########################
class Main_Space:
    @classmethod
    def accepts(self) -> tuple:
      return ()
    def __init__(self):
        pass

    def update(self,*_):
        pass

    def draw(self,*_):
        pass
    
    def onQuit(self):
        pass

class Border:
    def __init__(self):
        pass

    def update():
        pass

    def draw():
        pass

class Window_Space:
    def __init__(self):
      self._background_color = (0,0,0)
      self._mainSpaces = list()
      self._mainSpace = ScrollingMS()
      self._activeMainSpace = 0
      self._mainSpacePos = [0,0]
      self._mainSpaceSize = [WIDTH,HEIGHT]
      self._borders = {"top":None,"bottom":None,"left":None,"right":None}  
      self._miniWindows = {}     
      self._debug = Main_Space()
      self._miniwindowactive = False
      self._drawRects = list()
      self._rect = Rect(0,0,WIDTH,HEIGHT)
      self._msRect = self._rect

    def addMiniWindow(self,name:str,pos:tuple,size:tuple,bg_color=None,exit_command:function=None) -> None:
      if bg_color == None:
        bg_color = (70,70,70)
      if exit_command == None:
        exit_command = self.deactivateMiniWindow
      self._miniWindows[name] = MiniWindow(name,pos,size,bg_color,exit_command=exit_command)
    def activateMiniWindow(self,name,passFunc:bool = 0) -> None|function:
      if not name in self._miniWindows.keys(): raise TypeError('That miniwindow does not exist')
      if passFunc: return lambda :self.activateMiniWindow(name)
      if self._miniwindowactive: raise TypeError('Only one MiniWindow can be active at a time')
      self._miniwindowactive = True
      self._activeMiniWindow = self._miniWindows[name]
    def deactivateMiniWindow(self) -> None:
      self._miniwindowactive = False
      self._activeMiniWindow = None
      self._currentMS = self.mainSpace
      self.first_draw()
    def miniWindow(self,name) -> MiniWindow:
      return self._miniWindows[name]
    @property
    def top(self) -> Border: return self._borders['top']
    @property
    def left(self) -> Border: return self._borders['left']
    @property
    def right(self) -> Border: return self._borders['right']
    @property 
    def bottom(self) -> Border: return self._borders['bottom']
    @property
    def mainSpace(self) -> Main_Space:
      return self._mainSpaces[self._activeMainSpace]
    @property
    def MSSize(self) -> tuple:
      return self._mainSpaceSize
    @property
    def MSPos(self) -> tuple:
      return self._mainSpacePos
    def drawBorder(self,borderName):
      if borderName not in {'top','left','right','bottom'}:
        raise TypeError(f"Border named: {borderName} does not exist!")
      border = self._borders[borderName]
      border.draw()
      display.update(border._rect)

    @property
    def activeMainSpace(self) -> int:
      return self._activeMainSpace
    
    def getMainSpace(self,num:int) -> Main_Space:
      return self._mainSpaces[num]
    
    def drawMS(self) -> None:
      '''Draw Active Main Space'''
      self._mainSpaces[self._activeMainSpace].draw()
      display.update(self._msRect)
    
    def deleteMainSpace(self,num:int) -> None:
      del self._mainSpaces[num]
      if self._activeMainSpace == len(self._mainSpaces):
        self._activeMainSpace -= 1
        self._currentMS = self._mainSpaces[self._activeMainSpace]
        self._currentMS.draw()
        display.update(self._msRect)
    @property
    def leftSize(self) -> int:
      try:
        return self._borders['left']._size[0]
      except AttributeError:
        return 0
    @property
    def topSize(self) -> int:
      try:
        return self._borders['top']._size[1]
      except AttributeError:
        return 0
    @property
    def rightSize(self) -> int:
      try:
        return self._borders['right']._size[0]
      except AttributeError:
        return 0
    @property
    def bottomSize(self) -> int:
      try:
        return self._borders['bottom']._size[1]
      except AttributeError:
        return 0 
    @mainSpace.setter
    def mainSpace(self, newVal:int | Main_Space) -> None:
      if isinstance(newVal,int):
        self._activeMainSpace = newVal
        self._currentMS = self._mainSpaces[newVal]
      elif isinstance(newVal,ScrollingMS):
        self._mainSpaces.append(newVal)
        self._activeMainSpace = len(self._mainSpaces)-1
        self._currentMS = self._mainSpaces[-1]
      else:
        return
      self._update_mainspace()
      #self._currentMS.draw()  not sure why here commenting out just in case
      #display.update(self._msRect)

    def addMainSpace(self,newMS:Main_Space) -> None:
      self._mainSpaces.append(newMS)
      self._update_mainspace()

    def addDebugInfo(self,impact = 30) -> None:
      '''impact is how much you want the debug impact the current performance.
      the lower 'impact' is the higher the actual impact, impact > 0'''
      self._debug = Debug(performanceImpact=impact)
    
    def setActiveMainSpace(self,newVal:int) -> None:
      self._activeMainSpace = newVal
      self._currentMS = self._mainSpaces[newVal]
      self._currentMS.draw()
      display.update(self._msRect)
    
    def emptyMainSpace(self,num:int) -> None:
      for var in self._mainSpaces[num].__dict__:
        if var not in self._mainSpaces[num]._defaults:
          del self._mainSpaces[num].__dict__[var]

    @property
    def background_color(self) -> tuple:
      return self._background_color

    @background_color.setter
    def background_color(self,newColor) -> None:
      if not isinstance(newColor,tuple):
        raise TypeError("Has to be a tuple!")
      if len(newColor) != 3:
        raise TypeError("Color assignment is (R,G,B) (no A)!")
      for color in newColor:
        if not (0<= color <= 255):
          raise TypeError("Color range is not within bounds!")
      self._background_color = newColor

    def addBorder(self,direction:str,sizeintoMid,color,draw_need = 1) -> None:
      if direction == 'top':
        self._borders['top'] = Top_Border(color,draw_need)
        self._borders['top'].setSizeAndPos(self._borders,sizeintoMid)
        self._mainSpacePos[1] = sizeintoMid
        self._mainSpaceSize[1] -= sizeintoMid
        self._update_mainspace()
      elif direction == 'bottom':
        self._borders['bottom'] = Bottom_Border(color,draw_need)
        self._borders['bottom'].setSizeAndPos(self._borders,sizeintoMid)
        self._mainSpaceSize[1] -= sizeintoMid
        self._update_mainspace()
      elif direction == 'left':
        self._borders['left'] = Left_Border(color,draw_need)
        self._borders['left'].setSizeAndPos(self._borders,sizeintoMid)
        self._mainSpacePos[0] = sizeintoMid
        self._mainSpaceSize[0] -= sizeintoMid
        self._update_mainspace()
      elif direction == 'right':
        self._borders['right'] = Right_Border(color,draw_need)
        self._borders['right'].setSizeAndPos(self._borders,sizeintoMid)
        self._mainSpaceSize[0] -= sizeintoMid
        self._update_mainspace()

    def _update_mainspace(self) -> None:
      self._msRect = Rect(self._mainSpacePos[0],self._mainSpacePos[1],self._mainSpaceSize[0],self._mainSpaceSize[1])
      for mainSpace in self._mainSpaces:
        mainSpace.ChangeObjsOffset(self._mainSpacePos,self._mainSpaceSize)

    def first_update(self) -> None:
      self._live_borders = tuple([x for x in self._borders.values() if x != None])

    def update(self,input:Input) -> None:
      self._mpos = input.mpos
      if self._miniwindowactive:
        self._activeMiniWindow.update(input)
      else:  
        self.mainSpace.update(input)
        for border in self._live_borders:
          border.update(input)
        self._debug.update()

    def first_draw(self) -> None:
      self.mainSpace.draw()
      for border in self._borders.values():
        if border != None:
          border.draw()
      display.update(self._rect)
      #arrange borders by draw_need so that self.draw() can draw them
      self._draw_when_needed_borders = tuple([border for border in self._borders.values() if border != None and border._draw_need == 1])
      self._need_to_draw_borders =  tuple([border for border in self._borders.values() if border != None and border._draw_need == 2])

    def draw(self) -> None:
      if self._miniwindowactive:
        self._activeMiniWindow.draw()
      else:
        screen.fill(self.background_color)
        if self._msRect.collidepoint(self._mpos):
          self._currentMS.draw()
          display.update(self._msRect)
        else:
          for border in self._draw_when_needed_borders:
            if border._rect.collidepoint(self._mpos):
              border.draw()
              display.update(border._rect)
        for border in self._need_to_draw_borders:
          border.draw()
          display.update(border._rect)
      self._debug.draw()

    def onQuit(self) -> None:
      self._debug.onQuit()

class Top_Border(Border):
    def __init__(self,color,draw_need):
      self._color = color
      self._pos = tuple
      self._size = tuple
      self._rect = Rect
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] == '_':
        self.__dict__[__name] = __value
      else:
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._pos

    def setSizeAndPos(self, existingBorders:dict,ylen):
      if existingBorders['left'] == None:
        self._pos = (0,0) 
      else:
        self._pos = (existingBorders['left']._size[0],0)
      if existingBorders['right'] == None:
        self._size = (WIDTH-self._pos[0],ylen)
      else:
        self._size = (WIDTH-self._pos[0]-existingBorders['right']._size[0],ylen)
      self._rect = Rect(self._pos[0],self._pos[1],self._size[0],self._size[1])

    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        self.onMouseExit()
        if not self._draw_need: return
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
              obj.draw()
        display.update(self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(objInput)
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()

class Left_Border(Border):
    def __init__(self,color,draw_need):
      self._pos = (0,0)
      self._color = color
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] != '_':
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._pos
      else:
        self.__dict__[__name] = __value

    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass
    def setSizeAndPos(self, existingBorders:dict,xlen):
      if existingBorders['top'] == None:
        self._pos = (0,0)
      else:
        self._pos = (0,existingBorders['top']._size[1])
      if existingBorders['bottom'] == None:
        self._size = (xlen,HEIGHT-self._pos[1])
      else:
        self._size = (xlen,HEIGHT-self._pos[1]-existingBorders['bottom']._size[1])
      self._rect = Rect(self._pos[0],self._pos[1],self._size[0],self._size[1])

    def update(self,myInput):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        self.onMouseExit()
        if not self._draw_need: return
        draw.rect(screen,self._color,self._rect)
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
              obj.draw()
            elif isinstance(obj,Dropdown):
              obj.setAllToUp()
              obj.draw()
            else:
              obj.draw()
        display.update(self._rect)
      for object in self.__dict__:
        if object[0] == '_':
          continue
        else:
          objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(objInput)
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for obj in self.__dict__:
        if obj[0] != '_':
          self.__dict__[obj].draw()

class Right_Border(Border):
    def __init__(self,color,draw_need):
      self._color = color
      self._pos = tuple
      self._size = tuple
      self._rect = Rect
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] == '_':
        self.__dict__[__name] = __value
      else:
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._pos

    def setSizeAndPos(self, existingBorders:dict,xlen):
      if existingBorders['top'] == None:
        self._pos = (WIDTH-xlen,0) 
      else:
        self._pos = (WIDTH-xlen,existingBorders['top']._size[1])
      if existingBorders['bottom'] == None:
        self._size = (WIDTH-self._pos[0],HEIGHT-self._pos[1])
      else:
        self._size = (WIDTH-self._pos[0],HEIGHT-self._pos[1]-existingBorders['bottom']._size[1])
      self._rect = Rect(self._pos[0],self._pos[1],self._size[0],self._size[1])

    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        self.onMouseExit()
        if not self._draw_need: return
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
              obj.draw()
        display.update(self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(objInput)
      self._pactive = self._active


    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()

class Bottom_Border(Border):
    def __init__(self,color,draw_need):
      self._pos = (0,0)
      self._size = (0,0)
      self._color = color
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0

    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] == '_':
        self.__dict__[__name] = __value
      else:
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._pos

    def setSizeAndPos(self, existingBorders:dict,ylen):
      if existingBorders['left'] == None:
        self._pos = (0,HEIGHT-ylen) 
      else:
        self._pos = (existingBorders['left']._size[0],HEIGHT-ylen)
      if existingBorders['right'] == None:
        self._size = (WIDTH-self._pos[0],ylen)
      else:
        self._size = (WIDTH-self._pos[0]-existingBorders['right']._size[0],ylen)
      self._rect = Rect(self._pos[0],self._pos[1],self._size[0],self._size[1])
    
    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        self.onMouseExit()
        if not self._draw_need: return
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
              obj.draw()
        display.update(self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(objInput)
      self._pactive = self._active
    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()

class ScrollingMS(Main_Space):
    def __init__(self,draw_need = 2):
      super().__init__()
      self._scrollVal = 0
      self._offset = (0,0)
      self._size = (WIDTH,HEIGHT)
      self._background_color = (0,0,0)
      self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])
      self._draw_need = draw_need
      self._defaults = None
      self._active = 0
      self._pactive = 0
      ###self._defaults setter should go last
      self._defaults = {name for name in self.__dict__}

    @property
    def size(self):
      return self._size

    @property
    def background_color(self):
      self._background_color
    def set_background_color(self,newColor):
      if not isinstance(newColor,tuple):
        raise TypeError("Has to be a tuple!")
      if len(newColor) != 3:
        raise TypeError("Color assignment is (R,G,B) (no A)!")
      for color in newColor:
        if not (0<= color <= 255):
          raise TypeError("Color range is not within bounds!")
      self._background_color = newColor
    def __setattr__(self, __name: str, __value) -> None:
      if __name[0] != '_' :
        self.__dict__[__name] = __value
        self.__dict__[__name].offSetPos = self._offset
      else:
        self.__dict__[__name] = __value

    def onMouseEnter(self):
      pass
    def onMouseExit(self):
      pass
    def ChangeObjsOffset(self,newOffset,newSize) -> None:
      self._offset = tuple(newOffset)
      self._size = tuple(newSize)
      for obj in self.__dict__:
        if obj not in self._defaults:
          self.__dict__[obj].offSetPos = tuple(newOffset)
      self._rect = Rect(self._offset[0],self._offset[1],self._size[0],self._size[1])

    def update(self,myInput:Input):
      if self._rect.collidepoint(myInput.mpos):
        self._active = 1
      else:
        self._active = 0
      if self._active and not self._pactive:
        self.onMouseEnter()
      elif not self._active and self._pactive:
        self.onMouseExit()
        for obj in self.__dict__.values():
          if isinstance(obj,Button):
            obj.setToUp()
          elif isinstance(obj,Dropdown):
            obj.setAllToUp()
        self.draw()
        display.update(self._rect)
      for object in self.__dict__:
        if object not in self._defaults:
          objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(objInput)
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._background_color,self._rect)
      for drawThing in self.__dict__:
        if drawThing not in self._defaults:
          self.__dict__[drawThing].draw()

class SpaceMS(Main_Space):
    def __init__(self):
        super().__init__()
        self.spacePos = [0,0]

def pre_init() -> None:
    '''Sets Variables HEIGHT and WIDTH'''
    global screenInfo, _WIDTH,_HEIGHT,preInitiated
    if not preInitiated:
      pginit()
    screenInfo = display.Info()
    _WIDTH,_HEIGHT = screenInfo.current_w,screenInfo.current_h
    preInitiated = 1

def init(screenSize:tuple,flags = 0,name:str = '') -> None:
    global saved_flags,saved_name
    saved_flags = flags
    saved_name = name
    if not preInitiated:
      pre_init()
    global screen, running,WIDTH,HEIGHT
    screen = display.set_mode(screenSize,flags)
    WIDTH,HEIGHT = screenSize
    if name:
      display.set_caption(name)
    running = 1

def MinScreenSize(x:int,y:int) -> None:
    global minScreenX,minScreenY
    minScreenX = x
    minScreenY = y

def makeFont(FontName,FontSize):
  return font.SysFont(FontName,FontSize)

def find_all_files(ending:str,addedPath:str = '',strip:bool = True) -> list[str]:
    '''Find all files with a specific extension like .png or .txt'''
    from os.path import dirname, realpath
    from os import walk 
    all_songs = list()
    path = dirname(realpath(__file__)) 
    for _root, _dirs, files in walk(path+addedPath): 
        for file in files:
            if file.endswith(ending):
              if strip:
                all_songs.append(str('.'.join(file.split('.')[:-1])))
              else:
                all_songs.append(str(file))
    return all_songs

def loadSound(_FileName:str = '',usePath:bool = True) -> None:
  global currentSoundName
  FileName = '\\'.join([PATH,_FileName]) if usePath else _FileName
  mixer.music.unload()
  if _FileName:
    if _FileName.endswith('.ogg'):
      mixer.music.load(FileName)
      currentSoundName = _FileName[:-4]
    else:
      mixer.music.load(FileName+'.ogg')
      currentSoundName = _FileName
  else:
    currentSoundName = ''
  onSoundLoad()

def playSound(loops:int = 0,start:int = 0,fade_ms:int = 0) -> None:
  mixer.music.play(loops,start,fade_ms)
  onSoundPlay()

def stopSound() -> None:
  mixer.music.stop()

def pauseSound() -> None:
  mixer.music.paused = 1
  mixer.music.pause()

def unpauseSound() -> None:
  mixer.music.paused = 0
  mixer.music.unpause()

def PauseUnPauseSound() -> None:
  if mixer.music.paused:
    unpauseSound()
  elif not mixer.music.paused:
    pauseSound()
  else:
    raise IndexError(f"Value mixer.music.paused is not a bool instead it is a {type(mixer.music.paused)}: {mixer.music.paused}")

def SetSoundVolume(newVal:float) -> None:
  if not isinstance(newVal,float):
    raise TypeError(f"Volume is not correct data type! '{type(newVal)}")
  elif newVal > 1:
    newVal = 1
  elif newVal < 0:
    newVal = 0
  mixer.music.set_volume(newVal)

def setSoundPos(newPos:float) -> None:
  try:
    mixer.music.set_pos(newPos)
  except PygameEngineError:
    if mixer.music.get_busy():
      raise SoundError('Cannot Set Position of Sound currently')
    else:
      raise SoundError('Cannot Set position of sound currently, it looks like you dont have a sound loaded, maybe that is the problem')

def onSoundLoad():
  pass

def onSoundPlay():
  pass

def setOnSoundLoad(func:function) -> None:
  global onSoundLoad
  onSoundLoad = func

def setOnSoundPlay(func:function) -> None:
  global onSoundPlay
  onSoundPlay = func

def setSoundEndEvent(func:function):
  global endEventFunction
  endEventFunction = func

def endEventFunction():
  pass

def getSoundVolume() -> float:
  return mixer.music.get_volume()

def getSoundPos() -> int:
  return mixer.music.get_pos()

def getSoundPause() -> bool:
  return True if mixer.music.paused else False

def setWindowIcon(surf:Surface) -> None:
  display.set_icon(surf)

def loadImg(FileName:str,useAlpha:bool = False,usePath:bool = True) -> Surface:
  global PATH
  fullFilePath = '/'.join([PATH,FileName]) if usePath else FileName
  '''Returns a pygame Surface of image provided with FileName\n
  Use Alpha for Images that should have a transparent background'''
  if useAlpha:
    return image.load(fullFilePath).convert_alpha()
  elif not useAlpha:
    return image.load(fullFilePath).convert()

def flipSurface(surface:Surface,x:bool,y:bool) -> Surface:
  from pygame import transform
  return transform.flip(surface.copy(),x,y) 

def resizeSurface(surface:Surface,newSize:tuple) -> Surface:
  from pygame import transform
  return transform.scale(surface.copy(),newSize)

def isValidScreenSize(screenSize:tuple) -> bool:
  global minScreenX,minScreenY
  if screenSize[0] < minScreenX:
    return 0
  if screenSize[1] < minScreenY:
    return 0
  return 1

def get_clipboard(raw:bool = False) -> str | bytes:
  for _type in scrap.get_types():
    if SCRAP_TEXT in _type:
      if raw:
        return scrap.get(SCRAP_TEXT)

      else:
        return scrap.get(SCRAP_TEXT).decode('utf-8')
    
  return ''
def resizeToBecomeValid(screenSize:tuple) -> tuple[int,int]:
  global minScreenX,minScreenY,WIDTH,HEIGHT
  WIDTH,HEIGHT = (max(screenSize[0],minScreenX),max(screenSize[1],minScreenY))
  return (WIDTH,HEIGHT)


def getAllInput() -> Input:
  """Returns MouseState and KeyDownQueue, if quit event triggered, returns tuple (False,False)"""
  keyDownQueue = list()
  mb1d,mb2d,mb3d,scrollDown,scrollUp,mb1u,mb2u,mb3u = 0,0,0,0,0,0,0,0
  flagsRaised = list()
  for event in events.get():
    if event.type == QUIT:
      return Input(False,False,False)
    elif event.type == KEYDOWN:
      keyDownQueue.append(event.unicode)
      if event.unicode == paste_unicode:
        for letter in get_clipboard():
          keyDownQueue.append(letter)
    elif event.type == MOUSEBUTTONDOWN:
      if event.button == 1:
        mb1d = 1
      elif event.button == 2:
        mb2d = 1
      elif event.button == 3:
        mb3d = 1
      elif event.button == 4:
        scrollDown = 1
      elif event.button == 5:
        scrollUp = 1
    elif event.type == MOUSEBUTTONUP:
      if event.button == 1:
        mb1u = 1
      elif event.button == 2:
        mb2u = 1
      elif event.button == 3:
        mb3u = 1
    elif event.type == MUSIC_END:
      endEventFunction()
    elif event.type == VIDEORESIZE:
      global WIDTH,HEIGHT
      WIDTH,HEIGHT = display.get_window_size()
      if not isValidScreenSize((WIDTH,HEIGHT)):
        display.set_mode((resizeToBecomeValid((WIDTH,HEIGHT))),saved_flags)
    flagsRaised.append(event.type)
  mouseState = mouse.get_pos(),mouse.get_pressed(),scrollUp-scrollDown,(mb1d,mb2d,mb3d),(mb1u,mb2u,mb3u)
  return Input(mouseState,keyDownQueue,flagsRaised)
