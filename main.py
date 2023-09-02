import network
from machine import Pin
import network 
import os
import uasyncio
import utime
from ssd1306_setup import WIDTH, HEIGHT, setup
from writer import Writer
import futuramc32
import arial8
import gc
gc.collect()

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

def switch_input(out_val):
    bin_out_val='{:03b}'.format(out_val)
    print("Binary value is: %s - split to %i - %i - %i" % (bin_out_val, int(bin_out_val[0]), int(bin_out_val[1]), int(bin_out_val[2])))
#    print("Binary value is: %s" % bin_out_val)
    OutA.value(int(bin_out_val[0]))
    OutB.value(int(bin_out_val[1]))
    OutC.value(int(bin_out_val[2]))

def write_display(ssd,wri32,wri6,rhs,val):
    inputs=["PHONO","CD","TV","BLU-RAY","MIXER","AUX","MUTE"]
    string_length=wri32.stringlen(inputs[val])
    xpos=int((rhs-string_length)/2)
    ssd.fill(0)
    display_wifi(ssd,wri6,rhs)
    wri32.set_textpos(ssd, 16, xpos)
    wri32.printstring(inputs[val])
    if val!=6:
        wri6.set_textpos(ssd, 50, 60)
        wri6.printstring(str(val+1))
    ssd.show()

def display_wifi(ssd,wri6,rhs):
    wlan = network.WLAN()
    ipAddress,netMask,defaultGateway,DNS=wlan.ifconfig()
    if ipAddress!="0.0.0.0":
        wri6.set_textpos(ssd, 0, 0)
        wri6.printstring(ipAddress)
        ssd.line(rhs - 18, 0, rhs - 2, 0, 1)
        ssd.line(rhs - 15, 3, rhs - 5, 3, 1)
        ssd.line(rhs - 12, 6, rhs - 8, 6, 1)
        ssd.line(rhs - 10, 9, rhs - 9, 9, 1)
    else:
        wri6.printsring("wifi disconnected")
    ssd.show()

# Coroutine: blink on a timer
#async def blink():
#    delay_ms = 500
#    while True:
#        MotDn(not MotDn())
#        await uasyncio.sleep_ms(delay_ms)

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

async def serve_client(reader, writer):
    html = """<!DOCTYPE html>
<html>
    <head> <title>Web Servery</title> </head>
    <body> <h1>go</h1>
        <p>%s</p>
    </body>
</html>
"""
    print("Client connected")
    request_line = await reader.readline()
    print("Request:", request_line)
    # We are not interested in HTTP request headers, skip them
    while await reader.readline() != b"\r\n":
        pass

    request = str(request_line)
#    led_on = request.find('/light/on')
#    led_off = request.find('/light/off')
#    print( 'led on = ' + str(led_on))
#    print( 'led off = ' + str(led_off))

    response = html % "Pipes"
    writer.write('HTTP/1.0 200 OK\r\nContent-type: text/html\r\n\r\n')
    writer.write(response)

    await writer.drain()
    await writer.wait_closed()
    print("Client disconnected")


async def main():
    gc.collect()
    out_val=0
    mute=False

# Web server nonsense
    uasyncio.create_task(uasyncio.start_server(serve_client, "0.0.0.0", 80))

# initiate display nonsense
    ssd = setup()  # Create a display instance
    rhs = WIDTH -1
    ssd.fill(0)     
    wri6 = Writer(ssd, arial8)
    wri32 = Writer(ssd, futuramc32)
    wri6.set_textpos(ssd, 3, 0)
    display_wifi(ssd,wri6,rhs)

    # Start coroutine as a task and immediately return
    # uasyncio.create_task(blink())

## Start as we mean to go on - input 1 (or 0)
    print(str(out_val))
    switch_input(out_val)
    write_display(ssd,wri32,wri6,rhs,out_val)

    while True:
        gc.collect()
#        print("waiting for the button then")
        btn_press,long_press=await wait_button()
        if btn_press:
            if long_press and not mute:
# Do mute-y business
                switch_input(6)
                write_display(ssd,wri32,wri6,rhs,6)
                print("long press - muting")
                mute=True
            else:
# increment input
                if mute:
                    mute=False
                else:
                    out_val=(out_val+1) % 6
                switch_input(out_val)                    
                write_display(ssd,wri32,wri6,rhs,out_val)
                print("changing to input %i" % out_val)
# increment the doings

if __name__ == "__main__":
#    try:
# Start event loop and run entry point coroutine
    uasyncio.run(main())
#    except KeyboardInterrupt:
#        pass
