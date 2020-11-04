'''###########################################################################
#
# Project ACTV Competizione
# Version 1.1.0.0
#
******************************************************************************
*** .--. .-. ..- -. -. .--. .-. ..- -. -. .--. .-. ..- -. -. .--. .-. ..-  ***
***                                                               ***
*** ooooooooo.   ooooooooo.   ooooo     ooo ooooo      ooo ooooo      ooo  ***
*** `888   `Y88. `888   `Y88. `888'     `8' `888b.     `8' `888b.     `8'  ***
***  888   .d88'  888   .d88'  888       8   8 `88b.    8   8 `88b.    8   ***
***  888ooo88P'   888ooo88P'   888       8   8   `88b.  8   8   `88b.  8   ***
***  888          888`88b.     888       8   8     `88b.8   8     `88b.8   ***
***  888          888  `88b.   `88.    .8'   8       `888   8       `888   ***
*** o888o        o888o  o888o    `YbodP'    o8o        `8  o8o        `8   ***
***                                       ***            
*** .--. .-. ..- -. -. .--. .-. ..- -. -. .--. .-. ..- -. -. .--. .-. ..-  ***
******************************************************************************
***************************************************************************'''
import ac
import sys
import traceback
import os
import platform

try:
    if platform.architecture()[0] == "64bit":
        sysdir = "prunn_dll_x64"
    else:
        sysdir = "prunn_dll_x86"
        
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), sysdir))
    os.environ['PATH'] = os.environ['PATH'] + ";." 
    
    from apps_competizione.util.sim_info import SimInfo
    from apps_competizione.actimer import ACTimer
    from apps_competizione.acinfo import ACInfo
    from apps_competizione.actower import ACTower
    from apps_competizione.acdelta import ACDelta
    from apps_competizione.acweather import ACWeather
    from apps_competizione.configuration import Configuration
    from apps_competizione.util.classes import Log
    sim_info = SimInfo()
except:
    exc_type, exc_value, exc_traceback = sys.exc_info()
    lines = traceback.format_exception(exc_type, exc_value, exc_traceback)
    for line in lines:               
        ac.log(line)
        
timer = 0
info = 0
tower = 0
config = 0
delta = 0

timerInit = False
infoInit = False
towerInit = False
configInit = False
deltaInit = False
drivers_info_init = False
weather = 0
weatherInit = False


def acMain(ac_version):
    global timer, info, tower, timerInit, infoInit, towerInit, config, configInit, delta, deltaInit, weather, weatherInit
    try:
        config = Configuration()
        configInit = True
    except:
        Log.w("Error init config") 
    try:
        timer = ACTimer()
        timerInit = True
    except:
        Log.w("Error init timer")
    try:
        info = ACInfo()
        infoInit = True
    except:
        Log.w("Error init info")
    try:
        tower = ACTower()
        towerInit = True
    except:
        Log.w("Error init tower")
    try:
        delta = ACDelta()
        deltaInit = True
    except:
        Log.w("Error init delta")
    try:
        weather = ACWeather()
        weatherInit = True
    except:
        Log.w("Error init weather")

    return "ACTV Competizione"


def acUpdate(deltaT):
    global timer, info, tower, timerInit, infoInit, towerInit, config, configInit, delta, deltaInit, drivers_info_init, weather, weatherInit
    fl = 0
    standings = []
    drivers_info = []
    if configInit:     
        try:
            config_changed = config.on_update(sim_info)
            if config_changed:
                if timerInit:
                    timer.load_cfg()
                if infoInit:
                    info.load_cfg()
                if towerInit:
                    tower.load_cfg()
                if deltaInit:
                    delta.load_cfg()
                if weatherInit:
                    weather.load_cfg()
        except:
            Log.w("Error config")
    if timerInit:
        try:
            timer.on_update(sim_info)
        except:
            Log.w("Error timer")
    if towerInit:
        try:
            tower.on_update(sim_info)
            fl = tower.get_fastest_lap()
            standings = tower.get_standings()
            if not drivers_info_init or tower.drivers_info_is_updated():
                drivers_info = tower.get_drivers_info()
        except:
            Log.w("Error tower")  
    if infoInit:
        try:
            if len(drivers_info):
                info.set_drivers_info(drivers_info)
                drivers_info_init = True
            info.on_update(sim_info, fl, standings)
        except:
            Log.w("Error info")
    if deltaInit:     
        try:
            if len(drivers_info):
                delta.set_drivers_info(drivers_info)
                drivers_info_init = True
            delta.on_update(sim_info, standings)
        except:
            Log.w("Error delta")
    if weatherInit:
        try:
            weather.on_update(sim_info)
        except:
            Log.w("Error weather")

def acShutdown():
    ac.console("shutting down actv cp")
