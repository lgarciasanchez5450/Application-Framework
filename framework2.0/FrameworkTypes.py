from typing import Protocol, Callable, Literal, TypeAlias,Final, Generic,TypeVar,ParamSpec,Concatenate
from vector import Vec2Int
from pygame import Surface

BorderDirecton:TypeAlias = Literal['top','bottom','left','right']

class SupportsUpdate(Protocol):
  def update(self,mpos:Vec2Int): ...
  
class SupportsDraw(Protocol):
  def draw(self,surf:Surface): ...

class SupportsQuit(Protocol):
  def onQuit(self): ...

class Runnable(Protocol):
  def run(self): ...
  def stop(self): ...