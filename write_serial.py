#!/usr/bin/env python
          
import time
import serial
import bitstring
import math
import array

def reverse_mask(x):
    x = ((x & 0x55555555) << 1) | ((x & 0xAAAAAAAA) >> 1)
    x = ((x & 0x33333333) << 2) | ((x & 0xCCCCCCCC) >> 2)
    x = ((x & 0x0F0F0F0F) << 4) | ((x & 0xF0F0F0F0) >> 4)
    x = ((x & 0x00FF00FF) << 8) | ((x & 0xFF00FF00) >> 8)
    x = ((x & 0x0000FFFF) << 16) | ((x & 0xFFFF0000) >> 16)
    return x

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

    ch1 = ch1 + .2

    channels = [0]*16
    channels[0] = 1000
    channels[1] = 1000
    channels[2] = int(math.sin(ch1)*250 + 1000) 
    channels[3] = 1000 
    channels[4] = int(math.cos(ch1)*250 + 550) 
    if( ch1 > 5 ):
        channels[4] = 1000
    channels[5] = 50
    channels[6] = 50
    channels[7] = 50
    channels[8] = 50

    sbus_data = [0]*25
    sbus_data[0] = 0x0F
    for i in range(1, 25):
        sbus_data[i] = 0
    
        # Reset counters
        ch = 0
        bit_in_channel = 0
        byte_in_sbus = 1
        bit_in_sbus = 0
        
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

    print sbus_data
    ser.write( array.array('B', sbus_data).tostring() ) 

