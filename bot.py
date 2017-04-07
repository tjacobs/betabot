# Betabot
# Code: https://github.com/tjacobs/betabot
# by Tom Jacobs

import sys
sys.path.append( 'sim' )

from sensors import AMS
from simulator import Simulator
from sbus import SBUS

import keyboard
import time
import math
import array
import curses
import datetime

# Keyboard handling
up_key_pressed = False
down_key_pressed = False
left_key_pressed = False
right_key_pressed = False

armTime = time.time()*1000

sbus = 0

motorSpeeds = [0] * 8

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

# Go
def main():
		global motorSpeeds
		print( "Starting Betabot." )

		# Talk to motor angle sensors via I2C
		sensors = AMS()
		connected = sensors.connect(1)

		# Talk to motor controller via serial UART SBUS
		sbus = SBUS()
		sbus.connect()

		# Start simulator
		simulator = Simulator()

		# Motor speeds
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
#			currentAngles = readCurrentAngles(sensors)

			motorSpeeds[0] = vel_left
			motorSpeeds[1] = vel_right
			motorSpeeds = clampMotorSpeeds(motorSpeeds)
			#print( currentAngles[0] / 100, currentAngles[1] / 100, round( motorSpeeds[0] ), round( motorSpeeds[1]) )

			# Throttle off to enable arming
			motorSpeeds[2] = -150

			# Move
			sendMotorSpeeds(sbus, motorSpeeds, arm)

			simulator.simStep( motorSpeeds )

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

# def readCurrentAngles(sensors):
# 	currentAngles = [0] * 8
# 	try:
# 		for i in range(4):
# 			currentAngles[i] = sensors.getAngle(i+1)
# 	except:
# 		return currentAngles
# 	return currentAngles

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
	#sendSBUSPacket( sbus, [motorSpeeds[0]*6+middle, motorSpeeds[1]*6+middle, motorSpeeds[2]*6+middle, motorSpeeds[3]*6+middle, arm] )


# Go
if __name__=="__main__":
   main()
