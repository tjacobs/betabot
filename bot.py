# Betabot
# Code: https://github.com/tjacobs/betabot
# by Tom Jacobs

from ams import AMS
from time import sleep
import time
#import serial
import math
import array

# Go
def main():
	# Talk to motor angle sensors via I2C
	sensors = AMS()
	connected = sensors.connect(1)
	if connected < 0:
		print( "Warning: Can not read all motor sensors" )

	# Talk to motor controller via serial UART SBUS
	sbus = openSBUS()

	# Which part of the step is each leg in?
	stepStages = [1, 3, 1, 3]

	# What speed is each motor at?
	motorSpeeds = [0] * 4

	# Arm mode
	arm = 1000

	# Loop
	while True:
		stepStages, targetAngles = updateTargetAngles(stepStages)
		currentAngles = [4000]*8  #readCurrentAngles(sensors)
		Ps = calculatePs(currentAngles, targetAngles)
		motorSpeeds = clampMotorSpeeds(Ps)
		sendMotorSpeeds(sbus, motorSpeeds, arm)
		print( motorSpeeds )

# -------------
# Functions

timeThen = time.time()*1000
def updateTargetAngles( stepStages ):
	targetAngles = [0] * 8

	# Every 2 seconds
	global timeThen
	if( time.time()*1000 > timeThen + 2000 ):
		timeThen = time.time()*1000

		for i in range(len(stepStages)):
			stage = stepStages[i]
			if stage == 1:
				stage = 2
				targetAngles[i*2] = 4000
				targetAngles[i*2 +1] = 4000
			elif stage == 2:
				stage = 3
				targetAngles[i*2] = 7000
				targetAngles[i*2 +1] = 7000
			elif stage == 3:
				stage = 4
				targetAngles[i*2] = 4000
				targetAngles[i*2 +1] = 4000
			elif stage == 4:
				stage = 1
				targetAngles[i*2] = 4000
				targetAngles[i*2 +1] = 4000
			stepStages[i] = stage

	return stepStages, targetAngles

def readCurrentAngles(sensors):
	currentAngles = []
	for i in range(4):
		currentAngles[i] = sensors.getAngle(i)
	return currentAngles

def clampMotorSpeeds( motorSpeeds ):
	minSpeed = -200
	maxSpeed = 200
	for i in range(len(motorSpeeds)):
		motorSpeeds[i] = max(min(motorSpeeds[i], maxSpeed), minSpeed)
	return motorSpeeds

def calculatePs( currentAngles, targetAngles ):
	Ps = [0] * len( targetAngles )
	P_rate = 0.5
	for i in range(len(targetAngles)):
		Ps[i] = P_rate * (targetAngles[i] - currentAngles[i])
	return Ps

def sendMotorSpeeds( sbus, motorSpeedsIn, arm ):
	motorSpeeds = [0]*8
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = int(motorSpeedsIn[i])
	sendSBUSPacket( sbus, [motorSpeeds[0], motorSpeeds[1], motorSpeeds[2], motorSpeeds[3], arm] )

# ----------
# SBUS

def openSBUS():
	return 0
	return serial.Serial(
		port='/dev/serial0',
		baudrate = 115200, # Must rebuild and flash betaflight to listen at this rate, not 100,000 as per normal SBUS.
		parity=serial.PARITY_EVEN,
		stopbits=serial.STOPBITS_TWO,
		bytesize=serial.EIGHTBITS,
		timeout=10)

def sendSBUSPacket(sbus, channelValues):

	# 16 blank channels, copy as many channels as given
	channels = [0]*16
	for j in range(len(channelValues)):
		channels[j] = int(channelValues[j])

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

	# Send
	#sbus.write( array.array('B', sbus_data).tostring() ) 


if __name__=="__main__":
   main()
