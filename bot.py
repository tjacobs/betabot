# Betabot
# Code: https://github.com/tjacobs/betabot
# by Tom Jacobs

# Neural Network

# Inputs are:
# IMU X, Y angles (2) ( values 0 - 1. 0.5, 0.5 is flat level )
# CurrentAngles (8) ( values 0 - 1. from 0 to 2pi radians)
# Resistances (8) ( 0 - 1. amount of resistance each motor is currently experiencing )
# MotorSpeeds (8) ( 0 - 1. current motor speeds )
# Sin(t) (1) ( 0 - 1, sin of t, where t is increasing with time )
# Cos(t) (1) ( 0 - 1, cos of t, where t is increasing with time )

# Outputs are:
# TargetAngles (8) ( 0 - 1. )
# P_rate (8) (0 - 1, from off to max_p_rate)


# First task:

# Read FrSky telemetry, get acc_smoothed X,Y,Z.
# Use that to balance on wheels

# Second task:

# Install Picamera[array] - openCV videoinput into TF.



from ams import AMS
from time import sleep
import time
import math
import array
#import tensorflow as tf
import curses
import datetime
import thread
from pynput import keyboard

armTime = time.time()*1000

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# Keyboard handling
up_key_pressed = False
down_key_pressed = False
left_key_pressed = False
right_key_pressed = False

def on_press(key):
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed
	if( key == keyboard.Key.up ): up_key_pressed = True
	if( key == keyboard.Key.down ): down_key_pressed = True
	if( key == keyboard.Key.left ): left_key_pressed = True
	if( key == keyboard.Key.right ): right_key_pressed = True

def on_release(key):
	global up_key_pressed, down_key_pressed, left_key_pressed, right_key_pressed
	if( key == keyboard.Key.up ): up_key_pressed = False
	if( key == keyboard.Key.down ): down_key_pressed = False
	if( key == keyboard.Key.left ): left_key_pressed = False
	if( key == keyboard.Key.right ): right_key_pressed = False

def keyboard_listener():
	# Collect events until released
	with keyboard.Listener(
			on_press=on_press,
			on_release=on_release) as listener:
		listener.join()

thread.start_new_thread( keyboard_listener, () )

# Go
def main():
#	try:
		# Talk to motor angle sensors via I2C
		sensors = AMS()
		connected = sensors.connect(1)
		if connected < 0:
			print( "Warning: Can not read all motor sensors" )

		# Talk to motor controller via serial UART SBUS
		sbus = openSBUS()

		# What speed is each motor at, and one step back, two steps back?
		motorSpeeds = [0] * 8
		lastMotorSpeeds = [0] * 8
		lastLastMotorSpeeds = [0] * 8

		# Last loop values
		lastAngles = [0] * 8
		lastCheck = time.time()*1000
		
		v = 0.0
		vel_left = 0.0
		vel_right = 0.0
		heading = 0.0

		# Loop
		while True:			

			# Read accel X, Y, Z.
#				accelX, accelY, accelZ = readTelemetryPackets(sbus)

			# Arm after one second
			arm = 500
			if time.time()*1000 > armTime + 2000:
				arm = 1000

			if( up_key_pressed == True ): v = 1.5#v + 0.1
			if( down_key_pressed == True ): v = -1.5#v - 0.1
			
			v = clamp( v, -1.5, 1.5 )
			v = v * 0.99
			
			heading = math.pi

			# Calculate left and right wheel velocities based on velocity and heading
			R = 0.1 # Radius of wheels
			L = 0.1 # Linear distance between wheels
			vel_left += v #(2.0 * v - heading * L ) / 2.0 * R
			vel_right += v #(2.0 * v + heading * L ) / 2.0 * R
			
			if( left_key_pressed == True ): vel_right += 2
			if( right_key_pressed == True ): vel_left += 2

			vel_left = clamp( vel_left, -100.0, 100.0 )
			vel_right = clamp( vel_right, -100.0, 100.0 )
			vel_left *= 0.98
			vel_right *= 0.98
			
			# Main loop
#			targetAngles = updateTargetAngles(vel_left, vel_right)
			currentAngles = readCurrentAngles(sensors)
