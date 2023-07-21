# main.py -- put your code here!
# Basic functions
# Connect to wifi
# Run a webserver (not enough memory to run websockets)
# Display the current input on the screen
# If a button is pressed:
# - short button press mute
# - long button press go into input switching
# - hold the button to slowly go through the inputs
# - fast press the button to quickly go through the inptus
# - update the display
# If the request comes in from the websocket:
# - change input or mute or move the volume pot (future development)
# - update the display
#
# PINS
# Phys Pin In/Out Function
# D1   5   OUT    SCL - TFT Screen
# D2   4   OUT    SDA - TFT Screen
# D3   0   OUT    Motor +
# D4   2   OUT    Motor -
# D5   14  IN     Button (PullUp)
# D6   12  OUT    Input Selector A
# D7   13  OUT    Input Selector B
# D8   15  OUT    Input Selector C

# References
# https://www.upesy.com/blogs/tutorials/hardware-interrupts-rpi-pico-on-micropython#

# Important imports
import time
from machine import Pin, I2C
import ssd1306
import network
import sys  
import os

# Initialise the screen using default address 0x3C
# i2c = I2C(sda=Pin(4), scl=Pin(5 ))
# display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Easy To Remember variables
Btn=Pin(14, Pin.IN, Pin.PULL_UP)
MotUp=Pin(0, Pin.OUT)
MotDn=Pin(2, Pin.OUT)
OutA=Pin(12, Pin.OUT)
OutB=Pin(13, Pin.OUT)
OutC=Pin(15, Pin.OUT)

def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

def btn_on(pin):
    print("Button pressed")

def btn_off(pin):
    print("Button released")

def content_type(uri):
    this_type='text/html'
    if "." in uri:
        suffix=uri.split(".")[1]
        print("Suffix is: "+suffix)
        if suffix=='js':
            this_type='text/javascript'
        if suffix=='css':
            this_type='text/css'
    return this_type

def web_page(filename):
    content=""
    if file_exists("web/"+filename):
        response="200 OK"
        f=open("web/"+filename)
        for line in f:
            content=content+line
    else:
        response="404 not found"
    return content,response

def main():
    # configure an irq callback
    Btn.irq(trigger=Pin.IRQ_FALLING, handler=btn_off)
    Btn.irq(trigger=Pin.IRQ_RISING, handler=btn_on)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(5)
    print("Listening on port 80 then")
    while True:
        conn, addr = s.accept()
        print('Got a connection from %s' % str(addr))
        request = conn.recv(1024)
        request = str(request)
        print('Content = %s' % request)
        uri=request.split(" ")[1][1:]
        print("Bit I want is: "+uri)
        if uri=="":
            uri="index.html"
        content,responsecode = web_page(uri)
        conn.send('HTTP/1.1 '+responsecode+'\n')
        conn.send('Content-Type: '+content_type(uri)+'\n')
        conn.send('Connection: close\n\n')
        conn.sendall(content)
        conn.close()

if __name__ == "__main__":
#    try:
        main()
#    except KeyboardInterrupt:
#        pass
