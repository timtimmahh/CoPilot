import sys
import datetime
import time
import subprocess
import glob
import math
import pickle
import os
import operator

import settings
from utils import is_rpi, ip_addresses
import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.gridlayout import GridLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.slider import Slider
from kivy.uix.switch import Switch
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.widget import Widget
from kivy.graphics import Line
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from math import cos, sin, pi
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ListProperty, ObjectProperty
from kivy.uix.label import Label
from kivy.logger import Logger
from kivy.uix.screenmanager import ScreenManager, Screen, NoTransition, SlideTransition
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.uix.scatter import Scatter
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.image import AsyncImage
from kivy.metrics import dp
from kivymd.button import MDIconButton
from kivymd.label import MDLabel
from kivymd.list import ILeftBody, ILeftBodyTouch, IRightBodyTouch
from kivymd.theming import ThemeManager
from kivymd.dialog import MDDialog
import kivymd.snackbar as Snackbar

try:
    import RPi.GPIO as GPIO

    # import serial
    test_environment = False
except (ImportError, RuntimeError):
    test_environment = True

# 10/20/2017
#Created by Joel Zeller
#
#  1/25/2019
# Modified by Timothy Logan

global version
global name
global width
global height
global fullscreen
global window_state
global auto_brightness_enabled
global default_brightness_level
global night_light_enabled
global night_light_start_time
global night_light_end_time
global night_light_brightness_level

version, name, \
width, height, fullscreen, window_state, \
auto_brightness_enabled, default_brightness_level, \
night_light_enabled, night_light_start_time, night_light_end_time, night_light_brightness_level \
    = [value for section, options in settings.get_all_config_options().items() for value in options.values()]
printenvs = "%s %s %d %d %s %s %d %d %d %d %d %d" % (version, name, width, height, fullscreen, window_state,
                                                     auto_brightness_enabled, default_brightness_level,
                                                     night_light_enabled, night_light_start_time, night_light_end_time,
                                                     night_light_brightness_level)
from kivy.config import Config

Config.set('graphics', 'width', width)
Config.set('graphics', 'height', height)
Config.set('graphics', 'fullscreen', fullscreen)
Config.set('graphics', 'window_state', window_state)

from kivy.core.window import Window

Window.size = (width, height)

global ip
ip = ip_addresses
global devtaps
devtaps = 0
# ---------------------------------------


#_____________________________________________________________
#GPIO SETUP

#name GPIO pins
seekupPin = 13
seekdownPin = 19
auxPin = 16
amfmPin = 26
garagePin = 20
radarPin = 21
ledsPin = 5
driverwindowdownPin = 17  
driverwindowupPin = 15 
passwindowdownPin = 27 
passwindowupPin = 18 

HotKey1Pin = 12
HotKey2Pin = 6

if is_rpi:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(seekupPin, GPIO.OUT)
    GPIO.setup(seekdownPin, GPIO.OUT)
    GPIO.setup(auxPin, GPIO.OUT)
    GPIO.setup(amfmPin, GPIO.OUT)
    GPIO.setup(garagePin, GPIO.OUT)
    GPIO.setup(radarPin, GPIO.OUT)
    GPIO.setup(ledsPin, GPIO.OUT)
    GPIO.setup(driverwindowdownPin, GPIO.OUT)
    GPIO.setup(driverwindowupPin, GPIO.OUT)
    GPIO.setup(passwindowdownPin, GPIO.OUT)
    GPIO.setup(passwindowupPin, GPIO.OUT)

    GPIO.setup(HotKey1Pin, GPIO.IN)
    GPIO.setup(HotKey2Pin, GPIO.IN)

#initial state of GPIO

    GPIO.output(seekupPin, GPIO.HIGH)
    GPIO.output(seekdownPin, GPIO.HIGH)
    GPIO.output(auxPin, GPIO.HIGH)
    GPIO.output(amfmPin, GPIO.HIGH)
    GPIO.output(garagePin, GPIO.HIGH)
    GPIO.output(radarPin, GPIO.HIGH)
    GPIO.output(ledsPin, GPIO.LOW)
    GPIO.output(driverwindowdownPin, GPIO.HIGH)
    GPIO.output(driverwindowupPin, GPIO.HIGH)
    GPIO.output(passwindowdownPin, GPIO.HIGH)
    GPIO.output(passwindowupPin, GPIO.HIGH)

    # global AccelPresent #set to 1 if adxl345 accelerometer is present
    # AccelPresent = 1
    #
    # global accelxmaxpos
    # global accelxmaxneg
    # global accelymaxpos
    # global accelymaxneg
    # accelxmaxpos = 0
    # accelxmaxneg = 0
    # accelymaxpos = 0
    # accelymaxneg = 0
    # if AccelPresent == 1:
    #     try:
    #         from adxl345 import ADXL345
    #         adxl345 = ADXL345()
    #     except:
    #         print("Failed to initialize accelerometer.")
    #
    #         AccelPresent = 0
    # global ACCELON
    # ACCELON = 0

    # if is_rpi:
    os.system('pulseaudio --start') #start the pulseaudio daemon

global bluetoothdevicemac
bluetoothdevicemac = 'AC_37_43_D7_65_B4' #Enter your smartphones bluetooth mac address here so its audio can be controlled from the audio app
#iphone: F0_D1_A9_C9_86_3E
#HTCM8: 2C_8A_72_19_0F_F4
#HTC10: AC_37_43_D7_65_B4
global BLUETOOTHON
BLUETOOTHON = 1
global DISPLAYBTDATA
DISPLAYBTDATA = 0
global bluetoothdata
bluetoothdata = ['','','','','','','','','','','',''] #Default - only shown when bluetooth enabled

