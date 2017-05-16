# Betabot
# https://github.com/tjacobs/betabot
# by Tom Jacobs

print( "Starting Betabot." )

# Imports
import sys
import time
import math
import array
import datetime
import functions
import motors
import walk
from sensors import AMS

# What shall we enable?
ENABLE_KEYS 		= True
ENABLE_MOUSE 		= True
ENABLE_BRAIN 		= False
ENABLE_SIMULATOR 	= False

# Import Betabot parts
keys 		= None
mouse 		= None
brain 		= None
simulator 	= None
if ENABLE_KEYS:
	import keys
if ENABLE_MOUSE:
	import mouse
if ENABLE_BRAIN:
	import brain
if ENABLE_SIMULATOR:
	sys.path.append( 'simulator' )
	import simulator

# Go
def main():

	# Flush output for file logging
	sys.stdout.flush()

	# Init motor angle sensors via I2C
	sensors = AMS()
	sensors.connect(1)

	# Init motors via USB
	motors.initMotors()
	motorSpeeds = [0] * 6

	# Init mouse
	mouse_x_diff   = 0.0
	mouse_y_diff   = 0.0
	old_mouse_x    = 0.0
	old_mouse_y	   = 0.0
	mouse_speed_factor = 1.0
	
	# Init balance trim
	trim = 0.0

	# Read initial angles
	board = motors.readIMU()
	offsetPitch = board.rawIMU['ay']
	currentAngles = functions.readCurrentAngles(sensors)
	offsetAngle = currentAngles[1]

	# Loop
	while not keys or not keys.esc_key_pressed:

		# Read current IMU accelerometer values to see which way we're leaning
		board = motors.readIMU()
		pitch = board.rawIMU['ay']
		
		# Update from keyboard
		if( keys ):
			if( keys.up_key_pressed == True ):
				trim += 1
			if( keys.down_key_pressed == True ):
				trim -= 1

		# Update from mouse
		if( mouse ):
			# How much has the mouse moved from last loop?
			mouse_x = mouse.mouse_x
			mouse_y = mouse.mouse_y
			mouse_x_diff = mouse_x - old_mouse_x
			mouse_y_diff = mouse_y - old_mouse_y			
			if( mouse_x_diff > 500 ): mouse_x_diff = 0
			if( mouse_x_diff < -500 ): mouse_x_diff = 0
			if( mouse_y_diff > 500 ): mouse_y_diff = 0
			if( mouse_y_diff < -500 ): mouse_y_diff = 0
			old_mouse_x = mouse_x
			old_mouse_y = mouse_y
			mouse_x_diff *= mouse_speed_factor
			mouse_y_diff *= mouse_speed_factor

		# Read current angles of motors
		currentAngles = functions.readCurrentAngles(sensors)
		
		# Figure out what our angles should be now to walk
		targetAngles = walk.updateTargetAngles(1.0)

		# Compensate for the angle seen at startup
		targetAngles[0] += offsetAngle
		targetAngles[2] += offsetAngle

		# Compensate for our current body angle to always stand up straight
		targetAngles[0] += pitch
		targetAngles[2] += pitch

		# Allow ourselves to lean forward back manually
		targetAngles[0] += trim
		targetAngles[2] += trim

		# Move mouse up, raise up
		targetAngles[0] += mouse_y/3 # Right hip goes CW
		targetAngles[1] += mouse_y/3 # Left hip goes CW
		targetAngles[2] -= mouse_y/3 # Right knee goes CCW
		targetAngles[3] -= mouse_y/3 # Left knee goes CCW
		targetAngles[4] -= mouse_y/3 # Right foot goes CCW
		targetAngles[5] -= mouse_y/3 # Left foot goes CCW

		# Set foot angles
		rightFootServoAngle = targetAngles[4]
		leftFootServoAngle = targetAngles[5]

		# hack
		currentAngles[2] = 100
		
		# Run our movement controller to see how fast we should set our motor speeds to get to targets
		movement = walk.calculateMovement(currentAngles, targetAngles)

		# Send motor speeds
		motorSpeeds[0] = movement[0] # Right hip
		motorSpeeds[2] = 0#movement[1] # Left hip
		motorSpeeds[1] = movement[2] # Right knee
		motorSpeeds[3] = 0#movement[3] # Left knee
		motorSpeeds[4] = 0#rightFootServoAngle # Right foot servo, actually sending angle directly not speed
		motorSpeeds[5] = 0#leftFootServoAngle # Left foot servo, actually sending angle directly not speed
		motors.sendMotorSpeeds(motorSpeeds)
		
		# Display balance, angles, target angles and speeds
		functions.display( "Pitch: %3d. R Hip, R Knee: %3d, %3d, Target: %3d, %3d, Speeds: %3d, %3d" % (pitch, currentAngles[0], currentAngles[2], targetAngles[0], targetAngles[2], motorSpeeds[0], motorSpeeds[1] ) )

	# Finish up
	try:
		import RPi.GPIO as GPIO
		GPIO.cleanup()
	except:
		pass

	# Close
	motorSpeeds[0] = 0
	motorSpeeds[1] = 0
	motors.sendMotorSpeeds(motorSpeeds)
	motors.board.close()

# Go
if __name__=="__main__":
   main()
