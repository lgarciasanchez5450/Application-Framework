from FrameworkTypes import *
import time


def profile(framesIdle:int):
  def inner(object):
    assert hasattr(object,'draw') and callable(object.draw)
    frameCount = 0
    frameTimes = []
    def draw(self,surf:Surface):
      nonlocal frameCount
      frameCount += 1
      if frameCount % framesIdle == 0:
        frameTimes.append(time.perf_counter())
      return object._inner_draw(self,surf)
    def onQuit(self):
      if len(frameTimes) < 2:
        print('Insufficient information for debugger')
        return
      FPSlist = [framesIdle/(frameTimes[x+1]-frameTimes[x]) for x in range(len(frameTimes)-1)]
      from matplotlib import pyplot
      pyplot.plot(tuple(FPSlist))
      FPSlist.sort()
      average = sum(FPSlist) / len(FPSlist)
      print(f'Avg FPS: {round(average,2)}')
      print(f'Min FPS: {round(FPSlist[0],2)}')
      print(f'Max FPS: {round(FPSlist[-1],2)}')
      print(f'Total Frame s Updated: {frameCount}')
      pyplot.show()
      try:
        return object.onQuit() # type: ignore  because onQuit might not be defined 
      except:
        return None
    object._inner_draw = object.draw
    object.draw = draw
    object.onQuit = onQuit #type: ignore
    return object
  return inner
