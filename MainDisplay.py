from asyncore import loop
from distutils.util import subst_vars
from pickle import GLOBAL
from tracemalloc import start
from graphics import *
import time
import os
import math
from pyowm import OWM
from pyowm.utils import config
from pyowm.utils import timestamps
from pyowm.weatherapi25.uris import DAILY_FORECAST_URI
# custom imports 
from datafeeds.WeatherDataFeed import *
from datafeeds.CompassDataFeed import *

startTime = time.time()

try:
   tempArray = getWeather()
except:
   tempArray = {'temp': "?", 'temp_max': "?", 'temp_min': "?", 'feels_like': "?", 'temp_kf': "?"}

#\/----------------- UNCOMMENT THESE BEFORE RUNNING ON RPi **********************************************************************
#from gpiozero import CPUTemperature
#cpu = CPUTemperature()

win = GraphWin("script", 240, 240, autoflush= False)
win.setBackground(color_rgb(0, 0, 0))
#  \/-------- UNCOMMENT THIS BEFORE RUNNING ON RPi ******************************************************************************
#os.system("wmctrl -r script -e 0,198,90,-1,-1") 

#get initial time setting data and set the array
timeArray = time.localtime()
hour = str(timeArray[3] - 12)
minute = str(timeArray [4])
second = str(timeArray [5])
hourInt = 0

def drawCirclePie(x, y, angle, radius, color):
   drawAngle = 0
   while(drawAngle <= angle):
      drawDrawAngle = drawAngle + 90
      tri = Polygon (Point (x,y), Point (x + (math.cos(math.radians(drawDrawAngle)) * radius), y + (math.sin(math.radians(drawDrawAngle)) * radius)), Point (x + (math.cos(math.radians(drawDrawAngle+4)) * radius), y + (math.sin(math.radians(drawDrawAngle+4)) * radius)))
      tri.setFill (color) 
      tri.setOutline (color)
      tri.draw(win)
      drawAngle = drawAngle + 4
   pieCover.draw(win)
   update()

#program to create background and init pie cover
background = Image(Point(120,120), (os.getcwd() + "/images/" + "glassOSBackgroundReal.png"))
background.draw(win)
pieCover = Image(Point(120, 120), (os.getcwd() + "/images/" + "imagefrontreal.png"))

#make text for time (and set color, size, and position [point])
timeText = Text(Point (96, 215), hour + "" + minute + "" + second)
timeText.setTextColor("white")
timeText.setSize(28)
timeText.draw (win)

#make text for time (and set color, size, and position [point])
timeTextSec = Text(Point (146, 219.7), hour + "" + minute + "" + second)
timeTextSec.setTextColor("white")
timeTextSec.setSize(15)
timeTextSec.draw (win)

#make text for weather and check if it errored
if tempArray['temp'] == "?":
   tempText = Text(Point (207, 209), "?" + u"\N{DEGREE SIGN}")
   tempText.setTextColor("white")
   tempText.setSize(24)
   tempText.draw (win)
else:
   tempText = Text(Point (207, 209), str(round(tempArray['temp'])) + u"\N{DEGREE SIGN}")
   tempText.setTextColor("white")
   tempText.setSize(24)
   tempText.draw (win)

#make text for cpu temperature
cpuTempText = Text(Point (205, 32), "load")
cpuTempText.setTextColor("white")
cpuTempText.setSize(16)
cpuTempText.draw (win)

def clearCirclePie(win):
   for item in win.items[:]:
      if "Polygon" in str(item):
         item.undraw()


drawCirclePie (163, 120, 360, 55, "white")

movedForDouble = True
movedForSingle = False

#program to add compass lines
compassLines = Image(Point(158,140), (os.getcwd() + "/images/" + "Compass.png"))
compassLines.draw(win)

#to repeat every 20 milliseconds
def periodicFunctions():
   global movedForDouble
   global movedForSingle
   global compassLines
   global spikeCount

   timeArray = time.localtime()
   
   hourInt = timeArray[3]
   #check if the hour is past 12 and reset
   if (timeArray[3] > 12):
      hourInt = timeArray[3] - 12
      pmOrAm = True
   else:
      pmOrAm = False
   hour = str(hourInt)

   #check if the hour is 0 and set to 12
   if (timeArray[3] == 0):
      hourInt = 12


   #check if the hour is two digits and move seconds (moved for double and single are inverted because im dumb)
   if (hourInt > 9 and (movedForDouble)):
      timeTextSec.move (8, 0)
      movedForDouble = False
      movedForSingle = True
   elif(hourInt < 9 and (movedForSingle)):
      timeTextSec.move (-8, 0)
      movedForDouble = True
      movedForSingle = False

   hour = str(hourInt)
   
   minute = (timeArray [4])
   second = (timeArray [5])
   
   #add a 0 to seconds or minutes if they only have a single digit
   if (second < 10):
      second = str(timeArray [5])
      second = "0" + second
   else:
      second = str(timeArray [5])

   if (minute < 10):
      minute = str(timeArray [4])
      minute = "0" + minute
   else:
      minute = str(timeArray [4])

   timeText.setText (hour + ":" + minute)
   timeTextSec.setText (second)

   #  \/-------- UNCOMMENT THIS BEFORE RUNNING ON RPi ******************************************************************************
   #cpuTempText.setText(round(cpu.temperature, 1))
   cpuTempText.setText(50.6)
   
   update()

   #close program on click
   if (win.checkMouse() != None):
      print ("Program runtime: " + str(time.time()-startTime) + " seconds")
      exit()

   compassLines.undraw()
   compassHeading = CDFupdateCompass()
   compassLines = Image(Point((158 - ((compassHeading % 5) * 11)),113), (os.getcwd() + "/images/" + "Compass.png"))
   compassLines.draw(win)

#to repeat every 10 seconds (like api updates can go here)
def tenSecondFunctions():
   print ("ran 10 second functions")

nextRunTime = time.time()

spikeCount = 0

while True:
   
   periodicFunctions()

   #if the time has passed 10 seconds from the last check, run the 10 second functions
   if time.time() > nextRunTime:
      tenSecondFunctions()
      nextRunTime = nextRunTime + 10