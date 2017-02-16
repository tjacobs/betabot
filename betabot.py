#!/usr/bin/env python
          
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


forwardback = 1000
updown = 1000

moverange = 100

stepstep = 1

while 1:

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




    channels = [0]*16
    channels[0] = 1000 + forwardback + updown
    channels[1] = 1000 - forwardback + updown
    channels[2] = 1000 #int(math.sin(ch1)*250 + 1000) 
    channels[3] = 1000 
    channels[4] = 1000
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

    time.sleep( .001 )




