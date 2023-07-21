# boot.py -- run on boot-up
import network
import sys
import time
try:
  import usocket as socket
except:
  import socket

import esp
esp.osdebug(None)

import gc
gc.collect()

def connectToWiFi():
    print("Oh hello")
    wifiInfo={}
    f = open('wifi.env')
    for line in f:
        if "=" in line:
            thisAttr=(line.strip().split("=")[0])
            thisVal=(line.strip().split("=")[1])
            wifiInfo[thisAttr]=thisVal
    if 'ssid' in wifiInfo and 'pass' in wifiInfo:
        wlan = network.WLAN(network.STA_IF)
        wlan.active(True)
        print("Connecting",end="")
        wlan.connect(wifiInfo['ssid'], wifiInfo['pass'])
        ipAddress,netMask,defaultGateway,DNS=wlan.ifconfig()
        wifiCount=0
        while ipAddress=='0.0.0.0' and wifiCount<30:
            print(".",end="")
            time.sleep(1)
            ipAddress,netMask,defaultGateway,DNS=wlan.ifconfig()
            wifiCount+=1 
        if ipAddress=="0.0.0.0":
            print("No WiFi connection - please check details in wifi.env")
            sys.exit()
    else:
        print("You need to put some wifi details in wifi.env")
        sys.exit()
        
    print("Wifi connected - IP address is: "+ipAddress)

connectToWiFi()
