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

while 1:

    ch1 = ch1 + .05

    channels = [0]*16
    channels[0] = 1000
    channels[1] = 1000
    channels[2] = int(math.sin(ch1)*250 + 1000) 
    channels[3] = 1000 
    channels[4] = int(math.cos(ch1)*250 + 550) 
    if( ch1 > 15 ):
        channels[4] = 1000
    channels[5] = 50
    channels[6] = 50
    channels[7] = 50
    channels[8] = 50

    # SBUS start byte
    sbus_data = [0]*25
    sbus_data[0] = 0x0F

    # SBUS channel bytes. 11 bits per channel.
#    sbus_data[1:25] = 0
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

    time.sleep( .05 )




