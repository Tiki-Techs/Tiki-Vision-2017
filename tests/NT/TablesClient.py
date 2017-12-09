import time
from networktables import NetworkTable

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)

NetworkTable.initialize(server="192.168.1.56")
sd = NetworkTable.getTable("SmartDashboard")

print "IP: {0}".format(sd.getRemoteAddress())

i = 0
while True:
    try:
        print('dsTime:', sd.getNumber('dsTime'))
    except KeyError:
        print('dsTime: N/A')

    sd.putNumber('robotCount', i)
    time.sleep(1)
    i += 1