#_________________________________________________________________
#VARIABLES

#varibles from text file:
global theme
global wallpaper
global hotkey1string
global hotkey2string

f = open('savedata.txt', 'r+') # read from text file
theme = f.readline()
theme = theme.rstrip() #to remove \n from string
wallpaper = int(f.readline())
hotkey1string = f.readline()
hotkey1string = hotkey1string.rstrip()
hotkey2string = f.readline()
hotkey2string = hotkey2string.rstrip()
f.close()

global SEEKUPON 
SEEKUPON = 0

global SEEKDOWNON 
SEEKDOWNON = 0

global AUXON 
AUXON = 0

global AMFMON 
AMFMON = 0

global GARAGEON 
GARAGEON = 0

global RADARON 
RADARON = 0

global clock
clock = 0

global analog
analog = 1

global message
message = 0

global swminute
swminute = 0

global swsecond
swsecond = 0

global swtenth
swtenth = 0

global swactive
swactive = 0

global swstring
swstring = 0

global testvar
testvar = 0

global testvar2
testvar2 = 0

global screenon
screenon = 1

global clocktheme
clocktheme = 2

global launch_start_time
launch_start_time = 0

global animation_start_time
animation_start_time = 0

global time_second_mod
time_second_mod = 0

#__________________________________________________________________
#HOTKEY STUFF

