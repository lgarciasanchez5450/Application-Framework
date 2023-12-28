import framework as fw

fw.init((100,100),name = 'funky monkey')
ws = fw.WindowSpace()


titleScreen = fw.TitleScreen(fw.Vec2Int(0,0),fw.Vec2Int(100,100))
thread = fw.runInThread(titleScreen)
#load image
#load image
#create thingys
fw.time.sleep(10)

fw.stopThread(thread,titleScreen)
