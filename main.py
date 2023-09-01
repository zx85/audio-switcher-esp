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
##################################
# NOT D3   0   OUT    Motor + - this enables flash writing
# D4   2   OUT    Motor -     - so going to have to rethink this
##################################
# D5   14  IN     Button (PullUp)
# D6   12  OUT    Input Selector A
# D7   13  OUT    Input Selector B
# D8   15  OUT    Input Selector C

# References
# https://www.upesy.com/blogs/tutorials/hardware-interrupts-rpi-pico-on-micropython#
#
# Webserver - https://github.com/miguelgrinberg/microdot - TODO
# Async =  https://www.digikey.co.uk/en/maker/projects/getting-started-with-asyncio-in-micropython-raspberry-pi-pico/110b4243a2f544b6af60411a85f0437c
# Important imports
import time
from machine import Pin, I2C
import ssd1306
import network
import sys  
import os
import uasyncio
import usocket
import utime
from uselect import select

# Initialise the screen using default address 0x3C
# i2c = I2C(sda=Pin(4), scl=Pin(5 ))
# display = ssd1306.SSD1306_I2C(128, 64, i2c)

# Easy To Remember variables
# Going to pull up so it triggers on LOW
Btn=Pin(14, Pin.IN, Pin.PULL_UP)
# Going to have to rethink the motors because D3 can't be used
# MotUp=Pin(0, Pin.OUT)
MotDn=Pin(2, Pin.OUT) # This is actually the internal LED. Handy
OutA=Pin(12, Pin.OUT, Pin.PULL_UP)
OutB=Pin(13, Pin.OUT, Pin.PULL_UP)
OutC=Pin(15, Pin.OUT, Pin.PULL_UP)

def file_exists(filename):
    try:
        os.stat(filename)
        return True
    except OSError:
        return False

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


# Coroutine: blink on a timer
async def blink():
    delay_ms = 500
    while True:
        MotDn(not MotDn())
        await uasyncio.sleep_ms(delay_ms)

# Coroutine: only return on button press
async def wait_button():
    LONG_THRESHOLD=500
    btn_press=False
    long_press=False
    btn_prev = Btn.value()    
    timestamp=utime.ticks_ms()        
    while Btn.value() == 0:
        btn_press=True
        if btn_prev==1:
            timestamp=utime.ticks_ms()
        if utime.ticks_ms()-timestamp>LONG_THRESHOLD:
            long_press=True
        btn_prev = Btn.value()
    await uasyncio.sleep_ms(40)
    return btn_press,long_press

async def main():

    addr = usocket.getaddrinfo('0.0.0.0', 80)[0][-1]
    s = usocket.socket()
    s.bind(addr)
    s.listen(1)

    # Start coroutine as a task and immediately return
    uasyncio.create_task(blink())
#    uasyncio.create_task(webserver(s))
    while True:
#        print("waiting for the button then")
        btn_press,long_press=await wait_button()
        if btn_press:
            if long_press:
                print("LONG")
            else:
                print("SHORT")

if __name__ == "__main__":
#    try:
# Start event loop and run entry point coroutine
    uasyncio.run(main())
#    except KeyboardInterrupt:
#        pass
