# Betabot
# https://github.com/tjacobs/betabot
# by Tom Jacobs

print( "Starting Betabot." )

# What shall we enable?
ENABLE_SIMULATOR = False
ENABLE_BRAIN = True
ENABLE_KEYBOARD = False

# Imports
import sys
import time
import math
import array
import datetime
import functions

# Import Betabot I/O
sbus = 0
brain = 0
from sensors import AMS
from sbus import SBUS
if ENABLE_KEYBOARD:
	import keyboard
if ENABLE_BRAIN:
	import brain

# Import simulator
simulator = 0
if ENABLE_SIMULATOR:
	try:
		import sys
		sys.path.append( 'sim' )
		from simulator import Simulator
	except:
		print( "Simulator unavailable." )
		print( sys.exc_info() )

# Variables
armTime = time.time()*1000
motorSpeeds = [0] * 8
motorEnablePin = 18 # Broadcom pin 18

# Go
def main():
		global motorSpeeds, simulator, sbus

		# Motor enable pin
		try:
			import RPi.GPIO as GPIO
			GPIO.setwarnings(False)
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(motorEnablePin, GPIO.OUT)
			GPIO.output(motorEnablePin, GPIO.LOW)

			# Test
			if( True ):
				time.sleep( 0.2 )
				sys.stdout.write("\r\x1b[KTest: Motors on." )
				GPIO.output(motorEnablePin, GPIO.HIGH)
				time.sleep( 2 )
				sys.stdout.write("\r\x1b[KTest: Motors off." )
				GPIO.output(motorEnablePin, GPIO.LOW)
				time.sleep( 1 )
				sys.stdout.write("\n" )

		except:
			print( "Error: No Raspberry Pi GPIO available." )
			print( sys.exc_info() )

		# Talk to motor angle sensors via I2C
		sensors = AMS()
		sensors.connect(1)

		# Talk to motor controller via serial UART SBUS
		sbus = SBUS()
		sbus.connect()

		# Start simulator if loaded
		try:
			simulator = Simulator()
		except:
			pass

		# Init motor speeds
		velocity = 0.0
		velocity_left = 0.0
		velocity_right = 0.0

		# Flush output for file logging
		sys.stdout.flush()

		# Loop
		while not brain.esc_key_pressed:

			# Read current IMU accelerometer X, Y, Z values.
			accelX, accelY, accelZ = sbus.readIMU()

			# Arm after one second
			# TODO: Let controller always arm
			arm = 500
			if time.time()*1000 > armTime + 2000:
				arm = 1000

			# Keyboard/brain moving forward, left, or right?
			if( brain ):
				if( brain.up_key_pressed == True ):   velocity += 0.15
				if( brain.down_key_pressed == True ): velocity -= 0.15
				if( brain.left_key_pressed == True ): velocity_right += 0.3
				if( brain.right_key_pressed == True ): velocity_left += 0.3

			
			# Calculate left and right wheel velocities
			R = 0.1 # Radius of wheels
			L = 0.1 # Linear distance between wheels
			#(2.0 * velocity - heading * L ) / 2.0 * R
			#(2.0 * velocity + heading * L ) / 2.0 * R

			# Update velocity
			velocity = functions.clamp( velocity, -100.0, 100.0 )
			velocity = velocity * 0.998

			# Update left and right velocities
			velocity_left = functions.clamp( velocity_left, -100.0, 100.0 )
			velocity_right = functions.clamp( velocity_right, -100.0, 100.0 )
			velocity_left *= 0.998
			velocity_right *= 0.998

			# Read current wheel rotational angles
			currentAngles = readCurrentAngles(sensors)

			# Send motor speeds
			motorSpeeds[0] = velocity + velocity_left
			motorSpeeds[1] = velocity + velocity_right
			motorSpeeds = clampMotorSpeeds(motorSpeeds)
			motorSpeeds[2] = -150 	# Throttle off to enable arming. TODO: Remove
			if( sbus.sbus != 0 ):
				sendMotorSpeeds(motorSpeeds, arm)

 			# Update simulator
			if( simulator ):
				simulator.simStep( motorSpeeds )
			
			# Display wheel angles and speeds
			sys.stdout.write("\r\x1b[KAngles: %3d, %3d, Speeds: %3d, %3d" % 
				(currentAngles[0] / 100, currentAngles[1] / 100, motorSpeeds[0], motorSpeeds[1] ) )
			sys.stdout.flush()
			

		# Finish up
		GPIO.cleanup()

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

def sendMotorSpeeds( motorSpeedsIn, arm ):

	motorSpeeds = [0] * 8
	go = False
	for i in range(len(motorSpeedsIn)):
		motorSpeeds[i] = int(motorSpeedsIn[i])
		if( (i != 2 ) and (motorSpeeds[i] > 1 or motorSpeeds[i] < -1 ) ):
			go = True
	try:
		import RPi.GPIO as GPIO
		global motorEnablePin
		if( go ):
			GPIO.output(motorEnablePin, GPIO.HIGH)
		else:
			GPIO.output(motorEnablePin, GPIO.LOW)
	except NameError:
		pass

	middle = 995
	sbus.sendSBUSPacket( [motorSpeeds[0]*6+middle, motorSpeeds[1]*6+middle, motorSpeeds[2]*6+middle, motorSpeeds[3]*6+middle, arm] )

# Go
if __name__=="__main__":
   main()
