#This program runs on startup of the Pi
#Please note this code was written last minute and has not been optimized or refactored 
from networktables import NetworkTable
import subprocess, signal
import os
import psutil

NetworkTable.setIPAddress("10.38.80.2") #IP of the RoboRIO
NetworkTable.setClientMode()
NetworkTable.initialize()
sd=NetworkTable.getTable("SmartDashboard")

def getPid(processName):
    p = subprocess.Popen(['ps', 'au'], stdout=subprocess.PIPE)
    out, etc = p.communicate()
    for line in out.splitlines():
        if processName in line:
            l = line.split(None, 1)
            clip = l[1]
            space = clip.index(" ")
            pidStr = clip[:space]
            pid = pidStr.strip()
            pid = int(pid)
            print "pid: *",pid,"*"
    if running(processName):
        return pid
    else:
        return None

def killProgram(processName):
    print "attempting to kill program: ", processName
    pid = getPid(processName)
    if pid != None:
        os.kill(pid, signal.SIGKILL)
        print "Terminated ", processName
    if running(processName):
        print "Failed to terminate ", processName

def running(processName):
    p = subprocess.Popen(['ps', 'au'], stdout=subprocess.PIPE)
    out, etc = p.communicate()
    for line in out.splitlines():
        if processName in line:
            l = line.split(None, 1)
            clip = l[1]
            space = clip.index(" ")
            pidStr = clip[:space]
            pid = pidStr.strip()
            pid = int(pid)
            if pid != None:
                print processName, " is running"
                return True
    print processName, " is not running"
    return False

def main():
    '''
    if running("startUp.py") and :
        killProgram("startUp.py")
    '''
    #while running("shooterVision.py"):
    #   killProgram("shooterVision.py")
    #while running("gearVision.py"):
    #    killProgram("gearVision.py")
    sCheck = 0
    gCheck = 0

    runList = [getPid("startUp.py")]
    while True:
        shooterVision = sd.getBoolean("shooterVision", None)
        runList.append(getPid("startUp.py"))
        print "Run List: ", runList
        '''
        for i in runList:
            a = runList[i]
            for j in runList:
                b = runList[j-1]
                if a != b:
                    print "Killing startUp.py"
                    killProgram("startUp.py")
        '''
        if shooterVision == None:
            #print "No value recieved. Defaulting to shooting"
            #shooterVision = True

            print "No value recieved. Defaulting to gear."
            shooterVision = False

        if shooterVision:
            print "running shooterVision.py"

            while running("gearVision.py"):
                killProgram("gearVision.py")
                gCheck = 0

            if running("shooterVision.py") == False:
                subprocess.call(['python', '/home/pi/shooterVision.py'])
                sCheck = 1

        elif shooterVision == False:
            print "running gearVision.py"

            while running("shooterVision.py"):
                killProgram("shooterVision.py")
                sCheck = 0

            if running("gearVision.py") == False:
                subprocess.call(['python', '/home/pi/gearVision.py'])
                gCheck = 1
        else:
            print "Incorrect value: shooterVision = ", shooterVision


if __name__ == "__main__":
    main()
