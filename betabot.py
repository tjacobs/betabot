#!/usr/bin/env python

from ams import AMS
from time import sleep

ams = AMS()
connected = ams.connect(1)

if connected < -1:
  print "Not Connected"

import time
import serial
import math
import array

ser= serial.Serial(
    port='/dev/serial0',
    baudrate = 115200,
    parity=serial.PARITY_EVEN,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.EIGHTBITS,
    timeout=10)

ch1 = 1.0
ch2 = 0
arm = 500

forwardback = 1000
updown = 1000
posd = 0

moverange = 400

stepstep = 1
i = 0
shiftd = 0
shiftd2 = 0
d = ams.getAngle(1)
d2 = ams.getAngle(2)
oldd = d
oldd2 = d2

while 1:
   
    ch1 = ch1 + .14
    if ch1 > 5: 
        arm = 1000
#    print ch1
    if stepstep == 1:
	forwardback = forwardback + 1
    if stepstep == 2:
        updown = updown - 1
    if stepstep == 3:
        forwardback = forwardback - 1
    if stepstep == 4:
        updown = updown + 1

    if stepstep == 1 and forwardback > 1000 + moverange:
	stepstep = 2
    if stepstep == 2 and updown < 1000 - moverange:
       stepstep = 3
    if stepstep == 3 and forwardback < 1000 - moverange:
       stepstep = 4
    if stepstep == 4 and updown > 1000 + moverange:
       stepstep = 1

    #if i % 100 == 0:
    #    while ams.getMagnitude() < 100:
    #       sleep( 1 )
    #i += 1

    d = ams.getAngle(1)
    d2 = ams.getAngle(2)
    setpoint = int( math.cos(ch1)*2000)
    setpoint2 = int( math.sin(ch1)*2000)
    print d, d2, setpoint, setpoint2
    d = d + setpoint
    d2 = d2 + setpoint2
    #posd += ( d - posd ) * 0.001

    if ( d - oldd ) > 15000:
	oldd += 16000
        print "blip"
    if ( d - oldd ) < -15000:
	oldd -= 16000
        print "blipo"
    if ( d2 - oldd2 ) > 15000:
	oldd2 += 16000
        print "blip"
    if ( d2 - oldd2 ) < -15000:
	oldd2 -= 16000
        print "blipo"

    diff = (d - oldd ) * 0.2
    if( abs( diff ) < 2000 ):   
        shiftd -= diff
    diff2 = (d2 - oldd2 ) * 0.2
    if( abs( diff2 ) < 2000 ):   
        shiftd2 -= diff2
#    print int( diff )
    oldd += (d - oldd) * 0.1
    oldd2 += (d2 - oldd2) * 0.1
    shiftd *= 0.5 
    shiftd2 *= 0.5 
#    print posd
    channels = [0]*16
    channels[0] = int( 990 + shiftd ) #int(posd * 10 + 100) #1000 + forwardback + updown
    channels[1] = int( 990 + shiftd2 ) #int(posd * 10 + 100) #1000 - forwardback + updown
    channels[2] = int(ch1 % 1500 + 000) #int(math.sin(ch1)*250 + 1000) 
    #channels[2] = int(posd * 10 + 100) #int(math.sin(ch1)*450 + 1000) 
    channels[3] = 1000 
    channels[4] = arm
    channels[5] = 50
    channels[6] = 50
    channels[7] = 50
    channels[8] = 50

    # SBUS start byte
    sbus_data = [0]*25
    sbus_data[0] = 0x0F

    # SBUS channel bytes. 11 bits per channel.
    ch = 0
    bit_in_channel = 0
    byte_in_sbus = 1
    bit_in_sbus = 0
   
    # For 16ch * 11bits = 176 bits 
    for i in range(1, 176):
        if channels[ch] & (1<<bit_in_channel):
            sbus_data[byte_in_sbus] |= (1<<bit_in_sbus)
        bit_in_sbus = bit_in_sbus + 1
        bit_in_channel = bit_in_channel + 1

        if bit_in_sbus == 8:
            bit_in_sbus = 0
            byte_in_sbus = byte_in_sbus + 1
        if bit_in_channel == 11:
            bit_in_channel = 0
            ch = ch + 1

    ser.write( array.array('B', sbus_data).tostring() ) 

    #time.sleep( .001 )




