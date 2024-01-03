'''
Framework for building Graphical User Interfaces for existing applications\n
This has been used to make:\n
Music Player (similar to Spotify)\n
Notes Application (trashy)
'''
import threading, time
from math import sqrt, cos, sin, hypot,atan2,pi
from vector import Vec2Int
import unicode
from typing import Callable,Protocol,TypeAlias
from array import array
from FrameworkTypes import SupportsUpdate,SupportsDraw,SupportsQuit,BorderDirecton,Final, Runnable
from debug import profile

from pygame import Surface
from pygame import font
from pygame import gfxdraw
from pygame import display
from pygame.display import iconify as minimize
from pygame import image
from pygame import draw
from pygame import Rect
from pygame import event as events
from pygame import constants as CONSTANTS
from pygame import mouse
from pygame import scrap
from pygame import transform
from pygame import time as pg_time

import pygame
pygame.init()
from os.path import dirname, realpath
PATH = dirname(realpath(__file__))
del dirname, realpath

import sys
if sys.platform == 'win32':
  from ctypes import windll
  def maximize():
    '''Maximize Screen'''
    HWND = display.get_wm_info()['window']
    windll.user32.ShowWindow(HWND, 3)
del sys

def requirePlatform(*supported_platforms:str):
  if sys.platform not in supported_platforms:
    if len(supported_platforms) == 1:
      raise SystemError(f'This program only supports {supported_platforms[0]}, not {sys.platform}')
    else:
      raise SystemError(f'This program only supports {supported_platforms}, not {sys.platform}')


_info = display.Info()
MONITOR_WIDTH:Final[int] = _info.current_w
MONITOR_HEIGHT:Final[int] = _info.current_h
del _info

WIDTH, HEIGHT = 0,0
WHEEL_SENSITIVITY = 10

minScreenX,minScreenY = 0,0
inputBoxSelected = False
fps = 60
clock:pg_time.Clock = pg_time.Clock()

class Input:
  '''
  A way to dump all the input gathered by getAllInput() so that it can be directly put into
  update methods so that they can smartly pick what they need to update things.
  '''
  Events:set = set()
  KDQueue:list = []
  KUQueue:list = []
  mpos:Vec2Int = Vec2Int(0,0)
  
  mb1:bool
  mb2:bool
  mb3:bool
  wheel:int
  mbd:list[bool] = []
  mb1down:bool
  mb2down:bool
  mb3down:bool
  mb1up:bool
  mb2up:bool
  mb3up:bool
  quitEvent:bool = False

class TextBox:
  __slots__ = 'pos','text_font','text','words_color','text_surf','showing'
  def __init__(self,pos:Vec2Int,text_font:font.Font,text:str,words_color:pygame.Color,showing:bool = True):
    self.pos = pos.copy()
    self.text_font = text_font
    self.text = text
    self.words_color = words_color
    self.text_surf = self.text_font.render(self.text, True, self.words_color)
    self.showing = showing
  
  def setText(self,new_text:str) -> None:
    if self.text == new_text: return
    self.text = new_text
    self.text_surf = self.text_font.render(self.text,True,self.words_color)

  def setShowing(self,__value:bool) -> None:
    self.showing = __value

  def draw(self,surf:Surface):
    if self.showing:
      surf.blit(self.text_surf,self.pos.tupled)

