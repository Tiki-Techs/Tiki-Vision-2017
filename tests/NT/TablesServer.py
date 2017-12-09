import time
from networktables import NetworkTable

import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTable.setServerMode()
sd = NetworkTable.getTable("SmartDashboard")
i = 0
while True:
    sd.putNumber("dsTime", i)
    time.sleep(1)
    if (sd.containsKey("robotCount")) :
        rc = sd.getNumber("robotCount")
        print ("Received data 'robotCount' : {0}".format(rc))
    i += 1