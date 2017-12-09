import sys
import time
from networktables import NetworkTable

# To see messages from networktables, you must setup logging
import logging
logging.basicConfig(level=logging.DEBUG)


if len(sys.argv) != 2:
    print("Error: specify an IP to connect to!")
    exit(0)

ip = sys.argv[1]

NetworkTable.setIPAddress(ip)
NetworkTable.setClientMode()
NetworkTable.initialize()

def valueChanged(table, key, value, isNew):
    print("valueChanged: key: '%s'; value: %s; isNew: %s" % (key, value, isNew))

class ConnectionListener:

    def connected(self, table):
        print("Connected to", table.getRemoteAddress(), table)

    def disconnected(self, table):
        print("Disconnected", table)

c_listener = ConnectionListener()

sd = NetworkTable.getTable("SmartDashboard")
sd.addTableListener(valueChanged)
sd.addConnectionListener(c_listener)

while True:
    time.sleep(1)