class InputBox:
  def __init__(self,pos,size,caption = '',box_color = (100,100,100),max_chars=500,save_function = lambda x:x,restrict_input = None,fontSize = 21):
    self.pos = pos
    self.size = size
    self.font = font.SysFont('Courier New',fontSize)
    character = self.font.render('H',True,(0,0,0))
    self.character_x,self.character_y = character.get_size()
    del character
    self.active = False
    self.caption = caption
    self.box_color = box_color
    self.max_chars = max_chars
    self.chars = 0
    self.text = ''
    self.textsurface = self.font.render(self.text, True, (0, 0, 0))
    self.textRect = Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    self.max_chars_per_line = self.size[0]//self.character_x
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
    self.chars = len(new_text)
    self.text = new_text

  def check_keys(self,key):
    if self.active and self.restrict_input and key in self.restrict_input:
      if key == unicode.constants.BACK:
        if self.text:  #if self.text has any thing in it  
          self.text = self.text[:-1]
          self.chars -= 1
          self.save_function(self.text)
          return
      elif self.chars < self.max_chars: #has not reached max characters yet
        if key == '\r':
          self.text += '\n'
        else:
          self.text += key
        self.chars += 1 #previously, self.chars = len(self.text)
        self.save_function(self.text)

  def update(self,things):
    '''mpos,mb1down,keys'''
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
        self.cursor_rect = Rect(self.pos[0]+ (len(self.text)%self.max_chars_per_line)*self.character_x + self._offSetPos[0]+2,self.pos[1]+(len(self.text)//self.max_chars_per_line)*self.character_y + self._offSetPos[1]+2,3,self.character_y-3)
    else:
      inputBoxSelected = False
      
  def draw(self): 
    if not self.text:
      if self.box_color:
        draw.rect(screen,self.box_color,self.textRect)
      self.textsurface = self.font.render(self.caption, True, (100, 100, 100))
      screen.blit(self.textsurface,(self._offSetPos[0]+self.pos[0],self.pos[1]+self._offSetPos[1]))
      if self.active and not int(time.monotonic()-self.timeactive) % 2:
        draw.rect(screen,(0,0,0),self.cursor_rect)
    else:
      letters = [letter for letter in self.text]
      if self.box_color:
        draw.rect(screen,self.box_color,self.textRect)
      for char_num, letter in enumerate(letters):
        self.textsurface = self.font.render(letter, True, (0, 0, 0))
        letterx = self.pos[0]+(char_num%self.max_chars_per_line)*self.character_x
        screen.blit(self.textsurface,(letterx+self._offSetPos[0],self.pos[1]+((char_num//self.max_chars_per_line)*self.character_y)+self._offSetPos[1]))
      if self.active and not int(time.monotonic()-self.timeactive) % 2:
        draw.rect(screen,(0,0,0),self.cursor_rect)

class KeyBoundFunction: 
  __slots__ = 'func','keys','ignore_box_selected'
  def __init__(self,func:Callable,keys:tuple[str],ignore_box_selected:bool = False):
    self.func = func
    self.keys = set(keys)
    self.ignore_box_selected = ignore_box_selected

  def update(self,mpos:Vec2Int) -> None:
    KDQueue = set(Input.KDQueue).intersection(self.keys)
    if KDQueue:
      if self.ignore_box_selected:
        self.func()
      elif not inputBoxSelected:
        self.func()

class ButtonSimple:
  pass

class Button:
  font.init()
  default_font = font.SysFont("Arial",20)
  @classmethod
  def accepts(cls) -> tuple:
    return ('mpos','mb1down','mb3down','KDQueue','mb1up')
  __slots__ = ('x','y','xlen','ylen','OnDownCommand','OnUpCommand','down_color','up_color','down','previous_state','idle_color','text','textx','texty','idle','state','key','text_color','accepts_mb3','rightClickCommand','keyCommand','_offSetPos','_offsetY','_rect','pidle','textPos')
  def __init__(self,pos,xlen,ylen,OnDownCommand,down_color,up_color,idle_color,text = Surface((0,0)),textx:int = 0,texty:int = 0,rightClickCommand:Callable|None = None,key:str|None = None,accepts_mb3:bool = False, OnUpCommand:Callable|None = None,keyCommand:str = 'OnDownCommand',text_color:tuple = (0,0,0)):
    self.x = pos[0]
    self.y = pos[1]
    self.xlen = xlen
    self.ylen = ylen
    self.OnDownCommand = OnDownCommand
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
    self.text_color = text_color
    self.accepts_mb3 = accepts_mb3
    self.rightClickCommand = rightClickCommand if rightClickCommand is not None else lambda:None
    self.keyCommand = keyCommand
    self._offSetPos = (0,0)
    self._offsetY = 0
    self.offSetPos = (0,0)
    self.offsetY = 0
    self._rect = Rect(self.x,self.y,self.xlen,self.ylen)
    if not isinstance(self.text,Surface):
      self.text = self.default_font.render(self.text,True,self.text_color)
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
    '''mpos,mb1down,mb3down,KDQueue,mb1up'''
    mpos,mb1down, mb3,keyQueue,mb1up = things

    if keyQueue and self.key:
      if self.key in keyQueue and ((not inputBoxSelected) or self.key in keysThatIgnoreBoxSelected): #type: ignore
        self.__dict__[self.keyCommand]()
    if self._rect.collidepoint(mpos):
      if not self.pidle:
        self.onMouseEnter()
      self.idle = True
      if mb1down:
        self.OnDownCommand()
        self.down = True
      elif self.down and mb1up: #if we are down and just released mouse
        self.OnUpCommand()
        self.down = False

      if self.accepts_mb3 and mb3:
        self.rightClickCommand()
    elif self.pidle:
      self.idle = False
      self.down = False
      self.onMouseExit()
    self.pidle = self.idle

class Stopwatch:
  def __init__(self,function:Callable[[],float] = time.time):
    self.startTime = 0.0
    self.extraTime = 0.0
    self.paused = False
    self.measurement = function

  def running(self) -> bool:
    return not self.paused and bool(self.startTime)
    
  def start(self):
    self.startTime = self.measurement()

  def stop(self) -> float:
    time = self.timeElapsed()
    self.paused = False
    self.startTime = 0.0
    self.extraTime = 0.0
    return time

  def timeElapsed(self) -> float:
    if self.paused:
      return self.extraTime
    else:
      return self.measurement() - self.startTime + self.extraTime
    
  def setTime(self,newVal:float):
    if not self.paused:
      self.startTime = self.measurement() - newVal
      self.extraTime = 0.0
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
    self.startTime, self.extraTime = self.measurement(), 0.0
  
class Subspace:
  __slots__ = 'topleft','size','bg_color','surf','_elements_to_draw','_elements_to_update'
  def __init__(self,topleft:Vec2Int, size:Vec2Int):
    self.topleft = topleft.copy()
    self.size = size.copy()
    self.bg_color:tuple[int,int,int] = (0,0,0)
    self.surf = Surface(size.tupled)
    self._elements_to_draw:list[SupportsDraw] = []
    self._elements_to_update:list[SupportsUpdate] = []
    # Note: Elements can be in both to_draw and to_update at the same time!
  
  def addElement(self,element:SupportsDraw|SupportsUpdate):
    if hasattr(element,'draw') and callable(element.draw): # type: ignore 
      self._elements_to_draw.append(element) # type: ignore
    if hasattr(element,'update') and callable(element.update): # type: ignore 
      self._elements_to_draw.append(element) # type: ignore

  def update(self,mpos:Vec2Int):
    updated_mpos = mpos-self.topleft
    for u_object in self._elements_to_update:
      u_object.update(updated_mpos)

  def draw(self,surf:Surface):
    self.surf.fill(self.bg_color)
    for d_object in self._elements_to_draw:
      d_object.draw(self.surf)
    surf.blit(self.surf,self.topleft.tupled)
class TitleScreen(Subspace):

  '''This is a Space which can run independantly of the 
    WindowSpace and functions as a watered down version of
  it. Made to run in a thread'''
  __slots__ = 'title_done','fadeout_time','alpha_from_fadeout'
  def __init__(self,pos:Vec2Int,size:Vec2Int):
    super().__init__(pos,size)
    self.title_done = False
    self.fadeout_time = 1.0
    starting_alpha = 255
    ft = self.fadeout_time
    self.alpha_from_fadeout = lambda time: max(0,(starting_alpha/ft)*time)
 

  def run(self):
    dt = 0
    while True:
      if self.title_done and self.fadeout_time < 0:
        self.onQuit()
        break
      else:
        updateInput()
        self.update(Input.mpos - self.topleft)
        if self.title_done:
          self.fadeout_time -= dt
        self.surf.set_alpha(self.alpha_from_fadeout(self.fadeout_time).__trunc__())
        self.draw(screen)
        display.flip()
        dt = clock.tick(fps) / 1_000.0

  def onQuit(self): ...

  def stop(self) -> None:
    self.title_done = True

class WindowSpace:
  __slots__ = 'pos','size','surf','bg_color','_mainSpaces','_currentMainSpaceID','_mainSpacePos','_mainSpaceSize','_borders','active_borders','_miniWindows',\
  '_miniwindowactive','_visible_elements','_updating_elements'
  def __init__(self,pos:Vec2Int = Vec2Int(0,0),size:Vec2Int = Vec2Int(0,0), bg_color:tuple[int,int,int] = (0,0,0)):
    self.pos = pos.copy()
    size.x = size.x if size.x else MONITOR_WIDTH #change 0's to monitor size's
    size.y = size.y if size.y else MONITOR_HEIGHT #change 0's to monitor size's
    self.size = size.copy()
    self.surf = Surface(self.size.tupled)
    self.bg_color = bg_color

    self._mainSpaces:dict[int,Subspace] = {}
    self._currentMainSpaceID:int = -1
    self._mainSpacePos = Vec2Int(0,0)
    self._mainSpaceSize = size.copy()

    self._borders:dict[BorderDirecton,list[Subspace]] = {"top":[],"bottom":[],"left":[],"right":[]} 
    self.active_borders:list[Subspace] = []
    self._miniWindows = {}
    self._miniwindowactive = False
    self._visible_elements:list[SupportsDraw] = []
    self._updating_elements:list[SupportsUpdate] = []

  @property
  def topBorders(self): return self._borders['top']
  @property
  def leftBorders(self): return self._borders['left']
  @property
  def rightBorders(self): return self._borders['right']
  @property 
  def bottomBorders(self): return self._borders['bottom']
  @property
  def mainSpace(self):
    return self._mainSpaces[self._currentMainSpaceID]

  def addMainSpace(self,id:int, newMS:Subspace) -> None:
    self._mainSpaces[id] = newMS

  def setActiveMainSpace(self,id:int):
    assert id in self._mainSpaces
    self._currentMainSpaceID = id

  def _recalculateMainSpaceSizeAndPosWithRespectToBorders(self):
    left = self._borders['left'][-1].topleft.x + self._borders['left'][-1].size.x if self._borders['left'] else 0
    top = self._borders['top'][-1].topleft.y + self._borders['top'][-1].size.y if self._borders['top'] else 0
    right = self._borders['right'][-1].topleft.x if self._borders['right'] else self.size.x
    bottom = self._borders['bottom'][-1].topleft.y if self._borders['bottom'] else self.size.y
    self._mainSpacePos = Vec2Int(left,top)
    self._mainSpaceSize = Vec2Int(right-left,bottom-top) #bottom - top is because the y axis is inverted

  def addBorder(self,direction:BorderDirecton,widthOrHeight:int) -> None:
    topleft:Vec2Int
    match direction:
      case 'top':
        size = Vec2Int(self._mainSpaceSize.x,widthOrHeight)
        topleft = self._mainSpacePos.copy()
      case 'bottom':
        size = Vec2Int(self._mainSpaceSize.x,widthOrHeight)
        topleft = self._mainSpacePos + self._mainSpaceSize - size
      case 'left':
        size = Vec2Int(widthOrHeight,self._mainSpaceSize.y)
        topleft = self._mainSpacePos.copy()
      case 'right':
        size = Vec2Int(widthOrHeight,self._mainSpaceSize.y)
        topleft = self._mainSpacePos + self._mainSpaceSize - size
    self._borders[direction].append(Subspace(topleft,size))
    self._recalculateMainSpaceSizeAndPosWithRespectToBorders()

  def update(self) -> None:
    self._mainSpaces[self._currentMainSpaceID].update(Input.mpos-self.pos)
    for border in self.active_borders:
      border.update(Input.mpos-self.pos)

  def draw(self,surf:Surface) -> None:
    screen.fill(self.bg_color)
    for v_object in self._visible_elements:
      v_object.draw(self.surf)

  def onQuit(self) -> None:
    pass
'''

class Top_Border(Border):
    def __init__(self,color,draw_need,border_color:tuple = (0,0,0),border_width:int = 0):
      self._color = color
      self._pos = tuple
      self._size = tuple
      self._rect = Rect
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0
      self._border_color = border_color
      self._border_width = border_width
      self._border_exists = 1 if border_width else 0

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
        draw.rect(screen,self._color,self._rect)
        self.onMouseExit()
        if not self._draw_need: return
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
            obj.draw()
        if self._border_exists:
          draw.rect(screen,self._border_color,self._rect,self._border_width)
        display.update(self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()
      if self._border_exists:
        draw.rect(screen,self._border_color,self._rect,self._border_width)

class Left_Border(Border):
    def __init__(self,color,draw_need,border_color:tuple = (0,0,0),border_width:int = 0):
      self._pos = (0,0)
      self._color = color
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0
      self._border_color = border_color
      self._border_width = border_width
      self._border_exists = 1 if border_width else 0

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
        if self._border_exists:
          draw.rect(screen,self._border_color,self._rect,self._border_width)
        display.update(self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for obj in self.__dict__:
        if obj[0] != '_':
          self.__dict__[obj].draw()
      if self._border_exists:
        draw.rect(screen,self._border_color,self._rect,self._border_width)

class Right_Border(Border):
    def __init__(self,color,draw_need,border_color:tuple = (0,0,0),border_width:int = 0):
      self._color = color
      self._pos = tuple
      self._size = tuple
      self._rect = Rect
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0
      self._border_color = border_color
      self._border_width = border_width
      self._border_exists = 1 if border_width else 0

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
        draw.rect(screen,self._color,self._rect)
        self.onMouseExit()
        if not self._draw_need: return
        for object in self.__dict__:
          if object[0] != '_':
            obj = self.__dict__[object]
            if isinstance(obj,Button):
              obj.setToUp()
            obj.draw()
        if self._border_exists:
          draw.rect(screen,self._border_color,self._rect,self._border_width)
        display.update(self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))
      self._pactive = self._active

    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()
      if self._border_exists:
        draw.rect(screen,self._border_color,self._rect,self._border_width)

class Bottom_Border(Border):
    def __init__(self,color,draw_need,border_color:tuple = (0,0,0),border_width:int = 0):
      self._pos = (0,0)
      self._size = (0,0)
      self._color = color
      self._draw_need = draw_need
      self._active = 0
      self._pactive = 0
      self._border_color = border_color
      self._border_width = border_width
      self._border_exists = 1 if border_width else 0

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
        if self._border_exists:
          draw.rect(screen,self._border_color,self._rect,self._border_width)
        display.update(self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          #objInput = [myInput.__getattr__(acceptableInput) for acceptableInput in self.__dict__[object].accepts()]
          self.__dict__[object].update(myInput.get_all(self.__dict__[object].accepts()))
      self._pactive = self._active
    def draw(self):
      draw.rect(screen,self._color,self._rect)
      for object in self.__dict__:
        if object[0] != '_':
          self.__dict__[object].draw()
      if self._border_exists:
        draw.rect(screen,self._border_color,self._rect,self._border_width)
'''

def runInThread(obj:Runnable) -> threading.Thread:
  thread = threading.Thread(target = obj.run)
  thread.daemon = True
  thread.start()
  return thread

def stopThread(thread:threading.Thread,obj:Runnable):
  obj.stop()
  thread.join()

def tick() -> int:
  global fps
  return clock.tick(fps)

def getScreenSize() -> tuple[int,int]:
  return display.get_window_size()


def init(screenSize:tuple[int,int],flags = 0,name:str = '',**kwargs) -> None:
    #nerf miner
    global saved_flags,saved_name,clock
    saved_flags = flags
    saved_name = name
    global screen, running,WIDTH,HEIGHT
    if screenSize == (0,0):
      screenSize = (MONITOR_WIDTH,MONITOR_HEIGHT)
    screen = display.set_mode(screenSize,flags,**kwargs)
    WIDTH,HEIGHT = screenSize
    if name:
      display.set_caption(name)
    running = 1
    clock = pg_time.Clock()

def setMinScreenSize(x:int,y:int) -> None:
    global minScreenX,minScreenY
    minScreenX = x
    minScreenY = y

def getFonts() -> list[str]:
  return font.get_fonts()

def makeFont(FontName,FontSize,Bold:bool = False,Italic:bool = False):
  return font.SysFont(FontName,FontSize,Bold,Italic)

'''
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
  #utmily
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

def setOnSoundLoad(func:Callable) -> None:
  global onSoundLoad
  onSoundLoad = func

def setOnSoundPlay(func:Callable) -> None:
  global onSoundPlay
  onSoundPlay = func

def setSoundEndEvent(func:Callable):
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
'''

def setWindowIcon(surf:Surface) -> None: 
  display.set_icon(surf)

def loadImg(FileName:str,useAlpha:bool = False,usePath:bool = True) -> Surface:
  '''Returns a pygame Surface of image provided with FileName\n
  Use Alpha for Images that should have a transparent background'''
  global PATH
  fullFilePath = '/'.join([PATH,FileName]) if usePath else FileName
  return image.load(fullFilePath).convert_alpha() if useAlpha else image.load(fullFilePath).convert()

def flipSurface(surface:Surface,x:bool,y:bool) -> Surface:
  return transform.flip(surface,x,y) 

def resizeSurface(surface:Surface,newSize:tuple,dest_surf:Surface|None = None) -> Surface:
  return transform.scale(surface,newSize,dest_surf)

def rotateSurface(surface:Surface,angle:float) -> Surface:
  return transform.rotate(surface,angle)

def isValidScreenSize(width:int,height:int) -> bool:
  global minScreenX,minScreenY
  return not (width < minScreenX or height < minScreenY)


def getScreenValidFit(screenWidth:int,screenHeight:int) -> tuple[int,int]:
  '''Returns a valid screen size from input'''
  global minScreenX,minScreenY
  return (max(screenWidth,minScreenX),max(screenHeight,minScreenY))

def getClipboard() -> str:
  for _type in scrap.get_types():
    if CONSTANTS.SCRAP_TEXT in _type:
      clipboard = scrap.get(CONSTANTS.SCRAP_TEXT)
      if clipboard is None:
        return ''
      else:
        return clipboard.decode('utf-8')
  return ''

def updateInput():
  """Returns MouseState and KeyDownQueue, if quit event triggered, returns tuple (False,False)"""
  mbd = [0,0,0]
  mbu = [0,0,0]
  Input.wheel = 0
  Input.KDQueue.clear()
  Input.KUQueue.clear()
  flagsRaised = []
  for event in events.get():
    if event.type == CONSTANTS.QUIT:
      Input.quitEvent = True
    elif event.type == CONSTANTS.KEYDOWN:
      Input.KDQueue.append(event.unicode)
      if event.unicode == unicode.constants.PASTE:
        Input.KDQueue.extend(getClipboard())
    elif event.type == CONSTANTS.KEYUP:
      Input.KUQueue.append(event.unicode)  
    elif event.type == CONSTANTS.MOUSEBUTTONDOWN:
      if event.button < 4:
        mbd[event.button-1] = 1
    elif event.type == CONSTANTS.MOUSEBUTTONUP:
      if event.button < 4: 
        mbu[event.button-1] = 1
    elif event.type == CONSTANTS.MOUSEWHEEL:
      assert isinstance(event.precise_y, int) #for mypy
      Input.wheel = event.precise_y.__trunc__()
    elif event.type == CONSTANTS.VIDEORESIZE:
      global WIDTH,HEIGHT
      WIDTH,HEIGHT = display.get_window_size()
      if not isValidScreenSize(WIDTH,HEIGHT):
        size = WIDTH, HEIGHT = getScreenValidFit(WIDTH,HEIGHT)
        display.set_mode(size,saved_flags)
    flagsRaised.append(event.type)
#hola lola