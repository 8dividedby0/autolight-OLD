import datetime, trayApp, ctypes, subprocess, time, os
from log import logger

with open("settings", "r") as file: # read the settings file
    try:
        data = file.read()
        list = data.split(":") # the settings file split by a semicolin
        settingsDayHour = int(list[0])
        settingsNightHour = int(list[1])
        accuracy = int(list[2])
        logFolderName = list[3]
        logName = list[4]
        if list[6] == "1":
            useWallpaper = True
            wallpaperDayPath = os.path.abspath(list[7])
            wallpaperNightPath = os.path.abspath(list[8])
        else:
            useWallpaper = False
        match (list[5]): # exit theme: 0 = none, 1 = light, 2 = dark
            case "0":
                exitTheme = None
            case "1":
                exitTheme = "light"
            case "2":
                exitTheme = "dark"
            case _:
                raise Exception("Invalid exit theme option: " + list[5])
    except Exception as e:
        ctypes.windll.user32.MessageBoxW(0, f"The settings file appears to be corrupted.\n\nError: {e}\n\nsettings data:\n{data}", "AutoLight", 1)
        exit()

def setDarkForce(trayapp): 
    setDark(forced=True)   # set to dark and turn force switch on
def setLightForce(trayapp): 
    setLight(forced=True) # set to light and turn force switch on

def setDark(forced=False):
    if forced:
        global switch
        switch = True
    tray.changeIcon("icons/night.ico")
    if useWallpaper:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaperNightPath, 0) # sets night wallpaper
        log.logPrint(f"Changed wallpaper to {wallpaperNightPath}")
    subprocess.run(darkCmd) # sets pc to dark mode

def setLight(forced=False):
    if forced:
        global switch
        switch = True
    tray.changeIcon("icons/day.ico")
    if useWallpaper:
        ctypes.windll.user32.SystemParametersInfoW(20, 0, wallpaperDayPath, 0) # sets day wallpaper
        log.logPrint(f"Changed wallpaper to {wallpaperDayPath}")
    subprocess.run(lightCmd) # sets pc to light mode

def shutdown(trayapp): # gets called on trayapp shutdown
    global kill
    log.logPrint("Shutdown called")
    if exitTheme == "dark":
        ctypes.windll.user32.MessageBoxW(0, "Goodbye! We are going to set your desktop to dark before we leave.", "AutoLight", 1)
        setDark()
    elif exitTheme == "light":
        ctypes.windll.user32.MessageBoxW(0, "Goodbye! We are going to set your desktop to light before we leave.", "AutoLight", 1)
        setLight()
    kill = True # cant exit() here otherwise it errors and the script continues after trayapp exit

def checkCurrentTime():
    if datetime.datetime.now().hour >= settingsNightHour: # check if current time is before settingsNightHour, otherwise it is night
        return "night"
    else:
        return "day"
    
def getSecondsRemaining(target_hour): # get seconds until specified hour
    now = datetime.datetime.now()
    target_time = now.replace(hour=target_hour, minute=0, second=0, microsecond=0)

    if target_time <= now:
        # The target hour has already passed for today, so set it to tomorrow
        target_time += datetime.timedelta(days=1)

    until = (target_time - now).total_seconds()
    return until

def stop():
    exit()

log = logger(f"{logFolderName}/{logName}." + datetime.datetime.now().strftime("%m.%d.%Y_%H.%M.%S") + ".log") # initiates a log file object with the name autoLightLog.%m%.%d%.%y%_%h%.%m%.%s%.log

darkCmd = ['reg.exe', 'add', 'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize', '/v', 'AppsUseLightTheme', '/t', 'REG_DWORD', '/d', '0', '/f'] # switch to dark mode command
lightCmd = ['reg.exe', 'add', 'HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Themes\Personalize', '/v', 'AppsUseLightTheme', '/t', 'REG_DWORD', '/d', '1', '/f'] # switch to light mode command
switch = False # when this is set to true the loop will start waiting for the opposite of what its currently waiting for
kill = False # when this is true it kills the program

if checkCurrentTime() == "day": # gets appropriate icon to use in the trayapp when it starts up and it also sets the 
    icon = "icons/day.ico"
else:
    icon = "icons/night.ico"

tray = trayApp.trayApp(setDarkForce, setLightForce, shutdown, icon, log) # initiate the trayapp object

def waitUntilDark():
    setLight()
    global switch
    log.logPrint("Waiting until dark")
    until = getSecondsRemaining(settingsNightHour)
    surpassed = 0 # time surpassed from start
    while True: # loops until surpassed is greater than until
        tray.updateHoverText(f"Switching to dark in {round((until-surpassed) / 60 / 60)} hours and {round((until-surpassed) / 60) % 60} minutes")
        time.sleep(accuracy)
        surpassed += accuracy
        log.logPrint(f"Heartbeat: Until = {until}, Surpassed = {surpassed}, wait = {until-surpassed}")
        if switch:
            log.logPrint("Switch detected!")
            switch = False
            waitUntilLight()
            break
        if kill:
            stop()
        if until < surpassed:
            break

def waitUntilLight():
    setDark()
    global switch
    log.logPrint("Waiting until Light")
    until = getSecondsRemaining(settingsDayHour)
    surpassed = 0 # time surpassed from start
    while True: # loops until surpassed is greater than until
        tray.updateHoverText(f"Switching to light in {round((until-surpassed) / 60 / 60)} hours and {round((until-surpassed) / 60) % 60} minutes")
        time.sleep(accuracy)
        surpassed += accuracy
        log.logPrint(f"Heartbeat: Until = {until}, Surpassed = {surpassed}, wait = {until-surpassed}")
        if switch:
            log.logPrint("Switch detected!")
            switch = False
            waitUntilDark()
            break
        if kill:
            stop()
        if until < surpassed:
            break

while True: # main loop
    log.logPrint(f"The reported cycle is {checkCurrentTime()}")
    if checkCurrentTime() == "day":
        waitUntilDark()
    else:
        waitUntilLight()