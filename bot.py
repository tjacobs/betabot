# Betabot
# https://github.com/tjacobs/betabot
# by Tom Jacobs

print( "Starting Betabot." )

# What shall we enable?
ENABLE_SIMULATOR = True
ENABLE_BRAIN = True
ENABLE_KEYBOARD = True

# Imports
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
if ENABLE_BRAIN
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
motorEnablePin = 4 # Broadcom pin 4 (P1 pin 7)

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# Go
def main():
		global motorSpeeds, simulator, sbus

		# Motor enable pin
		try:
			import RPi.GPIO as GPIO
			GPIO.setwarnings(false)
			GPIO.setmode(GPIO.BCM)
			GPIO.setup(motorEnablePin, GPIO.OUT)
			GPIO.output(motorEnablePin, GPIO.LOW)
		except:
			print( "Error: No Raspberry Pi GPIO available." )

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

		# Motor speeds
		v = 0.0
		vel_left = 0.0
		vel_right = 0.0
		heading = 0.0

		# Loop
		while True:			
			time.sleep( 0.1 )

			# Read accel X, Y, Z.
#				accelX, accelY, accelZ = readTelemetryPackets(sbus)

			# Arm after one second
			arm = 500
			if time.time()*1000 > armTime + 2000:
				arm = 1000

			if( brain and brain.up_key_pressed == True ):   v = 1.5
			if( brain and brain.down_key_pressed == True ): v = -1.5
			
			v = clamp( v, -1.5, 1.5 )
			v = v * 0.99
			
			heading = math.pi

			# Calculate left and right wheel velocities based on velocity and heading
			R = 0.1 # Radius of wheels
			L = 0.1 # Linear distance between wheels
			vel_left += v #(2.0 * v - heading * L ) / 2.0 * R
			vel_right += v #(2.0 * v + heading * L ) / 2.0 * R
			
			if( brain and brain.left_key_pressed == True ): vel_right += 2
			if( brain and brain.right_key_pressed == True ): vel_left += 2

			vel_left = clamp( vel_left, -100.0, 100.0 )
			vel_right = clamp( vel_right, -100.0, 100.0 )
			vel_left *= 0.98
			vel_right *= 0.98
			
			currentAngles = readCurrentAngles(sensors)

			motorSpeeds[0] = vel_left
			motorSpeeds[1] = vel_right
			motorSpeeds = clampMotorSpeeds(motorSpeeds)
			#print( currentAngles[0] / 100, currentAngles[1] / 100, round( motorSpeeds[0] ), round( motorSpeeds[1]) )

			# Throttle off to enable arming
			motorSpeeds[2] = -150

			# Move
			if( sbus.sbus != 0 ):
				sendMotorSpeeds(motorSpeeds, arm)

			# Update simulator if present
			if( simulator ):
				simulator.simStep( motorSpeeds )

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
