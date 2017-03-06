# Betabot
# Code: https://github.com/tjacobs/betabot
# by Tom Jacobs

# Neural Network: LSTM.
# 

# Inputs are:
# IMU X, Y angles (2) ( 0 - 1, 0.5, 0.5 is flat level )
# CurrentAngles (8) ( 0 - 1, from 20 to 160 degrees, 0 being knees all straight up in the air, flipped for backwards motors )
# Resistances (8) ( 0 - 1, amount of resistance each motor is currently experiencing )
# MotorSpeeds (8) ( 0 - 1, current motor speeds from calculated from PID loop from output params )
# Sin(t) (1) ( 0 - 1, sin of t, where t is increasing with time )
# Cos(t) (1) ( 0 - 1, cos of t, where t is increasing with time )

# Outputs are:
# TargetAngles (8) ( 0 - 1, from 20 to 160 degrees. Flipped for every backwards motor, so 0 is always up. )
# P_rate (8) (0 - 1, from off to max_p_rate) (add later, fix to resonable default to start with)

# How it works
# Robot starts standing, all legs almost knees sraight up.
# CurrentAngles = [ 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1 ]

# 1. Train the network to stay like that.
# Loss function = difference of targetAngles to [ 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1 ]



from ams import AMS
from time import sleep
import time
import serial
import math
import array

hit = False
armTime = time.time()*1000

# Go
def main():
	try:
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
		motorSpeeds = [0] * 8
		lastAngles = [0] * 8
		lastMotorSpeeds = [0] * 8
		lastLastMotorSpeeds = [0] * 8

		lastCheck = time.time()*1000

		# Loop
		global hit
		while True:
			
			# Arm mode
			arm = 500
			if time.time()*1000 > armTime + 1000:
				arm = 1000

			stepStages, targetAngles = updateTargetAngles(stepStages)
			currentAngles = readCurrentAngles(sensors)
			Ps = calculatePs(currentAngles, targetAngles)
			motorSpeeds = clampMotorSpeeds(Ps)
			
			if hit == True:
				motorSpeeds[0] = motorSpeeds[0] / 8
				motorSpeeds[1] = motorSpeeds[1] / 8
			sendMotorSpeeds(sbus, motorSpeeds, arm)

			# Calculate how much the motor has moved in the last 100ms
			if time.time()*1000 > lastCheck + 100:
				lastCheck = time.time()*1000
				moved = currentAngles[0] - lastAngles[0]
				if( moved > 16384 - 5000 ):
					moved = moved - 16384
				if( moved < -(16384 - 5000) ):
					moved = moved + 16384
				percentageMoved = abs( moved / 30.0 )				
				percentagePower = abs(lastLastMotorSpeeds[0])
				
				# Record values for next check
				lastAngles[0] = currentAngles[0]
				lastLastMotorSpeeds[0] = lastMotorSpeeds[0]
				lastMotorSpeeds[0] = motorSpeeds[0]

				percentageExpectedMoved = percentagePower
				#print "MOVED " + str( int( percentageMoved)) + "   POWER " + str( int(percentageExpectedMoved))
				if( percentagePower > 40 and motorSpeeds[0] > 40 and percentageMoved < percentageExpectedMoved * 0.7 and hit == False):
					print "OW!"
					hit = True
				

	except:
		
		print "DONE" 
		arm = 500
		sendMotorSpeeds(sbus, motorSpeeds, arm)
		sleep(0.5)
		sendMotorSpeeds(sbus, motorSpeeds, arm)

# -------------
# Functions

t = 0
import math
def updateTargetAngles( stepStages ):
	global targetAngles, t, hit
	targetAngles[0] = int( math.sin( t * math.pi / 70 ) * 4000 + 6000 )
	targetAngles[1] = int( math.sin( t * math.pi / 70 + (0.5*math.pi)) * 4000 + 10000 )
	t += 1
	if( t > 70*2 ):
		t = 0
		hit = False
	return stepStages, targetAngles

targetAngles = [0] * 8
timeThen = time.time()*1000
def updateTargetAnglesOld( stepStages ):
	global hit
	global targetAngles
	# int( math.cos(ch1)*2000)
	# Every 2 seconds
	global timeThen
	if( time.time()*1000 > timeThen + 500 ):
		timeThen = time.time()*1000
		for i in range(len(stepStages)):
			stage = stepStages[i]
			if stage == 1:
				stage = 2
				targetAngles[i*2] = 7000
				targetAngles[i*2 +1] = 7000
			elif stage == 2:
				stage = 3
				targetAngles[i*2] = 5000
				targetAngles[i*2 +1] = 5000
			elif stage == 3:
				stage = 4
				targetAngles[i*2] = 3000
				targetAngles[i*2 +1] = 8000
			elif stage == 4:
				stage = 1
				targetAngles[i*2] = 6000
				targetAngles[i*2 +1] = 11000
				if i == 0 and hit == True:
					hit = False
					print( "ok again" )
			stepStages[i] = stage

	return stepStages, targetAngles

def readCurrentAngles(sensors):
	currentAngles = [0] * 8
	for i in range(4):
		currentAngles[i] = sensors.getAngle(i+1)
	return currentAngles

def clampMotorSpeeds( motorSpeeds ):
	minSpeed = -100
	maxSpeed = 100
	for i in range(len(motorSpeeds)):
		motorSpeeds[i] = max(min(motorSpeeds[i], maxSpeed), minSpeed)
	return motorSpeeds

def calculatePs( currentAngles, targetAngles ):
	Ps = [0] * len( targetAngles )
	P_rate = 0.05
	for i in range(len(targetAngles)):
		Ps[i] = P_rate * (targetAngles[i] - currentAngles[i])
	return Ps

def sendMotorSpeeds( sbus, motorSpeedsIn, arm ):
	motorSpeeds = [0] * 8
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = int(motorSpeedsIn[i])
	middle = 995
	sendSBUSPacket( sbus, [motorSpeeds[0]*6+middle, motorSpeeds[1]*6+middle, motorSpeeds[2]*2+middle, motorSpeeds[3]*2+middle, arm] )

# ----------
# SBUS

def openSBUS():
	return serial.Serial(
		port='/dev/serial0',
		baudrate = 115200, # Must rebuild and flash betaflight to listen at this rate, not 100,000 as per normal SBUS.
		parity=serial.PARITY_EVEN,
		stopbits=serial.STOPBITS_TWO,
		bytesize=serial.EIGHTBITS,
		timeout=10)

def sendSBUSPacket(sbus, channelValues):

	# 16 blank channels, copy as many channels as given
	channels = [100]*16
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
	sbus.write( array.array('B', sbus_data).tostring() ) 


if __name__=="__main__":
   main()
