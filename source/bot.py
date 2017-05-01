# Betabot
# https://github.com/tjacobs/betabot
# by Tom Jacobs

print( "Starting Betabot." )

# What shall we enable?
ENABLE_SIMULATOR = False
ENABLE_BRAIN = False
ENABLE_KEYBOARD = True

# Imports
import sys
import time
import math
import array
import datetime
import functions
import walk
from sys import stdout

# Import Betabot I/O
sbus = None
brain = None
keyboard = None
from sensors import AMS
from sbus import SBUS
if ENABLE_KEYBOARD:
	import keyboard
if ENABLE_BRAIN:
	import brain

# Import simulator
simulator = None
if ENABLE_SIMULATOR:
	try:
		sys.path.append( '../simulator' )
		from simulator import Simulator
		simulator = Simulator()
	except:
		print( "Simulator unavailable." )
		print( sys.exc_info() )

# Variables
armTime = time.time()*1000
motorSpeeds = [0] * 4

# Go
def main():
		global motorSpeeds, simulator, sbus

		# Talk to motor angle sensors via I2C
		sensors = AMS()
		sensors.connect(1)

		# Talk to motors via serial UART SBUS
		sbus = SBUS()
		sbus.connect()

		# Init motor speeds
		velocity = 0.0
		velocity_left = 0.0
		velocity_right = 0.0

		# Flush output for file logging
		sys.stdout.flush()

		functions.initMotors()

		# Loop
		while not keyboard or not keyboard.esc_key_pressed:

			# Read current IMU accelerometer X, Y, Z values.
			board = functions.readIMU()
			message = "ax= {:+.0f} ay= {:+.0f} az= {:+.0f} gx= {:+.0f} gy= {:+.0f} gz= {:+.0f} mx= {:+.0f} my= {:+.0f} mz= {:+.0f}" .format(float(board.rawIMU['ax']),float(board.rawIMU['ay']),float(board.rawIMU['az']),float(board.rawIMU['gx']),float(board.rawIMU['gy']),float(board.rawIMU['gz']),float(board.rawIMU['mx']),float(board.rawIMU['my']),float(board.rawIMU['mz']))
			stdout.write("\r%s" % message )
			stdout.flush()

			# Arm after one second
			# TODO: Let controller always arm
			arm = 500
			if time.time()*1000 > armTime + 2000:
				arm = 1000

			# Keyboard/brain moving forward, left, or right?
			if( brain ):
				if( brain.up_key_pressed == True ):   velocity += 0.15
				if( brain.down_key_pressed == True ): velocity -= 0.15
				if( brain.left_key_pressed == True ):
					velocity_right += 0.3
					velocity_left -= 0.3
				if( brain.right_key_pressed == True ):
					velocity_left += 0.3
					velocity_right -= 0.3
			if( keyboard ):
				if( keyboard.up_key_pressed == True ):   velocity += 0.3
				if( keyboard.down_key_pressed == True ): velocity -= 0.3
				if( keyboard.left_key_pressed == True ): 
					velocity_right += 0.5
					velocity_left -= 0.5
				if( keyboard.right_key_pressed == True ):
					velocity_left += 0.5
					velocity_right -= 0.5

			# Calculate left and right wheel velocities
			#R = 0.1 # Radius of wheels
			#L = 0.1 # Linear distance between wheels
			#(2.0 * velocity - heading * L ) / 2.0 * R
			#(2.0 * velocity + heading * L ) / 2.0 * R

			# Update velocity
			velocity = functions.clamp( velocity, -80.0, 80.0 )
			velocity = velocity * 0.98

			# Update left and right velocities
			velocity_left = functions.clamp( velocity_left, -80.0, 80.0 )
			velocity_right = functions.clamp( velocity_right, -80.0, 80.0 )
			velocity_left *= 0.95
			velocity_right *= 0.95

			# Read current wheel rotational angles
			currentAngles = functions.readCurrentAngles(sensors)
			
			# Figure out what our angles should be
			targetAngles = walk.updateTargetAngles( 10, 0 )
			
			# Run our movement controller
			movement = walk.calculateMovement( currentAngles, targetAngles )
			motorSpeeds[0] = -movement[0]
			motorSpeeds[1] = -movement[1]

			# Send motor speeds
#			motorSpeeds[0] += ( velocity + velocity_right )
#			motorSpeeds[1] += ( velocity + velocity_left )
			motorSpeeds[3] = 0
			motorSpeeds = functions.clampMotorSpeeds(motorSpeeds)
			motorSpeeds[2] = -150 	# Throttle off to enable arming. TODO: Remove
			functions.sendMotorSpeeds(sbus, motorSpeeds, arm)

 			# Update simulator
			if( simulator ): simulator.simStep( motorSpeeds )
			
			# Display wheel angles and speeds
#			sys.stdout.write("\r\x1b[KCurrent Angles: %3d, %3d, Target Angles: %3d, %3d, Motor Speeds: %3d, %3d" % 
#				(currentAngles[0], currentAngles[1], targetAngles[0], targetAngles[1], motorSpeeds[0], motorSpeeds[1] ) )
#			sys.stdout.flush()			

		# Finish up
		try:
			import RPi.GPIO as GPIO
			GPIO.cleanup()
		except:
			pass

# Go
if __name__=="__main__":
   main()
