from subprocess import DEVNULL, call, Popen, PIPE, check_output
from platform import system
import re
from os import getcwd, path, listdir
class Shell:
    def getAllAppsOpened():
        """
        This will get all the apps that are open.
        If the app is Electron, it may be VS Code, Atom, or Sublime Text.
        """
        os_name = system()
        if os_name == "Darwin":
            os_name = "macOS"
        if os_name == "macOS":
            with open(f'{getcwd()}/osascript_command.txt', 'r') as f:
                global command
                command = f.read()
            result = check_output([command], shell=True)
            result = result.decode('utf-8').strip('\n')
            apps = []
            for app in result.split():
                apps.append(app)
            return apps
        elif os_name == "Windows":
            result = check_output(["tasklist"], shell=True)
            result = result.decode('utf-8').strip('\n')
            return result
        elif os_name == "Linux":
            result = check_output(["ps -A"], shell=True)
            result = result.decode('utf-8').strip()
            return result
    def getAppPath(appName):
        """
        This will get the path of the app.
        """
        os_name = system()
        if os_name == "Darwin":
            os_name = "macOS"
        if os_name == "macOS":
           folderPath = "/Applications"
           if not appName == ".app":
                appName = appName + ".app"
                appPath = path.join(folderPath, appName)
                for app in listdir(folderPath):
                    if app == appName:
                        if " " in apps:
                          appPath.replace(" ", "/ ")
                          return appPath
                        else:
                          return appPath
                    else:
                        continue
                return "App not found."
           else:
                appPath = path.join(folderPath, appName)
                for apps in listdir(folderPath):
                    if apps == appName:
                        return appPath
                    else:
                        continue
                return "App not found."
        elif os_name == "Windows":
            folderPath = "C:\\Program Files"
            if not appName == ".exe":
                appName = appName + ".exe"
                appPath = path.join(folderPath, appName)
                for apps in listdir(folderPath):
                    if apps == appName:
                        return appPath
                    else:
                        continue
                return "App not found."
            else:
                appPath = path.join(folderPath, appName)
                for apps in listdir(folderPath):
                    if apps == appName:
                        return appPath
                    else:
                        continue
                return "App not found."
        elif os_name == "Linux":
            folderPath = "/usr/bin"
            folderPath2 = "/usr/local/bin"
            folderPath3 = "/usr/local/sbin"
            folderPath4 = "/usr/sbin"
            folderPath5 = "/sbin"
            folderPath6 = "/bin"
            appPath = path.join(folderPath, appName)
            for apps in listdir(folderPath):
                if apps == appName:
                    return appPath
                else:
                    continue
            for apps in listdir(folderPath2):
                if apps == appName:
                    return appPath
                else:
                    continue
            for apps in listdir(folderPath3):
                if apps == appName:
                    return appPath
                else:
                    continue
            for apps in listdir(folderPath4):
                if apps == appName:
                    return appPath
                else:
                    continue
            for apps in listdir(folderPath5):
                if apps == appName:
                    return appPath
                else:
                    continue
            for apps in listdir(folderPath6):
                if apps == appName:
                    return appPath
                else:
                    continue
            return "App not found."
    def KillApp(appName):
        """
        This will close a program if the app is open.
        """
        os_name = system()
        if os_name == "Darwin":   
            os_name = "macOS"
        if os_name == "Windows":
            return call(f"taskkill /f /im {appName}", shell=True)
        elif os_name == "Linux":
            return call(f"killall {appName}", shell=True)
        elif os_name == "macOS":
            proc = str(call(f"killall {appName}", shell=True, stdout=DEVNULL, stderr=DEVNULL, stdin=DEVNULL))
            if proc == "1":
                return f"{appName} was not running or doesn't exist."
            else:
                return 'Process Killed.'