def HotKey1(channel):
    global hotkey1string
    global screenon
    if hotkey1string == "Seek Up":
        if BLUETOOTHON == 0:
            Clock.schedule_once(seekup_callback)
            Clock.schedule_once(seekup_callback,.1)
        if BLUETOOTHON == 1:
            try:
                os.system('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_'+bluetoothdevicemac+'/player0 org.bluez.MediaPlayer1.Next')
            except:
                print("can't next")
    if hotkey1string == "Seek Down":
        if BLUETOOTHON == 0:
            Clock.schedule_once(seekdown_callback)
            Clock.schedule_once(seekdown_callback,.1)
        if BLUETOOTHON == 1:
            try:
                os.system('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_'+bluetoothdevicemac+'/player0 org.bluez.MediaPlayer1.Previous')
            except:
                print("can't prev")
    if hotkey1string == "Garage":
        Clock.schedule_once(garage_callback)
        Clock.schedule_once(garage_callback,.1)
    if hotkey1string == "Radar":
        Clock.schedule_once(radar_callback)
    if hotkey1string == "Screen Toggle":
        if screenon == 1:
            os.system("sudo echo 1 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen off
            screenon = 0
            return
        if screenon == 0:
            os.system("sudo echo 0 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen on
            screenon = 1
            return
    if hotkey1string == "None":
        return
    

def HotKey2(channel):
    global hotkey2string
    global screenon
    if hotkey2string == "Seek Up":
        if BLUETOOTHON == 0:
            Clock.schedule_once(seekup_callback)
            Clock.schedule_once(seekup_callback, .1)
        if BLUETOOTHON == 1:
            try:
                os.system('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_' + bluetoothdevicemac + '/player0 org.bluez.MediaPlayer1.Next')
            except:
                print("can't next")
    if hotkey2string == "Seek Down":
        if BLUETOOTHON == 0:
            Clock.schedule_once(seekdown_callback)
            Clock.schedule_once(seekdown_callback, .1)
        if BLUETOOTHON == 1:
            try:
                os.system('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_' + bluetoothdevicemac + '/player0 org.bluez.MediaPlayer1.Previous')
            except:
                print("can't prev")
    if hotkey2string == "Garage":
        Clock.schedule_once(garage_callback)
        Clock.schedule_once(garage_callback,.1)
    if hotkey2string == "Radar":
        Clock.schedule_once(radar_callback)
    if hotkey2string == "Screen Toggle":
        if screenon == 1:
            os.system("sudo echo 1 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen off
            screenon = 0
            return
        if screenon == 0:
            os.system("sudo echo 0 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen on
            screenon = 1
            return
    if hotkey2string == "None":
        return


if is_rpi:
    GPIO.add_event_detect(HotKey1Pin, GPIO.FALLING, callback=HotKey1, bouncetime=500)
    GPIO.add_event_detect(HotKey2Pin, GPIO.FALLING, callback=HotKey2, bouncetime=500)

#__________________________________________________________________
#DEFINE CLASSES

#ROOT CLASSES

class ROOT(FloatLayout):
    pass
class QUICKEYSLayout(FloatLayout):
    pass

        #MAIN SCREEN CLASSES

class MainScreen(Screen):
    pass
class AudioScreen(Screen):
    pass
class PerfScreen(Screen):
    pass
class AppsScreen(Screen):
    pass
class ControlsScreen(Screen):
    pass
class SettingsScreen(Screen):
    pass
class KillScreen(Screen):
    pass

        #APP SCREEN CLASSES

class PaintScreen(Screen):
    pass
class FilesScreen(Screen):
    pass
class LogoScreen(Screen):
    pass
class ClockChooserScreen(Screen):
    pass
class ClassicClockScreen(Screen):
    pass
class SportClockScreen(Screen):
    pass
class ExecutiveClockScreen(Screen):
    pass
class DayGaugeClockScreen(Screen):
    pass
class NightGaugeClockScreen(Screen):
    pass
class WormsClockScreen(Screen):
    pass
class InfoClockScreen(Screen):
    pass
class PhotoClockScreen(Screen):
    pass
class TestAppScreen(Screen):
    pass
class MaintenanceScreen(Screen):
    pass


# class MaintenanceSetOilInfoScreen(Screen):
#     pass
class GPSScreen(Screen):
    pass
class StopwatchScreen(Screen):
    pass
class DiagnosticsScreen(Screen):
    pass
class SystemDebugScreen(Screen):
    pass
class WindowDebugScreen(Screen):
    pass
class LaunchControlSetupScreen(Screen):
    pass
class LaunchControlScreen(Screen):
    pass
class PhotosScreen(Screen):
    pass


# class GaugeSelectScreen(Screen):
#     pass
# class OBDTachsScreen(Screen):
#     pass
# class OBDSpeedosScreen(Screen):
#     pass
# class OBDDiagnosticsScreen(Screen):
#     pass
# class GaugeSelectScreen(Screen):
#     pass
# class GaugeSelectScreen(Screen):
#     pass
# class OBDDigitalSpeedoScreen(Screen):
#     pass
# class OBDDigitalTachScreen(Screen):
#     pass
# class OBDGraphicTachScreen(Screen):
#     pass
# class OBDGraphicTach2Screen(Screen):
#     pass
# class OBDCoolantScreen(Screen):
#     pass
# class OBDIntakeTempScreen(Screen):
#     pass
# class OBDLoadScreen(Screen):
#     pass
# class OBDThrottlePosScreen(Screen):
#     pass
# class OBDIntakePressureScreen(Screen):
#     pass
# class OBDSettingsScreen(Screen):
#     pass
# class AccelerometerScreen(Screen):
#     pass
class NOSScreen(Screen):
    pass
class WallpaperSelectScreen(Screen):
    pass
class HotKey1ChooserScreen(Screen):
    pass
class HotKey2ChooserScreen(Screen):
    pass
class OffScreen(Screen):
    pass

#APP CLASSES
class Painter(Widget): #Paint App
    
    def on_touch_down(self, touch):
        with self.canvas:
            touch.ud["line"] = Line(points=(touch.x, touch.y))

    def on_touch_move(self, touch):
        touch.ud["line"].points += [touch.x, touch.y]

#_________________________________________________________________
#MAINAPP

class MainApp(App):
    theme_cls = ThemeManager()
    version = StringProperty()
    timenow = StringProperty()
    timenow_hour = NumericProperty(0)
    timenow_minute = NumericProperty(0)
    timenow_second = NumericProperty(0)
    launch_start_time = NumericProperty(0)
    time_second_mod = NumericProperty(0)
    datenow = StringProperty()
    daynow = StringProperty()
    yearnow = StringProperty()
    ampm = StringProperty()
    tempnow = StringProperty()
    CPUtempnow = StringProperty()
    corevoltagenow = StringProperty()
    stopwatchnow = StringProperty()
    stopwatchsecnow = ObjectProperty()
    stopwatchmilnow = ObjectProperty()
    HKonenow = StringProperty()
    HKtwonow = StringProperty()
    radariconsource = StringProperty()
    lightsiconsource = StringProperty()
    wallpapernow = StringProperty()
    ip = StringProperty()
    bluetoothtitle = StringProperty()
    bluetoothartist = StringProperty()
    bluetoothduration = NumericProperty(0)
    bluetoothprogress = NumericProperty(0)


    theme_cls.theme_style = "Dark"
    #theme_cls.primary_palette = "Indigo"
    global theme
    theme_cls.primary_palette = theme

    def updatetime(self, *args):
        time = datetime.datetime.now()
        time_hour = time.strftime("%I")  # time_hour
        if time_hour[0] == "0":  # one digit format
            time_hour = " " + time_hour[1]
        time_minute = time.strftime("%M")  # time_minute
        timenow = time_hour + ":" + time_minute  # create sting format (hour:minute)
        self.timenow = timenow
        #self.timenow = "3:14" # for screenshots
        self.timenow_hour = time.hour
        self.timenow_minute = time.minute
        self.timenow_second = time.second


        global time_second_mod
        time_second_mod = int(float(time_second_mod)) + 1
        if time_second_mod > 10000000:  # doesnt allow this var to get too big
            time_second_mod = 0
        self.time_second_mod = time_second_mod
        global launch_start_time
        self.launch_start_time = launch_start_time

    def updatedate(self, *args):
        day = time.strftime("%A") #current day of week
        month = time.strftime("%B") #current month
        date = time.strftime("%d")  #current day of month
        year = time.strftime("%Y")  #current year
        ampm = time.strftime("%p")  #AM or PM
        if date[0] == "0":  # one digit format for day of month
            date = " " + date[1]
        datenow = month + " " + date
        self.datenow = datenow
        self.daynow = day
        self.yearnow = year
        self.ampm = ampm

    def updatevariables(self, *args):
        global swminute
        global swsecond
        global swtenth
        global swactive
        global swstring
        global swminutestring
        global swsecondstring
        global version
        global devtaps
        # global OBDpage
        if swactive == 1:
            swtenth += 1
            if swtenth == 10:
                swtenth = 0
                swsecond += 1
            if swsecond == 60:
                swsecond = 0
                swminute += 1

        # fortmatting for stopwatch display - outside of if statement because watch will run in background
        if swsecond < 10:
            swsecondstring = "0" + str(swsecond)
        else:
            swsecondstring = str(swsecond)
        if swminute < 10:
            swminutestring = "0" + str(swminute)
        else:
            swminutestring = str(swminute)
        swstring = (swminutestring + ":" + swsecondstring + ":" + str(swtenth) + "0")
        #set vars
        self.stopwatchnow = swstring
        self.stopwatchsecnow = swsecond + (swtenth*.1)
        self.HKonenow = hotkey1string
        self.HKtwonow = hotkey2string
        self.version = version
        self.ip = ip
        self.devtaps = devtaps

        global BLUETOOTHON
        if BLUETOOTHON == 1:
            if int(float(animation_start_time)) + 5 <= int(float(time_second_mod)):
                try:
                    if DISPLAYBTDATA == 1:
                        bluetoothdataraw = os.popen('dbus-send --system --type=method_call --print-reply --dest=org.bluez /org/bluez/hci0/dev_' + bluetoothdevicemac + '/player0 org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:Track').read()
                        bluetoothduration = int((bluetoothdataraw.split("uint32"))[1].split('\n')[0])

                        bluetoothprogressraw = os.popen('dbus-send --system --type=method_call --print-reply --dest=org.bluez /org/bluez/hci0/dev_' + bluetoothdevicemac + '/player0 org.freedesktop.DBus.Properties.Get string:org.bluez.MediaPlayer1 string:Position').read()
                        bluetoothprogress = int((bluetoothprogressraw.split("uint32"))[1].split('\n')[0])

                        bluetoothdata = bluetoothdataraw.split('"')[1::2]  # takes string and finds things in quotes
                        self.bluetoothtitle = bluetoothdata[1]
                        self.bluetoothartist = bluetoothdata[7]
                        self.bluetoothduration = bluetoothduration
                        self.bluetoothprogress = bluetoothprogress
                    else:
                        self.bluetoothtitle = ''
                        self.bluetoothartist = ''
                        self.bluetoothduration = 0
                        self.bluetoothprogress = 0
                except:
                    self.bluetoothtitle = ''
                    self.bluetoothartist = ''
                    self.bluetoothduration = 0
                    self.bluetoothprogress = 0
        if BLUETOOTHON == 0: #show nothing when bluetooth is off
            self.bluetoothtitle = ''
            self.bluetoothartist = ''
            self.bluetoothduration = 0
            self.bluetoothprogress = 0

        global theme
        theme = self.theme_cls.primary_palette
        if RADARON == 1:
            self.radariconsource = 'data/icons/radarindicator.png'
        if RADARON == 0:
            self.radariconsource = 'data/icons/null.png'
        if wallpaper == 0:
            self.wallpapernow = 'data/wallpapers/greenmaterial.png'
        if wallpaper == 1:
            self.wallpapernow = 'data/wallpapers/blackgreenmaterial.png'
        if wallpaper == 2:
            self.wallpapernow = 'data/wallpapers/darkgreymaterial2.png'
        if wallpaper == 3:
            self.wallpapernow = 'data/wallpapers/polymountain.png'
        if wallpaper == 4:
            self.wallpapernow = 'data/wallpapers/trianglematerial.png'
        if wallpaper == 5:
            self.wallpapernow = 'data/wallpapers/blackredmaterial.png'
        if wallpaper == 6:
            self.wallpapernow = 'data/wallpapers/greybluematerial.png'
        if wallpaper == 7:
            self.wallpapernow = 'data/wallpapers/lightblueblackmaterial.png'
        if wallpaper == 8:
            self.wallpapernow = 'data/wallpapers/greyplain.png'
        if wallpaper == 9:
            self.wallpapernow = 'data/wallpapers/stopwatchblue.png'
        if wallpaper == 10:
            self.wallpapernow = 'data/wallpapers/polycube.png'
        if wallpaper == 11:
            self.wallpapernow = 'data/wallpapers/polyvalley.png'
        if wallpaper == 12:
            self.wallpapernow = 'data/wallpapers/purplebluematerial.png'
        if wallpaper == 13:
            self.wallpapernow = 'data/wallpapers/bluegreymaterial.png'
        if wallpaper == 14:
            self.wallpapernow = 'data/wallpapers/redpurplematerial.png'
        if wallpaper == 15:
            self.wallpapernow = 'data/wallpapers/CoPilot_Wallpaper_2.png'
        if wallpaper == 16:
            self.wallpapernow = 'data/wallpapers/blackredmaterial2.png'
        if wallpaper == 17:
            self.wallpapernow = 'data/wallpapers/androidauto.png'
        if wallpaper == 18:
            self.wallpapernow = 'data/wallpapers/tealmaterialdesign.png'
        if wallpaper == 19:
            self.wallpapernow = 'data/wallpapers/blueblackmaterial.png'
        if wallpaper == 20:
            self.wallpapernow = 'data/wallpapers/greenmaterial2.png'
        if wallpaper == 21:
            self.wallpapernow = 'data/wallpapers/redbluematerial.png'
        if wallpaper == 22:
            self.wallpapernow = 'data/wallpapers/blueblackwhitematerial.png'
        if wallpaper == 23:
            self.wallpapernow = 'data/wallpapers/polymountain2.png'
        if wallpaper == 24:
            self.wallpapernow = 'data/wallpapers/blackpoly.png'
        if wallpaper == 25:
            self.wallpapernow = 'data/wallpapers/blackredlacematerial.png'
        if wallpaper == 26:
            self.wallpapernow = 'data/wallpapers/blueredpoly.png'
        if wallpaper == 27:
            self.wallpapernow = 'data/wallpapers/firewaterpoly.png'
        if wallpaper == 28:
            self.wallpapernow = 'data/wallpapers/tanbluepoly.png'
        if wallpaper == 29:
            self.wallpapernow = 'data/wallpapers/road.png'
        if wallpaper == 30:
            self.wallpapernow = 'data/wallpapers/road2.png'
        if wallpaper == 31:
            self.wallpapernow = 'data/wallpapers/pixel.png'
        if wallpaper == 32:
            self.wallpapernow = 'data/wallpapers/pixel2.png'
        if wallpaper == 33:
            self.wallpapernow = 'data/wallpapers/darkgreyplain.png'
        if wallpaper == 34:
            self.wallpapernow = 'data/wallpapers/city.png'
        if wallpaper == 35:
            self.wallpapernow = 'data/wallpapers/cincy.png'

    def updatemessage(self, *args):
        # the logic for what the message says
        if message == 0:
            self.text = " "
        if message == 1:  # used for displaying the CPU temp
            if is_rpi:
                temperaturestring = subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_temp"])
                corevoltagestring = subprocess.check_output(["/opt/vc/bin/vcgencmd", "measure_volts core"])
                temperature = (temperaturestring.split('=')[1][:-3])
                corevoltage = (corevoltagestring.split('=')[1][:-3])
                CPUtempnow = temperature + u'\N{DEGREE SIGN}' + "C"
                corevoltagenow = corevoltage + " V"
            if developermode == 0:
                CPUtempnow = "40" + u'\N{DEGREE SIGN}' + "C"
                corevoltagenow = "3.14" + " V"
            self.CPUtempnow = CPUtempnow
            self.corevoltagenow = corevoltagenow

    #
    # def updateaccel(self, *args):
    #     global ACCELON
    #     global accelxmaxpos
    #     global accelxmaxneg
    #     global accelymaxpos
    #     global accelymaxneg
    #     if ACCELON == 1:
    #         if AccelPresent == 1:
    #             axes = adxl345.getAxes(True)
    #             accelx = axes['x'] - .13  # compensation amount
    #             self.accelx = accelx
    #             accely = axes['y'] - .34  # compensation amount
    #             self.accely = accely
    #
    #             if accelx > accelxmaxpos:
    #                 accelxmaxpos = accelx
    #             if accelx < accelxmaxneg:
    #                 accelxmaxneg = accelx
    #             if accely > accelymaxpos:
    #                 accelymaxpos = accely
    #             if accely < accelymaxneg:
    #                 accelymaxneg = accely
    #
    #             self.accelxmaxpos = accelxmaxpos
    #             self.accelxmaxneg = accelxmaxneg
    #             self.accelymaxpos = accelymaxpos
    #             self.accelymaxneg = accelymaxneg
    #
    #     if ACCELON == 0:
    #         self.accelx = 0
    #         self.accely = 0
    #         self.accelxmaxpos = accelxmaxpos
    #         self.accelxmaxneg = accelxmaxneg
    #         self.accelymaxpos = accelymaxpos
    #         self.accelymaxneg = accelymaxneg

    def build(self):
        global developermode
        KVFILE = Builder.load_file("main.kv")
        global root
        root = ROOT()

        Clock.schedule_interval(self.updatetime, .1)
        Clock.schedule_interval(self.updatedate, 1)
        # Clock.schedule_interval(self.updatetemp, 1)
        Clock.schedule_interval(self.updatevariables, .104556) #weird number to get RPi stopwatch as close as possible - found through testing
        Clock.schedule_interval(self.updatemessage, 1)
        #        Clock.schedule_interval(self.updateaccel, .1)
        #add the widgets
        
        root.add_widget(KVFILE) #adds the main GUI
        return root

#Some KivyMD Stuff
    def show_easter_dialog(self):
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="Congrats! You found this easter egg!\n\n"
                               "Thanks for trying out CoPilot!  :)",
                          valign='top')

        content.bind(size=content.setter('text_size'))
        self.dialog = MDDialog(title="Easter Egg!",
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=False)

        self.dialog.add_action_button("Dismiss",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    def show_indev_dialog(self):
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="This feature is currently in development.\n\n"
                               "Thanks for trying out CoPilot!  :)",
                          valign='top')

        content.bind(size=content.setter('text_size'))
        self.dialog = MDDialog(title="Coming soon!",
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=False)

        self.dialog.add_action_button("Dismiss",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    def show_version_dialog(self):
        content = MDLabel(font_style='Body1',
                          theme_text_color='Secondary',
                          text="Created by Joel Zeller\n\n"
                               "Please send any bugs to joelzeller25@hotmail.com",
                          valign='top')

        content.bind(size=content.setter('text_size'))
        self.dialog = MDDialog(title="CoPilot "+version,
                               content=content,
                               size_hint=(.8, None),
                               height=dp(200),
                               auto_dismiss=False)

        self.dialog.add_action_button("Dismiss",
                                      action=lambda *x: self.dialog.dismiss())
        self.dialog.open()

    def show_example_snackbar(self, snack_type):
        if devtaps == 4:
            if snack_type == 'enabledev':
                Snackbar.make("Developer Mode Enabled")
        # elif snack_type == 'button':
        #     Snackbar.make("This is a snackbar", button_text="with a button!",
        #                   button_callback=lambda *args: 2)
        # elif snack_type == 'verylong':
        #     Snackbar.make("This is a very very very very very very very long "
        #                   "snackbar!",
        #                   button_text="Hello world")


#SCHEDUALING

        #AUDIO

    def bluetoothplay_callback_schedge(obj):
        if BLUETOOTHON == 1:
            try:
                os.system('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_'+bluetoothdevicemac+'/player0 org.bluez.MediaPlayer1.Play')
                #subprocess.call('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_' + bluetoothdevicemac + '/player0 org.bluez.MediaPlayer1.Play') #doesnt work right now...
                #maybe try this: subprocess.call('sudo shutdown now', shell=True)

            except:
                print("can't play")

    def bluetoothpause_callback_schedge(obj):
        if BLUETOOTHON == 1:
            try:
                os.system('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_'+bluetoothdevicemac+'/player0 org.bluez.MediaPlayer1.Pause')
            except:
                print("can't pause")

    def seekup_callback_schedge(obj):
        if BLUETOOTHON == 0:
            Clock.schedule_once(seekup_callback)
            Clock.schedule_once(seekup_callback, 0.1) #on for .1 secs, then off again
        if BLUETOOTHON == 1:
            try:
                os.system('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_'+bluetoothdevicemac+'/player0 org.bluez.MediaPlayer1.Next')
            except:
                print("can't next")

    def seekdown_callback_schedge(obj):
        if BLUETOOTHON == 0:
            Clock.schedule_once(seekdown_callback)
            Clock.schedule_once(seekdown_callback, 0.1) #on for .1 secs, then off again
        if BLUETOOTHON == 1:
            try:
                os.system('dbus-send --system --type=method_call --dest=org.bluez /org/bluez/hci0/dev_'+bluetoothdevicemac+'/player0 org.bluez.MediaPlayer1.Previous')
            except:
                print("can't prev")

    def aux_callback_schedge(obj):
        Clock.schedule_once(aux_callback)
        Clock.schedule_once(aux_callback, 0.1) #on for .1 secs, then off again

    def amfm_callback_schedge(obj):
        Clock.schedule_once(amfm_callback) 
        Clock.schedule_once(amfm_callback, 0.1) #on for .1 secs, then off again

    def enablebluetooth(obj):
        global BLUETOOTHON
        BLUETOOTHON = 1

    def disablebluetooth(obj):
        global BLUETOOTHON
        BLUETOOTHON = 0

    def displaybtdata(obj):
        global DISPLAYBTDATA
        DISPLAYBTDATA = 1
        global animation_start_time
        animation_start_time = int(float(time_second_mod))  # sets a reference time for animations

    def killbtdata(obj):
        global DISPLAYBTDATA
        DISPLAYBTDATA = 0

        #CONTROLS

    def garage_callback_schedge(obj):
        Clock.schedule_once(garage_callback) #called once - setup to only activate when button is down

    def radar_callback_schedge(obj):
        Clock.schedule_once(radar_callback) #called once so next press alternates status

    def leds_callback_schedge(obj):
        Clock.schedule_once(leds_callback) #called once so next press alternates status

#VARIBLE SETTINGS
    def add_launch(obj): #use on_release: app.add_launchanalog() to call - used to create the lights on the xmas tree drag lights
        global time_second_mod
        global launch_start_time
        launch_start_time = int(float(time_second_mod)) #sets a reference time for launch control timing

    def killtemp(obj):  # used to kill the temp label when on screens other than main
        global TEMPON
        TEMPON = 0

    #messages
    def kill_message(obj): #use on_release: app.kill_message() to call
        global message
        message = 0
        
    def add_message(obj): #use on_release: app.add_message() to call
        global message
        message = 1

    def update_IP(obj): #updates IP address on button tap in System Diagnostics
        global ip
        try:
            ip = ip_addresses()
        except:
            ip = "No IP address found..."

    #stopwatch button functions
    def stopwatch_start(obj): #use on_release: app.stopwatch_start() to call
        global swactive
        swactive = 1
    def stopwatch_stop(obj): #use on_release: app.stopwatch_start() to call
        global swactive
        swactive = 0
    def stopwatch_reset(obj): #use on_release: app.stopwatch_start() to call
        global swactive
        global swminute
        global swsecond
        global swtenth
        swactive = 0
        swminute = 0
        swsecond = 0
        swtenth = 0

    #hot key 1 settings functions
    def sethotkey1_SeekUp(obj):
        global hotkey1string
        hotkey1string = "Seek Up"
    def sethotkey1_SeekDown(obj):
        global hotkey1string
        hotkey1string = "Seek Down"
    def sethotkey1_Garage(obj):
        global hotkey1string
        hotkey1string = "Garage"
    def sethotkey1_Radar(obj):
        global hotkey1string
        hotkey1string = "Radar"
    def sethotkey1_ScreenToggle(obj):
        global hotkey1string
        hotkey1string = "Screen Toggle"
    def sethotkey1_None(obj):
        global hotkey1string
        hotkey1string = "None"

    #hot key 2 settings functions
    def sethotkey2_SeekUp(obj):
        global hotkey2string
        hotkey2string = "Seek Up"
    def sethotkey2_SeekDown(obj):
        global hotkey2string
        hotkey2string = "Seek Down"
    def sethotkey2_Garage(obj):
        global hotkey2string
        hotkey2string = "Garage"
    def sethotkey2_Radar(obj):
        global hotkey2string
        hotkey2string = "Radar"
    def sethotkey2_ScreenToggle(obj):
        global hotkey2string
        hotkey2string = "Screen Toggle"
    def sethotkey2_None(obj):
        global hotkey2string
        hotkey2string = "None"

    def sethotkeydefaults(obj):
        global hotkey1string
        global hotkey2string
        hotkey1string = "None"
        hotkey2string = "None"

    def setwallpaper(obj,wallpapernum):
        global wallpaper
        wallpaper = wallpapernum

    def devtap(obj):
        global devtaps
        global developermode
        if devtaps <= 4:
            devtaps = devtaps + 1
        if devtaps == 5:            # five taps on the settings title will enter dev mode
            developermode = 1

    def killdev(obj):
        global devtaps
        global developermode
        developermode = 0
        devtaps = 0

    def save(obj):
        # save new varibles for next boot
        global theme
        global wallpaper
        global hotkey1string
        global hotkey2string
        wallpaper = str(wallpaper)
        f = open('savedata.txt', 'r+')
        f.truncate() # wipe everything
        f.write(theme + "\n" + wallpaper + "\n" + hotkey1string + "\n" + hotkey2string)
        f.close()

    def shutdown(obj):
        # save new varibles for next boot
        global theme
        global wallpaper
        global hotkey1string
        global hotkey2string
        wallpaper = str(wallpaper)
        f = open('savedata.txt', 'r+')
        f.truncate() # wipe everything
        f.write(theme + "\n" + wallpaper + "\n" + hotkey1string + "\n" + hotkey2string)
        f.close()

        # turn off screen and shutdown
        os.system("sudo echo 1 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen off
        os.system("sudo shutdown -h now")

    def reboot(obj):
        # save new varibles for next boot
        global theme
        global wallpaper
        global hotkey1string
        global hotkey2string
        wallpaper = str(wallpaper)
        f = open('savedata.txt', 'r+')
        f.truncate()
        f.write(theme + "\n" + wallpaper + "\n" + hotkey1string + "\n" + hotkey2string)
        f.close()

        os.system("sudo reboot")

    def TurnScreenOn(obj):
        global screenon
        screenon = 1
        os.system("sudo echo 0 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen on

    def TurnScreenOff(obj):
        global screenon
        screenon = 0
        os.system("sudo echo 1 > /sys/class/backlight/rpi_backlight/bl_power") #turns screen off


    #brightness control functions
    def BrightnessSetLock(obj): #only for lockscreen - not used yet
        os.system("sudo echo 15 > /sys/class/backlight/rpi_backlight/brightness") #sets screen brightness to ~ 1%
    def BrightnessSet1(obj):
        os.system("sudo echo 15 > /sys/class/backlight/rpi_backlight/brightness") #sets screen brightness to ~ 10%
    def BrightnessSet2(obj):
        os.system("sudo echo 60 > /sys/class/backlight/rpi_backlight/brightness") #sets screen brightness to ~ 25%
    def BrightnessSet3(obj):
        os.system("sudo echo 80 > /sys/class/backlight/rpi_backlight/brightness") #sets screen brightness to ~ 50%
    def BrightnessSet4(obj):
        os.system("sudo echo 120 > /sys/class/backlight/rpi_backlight/brightness") #sets screen brightness to ~ 75%
    def BrightnessSet5(obj):
        os.system("sudo echo 200 > /sys/class/backlight/rpi_backlight/brightness") #sets screen brightness to ~ 100%

    # def killaccel(obj):
    #     global ACCELON
    #     ACCELON = 0
    #
    # def addaccel(obj):
    #     global ACCELON
    #     ACCELON = 1
    #
    # def resetaccelmaxes(obj):
    #     global accelxmaxpos
    #     global accelxmaxneg
    #     global accelymaxpos
    #     global accelymaxneg
    #     accelxmaxpos = 0
    #     accelxmaxneg = 0
    #     accelymaxpos = 0
    #     accelymaxneg = 0

#____________________________________________________________________
#GPIO CALLBACKS
def seekup_callback(obj): #logic for seekup gpio
    global SEEKUPON
    if SEEKUPON == 0:
        if is_rpi:
            GPIO.output(seekupPin, GPIO.LOW)
        SEEKUPON = 1
    else:
        if is_rpi:
            GPIO.output(seekupPin, GPIO.HIGH)
        SEEKUPON = 0

def seekdown_callback(obj): #logic for seekdown gpio
    global SEEKDOWNON
    if SEEKDOWNON == 0:
        if is_rpi:
            GPIO.output(seekdownPin, GPIO.LOW)
        SEEKDOWNON = 1
    else:
        if is_rpi:
            GPIO.output(seekdownPin, GPIO.HIGH)
        SEEKDOWNON = 0

def aux_callback(obj): #logic for aux gpio
    global AUXON
    if AUXON == 0:
        if is_rpi:
            GPIO.output(auxPin, GPIO.LOW)
        AUXON = 1
    else:
        if is_rpi:
            GPIO.output(auxPin, GPIO.HIGH)
        AUXON = 0

def amfm_callback(obj): #logic for amfm gpio
    global AMFMON
    if AMFMON == 0:
        if is_rpi:
            GPIO.output(amfmPin, GPIO.LOW)
        AMFMON = 1
    else:
        if is_rpi:
            GPIO.output(amfmPin, GPIO.HIGH)
        AMFMON = 0

        #CONTROLS

def garage_callback(obj): #logic for garage gpio
    global GARAGEON
    if GARAGEON == 0:
        if is_rpi:
            GPIO.output(garagePin, GPIO.LOW)
        GARAGEON = 1
    else:
        if is_rpi:
            GPIO.output(garagePin, GPIO.HIGH)
        GARAGEON = 0

def radar_callback(obj): #logic for radar gpio
    global RADARON
    if RADARON == 0:
        if is_rpi:
            GPIO.output(radarPin, GPIO.LOW)
        RADARON = 1
    else:
        if is_rpi:
            GPIO.output(radarPin, GPIO.HIGH)
        RADARON = 0


# def leds_callback(obj): #logic for cup holder leds gpio
#     global LEDSON
#     if LEDSON == 0:
#         if is_rpi:
#             GPIO.output(ledsPin, GPIO.HIGH)
#         LEDSON = 1
#     else:
#         if is_rpi:
#             GPIO.output(ledsPin, GPIO.LOW)
#         LEDSON = 0
#
# def windowsup_callback(obj): #logic for windows up gpio
#     global WINDOWSUPON
#     global WINDOWSDOWNON
#
#     if WINDOWSDOWNON == 0:
#
#         if WINDOWSUPON == 0:
#             if is_rpi:
#                 GPIO.output(driverwindowupPin, GPIO.LOW)
#                 GPIO.output(passwindowupPin, GPIO.LOW)
#             WINDOWSUPON = 1
#             return
#         if WINDOWSUPON == 1:
#             if is_rpi:
#                 GPIO.output(driverwindowupPin, GPIO.HIGH)
#                 GPIO.output(passwindowupPin, GPIO.HIGH)
#             WINDOWSUPON = 0
#             return
#
#
# def windowsupOFF_callback(obj): #logic to halt the windows
#     global WINDOWSUPON
#     global WINDOWSDOWNON
#     WINDOWSUPON = 0
#     if is_rpi:
#         GPIO.output(driverwindowupPin, GPIO.HIGH)
#         GPIO.output(passwindowupPin, GPIO.HIGH)
#
# def windowsdown_callback(obj): #logic for windows down gpio
#     global WINDOWSDOWNON
#     global WINDOWSUPON
#
#     if WINDOWSUPON == 0:
#
#         if WINDOWSDOWNON == 0:
#             if is_rpi:
#                 GPIO.output(driverwindowdownPin, GPIO.LOW)
#                 GPIO.output(passwindowdownPin, GPIO.LOW)
#             WINDOWSDOWNON = 1
#             return
#         if WINDOWSDOWNON == 1:
#             if is_rpi:
#                 GPIO.output(driverwindowdownPin, GPIO.HIGH)
#                 GPIO.output(passwindowdownPin, GPIO.HIGH)
#             WINDOWSDOWNON = 0
#             return
#
# def windowsdownOFF_callback(obj): #logic to halt the windows
#     global WINDOWSDOWNON
#     global WINDOWSUPON
#     WINDOWSDOWNON = 0
#     if is_rpi:
#         GPIO.output(driverwindowdownPin, GPIO.HIGH)
#         GPIO.output(passwindowdownPin, GPIO.HIGH)
#
#     # callback functions for window debugging
#
# def driverup_callback(obj): #logic for driver up gpio
#     global DRIVERUPON
#     if DRIVERUPON == 0:
#         if is_rpi:
#             GPIO.output(driverwindowupPin, GPIO.LOW)
#         DRIVERUPON = 1
#     else:
#         if is_rpi:
#             GPIO.output(driverwindowupPin, GPIO.HIGH)
#         DRIVERUPON = 0
#
# def driverstop_callback(obj): #logic for driver window emergency stop
#     global WINDOWSDOWNON
#     global WINDOWSUPON
#     WINDOWSDOWNON = 0
#     WINDOWSUPON = 0
#     if is_rpi:
#         GPIO.output(driverwindowupPin, GPIO.HIGH)
#         GPIO.output(driverwindowdownPin, GPIO.HIGH)
#
# def driverdown_callback(obj): #logic for driver down gpio
#     global DRIVERDOWNON
#     if DRIVERDOWNON == 0:
#         if is_rpi:
#             GPIO.output(driverwindowdownPin, GPIO.LOW)
#         DRIVERDOWNON = 1
#     else:
#         if is_rpi:
#             GPIO.output(driverwindowdownPin, GPIO.HIGH)
#         DRIVERDOWNON = 0
#
# def passengerup_callback(obj): #logic for passenger up gpio
#     global PASSENGERUPON
#     if PASSENGERUPON == 0:
#         if is_rpi:
#             GPIO.output(passwindowupPin, GPIO.LOW)
#         PASSENGERUPON = 1
#     else:
#         if is_rpi:
#             GPIO.output(passwindowupPin, GPIO.HIGH)
#         PASSENGERUPON = 0
#
# def passengerstop_callback(obj): #logic for passenger window emergency stop
#     global WINDOWSDOWNON
#     global WINDOWSUPON
#     WINDOWSDOWNON = 0
#     WINDOWSUPON = 0
#     if is_rpi:
#         GPIO.output(passwindowupPin, GPIO.HIGH)
#         GPIO.output(passwindowdownPin, GPIO.HIGH)
#
# def passengerdown_callback(obj): #logic for passenger down gpio
#     global PASSENGERDOWNON
#     if PASSENGERDOWNON == 0:
#         if is_rpi:
#             GPIO.output(passwindowdownPin, GPIO.LOW)
#             GPIO.output(passwindowdownPin, GPIO.LOW)
#         PASSENGERDOWNON = 1
#     else:
#         if is_rpi:
#             GPIO.output(passwindowdownPin, GPIO.HIGH)
#         PASSENGERDOWNON = 0
#
# def allwindowsstop_callback(obj): #logic for all windows emergency stop
#     global WINDOWSDOWNON
#     global WINDOWSUPON
#     WINDOWSDOWNON = 0
#     WINDOWSUPON = 0
#     if is_rpi:
#         GPIO.output(passwindowupPin, GPIO.HIGH)
#         GPIO.output(passwindowdownPin, GPIO.HIGH)
#         GPIO.output(driverwindowupPin, GPIO.HIGH)
#         GPIO.output(driverwindowdownPin, GPIO.HIGH)

if __name__ =='__main__':
    MainApp().run()