#			currentAngles[1] = 16384 - currentAngles[1]
#			Ps = calculatePs(currentAngles, targetAngles)

			motorSpeeds[0] = vel_left
			motorSpeeds[1] = vel_right
			motorSpeeds = clampMotorSpeeds(motorSpeeds)
			print( currentAngles[0] / 100, currentAngles[1] / 100, round( motorSpeeds[0] ), round( motorSpeeds[1]) )

			# Throttle off to enable arming
			motorSpeeds[2] = -150

			# Move
			sendMotorSpeeds(sbus, motorSpeeds, arm)
			

#	except:
#		
#	 	print( "DONE" )
#	 	arm = 500
#	 	sendMotorSpeeds(sbus, motorSpeeds, arm)
#	 	sleep(0.5)
#	 	sendMotorSpeeds(sbus, motorSpeeds, arm)

# -------------
# Functions

t = 0.0
targetAngles = [0] * 8
def updateTargetAngles( vel_left, vel_right ):
	global targetAngles, t
	targetAngles[0] = int( (t * 16384.0 / 2000.0) % 16384 )
	targetAngles[1] = int( (t * 16384.0 / 2000.0) % 16384 )
	t += 1.0
	return targetAngles

def calculatePs( currentAngles, targetAngles ):
	Ps = [0] * len( targetAngles )
	P_rate = 0.05
	for i in range(len(targetAngles)):
		Ps[i] = P_rate * (targetAngles[i] - currentAngles[i])
	return Ps
	
	
# -------------
# Betabot functions

def readCurrentAngles(sensors):
	currentAngles = [0] * 8
	try:
		for i in range(4):
			currentAngles[i] = sensors.getAngle(i+1)
	except:
		return currentAngles
	return currentAngles

def clampMotorSpeeds( motorSpeeds ):
	minSpeed = -100
	maxSpeed = 100
	for i in range(len(motorSpeeds)):
		motorSpeeds[i] = max(min(motorSpeeds[i], maxSpeed), minSpeed)
	return motorSpeeds

def sendMotorSpeeds( sbus, motorSpeedsIn, arm ):
	motorSpeeds = [0] * 8
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = int(motorSpeedsIn[i])
	middle = 995
	sendSBUSPacket( sbus, [motorSpeeds[0]*6+middle, motorSpeeds[1]*6+middle, motorSpeeds[2]*6+middle, motorSpeeds[3]*6+middle, arm] )

# ----------
# SBUS functions

def openSBUS():
	try:
		import serial
		return serial.Serial(
			port='/dev/serial0',
			baudrate = 115200, # Must rebuild and flash betaflight to listen at this rate, not 100,000 as per normal SBUS.
			parity=serial.PARITY_EVEN,
			stopbits=serial.STOPBITS_TWO,
			bytesize=serial.EIGHTBITS,
			timeout=10)
	except:
		print( "Serial not available" )

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
	try:
		sbus.write( array.array('B', sbus_data).tostring() )
		time.sleep( 0.001 )
	except:
		pass


# ----------
# Serial telemetry functions

PROTOCOL_HEADER      = 0x5E
PROTOCOL_TAIL        = 0x5E
ID_ACC_X             = 0x24
ID_ACC_Y             = 0x25
ID_ACC_Z             = 0x26

def read16( serial ):
	v1 = serial.read( )
	v2 = serial.read( )
	print( v1, v2 )
	value = v1 + v2 << 8
	return value	

def readTelemetryPackets( serial ):

	accelX, accelY, accelZ = 0, 0, 0
	print( "..." + str( serial.inWaiting() ) )
	while( serial.inWaiting() > 0 ):
		x = serial.read( )
#		if( x == PROTOCOL_HEADER ):
		if( True ):
			packet = serial.read( )
			print( str( ord( packet ) ) )
			if( packet == ID_ACC_X ):
				accelX = read16( serial )
			if( packet == ID_ACC_Y ):
				accelY = read16( serial )
			if( packet == ID_ACC_Z ):
				accelZ = read16( serial )
	return accelX, accelY, accelZ



# Go
if __name__=="__main__":
   main()
